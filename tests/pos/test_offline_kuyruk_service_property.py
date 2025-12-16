# Version: 0.1.0
# Last Update: 2025-12-16
# Module: tests.pos.test_offline_kuyruk_service_property
# Description: OfflineKuyrukService özellik tabanlı testleri
# Changelog:
# - İlk oluşturma

"""
OfflineKuyrukService Özellik Tabanlı Testleri

Bu modül OfflineKuyrukService için özellik tabanlı testleri içerir.
Kuyruk senkronizasyonu ve hata yönetimi özelliklerini doğrular.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, List
import hypothesis.strategies as st
from hypothesis import given, assume, settings

from sontechsp.uygulama.moduller.pos.services.offline_kuyruk_service import OfflineKuyrukService
from sontechsp.uygulama.moduller.pos.arayuzler import (
    IOfflineKuyrukRepository, IslemTuru, KuyrukDurum
)
from sontechsp.uygulama.cekirdek.hatalar import (
    SontechHatasi, DogrulamaHatasi, NetworkHatasi
)


# Test veri stratejileri
@st.composite
def islem_turu_strategy(draw):
    """İşlem türü stratejisi"""
    return draw(st.sampled_from(list(IslemTuru)))


@st.composite
def kuyruk_durum_strategy(draw):
    """Kuyruk durumu stratejisi"""
    return draw(st.sampled_from(list(KuyrukDurum)))


@st.composite
def pozitif_int_strategy(draw):
    """Pozitif integer stratejisi"""
    return draw(st.integers(min_value=1, max_value=1000))


@st.composite
def oncelik_strategy(draw):
    """Öncelik stratejisi (1-5 arası)"""
    return draw(st.integers(min_value=1, max_value=5))


@st.composite
def islem_veri_strategy(draw):
    """İşlem verisi stratejisi"""
    return draw(st.dictionaries(
        keys=st.text(min_size=1, max_size=20),
        values=st.one_of(
            st.text(max_size=100),
            st.integers(),
            st.floats(allow_nan=False, allow_infinity=False),
            st.booleans()
        ),
        min_size=1,
        max_size=10
    ))


@st.composite
def kuyruk_kaydi_strategy(draw):
    """Kuyruk kaydı stratejisi"""
    return {
        'id': draw(pozitif_int_strategy()),
        'islem_turu': draw(islem_turu_strategy()).value,
        'durum': draw(kuyruk_durum_strategy()).value,
        'veri': draw(islem_veri_strategy()),
        'terminal_id': draw(pozitif_int_strategy()),
        'kasiyer_id': draw(pozitif_int_strategy()),
        'islem_tarihi': datetime.now().isoformat(),
        'deneme_sayisi': draw(st.integers(min_value=0, max_value=5)),
        'max_deneme_sayisi': 3,
        'oncelik': draw(oncelik_strategy()),
        'hata_mesaji': None
    }


class TestOfflineKuyrukServiceProperty:
    """OfflineKuyrukService özellik tabanlı testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.mock_repo = Mock(spec=IOfflineKuyrukRepository)
        self.service = OfflineKuyrukService(self.mock_repo)
    
    @given(
        islem_turu=islem_turu_strategy(),
        veri=islem_veri_strategy(),
        terminal_id=pozitif_int_strategy(),
        kasiyer_id=pozitif_int_strategy(),
        oncelik=oncelik_strategy()
    )
    @settings(max_examples=100)
    def test_property_20_kuyruk_senkronizasyonu(self, islem_turu, veri, terminal_id, 
                                              kasiyer_id, oncelik):
        """
        **Feature: pos-cekirdek-modulu, Property 20: Kuyruk Senkronizasyonu**
        **Validates: Requirements 5.3**
        
        Herhangi bir kuyruk durumu için, network bağlantısı geri geldiğinde 
        sistem kuyruktan işlemleri sırayla göndermeli
        """
        # Arrange
        kuyruk_id = 123
        self.mock_repo.kuyruk_ekle.return_value = kuyruk_id
        
        # Network durumu mock'u - önce offline, sonra online
        with patch.object(self.service, 'network_durumu_kontrol') as mock_network:
            with patch.object(self.service, '_islem_direkt_gonder') as mock_direkt:
                # İlk çağrıda offline (False), sonraki çağrılarda online (True)
                mock_network.side_effect = [False, True, True, True]
                mock_direkt.return_value = False  # Direkt gönderim başarısız
                
                # Bekleyen kuyruk listesi mock'u
                kuyruk_kaydi = {
                    'id': kuyruk_id,
                    'islem_turu': islem_turu.value,
                    'durum': KuyrukDurum.BEKLEMEDE.value,
                    'veri': veri,
                    'terminal_id': terminal_id,
                    'kasiyer_id': kasiyer_id
                }
                
                # İlk çağrıda kayıt var, ikinci çağrıda boş liste
                self.mock_repo.bekleyen_kuyruk_listesi.side_effect = [
                    [kuyruk_kaydi],  # İlk batch
                    []  # İkinci batch - boş
                ]
                
                # Kuyruk işlemi gönderimi başarılı
                with patch.object(self.service, '_kuyruk_islemini_gonder') as mock_gonder:
                    mock_gonder.return_value = True
                    
                    # Act - İşlemi kuyruğa ekle (offline durumda)
                    result = self.service.islem_kuyruga_ekle(
                        islem_turu, veri, terminal_id, kasiyer_id, oncelik
                    )
                    
                    # Assert - Kuyruk ekleme başarılı
                    assert result is True
                    self.mock_repo.kuyruk_ekle.assert_called_once()
                    
                    # Act - Senkronizasyon yap (online durumda)
                    islenen_sayisi = self.service.kuyruk_senkronize_et()
                    
                    # Assert - Senkronizasyon özellikleri
                    assert islenen_sayisi >= 0  # En az 0 işlem işlenmeli
                    
                    # Bekleyen kuyruk listesi çağrıldı
                    assert self.mock_repo.bekleyen_kuyruk_listesi.call_count >= 1
                    
                    # Durum güncellemeleri yapıldı
                    assert self.mock_repo.kuyruk_durum_guncelle.call_count >= 1
                    
                    # İşlem gönderildi
                    mock_gonder.assert_called_once_with(kuyruk_kaydi)
    
    @given(
        islem_turu=islem_turu_strategy(),
        veri=islem_veri_strategy(),
        terminal_id=pozitif_int_strategy(),
        kasiyer_id=pozitif_int_strategy()
    )
    @settings(max_examples=100)
    def test_property_21_kuyruk_hata_yonetimi(self, islem_turu, veri, terminal_id, kasiyer_id):
        """
        **Feature: pos-cekirdek-modulu, Property 21: Kuyruk Hata Yönetimi**
        **Validates: Requirements 5.4**
        
        Herhangi bir kuyruk işlemi hatası için, sistem hata durumunu kaydetmeli 
        ve tekrar deneme yapmalı
        """
        # Arrange
        kuyruk_id = 456
        self.mock_repo.kuyruk_ekle.return_value = kuyruk_id
        
        # Network durumu online
        with patch.object(self.service, 'network_durumu_kontrol') as mock_network:
            mock_network.return_value = True
            
            # Direkt gönderim başarısız
            with patch.object(self.service, '_islem_direkt_gonder') as mock_direkt:
                mock_direkt.return_value = False
                
                # Bekleyen kuyruk listesi - hatalı işlem
                kuyruk_kaydi = {
                    'id': kuyruk_id,
                    'islem_turu': islem_turu.value,
                    'durum': KuyrukDurum.BEKLEMEDE.value,
                    'veri': veri,
                    'terminal_id': terminal_id,
                    'kasiyer_id': kasiyer_id,
                    'deneme_sayisi': 0,
                    'max_deneme_sayisi': 3
                }
                
                self.mock_repo.bekleyen_kuyruk_listesi.side_effect = [
                    [kuyruk_kaydi],  # İlk batch
                    []  # İkinci batch - boş
                ]
                
                # Kuyruk işlemi gönderimi başarısız
                with patch.object(self.service, '_kuyruk_islemini_gonder') as mock_gonder:
                    mock_gonder.return_value = False  # Hata simülasyonu
                    
                    # Act - İşlemi kuyruğa ekle
                    result = self.service.islem_kuyruga_ekle(
                        islem_turu, veri, terminal_id, kasiyer_id
                    )
                    
                    # Assert - Kuyruk ekleme başarılı
                    assert result is True
                    
                    # Act - Senkronizasyon yap (hata ile)
                    islenen_sayisi = self.service.kuyruk_senkronize_et()
                    
                    # Assert - Hata yönetimi özellikleri
                    assert islenen_sayisi >= 0  # İşlem sayısı geçerli
                    
                    # Hata durumu için deneme artırma çağrıldı
                    self.mock_repo.kuyruk_deneme_artir.assert_called()
                    
                    # Deneme artırma çağrısının parametrelerini kontrol et
                    call_args = self.mock_repo.kuyruk_deneme_artir.call_args
                    assert call_args[0][0] == kuyruk_id  # İlk parametre kuyruk_id
                    assert isinstance(call_args[0][1], str)  # İkinci parametre hata mesajı
                    assert len(call_args[0][1]) > 0  # Hata mesajı boş değil
    
    @given(
        network_durumu=st.booleans(),
        islem_sayisi=st.integers(min_value=0, max_value=50)
    )
    @settings(max_examples=100)
    def test_property_network_durumu_cache_tutarliligi(self, network_durumu, islem_sayisi):
        """
        Herhangi bir network durumu için, cache mekanizması tutarlı çalışmalı
        """
        # Arrange
        with patch('socket.gethostbyname') as mock_dns:
            with patch('requests.get') as mock_http:
                if network_durumu:
                    mock_dns.return_value = '8.8.8.8'
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_http.return_value = mock_response
                else:
                    mock_dns.side_effect = Exception("Network error")
                
                # Act - İlk kontrol
                ilk_sonuc = self.service.network_durumu_kontrol()
                
                # Act - Ardışık kontroller (cache süresi içinde)
                sonuclar = []
                for _ in range(min(islem_sayisi, 10)):  # Maksimum 10 kontrol
                    sonuclar.append(self.service.network_durumu_kontrol())
                
                # Assert - Cache tutarlılığı
                assert ilk_sonuc == network_durumu
                
                # Tüm sonuçlar aynı olmalı (cache nedeniyle)
                for sonuc in sonuclar:
                    assert sonuc == ilk_sonuc
                
                # DNS çağrısı sadece bir kez yapılmalı (cache nedeniyle)
                assert mock_dns.call_count <= 1
    
    @given(
        terminal_id=pozitif_int_strategy(),
        kasiyer_id=pozitif_int_strategy(),
        gun_sayisi=st.integers(min_value=1, max_value=365)
    )
    @settings(max_examples=100)
    def test_property_kuyruk_temizleme_guvenli(self, terminal_id, kasiyer_id, gun_sayisi):
        """
        Herhangi bir gün sayısı için, kuyruk temizleme işlemi güvenli olmalı
        """
        # Arrange
        temizlenen_sayi = 42  # Mock değer
        self.mock_repo.kuyruk_temizle.return_value = temizlenen_sayi
        
        # Act
        sonuc = self.service.kuyruk_temizle(gun_sayisi)
        
        # Assert - Temizleme özellikleri
        assert sonuc >= 0  # Negatif olamaz
        assert isinstance(sonuc, int)  # Integer olmalı
        
        # Repository çağrısı doğru parametrelerle yapıldı
        self.mock_repo.kuyruk_temizle.assert_called_once_with(gun_sayisi)
    
    @given(
        islem_listesi=st.lists(kuyruk_kaydi_strategy(), min_size=0, max_size=20)
    )
    @settings(max_examples=100)
    def test_property_senkronizasyon_batch_isleme(self, islem_listesi):
        """
        Herhangi bir işlem listesi için, senkronizasyon batch halinde çalışmalı
        """
        # Arrange
        with patch.object(self.service, 'network_durumu_kontrol') as mock_network:
            mock_network.return_value = True
            
            # İşlem listesini batch'lere böl
            batch_boyutu = self.service._senkron_batch_boyutu
            batches = [islem_listesi[i:i + batch_boyutu] 
                      for i in range(0, len(islem_listesi), batch_boyutu)]
            
            if not batches:
                batches = [[]]  # Boş liste için boş batch
            
            # Bekleyen kuyruk listesi mock'u
            self.mock_repo.bekleyen_kuyruk_listesi.side_effect = batches
            
            # Tüm işlemler başarılı
            with patch.object(self.service, '_kuyruk_islemini_gonder') as mock_gonder:
                mock_gonder.return_value = True
                
                # Act
                islenen_sayisi = self.service.kuyruk_senkronize_et()
                
                # Assert - Batch işleme özellikleri
                assert islenen_sayisi >= 0
                assert islenen_sayisi <= len(islem_listesi)
                
                # Bekleyen kuyruk listesi en az bir kez çağrıldı
                assert self.mock_repo.bekleyen_kuyruk_listesi.call_count >= 1
                
                # Her batch için limit parametresi doğru
                for call in self.mock_repo.bekleyen_kuyruk_listesi.call_args_list:
                    if 'limit' in call.kwargs:
                        assert call.kwargs['limit'] == batch_boyutu
    
    def test_property_network_hatasi_durumunda_senkronizasyon_iptal(self):
        """
        Network hatası durumunda senkronizasyon iptal edilmeli
        """
        # Arrange
        with patch.object(self.service, 'network_durumu_kontrol') as mock_network:
            mock_network.return_value = False  # Network yok
            
            # Act & Assert
            with pytest.raises(NetworkHatasi):
                self.service.kuyruk_senkronize_et()
    
    @given(
        gecersiz_veri=st.one_of(
            st.none(),
            st.text(),
            st.integers(),
            st.lists(st.integers()),
            st.dictionaries(st.text(), st.text(), max_size=0)  # Boş dict
        )
    )
    @settings(max_examples=100)
    def test_property_gecersiz_veri_dogrulama(self, gecersiz_veri):
        """
        Herhangi bir geçersiz veri için, doğrulama hatası fırlatılmalı
        """
        # Arrange
        islem_turu = IslemTuru.SATIS
        terminal_id = 1
        kasiyer_id = 1
        
        # Act & Assert
        with pytest.raises(DogrulamaHatasi):
            self.service.islem_kuyruga_ekle(
                islem_turu, gecersiz_veri, terminal_id, kasiyer_id
            )
    
    @given(
        terminal_id=st.integers(max_value=0),
        kasiyer_id=pozitif_int_strategy()
    )
    @settings(max_examples=100)
    def test_property_gecersiz_terminal_id_dogrulama(self, terminal_id, kasiyer_id):
        """
        Herhangi bir geçersiz terminal ID için, doğrulama hatası fırlatılmalı
        """
        # Arrange
        islem_turu = IslemTuru.SATIS
        veri = {'test': 'data'}
        
        # Act & Assert
        with pytest.raises(DogrulamaHatasi):
            self.service.islem_kuyruga_ekle(
                islem_turu, veri, terminal_id, kasiyer_id
            )
    
    @given(
        terminal_id=pozitif_int_strategy(),
        kasiyer_id=st.integers(max_value=0)
    )
    @settings(max_examples=100)
    def test_property_gecersiz_kasiyer_id_dogrulama(self, terminal_id, kasiyer_id):
        """
        Herhangi bir geçersiz kasiyer ID için, doğrulama hatası fırlatılmalı
        """
        # Arrange
        islem_turu = IslemTuru.SATIS
        veri = {'test': 'data'}
        
        # Act & Assert
        with pytest.raises(DogrulamaHatasi):
            self.service.islem_kuyruga_ekle(
                islem_turu, veri, terminal_id, kasiyer_id
            )
    
    @given(
        oncelik=st.integers().filter(lambda x: x < 1 or x > 5)
    )
    @settings(max_examples=100)
    def test_property_gecersiz_oncelik_dogrulama(self, oncelik):
        """
        Herhangi bir geçersiz öncelik değeri için, doğrulama hatası fırlatılmalı
        """
        # Arrange
        islem_turu = IslemTuru.SATIS
        veri = {'test': 'data'}
        terminal_id = 1
        kasiyer_id = 1
        
        # Act & Assert
        with pytest.raises(DogrulamaHatasi):
            self.service.islem_kuyruga_ekle(
                islem_turu, veri, terminal_id, kasiyer_id, oncelik
            )