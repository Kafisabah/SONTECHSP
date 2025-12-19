# Version: 0.1.0
# Last Update: 2024-12-19
# Module: test_hizli_kontrol
# Description: Hızlı kontrol test dosyası
# Changelog:
# - İlk oluşturma

"""
Hızlı kontrol test modülü.
Temel sistem kontrollerini gerçekleştirir.
"""

import sys
from typing import Optional


def hizli_kontrol() -> bool:
    """
    Temel sistem kontrollerini yapar.

    Returns:
        bool: Kontroller başarılıysa True
    """
    print("Hızlı kontrol başlatılıyor...")

    # Python versiyonu kontrolü
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 8:
        print(f"Uyarı: Python {python_version.major}.{python_version.minor}")
        return False

    print("✓ Python versiyonu uygun")
    print("✓ Hızlı kontrol tamamlandı")
    return True


if __name__ == "__main__":
    sonuc = hizli_kontrol()
    sys.exit(0 if sonuc else 1)
