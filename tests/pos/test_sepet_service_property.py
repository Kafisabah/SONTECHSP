# Version: 0.1.0
# Last Update: 2025-12-16
# Module: tests.pos.test_sepet_service_property
# Description: SepetService özellik tabanlı testleri
# Changelog:
# - İlk oluşturma

"""
SepetService Özellik Tabanlı Testleri

Bu modül SepetService'in özellik tabanlı testlerini içerir.
Hypothesis kütüphanesi kullanılarak rastgele verilerle test edilir.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch
from hypothesis import given, strategies as st, assume, settings

from sontechsp.uygulama.moduller.pos.servisler.sepet_service import (
    SepetService, BarkodHatasi, StokHatasi
)
from sontechsp.uygulama.moduller.pos.arayuzler import SepetDurum
from sontechsp.uygulama.cekirdek.hatalar import DogrulamaHatasi, SontechHatasi


class TestSepetServicePropertyTests:
    """SepetService özellik tabanlı testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        # Mock repository ve stok service
        self.mock_sepet_repository = Mock()
        self.mock_stok_service = Mock()
        
        # SepetService instance'ı oluştur
        self.sepet_service = SepetService(
            sepet_repository=self.mock_sepet_repository,
            stok_service=self.mock_stok_service
        )
    
    def teardown_method(self):
        """Her test sonrası çalışır"""
        # Mock'ları sıfırla
        self.mock_sepet_repository.reset_mock()
        self.mock_stok_service.reset_mock()
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        barkod=st.text(alphabet='0123456789', min_size=8, max_size=13),
        urun_id=st.integers(min_value=1, max_value=10000),
        birim_fiyat=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('999.99'), places=2)
    )
    @settings(max_examples=100)
    def test_property_3_gecersiz_barkod_hata_yonetimi(
        self, terminal_id, kasiyer_id, barkod, urun_id, birim_fiyat
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 3: Geçersiz Barkod Hata Yönetimi**
        **Validates: Requirements 1.4**
        
        Herhangi bir geçersiz barkod için, sistem hata mesajı göstermeli ve sepeti değiştirmemeli
        """
        # Arrange
        sepet_id = 1
        
        # Mock sepet bilgisi - aktif sepet
        mock_sepet = {
            'id': sepet_id,
            'terminal_id': terminal_id,
            'kasiyer_id': kasiyer_id,
            'durum': SepetDurum.AKTIF.value,
            'toplam_tutar': 0.0,
            'satirlar': []
        }
        
        self.mock_sepet_repository.sepet_getir.return_value = mock_sepet
        
        # Mock stok service - geçersiz barkod için None döner
        self.mock_stok_service.urun_bilgisi_getir.return_value = None
        
        # Act & Assert - Geçersiz barkod ile ürün ekleme denemesi
        with pytest.raises(BarkodHatasi) as exc_info:
            self.sepet_service.barkod_ekle(sepet_id, barkod)
        
        # Hata mesajı kontrolü
        assert "Geçersiz barkod" in str(exc_info.value)
        
        # Sepet değişmemiş olmalı (repository'ye ekleme çağrısı yapılmamalı)
        self.mock_sepet_repository.sepet_satiri_ekle.assert_not_called()
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        satir_id=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=100)
    def test_property_5_sepet_satiri_silme(
        self, terminal_id, kasiyer_id, satir_id
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 5: Sepet Satırı Silme**
        **Validates: Requirements 2.1**
        
        Herhangi bir sepet satırı için, silme işlemi seçili satırı sepetten kaldırmalı
        """
        # Arrange
        self.mock_sepet_repository.sepet_satiri_sil.return_value = True
        
        # Act
        sonuc = self.sepet_service.satir_sil(satir_id)
        
        # Assert
        # 1. Silme işlemi başarılı olmalı
        assert sonuc is True
        
        # 2. Repository'nin silme metodu çağrılmış olmalı
        self.mock_sepet_repository.sepet_satiri_sil.assert_called_with(satir_id)
    
    @given(
        satir_id=st.integers(min_value=1, max_value=10000),
        yeni_adet=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=100)
    def test_property_6_urun_adedi_degistirme(
        self, satir_id, yeni_adet
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 6: Ürün Adedi Değiştirme**
        **Validates: Requirements 2.2**
        
        Herhangi bir ürün için, adet değiştirme işlemi yeni adedi doğrulamalı ve sepet toplamını güncellemeli
        """
        # Arrange
        self.mock_sepet_repository.sepet_satiri_guncelle.return_value = True
        
        # Act
        sonuc = self.sepet_service.urun_adedi_degistir(satir_id, yeni_adet)
        
        # Assert
        # 1. Güncelleme işlemi başarılı olmalı
        assert sonuc is True
        
        # 2. Repository'nin güncelleme metodu doğru parametrelerle çağrılmış olmalı
        self.mock_sepet_repository.sepet_satiri_guncelle.assert_called_with(
            satir_id, yeni_adet
        )
    
    @given(
        sepet_id=st.integers(min_value=1, max_value=10000),
        toplam_tutar=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('9999.99'), places=2),
        indirim_orani=st.floats(min_value=0.0, max_value=0.9)  # %90'a kadar indirim
    )
    @settings(max_examples=100)
    def test_property_7_indirim_uygulama(
        self, sepet_id, toplam_tutar, indirim_orani
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 7: İndirim Uygulama**
        **Validates: Requirements 2.3**
        
        Herhangi bir indirim tutarı için, sistem indirim tutarını sepet toplamından düşmeli
        """
        # Arrange
        indirim_tutari = toplam_tutar * Decimal(str(indirim_orani))
        
        mock_sepet = {
            'id': sepet_id,
            'toplam_tutar': float(toplam_tutar),
            'satirlar': []
        }
        
        self.mock_sepet_repository.sepet_getir.return_value = mock_sepet
        
        # Act
        sonuc = self.sepet_service.indirim_uygula(sepet_id, indirim_tutari)
        
        # Assert
        # 1. İndirim uygulama başarılı olmalı
        assert sonuc is True
        
        # 2. İndirim tutarı sepet toplamından küçük veya eşit olmalı
        assert indirim_tutari <= toplam_tutar
        
        # 3. Repository'nin sepet getirme metodu çağrılmış olmalı
        self.mock_sepet_repository.sepet_getir.assert_called_with(sepet_id)
    
    @given(
        sepet_id=st.integers(min_value=1, max_value=10000)
    )
    @settings(max_examples=100)
    def test_property_8_sepet_bosaltma(
        self, sepet_id
    ):
        """
        **Feature: pos-cekirdek-modulu, Property 8: Sepet Boşaltma**
        **Validates: Requirements 2.4**
        
        Herhangi bir sepet durumu için, boşaltma işlemi tüm satırları temizlemeli ve toplamı sıfırlamalı
        """
        # Arrange
        self.mock_sepet_repository.sepet_bosalt.return_value = True
        
        # Act
        sonuc = self.sepet_service.sepet_bosalt(sepet_id)
        
        # Assert
        # 1. Boşaltma işlemi başarılı olmalı
        assert sonuc is True
        
        # 2. Repository'nin boşaltma metodu çağrılmış olmalı
        self.mock_sepet_repository.sepet_bosalt.assert_called_with(sepet_id)
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        barkod=st.text(alphabet='0123456789', min_size=8, max_size=13),
        urun_id=st.integers(min_value=1, max_value=10000),
        stok_miktari=st.integers(min_value=0, max_value=0)  # Stok yetersiz
    )
    @settings(max_examples=50)
    def test_property_stok_yetersizligi_kontrolu(
        self, terminal_id, kasiyer_id, barkod, urun_id, stok_miktari
    ):
        """
        Stok yetersizliği durumunda sistem uyarı vermeli ve satışa izin vermemeli
        """
        # Arrange
        sepet_id = 1
        
        mock_sepet = {
            'id': sepet_id,
            'terminal_id': terminal_id,
            'kasiyer_id': kasiyer_id,
            'durum': SepetDurum.AKTIF.value,
            'toplam_tutar': 0.0,
            'satirlar': []
        }
        
        mock_urun_bilgisi = {
            'id': urun_id,
            'ad': f'Test Ürün {urun_id}',
            'barkod': barkod,
            'satis_fiyati': 10.00,
            'stok_miktari': stok_miktari
        }
        
        self.mock_sepet_repository.sepet_getir.return_value = mock_sepet
        self.mock_stok_service.urun_bilgisi_getir.return_value = mock_urun_bilgisi
        self.mock_stok_service.stok_kontrol.return_value = False  # Stok yetersiz
        
        # Act & Assert
        with pytest.raises(StokHatasi) as exc_info:
            self.sepet_service.barkod_ekle(sepet_id, barkod)
        
        # Hata mesajı kontrolü
        assert "Stok yetersiz" in str(exc_info.value)
        
        # Sepete ekleme yapılmamalı
        self.mock_sepet_repository.sepet_satiri_ekle.assert_not_called()


class TestSepetServiceValidasyonTests:
    """SepetService validasyon testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.mock_sepet_repository = Mock()
        self.mock_stok_service = Mock()
        self.sepet_service = SepetService(
            sepet_repository=self.mock_sepet_repository,
            stok_service=self.mock_stok_service
        )
    
    def teardown_method(self):
        """Her test sonrası çalışır"""
        # Mock'ları sıfırla
        self.mock_sepet_repository.reset_mock()
        self.mock_stok_service.reset_mock()
    
    @given(
        terminal_id=st.integers(max_value=0),  # Geçersiz terminal ID
        kasiyer_id=st.integers(min_value=1, max_value=1000)
    )
    @settings(max_examples=50)
    def test_gecersiz_terminal_id_validasyonu(self, terminal_id, kasiyer_id):
        """Geçersiz terminal ID için validasyon hatası"""
        with pytest.raises(DogrulamaHatasi) as exc_info:
            self.sepet_service.yeni_sepet_olustur(terminal_id, kasiyer_id)
        
        assert "Terminal ID pozitif olmalıdır" in str(exc_info.value)
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(max_value=0)  # Geçersiz kasiyer ID
    )
    @settings(max_examples=50)
    def test_gecersiz_kasiyer_id_validasyonu(self, terminal_id, kasiyer_id):
        """Geçersiz kasiyer ID için validasyon hatası"""
        with pytest.raises(DogrulamaHatasi) as exc_info:
            self.sepet_service.yeni_sepet_olustur(terminal_id, kasiyer_id)
        
        assert "Kasiyer ID pozitif olmalıdır" in str(exc_info.value)
    
    @given(
        sepet_id=st.integers(min_value=1, max_value=10000),
        bos_barkod=st.sampled_from(["", "   ", "\t", "\n"])  # Boş barkod varyasyonları
    )
    @settings(max_examples=50)
    def test_bos_barkod_validasyonu(self, sepet_id, bos_barkod):
        """Boş barkod için validasyon hatası"""
        with pytest.raises(DogrulamaHatasi) as exc_info:
            self.sepet_service.barkod_ekle(sepet_id, bos_barkod)
        
        assert "Barkod boş olamaz" in str(exc_info.value)
    
    @given(
        satir_id=st.integers(max_value=0),  # Geçersiz satır ID
        yeni_adet=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=50)
    def test_gecersiz_satir_id_validasyonu(self, satir_id, yeni_adet):
        """Geçersiz satır ID için validasyon hatası"""
        with pytest.raises(DogrulamaHatasi) as exc_info:
            self.sepet_service.urun_adedi_degistir(satir_id, yeni_adet)
        
        assert "Satır ID pozitif olmalıdır" in str(exc_info.value)
    
    @given(
        satir_id=st.integers(min_value=1, max_value=10000),
        gecersiz_adet=st.integers(max_value=0)  # Geçersiz adet
    )
    @settings(max_examples=50)
    def test_gecersiz_adet_validasyonu(self, satir_id, gecersiz_adet):
        """Geçersiz adet için validasyon hatası"""
        with pytest.raises(DogrulamaHatasi) as exc_info:
            self.sepet_service.urun_adedi_degistir(satir_id, gecersiz_adet)
        
        assert "Adet pozitif olmalıdır" in str(exc_info.value)
    
    @given(
        sepet_id=st.integers(min_value=1, max_value=10000),
        toplam_tutar=st.decimals(min_value=Decimal('1.00'), max_value=Decimal('100.00'), places=2),
        asiri_indirim_orani=st.floats(min_value=1.1, max_value=2.0)  # %110-200 indirim
    )
    @settings(max_examples=50)
    def test_asiri_indirim_validasyonu(self, sepet_id, toplam_tutar, asiri_indirim_orani):
        """Aşırı indirim tutarı için validasyon hatası"""
        # Arrange
        indirim_tutari = toplam_tutar * Decimal(str(asiri_indirim_orani))
        
        mock_sepet = {
            'id': sepet_id,
            'toplam_tutar': float(toplam_tutar),
            'satirlar': []
        }
        
        self.mock_sepet_repository.sepet_getir.return_value = mock_sepet
        
        # Act & Assert
        with pytest.raises(DogrulamaHatasi) as exc_info:
            self.sepet_service.indirim_uygula(sepet_id, indirim_tutari)
        
        assert "İndirim tutarı sepet toplamından büyük olamaz" in str(exc_info.value)


class TestSepetServiceEntegrasyonTests:
    """SepetService entegrasyon testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.mock_sepet_repository = Mock()
        self.mock_stok_service = Mock()
        self.sepet_service = SepetService(
            sepet_repository=self.mock_sepet_repository,
            stok_service=self.mock_stok_service
        )
    
    def teardown_method(self):
        """Her test sonrası çalışır"""
        # Mock'ları sıfırla
        self.mock_sepet_repository.reset_mock()
        self.mock_stok_service.reset_mock()
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        barkod=st.text(alphabet='0123456789', min_size=8, max_size=13),
        urun_id=st.integers(min_value=1, max_value=10000),
        birim_fiyat=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('999.99'), places=2)
    )
    @settings(max_examples=50)
    def test_basarili_barkod_ekleme_akisi(
        self, terminal_id, kasiyer_id, barkod, urun_id, birim_fiyat
    ):
        """Başarılı barkod ekleme akışı testi"""
        # Arrange
        sepet_id = 1
        
        mock_sepet = {
            'id': sepet_id,
            'terminal_id': terminal_id,
            'kasiyer_id': kasiyer_id,
            'durum': SepetDurum.AKTIF.value,
            'toplam_tutar': 0.0,
            'satirlar': []
        }
        
        mock_urun_bilgisi = {
            'id': urun_id,
            'ad': f'Test Ürün {urun_id}',
            'barkod': barkod,
            'satis_fiyati': float(birim_fiyat),
            'stok_miktari': 100
        }
        
        self.mock_sepet_repository.sepet_getir.return_value = mock_sepet
        self.mock_stok_service.urun_bilgisi_getir.return_value = mock_urun_bilgisi
        self.mock_stok_service.stok_kontrol.return_value = True
        self.mock_sepet_repository.sepet_satiri_ekle.return_value = 1
        
        # Act
        sonuc = self.sepet_service.barkod_ekle(sepet_id, barkod)
        
        # Assert
        assert sonuc is True
        
        # Tüm servis çağrıları yapılmış olmalı
        self.mock_sepet_repository.sepet_getir.assert_called_with(sepet_id)
        self.mock_stok_service.urun_bilgisi_getir.assert_called_with(barkod)
        self.mock_stok_service.stok_kontrol.assert_called_with(urun_id, 1)
        self.mock_sepet_repository.sepet_satiri_ekle.assert_called_with(
            sepet_id=sepet_id,
            urun_id=urun_id,
            barkod=barkod,
            adet=1,
            birim_fiyat=birim_fiyat
        )
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000)
    )
    @settings(max_examples=50)
    def test_sepet_bulunamadi_durumu(self, terminal_id, kasiyer_id):
        """Sepet bulunamadığında hata fırlatma testi"""
        # Arrange
        sepet_id = 999999  # Var olmayan sepet ID
        barkod = "1234567890"
        
        self.mock_sepet_repository.sepet_getir.return_value = None
        
        # Act & Assert
        with pytest.raises(SontechHatasi) as exc_info:
            self.sepet_service.barkod_ekle(sepet_id, barkod)
        
        assert f"Sepet bulunamadı: {sepet_id}" in str(exc_info.value)
    
    @given(
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=1000),
        barkod=st.text(alphabet='0123456789', min_size=8, max_size=13)
    )
    @settings(max_examples=50)
    def test_sepet_aktif_degil_durumu(self, terminal_id, kasiyer_id, barkod):
        """Sepet aktif değilken hata fırlatma testi"""
        # Arrange
        sepet_id = 1
        
        mock_sepet = {
            'id': sepet_id,
            'terminal_id': terminal_id,
            'kasiyer_id': kasiyer_id,
            'durum': SepetDurum.TAMAMLANDI.value,  # Aktif değil
            'toplam_tutar': 0.0,
            'satirlar': []
        }
        
        self.mock_sepet_repository.sepet_getir.return_value = mock_sepet
        
        # Act & Assert
        with pytest.raises(DogrulamaHatasi) as exc_info:
            self.sepet_service.barkod_ekle(sepet_id, barkod)
        
        assert "Sepet aktif durumda değil" in str(exc_info.value)