# Version: 0.1.0
# Last Update: 2024-12-15
# Module: test_turkce_dokumantasyon_standardi
# Description: SONTECHSP Türkçe dokümantasyon standardı property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Türkçe Dokümantasyon Standardı Property Testleri

**Feature: sontechsp-proje-iskeleti, Property 11: Türkçe dokümantasyon standardı**

Türkçe dokümantasyon kurallarının doğruluğunu test eder:
- Türkçe inline açıklamalar
- ASCII Türkçe isimlendirme (Türkçe karakter yok)
- Docstring'lerde Türkçe kullanım
- Değişken ve fonksiyon isimlerinde ASCII
"""

import os
import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Set

import pytest
from hypothesis import given, strategies as st, assume, settings

# Test edilecek proje kök dizini
PROJE_KOK = Path(__file__).parent.parent

# Türkçe karakterler
TURKCE_KARAKTERLER = set('çğıöşüÇĞIİÖŞÜ')

# ASCII Türkçe karşılıkları
ASCII_TURKCE_KARSILIKLAR = {
    'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
    'Ç': 'C', 'Ğ': 'G', 'I': 'I', 'İ': 'I', 'Ö': 'O', 'Ş': 'S', 'Ü': 'U'
}


def python_dosyalarini_al() -> List[Path]:
    """Projedeki tüm Python dosyalarını döndürür"""
    python_dosyalar = []
    
    for dosya_yolu in PROJE_KOK.rglob("*.py"):
        # __pycache__ klasörlerini hariç tut
        if "__pycache__" not in str(dosya_yolu):
            python_dosyalar.append(dosya_yolu)
    
    return python_dosyalar


def turkce_karakter_kontrol_et(metin: str) -> Dict[str, Any]:
    """
    Metinde Türkçe karakter kontrolü yapar
    
    Returns:
        Dict: Türkçe karakter bilgileri
    """
    turkce_karakterler_bulundu = set()
    
    for karakter in metin:
        if karakter in TURKCE_KARAKTERLER:
            turkce_karakterler_bulundu.add(karakter)
    
    return {
        'turkce_karakter_var': len(turkce_karakterler_bulundu) > 0,
        'bulunan_karakterler': list(turkce_karakterler_bulundu),
        'karakter_sayisi': len(turkce_karakterler_bulundu)
    }


def kod_isimlendirme_kontrol_et(dosya_yolu: Path) -> Dict[str, Any]:
    """
    Dosyadaki değişken, fonksiyon ve sınıf isimlerinde ASCII kontrolü
    
    Returns:
        Dict: İsimlendirme bilgileri
    """
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            icerik = f.read()
        
        # AST ile parse et
        agac = ast.parse(icerik)
        
        problemli_isimler = []
        
        for node in ast.walk(agac):
            isim = None
            
            if isinstance(node, ast.FunctionDef):
                isim = node.name
            elif isinstance(node, ast.ClassDef):
                isim = node.name
            elif isinstance(node, ast.Name):
                isim = node.id
            elif isinstance(node, ast.arg):
                isim = node.arg
            
            if isim and any(k in isim for k in TURKCE_KARAKTERLER):
                problemli_isimler.append({
                    'isim': isim,
                    'tip': type(node).__name__,
                    'satir': getattr(node, 'lineno', 0)
                })
        
        return {
            'problemli_isimler': problemli_isimler,
            'toplam_problem': len(problemli_isimler)
        }
        
    except Exception as e:
        return {
            'problemli_isimler': [],
            'toplam_problem': 0,
            'hata': str(e)
        }


def yorum_satirlari_kontrol_et(dosya_yolu: Path) -> Dict[str, Any]:
    """
    Dosyadaki yorum satırlarını kontrol eder
    
    Returns:
        Dict: Yorum bilgileri
    """
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            satirlar = f.readlines()
        
        yorum_satirlari = []
        turkce_yorumlar = []
        
        for i, satir in enumerate(satirlar, 1):
            satir_temiz = satir.strip()
            
            # Yorum satırı mı kontrol et
            if satir_temiz.startswith('#'):
                yorum_satirlari.append({
                    'satir_no': i,
                    'icerik': satir_temiz
                })
                
                # Türkçe karakter var mı kontrol et
                turkce_kontrol = turkce_karakter_kontrol_et(satir_temiz)
                if turkce_kontrol['turkce_karakter_var']:
                    turkce_yorumlar.append({
                        'satir_no': i,
                        'icerik': satir_temiz,
                        'karakterler': turkce_kontrol['bulunan_karakterler']
                    })
        
        return {
            'toplam_yorum': len(yorum_satirlari),
            'turkce_yorum_sayisi': len(turkce_yorumlar),
            'turkce_yorumlar': turkce_yorumlar
        }
        
    except Exception:
        return {
            'toplam_yorum': 0,
            'turkce_yorum_sayisi': 0,
            'turkce_yorumlar': []
        }


def docstring_kontrol_et(dosya_yolu: Path) -> Dict[str, Any]:
    """
    Dosyadaki docstring'leri kontrol eder
    
    Returns:
        Dict: Docstring bilgileri
    """
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            icerik = f.read()
        
        # AST ile parse et
        agac = ast.parse(icerik)
        
        docstring_bilgileri = []
        
        for node in ast.walk(agac):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                # İlk statement docstring mı kontrol et
                if (node.body and 
                    isinstance(node.body[0], ast.Expr) and 
                    isinstance(node.body[0].value, ast.Constant) and 
                    isinstance(node.body[0].value.value, str)):
                    
                    docstring = node.body[0].value.value
                    
                    # Türkçe karakter kontrolü
                    turkce_kontrol = turkce_karakter_kontrol_et(docstring)
                    
                    docstring_bilgileri.append({
                        'tip': type(node).__name__,
                        'isim': getattr(node, 'name', 'module'),
                        'satir': getattr(node, 'lineno', 0),
                        'docstring_uzunluk': len(docstring),
                        'turkce_karakter_var': turkce_kontrol['turkce_karakter_var'],
                        'bulunan_karakterler': turkce_kontrol['bulunan_karakterler']
                    })
        
        return {
            'docstring_sayisi': len(docstring_bilgileri),
            'docstring_bilgileri': docstring_bilgileri
        }
        
    except Exception:
        return {
            'docstring_sayisi': 0,
            'docstring_bilgileri': []
        }


class TestTurkceDokmantasyonStandardi:
    """SONTECHSP Türkçe dokümantasyon standardı testleri"""
    
    @pytest.mark.slow
    @pytest.mark.integration
    @pytest.mark.parametrize("dosya_yolu", python_dosyalarini_al())
    def test_kod_isimlendirme_ascii(self, dosya_yolu: Path):
        """
        **Feature: sontechsp-proje-iskeleti, Property 11: Türkçe dokümantasyon standardı**
        
        Kod isimlendirmesinde (değişken, fonksiyon, sınıf) Türkçe karakter kullanılmamalıdır.
        ASCII Türkçe isimlendirme kuralı uygulanmalıdır.
        """
        isimlendirme_bilgileri = kod_isimlendirme_kontrol_et(dosya_yolu)
        
        assert isimlendirme_bilgileri['toplam_problem'] == 0, (
            f"Dosya {dosya_yolu.name} kod isimlendirmesinde Türkçe karakter kullanılmış: "
            f"{isimlendirme_bilgileri['problemli_isimler']}"
        )
    
    @pytest.mark.slow
    @pytest.mark.integration
    @pytest.mark.parametrize("dosya_yolu", python_dosyalarini_al())
    def test_yorum_satirlari_turkce_destegi(self, dosya_yolu: Path):
        """
        **Feature: sontechsp-proje-iskeleti, Property 11: Türkçe dokümantasyon standardı**
        
        Yorum satırlarında Türkçe karakter kullanımına izin verilir.
        Bu test sadece yorum satırlarının varlığını kontrol eder.
        """
        yorum_bilgileri = yorum_satirlari_kontrol_et(dosya_yolu)
        
        # Yorum satırları olması beklenir (en az birkaç tane)
        if dosya_yolu.name != "__init__.py":  # __init__.py dosyaları hariç
            # En az dosya başlığı yorumu olmalı
            assert yorum_bilgileri['toplam_yorum'] >= 5, (
                f"Dosya {dosya_yolu.name} yeterli yorum satırı içermiyor: "
                f"{yorum_bilgileri['toplam_yorum']} < 5"
            )
    
    @pytest.mark.parametrize("dosya_yolu", python_dosyalarini_al())
    def test_docstring_varligi(self, dosya_yolu: Path):
        """
        **Feature: sontechsp-proje-iskeleti, Property 11: Türkçe dokümantasyon standardı**
        
        Fonksiyon ve sınıflarda docstring bulunmalıdır.
        Docstring'lerde Türkçe karakter kullanımına izin verilir.
        """
        docstring_bilgileri = docstring_kontrol_et(dosya_yolu)
        
        # __init__.py dosyaları hariç, en az modül docstring'i olmalı
        if dosya_yolu.name != "__init__.py":
            assert docstring_bilgileri['docstring_sayisi'] >= 1, (
                f"Dosya {dosya_yolu.name} docstring içermiyor"
            )


@pytest.mark.property
@given(st.text(min_size=1, max_size=100))
@settings(max_examples=50)
def test_ascii_turkce_donusum_property(metin: str):
    """
    **Feature: sontechsp-proje-iskeleti, Property 11: Türkçe dokümantasyon standardı**
    
    Herhangi bir metin için ASCII Türkçe dönüşümü doğru çalışmalıdır.
    """
    assume(len(metin.strip()) > 0)
    
    # Türkçe karakterleri ASCII karşılıklarına dönüştür
    ascii_metin = metin
    for turkce_kar, ascii_kar in ASCII_TURKCE_KARSILIKLAR.items():
        ascii_metin = ascii_metin.replace(turkce_kar, ascii_kar)
    
    # Dönüştürülmüş metinde Türkçe karakter kalmamalı
    turkce_kontrol = turkce_karakter_kontrol_et(ascii_metin)
    
    assert not turkce_kontrol['turkce_karakter_var'], (
        f"ASCII dönüşümü başarısız: {turkce_kontrol['bulunan_karakterler']}"
    )


@pytest.mark.property
@given(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=1, max_size=50))
@settings(max_examples=30)
def test_kod_ismi_gecerliligi_property(kod_ismi: str):
    """
    **Feature: sontechsp-proje-iskeleti, Property 11: Türkçe dokümantasyon standardı**
    
    Herhangi bir kod ismi için ASCII kuralları geçerli olmalıdır.
    """
    assume(len(kod_ismi.strip()) > 0)
    assume(kod_ismi[0].isalpha() or kod_ismi[0] == '_')  # Geçerli Python identifier
    
    # Türkçe karakter kontrolü
    turkce_kontrol = turkce_karakter_kontrol_et(kod_ismi)
    
    # Kod isimlerinde Türkçe karakter olmamalı
    assert not turkce_kontrol['turkce_karakter_var'], (
        f"Kod isminde Türkçe karakter: {kod_ismi} -> {turkce_kontrol['bulunan_karakterler']}"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])