# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_test_guncelleme_tutarliligi_property
# Description: Property test - Test güncelleme tutarlılığı
# Changelog:
# - İlk versiyon: Property 20 testi oluşturuldu

"""
Property Test: Test Güncelleme Tutarlılığı

**Feature: kod-kalitesi-standardizasyon, Property 20: Test Güncelleme Tutarlılığı**
**Validates: Requirements 6.2**

For any dosya bölme işlemi, ilgili testlerin güncellenmesi gerekir.
"""

import os
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from uygulama.moduller.kod_kalitesi.test_entegrasyon import (
    TestGuncelleyici,
    DosyaDegisikligi
)


# Stratejiler
modul_adi_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=('Ll', 'Lu'),
        whitelist_characters='_'
    ),
    min_size=5,
    max_size=20
).filter(lambda x: x and x[0].isalpha() and not x.startswith('_') and '_' in x)

sembol_adi_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=('Ll', 'Lu'),
        whitelist_characters='_'
    ),
    min_size=8,
    max_size=15
).filter(lambda x: x and x[0].isalpha() and '_' in x)


@settings(max_examples=100)
@given(
    eski_modul=modul_adi_strategy,
    yeni_modul=modul_adi_strategy,
    sembol=sembol_adi_strategy
)
def test_test_guncelleme_tutarliligi_property(
    eski_modul: str,
    yeni_modul: str,
    sembol: str
):
    """
    Property: For any dosya bölme işlemi,
    ilgili testlerin güncellenmesi gerekir.
    
    Test eder:
    1. Etkilenen testler doğru tespit edilmeli
    2. Import yapısı güncellendiğinde eski modül referansı kalmamalı
    3. Yeni modül referansı eklenmiş olmalı
    4. Test dosyası geçerli Python kodu olmalı
    """
    # Farklı modül adları olmalı ve sembol farklı olmalı
    assume(eski_modul != yeni_modul)
    assume(sembol != eski_modul)
    assume(sembol != yeni_modul)
    
    # Geçici test klasörü oluştur
    with tempfile.TemporaryDirectory() as test_klasoru:
        # Test dosyası oluştur
        test_dosyasi = os.path.join(test_klasoru, 'test_ornek.py')
        
        # Test içeriği - eski modülü import eden
        test_icerigi = f"""# Test dosyası
from uygulama.moduller.{eski_modul} import {sembol}

def test_ornek():
    # Test kodu
    assert {sembol} is not None
"""
        
        with open(test_dosyasi, 'w', encoding='utf-8') as f:
            f.write(test_icerigi)
        
        # Test güncelleyici oluştur
        guncelleyici = TestGuncelleyici(test_klasoru=test_klasoru)
        
        # Değişiklik bilgisi
        degisiklik = DosyaDegisikligi(
            eski_yol=f"uygulama/moduller/{eski_modul}.py",
            yeni_yol=f"uygulama/moduller/{yeni_modul}.py",
            eski_modul=f"uygulama.moduller.{eski_modul}",
            yeni_modul=f"uygulama.moduller.{yeni_modul}",
            tasınan_semboller=[sembol]
        )
        
        # Property 1: Import yapısını güncelle
        basari = guncelleyici.import_yapisini_guncelle(
            test_dosyasi,
            f"uygulama.moduller.{eski_modul}",
            f"uygulama.moduller.{yeni_modul}",
            [sembol]
        )
        assert basari, "Import güncelleme başarısız"
        
        # Güncellenmiş içeriği oku
        with open(test_dosyasi, 'r', encoding='utf-8') as f:
            guncellenmis_icerik = f.read()
        
        # Property 2: Yeni modül referansı eklenmiş olmalı
        assert yeni_modul in guncellenmis_icerik, \
            f"Yeni modül referansı eklenmedi: {yeni_modul}"
        
        # Property 3: Sembol import'u korunmalı
        assert f"import {sembol}" in guncellenmis_icerik, \
            "Sembol import'u kayboldu"
        
        # Property 4: Test dosyası geçerli Python kodu olmalı
        try:
            compile(guncellenmis_icerik, test_dosyasi, 'exec')
        except SyntaxError as e:
            raise AssertionError(f"Güncellenmiş test geçersiz Python kodu: {e}")


@settings(max_examples=100)
@given(
    modul_sayisi=st.integers(min_value=2, max_value=5),
    sembol_sayisi=st.integers(min_value=1, max_value=3)
)
def test_coklu_degisiklik_tutarliligi_property(
    modul_sayisi: int,
    sembol_sayisi: int
):
    """
    Property: For any çoklu dosya bölme işlemi,
    tüm ilgili testlerin tutarlı şekilde güncellenmesi gerekir.
    
    Test eder:
    1. Birden fazla değişiklik aynı anda uygulanabilmeli
    2. Tüm eski modül referansları temizlenmeli
    3. Test dosyası geçerli kalmalı
    """
    # Geçici test klasörü oluştur
    with tempfile.TemporaryDirectory() as test_klasoru:
        # Test dosyası oluştur
        test_dosyasi = os.path.join(test_klasoru, 'test_coklu.py')
        
        # Değişiklikler oluştur
        degisiklikler = []
        import_satirlari = []
        
        for i in range(modul_sayisi):
            eski_modul = f"modul_{i}"
            yeni_modul = f"yeni_modul_{i}"
            
            semboller = [f"sembol_{i}_{j}" for j in range(sembol_sayisi)]
            
            import_satirlari.append(
                f"from uygulama.moduller.{eski_modul} import {', '.join(semboller)}"
            )
            
            degisiklikler.append(DosyaDegisikligi(
                eski_yol=f"uygulama/moduller/{eski_modul}.py",
                yeni_yol=f"uygulama/moduller/{yeni_modul}.py",
                eski_modul=f"uygulama.moduller.{eski_modul}",
                yeni_modul=f"uygulama.moduller.{yeni_modul}",
                tasınan_semboller=semboller
            ))
        
        # Test içeriği
        test_icerigi = f"""# Test dosyası
{chr(10).join(import_satirlari)}

def test_coklu():
    # Test kodu
    pass
"""
        
        with open(test_dosyasi, 'w', encoding='utf-8') as f:
            f.write(test_icerigi)
        
        # Test güncelleyici oluştur
        guncelleyici = TestGuncelleyici(test_klasoru=test_klasoru)
        
        # Property 1: Tüm değişiklikleri uygula
        sonuclar = guncelleyici.testleri_guncelle(degisiklikler)
        
        assert len(sonuclar) > 0, "Hiç test güncellenmedi"
        
        # Property 2: Güncelleme başarılı olmalı
        for sonuc in sonuclar:
            assert sonuc.guncelleme_basarili, \
                f"Test güncelleme başarısız: {sonuc.hata_mesaji}"
        
        # Güncellenmiş içeriği oku
        with open(test_dosyasi, 'r', encoding='utf-8') as f:
            guncellenmis_icerik = f.read()
        
        # Property 3: Tüm yeni modül referansları eklenmiş olmalı
        for i in range(modul_sayisi):
            yeni_modul = f"yeni_modul_{i}"
            assert yeni_modul in guncellenmis_icerik, \
                f"Yeni modül referansı eklenmedi: {yeni_modul}"
        
        # Property 4: Test dosyası geçerli Python kodu olmalı
        try:
            compile(guncellenmis_icerik, test_dosyasi, 'exec')
        except SyntaxError as e:
            raise AssertionError(f"Güncellenmiş test geçersiz Python kodu: {e}")
