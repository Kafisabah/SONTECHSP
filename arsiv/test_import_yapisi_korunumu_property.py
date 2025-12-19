# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_import_yapisi_korunumu_property
# Description: Import yapısı korunumu property testi
# Changelog:
# - İlk versiyon: Property 2 testi oluşturuldu

"""
**Feature: kod-kalitesi-standardizasyon, Property 2: Import Yapısı Korunumu**
**Validates: Requirements 1.3**

Property: For any dosya bölme işlemi, bölme öncesi ve sonrası import yapısının
işlevsel olarak eşdeğer olması gerekir.
"""

import ast
import tempfile
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from uygulama.moduller.kod_kalitesi.refactoring.dosya_bolucu import (
    DosyaBolucu, BolmeStratejisi
)


def python_kod_uret(fonksiyon_sayisi: int, import_sayisi: int) -> str:
    """Test için Python kodu üretir"""
    kod_parcalari = []
    
    # Import'lar ekle
    standart_importlar = ['os', 'sys', 'ast', 'pathlib', 'typing']
    for i in range(min(import_sayisi, len(standart_importlar))):
        kod_parcalari.append(f"import {standart_importlar[i]}")
    
    kod_parcalari.append('')
    
    # Fonksiyonlar ekle
    for i in range(fonksiyon_sayisi):
        fonk_turu = i % 3
        if fonk_turu == 0:
            # Doğrulama fonksiyonu
            kod_parcalari.append(f"""def dogrula_veri_{i}(veri):
    \"\"\"Veri doğrulama fonksiyonu\"\"\"
    return veri is not None
""")
        elif fonk_turu == 1:
            # Yardımcı fonksiyon
            kod_parcalari.append(f"""def _yardimci_{i}(x):
    \"\"\"Yardımcı fonksiyon\"\"\"
    return x * 2
""")
        else:
            # İşleme fonksiyonu
            kod_parcalari.append(f"""def isle_veri_{i}(veri):
    \"\"\"Veri işleme fonksiyonu\"\"\"
    return str(veri)
""")
    
    return '\n'.join(kod_parcalari)


def importlari_cikart(kod: str) -> set:
    """Koddaki import'ları çıkartır"""
    try:
        agac = ast.parse(kod)
    except SyntaxError:
        return set()
    
    importlar = set()
    for node in agac.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                importlar.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                importlar.add(node.module)
    
    return importlar


@given(
    fonksiyon_sayisi=st.integers(min_value=5, max_value=15),
    import_sayisi=st.integers(min_value=1, max_value=5)
)
@settings(max_examples=100, deadline=None)
def test_import_yapisi_korunumu(fonksiyon_sayisi, import_sayisi):
    """
    **Feature: kod-kalitesi-standardizasyon, Property 2: Import Yapısı Korunumu**
    **Validates: Requirements 1.3**
    
    Property: Dosya bölme işlemi sonrasında, orijinal dosyadaki tüm import'lar
    yeni dosyalarda korunmalıdır.
    
    Test stratejisi:
    - Rastgele sayıda fonksiyon ve import içeren kod üret
    - Dosyayı böl
    - Orijinal import'ları topla
    - Yeni dosyalardaki import'ları topla
    - İki kümenin eşit olduğunu doğrula
    """
    # Geçici dizin oluştur
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test kodu oluştur
        test_kodu = python_kod_uret(fonksiyon_sayisi, import_sayisi)
        
        # Orijinal import'ları çıkart
        orijinal_importlar = importlari_cikart(test_kodu)
        
        # Test dosyası oluştur
        test_dosya = Path(temp_dir) / "test_modul.py"
        test_dosya.write_text(test_kodu, encoding='utf-8')
        
        # Dosyayı böl
        bolucu = DosyaBolucu(strateji=BolmeStratejisi.FONKSIYONEL)
        yeni_dosyalar = bolucu.dosyayi_bol(str(test_dosya), temp_dir)
        
        # Yeni dosyalardaki import'ları topla
        yeni_importlar = set()
        for dosya in yeni_dosyalar:
            dosya_importlari = importlari_cikart(dosya.icerik)
            yeni_importlar.update(dosya_importlari)
        
        # Property: Orijinal import'lar korunmalı
        # Yeni dosyalardaki import'lar, orijinal import'ların bir üst kümesi olmalı
        # (çünkü bazı dosyalarda kullanılmayan import'lar da olabilir)
        assert orijinal_importlar.issubset(yeni_importlar), (
            f"Import'lar korunmadı. Orijinal: {orijinal_importlar}, "
            f"Yeni: {yeni_importlar}"
        )
