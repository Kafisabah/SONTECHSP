# Version: 0.1.0
# Last Update: 2025-12-16
# Module: tests.pos.test_offline_kuyruk_repository_unit
# Description: OfflineKuyrukRepository birim testleri
# Changelog:
# - İlk oluşturma

"""
OfflineKuyrukRepository Birim Testleri

Bu modül OfflineKuyrukRepository kuyruk testlerini içerir.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from sontechsp.uygulama.moduller.pos.repositories.offline_kuyruk_repository import OfflineKuyrukRepository
from sontechsp.uygulama.moduller.pos.arayuzler import IslemTuru, KuyrukDurum
from sontechsp.uygulama.cekirdek.hatalar import DogrulamaHatasi, SontechHatasi, VeritabaniHatasi


class TestOfflineKuyrukRepository:
    """OfflineKuyrukRepository birim testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.repository = OfflineKuyrukRepository()
    
    def test_kuyruk_ekle_basarili(self):
        """Başarılı kuyruk ekleme testi"""
        # Arrange
        islem_turu = IslemTuru.SATIS
        veri = {"satis_id": 1, "tutar": "100.00"}
        terminal_id = 1
        kasiyer_id = 1
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.offline_kuyruk_repository.sqlite_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Yeni kuyruk mock'u
            mock_kuyruk = Mock()
            mock_kuyruk.id = 123
            mock_session_instance.add.return_value = None
            mock_session_instance.commit.return_value = None
            
            # Act
            with patch('sontechsp.uygulama.moduller.pos.repositories.offline_kuyruk_repository.OfflineKuyruk') as mock_kuyruk_class:
                mock_kuyruk_class.return_value = mock_kuyruk
                sonuc = self.repository.kuyruk_ekle(islem_turu, veri, terminal_id, kasiyer_id)
            
            # Assert
            assert sonuc == 123
            mock_session_instance.add.assert_called_once()
            mock_session_instance.commit.assert_called_once()
    
    def test_kuyruk_ekle_gecersiz_parametreler(self):
        """Geçersiz parametrelerle kuyruk ekleme testleri"""
        veri = {"test": "data"}
        
        # Geçersiz terminal ID
        with pytest.raises(DogrulamaHatasi, match="Terminal ID pozitif olmalıdır"):
            self.repository.kuyruk_ekle(IslemTuru.SATIS, veri, 0, 1)
        
        # Geçersiz kasiyer ID
        with pytest.raises(DogrulamaHatasi, match="Kasiyer ID pozitif olmalıdır"):
            self.repository.kuyruk_ekle(IslemTuru.SATIS, veri, 1, 0)
        
        # Boş veri
        with pytest.raises(DogrulamaHatasi, match="İşlem verisi boş olamaz"):
            self.repository.kuyruk_ekle(IslemTuru.SATIS, {}, 1, 1)
        
        # Geçersiz öncelik
        with pytest.raises(DogrulamaHatasi, match="Öncelik 1-5 arasında olmalıdır"):
            self.repository.kuyruk_ekle(IslemTuru.SATIS, veri, 1, 1, oncelik=0)
    
    def test_kuyruk_getir_basarili(self):
        """Başarılı kuyruk getirme testi"""
        # Arrange
        kuyruk_id = 1
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.offline_kuyruk_repository.sqlite_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock kuyruk
            mock_kuyruk = Mock()
            mock_kuyruk.id = 1
            mock_kuyruk.islem_turu = IslemTuru.SATIS
            mock_kuyruk.durum = KuyrukDurum.BEKLEMEDE
            mock_kuyruk.veri = {"test": "data"}
            mock_kuyruk.terminal_id = 1
            mock_kuyruk.kasiyer_id = 1
            mock_kuyruk.islem_tarihi = datetime(2025, 12, 16, 10, 0, 0)
            mock_kuyruk.son_deneme_tarihi = None
            mock_kuyruk.tamamlanma_tarihi = None
            mock_kuyruk.deneme_sayisi = 0
            mock_kuyruk.max_deneme_sayisi = 3
            mock_kuyruk.hata_mesaji = None
            mock_kuyruk.oncelik = 1
            mock_kuyruk.notlar = None
            mock_kuyruk.olusturma_tarihi = None
            mock_kuyruk.guncelleme_tarihi = None
            
            # Mock hesaplanan metodlar
            mock_kuyruk.beklemede_mi.return_value = True
            mock_kuyruk.isleniyor_mu.return_value = False
            mock_kuyruk.tamamlandi_mi.return_value = False
            mock_kuyruk.hata_durumunda_mi.return_value = False
            mock_kuyruk.tekrar_denenebilir_mi.return_value = True
            mock_kuyruk.max_deneme_asildi_mi.return_value = False
            mock_kuyruk.gecikme_suresi_hesapla.return_value = 60
            
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_kuyruk
            
            # Act
            sonuc = self.repository.kuyruk_getir(kuyruk_id)
            
            # Assert
            assert sonuc is not None
            assert sonuc['id'] == 1
            assert sonuc['islem_turu'] == 'satis'
            assert sonuc['durum'] == 'beklemede'
            assert sonuc['beklemede_mi'] is True
    
    def test_kuyruk_getir_bulunamadi(self):
        """Kuyruk bulunamadığında None döndürme testi"""
        # Arrange
        kuyruk_id = 999
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.offline_kuyruk_repository.sqlite_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            mock_session_instance.query.return_value.filter.return_value.first.return_value = None
            
            # Act
            sonuc = self.repository.kuyruk_getir(kuyruk_id)
            
            # Assert
            assert sonuc is None
    
    def test_bekleyen_kuyruk_listesi_basarili(self):
        """Başarılı bekleyen kuyruk listesi getirme testi"""
        # Arrange
        terminal_id = 1
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.offline_kuyruk_repository.sqlite_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock kuyruk listesi
            mock_kuyruk = Mock()
            mock_kuyruk.id = 1
            mock_kuyruk.islem_turu = IslemTuru.SATIS
            mock_kuyruk.durum = KuyrukDurum.BEKLEMEDE
            mock_kuyruk.veri = {"test": "data"}
            mock_kuyruk.terminal_id = 1
            mock_kuyruk.kasiyer_id = 1
            mock_kuyruk.islem_tarihi = datetime(2025, 12, 16, 10, 0, 0)
            mock_kuyruk.son_deneme_tarihi = None
            mock_kuyruk.tamamlanma_tarihi = None
            mock_kuyruk.deneme_sayisi = 0
            mock_kuyruk.max_deneme_sayisi = 3
            mock_kuyruk.hata_mesaji = None
            mock_kuyruk.oncelik = 1
            mock_kuyruk.notlar = None
            mock_kuyruk.olusturma_tarihi = None
            mock_kuyruk.guncelleme_tarihi = None
            
            # Mock hesaplanan metodlar
            mock_kuyruk.beklemede_mi.return_value = True
            mock_kuyruk.isleniyor_mu.return_value = False
            mock_kuyruk.tamamlandi_mi.return_value = False
            mock_kuyruk.hata_durumunda_mi.return_value = False
            mock_kuyruk.tekrar_denenebilir_mi.return_value = True
            mock_kuyruk.max_deneme_asildi_mi.return_value = False
            mock_kuyruk.gecikme_suresi_hesapla.return_value = 60
            
            mock_query = mock_session_instance.query.return_value.filter.return_value
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.limit.return_value = mock_query
            mock_query.all.return_value = [mock_kuyruk]
            
            # Act
            sonuc = self.repository.bekleyen_kuyruk_listesi(terminal_id=terminal_id, limit=10)
            
            # Assert
            assert len(sonuc) == 1
            assert sonuc[0]['id'] == 1
            assert sonuc[0]['durum'] == 'beklemede'
    
    def test_kuyruk_durum_guncelle_basarili(self):
        """Başarılı kuyruk durum güncelleme testi"""
        # Arrange
        kuyruk_id = 1
        yeni_durum = KuyrukDurum.TAMAMLANDI
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.offline_kuyruk_repository.sqlite_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock kuyruk
            mock_kuyruk = Mock()
            mock_kuyruk.tamamla.return_value = None
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_kuyruk
            mock_session_instance.commit.return_value = None
            
            # Act
            sonuc = self.repository.kuyruk_durum_guncelle(kuyruk_id, yeni_durum)
            
            # Assert
            assert sonuc is True
            mock_kuyruk.tamamla.assert_called_once()
            mock_session_instance.commit.assert_called_once()
    
    def test_kuyruk_durum_guncelle_kuyruk_bulunamadi(self):
        """Kuyruk bulunamadığında durum güncelleme testi"""
        # Arrange
        kuyruk_id = 999
        yeni_durum = KuyrukDurum.TAMAMLANDI
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.offline_kuyruk_repository.sqlite_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Kuyruk bulunamadı
            mock_session_instance.query.return_value.filter.return_value.first.return_value = None
            
            # Act & Assert
            with pytest.raises(SontechHatasi, match="Kuyruk bulunamadı: 999"):
                self.repository.kuyruk_durum_guncelle(kuyruk_id, yeni_durum)
    
    def test_kuyruk_deneme_artir_basarili(self):
        """Başarılı kuyruk deneme artırma testi"""
        # Arrange
        kuyruk_id = 1
        hata_mesaji = "Network hatası"
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.offline_kuyruk_repository.sqlite_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock kuyruk
            mock_kuyruk = Mock()
            mock_kuyruk.deneme_artir.return_value = None
            mock_kuyruk.max_deneme_asildi_mi.return_value = False
            mock_kuyruk.hata_durumuna_getir.return_value = None
            mock_kuyruk.beklemede_durumuna_getir.return_value = None
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_kuyruk
            mock_session_instance.commit.return_value = None
            
            # Act
            sonuc = self.repository.kuyruk_deneme_artir(kuyruk_id, hata_mesaji)
            
            # Assert
            assert sonuc is True
            mock_kuyruk.deneme_artir.assert_called_once()
            mock_kuyruk.hata_durumuna_getir.assert_called_with(hata_mesaji)
            mock_kuyruk.beklemede_durumuna_getir.assert_called_once()
            mock_session_instance.commit.assert_called_once()
    
    def test_kuyruk_deneme_artir_max_deneme_asildi(self):
        """Maksimum deneme sayısı aşıldığında kuyruk deneme artırma testi"""
        # Arrange
        kuyruk_id = 1
        hata_mesaji = "Network hatası"
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.offline_kuyruk_repository.sqlite_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock kuyruk
            mock_kuyruk = Mock()
            mock_kuyruk.deneme_artir.return_value = None
            mock_kuyruk.max_deneme_asildi_mi.return_value = True
            mock_kuyruk.hata_durumuna_getir.return_value = None
            mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_kuyruk
            mock_session_instance.commit.return_value = None
            
            # Act
            sonuc = self.repository.kuyruk_deneme_artir(kuyruk_id, hata_mesaji)
            
            # Assert
            assert sonuc is True
            mock_kuyruk.deneme_artir.assert_called_once()
            mock_kuyruk.hata_durumuna_getir.assert_called_with(f"Maksimum deneme sayısı aşıldı: {hata_mesaji}")
            mock_session_instance.commit.assert_called_once()
    
    def test_hata_durumundaki_kuyruklar_basarili(self):
        """Başarılı hata durumundaki kuyruklar getirme testi"""
        # Arrange
        with patch('sontechsp.uygulama.moduller.pos.repositories.offline_kuyruk_repository.sqlite_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock hata durumundaki kuyruk
            mock_kuyruk = Mock()
            mock_kuyruk.id = 1
            mock_kuyruk.islem_turu = IslemTuru.SATIS
            mock_kuyruk.durum = KuyrukDurum.HATA
            mock_kuyruk.veri = {"test": "data"}
            mock_kuyruk.terminal_id = 1
            mock_kuyruk.kasiyer_id = 1
            mock_kuyruk.islem_tarihi = datetime(2025, 12, 16, 10, 0, 0)
            mock_kuyruk.son_deneme_tarihi = datetime(2025, 12, 16, 10, 5, 0)
            mock_kuyruk.tamamlanma_tarihi = None
            mock_kuyruk.deneme_sayisi = 3
            mock_kuyruk.max_deneme_sayisi = 3
            mock_kuyruk.hata_mesaji = "Network hatası"
            mock_kuyruk.oncelik = 1
            mock_kuyruk.notlar = None
            mock_kuyruk.olusturma_tarihi = None
            mock_kuyruk.guncelleme_tarihi = None
            
            # Mock hesaplanan metodlar
            mock_kuyruk.beklemede_mi.return_value = False
            mock_kuyruk.isleniyor_mu.return_value = False
            mock_kuyruk.tamamlandi_mi.return_value = False
            mock_kuyruk.hata_durumunda_mi.return_value = True
            mock_kuyruk.tekrar_denenebilir_mi.return_value = False
            mock_kuyruk.max_deneme_asildi_mi.return_value = True
            mock_kuyruk.gecikme_suresi_hesapla.return_value = 480
            
            mock_query = mock_session_instance.query.return_value.filter.return_value
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.limit.return_value = mock_query
            mock_query.all.return_value = [mock_kuyruk]
            
            # Act
            sonuc = self.repository.hata_durumundaki_kuyruklar(limit=10)
            
            # Assert
            assert len(sonuc) == 1
            assert sonuc[0]['id'] == 1
            assert sonuc[0]['durum'] == 'hata'
            assert sonuc[0]['hata_mesaji'] == "Network hatası"
    
    def test_kuyruk_temizle_basarili(self):
        """Başarılı kuyruk temizleme testi"""
        # Arrange
        gun_sayisi = 30
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.offline_kuyruk_repository.sqlite_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock silme işlemi
            mock_session_instance.query.return_value.filter.return_value.delete.return_value = 5
            mock_session_instance.commit.return_value = None
            
            # Act
            sonuc = self.repository.kuyruk_temizle(gun_sayisi)
            
            # Assert
            assert sonuc == 5
            mock_session_instance.commit.assert_called_once()
    
    def test_kuyruk_istatistikleri_basarili(self):
        """Başarılı kuyruk istatistikleri getirme testi"""
        # Arrange
        terminal_id = 1
        
        with patch('sontechsp.uygulama.moduller.pos.repositories.offline_kuyruk_repository.sqlite_session') as mock_session:
            mock_session_instance = Mock()
            mock_session.return_value.__enter__.return_value = mock_session_instance
            
            # Mock kuyruk listesi
            mock_kuyruk1 = Mock()
            mock_kuyruk1.durum = KuyrukDurum.BEKLEMEDE
            mock_kuyruk1.islem_turu = IslemTuru.SATIS
            mock_kuyruk1.islem_tarihi = datetime.now() - timedelta(minutes=30)
            
            mock_kuyruk2 = Mock()
            mock_kuyruk2.durum = KuyrukDurum.TAMAMLANDI
            mock_kuyruk2.islem_turu = IslemTuru.IADE
            mock_kuyruk2.islem_tarihi = datetime.now() - timedelta(hours=1)
            
            mock_query = mock_session_instance.query.return_value
            mock_query.filter.return_value = mock_query
            mock_query.all.return_value = [mock_kuyruk1, mock_kuyruk2]
            
            # Act
            sonuc = self.repository.kuyruk_istatistikleri(terminal_id=terminal_id)
            
            # Assert
            assert sonuc['toplam_kayit'] == 2
            assert sonuc['terminal_id'] == terminal_id
            assert 'durum_sayilari' in sonuc
            assert 'islem_turu_sayilari' in sonuc
            assert 'ortalama_bekleme_suresi_saniye' in sonuc
    
    def test_satis_kuyruk_ekle_basarili(self):
        """Başarılı satış kuyruk ekleme testi"""
        # Arrange
        satis_data = {"satis_id": 1, "toplam_tutar": "100.00"}
        terminal_id = 1
        kasiyer_id = 1
        
        # Act
        with patch.object(self.repository, 'kuyruk_ekle', return_value=123) as mock_kuyruk_ekle:
            sonuc = self.repository.satis_kuyruk_ekle(satis_data, terminal_id, kasiyer_id)
        
        # Assert
        assert sonuc == 123
        mock_kuyruk_ekle.assert_called_once()
        args = mock_kuyruk_ekle.call_args[0]
        assert args[0] == IslemTuru.SATIS
        assert args[2] == terminal_id
        assert args[3] == kasiyer_id
    
    def test_iade_kuyruk_ekle_basarili(self):
        """Başarılı iade kuyruk ekleme testi"""
        # Arrange
        iade_data = {"iade_id": 1, "toplam_tutar": "50.00"}
        terminal_id = 1
        kasiyer_id = 1
        
        # Act
        with patch.object(self.repository, 'kuyruk_ekle', return_value=456) as mock_kuyruk_ekle:
            sonuc = self.repository.iade_kuyruk_ekle(iade_data, terminal_id, kasiyer_id)
        
        # Assert
        assert sonuc == 456
        mock_kuyruk_ekle.assert_called_once()
        args = mock_kuyruk_ekle.call_args[0]
        assert args[0] == IslemTuru.IADE
        assert args[2] == terminal_id
        assert args[3] == kasiyer_id
    
    def test_stok_dusumu_kuyruk_ekle_basarili(self):
        """Başarılı stok düşümü kuyruk ekleme testi"""
        # Arrange
        stok_data = {"urun_id": 1, "adet": 5}
        terminal_id = 1
        kasiyer_id = 1
        
        # Act
        with patch.object(self.repository, 'kuyruk_ekle', return_value=789) as mock_kuyruk_ekle:
            sonuc = self.repository.stok_dusumu_kuyruk_ekle(stok_data, terminal_id, kasiyer_id)
        
        # Assert
        assert sonuc == 789
        mock_kuyruk_ekle.assert_called_once()
        args = mock_kuyruk_ekle.call_args[0]
        assert args[0] == IslemTuru.STOK_DUSUMU
        assert args[2] == terminal_id
        assert args[3] == kasiyer_id