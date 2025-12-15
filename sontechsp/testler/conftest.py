# Version: 0.1.0
# Last Update: 2024-12-15
# Module: conftest
# Description: SONTECHSP pytest yapılandırması ve fixture'ları
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Test Yapılandırması

Pytest ve Hypothesis yapılandırması.
Ortak test fixture'ları ve yardımcı fonksiyonlar.

Sorumluluklar:
- Pytest yapılandırması
- Test fixture'ları
- Test veri üreticileri
- Property-based test ayarları
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, Generator

import pytest
from hypothesis import settings, Verbosity

# Test için proje kök dizinini sys.path'e ekle
PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))

# Hypothesis ayarları
settings.register_profile("default", max_examples=100, verbosity=Verbosity.normal)
settings.register_profile("ci", max_examples=1000, verbosity=Verbosity.verbose)
settings.register_profile("dev", max_examples=10, verbosity=Verbosity.quiet)

# Ortam değişkenine göre profil seç
profile = os.getenv("HYPOTHESIS_PROFILE", "default")
settings.load_profile(profile)


@pytest.fixture(scope="session")
def proje_koku() -> Path:
    """
    Proje kök dizinini döndürür
    
    Returns:
        Path: Proje kök dizini
    """
    return PROJE_KOK


@pytest.fixture(scope="session")
def test_veritabani_url() -> str:
    """
    Test veritabanı URL'ini döndürür
    
    Returns:
        str: Test veritabanı bağlantı URL'i
    """
    return "sqlite:///:memory:"


@pytest.fixture
def gecici_dizin() -> Generator[Path, None, None]:
    """
    Geçici test dizini oluşturur
    
    Yields:
        Path: Geçici dizin yolu
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def ornek_dosya_yapisi(gecici_dizin: Path) -> Dict[str, Path]:
    """
    Test için örnek dosya yapısı oluşturur
    
    Args:
        gecici_dizin: Geçici dizin
        
    Returns:
        Dict[str, Path]: Dosya yolları sözlüğü
    """
    # Klasör yapısı oluştur
    uygulama_dir = gecici_dizin / "uygulama"
    cekirdek_dir = uygulama_dir / "cekirdek"
    veritabani_dir = uygulama_dir / "veritabani"
    
    uygulama_dir.mkdir()
    cekirdek_dir.mkdir()
    veritabani_dir.mkdir()
    
    # Örnek dosyalar oluştur
    dosyalar = {
        "ana_py": uygulama_dir / "ana.py",
        "ayarlar_py": cekirdek_dir / "ayarlar.py",
        "baglanti_py": veritabani_dir / "baglanti.py"
    }
    
    # Dosya içerikleri
    dosya_icerikleri = {
        "ana_py": '''# Version: 0.1.0
# Last Update: 2024-12-15
# Module: ana
# Description: Test ana dosyası
# Changelog:
# - Test oluşturma

def main():
    """Ana fonksiyon"""
    print("Test")
''',
        "ayarlar_py": '''# Version: 0.1.0
# Last Update: 2024-12-15
# Module: ayarlar
# Description: Test ayarlar dosyası
# Changelog:
# - Test oluşturma

class Ayarlar:
    """Test ayarlar sınıfı"""
    pass
''',
        "baglanti_py": '''# Version: 0.1.0
# Last Update: 2024-12-15
# Module: baglanti
# Description: Test bağlantı dosyası
# Changelog:
# - Test oluşturma

def baglan():
    """Test bağlantı fonksiyonu"""
    return True
'''
    }
    
    # Dosyaları oluştur
    for dosya_key, dosya_yolu in dosyalar.items():
        dosya_yolu.write_text(dosya_icerikleri[dosya_key], encoding='utf-8')
    
    return dosyalar


@pytest.fixture
def ornek_python_kodu() -> str:
    """
    Test için örnek Python kodu döndürür
    
    Returns:
        str: Örnek Python kodu
    """
    return '''# Version: 0.1.0
# Last Update: 2024-12-15
# Module: ornek
# Description: Örnek test modülü
# Changelog:
# - İlk oluşturma

"""
Örnek test modülü
"""

def kisa_fonksiyon():
    """Kısa test fonksiyonu"""
    return "test"

def orta_fonksiyon(parametre1, parametre2):
    """
    Orta uzunlukta test fonksiyonu
    
    Args:
        parametre1: İlk parametre
        parametre2: İkinci parametre
        
    Returns:
        str: Test sonucu
    """
    if parametre1 and parametre2:
        return f"{parametre1}_{parametre2}"
    return "bos"

class OrnekSinif:
    """Örnek test sınıfı"""
    
    def __init__(self, isim: str):
        """
        Sınıf başlatıcı
        
        Args:
            isim: Sınıf ismi
        """
        self.isim = isim
    
    def metod(self):
        """Test metodu"""
        return self.isim
'''


@pytest.fixture
def test_ayarlari() -> Dict[str, Any]:
    """
    Test ayarları döndürür
    
    Returns:
        Dict[str, Any]: Test ayarları
    """
    return {
        "max_satir_sayisi": 120,
        "max_fonksiyon_satiri": 25,
        "test_max_satir_sayisi": 200,
        "test_max_fonksiyon_satiri": 50,
        "zorunlu_baslık_alanlari": [
            "Version:",
            "Last Update:",
            "Module:",
            "Description:",
            "Changelog:"
        ]
    }


def pytest_configure(config):
    """Pytest yapılandırması"""
    # Özel işaretleyiciler ekle
    config.addinivalue_line(
        "markers", "property: Property-based test işaretleyicisi"
    )
    config.addinivalue_line(
        "markers", "unit: Unit test işaretleyicisi"
    )
    config.addinivalue_line(
        "markers", "integration: Entegrasyon test işaretleyicisi"
    )
    config.addinivalue_line(
        "markers", "slow: Yavaş test işaretleyicisi"
    )


def pytest_collection_modifyitems(config, items):
    """Test toplama sonrası modifikasyon"""
    # Property testleri için özel işaretleme
    for item in items:
        if "property" in item.name.lower() or "hypothesis" in str(item.function):
            item.add_marker(pytest.mark.property)
        
        # Yavaş testler için işaretleme
        if "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)