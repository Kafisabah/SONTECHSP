# Version: 0.1.0
# Last Update: 2024-12-15
# Module: test_klasor_hiyerarsisi
# Description: SONTECHSP klasör hiyerarşisi property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Klasör Hiyerarşisi Property Testleri

Bu dosya proje iskeletinin klasör yapısının doğruluğunu
property-based testing ile kontrol eder.
"""

import os
import pytest
from hypothesis import given, strategies as st
from pathlib import Path


class TestKlasorHiyerarsisi:
    """SONTECHSP klasör hiyerarşisi tutarlılığı testleri"""
    
    def test_temel_klasor_yapisi_mevcut(self):
        """
        **Feature: sontechsp-proje-iskeleti, Property 1: SONTECHSP klasör hiyerarşisi tutarlılığı**
        
        Herhangi bir proje iskeleti oluşturulduğunda, 
        sontechsp/uygulama/cekirdek/veritabani/moduller klasör hiyerarşisi mevcut olmalıdır
        **Doğrular: Gereksinim 1.1**
        """
        # Temel klasör yapısının varlığını kontrol et
        temel_klasorler = [
            "sontechsp",
            "sontechsp/uygulama", 
            "sontechsp/uygulama/cekirdek",
            "sontechsp/uygulama/veritabani",
            "sontechsp/uygulama/moduller",
            "sontechsp/uygulama/servisler",
            "sontechsp/uygulama/arayuz",
            "sontechsp/uygulama/kurulum",
            "sontechsp/testler"
        ]
        
        for klasor in temel_klasorler:
            assert os.path.exists(klasor), f"Klasör mevcut değil: {klasor}"
            assert os.path.isdir(klasor), f"Yol bir klasör değil: {klasor}"
    
    def test_modul_klasorleri_mevcut(self):
        """
        Ajan bazlı modül klasörlerinin varlığını kontrol eder
        """
        modul_klasorleri = [
            "sontechsp/uygulama/moduller/stok",
            "sontechsp/uygulama/moduller/pos", 
            "sontechsp/uygulama/moduller/crm",
            "sontechsp/uygulama/moduller/satis_belgeleri",
            "sontechsp/uygulama/moduller/eticaret",
            "sontechsp/uygulama/moduller/ebelge",
            "sontechsp/uygulama/moduller/kargo",
            "sontechsp/uygulama/moduller/raporlar"
        ]
        
        for klasor in modul_klasorleri:
            assert os.path.exists(klasor), f"Modül klasörü mevcut değil: {klasor}"
            assert os.path.isdir(klasor), f"Modül yolu bir klasör değil: {klasor}"
    
    def test_init_dosyalari_mevcut(self):
        """
        Tüm Python paketlerinin __init__.py dosyalarına sahip olduğunu kontrol eder
        """
        init_dosyalari = [
            "sontechsp/uygulama/__init__.py",
            "sontechsp/uygulama/cekirdek/__init__.py", 
            "sontechsp/uygulama/veritabani/__init__.py",
            "sontechsp/uygulama/moduller/__init__.py",
            "sontechsp/uygulama/moduller/stok/__init__.py",
            "sontechsp/uygulama/moduller/pos/__init__.py",
            "sontechsp/uygulama/moduller/crm/__init__.py",
            "sontechsp/uygulama/moduller/satis_belgeleri/__init__.py",
            "sontechsp/uygulama/moduller/eticaret/__init__.py",
            "sontechsp/uygulama/moduller/ebelge/__init__.py",
            "sontechsp/uygulama/moduller/kargo/__init__.py",
            "sontechsp/uygulama/moduller/raporlar/__init__.py",
            "sontechsp/uygulama/servisler/__init__.py",
            "sontechsp/uygulama/arayuz/__init__.py",
            "sontechsp/uygulama/kurulum/__init__.py",
            "sontechsp/testler/__init__.py"
        ]
        
        for init_dosya in init_dosyalari:
            assert os.path.exists(init_dosya), f"__init__.py dosyası mevcut değil: {init_dosya}"
            assert os.path.isfile(init_dosya), f"__init__.py yolu bir dosya değil: {init_dosya}"
    
    @given(st.sampled_from([
        "sontechsp/uygulama",
        "sontechsp/uygulama/cekirdek", 
        "sontechsp/uygulama/veritabani",
        "sontechsp/uygulama/moduller"
    ]))
    def test_klasor_hiyerarsisi_tutarliligi_property(self, klasor_yolu):
        """
        Property test: Herhangi bir temel klasör için hiyerarşi tutarlılığı
        """
        # Klasörün var olduğunu kontrol et
        assert os.path.exists(klasor_yolu), f"Klasör mevcut değil: {klasor_yolu}"
        assert os.path.isdir(klasor_yolu), f"Yol bir klasör değil: {klasor_yolu}"
        
        # Üst klasörün de var olduğunu kontrol et
        ust_klasor = os.path.dirname(klasor_yolu)
        if ust_klasor and ust_klasor != ".":
            assert os.path.exists(ust_klasor), f"Üst klasör mevcut değil: {ust_klasor}"
            assert os.path.isdir(ust_klasor), f"Üst yol bir klasör değil: {ust_klasor}"