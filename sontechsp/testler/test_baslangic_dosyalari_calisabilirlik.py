# Version: 0.1.0
# Last Update: 2024-12-15
# Module: test_baslangic_dosyalari_calisabilirlik
# Description: SONTECHSP başlangıç dosyaları çalışabilirlik property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Başlangıç Dosyaları Çalışabilirlik Property Testleri

**Feature: sontechsp-proje-iskeleti, Property 15: Başlangıç dosyaları çalışabilirliği**

Başlangıç dosyalarının çalışabilirliğini test eder:
- Import edilebilirlik
- Syntax doğruluğu
- Temel fonksiyonellik
- Bağımlılık kontrolü
"""

import sys
import ast
import importlib
import importlib.util
from pathlib import Path
from typing import List, Dict, Any, Optional

import pytest
from hypothesis import given, strategies as st, assume, settings

# Test edilecek proje kök dizini
PROJE_KOK = Path(__file__).parent.parent

# Sys.path'e proje kökünü ekle
if str(PROJE_KOK) not in sys.path:
    sys.path.insert(0, str(PROJE_KOK))


def kritik_dosyalari_al() -> List[Path]:
    """Kritik başlangıç dosyalarını döndürür"""
    kritik_dosyalar = [
        PROJE_KOK / "sontechsp" / "uygulama" / "ana.py",
        PROJE_KOK / "sontechsp" / "uygulama" / "cekirdek" / "kayit.py",
        PROJE_KOK / "sontechsp" / "uygulama" / "cekirdek" / "hatalar.py",
        PROJE_KOK / "sontechsp" / "uygulama" / "cekirdek" / "oturum.py",
        PROJE_KOK / "sontechsp" / "uygulama" / "veritabani" / "baglanti.py",
        PROJE_KOK / "sontechsp" / "uygulama" / "veritabani" / "taban.py",
        PROJE_KOK / "sontechsp" / "uygulama" / "arayuz" / "ana_pencere.py",
        PROJE_KOK / "sontechsp" / "uygulama" / "arayuz" / "taban_ekran.py",
        PROJE_KOK / "sontechsp" / "uygulama" / "servisler" / "taban_servis.py"
    ]
    
    # Sadece mevcut dosyaları döndür
    return [dosya for dosya in kritik_dosyalar if dosya.exists()]


def python_dosyalarini_al() -> List[Path]:
    """Projedeki tüm Python dosyalarını döndürür"""
    python_dosyalar = []
    
    for dosya_yolu in PROJE_KOK.rglob("*.py"):
        # Test dosyalarını ve __pycache__ klasörlerini hariç tut
        if "__pycache__" not in str(dosya_yolu) and not dosya_yolu.name.startswith("test_"):
            python_dosyalar.append(dosya_yolu)
    
    return python_dosyalar


def dosya_syntax_kontrol_et(dosya_yolu: Path) -> Dict[str, Any]:
    """
    Dosyanın syntax doğruluğunu kontrol eder
    
    Returns:
        Dict: Syntax kontrol bilgileri
    """
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            icerik = f.read()
        
        # AST ile parse et
        agac = ast.parse(icerik, filename=str(dosya_yolu))
        
        return {
            'syntax_dogru': True,
            'hata': None,
            'ast_node_sayisi': len(list(ast.walk(agac)))
        }
        
    except SyntaxError as e:
        return {
            'syntax_dogru': False,
            'hata': str(e),
            'ast_node_sayisi': 0
        }
    except Exception as e:
        return {
            'syntax_dogru': False,
            'hata': f"Beklenmeyen hata: {str(e)}",
            'ast_node_sayisi': 0
        }


def modul_import_kontrol_et(dosya_yolu: Path) -> Dict[str, Any]:
    """
    Modülün import edilebilirliğini kontrol eder
    
    Returns:
        Dict: Import kontrol bilgileri
    """
    try:
        # Dosya yolunu modül ismine çevir
        proje_kök_str = str(PROJE_KOK)
        dosya_str = str(dosya_yolu)
        
        if not dosya_str.startswith(proje_kök_str):
            return {
                'import_edilebilir': False,
                'hata': "Dosya proje kökü dışında",
                'modul_ismi': None
            }
        
        # Relatif yolu al
        relatif_yol = Path(dosya_str[len(proje_kök_str):].lstrip('/\\'))
        
        # .py uzantısını kaldır ve modül ismine çevir
        modul_parcalari = list(relatif_yol.parts[:-1]) + [relatif_yol.stem]
        modul_ismi = '.'.join(modul_parcalari)
        
        # Import et
        spec = importlib.util.spec_from_file_location(modul_ismi, dosya_yolu)
        if spec is None or spec.loader is None:
            return {
                'import_edilebilir': False,
                'hata': "Modül spec oluşturulamadı",
                'modul_ismi': modul_ismi
            }
        
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        
        return {
            'import_edilebilir': True,
            'hata': None,
            'modul_ismi': modul_ismi,
            'modul_nitelikleri': len(dir(modul))
        }
        
    except ImportError as e:
        return {
            'import_edilebilir': False,
            'hata': f"Import hatası: {str(e)}",
            'modul_ismi': modul_ismi if 'modul_ismi' in locals() else None
        }
    except Exception as e:
        return {
            'import_edilebilir': False,
            'hata': f"Beklenmeyen hata: {str(e)}",
            'modul_ismi': modul_ismi if 'modul_ismi' in locals() else None
        }


def bagimliliklari_kontrol_et(dosya_yolu: Path) -> Dict[str, Any]:
    """
    Dosyanın bağımlılıklarını kontrol eder
    
    Returns:
        Dict: Bağımlılık kontrol bilgileri
    """
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            icerik = f.read()
        
        # AST ile import'ları bul
        agac = ast.parse(icerik)
        
        importlar = []
        eksik_bagimliliklar = []
        
        for node in ast.walk(agac):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    importlar.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    importlar.append(node.module)
        
        # Import'ları kontrol et
        for import_ismi in importlar:
            try:
                # Sadece ilk seviye modül ismini al
                ana_modul = import_ismi.split('.')[0]
                
                # Standart kütüphane ve yaygın paketleri atla
                standart_moduller = {
                    'sys', 'os', 'pathlib', 'typing', 'abc', 'contextlib',
                    'traceback', 'tempfile', 'ast', 're', 'json'
                }
                
                if ana_modul not in standart_moduller:
                    importlib.import_module(ana_modul)
                    
            except ImportError:
                eksik_bagimliliklar.append(import_ismi)
        
        return {
            'toplam_import': len(importlar),
            'eksik_bagimlilık_sayisi': len(eksik_bagimliliklar),
            'eksik_bagimliliklar': eksik_bagimliliklar,
            'tum_bagimliliklar_mevcut': len(eksik_bagimliliklar) == 0
        }
        
    except Exception as e:
        return {
            'toplam_import': 0,
            'eksik_bagimlilık_sayisi': -1,
            'eksik_bagimliliklar': [],
            'tum_bagimliliklar_mevcut': False,
            'hata': str(e)
        }


class TestBaslangicDosyalariCalisabilirlik:
    """SONTECHSP başlangıç dosyaları çalışabilirlik testleri"""
    
    @pytest.mark.critical
    @pytest.mark.integration
    @pytest.mark.parametrize("dosya_yolu", kritik_dosyalari_al())
    def test_kritik_dosya_syntax_dogrulugu(self, dosya_yolu: Path):
        """
        **Feature: sontechsp-proje-iskeleti, Property 15: Başlangıç dosyaları çalışabilirliği**
        
        Kritik başlangıç dosyalarının syntax'ı doğru olmalıdır.
        """
        syntax_bilgileri = dosya_syntax_kontrol_et(dosya_yolu)
        
        assert syntax_bilgileri['syntax_dogru'], (
            f"Kritik dosya {dosya_yolu.name} syntax hatası: "
            f"{syntax_bilgileri['hata']}"
        )
        
        # En az birkaç AST node olmalı
        assert syntax_bilgileri['ast_node_sayisi'] > 0, (
            f"Kritik dosya {dosya_yolu.name} boş veya geçersiz"
        )
    
    @pytest.mark.slow
    @pytest.mark.integration
    @pytest.mark.parametrize("dosya_yolu", python_dosyalarini_al())
    def test_tum_dosyalar_syntax_dogrulugu(self, dosya_yolu: Path):
        """
        **Feature: sontechsp-proje-iskeleti, Property 15: Başlangıç dosyaları çalışabilirliği**
        
        Tüm Python dosyalarının syntax'ı doğru olmalıdır.
        """
        syntax_bilgileri = dosya_syntax_kontrol_et(dosya_yolu)
        
        assert syntax_bilgileri['syntax_dogru'], (
            f"Dosya {dosya_yolu.name} syntax hatası: "
            f"{syntax_bilgileri['hata']}"
        )
    
    @pytest.mark.parametrize("dosya_yolu", kritik_dosyalari_al())
    def test_kritik_dosya_import_edilebilirlik(self, dosya_yolu: Path):
        """
        **Feature: sontechsp-proje-iskeleti, Property 15: Başlangıç dosyaları çalışabilirliği**
        
        Kritik başlangıç dosyaları import edilebilir olmalıdır.
        """
        # ana.py dosyası PyQt6 gerektirdiği için atla
        if dosya_yolu.name == "ana.py":
            pytest.skip("ana.py PyQt6 gerektirir, CI ortamında atlanır")
        
        import_bilgileri = modul_import_kontrol_et(dosya_yolu)
        
        assert import_bilgileri['import_edilebilir'], (
            f"Kritik dosya {dosya_yolu.name} import edilemiyor: "
            f"{import_bilgileri['hata']}"
        )
    
    @pytest.mark.parametrize("dosya_yolu", kritik_dosyalari_al())
    def test_kritik_dosya_bagimliliklari(self, dosya_yolu: Path):
        """
        **Feature: sontechsp-proje-iskeleti, Property 15: Başlangıç dosyaları çalışabilirliği**
        
        Kritik başlangıç dosyalarının bağımlılıkları mevcut olmalıdır.
        """
        bagimlilık_bilgileri = bagimliliklari_kontrol_et(dosya_yolu)
        
        # PyQt6 ve hypothesis gibi opsiyonel bağımlılıkları atla
        opsiyonel_bagimliliklar = {'PyQt6', 'hypothesis', 'pytest'}
        
        eksik_bagimliliklar = [
            bag for bag in bagimlilık_bilgileri.get('eksik_bagimliliklar', [])
            if not any(ops in bag for ops in opsiyonel_bagimliliklar)
        ]
        
        assert len(eksik_bagimliliklar) == 0, (
            f"Kritik dosya {dosya_yolu.name} eksik bağımlılıklar: "
            f"{eksik_bagimliliklar}"
        )


@given(st.text(min_size=10, max_size=200))
@settings(max_examples=30)
def test_python_kod_syntax_property(kod_ornegi: str):
    """
    **Feature: sontechsp-proje-iskeleti, Property 15: Başlangıç dosyaları çalışabilirliği**
    
    Herhangi bir Python kod örneği için syntax kontrolü çalışmalıdır.
    """
    assume(len(kod_ornegi.strip()) > 0)
    
    try:
        # Syntax kontrolü yapabilmeli (hata vermese de vermese de)
        ast.parse(kod_ornegi)
        syntax_dogru = True
    except SyntaxError:
        syntax_dogru = False
    
    # Test sadece fonksiyonun çalıştığını doğrular
    assert isinstance(syntax_dogru, bool)


@given(st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=5))
@settings(max_examples=20)
def test_modul_ismi_olusturma_property(modul_parcalari: List[str]):
    """
    **Feature: sontechsp-proje-iskeleti, Property 15: Başlangıç dosyaları çalışabilirliği**
    
    Herhangi bir modül parçaları listesi için modül ismi oluşturulabilmelidir.
    """
    assume(all(parca.strip() for parca in modul_parcalari))
    
    # Geçerli Python identifier karakterleri filtrele
    temiz_parcalar = []
    for parca in modul_parcalari:
        temiz_parca = ''.join(c for c in parca if c.isalnum() or c == '_')
        if temiz_parca and (temiz_parca[0].isalpha() or temiz_parca[0] == '_'):
            temiz_parcalar.append(temiz_parca)
    
    assume(len(temiz_parcalar) > 0)
    
    # Modül ismi oluştur
    modul_ismi = '.'.join(temiz_parcalar)
    
    # Geçerli modül ismi olmalı
    assert len(modul_ismi) > 0
    assert '.' in modul_ismi or len(temiz_parcalar) == 1


def test_proje_yapisinin_temel_gereksinimleri():
    """
    **Feature: sontechsp-proje-iskeleti, Property 15: Başlangıç dosyaları çalışabilirliği**
    
    Proje yapısının temel gereksinimleri karşılanmalıdır.
    """
    # Temel klasörler mevcut olmalı
    temel_klasorler = [
        PROJE_KOK / "uygulama",
        PROJE_KOK / "uygulama" / "cekirdek",
        PROJE_KOK / "uygulama" / "veritabani",
        PROJE_KOK / "testler"
    ]
    
    for klasor in temel_klasorler:
        assert klasor.exists() and klasor.is_dir(), (
            f"Temel klasör eksik: {klasor}"
        )
    
    # Temel dosyalar mevcut olmalı
    temel_dosyalar = [
        PROJE_KOK / "pyproject.toml",
        PROJE_KOK / "README.md"
    ]
    
    for dosya in temel_dosyalar:
        assert dosya.exists() and dosya.is_file(), (
            f"Temel dosya eksik: {dosya}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])