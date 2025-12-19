# Version: 0.1.0
# Last Update: 2024-12-18
# Module: test_runner_temp
# Description: POS ekran bileşenleri testi için geçici test runner
# Changelog:
# - İlk oluşturma - POS ekran bileşenleri property testini çalıştırmak için

"""
Geçici Test Runner - POS Ekran Bileşenleri

Bu dosya POS ekran bileşenleri property testini manuel olarak çalıştırmak için oluşturulmuştur.
"""

import sys
import traceback

from PyQt6.QtWidgets import QApplication

# Proje kök dizinini path'e ekle
sys.path.append(".")

from tests.pos.test_pos_ekran_bilesenleri_property import TestPOSEkranBilesenleriProperty


def main():
    """Ana test çalıştırma fonksiyonu"""
    # Qt uygulaması oluştur
    app = QApplication(sys.argv)

    # Test sınıfını oluştur
    test_instance = TestPOSEkranBilesenleriProperty()

    try:
        # Test setup'ını çalıştır
        setup_generator = test_instance.setup_qt_app()
        next(setup_generator)  # Setup'ı başlat

        # Test metodunu çalıştır
        test_instance.test_pos_ekrani_acilisinda_temel_bilesenler_mevcut(1)
        print("✓ Test başarılı!")

        # Cleanup
        try:
            next(setup_generator)
        except StopIteration:
            pass  # Generator tamamlandı

    except Exception as e:
        print(f"✗ Test hatası: {e}")
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
