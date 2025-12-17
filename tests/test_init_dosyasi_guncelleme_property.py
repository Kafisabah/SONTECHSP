# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_init_dosyasi_guncelleme_property
# Description: Init dosyası güncelleme tutarlılığı property testi
# Changelog:
# - İlk versiyon: Property 3 testi oluşturuldu

"""
**Feature: kod-kalitesi-standardizasyon, Property 3: Init Dosyası Güncelleme Tutarlılığı**
**Validates: Requirements 1.4**

Property: For any yeni alt dosya oluşturma işlemi, ilgili __init__.py dosyasının
otomatik güncellenmesi gerekir.
"""

import os
import tempfile
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from uygulama.moduller.kod_kalitesi.refactoring.dosya_bolucu import (
    DosyaBolucu, YeniDosya
)


@given(
    dosya_sayisi=st.integers(min_value=1, max_value=5)
)
@settings(max_examples=100, deadline=None)
def test_init_dosyasi_guncelleme_tutarliligi(dosya_sayisi):
    """
    **Feature: kod-kalitesi-standardizasyon, Property 3: Init Dosyası Güncelleme Tutarlılığı**
    **Validates: Requirements 1.4**
    
    Property: Yeni dosyalar oluşturulduğunda, __init__.py dosyası bu dosyaları
    import edecek şekilde otomatik güncellenmelidir.
    
    Test stratejisi:
    - Rastgele sayıda yeni dosya oluştur
    - __init__.py'yi güncelle
    - __init__.py'nin tüm yeni dosyaları import ettiğini doğrula
    """
    # Geçici dizin oluştur
    with tempfile.TemporaryDirectory() as temp_dir:
        # Yeni dosyalar oluştur
        yeni_dosyalar = []
        for i in range(dosya_sayisi):
            dosya = YeniDosya(
                dosya_adi=f"modul_{i}.py",
                dosya_yolu=os.path.join(temp_dir, f"modul_{i}.py"),
                icerik=f"# Modül {i}\n\ndef fonksiyon_{i}():\n    pass\n",
                import_listesi=[]
            )
            yeni_dosyalar.append(dosya)
            
            # Dosyayı fiziksel olarak oluştur
            Path(dosya.dosya_yolu).write_text(dosya.icerik, encoding='utf-8')
        
        # DosyaBolucu ile __init__.py'yi güncelle
        bolucu = DosyaBolucu()
        bolucu.init_dosyasini_guncelle(temp_dir, yeni_dosyalar)
        
        # __init__.py'nin oluşturulduğunu doğrula
        init_yolu = os.path.join(temp_dir, '__init__.py')
        assert os.path.exists(init_yolu), "__init__.py oluşturulmadı"
        
        # __init__.py içeriğini oku
        with open(init_yolu, 'r', encoding='utf-8') as f:
            init_icerik = f.read()
        
        # Property: Her yeni dosya için import ifadesi olmalı
        for dosya in yeni_dosyalar:
            modul_adi = Path(dosya.dosya_adi).stem
            beklenen_import = f"from .{modul_adi} import *"
            
            assert beklenen_import in init_icerik, (
                f"__init__.py'de {modul_adi} için import bulunamadı. "
                f"Beklenen: {beklenen_import}"
            )


@given(
    ilk_dosya_sayisi=st.integers(min_value=1, max_value=3),
    yeni_dosya_sayisi=st.integers(min_value=1, max_value=3)
)
@settings(max_examples=100, deadline=None)
def test_init_dosyasi_mevcut_importlari_korur(ilk_dosya_sayisi, yeni_dosya_sayisi):
    """
    Property: Mevcut __init__.py güncellenirken, eski import'lar korunmalıdır.
    
    Test stratejisi:
    - Mevcut import'larla bir __init__.py oluştur
    - Yeni dosyalar ekle
    - Hem eski hem yeni import'ların varlığını doğrula
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mevcut __init__.py oluştur
        mevcut_importlar = []
        for i in range(ilk_dosya_sayisi):
            mevcut_importlar.append(f"from .eski_modul_{i} import *")
        
        init_yolu = os.path.join(temp_dir, '__init__.py')
        mevcut_icerik = "# Mevcut init\n\n" + "\n".join(mevcut_importlar) + "\n"
        Path(init_yolu).write_text(mevcut_icerik, encoding='utf-8')
        
        # Yeni dosyalar oluştur
        yeni_dosyalar = []
        for i in range(yeni_dosya_sayisi):
            dosya = YeniDosya(
                dosya_adi=f"yeni_modul_{i}.py",
                dosya_yolu=os.path.join(temp_dir, f"yeni_modul_{i}.py"),
                icerik=f"# Yeni modül {i}\n",
                import_listesi=[]
            )
            yeni_dosyalar.append(dosya)
        
        # __init__.py'yi güncelle
        bolucu = DosyaBolucu()
        bolucu.init_dosyasini_guncelle(temp_dir, yeni_dosyalar)
        
        # Güncellenmiş içeriği oku
        with open(init_yolu, 'r', encoding='utf-8') as f:
            guncellenmis_icerik = f.read()
        
        # Property 1: Eski import'lar korunmalı
        for eski_import in mevcut_importlar:
            assert eski_import in guncellenmis_icerik, (
                f"Eski import korunmadı: {eski_import}"
            )
        
        # Property 2: Yeni import'lar eklenmiş olmalı
        for dosya in yeni_dosyalar:
            modul_adi = Path(dosya.dosya_adi).stem
            yeni_import = f"from .{modul_adi} import *"
            assert yeni_import in guncellenmis_icerik, (
                f"Yeni import eklenmedi: {yeni_import}"
            )
