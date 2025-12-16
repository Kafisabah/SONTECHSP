# Version: 0.1.0
# Last Update: 2025-12-16
# Module: tests.pos.test_iade_repository_unit
# Description: IadeRepository birim testleri
# Changelog:
# - İlk oluşturma

"""
IadeRepository Birim Testleri

Bu modül IadeRepository doğrulama testlerini içerir.
"""

import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, patch

from sontechsp.uygulama.moduller.pos.repositories.iade_repository import IadeRepository
from sontechsp.uygulama.moduller.pos.arayuzler import SatisDurum
from sontechsp.uygulama.cekirdek.hatalar import DogrulamaHatasi, SontechHatasi, VeritabaniHatasi


class TestIadeRepository:
    """IadeRepository birim testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.repository = IadeRepository()
    
    def test_iade_olustur_basarili(self):
        """Başarılı iade oluşturma testi"""
        # Arrange
        orijinal_satis_id = 1
        terminal_id = 1
        kasiyer_id = 1
        neden = "Ürün hasarlı"
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.iade_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock orijinal satış
            mock_satis = Mock()
            mock_satis.durum = SatisDurum.TAMAMLANDI
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_satis
            
            # Yeni iade mock'u
            mock_iade = Mock()
            mock_iade.id = 123
            mock_session_instance.add.return_value = None
            mock_session_instance.commit.return_value = None
            
            # Act
            with patch('sontechsp.uygulama.moduller.pos.repositories.iade_repository.Iade') as mock_iade_class:
                mock_iade_class.return_value = mock_iade
                sonuc = self.repository.iade_olustur(orijinal_satis_id, terminal_id, kasiyer_id, neden)
            
            # Assert
            assert sonuc == 123
            mock_session_instance.add.assert_called_once()
            mock_session_instance.commit.assert_called_once()
    
    def test_iade_olustur_gecersiz_parametreler(self):
        """Geçersiz parametrelerle iade oluşturma testleri"""
        # Geçersiz orijinal satış ID
        with pytest.raises(DogrulamaHatasi, match="Orijinal satış ID pozitif olmalıdır"):
            self.repository.iade_olustur(0, 1, 1, "Test")
        
        # Geçersiz terminal ID
        with pytest.raises(DogrulamaHatasi, match="Terminal ID pozitif olmalıdır"):
            self.repository.iade_olustur(1, 0, 1, "Test")
        
        # Geçersiz kasiyer ID
        with pytest.raises(DogrulamaHatasi, match="Kasiyer ID pozitif olmalıdır"):
            self.repository.iade_olustur(1, 1, 0, "Test")
        
        # Boş iade nedeni
        with pytest.raises(DogrulamaHatasi, match="İade nedeni boş olamaz"):
            self.repository.iade_olustur(1, 1, 1, "")
    
    def test_iade_olustur_orijinal_satis_bulunamadi(self):
        """Orijinal satış bulunamadığında iade oluşturma testi"""
        # Arrange
        orijinal_satis_id = 999
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.iade_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Orijinal satış bulunamadı
            mock_session_instance.query.return_value.filter.return_value.first.return_value = None
            
            # Act & Assert
            with pytest.raises(SontechHatasi, match="Orijinal satış bulunamadı: 999"):
                self.repository.iade_olustur(orijinal_satis_id, 1, 1, "Test")
    
    def test_iade_olustur_tamamlanmamis_satis(self):
        """Tamamlanmamış satış için iade oluşturma testi"""
        # Arrange
        orijinal_satis_id = 1
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.iade_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock tamamlanmamış satış
            mock_satis = Mock()
            mock_satis.durum = SatisDurum.BEKLEMEDE
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_satis
            
            # Act & Assert
            with pytest.raises(SontechHatasi, match="Sadece tamamlanan satışlar iade edilebilir"):
                self.repository.iade_olustur(orijinal_satis_id, 1, 1, "Test")
    
    def test_iade_getir_basarili(self):
        """Başarılı iade getirme testi"""
        # Arrange
        iade_id = 1
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.iade_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock iade
            mock_iade = Mock()
            mock_iade.id = 1
            mock_iade.orijinal_satis_id = 1
            mock_iade.terminal_id = 1
            mock_iade.kasiyer_id = 1
            mock_iade.iade_tarihi = datetime(2025, 12, 16, 10, 0, 0)
            mock_iade.toplam_tutar = Decimal('50.00')
            mock_iade.neden = "Ürün hasarlı"
            mock_iade.musteri_id = None
            mock_iade.notlar = None
            mock_iade.fis_no = None
            mock_iade.olusturma_tarihi = None
            mock_iade.guncelleme_tarihi = None
            mock_iade.satirlar = []
            mock_iade.satir_sayisi.return_value = 0
            mock_iade.toplam_adet.return_value = 0
            mock_iade.hesaplanan_toplam_tutar.return_value = Decimal('0.00')
            
            mock_session_instance.query.return_value.options.return_value.filter.return_value.first.return_value = mock_iade
            
            # Act
            sonuc = self.repository.iade_getir(iade_id)
            
            # Assert
            assert sonuc is not None
            assert sonuc['id'] == 1
            assert sonuc['orijinal_satis_id'] == 1
            assert sonuc['neden'] == "Ürün hasarlı"
            assert sonuc['toplam_tutar'] == 50.0
    
    def test_iade_satiri_ekle_basarili(self):
        """Başarılı iade satırı ekleme testi"""
        # Arrange
        iade_id = 1
        urun_id = 1
        barkod = "1234567890"
        urun_adi = "Test Ürün"
        adet = 2
        birim_fiyat = Decimal('25.00')
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.iade_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock iade
            mock_iade = Mock()
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_iade
            
            # Yeni satır mock'u
            mock_satir = Mock()
            mock_satir.id = 456
            mock_session_instance.add.return_value = None
            mock_session_instance.flush.return_value = None
            mock_session_instance.commit.return_value = None
            
            # Act
            with patch('sontechsp.uygulama.moduller.pos.repositories.iade_repository.IadeSatiri') as mock_satir_class:
                mock_satir_class.return_value = mock_satir
                with patch.object(self.repository, '_iade_toplam_guncelle'):
                    sonuc = self.repository.iade_satiri_ekle(iade_id, urun_id, barkod, urun_adi, adet, birim_fiyat)
            
            # Assert
            assert sonuc == 456
            mock_session_instance.add.assert_called_once()
            mock_session_instance.commit.assert_called_once()
    
    def test_iade_satiri_ekle_gecersiz_parametreler(self):
        """Geçersiz parametrelerle iade satırı ekleme testleri"""
        # Geçersiz iade ID
        with pytest.raises(DogrulamaHatasi, match="İade ID pozitif olmalıdır"):
            self.repository.iade_satiri_ekle(0, 1, "123", "Test", 1, Decimal('10.00'))
        
        # Geçersiz ürün ID
        with pytest.raises(DogrulamaHatasi, match="Ürün ID pozitif olmalıdır"):
            self.repository.iade_satiri_ekle(1, 0, "123", "Test", 1, Decimal('10.00'))
        
        # Boş barkod
        with pytest.raises(DogrulamaHatasi, match="Barkod boş olamaz"):
            self.repository.iade_satiri_ekle(1, 1, "", "Test", 1, Decimal('10.00'))
        
        # Boş ürün adı
        with pytest.raises(DogrulamaHatasi, match="Ürün adı boş olamaz"):
            self.repository.iade_satiri_ekle(1, 1, "123", "", 1, Decimal('10.00'))
        
        # Geçersiz adet
        with pytest.raises(DogrulamaHatasi, match="Adet pozitif olmalıdır"):
            self.repository.iade_satiri_ekle(1, 1, "123", "Test", 0, Decimal('10.00'))
        
        # Negatif birim fiyat
        with pytest.raises(DogrulamaHatasi, match="Birim fiyat negatif olamaz"):
            self.repository.iade_satiri_ekle(1, 1, "123", "Test", 1, Decimal('-10.00'))
    
    def test_iade_satiri_guncelle_basarili(self):
        """Başarılı iade satırı güncelleme testi"""
        # Arrange
        satir_id = 1
        yeni_adet = 3
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.iade_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock satır
            mock_satir = Mock()
            mock_satir.iade_id = 1
            mock_satir.toplam_tutar_guncelle.return_value = None
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_satir
            
            mock_session_instance.commit.return_value = None
            
            # Act
            with patch.object(self.repository, '_iade_toplam_guncelle'):
                sonuc = self.repository.iade_satiri_guncelle(satir_id, yeni_adet)
            
            # Assert
            assert sonuc is True
            assert mock_satir.adet == yeni_adet
            mock_satir.toplam_tutar_guncelle.assert_called_once()
            mock_session_instance.commit.assert_called_once()
    
    def test_iade_satiri_sil_basarili(self):
        """Başarılı iade satırı silme testi"""
        # Arrange
        satir_id = 1
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.iade_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock satır
            mock_satir = Mock()
            mock_satir.iade_id = 1
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_satir
            
            mock_session_instance.delete.return_value = None
            mock_session_instance.commit.return_value = None
            
            # Act
            with patch.object(self.repository, '_iade_toplam_guncelle'):
                sonuc = self.repository.iade_satiri_sil(satir_id)
            
            # Assert
            assert sonuc is True
            mock_session_instance.delete.assert_called_once_with(mock_satir)
            mock_session_instance.commit.assert_called_once()
    
    def test_orijinal_satis_dogrula_basarili(self):
        """Başarılı orijinal satış doğrulama testi"""
        # Arrange
        satis_id = 1
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.iade_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock satış
            mock_satis = Mock()
            mock_satis.id = 1
            mock_satis.fis_no = "F001"
            mock_satis.satis_tarihi = datetime(2025, 12, 16, 10, 0, 0)
            mock_satis.toplam_tutar = Decimal('100.00')
            mock_satis.indirim_tutari = Decimal('10.00')
            mock_satis.net_tutar_hesapla.return_value = Decimal('90.00')
            mock_satis.durum = SatisDurum.TAMAMLANDI
            
            # Mock mevcut iadeler
            mock_iade = Mock()
            mock_iade.toplam_tutar = Decimal('20.00')
            
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_satis
            mock_session_instance.query.return_value.filter.return_value.all.return_value = [mock_iade]
            
            # Act
            sonuc = self.repository.orijinal_satis_dogrula(satis_id)
            
            # Assert
            assert sonuc['satis_id'] == 1
            assert sonuc['fis_no'] == "F001"
            assert sonuc['net_tutar'] == 90.0
            assert sonuc['iade_edilebilir'] is True
            assert sonuc['toplam_iade_tutari'] == 20.0
            assert sonuc['kalan_iade_tutari'] == 70.0
    
    def test_iade_listesi_getir_basarili(self):
        """Başarılı iade listesi getirme testi"""
        # Arrange
        terminal_id = 1
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.iade_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock iade listesi
            mock_iade = Mock()
            mock_iade.id = 1
            mock_iade.orijinal_satis_id = 1
            mock_iade.terminal_id = 1
            mock_iade.kasiyer_id = 1
            mock_iade.iade_tarihi = datetime(2025, 12, 16, 10, 0, 0)
            mock_iade.toplam_tutar = Decimal('50.00')
            mock_iade.neden = "Test"
            mock_iade.fis_no = None
            mock_iade.musteri_id = None
            mock_iade.satir_sayisi.return_value = 1
            mock_iade.toplam_adet.return_value = 2
            
            mock_query = mock_session_instance.query.return_value.options.return_value
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.offset.return_value = mock_query
            mock_query.limit.return_value = mock_query
            mock_query.all.return_value = [mock_iade]
            
            # Act
            sonuc = self.repository.iade_listesi_getir(terminal_id=terminal_id, limit=10)
            
            # Assert
            assert len(sonuc) == 1
            assert sonuc[0]['id'] == 1
            assert sonuc[0]['terminal_id'] == 1
            assert sonuc[0]['neden'] == "Test"
    
    def test_iade_fis_no_guncelle_basarili(self):
        """Başarılı iade fiş numarası güncelleme testi"""
        # Arrange
        iade_id = 1
        fis_no = "IF001"
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.iade_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock iade
            mock_iade = Mock()
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_iade
            mock_session_instance.commit.return_value = None
            
            # Act
            sonuc = self.repository.iade_fis_no_guncelle(iade_id, fis_no)
            
            # Assert
            assert sonuc is True
            assert mock_iade.fis_no == fis_no
            mock_session_instance.commit.assert_called_once()