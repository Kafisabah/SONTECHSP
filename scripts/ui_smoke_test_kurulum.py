#!/usr/bin/env python3
# Version: 1.0.0
# Last Update: 2024-12-18
# Module: scripts.ui_smoke_test_kurulum
# Description: UI Smoke Test kurulum script'i - cross-platform
# Changelog:
# - İlk versiyon: sanal ortam kurulumu ve bağımlılık yükleme

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(command, description, check=True):
    """Komut çalıştır ve sonucu kontrol et"""
    print(f"  → {description}...")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ {description} başarılı")
            return True
        else:
            print(f"  ✗ {description} başarısız: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"  ✗ {description} başarısız: {e}")
        return False
    except Exception as e:
        print(f"  ✗ {description} hatası: {e}")
        return False


def check_python():
    """Python varlığını ve versiyonunu kontrol et"""
    print("Python kontrolü yapılıyor...")
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        print(f"  ✓ {version} bulundu")

        # Python 3.8+ kontrolü
        version_info = sys.version_info
        if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 8):
            print(f"  ✗ Python 3.8+ gerekli, mevcut: {version_info.major}.{version_info.minor}")
            return False

        return True
    except Exception as e:
        print(f"  ✗ Python bulunamadı: {e}")
        return False


def create_virtual_environment():
    """Sanal ortam oluştur"""
    print("\nSanal ortam oluşturuluyor...")

    venv_path = Path("venv")

    # Mevcut sanal ortamı sil
    if venv_path.exists():
        print("  ⚠ Mevcut sanal ortam bulundu, siliniyor...")
        import shutil

        shutil.rmtree(venv_path)

    # Yeni sanal ortam oluştur
    if not run_command(f"{sys.executable} -m venv venv", "Sanal ortam oluşturma"):
        return False

    return True


def get_activation_command():
    """Platform'a göre aktivasyon komutunu döndür"""
    if platform.system() == "Windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"


def install_dependencies():
    """Bağımlılıkları yükle"""
    print("\nBağımlılıklar yükleniyor...")

    # Platform'a göre Python executable'ı belirle
    if platform.system() == "Windows":
        python_exe = "venv\\Scripts\\python.exe"
        pip_exe = "venv\\Scripts\\pip.exe"
    else:
        python_exe = "venv/bin/python"
        pip_exe = "venv/bin/pip"

    # Pip'i güncelle
    run_command(f"{python_exe} -m pip install --upgrade pip", "pip güncelleme", check=False)

    # Temel bağımlılıklar
    dependencies = ["PyQt6", "SQLAlchemy", "psycopg2-binary"]

    for dep in dependencies:
        if not run_command(f"{pip_exe} install {dep}", f"{dep} yükleme"):
            print(f"  ⚠ {dep} yüklenemedi, devam ediliyor...")

    # Test bağımlılıkları (opsiyonel)
    test_dependencies = ["pytest", "hypothesis"]
    print("\n  Test bağımlılıkları yükleniyor...")
    for dep in test_dependencies:
        run_command(f"{pip_exe} install {dep}", f"{dep} yükleme", check=False)

    # requirements.txt varsa yükle
    if Path("requirements.txt").exists():
        print("\n  Proje bağımlılıkları yükleniyor...")
        run_command(f"{pip_exe} install -r requirements.txt", "requirements.txt yükleme", check=False)

    return True


def verify_installation():
    """Kurulum doğrulaması"""
    print("\nKurulum doğrulaması yapılıyor...")

    if platform.system() == "Windows":
        python_exe = "venv\\Scripts\\python.exe"
    else:
        python_exe = "venv/bin/python"

    # PyQt6 kontrolü
    if run_command(f'{python_exe} -c "import PyQt6; print(\\"✓ PyQt6 OK\\")"', "PyQt6 kontrolü", check=False):
        pass
    else:
        print("  ✗ PyQt6 import edilemedi!")
        return False

    # SQLAlchemy kontrolü
    if run_command(
        f'{python_exe} -c "import sqlalchemy; print(\\"✓ SQLAlchemy OK\\")"', "SQLAlchemy kontrolü", check=False
    ):
        pass
    else:
        print("  ✗ SQLAlchemy import edilemedi!")
        return False

    return True


def main():
    """Ana kurulum fonksiyonu"""
    print("=" * 50)
    print("SONTECHSP UI Smoke Test Kurulum")
    print("=" * 50)

    # Python kontrolü
    if not check_python():
        print("\n✗ Python kontrolü başarısız!")
        return 1

    # Sanal ortam oluştur
    if not create_virtual_environment():
        print("\n✗ Sanal ortam oluşturulamadı!")
        return 1

    # Bağımlılıkları yükle
    if not install_dependencies():
        print("\n✗ Bağımlılık yükleme başarısız!")
        return 1

    # Kurulum doğrulaması
    if not verify_installation():
        print("\n✗ Kurulum doğrulaması başarısız!")
        return 1

    # Başarı mesajı
    print("\n" + "=" * 50)
    print("✓ KURULUM TAMAMLANDI!")
    print("=" * 50)

    activation_cmd = get_activation_command()
    print(f"\nKullanım:")
    print(f"  1. Sanal ortamı aktifleştirin: {activation_cmd}")
    print(f"  2. Smoke test çalıştırın: python -m uygulama.arayuz.smoke_test_calistir")
    print(f"\nÖrnekler:")
    print(f"  python -m uygulama.arayuz.smoke_test_calistir --help")
    print(f"  python -m uygulama.arayuz.smoke_test_calistir --csv")
    print(f"  python -m uygulama.arayuz.smoke_test_calistir --csv-file rapor.csv")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nKurulum kullanıcı tarafından iptal edildi.")
        sys.exit(130)
    except Exception as e:
        print(f"\nBeklenmeyen hata: {e}")
        sys.exit(1)
