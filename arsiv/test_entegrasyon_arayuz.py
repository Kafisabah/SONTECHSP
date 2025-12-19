# Version: 0.1.0
# Last Update: 2024-12-16
# Module: tests.test_entegrasyon_arayuz
# Description: PyQt arayüz entegrasyon testleri
# Changelog:
# - İlk sürüm oluşturuldu

"""
SONTECHSP PyQt Arayüz Entegrasyon Testleri

Bu modül tüm arayüz bileşenlerinin birlikte çalışmasını test eder.
"""

import sys
import pytest
from unittest.mock import Mock, MagicMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtTest import QTest

from uygulama.arayuz.ana_pencere import AnaPencere
from uygulama.arayuz.servis_fabrikasi import ServisFabrikasi


class TestArayuzEntegrasyonu:
    """Arayüz entegrasyon testleri"""
    
    @classmethod
    def setup_class(cls):
        """Test sınıfı kurulumu"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setup_method(self):
        """Her test öncesi kurulum"""
        # Mock servis fabrikası oluştur
        self.mock_servis_fabrikasi = Mock(spec=ServisFabrikasi)
        
        # Mock servisler
        self.mock_stok_servisi = Mock()
        self.mock_pos_servisi = Mock()
        self.mock_crm_servisi = Mock()
        self.mock_eticaret_servisi = Mock()
        self.mock_ebelge_servisi = Mock()
        self.mock_kargo_servisi = Mock()
        self.mock_rapor_servisi = Mock()
        self.mock_ayar_servisi = Mock()
        
        # Servis fabrikası mock'larını ayarla
        self.mock_servis_fabrikasi.stok_servisi.return_value = self.mock_stok_servisi
        self.mock_servis_fabrikasi.pos_servisi.return_value = self.mock_pos_servisi
        self.mock_servis_fabrikasi.crm_servisi.return_value = self.mock_crm_servisi
        self.mock_servis_fabrikasi.eticaret_servisi.return_value = self.mock_eticaret_servisi
        self.mock_servis_fabrikasi.ebelge_servisi.return_value = self.mock_ebelge_servisi
        self.mock_servis_fabrikasi.kargo_servisi.return_value = self.mock_kargo_servisi
        self.mock_servis_fabrikasi.rapor_servisi.return_value = self.mock_rapor_servisi
        self.mock_servis_fabrikasi.ayar_servisi.return_value = self.mock_ayar_servisi
        
        # Ana pencereyi oluştur
        self.ana_pencere = AnaPencere(self.mock_servis_fabrikasi)
    
    def teardown_method(self):
        """Her test sonrası temizlik"""
        if hasattr(self, 'ana_pencere'):
            self.ana_pencere.close()
            self.ana_pencere.deleteLater()
    
    def test_ana_pencere_olusturma(self):
        """Ana pencerenin doğru oluşturulduğunu test et"""
        # Ana pencerenin oluşturulduğunu doğrula
        assert self.ana_pencere is not None
        assert self.ana_pencere.windowTitle() == "SONTECHSP - POS & ERP Sistemi"
        
        # Servis fabrikasının atandığını doğrula
        assert self.ana_pencere.servis_fabrikasi == self.mock_servis_fabrikasi
        
        # Temel bileşenlerin var olduğunu doğrula
        assert self.ana_pencere.menu_paneli is not None
        assert self.ana_pencere.icerik_alani is not None
        assert self.ana_pencere.menu_listesi is not None
    
    def test_tum_ekranlarin_yuklenmesi(self):
        """Tüm ekranların doğru yüklendiğini test et"""
        beklenen_ekranlar = [
            "gosterge_paneli",
            "pos_satis", 
            "urunler_stok",
            "musteriler",
            "eticaret",
            "ebelge",
            "kargo",
            "raporlar",
            "ayarlar"
        ]
        
        # Tüm ekranların yüklendiğini doğrula
        for ekran_adi in beklenen_ekranlar:
            assert ekran_adi in self.ana_pencere.ekranlar
            assert self.ana_pencere.ekranlar[ekran_adi] is not None
        
        # İçerik alanında doğru sayıda widget olduğunu doğrula
        assert self.ana_pencere.icerik_alani.count() == len(beklenen_ekranlar)
    
    def test_menu_navigasyonu(self):
        """Menü navigasyonunun çalıştığını test et"""
        # İlk ekranın gösterge paneli olduğunu doğrula
        assert self.ana_pencere.aktif_ekran == "gosterge_paneli"
        
        # Farklı ekranlara geçiş yap
        test_ekranlari = ["pos_satis", "urunler_stok", "musteriler", "ayarlar"]
        
        for ekran_adi in test_ekranlari:
            # Ekran değiştir
            self.ana_pencere.ekran_degistir(ekran_adi)
            
            # Aktif ekranın değiştiğini doğrula
            assert self.ana_pencere.aktif_ekran == ekran_adi
            
            # İçerik alanında doğru widget'ın gösterildiğini doğrula
            aktif_widget = self.ana_pencere.icerik_alani.currentWidget()
            beklenen_widget = self.ana_pencere.ekranlar[ekran_adi]
            assert aktif_widget == beklenen_widget
    
    def test_menu_listesi_navigasyonu(self):
        """Menü listesi tıklamalarının çalıştığını test et"""
        # Menü öğelerinin doğru sayıda olduğunu doğrula
        assert self.ana_pencere.menu_listesi.count() == 9
        
        # İlk menü öğesini tıkla (Gösterge Paneli)
        ilk_item = self.ana_pencere.menu_listesi.item(0)
        assert ilk_item.text() == "Gösterge Paneli"
        
        # Menü tıklamasını simüle et
        self.ana_pencere.menu_tiklandi(ilk_item)
        assert self.ana_pencere.aktif_ekran == "gosterge_paneli"
        
        # İkinci menü öğesini tıkla (POS Satış)
        ikinci_item = self.ana_pencere.menu_listesi.item(1)
        assert ikinci_item.text() == "POS Satış"
        
        self.ana_pencere.menu_tiklandi(ikinci_item)
        assert self.ana_pencere.aktif_ekran == "pos_satis"
    
    def test_servis_erisimi(self):
        """Servis erişiminin çalıştığını test et"""
        # Farklı servis tiplerini test et
        servis_tipleri = [
            ("stok", self.mock_stok_servisi),
            ("pos", self.mock_pos_servisi),
            ("crm", self.mock_crm_servisi),
            ("eticaret", self.mock_eticaret_servisi),
            ("ebelge", self.mock_ebelge_servisi),
            ("kargo", self.mock_kargo_servisi),
            ("rapor", self.mock_rapor_servisi),
            ("ayar", self.mock_ayar_servisi)
        ]
        
        for servis_tipi, beklenen_servis in servis_tipleri:
            servis = self.ana_pencere.servis_al(servis_tipi)
            assert servis == beklenen_servis
        
        # Geçersiz servis tipi testi
        gecersiz_servis = self.ana_pencere.servis_al("gecersiz_servis")
        assert gecersiz_servis is None
    
    def test_ekran_degisim_sinyali(self):
        """Ekran değişim sinyalinin çalıştığını test et"""
        # Sinyal dinleyicisi oluştur
        sinyal_alindi = []
        
        def sinyal_dinleyici(ekran_adi):
            sinyal_alindi.append(ekran_adi)
        
        # Sinyali bağla
        self.ana_pencere.ekran_degisti.connect(sinyal_dinleyici)
        
        # Ekran değiştir
        self.ana_pencere.ekran_degistir("pos_satis")
        
        # Sinyalin gönderildiğini doğrula
        assert len(sinyal_alindi) == 1
        assert sinyal_alindi[0] == "pos_satis"
        
        # Başka bir ekrana geç
        self.ana_pencere.ekran_degistir("ayarlar")
        
        assert len(sinyal_alindi) == 2
        assert sinyal_alindi[1] == "ayarlar"
    
    def test_onceki_ekran_takibi(self):
        """Önceki ekran takibinin çalıştığını test et"""
        # İlk durumda önceki ekran None olmalı
        assert self.ana_pencere.onceki_ekran is None
        
        # Ekran değiştir
        self.ana_pencere.ekran_degistir("pos_satis")
        assert self.ana_pencere.onceki_ekran == "gosterge_paneli"
        assert self.ana_pencere.aktif_ekran == "pos_satis"
        
        # Tekrar ekran değiştir
        self.ana_pencere.ekran_degistir("ayarlar")
        assert self.ana_pencere.onceki_ekran == "pos_satis"
        assert self.ana_pencere.aktif_ekran == "ayarlar"
    
    def test_pencere_boyutlari(self):
        """Pencere boyutlarının doğru ayarlandığını test et"""
        geometry = self.ana_pencere.geometry()
        
        # Pencere boyutlarını doğrula
        assert geometry.width() == 1200
        assert geometry.height() == 800
        
        # Pencere pozisyonunu doğrula
        assert geometry.x() == 100
        assert geometry.y() == 100
    
    def test_menu_secimi_guncelleme(self):
        """Menü seçimi güncellemesinin çalıştığını test et"""
        # POS satış ekranına geç
        self.ana_pencere.ekran_degistir("pos_satis")
        
        # Menü seçiminin güncellendiğini doğrula
        secili_item = self.ana_pencere.menu_listesi.currentItem()
        assert secili_item is not None
        assert secili_item.data(Qt.ItemDataRole.UserRole) == "pos_satis"  # UserRole verisi
        
        # Ayarlar ekranına geç
        self.ana_pencere.ekran_degistir("ayarlar")
        
        # Menü seçiminin tekrar güncellendiğini doğrula
        secili_item = self.ana_pencere.menu_listesi.currentItem()
        assert secili_item is not None
        assert secili_item.data(Qt.ItemDataRole.UserRole) == "ayarlar"