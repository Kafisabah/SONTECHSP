# Version: 0.1.0
# Last Update: 2025-12-16
# Module: tests.pos.test_sepet_repository_unit
# Description: SepetRepository birim testleri
# Changelog:
# - İlk oluşturma

"""
SepetRepository Birim Testleri

Bu modül SepetRepository CRUD operasyonlarının birim testlerini içerir.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch

from sontechsp.uygulama.moduller.pos.repositories.sepet_repository import SepetRepository
from sontechsp.uygulama.moduller.pos.arayuzler import SepetDurum
from sontechsp.uygulama.cekirdek.hatalar import DogrulamaHatasi, SontechHatasi, VeritabaniHatasi


class TestSepetRepository:
    """SepetRepository birim testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.repository = SepetRepository()
    
    def test_sepet_olustur_basarili(self):
        """Başarılı sepet oluşturma testi"""
        # Arrange
        terminal_id = 1
        kasiyer_id = 1
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.sepet_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mevcut aktif sepet yok
            mock_session_instance.query.return_value.filter.return_value.first.return_value = None
            
            # Mock sepet objesi
            mock_sepet = Mock()
            mock_sepet.id = 123
            mock_session_instance.add.return_value = None
            mock_session_instance.commit.return_value = None
            
            # Validasyon fonksiyonunu mock'la
            with patch('sontechsp.uygulama.moduller.pos.repositories.sepet_repository.sepet_validasyon') as mock_validasyon:
                mock_validasyon.return_value = []  # Hata yok
                
                # Sepet sınıfını mock'la
                with patch('sontechsp.uygulama.moduller.pos.repositories.sepet_repository.Sepet') as mock_sepet_class:
                    mock_sepet_class.return_value = mock_sepet
                    
                    # Act
                    sonuc = self.repository.sepet_olustur(terminal_id, kasiyer_id)
                    
                    # Assert
                    assert sonuc == 123
                    mock_session_instance.add.assert_called_once()
                    mock_session_instance.commit.assert_called_once()
    
    def test_sepet_olustur_gecersiz_terminal_id(self):
        """Geçersiz terminal ID ile sepet oluşturma testi"""
        # Arrange & Act & Assert
        with pytest.raises(DogrulamaHatasi):
            self.repository.sepet_olustur(0, 1)
    
    def test_sepet_olustur_gecersiz_kasiyer_id(self):
        """Geçersiz kasiyer ID ile sepet oluşturma testi"""
        # Arrange & Act & Assert
        with pytest.raises(DogrulamaHatasi):
            self.repository.sepet_olustur(1, 0)
    
    def test_sepet_getir_basarili(self):
        """Başarılı sepet getirme testi"""
        # Arrange
        sepet_id = 1
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.sepet_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock sepet
            mock_sepet = Mock()
            mock_sepet.id = 1
            mock_sepet.terminal_id = 1
            mock_sepet.kasiyer_id = 1
            mock_sepet.durum = SepetDurum.AKTIF
            mock_sepet.toplam_tutar = Decimal('100.00')
            mock_sepet.indirim_tutari = Decimal('10.00')
            mock_sepet.net_tutar_hesapla.return_value = Decimal('90.00')
            mock_sepet.olusturma_tarihi = None
            mock_sepet.guncelleme_tarihi = None
            mock_sepet.satirlar = []
            
            mock_session_instance.query.return_value.options.return_value.filter.return_value.first.return_value = mock_sepet
            
            # Act
            sonuc = self.repository.sepet_getir(sepet_id)
            
            # Assert
            assert sonuc is not None
            assert sonuc['id'] == 1
            assert sonuc['terminal_id'] == 1
            assert sonuc['durum'] == 'aktif'
            assert sonuc['toplam_tutar'] == 100.0
            assert sonuc['net_tutar'] == 90.0
    
    def test_sepet_getir_bulunamadi(self):
        """Sepet bulunamadığında None döndürme testi"""
        # Arrange
        sepet_id = 999
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.sepet_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            mock_session_instance.query.return_value.options.return_value.filter.return_value.first.return_value = None
            
            # Act
            sonuc = self.repository.sepet_getir(sepet_id)
            
            # Assert
            assert sonuc is None
    
    def test_sepet_getir_gecersiz_id(self):
        """Geçersiz sepet ID ile getirme testi"""
        # Arrange & Act & Assert
        with pytest.raises(DogrulamaHatasi):
            self.repository.sepet_getir(0)
    
    def test_sepet_satiri_ekle_basarili(self):
        """Başarılı sepet satırı ekleme testi"""
        # Arrange
        sepet_id = 1
        urun_id = 1
        barkod = "1234567890"
        adet = 2
        birim_fiyat = Decimal('50.00')
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.sepet_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock sepet
            mock_sepet = Mock()
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_sepet
            
            # Mevcut satır yok
            mock_session_instance.query.return_value.filter.return_value.first.side_effect = [mock_sepet, None]
            
            # Yeni satır mock'u
            mock_satir = Mock()
            mock_satir.id = 456
            mock_session_instance.add.return_value = None
            mock_session_instance.flush.return_value = None
            mock_session_instance.commit.return_value = None
            
            # Act
            with patch('sontechsp.uygulama.moduller.pos.repositories.sepet_repository.sepet_satiri_validasyon') as mock_validasyon:
                mock_validasyon.return_value = []  # Hata yok
                with patch('sontechsp.uygulama.moduller.pos.repositories.sepet_repository.SepetSatiri') as mock_satir_class:
                    mock_satir_class.return_value = mock_satir
                    with patch.object(self.repository, '_sepet_toplam_guncelle'):
                        sonuc = self.repository.sepet_satiri_ekle(sepet_id, urun_id, barkod, adet, birim_fiyat)
            
            # Assert
            assert sonuc == 456
            mock_session_instance.add.assert_called_once()
            mock_session_instance.commit.assert_called_once()
    
    def test_sepet_satiri_ekle_gecersiz_parametreler(self):
        """Geçersiz parametrelerle sepet satırı ekleme testleri"""
        # Geçersiz sepet ID
        with pytest.raises(DogrulamaHatasi):
            self.repository.sepet_satiri_ekle(0, 1, "123", 1, Decimal('10.00'))
        
        # Geçersiz ürün ID
        with pytest.raises(DogrulamaHatasi):
            self.repository.sepet_satiri_ekle(1, 0, "123", 1, Decimal('10.00'))
        
        # Boş barkod
        with pytest.raises(DogrulamaHatasi):
            self.repository.sepet_satiri_ekle(1, 1, "", 1, Decimal('10.00'))
        
        # Geçersiz adet
        with pytest.raises(DogrulamaHatasi):
            self.repository.sepet_satiri_ekle(1, 1, "123", 0, Decimal('10.00'))
        
        # Geçersiz birim fiyat
        with pytest.raises(DogrulamaHatasi):
            self.repository.sepet_satiri_ekle(1, 1, "123", 1, Decimal('0.00'))
    
    def test_sepet_satiri_guncelle_basarili(self):
        """Başarılı sepet satırı güncelleme testi"""
        # Arrange
        satir_id = 1
        yeni_adet = 5
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.sepet_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock satır
            mock_satir = Mock()
            mock_satir.sepet_id = 1
            mock_satir.toplam_tutar_guncelle.return_value = None
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_satir
            
            mock_session_instance.commit.return_value = None
            
            # Act
            with patch('sontechsp.uygulama.moduller.pos.repositories.sepet_repository.sepet_satiri_validasyon') as mock_validasyon:
                mock_validasyon.return_value = []  # Hata yok
                with patch.object(self.repository, '_sepet_toplam_guncelle'):
                    sonuc = self.repository.sepet_satiri_guncelle(satir_id, yeni_adet)
            
            # Assert
            assert sonuc is True
            assert mock_satir.adet == yeni_adet
            mock_satir.toplam_tutar_guncelle.assert_called_once()
            mock_session_instance.commit.assert_called_once()
    
    def test_sepet_satiri_sil_basarili(self):
        """Başarılı sepet satırı silme testi"""
        # Arrange
        satir_id = 1
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.sepet_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock satır
            mock_satir = Mock()
            mock_satir.sepet_id = 1
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_satir
            
            mock_session_instance.delete.return_value = None
            mock_session_instance.commit.return_value = None
            
            # Act
            with patch.object(self.repository, '_sepet_toplam_guncelle'):
                sonuc = self.repository.sepet_satiri_sil(satir_id)
            
            # Assert
            assert sonuc is True
            mock_session_instance.delete.assert_called_once_with(mock_satir)
            mock_session_instance.commit.assert_called_once()
    
    def test_sepet_bosalt_basarili(self):
        """Başarılı sepet boşaltma testi"""
        # Arrange
        sepet_id = 1
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.sepet_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock sepet
            mock_sepet = Mock()
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_sepet
            
            # Mock satır silme
            mock_session_instance.query.return_value.filter.return_value.delete.return_value = 3
            mock_session_instance.commit.return_value = None
            
            # Act
            sonuc = self.repository.sepet_bosalt(sepet_id)
            
            # Assert
            assert sonuc is True
            assert mock_sepet.toplam_tutar == Decimal('0.00')
            assert mock_sepet.indirim_tutari == Decimal('0.00')
            mock_session_instance.commit.assert_called_once()
    
    def test_terminal_aktif_sepet_getir_basarili(self):
        """Terminal için aktif sepet getirme testi"""
        # Arrange
        terminal_id = 1
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.sepet_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock aktif sepet
            mock_sepet = Mock()
            mock_sepet.id = 123
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_sepet
            
            # Act
            with patch.object(self.repository, 'sepet_getir', return_value={'id': 123}) as mock_getir:
                sonuc = self.repository.terminal_aktif_sepet_getir(terminal_id)
            
            # Assert
            assert sonuc == {'id': 123}
            mock_getir.assert_called_once_with(123)
    
    def test_sepet_durum_guncelle_basarili(self):
        """Başarılı sepet durum güncelleme testi"""
        # Arrange
        sepet_id = 1
        yeni_durum = SepetDurum.TAMAMLANDI
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.sepet_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock sepet
            mock_sepet = Mock()
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_sepet
            mock_session_instance.commit.return_value = None
            
            # Act
            with patch('sontechsp.uygulama.moduller.pos.repositories.sepet_repository.sepet_validasyon') as mock_validasyon:
                mock_validasyon.return_value = []  # Hata yok
                sonuc = self.repository.sepet_durum_guncelle(sepet_id, yeni_durum)
            
            # Assert
            assert sonuc is True
            assert mock_sepet.durum == yeni_durum
            mock_session_instance.commit.assert_called_once()