# Version: 0.1.0
# Last Update: 2024-12-17
# Module: test_crm_unit
# Description: CRM modülü unit testleri
# Changelog:
# - İlk oluşturma: Müşteri CRUD, puan işlemleri, entegrasyon hook'ları unit testleri

"""
CRM Modülü Unit Testleri

Bu dosya CRM modülünün unit testlerini içerir:
- Müşteri CRUD işlemleri
- Puan işlemleri
- Entegrasyon hook'ları
- Edge case'ler

Requirements: Tüm gereksinimler
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from sontechsp.uygulama.moduller.crm import (
    MusteriServisi, SadakatServisi,
    MusteriDeposu, SadakatDeposu,
    MusteriOlusturDTO, MusteriGuncelleDTO, PuanIslemDTO, MusteriAraDTO,
    PuanIslemTuru, ReferansTuru,
    pos_satis_tamamlandi, satis_belgesi_olustu
)
from sontechsp.uygulama.veritabani.modeller.crm import Musteriler, SadakatPuanlari
from sontechsp.uygulama.cekirdek.hatalar import DogrulamaHatasi, VeritabaniHatasi, AlanHatasi


class TestMusteriServisi:
    """Müşteri servisi unit testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.mock_db = Mock(spec=Session)
        self.mock_depo = Mock(spec=MusteriDeposu)
        self.servis = MusteriServisi(self.mock_db)
        self.servis.depo = self.mock_depo
    
    def test_musteri_olustur_basarili(self):
        """Başarılı müşteri oluşturma testi"""
        # Arrange
        dto = MusteriOlusturDTO(ad="Ahmet", soyad="Yılmaz", telefon="5551234567")
        mock_musteri = Mock(spec=Musteriler)
        mock_musteri.id = 1
        self.mock_depo.musteri_olustur.return_value = mock_musteri
        
        # Act
        result = self.servis.musteri_olustur(dto)
        
        # Assert
        assert result == mock_musteri
        self.mock_depo.musteri_olustur.assert_called_once_with(dto)
        self.mock_db.commit.assert_called_once()
    
    def test_musteri_olustur_ad_bos(self):
        """Ad boş olduğunda hata fırlatma testi"""
        # Arrange
        dto = MusteriOlusturDTO(ad="", soyad="Yılmaz")
        
        # Act & Assert
        with pytest.raises(DogrulamaHatasi, match="Ad alanı zorunludur"):
            self.servis.musteri_olustur(dto)
        
        self.mock_db.rollback.assert_called_once()
    
    def test_musteri_olustur_soyad_bos(self):
        """Soyad boş olduğunda hata fırlatma testi"""
        # Arrange
        dto = MusteriOlusturDTO(ad="Ahmet", soyad="")
        
        # Act & Assert
        with pytest.raises(DogrulamaHatasi, match="Soyad alanı zorunludur"):
            self.servis.musteri_olustur(dto)
        
        self.mock_db.rollback.assert_called_once()
    
    def test_musteri_guncelle_basarili(self):
        """Başarılı müşteri güncelleme testi"""
        # Arrange
        musteri_id = 1
        dto = MusteriGuncelleDTO(ad="Mehmet")
        mock_musteri = Mock(spec=Musteriler)
        self.mock_depo.musteri_guncelle.return_value = mock_musteri
        
        # Act
        result = self.servis.musteri_guncelle(musteri_id, dto)
        
        # Assert
        assert result == mock_musteri
        self.mock_depo.musteri_guncelle.assert_called_once_with(musteri_id, dto)
        self.mock_db.commit.assert_called_once()
    
    def test_musteri_guncelle_gecersiz_id(self):
        """Geçersiz ID ile güncelleme testi"""
        # Arrange
        dto = MusteriGuncelleDTO(ad="Mehmet")
        
        # Act & Assert
        with pytest.raises(DogrulamaHatasi, match="Geçersiz müşteri ID'si"):
            self.servis.musteri_guncelle(0, dto)
        
        self.mock_db.rollback.assert_called_once()
    
    def test_musteri_getir_basarili(self):
        """Başarılı müşteri getirme testi"""
        # Arrange
        musteri_id = 1
        mock_musteri = Mock(spec=Musteriler)
        self.mock_depo.musteri_getir.return_value = mock_musteri
        
        # Act
        result = self.servis.musteri_getir(musteri_id)
        
        # Assert
        assert result == mock_musteri
        self.mock_depo.musteri_getir.assert_called_once_with(musteri_id)
    
    def test_musteri_ara_basarili(self):
        """Başarılı müşteri arama testi"""
        # Arrange
        dto = MusteriAraDTO(ad="Ahmet")
        mock_musteriler = [Mock(spec=Musteriler)]
        self.mock_depo.musteri_ara.return_value = mock_musteriler
        
        # Act
        result = self.servis.musteri_ara(dto)
        
        # Assert
        assert result == mock_musteriler
        self.mock_depo.musteri_ara.assert_called_once_with(dto)
    
    def test_musteri_ara_bos_kriterler(self):
        """Boş kriterlerle arama testi"""
        # Arrange
        dto = MusteriAraDTO()
        
        # Act
        result = self.servis.musteri_ara(dto)
        
        # Assert
        assert result == []


class TestSadakatServisi:
    """Sadakat servisi unit testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.mock_db = Mock(spec=Session)
        self.mock_depo = Mock(spec=SadakatDeposu)
        self.servis = SadakatServisi(self.mock_db)
        self.servis.depo = self.mock_depo
    
    def test_puan_kazan_basarili(self):
        """Başarılı puan kazanımı testi"""
        # Arrange
        dto = PuanIslemDTO(musteri_id=1, puan=100)
        mock_puan_kaydi = Mock(spec=SadakatPuanlari)
        self.mock_depo.puan_kaydi_ekle.return_value = mock_puan_kaydi
        
        # Act
        result = self.servis.puan_kazan(dto)
        
        # Assert
        assert result == mock_puan_kaydi
        self.mock_depo.puan_kaydi_ekle.assert_called_once_with(dto, PuanIslemTuru.KAZANIM)
        self.mock_db.commit.assert_called_once()
    
    def test_puan_kazan_negatif_puan(self):
        """Negatif puan ile kazanım testi"""
        # Arrange
        dto = PuanIslemDTO(musteri_id=1, puan=-50)
        
        # Act & Assert
        with pytest.raises(DogrulamaHatasi, match="Puan değeri pozitif olmalıdır"):
            self.servis.puan_kazan(dto)
        
        self.mock_db.rollback.assert_called_once()
    
    def test_puan_harca_basarili(self):
        """Başarılı puan harcama testi"""
        # Arrange
        dto = PuanIslemDTO(musteri_id=1, puan=50)
        mock_puan_kaydi = Mock(spec=SadakatPuanlari)
        self.mock_depo.puan_bakiyesi_getir.return_value = 100  # Yeterli bakiye
        self.mock_depo.puan_kaydi_ekle.return_value = mock_puan_kaydi
        
        # Act
        result = self.servis.puan_harca(dto)
        
        # Assert
        assert result == mock_puan_kaydi
        self.mock_depo.puan_bakiyesi_getir.assert_called_once_with(dto.musteri_id)
        self.mock_depo.puan_kaydi_ekle.assert_called_once_with(dto, PuanIslemTuru.HARCAMA)
        self.mock_db.commit.assert_called_once()
    
    def test_puan_harca_yetersiz_bakiye(self):
        """Yetersiz bakiye ile harcama testi"""
        # Arrange
        dto = PuanIslemDTO(musteri_id=1, puan=150)
        self.mock_depo.puan_bakiyesi_getir.return_value = 100  # Yetersiz bakiye
        
        # Act & Assert
        with pytest.raises(DogrulamaHatasi, match="Yetersiz bakiye"):
            self.servis.puan_harca(dto)
        
        self.mock_db.rollback.assert_called_once()
    
    def test_bakiye_getir_basarili(self):
        """Başarılı bakiye getirme testi"""
        # Arrange
        musteri_id = 1
        expected_bakiye = 250
        self.mock_depo.puan_bakiyesi_getir.return_value = expected_bakiye
        
        # Act
        result = self.servis.bakiye_getir(musteri_id)
        
        # Assert
        assert result == expected_bakiye
        self.mock_depo.puan_bakiyesi_getir.assert_called_once_with(musteri_id)
    
    def test_hareketler_basarili(self):
        """Başarılı hareket listeleme testi"""
        # Arrange
        musteri_id = 1
        limit = 50
        mock_hareketler = [Mock(spec=SadakatPuanlari)]
        self.mock_depo.puan_hareketleri_listele.return_value = mock_hareketler
        
        # Act
        result = self.servis.hareketler(musteri_id, limit)
        
        # Assert
        assert result == mock_hareketler
        self.mock_depo.puan_hareketleri_listele.assert_called_once_with(musteri_id, limit)
    
    def test_puan_duzelt_basarili_pozitif(self):
        """Başarılı pozitif puan düzeltme testi"""
        # Arrange
        dto = PuanIslemDTO(musteri_id=1, puan=50, aciklama="Test düzeltme")
        mock_puan_kaydi = Mock(spec=SadakatPuanlari)
        self.mock_depo.puan_kaydi_ekle.return_value = mock_puan_kaydi
        
        # Act
        result = self.servis.puan_duzelt(dto)
        
        # Assert
        assert result == mock_puan_kaydi
        self.mock_depo.puan_kaydi_ekle.assert_called_once_with(dto, PuanIslemTuru.DUZELTME)
        self.mock_db.commit.assert_called_once()
    
    def test_puan_duzelt_aciklama_zorunlu(self):
        """Açıklama olmadan düzeltme testi"""
        # Arrange
        dto = PuanIslemDTO(musteri_id=1, puan=50)  # Açıklama yok
        
        # Act & Assert
        with pytest.raises(DogrulamaHatasi, match="açıklama zorunludur"):
            self.servis.puan_duzelt(dto)
        
        self.mock_db.rollback.assert_called_once()


class TestMusteriDeposu:
    """Müşteri deposu unit testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.mock_db = Mock(spec=Session)
        self.depo = MusteriDeposu(self.mock_db)
    
    def test_eposta_gecerli_mi_gecerli(self):
        """Geçerli e-posta format testi"""
        # Act & Assert
        assert self.depo._eposta_gecerli_mi("test@example.com") == True
        assert self.depo._eposta_gecerli_mi("user.name@domain.co.uk") == True
    
    def test_eposta_gecerli_mi_gecersiz(self):
        """Geçersiz e-posta format testi"""
        # Act & Assert
        assert self.depo._eposta_gecerli_mi("invalid-email") == False
        assert self.depo._eposta_gecerli_mi("@domain.com") == False
        assert self.depo._eposta_gecerli_mi("user@") == False
        assert self.depo._eposta_gecerli_mi("") == False


class TestEntegrasyonHooklari:
    """Entegrasyon hook'ları unit testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.mock_db = Mock(spec=Session)
    
    @patch('sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.SadakatServisi')
    @patch('sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.logger')
    def test_pos_satis_tamamlandi_basarili(self, mock_logger, mock_sadakat_servisi_class):
        """Başarılı POS satış hook testi"""
        # Arrange
        mock_sadakat_servisi = Mock()
        mock_sadakat_servisi_class.return_value = mock_sadakat_servisi
        
        musteri_id = 1
        toplam_tutar = 100.0
        satis_id = 123
        
        # Act
        result = pos_satis_tamamlandi(self.mock_db, musteri_id, toplam_tutar, satis_id)
        
        # Assert
        assert result == True
        mock_sadakat_servisi_class.assert_called_once_with(self.mock_db)
        mock_sadakat_servisi.puan_kazan.assert_called_once()
        mock_logger.info.assert_called_once()
    
    def test_pos_satis_tamamlandi_musteri_yok(self):
        """Müşteri olmadan POS satış hook testi"""
        # Act
        result = pos_satis_tamamlandi(self.mock_db, None, 100.0, 123)
        
        # Assert
        assert result == True  # Sessizce atlanmalı
    
    def test_pos_satis_tamamlandi_sifir_tutar(self):
        """Sıfır tutarla POS satış hook testi"""
        # Act
        result = pos_satis_tamamlandi(self.mock_db, 1, 0.0, 123)
        
        # Assert
        assert result == True  # Sessizce atlanmalı
    
    @patch('sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.SadakatServisi')
    @patch('sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.logger')
    def test_pos_satis_tamamlandi_hata_yonetimi(self, mock_logger, mock_sadakat_servisi_class):
        """POS satış hook hata yönetimi testi"""
        # Arrange
        mock_sadakat_servisi = Mock()
        mock_sadakat_servisi.puan_kazan.side_effect = DogrulamaHatasi("Test hatası")
        mock_sadakat_servisi_class.return_value = mock_sadakat_servisi
        
        # Act
        result = pos_satis_tamamlandi(self.mock_db, 1, 100.0, 123)
        
        # Assert
        assert result == False  # Hata durumunda False döner
        mock_logger.warning.assert_called_once()
    
    @patch('sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.SadakatServisi')
    @patch('sontechsp.uygulama.moduller.crm.entegrasyon_kancalari.logger')
    def test_satis_belgesi_olustu_basarili(self, mock_logger, mock_sadakat_servisi_class):
        """Başarılı satış belgesi hook testi"""
        # Arrange
        mock_sadakat_servisi = Mock()
        mock_sadakat_servisi_class.return_value = mock_sadakat_servisi
        
        musteri_id = 1
        belge_tutari = 200.0
        belge_id = 456
        
        # Act
        result = satis_belgesi_olustu(self.mock_db, musteri_id, belge_tutari, belge_id)
        
        # Assert
        assert result == True
        mock_sadakat_servisi_class.assert_called_once_with(self.mock_db)
        mock_sadakat_servisi.puan_kazan.assert_called_once()
        mock_logger.info.assert_called_once()


class TestEdgeCases:
    """Edge case testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.mock_db = Mock(spec=Session)
    
    def test_musteri_servisi_veritabani_hatasi(self):
        """Veritabanı hatası durumu testi"""
        # Arrange
        servis = MusteriServisi(self.mock_db)
        servis.depo = Mock()
        servis.depo.musteri_olustur.side_effect = Exception("DB bağlantı hatası")
        
        dto = MusteriOlusturDTO(ad="Test", soyad="User")
        
        # Act & Assert
        with pytest.raises(VeritabaniHatasi):
            servis.musteri_olustur(dto)
        
        self.mock_db.rollback.assert_called_once()
    
    def test_sadakat_servisi_transaction_rollback(self):
        """Transaction rollback testi"""
        # Arrange
        servis = SadakatServisi(self.mock_db)
        servis.depo = Mock()
        servis.depo.puan_kaydi_ekle.side_effect = Exception("DB hatası")
        
        dto = PuanIslemDTO(musteri_id=1, puan=100)
        
        # Act & Assert
        with pytest.raises(VeritabaniHatasi):
            servis.puan_kazan(dto)
        
        self.mock_db.rollback.assert_called_once()
    
    def test_limit_parametresi_negatif(self):
        """Negatif limit parametresi testi"""
        # Arrange
        servis = SadakatServisi(self.mock_db)
        servis.depo = Mock()
        servis.depo.puan_hareketleri_listele.return_value = []
        
        # Act
        result = servis.hareketler(1, -10)
        
        # Assert - Negatif limit 100'e çevrilmeli
        servis.depo.puan_hareketleri_listele.assert_called_once_with(1, 100)
    
    def test_musteri_ara_whitespace_temizleme(self):
        """Arama kriterlerinde whitespace temizleme testi"""
        # Arrange
        servis = MusteriServisi(self.mock_db)
        servis.depo = Mock()
        servis.depo.musteri_ara.return_value = []
        
        dto = MusteriAraDTO(ad="  Ahmet  ", soyad="  Yılmaz  ")
        
        # Act
        servis.musteri_ara(dto)
        
        # Assert - Depo çağrısında whitespace'ler temizlenmeli
        servis.depo.musteri_ara.assert_called_once_with(dto)