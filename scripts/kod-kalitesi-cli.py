#!/usr/bin/env python3
# Version: 0.1.0
# Last Update: 2024-12-17
# Module: scripts.kod_kalitesi_cli
# Description: Kod kalitesi CLI entry point scripti
# Changelog:
# - İlk sürüm: CLI entry point

"""
SONTECHSP Kod Kalitesi ve Standardizasyon CLI Aracı

Bu script, SONTECHSP kod tabanının kalite standartlarına uygun hale getirilmesi
için komut satırı arayüzü sağlar.

Kullanım:
    python scripts/kod-kalitesi-cli.py <proje_yolu> [seçenekler]

Örnekler:
    # İnteraktif mod
    python scripts/kod-kalitesi-cli.py .
    
    # Sadece analiz
    python scripts/kod-kalitesi-cli.py . --analiz
    
    # Otomatik mod (onaysız)
    python scripts/kod-kalitesi-cli.py . --otomatik
"""

import sys
import os
from pathlib import Path

# Proje kök dizinini Python path'ine ekle
proje_kok = Path(__file__).parent.parent
sys.path.insert(0, str(proje_kok))

try:
    from sontechsp.uygulama.kod_kalitesi.cli_arayuzu import ana_cli
except ImportError as e:
    print(f"❌ Modül import hatası: {e}")
    print("🔧 Lütfen proje kök dizininden çalıştırdığınızdan emin olun.")
    sys.exit(1)

if __name__ == "__main__":
    sys.exit(ana_cli())