# Version: 0.1.0
# Last Update: 2024-12-15
# Module: test_cekirdek_bagimsizlik
# Description: Çekirdek modül bağımsızlık property testleri
# Changelog:
# - 0.1.0: İlk sürüm, çekirdek modül bağımsızlık testleri oluşturuldu

"""
Çekirdek Modül Bağımsızlık Property Testleri

Bu modül çekirdek altyapının diğer katmanlardan bağımsızlığını test eder.
"""

import ast
import importlib
import sys
from pathlib import Path
from typing import List, Set

import pytest
from hypothesis import given, strategies as st, settings


class CekirdekBagimsizlikTesti:
    """Çekirdek modül bağımsızlık testlerini içeren sınıf"""
    
    def __init__(self):
        self.cekirdek_klasoru = Path("sontechsp/uygulama/cekirdek")
        self.yasak_ui_moduller = {
            "PyQt6", "PyQt5", "tkinter", "wx", "kivy", "flet"
        }
        self.yasak_db_moduller = {
            "sqlalchemy", "psycopg2", "sqlite3", "pymongo", "redis"
        }
        self.izinli_standart_moduller = {
            "os", "sys", "json", "logging", "datetime", "pathlib",
            "typing", "dataclasses", "enum", "collections", "functools",
            "itertools", "re", "hashlib", "uuid", "time", "threading"
        }

    def _dosya_import_analizi(self, dosya_yolu: Path) -> Set[str]:
        """Dosyadaki import'ları analiz eder"""
        try:
            with open(dosya_yolu, 'r', encoding='utf-8') as f:
                icerik = f.read()
            
            agac = ast.parse(icerik)
            importlar = set()
            
            for node in ast.walk(agac):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        importlar.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        importlar.add(node.module.split('.')[0])
            
            return importlar
        except Exception:
            return set()

    def _cekirdek_dosyalarini_bul(self) -> List[Path]:
        """Çekirdek klasöründeki Python dosyalarını bulur"""
        if not self.cekirdek_klasoru.exists():
            return []
        
        dosyalar = []
        for dosya in self.cekirdek_klasoru.rglob("*.py"):
            if dosya.name != "__init__.py":
                dosyalar.append(dosya)
        return dosyalar


# **Feature: cekirdek-altyapi, Property 13: UI katman bağımsızlığı**
@settings(max_examples=100)
@given(st.just(None))
def test_ui_katman_bagimsizligi(dummy):
    """
    Özellik 13: UI katman bağımsızlığı
    Herhangi bir çekirdek modül için, UI katmanından bağımsız çalışmalıdır
    Doğrular: Gereksinim 6.1
    """
    tester = CekirdekBagimsizlikTesti()
    cekirdek_dosyalar = tester._cekirdek_dosyalarini_bul()
    
    for dosya in cekirdek_dosyalar:
        importlar = tester._dosya_import_analizi(dosya)
        ui_importlar = importlar.intersection(tester.yasak_ui_moduller)
        
        assert len(ui_importlar) == 0, (
            f"Çekirdek dosya {dosya} UI modüllerini import ediyor: {ui_importlar}"
        )


# **Feature: cekirdek-altyapi, Property 14: Veritabanı katman bağımsızlığı**
@settings(max_examples=100)
@given(st.just(None))
def test_veritabani_katman_bagimsizligi(dummy):
    """
    Özellik 14: Veritabanı katman bağımsızlığı
    Herhangi bir çekirdek modül için, veritabanı katmanından bağımsız çalışmalıdır
    Doğrular: Gereksinim 6.2
    """
    tester = CekirdekBagimsizlikTesti()
    cekirdek_dosyalar = tester._cekirdek_dosyalarini_bul()
    
    for dosya in cekirdek_dosyalar:
        importlar = tester._dosya_import_analizi(dosya)
        db_importlar = importlar.intersection(tester.yasak_db_moduller)
        
        assert len(db_importlar) == 0, (
            f"Çekirdek dosya {dosya} veritabanı modüllerini import ediyor: {db_importlar}"
        )


# **Feature: cekirdek-altyapi, Property 15: Standart kütüphane bağımlılığı**
@settings(max_examples=100)
@given(st.just(None))
def test_standart_kutuphane_bagimliligi(dummy):
    """
    Özellik 15: Standart kütüphane bağımlılığı
    Herhangi bir çekirdek modül için, sadece standart kütüphaneler kullanılmalıdır
    Doğrular: Gereksinim 6.3
    """
    tester = CekirdekBagimsizlikTesti()
    cekirdek_dosyalar = tester._cekirdek_dosyalarini_bul()
    
    for dosya in cekirdek_dosyalar:
        importlar = tester._dosya_import_analizi(dosya)
        
        # Kendi modüllerini ve standart kütüphaneleri filtrele
        harici_importlar = set()
        for imp in importlar:
            if (imp not in tester.izinli_standart_moduller and 
                not imp.startswith('sontechsp') and
                imp not in sys.builtin_module_names):
                harici_importlar.add(imp)
        
        assert len(harici_importlar) == 0, (
            f"Çekirdek dosya {dosya} harici kütüphaneleri import ediyor: {harici_importlar}"
        )


def test_cekirdek_modul_import_edilebilirlik():
    """Çekirdek modülün başarıyla import edilebilirliğini test eder"""
    try:
        import sontechsp.uygulama.cekirdek
        assert True
    except ImportError as e:
        pytest.fail(f"Çekirdek modül import edilemedi: {e}")


def test_cekirdek_baslat_fonksiyonu():
    """Çekirdek başlatma fonksiyonunun varlığını test eder"""
    try:
        from sontechsp.uygulama.cekirdek import cekirdek_baslat
        assert callable(cekirdek_baslat)
    except ImportError as e:
        pytest.fail(f"cekirdek_baslat fonksiyonu bulunamadı: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])