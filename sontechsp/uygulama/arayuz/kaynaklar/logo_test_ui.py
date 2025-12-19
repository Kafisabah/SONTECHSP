# Version: 0.1.0
# Last Update: 2024-12-19
# Module: arayuz.kaynaklar.logo_test_ui
# Description: Logo UI test scripti
# Changelog:
# - İlk sürüm: Ana pencerede logo görüntüleme testi

"""
Logo UI Test Scripti

Ana pencerede logo görüntülemeyi test eder.
"""

import sys
from pathlib import Path

# Proje kök dizinini sys.path'e ekle
proje_kok = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(proje_kok))

try:
    from PyQt6.QtWidgets import QApplication
    from sontechsp.uygulama.arayuz.ana_pencere import AnaPencere

    def main():
        """Ana test fonksiyonu"""
        app = QApplication(sys.argv)

        print("🚀 Logo UI Testi Başlatılıyor...")

        # Ana pencereyi oluştur
        pencere = AnaPencere()
        pencere.show()

        print("✅ Ana pencere logo ile açıldı!")
        print("💡 Pencereyi kapatmak için X butonuna tıklayın.")

        # Uygulamayı çalıştır
        sys.exit(app.exec())

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"❌ İmport hatası: {e}")
    print("💡 PyQt6 ve gerekli modüllerin yüklü olduğundan emin olun.")
except Exception as e:
    print(f"❌ Beklenmeyen hata: {e}")
