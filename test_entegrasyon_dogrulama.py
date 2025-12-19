#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Version: 0.1.0
# Last Update: 2024-12-19
# Module: test_entegrasyon_dogrulama
# Description: POS AnaPencere entegrasyon doğrulama testi
# Changelog:
# - İlk versiyon: POS-AnaPencere entegrasyon kontrolü

"""
POS AnaPencere Entegrasyon Doğrulama Testi

Bu test, POS modülünün AnaPencere ile doğru şekilde entegre olduğunu
ve menü geçişlerinin çalıştığını doğrular.
"""

import os
import sys
from typing import Optional

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "sontechsp"))

from PyQt6.QtWidgets import QApplication

try:
    from sontechsp.uygulama.arayuz.ana_pencere import AnaPencere
    from sontechsp.uygulama.moduller.pos.ui.pos_ana_ekran import POSAnaEkran
except ImportError as e:
    print(f"❌ Import hatası: {e}")
    sys.exit(1)


def entegrasyon_dogrulama() -> bool:
    """POS-AnaPencere entegrasyonunu doğrular."""

    # QApplication oluştur veya mevcut olanı kullan
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    print("=" * 60)
    print("POS ANAPENCERE ENTEGRASYON DOĞRULAMA")
    print("=" * 60)

    try:
        # AnaPencere oluştur
        ana_pencere = AnaPencere()
        print("✅ AnaPencere başarıyla oluşturuldu")

        # POS menüsünü seç
        pos_secildi = ana_pencere.pos_menusunu_sec()
        print(f"✅ POS menü seçimi: {pos_secildi}")

        # Aktif widget'ı kontrol et
        aktif_widget = ana_pencere.icerik_alani.currentWidget()
        widget_tipi = type(aktif_widget).__name__

        print(f"📋 Aktif widget tipi: {widget_tipi}")

        # Entegrasyon kontrolü
        if isinstance(aktif_widget, POSAnaEkran):
            print("✅ POS ANA EKRANI BAŞARIYLA YÜKLENDİ!")
            print("✅ ENTEGRASYON TAMAMLANDI!")

            # Detaylı kontroller
            print("\n📊 Entegrasyon Detayları:")
            bilesenler = getattr(aktif_widget, "_bilesenler", {})
            print(f"   - POS ekranı bileşen sayısı: {len(bilesenler)}")

            pos_sinyalleri = getattr(aktif_widget, "pos_sinyalleri", None)
            print(f"   - Sinyal sistemi: {'✅ Aktif' if pos_sinyalleri else '❌ Pasif'}")

            klavye_yoneticisi = getattr(aktif_widget, "klavye_yoneticisi", None)
            print(f"   - Klavye yöneticisi: {'✅ Aktif' if klavye_yoneticisi else '❌ Pasif'}")

            return True
        else:
            print("❌ POS ANA EKRANI YÜKLENEMEDİ!")
            print(f"❌ Placeholder gösteriliyor: {widget_tipi}")
            return False

    except Exception as e:
        print(f"❌ Entegrasyon hatası: {e}")
        return False

    finally:
        print("=" * 60)


if __name__ == "__main__":
    basarili = entegrasyon_dogrulama()
    sys.exit(0 if basarili else 1)
