# Version: 0.1.0
# Last Update: 2024-12-15
# Module: test_yardimcilari
# Description: SONTECHSP test yardımcı fonksiyonları
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Test Yardımcı Fonksiyonları

Test yazımında kullanılan ortak yardımcı fonksiyonlar.
Property-based test şablonları ve veri üreticileri.

Sorumluluklar:
- Test veri üreticileri
- Ortak test fonksiyonları
- Property test şablonları
- Test doğrulama yardımcıları
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable

from hypothesis import strategies as st


def python_dosya_stratejisi() -> st.SearchStrategy[str]:
    """
    Geçerli Python dosya içeriği üretir
    
    Returns:
        SearchStrategy: Python dosya içeriği stratejisi
    """
    return st.text(
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc', 'Pd', 'Ps', 'Pe', 'Zs'),
            whitelist_characters='\n#"\'()[]{}:.,_'
        ),
        min_size=10,
        max_size=500
    )


def fonksiyon_ismi_stratejisi() -> st.SearchStrategy[str]:
    """
    Geçerli Python fonksiyon ismi üretir
    
    Returns:
        SearchStrategy: Fonksiyon ismi stratejisi
    """
    return st.text(
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='_'
        ),
        min_size=1,
        max_size=50
    ).filter(lambda x: x and (x[0].isalpha() or x[0] == '_'))


def sinif_ismi_stratejisi() -> st.SearchStrategy[str]:
    """
    Geçerli Python sınıf ismi üretir (PascalCase)
    
    Returns:
        SearchStrategy: Sınıf ismi stratejisi
    """
    return st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
        min_size=1,
        max_size=50
    ).filter(lambda x: x and x[0].isupper())


def dosya_basligi_stratejisi() -> st.SearchStrategy[Dict[str, str]]:
    """
    SONTECHSP dosya başlığı üretir
    
    Returns:
        SearchStrategy: Dosya başlığı stratejisi
    """
    return st.fixed_dictionaries({
        'version': st.text(min_size=5, max_size=10).filter(lambda x: '.' in x),
        'last_update': st.dates().map(str),
        'module': st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='._'), min_size=1, max_size=30),
        'description': st.text(min_size=10, max_size=100),
        'changelog': st.lists(st.text(min_size=5, max_size=50), min_size=1, max_size=5)
    })


def dosya_basligi_olustur(baslık_bilgileri: Dict[str, Any]) -> str:
    """
    Dosya başlığı string'i oluşturur
    
    Args:
        baslık_bilgileri: Başlık bilgileri
        
    Returns:
        str: Formatlanmış dosya başlığı
    """
    changelog_satirlari = '\n'.join(f'# - {item}' for item in baslık_bilgileri['changelog'])
    
    return f"""# Version: {baslık_bilgileri['version']}
# Last Update: {baslık_bilgileri['last_update']}
# Module: {baslık_bilgileri['module']}
# Description: {baslık_bilgileri['description']}
# Changelog:
{changelog_satirlari}"""


def python_kodu_parse_et(kod: str) -> Optional[ast.AST]:
    """
    Python kodunu AST'ye parse eder
    
    Args:
        kod: Python kodu
        
    Returns:
        Optional[ast.AST]: Parse edilmiş AST veya None
    """
    try:
        return ast.parse(kod)
    except SyntaxError:
        return None


def fonksiyon_satirlarini_say(kod: str, fonksiyon_ismi: str) -> int:
    """
    Belirli bir fonksiyonun satır sayısını hesaplar
    
    Args:
        kod: Python kodu
        fonksiyon_ismi: Fonksiyon ismi
        
    Returns:
        int: Fonksiyon satır sayısı
    """
    try:
        agac = ast.parse(kod)
        
        for node in ast.walk(agac):
            if (isinstance(node, ast.FunctionDef) and 
                node.name == fonksiyon_ismi):
                
                baslangic = node.lineno
                bitis = node.end_lineno if hasattr(node, 'end_lineno') else baslangic
                return bitis - baslangic + 1
        
        return 0
        
    except SyntaxError:
        return 0


def kod_satirlarini_say(kod: str) -> Dict[str, int]:
    """
    Kod satır sayılarını hesaplar
    
    Args:
        kod: Python kodu
        
    Returns:
        Dict[str, int]: Satır sayı bilgileri
    """
    satirlar = kod.split('\n')
    
    toplam_satirlar = len(satirlar)
    yorum_satirlari = sum(1 for s in satirlar if s.strip().startswith('#'))
    bos_satirlar = sum(1 for s in satirlar if not s.strip())
    kod_satirlari = toplam_satirlar - yorum_satirlari - bos_satirlar
    
    return {
        'toplam': toplam_satirlar,
        'kod': kod_satirlari,
        'yorum': yorum_satirlari,
        'bos': bos_satirlar
    }


def dosya_basligi_kontrol_et(kod: str) -> Dict[str, bool]:
    """
    Dosya başlığının varlığını kontrol eder
    
    Args:
        kod: Python kodu
        
    Returns:
        Dict[str, bool]: Başlık alan varlık bilgileri
    """
    ilk_satirlar = kod.split('\n')[:10]
    ilk_satirlar_str = '\n'.join(ilk_satirlar)
    
    return {
        'version': '# Version:' in ilk_satirlar_str,
        'last_update': '# Last Update:' in ilk_satirlar_str,
        'module': '# Module:' in ilk_satirlar_str,
        'description': '# Description:' in ilk_satirlar_str,
        'changelog': '# Changelog:' in ilk_satirlar_str
    }


def turkce_karakter_var_mi(metin: str) -> bool:
    """
    Metinde Türkçe karakter olup olmadığını kontrol eder
    
    Args:
        metin: Kontrol edilecek metin
        
    Returns:
        bool: Türkçe karakter var mı
    """
    turkce_karakterler = set('çğıöşüÇĞIİÖŞÜ')
    return any(karakter in turkce_karakterler for karakter in metin)


def ascii_turkce_donustur(metin: str) -> str:
    """
    Türkçe karakterleri ASCII karşılıklarına dönüştürür
    
    Args:
        metin: Dönüştürülecek metin
        
    Returns:
        str: ASCII'ye dönüştürülmüş metin
    """
    donusum_tablosu = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'Ç': 'C', 'Ğ': 'G', 'I': 'I', 'İ': 'I', 'Ö': 'O', 'Ş': 'S', 'Ü': 'U'
    }
    
    sonuc = metin
    for turkce_kar, ascii_kar in donusum_tablosu.items():
        sonuc = sonuc.replace(turkce_kar, ascii_kar)
    
    return sonuc


def klasor_yapisi_kontrol_et(kök_dizin: Path, beklenen_yapilar: List[str]) -> Dict[str, bool]:
    """
    Klasör yapısının varlığını kontrol eder
    
    Args:
        kök_dizin: Kök dizin
        beklenen_yapilar: Beklenen klasör/dosya yolları
        
    Returns:
        Dict[str, bool]: Yapı varlık bilgileri
    """
    sonuclar = {}
    
    for yapi in beklenen_yapilar:
        yol = kök_dizin / yapi
        sonuclar[yapi] = yol.exists()
    
    return sonuclar


def property_test_sablon_olustur(
    test_ismi: str,
    property_numarasi: int,
    property_aciklamasi: str,
    dogrulama_fonksiyonu: Callable
) -> Callable:
    """
    Property-based test şablonu oluşturur
    
    Args:
        test_ismi: Test ismi
        property_numarasi: Property numarası
        property_aciklamasi: Property açıklaması
        dogrulama_fonksiyonu: Doğrulama fonksiyonu
        
    Returns:
        Callable: Test fonksiyonu
    """
    def test_fonksiyonu(*args, **kwargs):
        f"""
        **Feature: sontechsp-proje-iskeleti, Property {property_numarasi}: {property_aciklamasi}**
        
        {test_ismi}
        """
        return dogrulama_fonksiyonu(*args, **kwargs)
    
    test_fonksiyonu.__name__ = f"test_{test_ismi}"
    test_fonksiyonu.__doc__ = f"""
    **Feature: sontechsp-proje-iskeleti, Property {property_numarasi}: {property_aciklamasi}**
    
    {test_ismi}
    """
    
    return test_fonksiyonu


class TestDogrulayicilari:
    """Test doğrulama yardımcı sınıfı"""
    
    @staticmethod
    def dosya_boyutu_dogrula(dosya_yolu: Path, max_boyut: int) -> bool:
        """
        Dosya boyutunu doğrular
        
        Args:
            dosya_yolu: Dosya yolu
            max_boyut: Maksimum boyut (byte)
            
        Returns:
            bool: Boyut uygun mu
        """
        try:
            return dosya_yolu.stat().st_size <= max_boyut
        except OSError:
            return False
    
    @staticmethod
    def python_syntax_dogrula(kod: str) -> bool:
        """
        Python syntax doğruluğunu kontrol eder
        
        Args:
            kod: Python kodu
            
        Returns:
            bool: Syntax doğru mu
        """
        try:
            ast.parse(kod)
            return True
        except SyntaxError:
            return False
    
    @staticmethod
    def import_dogrula(kod: str, beklenen_importlar: List[str]) -> bool:
        """
        Import ifadelerini doğrular
        
        Args:
            kod: Python kodu
            beklenen_importlar: Beklenen import'lar
            
        Returns:
            bool: Import'lar mevcut mu
        """
        try:
            agac = ast.parse(kod)
            
            bulunan_importlar = set()
            
            for node in ast.walk(agac):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        bulunan_importlar.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        bulunan_importlar.add(node.module)
            
            return all(imp in bulunan_importlar for imp in beklenen_importlar)
            
        except SyntaxError:
            return False