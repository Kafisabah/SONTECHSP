# Version: 0.1.0
# Last Update: 2024-12-19
# Module: arayuz.kaynaklar.logo_test
# Description: Logo ölçeklendirme test scripti
# Changelog:
# - İlk sürüm: Logo ölçeklendirme testi

"""
Logo Ölçeklendirme Test Scripti

Bu script, logo ölçeklendirme fonksiyonunu test eder.
"""

import sys
import os
from pathlib import Path

# Proje kök dizinini sys.path'e ekle
proje_kok = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(proje_kok))

try:
    from PyQt6.QtWidgets import QApplication
    from sontechsp.uygulama.arayuz.kaynaklar import logo_olceklendir, kaynak_yoneticisi

    def main():
        """Ana test fonksiyonu"""
        # QApplication oluştur
        app = QApplication(sys.argv)

        print("🚀 Logo Ölçeklendirme Testi Başlatılıyor...")
        print("=" * 50)

        # Ana logo varlığını kontrol et
        ana_logo_yolu = kaynak_yoneticisi.logo_yolu("logo.png")

        if not ana_logo_yolu.exists():
            print("❌ Ana logo dosyası bulunamadı!")
            print(f"📝 Beklenen konum: {ana_logo_yolu}")
            print("💡 Lütfen logo.png dosyasını resimler/ klasörüne yerleştirin.")
            return

        print(f"✅ Ana logo bulundu: {ana_logo_yolu}")

        # Logo ölçeklendirme işlemini başlat
        print("\n📏 Logo ölçeklendirme işlemi başlatılıyor...")

        basarili = logo_olceklendir()

        if basarili:
            print("\n🎉 Logo ölçeklendirme işlemi başarıyla tamamlandı!")

            # Oluşturulan dosyaları listele
            print("\n📁 Oluşturulan dosyalar:")

            # Resimler klasörü
            resim_dizini = kaynak_yoneticisi._resim_dizini
            for dosya in sorted(resim_dizini.glob("logo*.png")):
                if dosya.name != "logo.png":  # Ana logoyu hariç tut
                    print(f"  📷 {dosya.name}")

            # İkonlar klasörü
            ikon_dizini = kaynak_yoneticisi._ikon_dizini
            if ikon_dizini.exists():
                for dosya in sorted(ikon_dizini.glob("logo*.png")):
                    print(f"  🎯 {dosya.name}")

            print("\n💡 Artık bu logoları uygulamanızda kullanabilirsiniz!")

        else:
            print("\n❌ Logo ölçeklendirme işlemi başarısız!")

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"❌ İmport hatası: {e}")
    print("💡 PyQt6 yüklü olduğundan emin olun.")
except Exception as e:
    print(f"❌ Beklenmeyen hata: {e}")
