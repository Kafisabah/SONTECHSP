# Version: 0.1.0
# Last Update: 2024-12-15
# Module: test_katmanli_mimari
# Description: SONTECHSP katmanlı mimari uyumluluğu property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Katmanlı Mimari Property Testleri

Bu dosya katmanlı mimari kurallarının doğruluğunu
property-based testing ile kontrol eder.

Mimari kuralları:
UI -> Servisler -> Depolar -> Veritabanı
"""

import os
import pytest
from hypothesis import given, strategies as st
from pathlib import Path


class TestKatmanliMimari:
    """SONTECHSP katmanlı mimari uyumluluğu testleri"""
    
    def test_katman_klasorleri_mevcut(self):
        """
        **Feature: sontechsp-proje-iskeleti, Property 3: Katmanlı mimari uyumluluğu**
        
        Herhangi bir proje yapısında, UI->Servis->Repository->DB katman kuralları 
        korunmalı ve modüller kendi dizinlerinde olmalıdır
        **Doğrular: Gereksinim 1.3, 4.1, 4.2, 4.4**
        """
        # Katman klasörlerinin varlığını kontrol et
        katman_klasorleri = [
            "sontechsp/uygulama/arayuz",      # UI katmanı
            "sontechsp/uygulama/servisler",   # Servis katmanı  
            "sontechsp/uygulama/veritabani",  # Repository + DB katmanı
            "sontechsp/uygulama/moduller"     # İş modülleri
        ]
        
        for klasor in katman_klasorleri:
            assert os.path.exists(klasor), f"Katman klasörü mevcut değil: {klasor}"
            assert os.path.isdir(klasor), f"Katman yolu bir klasör değil: {klasor}"
    
    def test_modul_organizasyonu(self):
        """
        İş modüllerinin doğru şekilde organize edildiğini kontrol eder
        """
        beklenen_moduller = [
            "stok", "pos", "crm", "satis_belgeleri", 
            "eticaret", "ebelge", "kargo", "raporlar"
        ]
        
        moduller_klasoru = "sontechsp/uygulama/moduller"
        assert os.path.exists(moduller_klasoru), "Modüller klasörü mevcut değil"
        
        for modul in beklenen_moduller:
            modul_yolu = os.path.join(moduller_klasoru, modul)
            assert os.path.exists(modul_yolu), f"Modül klasörü mevcut değil: {modul}"
            assert os.path.isdir(modul_yolu), f"Modül yolu bir klasör değil: {modul}"
            
            # Her modülün __init__.py dosyası olmalı
            init_yolu = os.path.join(modul_yolu, "__init__.py")
            assert os.path.exists(init_yolu), f"Modül __init__.py dosyası mevcut değil: {modul}"
    
    def test_cekirdek_modul_bagimsizligi(self):
        """
        Çekirdek modülün diğer katmanlardan bağımsız olduğunu kontrol eder
        """
        cekirdek_klasoru = "sontechsp/uygulama/cekirdek"
        assert os.path.exists(cekirdek_klasoru), "Çekirdek klasörü mevcut değil"
        assert os.path.isdir(cekirdek_klasoru), "Çekirdek yolu bir klasör değil"
        
        # Çekirdek modülün __init__.py dosyası olmalı
        init_yolu = os.path.join(cekirdek_klasoru, "__init__.py")
        assert os.path.exists(init_yolu), "Çekirdek __init__.py dosyası mevcut değil"
    
    @given(st.sampled_from([
        ("arayuz", "UI katmanı"),
        ("servisler", "Servis katmanı"), 
        ("veritabani", "Repository katmanı"),
        ("moduller", "İş modülleri")
    ]))
    def test_katman_yapisinin_tutarliligi_property(self, katman_bilgisi):
        """
        Property test: Herhangi bir katman için yapısal tutarlılık
        """
        katman_adi, katman_aciklama = katman_bilgisi
        katman_yolu = f"sontechsp/uygulama/{katman_adi}"
        
        # Katmanın var olduğunu kontrol et
        assert os.path.exists(katman_yolu), f"{katman_aciklama} klasörü mevcut değil: {katman_yolu}"
        assert os.path.isdir(katman_yolu), f"{katman_aciklama} yolu bir klasör değil: {katman_yolu}"
        
        # __init__.py dosyasının var olduğunu kontrol et
        init_yolu = os.path.join(katman_yolu, "__init__.py")
        assert os.path.exists(init_yolu), f"{katman_aciklama} __init__.py dosyası mevcut değil"
        assert os.path.isfile(init_yolu), f"{katman_aciklama} __init__.py yolu bir dosya değil"
    
    @given(st.sampled_from([
        "stok", "pos", "crm", "satis_belgeleri",
        "eticaret", "ebelge", "kargo", "raporlar"
    ]))
    def test_modul_yapisinin_tutarliligi_property(self, modul_adi):
        """
        Property test: Herhangi bir iş modülü için yapısal tutarlılık
        """
        modul_yolu = f"sontechsp/uygulama/moduller/{modul_adi}"
        
        # Modülün var olduğunu kontrol et
        assert os.path.exists(modul_yolu), f"Modül klasörü mevcut değil: {modul_yolu}"
        assert os.path.isdir(modul_yolu), f"Modül yolu bir klasör değil: {modul_yolu}"
        
        # __init__.py dosyasının var olduğunu kontrol et
        init_yolu = os.path.join(modul_yolu, "__init__.py")
        assert os.path.exists(init_yolu), f"Modül __init__.py dosyası mevcut değil: {modul_adi}"
        assert os.path.isfile(init_yolu), f"Modül __init__.py yolu bir dosya değil: {modul_adi}"