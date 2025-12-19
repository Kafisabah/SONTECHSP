# Version: 0.1.0
# Last Update: 2024-12-19
# Module: arayuz.kaynaklar.logo_olceklendir_qt
# Description: PyQt6 kullanarak logo ölçeklendirme script'i
# Changelog:
# - İlk sürüm: PyQt6 ile logo ölçeklendirme

"""
PyQt6 Logo Ölçeklendirici

Bu script, PyQt6'nın kendi resim işleme yeteneklerini kullanarak
ana logoyu farklı boyutlarda ölçeklendirir.
"""

import sys
from pathlib import Path
from typing import Dict, Tuple
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication


class QtLogoOlceklendirici:
    """PyQt6 ile logo ölçeklendirme sınıfı"""

    def __init__(self):
        """Ölçeklendiriciyi başlatır"""
        self.kaynak_dizini = Path(__file__).parent
        self.resim_dizini = self.kaynak_dizini / "resimler"
        self.ikon_dizini = self.kaynak_dizini / "ikonlar"

        # İkonlar klasörünü oluştur
        self.ikon_dizini.mkdir(exist_ok=True)

        # Hedef boyutlar
        self.hedef_boyutlar: Dict[str, Tuple[int, int]] = {
            # Ana pencere logoları (resimler klasörü)
            "logo_buyuk.png": (256, 256),
            "logo_orta.png": (128, 128),
            "logo_kucuk.png": (64, 64),
            "logo_banner.png": (400, 100),
            # İkonlar (ikonlar klasörü)
            "logo_ikon_32.png": (32, 32),
            "logo_ikon_16.png": (16, 16),
            "logo_tepsi.png": (24, 24),
            "logo_favicon.png": (48, 48),
        }

    def ana_logo_kontrol(self) -> bool:
        """Ana logo dosyasının varlığını kontrol eder"""
        ana_logo_yolu = self.resim_dizini / "logo.png"
        return ana_logo_yolu.exists()

    def logo_olceklendir(self) -> Dict[str, bool]:
        """
        Ana logoyu farklı boyutlarda ölçeklendirir

        Returns:
            Her dosya için başarı durumu
        """
        if not self.ana_logo_kontrol():
            print("❌ Ana logo dosyası bulunamadı: logo.png")
            return {}

        ana_logo_yolu = self.resim_dizini / "logo.png"
        sonuclar = {}

        # Ana logoyu yükle
        ana_pixmap = QPixmap(str(ana_logo_yolu))

        if ana_pixmap.isNull():
            print("❌ Ana logo yüklenemedi!")
            return {}

        print(f"📷 Ana logo yüklendi: {ana_pixmap.width()}x{ana_pixmap.height()}")

        # Her hedef boyut için ölçeklendir
        for dosya_adi, (genislik, yukseklik) in self.hedef_boyutlar.items():
            try:
                # Ölçeklendir (smooth transformation ile)
                olcekli_pixmap = ana_pixmap.scaled(
                    genislik, yukseklik, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                )

                # Dosya yolunu belirle
                if "ikon" in dosya_adi or dosya_adi in ["logo_tepsi.png", "logo_favicon.png"]:
                    hedef_yol = self.ikon_dizini / dosya_adi
                else:
                    hedef_yol = self.resim_dizini / dosya_adi

                # Kaydet
                basarili = olcekli_pixmap.save(str(hedef_yol), "PNG")

                if basarili:
                    sonuclar[dosya_adi] = True
                    print(f"✅ {dosya_adi} oluşturuldu ({genislik}x{yukseklik})")
                else:
                    sonuclar[dosya_adi] = False
                    print(f"❌ {dosya_adi} kaydedilemedi")

            except Exception as e:
                sonuclar[dosya_adi] = False
                print(f"❌ {dosya_adi} oluşturulamadı: {e}")

        return sonuclar

    def kare_logo_olustur(self) -> bool:
        """Ana logodan kare logo oluşturur"""
        if not self.ana_logo_kontrol():
            return False

        ana_logo_yolu = self.resim_dizini / "logo.png"
        kare_logo_yolu = self.resim_dizini / "logo_kare.png"

        try:
            ana_pixmap = QPixmap(str(ana_logo_yolu))

            if ana_pixmap.isNull():
                return False

            # En küçük kenarı bul
            min_kenar = min(ana_pixmap.width(), ana_pixmap.height())

            # Kare olarak ölçeklendir
            kare_pixmap = ana_pixmap.scaled(
                min_kenar,
                min_kenar,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )

            # Kaydet
            basarili = kare_pixmap.save(str(kare_logo_yolu), "PNG")

            if basarili:
                print(f"✅ Kare logo oluşturuldu: {min_kenar}x{min_kenar}")
                return True
            else:
                print("❌ Kare logo kaydedilemedi")
                return False

        except Exception as e:
            print(f"❌ Kare logo oluşturulamadı: {e}")
            return False

    def rapor_olustur(self) -> None:
        """Oluşturulan dosyaların raporunu yazdırır"""
        print("\n📊 LOGO DOSYALARI RAPORU")
        print("=" * 50)

        # Resimler klasörü
        print("\n📁 Resimler klasörü:")
        for dosya in sorted(self.resim_dizini.glob("logo*.png")):
            pixmap = QPixmap(str(dosya))
            if not pixmap.isNull():
                dosya_boyutu = dosya.stat().st_size / 1024  # KB
                print(f"  📷 {dosya.name}: {pixmap.width()}x{pixmap.height()} ({dosya_boyutu:.1f} KB)")
            else:
                print(f"  ❌ {dosya.name}: Okunamadı")

        # İkonlar klasörü
        if self.ikon_dizini.exists():
            print("\n📁 İkonlar klasörü:")
            for dosya in sorted(self.ikon_dizini.glob("logo*.png")):
                pixmap = QPixmap(str(dosya))
                if not pixmap.isNull():
                    dosya_boyutu = dosya.stat().st_size / 1024  # KB
                    print(f"  🎯 {dosya.name}: {pixmap.width()}x{pixmap.height()} ({dosya_boyutu:.1f} KB)")
                else:
                    print(f"  ❌ {dosya.name}: Okunamadı")


def main():
    """Ana çalıştırma fonksiyonu"""
    # QApplication oluştur (GUI olmadan da çalışır)
    app = QApplication(sys.argv)

    print("🚀 PyQt6 Logo Ölçeklendirme İşlemi Başlatılıyor...")
    print("=" * 50)

    olceklendirici = QtLogoOlceklendirici()

    # Ana logo kontrolü
    if not olceklendirici.ana_logo_kontrol():
        print("❌ Ana logo dosyası bulunamadı!")
        print("📝 Lütfen logo.png dosyasını resimler/ klasörüne yerleştirin.")
        return

    # Kare logo oluştur
    print("\n🔲 Kare logo oluşturuluyor...")
    olceklendirici.kare_logo_olustur()

    # Farklı boyutlarda ölçeklendir
    print("\n📏 Farklı boyutlarda ölçeklendiriliyor...")
    sonuclar = olceklendirici.logo_olceklendir()

    # Sonuç özeti
    basarili = sum(1 for basari in sonuclar.values() if basari)
    toplam = len(sonuclar)

    print(f"\n📈 İşlem Tamamlandı: {basarili}/{toplam} dosya başarılı")

    # Rapor oluştur
    olceklendirici.rapor_olustur()

    print("\n✨ Logo ölçeklendirme işlemi tamamlandı!")
    print("💡 Artık uygulamanızda farklı boyutlardaki logoları kullanabilirsiniz.")


if __name__ == "__main__":
    main()
