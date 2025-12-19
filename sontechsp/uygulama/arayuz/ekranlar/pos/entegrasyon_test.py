# Version: 0.1.0
# Last Update: 2024-12-19
# Module: entegrasyon_test
# Description: POS yeni ekran AnaPencere entegrasyon testi
# Changelog:
# - İlk oluşturma

"""
POS Entegrasyon Test - AnaPencere entegrasyonu test fonksiyonları
"""

import sys
import os

# Proje kök dizinini path'e ekle
proje_kok = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))
sys.path.insert(0, proje_kok)

from PyQt6.QtWidgets import QApplication
from sontechsp.uygulama.arayuz.ana_pencere import AnaPencere


def entegrasyon_testi():
    """POS entegrasyon testini çalıştırır"""
    print("POS AnaPencere Entegrasyon Testi")
    print("=" * 40)

    try:
        # QApplication oluştur
        app = QApplication([])

        # Ana pencere oluştur
        ana_pencere = AnaPencere()
        print("✓ Ana pencere oluşturuldu")

        # POS menüsünü seç
        pos_secildi = ana_pencere.pos_menusunu_sec()
        print(f"✓ POS menü seçimi: {'Başarılı' if pos_secildi else 'Başarısız'}")

        # Aktif modül kontrolü
        aktif_modul = ana_pencere.aktif_modul_kodunu_al()
        print(f"✓ Aktif modül: {aktif_modul}")

        # POS yeni ekran yükleme testi
        yeni_ekran_yuklendi = ana_pencere.pos_yeni_ekran_yukle()
        print(f"✓ POS yeni ekran yükleme: {'Başarılı' if yeni_ekran_yuklendi else 'Başarısız'}")

        # Modül ekranları sayısı
        ekran_sayisi = len(ana_pencere._modul_ekranlari)
        print(f"✓ Yüklü modül ekran sayısı: {ekran_sayisi}")

        # Sepet verilerini kaydetme testi
        ana_pencere._pos_sepet_verilerini_kaydet()
        print("✓ Sepet verilerini kaydetme testi tamamlandı")

        print("\nEntegrasyon testi başarıyla tamamlandı!")
        return True

    except Exception as e:
        print(f"✗ Entegrasyon testi hatası: {e}")
        import traceback

        traceback.print_exc()
        return False


def gui_entegrasyon_testi():
    """GUI ile entegrasyon testini çalıştırır"""
    app = QApplication(sys.argv)

    # Konsol testini çalıştır
    test_basarili = entegrasyon_testi()

    if test_basarili:
        print("\nGUI testi başlatılıyor...")

        # Ana pencereyi göster
        ana_pencere = AnaPencere()
        ana_pencere.show()

        # POS menüsünü otomatik seç
        ana_pencere.pos_menusunu_sec()

        print("Ana pencere açıldı. POS menüsü seçili durumda.")
        print("Pencereyi kapatarak testi sonlandırabilirsiniz.")

        return app.exec()
    else:
        print("Konsol testi başarısız, GUI testi atlanıyor.")
        return 1


if __name__ == "__main__":
    # Sadece konsol testini çalıştır
    entegrasyon_testi()
