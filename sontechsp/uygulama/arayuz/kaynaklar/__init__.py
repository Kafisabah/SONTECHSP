# Version: 0.1.0
# Last Update: 2024-12-19
# Module: arayuz.kaynaklar
# Description: Uygulama kaynaklarını (logo, ikon, resim) yöneten modül
# Changelog:
# - İlk sürüm: Kaynak yolu yönetimi ve yükleme fonksiyonları

"""
Uygulama Kaynakları Modülü

Bu modül, uygulamanın görsel kaynaklarını (logo, ikon, resim)
merkezi bir yerden yönetir ve PyQt6 uygulamasında kullanılabilir
hale getirir.
"""

import os
from pathlib import Path
from typing import Optional
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon, QPixmap


class KaynakYoneticisi:
    """Uygulama kaynaklarını yöneten sınıf"""

    def __init__(self):
        """Kaynak yöneticisini başlatır"""
        self._kaynak_dizini = Path(__file__).parent
        self._resim_dizini = self._kaynak_dizini / "resimler"
        self._ikon_dizini = self._kaynak_dizini / "ikonlar"

    def logo_yolu(self, dosya_adi: str = "logo.png") -> Path:
        """
        Logo dosyasının tam yolunu döndürür

        Args:
            dosya_adi: Logo dosya adı (varsayılan: logo.png)

        Returns:
            Logo dosyasının Path nesnesi
        """
        return self._resim_dizini / dosya_adi

    def resim_yolu(self, dosya_adi: str) -> Path:
        """
        Resim dosyasının tam yolunu döndürür

        Args:
            dosya_adi: Resim dosya adı

        Returns:
            Resim dosyasının Path nesnesi
        """
        return self._resim_dizini / dosya_adi

    def ikon_yolu(self, dosya_adi: str) -> Path:
        """
        İkon dosyasının tam yolunu döndürür

        Args:
            dosya_adi: İkon dosya adı

        Returns:
            İkon dosyasının Path nesnesi
        """
        return self._ikon_dizini / dosya_adi

    def logo_yukle(
        self, dosya_adi: str = "logo.png", genislik: Optional[int] = None, yukseklik: Optional[int] = None
    ) -> Optional[QPixmap]:
        """
        Logo dosyasını QPixmap olarak yükler

        Args:
            dosya_adi: Logo dosya adı
            genislik: Ölçeklendirme genişliği (opsiyonel)
            yukseklik: Ölçeklendirme yüksekliği (opsiyonel)

        Returns:
            QPixmap nesnesi veya None (dosya bulunamazsa)
        """
        yol = self.logo_yolu(dosya_adi)
        return self._pixmap_yukle(yol, genislik, yukseklik)

    def resim_yukle(
        self, dosya_adi: str, genislik: Optional[int] = None, yukseklik: Optional[int] = None
    ) -> Optional[QPixmap]:
        """
        Resim dosyasını QPixmap olarak yükler

        Args:
            dosya_adi: Resim dosya adı
            genislik: Ölçeklendirme genişliği (opsiyonel)
            yukseklik: Ölçeklendirme yüksekliği (opsiyonel)

        Returns:
            QPixmap nesnesi veya None (dosya bulunamazsa)
        """
        yol = self.resim_yolu(dosya_adi)
        return self._pixmap_yukle(yol, genislik, yukseklik)

    def ikon_yukle(self, dosya_adi: str, boyut: Optional[int] = None) -> Optional[QIcon]:
        """
        İkon dosyasını QIcon olarak yükler

        Args:
            dosya_adi: İkon dosya adı
            boyut: İkon boyutu (piksel, opsiyonel)

        Returns:
            QIcon nesnesi veya None (dosya bulunamazsa)
        """
        yol = self.ikon_yolu(dosya_adi)

        if not yol.exists():
            return None

        ikon = QIcon(str(yol))

        if boyut:
            # İkon boyutunu ayarla
            pixmap = ikon.pixmap(QSize(boyut, boyut))
            return QIcon(pixmap)

        return ikon

    def _pixmap_yukle(self, yol: Path, genislik: Optional[int], yukseklik: Optional[int]) -> Optional[QPixmap]:
        """
        Dosya yolundan QPixmap yükler ve ölçeklendirir

        Args:
            yol: Dosya yolu
            genislik: Ölçeklendirme genişliği
            yukseklik: Ölçeklendirme yüksekliği

        Returns:
            QPixmap nesnesi veya None
        """
        if not yol.exists():
            return None

        pixmap = QPixmap(str(yol))

        if genislik or yukseklik:
            # Ölçeklendirme yap
            if genislik and yukseklik:
                from PyQt6.QtCore import Qt

                pixmap = pixmap.scaled(genislik, yukseklik, Qt.AspectRatioMode.KeepAspectRatio)
            elif genislik:
                pixmap = pixmap.scaledToWidth(genislik)
            elif yukseklik:
                pixmap = pixmap.scaledToHeight(yukseklik)

        return pixmap

    def logo_olceklendir_ve_kaydet(self) -> bool:
        """
        Ana logoyu farklı boyutlarda ölçeklendirip kaydeder

        Returns:
            İşlem başarılıysa True
        """
        from PyQt6.QtCore import Qt

        ana_logo_yolu = self.logo_yolu("logo.png")

        if not ana_logo_yolu.exists():
            print("❌ Ana logo dosyası bulunamadı: logo.png")
            return False

        # İkonlar klasörünü oluştur
        self._ikon_dizini.mkdir(exist_ok=True)

        # Ana logoyu yükle
        ana_pixmap = QPixmap(str(ana_logo_yolu))

        if ana_pixmap.isNull():
            print("❌ Ana logo yüklenemedi!")
            return False

        print(f"📷 Ana logo yüklendi: {ana_pixmap.width()}x{ana_pixmap.height()}")

        # Hedef boyutlar
        hedef_boyutlar = {
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

        basarili_sayisi = 0
        toplam_sayisi = len(hedef_boyutlar)

        # Her hedef boyut için ölçeklendir
        for dosya_adi, (genislik, yukseklik) in hedef_boyutlar.items():
            try:
                # Ölçeklendir
                olcekli_pixmap = ana_pixmap.scaled(
                    genislik, yukseklik, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                )

                # Dosya yolunu belirle
                if "ikon" in dosya_adi or dosya_adi in ["logo_tepsi.png", "logo_favicon.png"]:
                    hedef_yol = self._ikon_dizini / dosya_adi
                else:
                    hedef_yol = self._resim_dizini / dosya_adi

                # Kaydet
                if olcekli_pixmap.save(str(hedef_yol), "PNG"):
                    basarili_sayisi += 1
                    print(f"✅ {dosya_adi} oluşturuldu ({genislik}x{yukseklik})")
                else:
                    print(f"❌ {dosya_adi} kaydedilemedi")

            except Exception as e:
                print(f"❌ {dosya_adi} oluşturulamadı: {e}")

        print(f"\n📈 İşlem Tamamlandı: {basarili_sayisi}/{toplam_sayisi} dosya başarılı")
        return basarili_sayisi > 0


# Global kaynak yöneticisi instance
kaynak_yoneticisi = KaynakYoneticisi()


# Kolay erişim fonksiyonları
def logo_yukle(
    dosya_adi: str = "logo.png", genislik: Optional[int] = None, yukseklik: Optional[int] = None
) -> Optional[QPixmap]:
    """Logo yükler"""
    return kaynak_yoneticisi.logo_yukle(dosya_adi, genislik, yukseklik)


def resim_yukle(dosya_adi: str, genislik: Optional[int] = None, yukseklik: Optional[int] = None) -> Optional[QPixmap]:
    """Resim yükler"""
    return kaynak_yoneticisi.resim_yukle(dosya_adi, genislik, yukseklik)


def ikon_yukle(dosya_adi: str, boyut: Optional[int] = None) -> Optional[QIcon]:
    """İkon yükler"""
    return kaynak_yoneticisi.ikon_yukle(dosya_adi, boyut)


def logo_olceklendir():
    """Ana logoyu farklı boyutlarda ölçeklendirir"""
    return kaynak_yoneticisi.logo_olceklendir_ve_kaydet()
