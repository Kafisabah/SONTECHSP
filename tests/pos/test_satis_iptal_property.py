# Version: 0.1.0
# Last Update: 2025-12-16
# Module: tests.pos.test_satis_iptal_property
# Description: Satış iptal özellik tabanlı testleri
# Changelog:
# - İlk oluşturma

"""
Satış İptal Özellik Tabanlı Testleri

Bu modül satış iptal işlemlerinin özellik tabanlı testlerini içerir.
Hypothesis kütüphanesi kullanılarak rastgele verilerle test edilir.
"""

import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, strategies as st, assume, settings

from sontechsp.uygulama.moduller.pos.servisler.satis_iptal_service import SatisIptalService
from sontechsp.uygulama.moduller.pos.arayuzler import SepetDurum, SatisDurum
from sontechsp.uygulama.cekirdek.hatalar import DogrulamaHatasi, SontechHatasi


class TestSatisIptalPropertyTests:
    """Satış iptal özellik tabanlı testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        # Mock repository'ler
        self.mock_sepet_repository = Mock()
        self.mock_satis_repository = Mock()
        self.mock_stok_service = Mock()
        
        # SatisIptalService instance'ı oluştur
        self.iptal_service = SatisIptalService(
            sepet_repository=self.mock_sepet_repository,
            satis_repository=self.mock_satis_repository,
            stok_service=self.mock_stok_service
        )
    
    def teardown_method(self):
        """Her test sonrası çalışır"""
        # Mock'ları sıfırla
        self.mock_sepet_repository.reset_mock()
        self.mock_satis_repository.reset_mock()
        self.mock_stok_service.reset_mock()
    
    @given(
        sepet_id=st.integers(min_value=1, max_value=10000),
        iptal_nedeni=st.text(min_size=5, max_size=100, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?'),
        urun_listesi=st.lists(
            st.tuples(
                st.integers(min_value=1, max_value=1000),  # urun_id
                st.integers(min_value=1, max_value=10)     # adet
            ),
            min_size=1,
            max_size=5
        )
    )
    @settings(max_examples=50)
    def test_property_29_satis_iptal_sureci(self, sepet_id, iptal_nedeni, urun_listesi):
        """
        **Feature: pos-cekirdek-modulu, Property 29: Satış İptal Süreci**
        **Validates: Requirements 8.1, 8.2**
        
        Herhangi bir satış iptal işlemi için, sistem iptal nedenini sormalı ve onaylandığında 
        sepeti temizlemeli, satış kaydını iptal durumuna getirmeli
        """
        # Arrange
        satirlar = []
        for urun_id, adet in urun_listesi:
            satirlar.append({
                'urun_id': urun_id,
                'adet': adet
            })
        
        mock_sepet = {
            'id': sepet_id,
            'durum': SepetDurum.AKTIF.value,
            'satirlar': satirlar
        }
        
        self.mock_sepet_repository.sepet_getir.return_value = mock_sepet
        self.mock_sepet_repository.sepet_bosalt.return_value = True
        self.mock_satis_repository.sepet_ile_satis_getir.return_value = None
        self.mock_stok_service.stok_rezervasyon_serbest_birak.return_value = True
        
        # Mock sepet repository'de durum güncelleme metodu ekle
        self.mock_sepet_repository.sepet_durum_guncelle.return_value = True
        
        # Act
        # 1. İptal nedeni sorgula
        sorgulanan_neden = self.iptal_service.iptal_nedeni_sorgula(sepet_id)
        
        # 2. Satış iptal et
        iptal_sonucu = self.iptal_service.satis_iptal_et(sepet_id, iptal_nedeni)
        
        # Assert
        # 1. İptal nedeni sorgulandı
        assert sorgulanan_neden is not None
        assert isinstance(sorgulanan_neden, str)
        assert len(sorgulanan_neden) > 0
        
        # 2. İptal işlemi başarılı
        assert iptal_sonucu is True
        
        # 3. Sepet bilgisi alındı
        self.mock_sepet_repository.sepet_getir.assert_called_with(sepet_id)
        
        # 4. Sepet boşaltıldı
        self.mock_sepet_repository.sepet_bosalt.assert_called_with(sepet_id)
        
        # 5. Sepet durumu iptal olarak güncellendi
        self.mock_sepet_repository.sepet_durum_guncelle.assert_called_with(sepet_id, SepetDurum.IPTAL)
        
        # 6. Stok rezervasyonları serbest bırakıldı
        for urun_id, adet in urun_listesi:
            self.mock_stok_service.stok_rezervasyon_serbest_birak.assert_any_call(urun_id, adet)
    
    @given(
        sepet_id=st.integers(min_value=1, max_value=10000),
        urun_listesi=st.lists(
            st.tuples(
                st.integers(min_value=1, max_value=1000),  # urun_id
                st.integers(min_value=1, max_value=10)     # adet
            ),
            min_size=1,
            max_size=5
        )
    )
    @settings(max_examples=50)
    def test_property_30_stok_rezervasyon_serbest_birakma(self, sepet_id, urun_listesi):
        """
        **Feature: pos-cekirdek-modulu, Property 30: Stok Rezervasyon Serbest Bırakma**
        **Validates: Requirements 8.3**
        
        Herhangi bir stok rezervasyonu için, iptal işleminde sistem stok rezervasyonunu serbest bırakmalı
        """
        # Arrange
        satirlar = []
        for urun_id, adet in urun_listesi:
            satirlar.append({
                'urun_id': urun_id,
                'adet': adet
            })
        
        mock_sepet = {
            'id': sepet_id,
            'durum': SepetDurum.AKTIF.value,
            'satirlar': satirlar
        }
        
        self.mock_sepet_repository.sepet_getir.return_value = mock_sepet
        self.mock_stok_service.stok_rezervasyon_serbest_birak.return_value = True
        
        # Act
        sonuc = self.iptal_service.stok_rezervasyon_serbest_birak(sepet_id)
        
        # Assert
        # 1. İşlem başarılı
        assert sonuc is True
        
        # 2. Sepet bilgisi alındı
        self.mock_sepet_repository.sepet_getir.assert_called_with(sepet_id)
        
        # 3. Her ürün için stok rezervasyonu serbest bırakıldı
        for urun_id, adet in urun_listesi:
            self.mock_stok_service.stok_rezervasyon_serbest_birak.assert_any_call(urun_id, adet)
        
        # 4. Toplam çağrı sayısı doğru (her test durumu için)
        expected_calls = len(urun_listesi)
        actual_calls = self.mock_stok_service.stok_rezervasyon_serbest_birak.call_count
        assert actual_calls >= expected_calls  # En az beklenen sayıda çağrı yapılmalı
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        yeni_sepet_id=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=50)
    def test_property_31_iptal_sonrasi_hazir_duruma_gecme(self, terminal_id, kasiyer_id, yeni_sepet_id):
        """
        **Feature: pos-cekirdek-modulu, Property 31: İptal Sonrası Hazır Duruma Geçme**
        **Validates: Requirements 8.4**
        
        Herhangi bir iptal tamamlama işlemi için, sistem yeni satış için hazır duruma geçmeli
        """
        # Arrange
        # Mock'ları her test için sıfırla
        self.mock_sepet_repository.reset_mock()
        
        # Mock sepet repository'de sepet oluşturma
        self.mock_sepet_repository.sepet_olustur.return_value = yeni_sepet_id
        
        # Act
        sonuc_sepet_id = self.iptal_service.yeni_satis_hazirla(terminal_id, kasiyer_id)
        
        # Assert
        # 1. Yeni sepet ID döndürüldü
        assert sonuc_sepet_id == yeni_sepet_id
        assert isinstance(sonuc_sepet_id, int)
        assert sonuc_sepet_id > 0
        
        # 2. Yeni sepet oluşturuldu
        self.mock_sepet_repository.sepet_olustur.assert_called_once_with(terminal_id, kasiyer_id)
    
    @given(
        sepet_id=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=30)
    def test_iptal_edilebilir_sepet_kontrol_property(self, sepet_id):
        """
        İptal edilebilir sepet kontrol özellik testi
        
        Herhangi bir aktif sepet için iptal edilebilirlik kontrolü doğru sonuç vermeli
        """
        # Arrange - Aktif sepet
        mock_sepet = {
            'id': sepet_id,
            'durum': SepetDurum.AKTIF.value
        }
        
        self.mock_sepet_repository.sepet_getir.return_value = mock_sepet
        
        # Act
        kontrol_sonucu = self.iptal_service.sepet_iptal_edilebilir_mi(sepet_id)
        
        # Assert
        assert 'iptal_edilebilir' in kontrol_sonucu
        assert 'neden' in kontrol_sonucu
        assert kontrol_sonucu['iptal_edilebilir'] is True
        assert isinstance(kontrol_sonucu['neden'], str)
    
    @given(
        sepet_id=st.integers(min_value=1, max_value=10000),
        iptal_durum=st.sampled_from([SepetDurum.IPTAL.value, SepetDurum.TAMAMLANDI.value])
    )
    @settings(max_examples=30)
    def test_iptal_edilemez_sepet_kontrol_property(self, sepet_id, iptal_durum):
        """
        İptal edilemez sepet kontrol özellik testi
        
        Herhangi bir iptal edilmiş veya tamamlanmış sepet için iptal edilemez sonucu vermeli
        """
        # Arrange - İptal edilmiş veya tamamlanmış sepet
        mock_sepet = {
            'id': sepet_id,
            'durum': iptal_durum
        }
        
        self.mock_sepet_repository.sepet_getir.return_value = mock_sepet
        
        # Act
        kontrol_sonucu = self.iptal_service.sepet_iptal_edilebilir_mi(sepet_id)
        
        # Assert
        assert 'iptal_edilebilir' in kontrol_sonucu
        assert 'neden' in kontrol_sonucu
        assert kontrol_sonucu['iptal_edilebilir'] is False
        assert isinstance(kontrol_sonucu['neden'], str)
        assert len(kontrol_sonucu['neden']) > 0
    
    @given(
        sepet_id=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=30)
    def test_iptal_nedenleri_listesi_property(self, sepet_id):
        """
        İptal nedenleri listesi özellik testi
        
        İptal nedenleri listesi her zaman geçerli nedenler içermeli
        """
        # Act
        nedenler = self.iptal_service.iptal_nedenleri_listesi()
        
        # Assert
        # 1. Liste mevcut
        assert isinstance(nedenler, list)
        assert len(nedenler) > 0
        
        # 2. Tüm nedenler string
        for neden in nedenler:
            assert isinstance(neden, str)
            assert len(neden) > 0
        
        # 3. Beklenen nedenler mevcut
        beklenen_nedenler = [
            "Müşteri vazgeçti",
            "Yanlış ürün eklendi", 
            "Fiyat hatası",
            "Stok yetersizliği",
            "Ödeme problemi",
            "Sistem hatası",
            "Diğer"
        ]
        
        for beklenen in beklenen_nedenler:
            assert beklenen in nedenler
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=30)
    def test_iptal_istatistikleri_property(self, terminal_id):
        """
        İptal istatistikleri özellik testi
        
        İstatistikler her zaman geçerli format ve değerler içermeli
        """
        # Act
        istatistikler = self.iptal_service.iptal_istatistikleri(terminal_id)
        
        # Assert
        # 1. Gerekli alanlar mevcut
        gerekli_alanlar = [
            'toplam_iptal_sayisi',
            'basarili_iptal_sayisi', 
            'basarisiz_iptal_sayisi',
            'iptal_basari_orani',
            'ortalama_iptal_suresi'
        ]
        
        for alan in gerekli_alanlar:
            assert alan in istatistikler
        
        # 2. Değerler geçerli tipte
        assert isinstance(istatistikler['toplam_iptal_sayisi'], int)
        assert isinstance(istatistikler['basarili_iptal_sayisi'], int)
        assert isinstance(istatistikler['basarisiz_iptal_sayisi'], int)
        assert isinstance(istatistikler['iptal_basari_orani'], (int, float))
        assert isinstance(istatistikler['ortalama_iptal_suresi'], (int, float))
        
        # 3. Değerler mantıklı aralıkta
        assert istatistikler['toplam_iptal_sayisi'] >= 0
        assert istatistikler['basarili_iptal_sayisi'] >= 0
        assert istatistikler['basarisiz_iptal_sayisi'] >= 0
        assert 0 <= istatistikler['iptal_basari_orani'] <= 100
        assert istatistikler['ortalama_iptal_suresi'] >= 0


class TestSatisIptalValidasyonTests:
    """Satış iptal validasyon testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.mock_sepet_repository = Mock()
        self.mock_satis_repository = Mock()
        self.mock_stok_service = Mock()
        self.iptal_service = SatisIptalService(
            sepet_repository=self.mock_sepet_repository,
            satis_repository=self.mock_satis_repository,
            stok_service=self.mock_stok_service
        )
    
    def teardown_method(self):
        """Her test sonrası çalışır"""
        self.mock_sepet_repository.reset_mock()
        self.mock_satis_repository.reset_mock()
        self.mock_stok_service.reset_mock()
    
    @given(
        gecersiz_sepet_id=st.integers(max_value=0)
    )
    @settings(max_examples=30)
    def test_gecersiz_sepet_id_validasyonu(self, gecersiz_sepet_id):
        """Geçersiz sepet ID için validasyon hatası"""
        with pytest.raises(DogrulamaHatasi) as exc_info:
            self.iptal_service.iptal_nedeni_sorgula(gecersiz_sepet_id)
        
        assert "Sepet ID pozitif olmalıdır" in str(exc_info.value)
    
    @given(
        sepet_id=st.integers(min_value=1, max_value=10000),
        bos_neden=st.one_of(st.just(""), st.just("   "), st.just("\t\n"))
    )
    @settings(max_examples=30)
    def test_bos_iptal_nedeni_validasyonu(self, sepet_id, bos_neden):
        """Boş iptal nedeni için validasyon hatası"""
        with pytest.raises(DogrulamaHatasi) as exc_info:
            self.iptal_service.satis_iptal_et(sepet_id, bos_neden)
        
        assert "İptal nedeni boş olamaz" in str(exc_info.value)
    
    @given(
        sepet_id=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=30)
    def test_sepet_bulunamadi_validasyonu(self, sepet_id):
        """Sepet bulunamadığında validasyon hatası"""
        # Arrange
        self.mock_sepet_repository.sepet_getir.return_value = None
        
        # Act & Assert
        with pytest.raises(SontechHatasi) as exc_info:
            self.iptal_service.iptal_nedeni_sorgula(sepet_id)
        
        assert "Sepet bulunamadı" in str(exc_info.value)
    
    @given(
        sepet_id=st.integers(min_value=1, max_value=10000),
        iptal_nedeni=st.text(min_size=5, max_size=50)
    )
    @settings(max_examples=30)
    def test_zaten_iptal_edilmis_sepet_validasyonu(self, sepet_id, iptal_nedeni):
        """Zaten iptal edilmiş sepet için validasyon hatası"""
        # Arrange
        mock_sepet = {
            'id': sepet_id,
            'durum': SepetDurum.IPTAL.value
        }
        self.mock_sepet_repository.sepet_getir.return_value = mock_sepet
        
        # Act & Assert
        with pytest.raises(SontechHatasi) as exc_info:
            self.iptal_service.satis_iptal_et(sepet_id, iptal_nedeni)
        
        assert "Sepet zaten iptal edilmiş" in str(exc_info.value)
    
    @given(
        sepet_id=st.integers(min_value=1, max_value=10000),
        iptal_nedeni=st.text(min_size=5, max_size=50)
    )
    @settings(max_examples=30)
    def test_tamamlanmis_sepet_iptal_validasyonu(self, sepet_id, iptal_nedeni):
        """Tamamlanmış sepet iptal validasyon hatası"""
        # Arrange
        mock_sepet = {
            'id': sepet_id,
            'durum': SepetDurum.TAMAMLANDI.value
        }
        self.mock_sepet_repository.sepet_getir.return_value = mock_sepet
        
        # Act & Assert
        with pytest.raises(SontechHatasi) as exc_info:
            self.iptal_service.satis_iptal_et(sepet_id, iptal_nedeni)
        
        assert "Tamamlanmış sepet iptal edilemez" in str(exc_info.value)
    
    @given(
        gecersiz_terminal_id=st.integers(max_value=0),
        kasiyer_id=st.integers(min_value=1, max_value=1000)
    )
    @settings(max_examples=30)
    def test_gecersiz_terminal_id_yeni_satis_validasyonu(self, gecersiz_terminal_id, kasiyer_id):
        """Geçersiz terminal ID ile yeni satış hazırlama validasyon hatası"""
        with pytest.raises(DogrulamaHatasi) as exc_info:
            self.iptal_service.yeni_satis_hazirla(gecersiz_terminal_id, kasiyer_id)
        
        assert "Terminal ID pozitif olmalıdır" in str(exc_info.value)
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        gecersiz_kasiyer_id=st.integers(max_value=0)
    )
    @settings(max_examples=30)
    def test_gecersiz_kasiyer_id_yeni_satis_validasyonu(self, terminal_id, gecersiz_kasiyer_id):
        """Geçersiz kasiyer ID ile yeni satış hazırlama validasyon hatası"""
        with pytest.raises(DogrulamaHatasi) as exc_info:
            self.iptal_service.yeni_satis_hazirla(terminal_id, gecersiz_kasiyer_id)
        
        assert "Kasiyer ID pozitif olmalıdır" in str(exc_info.value)