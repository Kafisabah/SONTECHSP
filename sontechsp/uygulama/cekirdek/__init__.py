# Version: 0.1.0
# Last Update: 2024-12-15
# Module: cekirdek
# Description: SONTECHSP çekirdek altyapı modülü entegrasyon noktası
# Changelog:
# - 0.1.0: İlk versiyon - Çekirdek modül entegrasyonu

"""
SONTECHSP Çekirdek Altyapı Modülü

Bu modül tüm çekirdek bileşenleri entegre eder ve merkezi başlatma
fonksiyonalitesi sağlar.
"""

from typing import Optional, Dict, Any
import os
import sys

from .ayarlar import AyarlarYoneticisi, ayarlar_yoneticisi_al
from .kayit import KayitSistemi, kayit_sistemi_al
from .hatalar import SontechHatasi, AlanHatasi, DogrulamaHatasi, EntegrasyonHatasi
from .yetki import YetkiKontrolcu, yetki_kontrolcu_al
from .oturum import OturumYoneticisi, oturum_yoneticisi_al, OturumBilgisi


class CekirdekSistem:
    """Çekirdek altyapı sisteminin merkezi yöneticisi"""
    
    def __init__(self):
        self._baslatildi = False
        self._ayarlar_yoneticisi: Optional[AyarlarYoneticisi] = None
        self._kayit_sistemi: Optional[KayitSistemi] = None
        self._yetki_kontrolcu: Optional[YetkiKontrolcu] = None
        self._oturum_yoneticisi: Optional[OturumYoneticisi] = None
    
    def baslat(self, yapilandirma_yolu: Optional[str] = None) -> bool:
        """
        Çekirdek sistemi başlatır
        
        Args:
            yapilandirma_yolu: .env dosyasının yolu (opsiyonel)
            
        Returns:
            bool: Başlatma başarılı ise True
        """
        try:
            # 1. Ayarlar yöneticisini başlat
            self._ayarlar_yoneticisi = ayarlar_yoneticisi_al()
            if yapilandirma_yolu:
                self._ayarlar_yoneticisi.env_dosya_yolu = yapilandirma_yolu
            
            # Zorunlu ayarları kontrol et
            if not self._ayarlar_yoneticisi.ayar_dogrula():
                raise DogrulamaHatasi("Zorunlu ayarlar eksik veya hatalı")
            
            # 2. Kayıt sistemini başlat
            self._kayit_sistemi = kayit_sistemi_al()
            self._kayit_sistemi.info("Çekirdek sistem başlatılıyor...")
            
            # 3. Yetki kontrolcüyü başlat
            self._yetki_kontrolcu = yetki_kontrolcu_al()
            
            # 4. Oturum yöneticisini başlat
            self._oturum_yoneticisi = oturum_yoneticisi_al()
            
            self._baslatildi = True
            self._kayit_sistemi.info("Çekirdek sistem başarıyla başlatıldı")
            
            return True
            
        except Exception as e:
            if self._kayit_sistemi:
                self._kayit_sistemi.error(f"Çekirdek sistem başlatma hatası: {e}")
            else:
                print(f"Çekirdek sistem başlatma hatası: {e}", file=sys.stderr)
            return False
    
    def durdur(self) -> bool:
        """
        Çekirdek sistemi durdurur
        
        Returns:
            bool: Durdurma başarılı ise True
        """
        try:
            if not self._baslatildi:
                return True
            
            if self._kayit_sistemi:
                self._kayit_sistemi.info("Çekirdek sistem durduruluyor...")
            
            # Aktif oturumu sonlandır
            if self._oturum_yoneticisi and self._oturum_yoneticisi.oturum_aktif_mi():
                self._oturum_yoneticisi.oturum_sonlandir()
            
            # Bileşenleri temizle
            self._oturum_yoneticisi = None
            self._yetki_kontrolcu = None
            
            if self._kayit_sistemi:
                self._kayit_sistemi.info("Çekirdek sistem başarıyla durduruldu")
            
            self._kayit_sistemi = None
            self._ayarlar_yoneticisi = None
            
            self._baslatildi = False
            return True
            
        except Exception as e:
            if self._kayit_sistemi:
                self._kayit_sistemi.error(f"Çekirdek sistem durdurma hatası: {e}")
            return False
    
    def baslatildi_mi(self) -> bool:
        """Sistem başlatıldı mı kontrol eder"""
        return self._baslatildi
    
    def durum_bilgisi_al(self) -> Dict[str, Any]:
        """Sistem durum bilgilerini döndürür"""
        return {
            'baslatildi': self._baslatildi,
            'ayarlar_yuklendi': self._ayarlar_yoneticisi is not None,
            'kayit_aktif': self._kayit_sistemi is not None,
            'yetki_aktif': self._yetki_kontrolcu is not None,
            'oturum_aktif': (self._oturum_yoneticisi is not None and 
                           self._oturum_yoneticisi.oturum_aktif_mi()),
            'python_surumu': sys.version,
            'platform': sys.platform
        }
    
    def saglik_kontrolu(self) -> bool:
        """Sistem sağlık kontrolü yapar"""
        try:
            if not self._baslatildi:
                return False
            
            # Ayarlar kontrolü
            if not self._ayarlar_yoneticisi or not self._ayarlar_yoneticisi.ayar_dogrula():
                return False
            
            # Kayıt sistemi kontrolü
            if not self._kayit_sistemi:
                return False
            
            # Test log yazma
            self._kayit_sistemi.debug("Sağlık kontrolü - test log")
            
            # Yetki kontrolcü kontrolü
            if not self._yetki_kontrolcu:
                return False
            
            # Oturum yöneticisi kontrolü
            if not self._oturum_yoneticisi:
                return False
            
            return True
            
        except Exception:
            return False


# Global çekirdek sistem instance
_cekirdek_sistem: Optional[CekirdekSistem] = None


def cekirdek_sistem_al() -> CekirdekSistem:
    """Global çekirdek sistem instance'ını döndürür"""
    global _cekirdek_sistem
    if _cekirdek_sistem is None:
        _cekirdek_sistem = CekirdekSistem()
    return _cekirdek_sistem


def cekirdek_baslat(yapilandirma_yolu: Optional[str] = None) -> bool:
    """Çekirdek sistemi başlatır (kısayol fonksiyon)"""
    return cekirdek_sistem_al().baslat(yapilandirma_yolu)


def cekirdek_durdur() -> bool:
    """Çekirdek sistemi durdurur (kısayol fonksiyon)"""
    return cekirdek_sistem_al().durdur()


def cekirdek_durum() -> Dict[str, Any]:
    """Çekirdek sistem durum bilgilerini döndürür (kısayol fonksiyon)"""
    return cekirdek_sistem_al().durum_bilgisi_al()


def cekirdek_saglik() -> bool:
    """Çekirdek sistem sağlık kontrolü yapar (kısayol fonksiyon)"""
    return cekirdek_sistem_al().saglik_kontrolu()


# Hata sınıflarını dışa aktar
__all__ = [
    'CekirdekSistem',
    'cekirdek_sistem_al',
    'cekirdek_baslat',
    'cekirdek_durdur',
    'cekirdek_durum',
    'cekirdek_saglik',
    'AyarlarYoneticisi',
    'ayarlar_yoneticisi_al',
    'KayitSistemi',
    'kayit_sistemi_al',
    'YetkiKontrolcu',
    'yetki_kontrolcu_al',
    'OturumYoneticisi',
    'oturum_yoneticisi_al',
    'OturumBilgisi',
    'SontechHatasi',
    'AlanHatasi',
    'DogrulamaHatasi',
    'EntegrasyonHatasi'
]