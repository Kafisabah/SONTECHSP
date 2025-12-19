# Version: 0.1.0
# Last Update: 2024-12-18
# Module: ui_test_scripti
# Description: SONTECHSP UI bileşenlerini test eden script
# Changelog:
# - İlk oluşturma

"""
SONTECHSP UI Test Scripti

Ana pencere ve modül ekranlarının temel işlevselliğini test eder.
PyQt6 uygulamasını programatik olarak test eder.
"""

import sys
import os
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from PyQt6.QtTest import QTest

# PYTHONPATH ayarla
sys.path.insert(0, os.getcwd())

from sontechsp.uygulama.cekirdek.kayit import kayit_al
from sontechsp.uygulama.arayuz.ana_pencere import AnaPencere


class UITestThread(QThread):
    """UI testlerini ayrı thread'de çalıştırır"""

    test_tamamlandi = pyqtSignal(dict)

    def __init__(self, ana_pencere):
        super().__init__()
        self.ana_pencere = ana_pencere
        self.logger = kayit_al("ui_test")
        self.test_sonuclari = {
            "ana_pencere_acildi": False,
            "modul_menusu_yuklendi": False,
            "modul_secimi_calisiyor": False,
            "icerik_alani_degisiyor": False,
            "statusbar_guncelleniyor": False,
            "oturum_bilgisi_gosteriliyor": False,
        }

    def run(self):
        """Test senaryolarını çalıştırır"""
        self.logger.info("UI testleri başlatılıyor...")

        # Test 1: Ana pencere açıldı mı?
        self.test_ana_pencere()
        QTest.qWait(500)

        # Test 2: Modül menüsü yüklendi mi?
        self.test_modul_menusu()
        QTest.qWait(500)

        # Test 3: Modül seçimi çalışıyor mu?
        self.test_modul_secimi()
        QTest.qWait(1000)

        # Test 4: İçerik alanı değişiyor mu?
        self.test_icerik_alani()
        QTest.qWait(500)

        # Test 5: Status bar güncelleniyor mu?
        self.test_statusbar()
        QTest.qWait(500)

        # Test 6: Oturum bilgisi gösteriliyor mu?
        self.test_oturum_bilgisi()
        QTest.qWait(500)

        self.logger.info("UI testleri tamamlandı")
        self.test_tamamlandi.emit(self.test_sonuclari)

    def test_ana_pencere(self):
        """Ana pencere testleri"""
        try:
            # Pencere görünür mü?
            if self.ana_pencere.isVisible():
                self.test_sonuclari["ana_pencere_acildi"] = True
                self.logger.info("✓ Ana pencere başarıyla açıldı")
            else:
                self.logger.error("✗ Ana pencere açılamadı")
        except Exception as e:
            self.logger.error(f"Ana pencere testi hatası: {e}")

    def test_modul_menusu(self):
        """Modül menüsü testleri"""
        try:
            # Modül menüsü var mı?
            if hasattr(self.ana_pencere, "modul_menusu"):
                menu_count = self.ana_pencere.modul_menusu.count()
                if menu_count > 0:
                    self.test_sonuclari["modul_menusu_yuklendi"] = True
                    self.logger.info(f"✓ Modül menüsü yüklendi ({menu_count} modül)")
                else:
                    self.logger.error("✗ Modül menüsü boş")
            else:
                self.logger.error("✗ Modül menüsü bulunamadı")
        except Exception as e:
            self.logger.error(f"Modül menüsü testi hatası: {e}")

    def test_modul_secimi(self):
        """Modül seçimi testleri"""
        try:
            # İlk modülü seç
            if hasattr(self.ana_pencere, "modul_menusu"):
                self.ana_pencere.modul_menusu.setCurrentRow(0)
                QTest.qWait(200)

                # Seçim yapıldı mı?
                if self.ana_pencere.modul_menusu.currentRow() == 0:
                    self.test_sonuclari["modul_secimi_calisiyor"] = True
                    self.logger.info("✓ Modül seçimi çalışıyor")
                else:
                    self.logger.error("✗ Modül seçimi çalışmıyor")
        except Exception as e:
            self.logger.error(f"Modül seçimi testi hatası: {e}")

    def test_icerik_alani(self):
        """İçerik alanı testleri"""
        try:
            # İçerik alanı var mı?
            if hasattr(self.ana_pencere, "icerik_alani"):
                widget_count = self.ana_pencere.icerik_alani.count()
                if widget_count > 0:
                    self.test_sonuclari["icerik_alani_degisiyor"] = True
                    self.logger.info(f"✓ İçerik alanı çalışıyor ({widget_count} widget)")
                else:
                    self.logger.error("✗ İçerik alanı boş")
            else:
                self.logger.error("✗ İçerik alanı bulunamadı")
        except Exception as e:
            self.logger.error(f"İçerik alanı testi hatası: {e}")

    def test_statusbar(self):
        """Status bar testleri"""
        try:
            # Status bar var mı?
            if hasattr(self.ana_pencere, "statusbar"):
                # Mesaj göstermeyi test et
                self.ana_pencere.statusbar.showMessage("Test mesajı")
                QTest.qWait(100)

                current_message = self.ana_pencere.statusbar.currentMessage()
                if "Test" in current_message:
                    self.test_sonuclari["statusbar_guncelleniyor"] = True
                    self.logger.info("✓ Status bar çalışıyor")
                else:
                    self.logger.error("✗ Status bar mesaj göstermiyor")
            else:
                self.logger.error("✗ Status bar bulunamadı")
        except Exception as e:
            self.logger.error(f"Status bar testi hatası: {e}")

    def test_oturum_bilgisi(self):
        """Oturum bilgisi testleri"""
        try:
            # Oturum label'ı var mı?
            if hasattr(self.ana_pencere, "oturum_label"):
                label_text = self.ana_pencere.oturum_label.text()
                if "Oturum" in label_text:
                    self.test_sonuclari["oturum_bilgisi_gosteriliyor"] = True
                    self.logger.info(f"✓ Oturum bilgisi gösteriliyor: {label_text}")
                else:
                    self.logger.error("✗ Oturum bilgisi gösterilmiyor")
            else:
                self.logger.error("✗ Oturum label'ı bulunamadı")
        except Exception as e:
            self.logger.error(f"Oturum bilgisi testi hatası: {e}")


def test_sonuclarini_yazdir(sonuclar):
    """Test sonuçlarını yazdırır"""
    print("\n" + "=" * 50)
    print("SONTECHSP UI TEST SONUÇLARI")
    print("=" * 50)

    basarili_testler = 0
    toplam_testler = len(sonuclar)

    for test_adi, sonuc in sonuclar.items():
        durum = "✓ BAŞARILI" if sonuc else "✗ BAŞARISIZ"
        print(f"{test_adi.replace('_', ' ').title()}: {durum}")
        if sonuc:
            basarili_testler += 1

    print("-" * 50)
    print(f"Toplam: {toplam_testler} test")
    print(f"Başarılı: {basarili_testler} test")
    print(f"Başarısız: {toplam_testler - basarili_testler} test")
    print(f"Başarı Oranı: %{(basarili_testler/toplam_testler)*100:.1f}")
    print("=" * 50)


def main():
    """Ana test fonksiyonu"""
    # PyQt6 uygulaması oluştur
    app = QApplication(sys.argv)
    app.setApplicationName("SONTECHSP UI Test")

    logger = kayit_al("ui_test_main")
    logger.info("UI test uygulaması başlatılıyor...")

    try:
        # Ana pencereyi oluştur
        ana_pencere = AnaPencere()
        ana_pencere.show()

        # Test thread'ini başlat
        test_thread = UITestThread(ana_pencere)

        # Test tamamlandığında uygulamayı kapat
        def testler_tamamlandi(sonuclar):
            test_sonuclarini_yazdir(sonuclar)
            # 2 saniye bekle sonra kapat
            QTimer.singleShot(2000, app.quit)

        test_thread.test_tamamlandi.connect(testler_tamamlandi)

        # Testleri 1 saniye sonra başlat
        QTimer.singleShot(1000, test_thread.start)

        # Uygulamayı çalıştır
        logger.info("Test uygulaması çalışıyor...")
        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"Test uygulaması hatası: {e}")
        print(f"HATA: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
