# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_test_import_guncelleme_property
# Description: Property test - Test import güncelleme
# Changelog:
# - İlk versiyon: Property 21 testi oluşturuldu

"""
Property Test: Test Import Güncelleme

**Feature: kod-kalitesi-standardizasyon, Property 21: Test Import Güncelleme**
**Validates: Requirements 6.3**

For any yeni modül oluşturma işlemi, test import yapılarının düzenlenmesi gerekir.
"""

import os
import tempfile
import ast
from hypothesis import given, strategies as st, settings, assume
from uygulama.moduller.kod_kalitesi.test_entegrasyon import (
    TestGuncelleyici,
    DosyaDegisikligi
)


# Stratejiler
modul_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Ll', 'Lu'), whitelist_characters='_'),
    min_size=5,
    max_size=15
).filter(lambda x: x and x[0].isalpha() and not x.startswith('_'))


@settings(max_examples=100)
@given(
    eski_modul=modul_strategy,
    yeni_modul=modul_strategy
)
def test_test_import_guncelleme_property(eski_modul: str, yeni_modul: str):
    """
    Property: For any yeni modül oluşturma işlemi,
    test import yapılarının düzenlenmesi gerekir.
    
    Test eder:
    1. Import güncelleme işlemi başarılı olmalı
    2. Güncellenmiş import geçerli Python kodu olmalı
    3. Yeni modül adı import'ta bulunmalı
    """
    assume(eski_modul != yeni_modul)
    
    with tempfile.TemporaryDirectory() as test_klasoru:
        test_dosyasi = os.path.join(test_klasoru, 'test_import.py')
        
        # Test içeriği
        test_icerigi = f"""# Test
from uygulama.moduller.{eski_modul} import fonksiyon

def test_fonksiyon():
    assert fonksiyon is not None
"""
        
        with open(test_dosyasi, 'w', encoding='utf-8') as f:
            f.write(test_icerigi)
        
        guncelleyici = TestGuncelleyici(test_klasoru=test_klasoru)
        
        # Property 1: Import güncelleme başarılı olmalı
        basari = guncelleyici.import_yapisini_guncelle(
            test_dosyasi,
            f"uygulama.moduller.{eski_modul}",
            f"uygulama.moduller.{yeni_modul}"
        )
        assert basari, "Import güncelleme başarısız"
        
        # Güncellenmiş içeriği oku
        with open(test_dosyasi, 'r', encoding='utf-8') as f:
            guncellenmis = f.read()
        
        # Property 2: Geçerli Python kodu olmalı
        try:
            ast.parse(guncellenmis)
        except SyntaxError as e:
            raise AssertionError(f"Geçersiz Python kodu: {e}")
        
        # Property 3: Yeni modül adı bulunmalı
        assert yeni_modul in guncellenmis, \
            f"Yeni modül adı bulunamadı: {yeni_modul}"


@settings(max_examples=100)
@given(modul=modul_strategy)
def test_import_yapisi_korunumu_property(modul: str):
    """
    Property: Import yapısı güncellendiğinde,
    import edilen sembollerin korunması gerekir.
    """
    with tempfile.TemporaryDirectory() as test_klasoru:
        test_dosyasi = os.path.join(test_klasoru, 'test_sembol.py')
        
        semboller = ['fonk1', 'fonk2', 'Sinif1']
        test_icerigi = f"""from uygulama.moduller.{modul} import {', '.join(semboller)}

def test():
    pass
"""
        
        with open(test_dosyasi, 'w', encoding='utf-8') as f:
            f.write(test_icerigi)
        
        guncelleyici = TestGuncelleyici(test_klasoru=test_klasoru)
        yeni_modul = f"yeni_{modul}"
        
        guncelleyici.import_yapisini_guncelle(
            test_dosyasi,
            f"uygulama.moduller.{modul}",
            f"uygulama.moduller.{yeni_modul}"
        )
        
        with open(test_dosyasi, 'r', encoding='utf-8') as f:
            guncellenmis = f.read()
        
        # Property: Tüm semboller korunmalı
        for sembol in semboller:
            assert sembol in guncellenmis, \
                f"Sembol kayboldu: {sembol}"
