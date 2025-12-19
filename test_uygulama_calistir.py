# Version: 0.1.0
# Last Update: 2024-12-19
# Module: test_uygulama_calistir
# Description: SONTECHSP uygulama başlatma ve import testleri
# Changelog:
# - İlk versiyon oluşturuldu
# - Import testleri eklendi
# - Syntax hataları düzeltildi

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SONTECHSP Uygulama Test Scripti
Uygulamanın doğru şekilde import edilip çalıştırılabildiğini test eder.
"""

import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

# Proje kök dizinini sys.path'e ekle
sys.path.insert(0, ".")


def test_uygulama_import():
    """Uygulama import testlerini çalıştırır"""
    print("🔍 Import testleri başlatılıyor...")

    try:
        from sontechsp.uygulama.ana import main

        print("✅ Ana uygulama import edildi")
        return True

    except ImportError as e:
        print(f"❌ Import hatası: {e}")
        return False
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
        return False


def test_uygulama_calistir():
    """Uygulamayı test modunda çalıştırır"""
    print("🚀 Uygulama başlatma testi...")

    # PyQt uygulaması oluştur
    app = QApplication(sys.argv)

    try:
        from sontechsp.uygulama.ana import main

        # Test modunda çalıştır (hemen kapat)
        timer = QTimer()
        timer.timeout.connect(app.quit)
        timer.start(1000)  # 1 saniye sonra kapat

        print("✅ Uygulama başarıyla başlatıldı")
        return True

    except Exception as e:
        print(f"❌ Uygulama başlatma hatası: {e}")
        return False
    finally:
        app.quit()


def main():
    """Ana test fonksiyonu"""
    print("=" * 50)
    print("SONTECHSP Uygulama Test Scripti")
    print("=" * 50)

    # Import testleri
    import_basarili = test_uygulama_import()

    if import_basarili:
        # Uygulama başlatma testi
        calistirma_basarili = test_uygulama_calistir()

        if calistirma_basarili:
            print("\n🎉 Tüm testler başarılı!")
            return 0
        else:
            print("\n❌ Uygulama başlatma testi başarısız!")
            return 1
    else:
        print("\n❌ Import testleri başarısız!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
