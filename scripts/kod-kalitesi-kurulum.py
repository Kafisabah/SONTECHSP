#!/usr/bin/env python3
# Version: 0.1.0
# Last Update: 2024-12-17
# Module: scripts.kod_kalitesi_kurulum
# Description: Kod kalitesi sistemi kurulum scripti
# Changelog:
# - İlk sürüm: Otomatik kurulum scripti

"""
SONTECHSP Kod Kalitesi Sistemi Kurulum Aracı

Bu script, kod kalitesi sisteminin proje içine kurulumunu ve entegrasyonunu sağlar.

Kullanım:
    python scripts/kod-kalitesi-kurulum.py [proje_yolu] [seçenekler]

Örnekler:
    # Mevcut dizine kurulum
    python scripts/kod-kalitesi-kurulum.py
    
    # Belirli dizine kurulum
    python scripts/kod-kalitesi-kurulum.py /path/to/project
    
    # Sadece durumu kontrol et
    python scripts/kod-kalitesi-kurulum.py --durum
"""

import sys
import os
from pathlib import Path

# Proje kök dizinini Python path'ine ekle
proje_kok = Path(__file__).parent.parent
sys.path.insert(0, str(proje_kok))

try:
    from sontechsp.uygulama.kod_kalitesi.kurulum_yoneticisi import ana_kurulum
except ImportError as e:
    print(f"❌ Modül import hatası: {e}")
    print("🔧 Lütfen proje kök dizininden çalıştırdığınızdan emin olun.")
    sys.exit(1)

if __name__ == "__main__":
    sys.exit(ana_kurulum())