# Version: 0.1.0
# Last Update: 2025-12-16
# Module: tests.pos.test_odeme_service_property
# Description: OdemeService özellik tabanlı testleri
# Changelog:
# - İlk oluşturma

"""
OdemeService Özellik Tabanlı Testleri

Bu modül OdemeService'in özellik tabanlı testlerini içerir.
Hypothesis kütüphanesi kullanılarak rastgele verilerle test edilir.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch
from hypothesis import given, strategies as st, assume, settings

from sontechsp.uygulama.moduller.pos.servisler.odeme_service import (
    OdemeService, OdemeHatasi
)
from sontechsp.uygulama.moduller.pos.arayuzler import SepetDurum, OdemeTuru
from sontechsp.uygulama.cekirdek.hatalar import DogrulamaHatasi, SontechHatasi


class TestOdemeServicePropertyTests:
    """OdemeService özellik tabanlı testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        # Mock repository'ler ve stok service
        self.mock_sepet_repository = Mock()
        self.mock_satis_repository = Mock()
        self.mock_stok_service = Mock()
        
        # OdemeService instance'ı oluştur
        self.odeme_service = OdemeService(
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
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        toplam_tutar=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('9999.99'), places=2),
        odeme_turu=st.sampled_from([OdemeTuru.NAKIT, OdemeTuru.KART, OdemeTuru.HAVALE])
    )
    @settings(max_examples=100)
    def test_property_11_odeme_tutari_eslesmesi(
        self, sepet_id, terminal_id, kasiyer_id, toplam_tutar, odeme_turu
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 11: Ödeme Tutarı Eşleşmesi**
        **Validates: Requirements 3.3**
        
        Herhangi bir sepet ve ödeme tutarı eşleşmesi için, sistem satışı onaylamalı ve stok düşümü yapmalı
        """
        # Arrange
        mock_sepet = {
            'id': sepet_id,
            'terminal_id': terminal_id,
            'kasiyer_id': kasiyer_id,
            'durum': SepetDurum.AKTIF.value,
            'toplam_tutar': float(toplam_tutar),
            'net_tutar': float(toplam_tutar),
            'satirlar': [
                {
                    'urun_id': 1,
                    'adet': 2,
                    'birim_fiyat': float(toplam_tutar / 2)
                }
            ]
        }
        
        self.mock_sepet_repository.sepet_getir.return_value = mock_sepet
        self.mock_satis_repository.satis_olustur.return_value = 1
        self.mock_satis_repository.satis_odeme_ekle.return_value = 1
        self.mock_satis_repository.satis_tamamla.return_value = True
        self.mock_sepet_repository.sepet_durum_guncelle.return_value = True
        self.mock_stok_service.stok_dusur.return_value = True
        
        # Act
        sonuc = self.odeme_service.tek_odeme_yap(sepet_id, odeme_turu, toplam_tutar)
        
        # Assert
        # 1. Ödeme başarılı olmalı
        assert sonuc is True
        
        # 2. Satış onaylanmış olmalı (satış oluşturulmuş)
        self.mock_satis_repository.satis_olustur.assert_called_with(
            sepet_id=sepet_id,
            terminal_id=terminal_id,
            kasiyer_id=kasiyer_id,
            toplam_tutar=toplam_tutar
        )
        
        # 3. Ödeme kaydı eklenmiş olmalı
        self.mock_satis_repository.satis_odeme_ekle.assert_called_with(
            satis_id=1,
            odeme_turu=odeme_turu,
            tutar=toplam_tutar
        )
        
        # 4. Stok düşümü yapılmış olmalı
        self.mock_stok_service.stok_dusur.assert_called_with(1, 2)
        
        # 5. Satış tamamlanmış olmalı
        self.mock_satis_repository.satis_tamamla.assert_called()
        
        # 6. Sepet durumu güncellenmiş olmalı
        self.mock_sepet_repository.sepet_durum_guncelle.assert_called_with(
            sepet_id, SepetDurum.TAMAMLANDI
        )
    
    @given(
        sepet_id=st.integers(min_value=1, max_value=10000),
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        toplam_tutar=st.decimals(min_value=Decimal('10.00'), max_value=Decimal('1000.00'), places=2),
        eksik_oran=st.floats(min_value=0.1, max_value=0.9)  # %10-90 eksik ödeme
    )
    @settings(max_examples=100)
    def test_property_12_yetersiz_odeme_kontrolu(
        self, sepet_id, terminal_id, kasiyer_id, toplam_tutar, eksik_oran
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 12: Yetersiz Ödeme Kontrolü**
        **Validates: Requirements 3.4**
        
        Herhangi bir yetersiz ödeme durumu için, sistem eksik tutarı bildirmeli ve satışı tamamlamamalı
        """
        # Arrange
        yetersiz_tutar = toplam_tutar * Decimal(str(eksik_oran))
        
        mock_sepet = {
            'id': sepet_id,
            'terminal_id': terminal_id,
            'kasiyer_id': kasiyer_id,
            'durum': SepetDurum.AKTIF.value,
            'toplam_tutar': float(toplam_tutar),
            'net_tutar': float(toplam_tutar),
            'satirlar': []
        }
        
        self.mock_sepet_repository.sepet_getir.return_value = mock_sepet
        
        # Act & Assert - Yetersiz ödeme ile ödeme denemesi
        with pytest.raises(OdemeHatasi) as exc_info:
            self.odeme_service.tek_odeme_yap(sepet_id, OdemeTuru.NAKIT, yetersiz_tutar)
        
        # Hata mesajı kontrolü
        assert "Ödeme tutarı sepet toplamına eşit değil" in str(exc_info.value)
        
        # Satış oluşturulmamalı
        self.mock_satis_repository.satis_olustur.assert_not_called()
        
        # Stok düşümü yapılmamalı
        self.mock_stok_service.stok_dusur.assert_not_called()
    
    @given(
        sepet_id=st.integers(min_value=1, max_value=10000),
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        toplam_tutar=st.decimals(min_value=Decimal('10.00'), max_value=Decimal('1000.00'), places=2),
        odeme_sayisi=st.integers(min_value=2, max_value=5)
    )
    @settings(max_examples=50)
    def test_parcali_odeme_basarili_akis(
        self, sepet_id, terminal_id, kasiyer_id, toplam_tutar, odeme_sayisi
    ):
        """
        Parçalı ödeme başarılı akış testi
        
        Herhangi bir parçalı ödeme kombinasyonu için, sistem birden fazla ödeme yöntemini kabul etmeli
        """
        # Arrange
        # Toplam tutarı parçalara böl
        parcalar = []
        kalan_tutar = toplam_tutar
        
        for i in range(odeme_sayisi - 1):
            parca = kalan_tutar / Decimal(str(odeme_sayisi - i))
            # Küsuratlı tutarları önlemek için yuvarla
            parca = parca.quantize(Decimal('0.01'))
            parcalar.append(parca)
            kalan_tutar -= parca
        
        # Son parça kalan tutarın tamamı
        parcalar.append(kalan_tutar)
        
        # Ödeme listesi oluştur
        odemeler = []
        odeme_turleri = [OdemeTuru.NAKIT, OdemeTuru.KART, OdemeTuru.HAVALE]
        
        for i, parca in enumerate(parcalar):
            odemeler.append({
                'turu': odeme_turleri[i % len(odeme_turleri)],
                'tutar': parca,
                'referans': f'REF{i+1}'
            })
        
        mock_sepet = {
            'id': sepet_id,
            'terminal_id': terminal_id,
            'kasiyer_id': kasiyer_id,
            'durum': SepetDurum.AKTIF.value,
            'toplam_tutar': float(toplam_tutar),
            'net_tutar': float(toplam_tutar),
            'satirlar': []
        }
        
        self.mock_sepet_repository.sepet_getir.return_value = mock_sepet
        self.mock_satis_repository.satis_olustur.return_value = 1
        self.mock_satis_repository.satis_odeme_ekle.return_value = 1
        self.mock_satis_repository.satis_tamamla.return_value = True
        self.mock_sepet_repository.sepet_durum_guncelle.return_value = True
        
        # Act
        sonuc = self.odeme_service.parcali_odeme_yap(sepet_id, odemeler)
        
        # Assert
        # 1. Parçalı ödeme başarılı olmalı
        assert sonuc is True
        
        # 2. Ödeme kayıtları eklenmiş olmalı
        self.mock_satis_repository.satis_odeme_ekle.assert_called()
        
        # 3. Satış tamamlanmış olmalı
        self.mock_satis_repository.satis_tamamla.assert_called()
    
    @given(
        sepet_id=st.integers(min_value=1, max_value=10000),
        toplam_tutar=st.decimals(min_value=Decimal('1.00'), max_value=Decimal('1000.00'), places=2),
        odeme_tutari=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('1000.00'), places=2)
    )
    @settings(max_examples=100)
    def test_odeme_tutari_kontrol_property(
        self, sepet_id, toplam_tutar, odeme_tutari
    ):
        """
        Ödeme tutarı kontrol özellik testi
        
        Herhangi bir ödeme tutarı için, kontrol sonucu doğru olmalı
        """
        # Arrange
        mock_sepet = {
            'id': sepet_id,
            'toplam_tutar': float(toplam_tutar),
            'net_tutar': float(toplam_tutar),
            'satirlar': []
        }
        
        self.mock_sepet_repository.sepet_getir.return_value = mock_sepet
        
        # Act
        sonuc = self.odeme_service.odeme_tutari_kontrol(sepet_id, odeme_tutari)
        
        # Assert
        assert 'gecerli' in sonuc
        assert 'mesaj' in sonuc
        assert 'eksik_tutar' in sonuc
        
        if odeme_tutari == toplam_tutar:
            assert sonuc['gecerli'] is True
            assert sonuc['eksik_tutar'] == Decimal('0.00')
        elif odeme_tutari < toplam_tutar:
            assert sonuc['gecerli'] is False
            assert sonuc['eksik_tutar'] == toplam_tutar - odeme_tutari
            assert 'Yetersiz ödeme' in sonuc['mesaj']
        else:
            assert sonuc['gecerli'] is False
            assert sonuc['eksik_tutar'] == Decimal('0.00')
            assert 'Fazla ödeme' in sonuc['mesaj']


class TestOdemeServiceValidasyonTests:
    """OdemeService validasyon testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.mock_sepet_repository = Mock()
        self.mock_satis_repository = Mock()
        self.mock_stok_service = Mock()
        self.odeme_service = OdemeService(
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
        sepet_id=st.integers(max_value=0),  # Geçersiz sepet ID
        tutar=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('100.00'), places=2)
    )
    @settings(max_examples=50)
    def test_gecersiz_sepet_id_validasyonu(self, sepet_id, tutar):
        """Geçersiz sepet ID için validasyon hatası"""
        with pytest.raises(DogrulamaHatasi) as exc_info:
            self.odeme_service.tek_odeme_yap(sepet_id, OdemeTuru.NAKIT, tutar)
        
        assert "Sepet ID pozitif olmalıdır" in str(exc_info.value)
    
    @given(
        sepet_id=st.integers(min_value=1, max_value=10000),
        gecersiz_tutar=st.decimals(min_value=Decimal('-100.00'), max_value=Decimal('0.00'), places=2)  # Negatif ve sıfır
    )
    @settings(max_examples=50)
    def test_gecersiz_tutar_validasyonu(self, sepet_id, gecersiz_tutar):
        """Geçersiz ödeme tutarı için validasyon hatası"""
        with pytest.raises(DogrulamaHatasi) as exc_info:
            self.odeme_service.tek_odeme_yap(sepet_id, OdemeTuru.NAKIT, gecersiz_tutar)
        
        # Hem geçersiz hem de pozitif olmayan tutarlar için hata mesajı kontrol et
        hata_mesaji = str(exc_info.value)
        assert ("Ödeme tutarı pozitif olmalıdır" in hata_mesaji or 
                "Ödeme tutarı geçersiz" in hata_mesaji)
    
    @given(
        sepet_id=st.integers(min_value=1, max_value=10000),
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        toplam_tutar=st.decimals(min_value=Decimal('1.00'), max_value=Decimal('100.00'), places=2)
    )
    @settings(max_examples=50)
    def test_sepet_aktif_degil_validasyonu(self, sepet_id, terminal_id, kasiyer_id, toplam_tutar):
        """Sepet aktif değilken validasyon hatası"""
        # Arrange
        mock_sepet = {
            'id': sepet_id,
            'terminal_id': terminal_id,
            'kasiyer_id': kasiyer_id,
            'durum': SepetDurum.TAMAMLANDI.value,  # Aktif değil
            'toplam_tutar': float(toplam_tutar),
            'net_tutar': float(toplam_tutar),
            'satirlar': []
        }
        
        self.mock_sepet_repository.sepet_getir.return_value = mock_sepet
        
        # Act & Assert
        with pytest.raises(DogrulamaHatasi) as exc_info:
            self.odeme_service.tek_odeme_yap(sepet_id, OdemeTuru.NAKIT, toplam_tutar)
        
        assert "Sepet aktif durumda değil" in str(exc_info.value)
    
    @given(
        sepet_id=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=50)
    def test_sepet_bulunamadi_validasyonu(self, sepet_id):
        """Sepet bulunamadığında validasyon hatası"""
        # Arrange
        self.mock_sepet_repository.sepet_getir.return_value = None
        
        # Act & Assert
        with pytest.raises(SontechHatasi) as exc_info:
            self.odeme_service.tek_odeme_yap(sepet_id, OdemeTuru.NAKIT, Decimal('10.00'))
        
        assert f"Sepet bulunamadı: {sepet_id}" in str(exc_info.value)
    
    @given(
        sepet_id=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=50)
    def test_bos_odeme_listesi_validasyonu(self, sepet_id):
        """Boş ödeme listesi için validasyon hatası"""
        with pytest.raises(DogrulamaHatasi) as exc_info:
            self.odeme_service.parcali_odeme_yap(sepet_id, [])
        
        assert "Ödeme listesi boş olamaz" in str(exc_info.value)


class TestOdemeServiceEntegrasyonTests:
    """OdemeService entegrasyon testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.mock_sepet_repository = Mock()
        self.mock_satis_repository = Mock()
        self.mock_stok_service = Mock()
        self.odeme_service = OdemeService(
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
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        toplam_tutar=st.decimals(min_value=Decimal('1.00'), max_value=Decimal('100.00'), places=2)
    )
    @settings(max_examples=50)
    def test_sepet_odeme_bilgisi_getir(self, sepet_id, terminal_id, kasiyer_id, toplam_tutar):
        """Sepet ödeme bilgisi getirme testi"""
        # Arrange
        indirim_tutari = toplam_tutar * Decimal('0.1')  # %10 indirim
        
        mock_sepet = {
            'id': sepet_id,
            'terminal_id': terminal_id,
            'kasiyer_id': kasiyer_id,
            'durum': SepetDurum.AKTIF.value,
            'toplam_tutar': float(toplam_tutar),
            'indirim_tutari': float(indirim_tutari),
            'satirlar': [{'id': 1}, {'id': 2}]  # 2 satır
        }
        
        self.mock_sepet_repository.sepet_getir.return_value = mock_sepet
        
        # Act
        bilgi = self.odeme_service.sepet_odeme_bilgisi_getir(sepet_id)
        
        # Assert
        assert bilgi['sepet_id'] == sepet_id
        assert bilgi['toplam_tutar'] == float(toplam_tutar)
        assert bilgi['indirim_tutari'] == float(indirim_tutari)
        assert bilgi['net_tutar'] == float(toplam_tutar - indirim_tutari)
        assert bilgi['satir_sayisi'] == 2
        assert bilgi['durum'] == SepetDurum.AKTIF.value
    
    @given(
        sepet_id=st.integers(min_value=1, max_value=10000),
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        toplam_tutar=st.decimals(min_value=Decimal('10.00'), max_value=Decimal('100.00'), places=2)
    )
    @settings(max_examples=30)
    def test_fis_numarasi_olusturma(self, sepet_id, terminal_id, kasiyer_id, toplam_tutar):
        """Fiş numarası oluşturma testi"""
        # Arrange
        mock_sepet = {
            'id': sepet_id,
            'terminal_id': terminal_id,
            'kasiyer_id': kasiyer_id,
            'durum': SepetDurum.AKTIF.value,
            'toplam_tutar': float(toplam_tutar),
            'net_tutar': float(toplam_tutar),
            'satirlar': []
        }
        
        self.mock_sepet_repository.sepet_getir.return_value = mock_sepet
        self.mock_satis_repository.satis_olustur.return_value = 123
        self.mock_satis_repository.satis_odeme_ekle.return_value = 1
        self.mock_satis_repository.satis_tamamla.return_value = True
        self.mock_sepet_repository.sepet_durum_guncelle.return_value = True
        
        # Act
        sonuc = self.odeme_service.tek_odeme_yap(sepet_id, OdemeTuru.NAKIT, toplam_tutar)
        
        # Assert
        assert sonuc is True
        
        # Fiş numarası ile satış tamamlanmış olmalı
        self.mock_satis_repository.satis_tamamla.assert_called()
        
        # Çağrılan fiş numarası formatını kontrol et
        call_args = self.mock_satis_repository.satis_tamamla.call_args
        fis_no = call_args[0][1]  # İkinci parametre fiş numarası
        
        # Fiş numarası formatı: YYYYMMDD-HHMMSS-SATISID
        assert len(fis_no.split('-')) == 3
        assert fis_no.endswith('-000123')  # Satış ID 123