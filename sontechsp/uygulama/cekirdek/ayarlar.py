# Version: 0.1.0
# Last Update: 2024-12-15
# Module: ayarlar
# Description: SONTECHSP ayarlar yönetimi modülü
# Changelog:
# - 0.1.0: İlk sürüm, .env dosya okuma ve ayar yönetimi sistemi

"""
SONTECHSP Ayarlar Yönetimi Modülü

Bu modül uygulama yapılandırmasını yönetir:
- .env dosya okuma
- Ortam değişkeni öncelik sistemi
- Zorunlu ayar doğrulama
- Tip güvenli değer dönüşümü
- Örnek ayar dosyası oluşturma
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass


@dataclass
class YapilandirmaModeli:
    """Uygulama yapılandırma modeli"""
    veritabani_url: str
    log_klasoru: str
    ortam: str  # dev/prod
    log_seviyesi: str = "INFO"
    log_dosya_boyutu: int = 10485760  # 10MB
    log_dosya_sayisi: int = 5


class AyarlarYoneticisi:
    """
    Uygulama ayarlarını yöneten merkezi sınıf
    
    Öncelik sırası:
    1. Ortam değişkenleri
    2. .env dosyası
    3. Varsayılan değerler
    """
    
    def __init__(self, env_dosya_yolu: Optional[str] = None):
        self._ayarlar: Dict[str, str] = {}
        self._varsayilan_ayarlar: Dict[str, str] = {
            "VERITABANI_URL": "postgresql://localhost:5432/sontechsp",
            "LOG_KLASORU": "logs",
            "ORTAM": "dev",
            "LOG_SEVIYESI": "INFO",
            "LOG_DOSYA_BOYUTU": "10485760",
            "LOG_DOSYA_SAYISI": "5"
        }
        self._zorunlu_ayarlar = {"VERITABANI_URL", "LOG_KLASORU", "ORTAM"}
        self._env_dosya_yolu = env_dosya_yolu or ".env"
        self._ayarlari_yukle()

    def _ayarlari_yukle(self) -> None:
        """Ayarları tüm kaynaklardan yükler"""
        # Önce varsayılan değerleri yükle
        self._ayarlar.update(self._varsayilan_ayarlar)
        
        # .env dosyasından yükle
        self._env_dosyasini_oku()
        
        # Ortam değişkenlerinden yükle (en yüksek öncelik)
        self._ortam_degiskenlerini_yukle()

    def _env_dosyasini_oku(self) -> None:
        """
        .env dosyasını okur ve ayarları yükler
        Dosya yoksa sessizce geçer
        """
        env_dosya = Path(self._env_dosya_yolu)
        if not env_dosya.exists():
            return
        
        try:
            with open(env_dosya, 'r', encoding='utf-8') as f:
                for satir in f:
                    satir = satir.strip()
                    if satir and not satir.startswith('#'):
                        if '=' in satir:
                            anahtar, deger = satir.split('=', 1)
                            anahtar = anahtar.strip()
                            deger = deger.strip().strip('"\'')
                            self._ayarlar[anahtar] = deger
        except Exception as e:
            raise ValueError(f".env dosyası okunamadı: {e}")

    def _ortam_degiskenlerini_yukle(self) -> None:
        """Ortam değişkenlerini yükler (en yüksek öncelik)"""
        for anahtar in self._ayarlar.keys():
            ortam_degeri = os.getenv(anahtar)
            if ortam_degeri is not None:
                self._ayarlar[anahtar] = ortam_degeri

    def ayar_oku(self, anahtar: str, varsayilan: Any = None) -> Any:
        """
        Ayar değerini okur
        
        Args:
            anahtar: Ayar anahtarı
            varsayilan: Bulunamazsa döndürülecek varsayılan değer
            
        Returns:
            Ayar değeri veya varsayılan değer
        """
        deger = self._ayarlar.get(anahtar, varsayilan)
        return self._tip_donusumu_yap(deger)

    def zorunlu_ayar_oku(self, anahtar: str) -> Any:
        """
        Zorunlu ayar değerini okur
        
        Args:
            anahtar: Ayar anahtarı
            
        Returns:
            Ayar değeri
            
        Raises:
            ValueError: Ayar bulunamazsa
        """
        if anahtar not in self._ayarlar:
            raise ValueError(f"Zorunlu ayar bulunamadı: {anahtar}")
        
        deger = self._ayarlar[anahtar]
        if not deger:
            raise ValueError(f"Zorunlu ayar boş: {anahtar}")
        
        return self._tip_donusumu_yap(deger)

    def _tip_donusumu_yap(self, deger: Any) -> Any:
        """
        Değeri uygun tipe dönüştürür
        
        Args:
            deger: Dönüştürülecek değer
            
        Returns:
            Tip güvenli değer
        """
        if not isinstance(deger, str):
            return deger
        
        # Boolean dönüşümü
        if deger.lower() in ('true', 'false'):
            return deger.lower() == 'true'
        
        # Integer dönüşümü
        if deger.isdigit():
            return int(deger)
        
        # Float dönüşümü
        try:
            if '.' in deger:
                return float(deger)
        except ValueError:
            pass
        
        return deger

    def ayar_dogrula(self) -> bool:
        """
        Zorunlu ayarların varlığını doğrular
        
        Returns:
            True: Tüm zorunlu ayarlar mevcut
            
        Raises:
            ValueError: Zorunlu ayar eksikse
        """
        eksik_ayarlar = []
        
        for zorunlu_ayar in self._zorunlu_ayarlar:
            if zorunlu_ayar not in self._ayarlar or not self._ayarlar[zorunlu_ayar]:
                eksik_ayarlar.append(zorunlu_ayar)
        
        if eksik_ayarlar:
            raise ValueError(
                f"Eksik zorunlu ayarlar: {', '.join(eksik_ayarlar)}. "
                f"Lütfen .env dosyasını kontrol edin veya ortam değişkenlerini ayarlayın."
            )
        
        return True

    def ornek_dosya_olustur(self) -> None:
        """
        Örnek .env dosyası oluşturur
        Mevcut dosya varsa .env.example olarak oluşturur
        """
        dosya_adi = ".env.example" if Path(self._env_dosya_yolu).exists() else self._env_dosya_yolu
        
        ornek_icerik = """# SONTECHSP Yapılandırma Dosyası
# Bu dosyayı .env olarak kopyalayın ve değerleri düzenleyin

# Veritabanı Bağlantısı (ZORUNLU)
VERITABANI_URL=postgresql://kullanici:sifre@localhost:5432/sontechsp

# Log Ayarları (ZORUNLU)
LOG_KLASORU=logs
LOG_SEVIYESI=INFO
LOG_DOSYA_BOYUTU=10485760
LOG_DOSYA_SAYISI=5

# Ortam Ayarı (ZORUNLU)
# dev: Geliştirme ortamı
# prod: Üretim ortamı
ORTAM=dev

# Güvenlik Ayarları
# GIZLI_ANAHTAR=your-secret-key-here
# JWT_GIZLI_ANAHTAR=your-jwt-secret-here

# E-belge Ayarları
# EBELGE_KULLANICI=
# EBELGE_SIFRE=
# EBELGE_TEST_MODU=true

# Kargo Ayarları
# KARGO_API_ANAHTARI=
# KARGO_TEST_MODU=true
"""
        
        try:
            with open(dosya_adi, 'w', encoding='utf-8') as f:
                f.write(ornek_icerik)
        except Exception as e:
            raise ValueError(f"Örnek ayar dosyası oluşturulamadı: {e}")

    def yapilandirma_modeli_olustur(self) -> YapilandirmaModeli:
        """
        Mevcut ayarlardan yapılandırma modeli oluşturur
        
        Returns:
            YapilandirmaModeli instance'ı
        """
        return YapilandirmaModeli(
            veritabani_url=self.zorunlu_ayar_oku("VERITABANI_URL"),
            log_klasoru=self.zorunlu_ayar_oku("LOG_KLASORU"),
            ortam=self.zorunlu_ayar_oku("ORTAM"),
            log_seviyesi=self.ayar_oku("LOG_SEVIYESI", "INFO"),
            log_dosya_boyutu=self.ayar_oku("LOG_DOSYA_BOYUTU", 10485760),
            log_dosya_sayisi=self.ayar_oku("LOG_DOSYA_SAYISI", 5)
        )

    def ayar_degisikligini_algi(self) -> bool:
        """
        Ayar dosyasındaki değişiklikleri algılar
        
        Returns:
            True: Değişiklik algılandı
        """
        eski_ayarlar = self._ayarlar.copy()
        self._ayarlari_yukle()
        return eski_ayarlar != self._ayarlar

    def tum_ayarlari_listele(self) -> Dict[str, Any]:
        """
        Tüm ayarları döndürür (hassas bilgiler maskelenir)
        
        Returns:
            Ayarlar sözlüğü
        """
        maskelenmis_ayarlar = {}
        hassas_anahtarlar = {"SIFRE", "PASSWORD", "SECRET", "KEY", "TOKEN"}
        
        for anahtar, deger in self._ayarlar.items():
            if any(hassas in anahtar.upper() for hassas in hassas_anahtarlar):
                maskelenmis_ayarlar[anahtar] = "***"
            else:
                maskelenmis_ayarlar[anahtar] = deger
        
        return maskelenmis_ayarlar


# Global ayarlar yöneticisi instance
_ayarlar_yoneticisi: Optional[AyarlarYoneticisi] = None


def ayarlar_yoneticisi_al() -> AyarlarYoneticisi:
    """Global ayarlar yöneticisi instance'ını döndürür"""
    global _ayarlar_yoneticisi
    if _ayarlar_yoneticisi is None:
        _ayarlar_yoneticisi = AyarlarYoneticisi()
    return _ayarlar_yoneticisi


# Kısayol fonksiyonlar
def ayar_al(anahtar: str, varsayilan: Any = None) -> Any:
    """Ayar değerini okuma kısayolu"""
    return ayarlar_yoneticisi_al().ayar_oku(anahtar, varsayilan)


def zorunlu_ayar_al(anahtar: str) -> Any:
    """Zorunlu ayar değerini okuma kısayolu"""
    return ayarlar_yoneticisi_al().zorunlu_ayar_oku(anahtar)


def ayarlari_dogrula() -> bool:
    """Ayar doğrulama kısayolu"""
    return ayarlar_yoneticisi_al().ayar_dogrula()