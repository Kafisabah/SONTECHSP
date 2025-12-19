# Version: 0.1.0
# Last Update: 2024-12-19
# Module: arayuz.kaynaklar.logo_olceklendir
# Description: Ana logoyu farklı boyutlarda ölçeklendiren yardımcı script
# Changelog:
# - İlk sürüm: Logo ölçeklendirme ve kaydetme fonksiyonları

"""
Logo Ölçeklendirme Yardımcısı

Bu script, ana logo dosyasını alıp farklı boyutlarda
ölçeklendirilmiş versiyonlarını oluşturur.
"""

import os
from pathlib import Path
from PIL import Image, ImageOps
from typing import Dict, Tuple


class LogoOlceklendirici:
    """Logo ölçeklendirme işlemlerini yöneten sınıf"""

    def __init__(self):
        """Ölçeklendiriciyi başlatır"""
        self.kaynak_dizini = Path(__file__).parent
        self.resim_dizini = self.kaynak_dizini / "resimler"
        self.ikon_dizini = self.kaynak_dizini / "ikonlar"

        # Hedef boyutlar (genişlik, yükseklik)
        self.hedef_boyutlar: Dict[str, Tuple[int, int]] = {
            # Ana pencere logoları
            "logo_buyuk.png": (256, 256),  # Splash screen, hakkında
            "logo_orta.png": (128, 128),  # Ana pencere header
            "logo_kucuk.png": (64, 64),  # Toolbar, küçük alanlar
            # Pencere ikonları
            "logo_ikon_32.png": (32, 32),  # Pencere ikonu
            "logo_ikon_16.png": (16, 16),  # Küçük pencere ikonu
            # Sistem tepsisi
            "logo_tepsi.png": (24, 24),  # Sistem tepsisi ikonu
            # Özel boyutlar
            "logo_banner.png": (400, 100),  # Banner/header için
            "logo_favicon.png": (48, 48),  # Web/favicon benzeri
        }

    def ana_logo_kontrol(self) -> bool:
        """
        Ana logo dosyasının varlığını kontrol eder

        Returns:
            Ana logo varsa True, yoksa False
        """
        ana_logo_yolu = self.resim_dizini / "logo.png"
        return ana_logo_yolu.exists()

    def logo_olceklendir(self, kalite_koruma: bool = True) -> Dict[str, bool]:
        """
        Ana logoyu farklı boyutlarda ölçeklendirir

        Args:
            kalite_koruma: Yüksek kalite ölçeklendirme kullanılsın mı

        Returns:
            Her dosya için başarı durumu dict'i
        """
        if not self.ana_logo_kontrol():
            print("❌ Ana logo dosyası bulunamadı: logo.png")
            return {}

        ana_logo_yolu = self.resim_dizini / "logo.png"
        sonuclar = {}

        try:
            # Ana logoyu aç
            with Image.open(ana_logo_yolu) as ana_resim:
                print(f"📷 Ana logo yüklendi: {ana_resim.size}")

                # Her hedef boyut için ölçeklendir
                for dosya_adi, (genislik, yukseklik) in self.hedef_boyutlar.items():
                    try:
                        # Ölçeklendirme yap
                        if kalite_koruma:
                            # Yüksek kalite ölçeklendirme (LANCZOS)
                            olcekli_resim = ana_resim.resize((genislik, yukseklik), Image.Resampling.LANCZOS)
                        else:
                            # Hızlı ölçeklendirme
                            olcekli_resim = ana_resim.resize((genislik, yukseklik))

                        # Dosya yolunu belirle
                        if "ikon" in dosya_adi or dosya_adi in ["logo_tepsi.png"]:
                            hedef_yol = self.ikon_dizini / dosya_adi
                        else:
                            hedef_yol = self.resim_dizini / dosya_adi

                        # Kaydet
                        olcekli_resim.save(hedef_yol, "PNG", optimize=True)
                        sonuclar[dosya_adi] = True
                        print(f"✅ {dosya_adi} oluşturuldu ({genislik}x{yukseklik})")

                    except Exception as e:
                        sonuclar[dosya_adi] = False
                        print(f"❌ {dosya_adi} oluşturulamadı: {e}")

        except Exception as e:
            print(f"❌ Ana logo açılamadı: {e}")
            return {}

        return sonuclar

    def kare_logo_olustur(self) -> bool:
        """
        Ana logodan kare (1:1) oran logo oluşturur

        Returns:
            Başarılıysa True
        """
        if not self.ana_logo_kontrol():
            return False

        ana_logo_yolu = self.resim_dizini / "logo.png"
        kare_logo_yolu = self.resim_dizini / "logo_kare.png"

        try:
            with Image.open(ana_logo_yolu) as ana_resim:
                # En küçük kenarı bul
                min_kenar = min(ana_resim.size)

                # Kare kırpma yap (merkezi al)
                kare_resim = ImageOps.fit(
                    ana_resim, (min_kenar, min_kenar), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5)
                )

                # Kaydet
                kare_resim.save(kare_logo_yolu, "PNG", optimize=True)
                print(f"✅ Kare logo oluşturuldu: {min_kenar}x{min_kenar}")
                return True

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
            try:
                with Image.open(dosya) as img:
                    boyut = img.size
                    dosya_boyutu = dosya.stat().st_size / 1024  # KB
                    print(f"  📷 {dosya.name}: {boyut[0]}x{boyut[1]} ({dosya_boyutu:.1f} KB)")
            except:
                print(f"  ❌ {dosya.name}: Okunamadı")

        # İkonlar klasörü
        print("\n📁 İkonlar klasörü:")
        for dosya in sorted(self.ikon_dizini.glob("logo*.png")):
            try:
                with Image.open(dosya) as img:
                    boyut = img.size
                    dosya_boyutu = dosya.stat().st_size / 1024  # KB
                    print(f"  🎯 {dosya.name}: {boyut[0]}x{boyut[1]} ({dosya_boyutu:.1f} KB)")
            except:
                print(f"  ❌ {dosya.name}: Okunamadı")


def main():
    """Ana çalıştırma fonksiyonu"""
    print("🚀 Logo Ölçeklendirme İşlemi Başlatılıyor...")
    print("=" * 50)

    olceklendirici = LogoOlceklendirici()

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
    sonuclar = olceklendirici.logo_olceklendir(kalite_koruma=True)

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
