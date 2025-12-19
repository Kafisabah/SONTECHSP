#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
POS Kod Kalitesi Test Script'i
"""

import sys
import os
from pathlib import Path

# Proje kök dizinini sys.path'e ekle
sys.path.insert(0, str(Path(__file__).parent))


# Basit kod kalitesi kontrol fonksiyonu
def pos_kod_kalitesi_kontrol():
    """POS kod kalitesi kontrolü yapar"""
    print("=" * 70)
    print("🔍 POS KOD KALİTESİ ANALİZ RAPORU")
    print("=" * 70)

    pos_ui_klasoru = "sontechsp/uygulama/moduller/pos/ui"
    max_dosya_boyutu = 120
    max_fonksiyon_boyutu = 25

    if not os.path.exists(pos_ui_klasoru):
        print(f"❌ POS UI klasörü bulunamadı: {pos_ui_klasoru}")
        return

    # POS dosyalarını bul
    pos_dosyalari = []
    for root, dirs, files in os.walk(pos_ui_klasoru):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                pos_dosyalari.append(os.path.join(root, file))

    print(f"📁 Toplam Dosya: {len(pos_dosyalari)}")

    dosya_boyutu_sorunlari = []
    fonksiyon_boyutu_sorunlari = []
    pep8_sorunlari = []

    for dosya_yolu in pos_dosyalari:
        try:
            with open(dosya_yolu, "r", encoding="utf-8") as f:
                satirlar = f.readlines()

            # Dosya boyutu kontrolü
            kod_satirlari = [satir for satir in satirlar if satir.strip() and not satir.strip().startswith("#")]

            if len(kod_satirlari) > max_dosya_boyutu:
                dosya_boyutu_sorunlari.append({"dosya": dosya_yolu, "satir_sayisi": len(kod_satirlari)})

            # PEP8 kontrolü
            for satir_no, satir in enumerate(satirlar, 1):
                # Satır uzunluğu kontrolü
                if len(satir.rstrip()) > 120:
                    pep8_sorunlari.append(
                        {
                            "dosya": dosya_yolu,
                            "satir": satir_no,
                            "sorun": f"Satır uzunluğu {len(satir.rstrip())} karakter",
                        }
                    )

                # Tab karakteri kontrolü
                if "\t" in satir:
                    pep8_sorunlari.append(
                        {"dosya": dosya_yolu, "satir": satir_no, "sorun": "Tab karakteri kullanılmış"}
                    )

                # Satır sonu boşluk kontrolü
                if satir.endswith(" \n") or satir.endswith(" \r\n"):
                    pep8_sorunlari.append(
                        {"dosya": dosya_yolu, "satir": satir_no, "sorun": "Satır sonunda gereksiz boşluk"}
                    )

        except Exception as e:
            print(f"❌ Dosya okuma hatası {dosya_yolu}: {e}")

    # Sonuçları göster
    toplam_sorun = len(dosya_boyutu_sorunlari) + len(fonksiyon_boyutu_sorunlari) + len(pep8_sorunlari)
    sorunlu_dosya = len(set([s["dosya"] for s in dosya_boyutu_sorunlari + pep8_sorunlari]))

    print(f"⚠️  Sorunlu Dosya: {sorunlu_dosya}")
    print(f"🐛 Toplam Sorun: {toplam_sorun}")
    print()

    if dosya_boyutu_sorunlari:
        print(f"📄 DOSYA BOYUTU SORUNLARI ({len(dosya_boyutu_sorunlari)} adet):")
        for sorun in dosya_boyutu_sorunlari[:5]:
            print(f"  • {sorun['dosya']}")
            print(f"    {sorun['satir_sayisi']} satır (limit: {max_dosya_boyutu})")
        if len(dosya_boyutu_sorunlari) > 5:
            print(f"  ... ve {len(dosya_boyutu_sorunlari) - 5} dosya daha")
        print()

    if pep8_sorunlari:
        print(f"📏 PEP8 SORUNLARI ({len(pep8_sorunlari)} adet):")
        for sorun in pep8_sorunlari[:10]:
            print(f"  • {sorun['dosya']} (satır {sorun['satir']})")
            print(f"    {sorun['sorun']}")
        if len(pep8_sorunlari) > 10:
            print(f"  ... ve {len(pep8_sorunlari) - 10} sorun daha")
        print()

    temiz_dosyalar = [
        d for d in pos_dosyalari if d not in [s["dosya"] for s in dosya_boyutu_sorunlari + pep8_sorunlari]
    ]

    if temiz_dosyalar:
        print(f"✅ TEMİZ DOSYALAR ({len(temiz_dosyalar)} adet):")
        for dosya in temiz_dosyalar:
            print(f"  • {dosya}")
        print()

    print("=" * 70)

    # Kalite skoru hesapla
    if len(pos_dosyalari) > 0:
        kalite_skoru = max(0, 100 - (toplam_sorun / len(pos_dosyalari) * 10))
        print(f"📊 Kod Kalitesi Skoru: {kalite_skoru:.1f}/100")

    return toplam_sorun == 0


if __name__ == "__main__":
    basarili = pos_kod_kalitesi_kontrol()
    sys.exit(0 if basarili else 1)
