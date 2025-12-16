# Version: 0.1.0
# Last Update: 2025-12-16
# Module: tests.pos.test_satis_repository_unit
# Description: SatisRepository birim testleri
# Changelog:
# - İlk oluşturma

"""
SatisRepository Birim Testleri

Bu modül SatisRepository transaction testlerini içerir.
"""

import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, patch

from sontechsp.uygulama.moduller.pos.repositories.satis_repository import SatisRepository
from sontechsp.uygulama.moduller.pos.arayuzler import SatisDurum, OdemeTuru
from sontechsp.uygulama.cekirdek.hatalar import DogrulamaHatasi, SontechHatasi, VeritabaniHatasi


class TestSatisRepository:
    """SatisRepository birim testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.repository = SatisRepository()
    
    def test_satis_olustur_basarili(self):
        """Başarılı satış oluşturma testi"""
        # Arrange
        sepet_id = 1
        terminal_id = 1
        kasiyer_id = 1
        toplam_tutar = Decimal('100.00')
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.satis_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Yeni satış mock'u
            mock_satis = Mock()
            mock_satis.id = 123
            mock_session_instance.add.return_value = None
            mock_session_instance.commit.return_value = None
            
            # Act
            with patch('sontechsp.uygulama.moduller.pos.repositories.satis_repository.Satis') as mock_satis_class:
                mock_satis_class.return_value = mock_satis
                sonuc = self.repository.satis_olustur(sepet_id, terminal_id, kasiyer_id, toplam_tutar)
            
            # Assert
            assert sonuc == 123
            mock_session_instance.add.assert_called_once()
            mock_session_instance.commit.assert_called_once()
    
    def test_satis_olustur_gecersiz_parametreler(self):
        """Geçersiz parametrelerle satış oluşturma testleri"""
        # Geçersiz sepet ID
        with pytest.raises(DogrulamaHatasi, match="Sepet ID pozitif olmalıdır"):
            self.repository.satis_olustur(0, 1, 1, Decimal('100.00'))
        
        # Geçersiz terminal ID
        with pytest.raises(DogrulamaHatasi, match="Terminal ID pozitif olmalıdır"):
            self.repository.satis_olustur(1, 0, 1, Decimal('100.00'))
        
        # Geçersiz kasiyer ID
        with pytest.raises(DogrulamaHatasi, match="Kasiyer ID pozitif olmalıdır"):
            self.repository.satis_olustur(1, 1, 0, Decimal('100.00'))
        
        # Negatif toplam tutar
        with pytest.raises(DogrulamaHatasi, match="Toplam tutar negatif olamaz"):
            self.repository.satis_olustur(1, 1, 1, Decimal('-10.00'))
    
    def test_satis_getir_basarili(self):
        """Başarılı satış getirme testi"""
        # Arrange
        satis_id = 1
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.satis_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock satış
            mock_satis = Mock()
            mock_satis.id = 1
            mock_satis.sepet_id = 1
            mock_satis.terminal_id = 1
            mock_satis.kasiyer_id = 1
            mock_satis.satis_tarihi = datetime(2025, 12, 16, 10, 0, 0)
            mock_satis.toplam_tutar = Decimal('100.00')
            mock_satis.indirim_tutari = Decimal('10.00')
            mock_satis.net_tutar_hesapla.return_value = Decimal('90.00')
            mock_satis.durum = SatisDurum.TAMAMLANDI
            mock_satis.fis_no = "F001"
            mock_satis.musteri_id = None
            mock_satis.notlar = None
            mock_satis.olusturma_tarihi = None
            mock_satis.guncelleme_tarihi = None
            mock_satis.odemeler = []
            mock_satis.toplam_odeme_tutari.return_value = Decimal('90.00')
            mock_satis.odeme_tamamlandi_mi.return_value = True
            mock_satis.kalan_tutar.return_value = Decimal('0.00')
            
            mock_session_instance.query.return_value.options.return_value.filter.return_value.first.return_value = mock_satis
            
            # Act
            sonuc = self.repository.satis_getir(satis_id)
            
            # Assert
            assert sonuc is not None
            assert sonuc['id'] == 1
            assert sonuc['sepet_id'] == 1
            assert sonuc['durum'] == 'tamamlandi'
            assert sonuc['toplam_tutar'] == 100.0
            assert sonuc['net_tutar'] == 90.0
            assert sonuc['odeme_tamamlandi'] is True
    
    def test_odeme_ekle_basarili(self):
        """Başarılı ödeme ekleme testi"""
        # Arrange
        satis_id = 1
        odeme_turu = OdemeTuru.NAKIT
        tutar = Decimal('50.00')
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.satis_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock satış
            mock_satis = Mock()
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_satis
            
            # Yeni ödeme mock'u
            mock_odeme = Mock()
            mock_odeme.id = 456
            mock_session_instance.add.return_value = None
            mock_session_instance.commit.return_value = None
            
            # Act
            with patch('sontechsp.uygulama.moduller.pos.repositories.satis_repository.SatisOdeme') as mock_odeme_class:
                mock_odeme_class.return_value = mock_odeme
                sonuc = self.repository.odeme_ekle(satis_id, odeme_turu, tutar)
            
            # Assert
            assert sonuc == 456
            mock_session_instance.add.assert_called_once()
            mock_session_instance.commit.assert_called_once()
    
    def test_odeme_ekle_satis_bulunamadi(self):
        """Satış bulunamadığında ödeme ekleme testi"""
        # Arrange
        satis_id = 999
        odeme_turu = OdemeTuru.NAKIT
        tutar = Decimal('50.00')
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.satis_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Satış bulunamadı
            mock_session_instance.query.return_value.filter.return_value.first.return_value = None
            
            # Act & Assert
            with pytest.raises(SontechHatasi, match="Satış bulunamadı: 999"):
                self.repository.odeme_ekle(satis_id, odeme_turu, tutar)
    
    def test_satis_durum_guncelle_basarili(self):
        """Başarılı satış durum güncelleme testi"""
        # Arrange
        satis_id = 1
        yeni_durum = SatisDurum.TAMAMLANDI
        fis_no = "F001"
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.satis_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock satış
            mock_satis = Mock()
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_satis
            mock_session_instance.commit.return_value = None
            
            # Act
            sonuc = self.repository.satis_durum_guncelle(satis_id, yeni_durum, fis_no)
            
            # Assert
            assert sonuc is True
            assert mock_satis.durum == yeni_durum
            assert mock_satis.fis_no == fis_no
            mock_session_instance.commit.assert_called_once()
    
    def test_satis_durum_guncelle_tamamlandi_fis_no_gerekli(self):
        """Tamamlanan satış için fiş numarası gerekli testi"""
        # Arrange & Act & Assert
        with pytest.raises(DogrulamaHatasi, match="Tamamlanan satış için fiş numarası gereklidir"):
            self.repository.satis_durum_guncelle(1, SatisDurum.TAMAMLANDI)
    
    def test_satis_listesi_getir_basarili(self):
        """Başarılı satış listesi getirme testi"""
        # Arrange
        terminal_id = 1
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.satis_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock satış listesi
            mock_satis1 = Mock()
            mock_satis1.id = 1
            mock_satis1.sepet_id = 1
            mock_satis1.terminal_id = 1
            mock_satis1.kasiyer_id = 1
            mock_satis1.satis_tarihi = datetime(2025, 12, 16, 10, 0, 0)
            mock_satis1.toplam_tutar = Decimal('100.00')
            mock_satis1.indirim_tutari = Decimal('10.00')
            mock_satis1.net_tutar_hesapla.return_value = Decimal('90.00')
            mock_satis1.durum = SatisDurum.TAMAMLANDI
            mock_satis1.fis_no = "F001"
            mock_satis1.musteri_id = None
            mock_satis1.toplam_odeme_tutari.return_value = Decimal('90.00')
            mock_satis1.odeme_tamamlandi_mi.return_value = True
            
            mock_query = mock_session_instance.query.return_value.options.return_value
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.offset.return_value = mock_query
            mock_query.limit.return_value = mock_query
            mock_query.all.return_value = [mock_satis1]
            
            # Act
            sonuc = self.repository.satis_listesi_getir(terminal_id=terminal_id, limit=10)
            
            # Assert
            assert len(sonuc) == 1
            assert sonuc[0]['id'] == 1
            assert sonuc[0]['terminal_id'] == 1
            assert sonuc[0]['durum'] == 'tamamlandi'
    
    def test_fis_no_ile_satis_getir_basarili(self):
        """Fiş numarası ile satış getirme testi"""
        # Arrange
        fis_no = "F001"
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.satis_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock satış
            mock_satis = Mock()
            mock_satis.id = 123
            mock_session_instance.query.return_value.options.return_value.filter.return_value.first.return_value = mock_satis
            
            # Act
            with patch.object(self.repository, 'satis_getir', return_value={'id': 123}) as mock_getir:
                sonuc = self.repository.fis_no_ile_satis_getir(fis_no)
            
            # Assert
            assert sonuc == {'id': 123}
            mock_getir.assert_called_once_with(123)
    
    def test_satis_iptal_et_basarili(self):
        """Başarılı satış iptal etme testi"""
        # Arrange
        satis_id = 1
        iptal_nedeni = "Müşteri talebi"
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.satis_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock satış
            mock_satis = Mock()
            mock_satis.durum = SatisDurum.TAMAMLANDI
            mock_satis.notlar = None
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_satis
            mock_session_instance.commit.return_value = None
            
            # Act
            sonuc = self.repository.satis_iptal_et(satis_id, iptal_nedeni)
            
            # Assert
            assert sonuc is True
            assert mock_satis.durum == SatisDurum.IPTAL
            assert "İPTAL: Müşteri talebi" in mock_satis.notlar
            mock_session_instance.commit.assert_called_once()
    
    def test_satis_iptal_et_zaten_iptal(self):
        """Zaten iptal edilmiş satış iptal etme testi"""
        # Arrange
        satis_id = 1
        iptal_nedeni = "Test"
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.satis_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock iptal edilmiş satış
            mock_satis = Mock()
            mock_satis.durum = SatisDurum.IPTAL
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_satis
            
            # Act & Assert
            with pytest.raises(SontechHatasi, match="Satış zaten iptal edilmiş"):
                self.repository.satis_iptal_et(satis_id, iptal_nedeni)
    
    def test_gunluk_satis_ozeti_basarili(self):
        """Başarılı günlük satış özeti testi"""
        # Arrange
        terminal_id = 1
        tarih = datetime(2025, 12, 16, 15, 30, 0)
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.satis_repository.postgresql_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock satış listesi
            mock_satis = Mock()
            mock_satis.net_tutar_hesapla.return_value = Decimal('90.00')
            mock_satis.indirim_tutari = Decimal('10.00')
            mock_satis.odemeler = []
            
            mock_session_instance.query.return_value.filter.return_value.all.return_value = [mock_satis]
            
            # Act
            sonuc = self.repository.gunluk_satis_ozeti(terminal_id, tarih)
            
            # Assert
            assert sonuc['terminal_id'] == terminal_id
            assert sonuc['tarih'] == '2025-12-16'
            assert sonuc['toplam_satis_sayisi'] == 1
            assert sonuc['toplam_tutar'] == 90.0
            assert sonuc['toplam_indirim'] == 10.0