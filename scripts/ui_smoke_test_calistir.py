#!/usr/bin/env python3
# Version: 1.0.0
# Last Update: 2024-12-18
# Module: scripts.ui_smoke_test_calistir
# Description: UI Smoke Test çalıştırma script'i - cross-platform
# Changelog:
# - İlk versiyon: smoke test çalıştırma ve rapor üretme

import os
import sys
import subprocess
import platform
import argparse
from pathlib import Path


def check_virtual_environment():
    """Sanal ortam varlığını kontrol et"""
    if platform.system() == "Windows":
        venv_python = Path("venv/Scripts/python.exe")
        activate_script = Path("venv/Scripts/activate.bat")
    else:
        venv_python = Path("venv/bin/python")
        activate_script = Path("venv/bin/activate")

    if not venv_python.exists():
        print("✗ Sanal ortam bulunamadı!")
        print("Önce kurulum script'ini çalıştırın:")
        print("  Windows: scripts\\ui-smoke-test-kurulum.bat")
        print("  Linux/Mac: python scripts/ui_smoke_test_kurulum.py")
        return False, None

    return True, str(venv_python)


def run_smoke_test(python_exe, args):
    """Smoke test çalıştır"""
    # Logs klasörünü oluştur
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Smoke test komutunu oluştur
    cmd_parts = [python_exe, "-m", "uygulama.arayuz.smoke_test_calistir"]

    # Argümanları ekle
    if args.quiet:
        cmd_parts.append("--quiet")
    if args.csv:
        cmd_parts.append("--csv")
    if args.csv_file:
        cmd_parts.extend(["--csv-file", args.csv_file])
    if args.screens:
        cmd_parts.extend(["--screens"] + args.screens)
    if args.help:
        cmd_parts.append("--help")

    # Komutu çalıştır
    if not args.quiet:
        print("Smoke test başlatılıyor...")
        print(f"Komut: {' '.join(cmd_parts)}")
        print()

    try:
        result = subprocess.run(cmd_parts, check=False)
        return result.returncode
    except Exception as e:
        print(f"✗ Smoke test çalıştırılamadı: {e}")
        return 1


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(
        description="SONTECHSP UI Smoke Test Çalıştırıcısı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python scripts/ui_smoke_test_calistir.py
  python scripts/ui_smoke_test_calistir.py --quiet
  python scripts/ui_smoke_test_calistir.py --csv
  python scripts/ui_smoke_test_calistir.py --csv-file rapor.csv
  python scripts/ui_smoke_test_calistir.py --screens pos_satis urunler_stok
        """,
    )

    parser.add_argument("--quiet", "-q", action="store_true", help="Sessiz mod - minimal çıktı")
    parser.add_argument("--csv", action="store_true", help="CSV formatında rapor üret")
    parser.add_argument("--csv-file", type=str, help="CSV raporunu dosyaya kaydet")
    parser.add_argument("--screens", "-s", nargs="*", help="Test edilecek ekranlar (boş ise tümü)")
    parser.add_argument("--help-smoke", dest="help", action="store_true", help="Smoke test yardımını göster")

    args = parser.parse_args()

    print("=" * 50)
    print("SONTECHSP UI Smoke Test Çalıştırıcısı")
    print("=" * 50)

    # Sanal ortam kontrolü
    venv_ok, python_exe = check_virtual_environment()
    if not venv_ok:
        return 1

    if not args.quiet:
        print("✓ Sanal ortam bulundu")

    # Smoke test çalıştır
    result = run_smoke_test(python_exe, args)

    # Sonuç raporu
    print()
    if result == 0:
        print("=" * 50)
        print("✓ SMOKE TEST BAŞARILI!")
        print("=" * 50)

        if args.csv_file:
            print(f"✓ CSV raporu oluşturuldu: {args.csv_file}")

        if not args.quiet:
            print()
            print("Log dosyası: logs/ui_smoke_test.log")
            print()
            print("Ek komutlar:")
            print("  CSV raporu: python scripts/ui_smoke_test_calistir.py --csv")
            print("  Belirli ekranlar: python scripts/ui_smoke_test_calistir.py --screens pos_satis")
            print("  Yardım: python scripts/ui_smoke_test_calistir.py --help-smoke")
    else:
        print("=" * 50)
        print("✗ SMOKE TEST BAŞARISIZ!")
        print("=" * 50)
        print(f"Hata kodu: {result}")
        print("Log dosyasını kontrol edin: logs/ui_smoke_test.log")

    return result


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest kullanıcı tarafından iptal edildi.")
        sys.exit(130)
    except Exception as e:
        print(f"\nBeklenmeyen hata: {e}")
        sys.exit(1)
