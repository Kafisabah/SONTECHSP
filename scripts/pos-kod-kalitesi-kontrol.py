#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Version: 0.1.0
# Last Update: 2024-12-19
# Module: pos_kod_kalitesi_kontrol
# Description: POS kod kalitesi kontrol script'i
# Changelog:
# - İlk oluşturma - POS kod kalitesi kontrol CLI

"""
POS Kod Kalitesi Kontrol Script'i

POS modülü dosyalarının kod kalitesi standartlarına uygunluğunu kontrol eder.
Komut satırından çalıştırılabilir ve otomatik raporlama yapar.
"""

import sys
import os
import argparse
from pathlib import Path

# Proje kök dizinini sys.path'e ekle
proje_kok = Path(__file__).parent.parent
sys.path.insert(0, str(proje_kok))

from sontechsp.uygulama.kod_kalitesi.pos_kod_kalitesi import POSKodKalitesiKontrolcu


def main():
    """Ana çalıştırma fonksiyonu"""
    parser = argparse.ArgumentParser(
        description="POS Kod Kalitesi Kontrol Aracı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python scripts/pos-kod-kalitesi-kontrol.py                    # Standart analiz
  python scripts/pos-kod-kalitesi-kontrol.py --sadece-rapor     # Sadece rapor göster
  python scripts/pos-kod-kalitesi-kontrol.py --json-dosya rapor.json  # Özel JSON dosyası
        """,
    )

    parser.add_argument(
        "--sadece-rapor", action="store_true", help="Sadece konsol raporu göster, JSON dosyası oluşturma"
    )
    parser.add_argument(
        "--json-dosya",
        type=str,
        default="pos_kod_kalitesi_raporu.json",
        help="JSON rapor dosyası adı (varsayılan: pos_kod_kalitesi_raporu.json)",
    )
    parser.add_argument("--sessiz", action="store_true", help="Sadece hata durumlarında çıktı ver")

    args = parser.parse_args()

    try:
        # Kod kalitesi kontrolcüsünü oluştur
        kontrolcu = POSKodKalitesiKontrolcu()

        if not args.sessiz:
            print("🔍 POS kod kalitesi analizi başlatılıyor...")

        # Analiz yap
        rapor = kontrolcu.analiz_yap()

        # Konsol raporu göster
        if not args.sessiz:
            kontrolcu.konsol_raporu_yazdir(rapor)

        # JSON raporu oluştur (eğer isteniyorsa)
        if not args.sadece_rapor:
            kontrolcu.rapor_olustur(rapor, args.json_dosya)
            if not args.sessiz:
                print(f"📄 JSON raporu kaydedildi: {args.json_dosya}")

        # Çıkış kodu belirle
        if rapor.toplam_sorun > 0:
            if not args.sessiz:
                print(f"\n⚠️  {rapor.toplam_sorun} kod kalitesi sorunu bulundu!")
            return 1
        else:
            if not args.sessiz:
                print("\n✅ Tüm dosyalar kod kalitesi standartlarına uygun!")
            return 0

    except Exception as e:
        print(f"❌ Hata: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
