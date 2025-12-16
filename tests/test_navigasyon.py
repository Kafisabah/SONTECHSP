# Version: 0.1.0
# Last Update: 2024-12-16
# Module: test_navigasyon
# Description: Navigasyon tutarlılığı property testleri
# Changelog:
# - İlk sürüm oluşturuldu

import pytest
from hypothesis import given, strategies as st, settings
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from uygulama.arayuz.ana_pencere import AnaPencere
from uygulama.arayuz.servis_fabrikasi import ServisFabrikasi


class TestNavigasyonTutarliligi:
    """**Feature: pyqt-arayuz-iskeleti, Property 2: Navigasyon tutarlılığı**"""
    
    def setup_method(self):
        """Her test öncesi QApplication oluştur"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        # Servis fabrikasını sıfırla
        ServisFabrikasi._instance = None
        ServisFabrikasi._servisler = {}
    
    def teardown_method(self):
        """Test sonrası temizlik"""
        if hasattr(self, 'ana_pencere'):
            self.ana_pencere.close()
    
    def test_menu_tiklama_navigasyonu(self):
        """
        Property 2: Navigasyon tutarlılığı
        For any menü öğesi tıklaması, ilgili ekran içerik alanında gösterilmeli
        Validates: Requirements 2.2, 2.4
        """
        # Ana pencere oluştur
        servis_fabrikasi = ServisFabrikasi()
        self.ana_pencere = AnaPencere(servis_fabrikasi)
        
        # Test edilecek ekranlar
        test_ekranlari = ["pos_satis", "urunler_stok", "musteriler"]
        
        for ekran_adi in test_ekranlari:
            # Ekran değiştir
            self.ana_pencere.ekran_degistir(ekran_adi)
            
            # Aktif ekranın doğru olduğunu kontrol et
            assert self.ana_pencere.aktif_ekran == ekran_adi
            
            # İçerik alanında doğru widget'ın gösterildiğini kontrol et
            aktif_widget = self.ana_pencere.icerik_alani.currentWidget()
            beklenen_widget = self.ana_pencere.ekranlar[ekran_adi]
            assert aktif_widget == beklenen_widget
    
    @given(st.sampled_from([
        "gosterge_paneli", "pos_satis", "urunler_stok", 
        "musteriler", "eticaret", "ebelge"
    ]))
    @settings(deadline=1000)  # 1 saniye timeout
    def test_ekran_degisim_tutarliligi(self, ekran_adi):
        """
        Property 2: Ekran değişim tutarlılığı
        For any geçerli ekran adı, ekran değişimi gerçekleşmeli
        Validates: Requirements 2.2, 2.4
        """
        # Ana pencere oluştur
        servis_fabrikasi = ServisFabrikasi()
        self.ana_pencere = AnaPencere(servis_fabrikasi)
        
        # Önceki ekranı kaydet
        onceki_ekran = self.ana_pencere.aktif_ekran
        
        # Ekran değiştir
        self.ana_pencere.ekran_degistir(ekran_adi)
        
        # Değişimin gerçekleştiğini kontrol et
        assert self.ana_pencere.aktif_ekran == ekran_adi
        assert self.ana_pencere.onceki_ekran == onceki_ekran
    
    def test_sinyal_gonderme_tutarliligi(self):
        """
        Property 2: Sinyal gönderme tutarlılığı
        For any ekran değişimi, ekran_degisti sinyali gönderilmeli
        Validates: Requirements 2.4
        """
        # Ana pencere oluştur
        servis_fabrikasi = ServisFabrikasi()
        self.ana_pencere = AnaPencere(servis_fabrikasi)
        
        # Sinyal yakalayıcı
        sinyal_yakalandi = []
        
        def sinyal_yakala(ekran_adi):
            sinyal_yakalandi.append(ekran_adi)
        
        # Sinyali bağla
        self.ana_pencere.ekran_degisti.connect(sinyal_yakala)
        
        # Ekran değiştir
        test_ekran = "pos_satis"
        self.ana_pencere.ekran_degistir(test_ekran)
        
        # Sinyalin gönderildiğini kontrol et
        assert len(sinyal_yakalandi) == 1
        assert sinyal_yakalandi[0] == test_ekran


class TestEkranYapisiTutarliligi:
    """**Feature: pyqt-arayuz-iskeleti, Property 9: Ekran yapısı tutarlılığı**"""
    
    def setup_method(self):
        """Her test öncesi QApplication oluştur"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        
        # Servis fabrikasını sıfırla
        ServisFabrikasi._instance = None
        ServisFabrikasi._servisler = {}
    
    def teardown_method(self):
        """Test sonrası temizlik"""
        if hasattr(self, 'ana_pencere'):
            self.ana_pencere.close()
    
    def test_ana_pencere_yapisi(self):
        """
        Property 9: Ana pencere yapısı tutarlılığı
        For any ana pencere açılışı, sol menü ve içerik alanı yapısı görüntülenmeli
        Validates: Requirements 2.1
        """
        # Ana pencere oluştur
        servis_fabrikasi = ServisFabrikasi()
        self.ana_pencere = AnaPencere(servis_fabrikasi)
        
        # Sol menü panelinin varlığını kontrol et
        assert hasattr(self.ana_pencere, 'menu_paneli')
        assert self.ana_pencere.menu_paneli is not None
        
        # İçerik alanının varlığını kontrol et
        assert hasattr(self.ana_pencere, 'icerik_alani')
        assert self.ana_pencere.icerik_alani is not None
        
        # Menü listesinin varlığını kontrol et
        assert hasattr(self.ana_pencere, 'menu_listesi')
        assert self.ana_pencere.menu_listesi is not None
        
        # Menü öğelerinin yüklendiğini kontrol et
        assert self.ana_pencere.menu_listesi.count() > 0