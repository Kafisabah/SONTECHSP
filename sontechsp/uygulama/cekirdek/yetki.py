# Version: 0.1.0
# Last Update: 2024-12-15
# Module: yetki
# Description: SONTECHSP yetki kontrol modülü
# Changelog:
# - 0.1.0: İlk sürüm, rol tabanlı yetki kontrol sistemi

"""
SONTECHSP Yetki Kontrol Modülü

Bu modül kullanıcı yetkilendirmelerini kontrol eder:
- Rol tabanlı erişim kontrolü (RBAC)
- Yetki matrisi yönetimi
- Performanslı yetki kontrolü
- Hiyerarşik rol desteği
"""

from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
from enum import Enum


class YetkiSeviyesi(Enum):
    """Yetki seviye enum'u"""
    OKUMA = "okuma"
    YAZMA = "yazma"
    SILME = "silme"
    YONETIM = "yonetim"


@dataclass
class YetkiMatrisi:
    """Yetki matrisi veri modeli"""
    roller: Dict[str, List[str]]  # rol -> izinler listesi
    varsayilan_roller: List[str]
    admin_rolleri: List[str]
    rol_hiyerarsisi: Optional[Dict[str, List[str]]] = None  # üst_rol -> alt_roller


class YetkiKontrolcu:
    """
    SONTECHSP yetki kontrol sınıfı
    
    Rol tabanlı erişim kontrolü (RBAC) sağlar
    """
    
    def __init__(self):
        self._yetki_matrisi: Optional[YetkiMatrisi] = None
        self._rol_izin_cache: Dict[str, Set[str]] = {}
        self._gecerli_roller: Set[str] = set()
        self._gecerli_izinler: Set[str] = set()
        
        # Varsayılan yetki matrisi yükle
        self._varsayilan_yetki_matrisi_yukle()

    def _varsayilan_yetki_matrisi_yukle(self) -> None:
        """Varsayılan yetki matrisini yükler"""
        varsayilan_matris = YetkiMatrisi(
            roller={
                "misafir": ["sistem_goruntule"],
                "kullanici": ["sistem_goruntule", "veri_oku", "rapor_goruntule"],
                "operator": ["sistem_goruntule", "veri_oku", "veri_yaz", "rapor_goruntule", "rapor_olustur"],
                "mudur": ["sistem_goruntule", "veri_oku", "veri_yaz", "veri_sil", "rapor_goruntule", "rapor_olustur", "kullanici_yonet"],
                "admin": ["*"]  # Tüm yetkiler
            },
            varsayilan_roller=["kullanici"],
            admin_rolleri=["admin"],
            rol_hiyerarsisi={
                "admin": ["mudur", "operator", "kullanici", "misafir"],
                "mudur": ["operator", "kullanici", "misafir"],
                "operator": ["kullanici", "misafir"],
                "kullanici": ["misafir"]
            }
        )
        
        self.yetki_matrisi_yukle(varsayilan_matris)

    def yetki_matrisi_yukle(self, matris: YetkiMatrisi) -> None:
        """
        Yetki matrisini yükler
        
        Args:
            matris: Yetki matrisi
        """
        self._yetki_matrisi = matris
        self._rol_izin_cache.clear()
        
        # Geçerli rol ve izinleri güncelle
        self._gecerli_roller = set(matris.roller.keys())
        self._gecerli_izinler = set()
        
        for izinler in matris.roller.values():
            self._gecerli_izinler.update(izinler)
        
        # Cache'i önceden doldur (performans için)
        self._cache_doldur()

    def _cache_doldur(self) -> None:
        """Rol-izin cache'ini önceden doldurur"""
        if not self._yetki_matrisi:
            return
        
        for rol in self._gecerli_roller:
            self._rol_izin_cache[rol] = self._rol_izinlerini_hesapla(rol)

    def _rol_izinlerini_hesapla(self, rol: str) -> Set[str]:
        """
        Rolün tüm izinlerini hesaplar (hiyerarşi dahil)
        
        Args:
            rol: Rol adı
            
        Returns:
            İzinler kümesi
        """
        if not self._yetki_matrisi or rol not in self._yetki_matrisi.roller:
            return set()
        
        izinler = set(self._yetki_matrisi.roller[rol])
        
        # Admin rolü tüm izinlere sahip
        if "*" in izinler:
            return self._gecerli_izinler.copy()
        
        # Hiyerarşik izinleri ekle
        if (self._yetki_matrisi.rol_hiyerarsisi and 
            rol in self._yetki_matrisi.rol_hiyerarsisi):
            
            for alt_rol in self._yetki_matrisi.rol_hiyerarsisi[rol]:
                if alt_rol in self._yetki_matrisi.roller:
                    alt_izinler = set(self._yetki_matrisi.roller[alt_rol])
                    if "*" not in alt_izinler:  # Admin rolü hariç
                        izinler.update(alt_izinler)
        
        return izinler

    def izin_var_mi(self, rol: str, izin: str) -> bool:
        """
        Rolün belirtilen izne sahip olup olmadığını kontrol eder
        
        Args:
            rol: Kontrol edilecek rol
            izin: Kontrol edilecek izin
            
        Returns:
            True: İzin var, False: İzin yok
        """
        # Geçersiz rol kontrolü
        if not self.rol_dogrula(rol):
            return False
        
        # Geçersiz izin kontrolü
        if not izin or izin not in self._gecerli_izinler:
            return False
        
        # Cache'den kontrol et
        if rol in self._rol_izin_cache:
            return izin in self._rol_izin_cache[rol]
        
        # Cache'de yoksa hesapla ve cache'e ekle
        rol_izinleri = self._rol_izinlerini_hesapla(rol)
        self._rol_izin_cache[rol] = rol_izinleri
        
        return izin in rol_izinleri

    def coklu_izin_var_mi(self, rol: str, izinler: List[str]) -> Dict[str, bool]:
        """
        Rolün birden fazla izne sahip olup olmadığını kontrol eder
        
        Args:
            rol: Kontrol edilecek rol
            izinler: Kontrol edilecek izinler listesi
            
        Returns:
            İzin -> sonuç sözlüğü
        """
        sonuclar = {}
        for izin in izinler:
            sonuclar[izin] = self.izin_var_mi(rol, izin)
        return sonuclar

    def rol_dogrula(self, rol: str) -> bool:
        """
        Rolün geçerli olup olmadığını kontrol eder
        
        Args:
            rol: Kontrol edilecek rol
            
        Returns:
            True: Geçerli rol, False: Geçersiz rol
        """
        return bool(rol and rol in self._gecerli_roller)

    def izin_dogrula(self, izin: str) -> bool:
        """
        İznin geçerli olup olmadığını kontrol eder
        
        Args:
            izin: Kontrol edilecek izin
            
        Returns:
            True: Geçerli izin, False: Geçersiz izin
        """
        return bool(izin and izin in self._gecerli_izinler)

    def rol_izinlerini_listele(self, rol: str) -> List[str]:
        """
        Rolün sahip olduğu tüm izinleri listeler
        
        Args:
            rol: Rol adı
            
        Returns:
            İzinler listesi
        """
        if not self.rol_dogrula(rol):
            return []
        
        if rol in self._rol_izin_cache:
            return sorted(list(self._rol_izin_cache[rol]))
        
        rol_izinleri = self._rol_izinlerini_hesapla(rol)
        self._rol_izin_cache[rol] = rol_izinleri
        
        return sorted(list(rol_izinleri))

    def izin_gerektiren_rolleri_listele(self, izin: str) -> List[str]:
        """
        Belirtilen izne sahip rolleri listeler
        
        Args:
            izin: İzin adı
            
        Returns:
            Roller listesi
        """
        if not self.izin_dogrula(izin):
            return []
        
        roller = []
        for rol in self._gecerli_roller:
            if self.izin_var_mi(rol, izin):
                roller.append(rol)
        
        return sorted(roller)

    def en_yuksek_rol_bul(self, roller: List[str]) -> Optional[str]:
        """
        Verilen roller arasından en yüksek yetkili olanı bulur
        
        Args:
            roller: Rol listesi
            
        Returns:
            En yüksek rol veya None
        """
        if not roller or not self._yetki_matrisi:
            return None
        
        # Admin rolü varsa öncelik ver
        for rol in roller:
            if rol in self._yetki_matrisi.admin_rolleri:
                return rol
        
        # Hiyerarşiye göre en yüksek rolü bul
        if self._yetki_matrisi.rol_hiyerarsisi:
            for ust_rol, alt_roller in self._yetki_matrisi.rol_hiyerarsisi.items():
                if ust_rol in roller:
                    return ust_rol
        
        # Hiyerarşi yoksa izin sayısına göre
        en_yuksek_rol = None
        en_fazla_izin = 0
        
        for rol in roller:
            if self.rol_dogrula(rol):
                izin_sayisi = len(self.rol_izinlerini_listele(rol))
                if izin_sayisi > en_fazla_izin:
                    en_fazla_izin = izin_sayisi
                    en_yuksek_rol = rol
        
        return en_yuksek_rol

    def yetki_istatistikleri(self) -> Dict[str, Any]:
        """
        Yetki sistemi istatistiklerini döndürür
        
        Returns:
            İstatistik bilgileri
        """
        if not self._yetki_matrisi:
            return {}
        
        return {
            'toplam_rol_sayisi': len(self._gecerli_roller),
            'toplam_izin_sayisi': len(self._gecerli_izinler),
            'admin_rol_sayisi': len(self._yetki_matrisi.admin_rolleri),
            'varsayilan_rol_sayisi': len(self._yetki_matrisi.varsayilan_roller),
            'cache_boyutu': len(self._rol_izin_cache),
            'hiyerarsi_var_mi': bool(self._yetki_matrisi.rol_hiyerarsisi),
            'roller': sorted(list(self._gecerli_roller)),
            'izinler': sorted(list(self._gecerli_izinler))
        }

    def yetki_matrisi_disa_aktar(self) -> Dict[str, Any]:
        """
        Yetki matrisini dışa aktarır
        
        Returns:
            Yetki matrisi sözlüğü
        """
        if not self._yetki_matrisi:
            return {}
        
        return {
            'roller': self._yetki_matrisi.roller.copy(),
            'varsayilan_roller': self._yetki_matrisi.varsayilan_roller.copy(),
            'admin_rolleri': self._yetki_matrisi.admin_rolleri.copy(),
            'rol_hiyerarsisi': self._yetki_matrisi.rol_hiyerarsisi.copy() if self._yetki_matrisi.rol_hiyerarsisi else None
        }

    def cache_temizle(self) -> None:
        """Rol-izin cache'ini temizler"""
        self._rol_izin_cache.clear()

    def cache_yenile(self) -> None:
        """Cache'i yeniden doldurur"""
        self.cache_temizle()
        self._cache_doldur()


# Global yetki kontrolcü instance'ı
_yetki_kontrolcu = None


def yetki_kontrolcu_al() -> YetkiKontrolcu:
    """Global yetki kontrolcü instance'ını döndürür"""
    global _yetki_kontrolcu
    if _yetki_kontrolcu is None:
        _yetki_kontrolcu = YetkiKontrolcu()
    return _yetki_kontrolcu


# Yardımcı fonksiyonlar
def izin_kontrol_et(rol: str, izin: str) -> bool:
    """
    Hızlı izin kontrolü
    
    Args:
        rol: Rol adı
        izin: İzin adı
        
    Returns:
        İzin durumu
    """
    return yetki_kontrolcu_al().izin_var_mi(rol, izin)


def yetki_gerekli(gerekli_izin: str):
    """
    Decorator: Fonksiyon çağrısı için yetki kontrolü
    
    Usage:
        @yetki_gerekli("veri_yaz")
        def veri_kaydet(rol, ...):
            # kod
    """
    def decorator(func):
        def wrapper(rol, *args, **kwargs):
            if not izin_kontrol_et(rol, gerekli_izin):
                from .hatalar import DogrulamaHatasi
                raise DogrulamaHatasi(
                    "yetki_kontrolu",
                    f"'{gerekli_izin}' izni gerekli",
                    mevcut_deger=rol,
                    beklenen_deger=gerekli_izin
                )
            return func(rol, *args, **kwargs)
        return wrapper
    return decorator