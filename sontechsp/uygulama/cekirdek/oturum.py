# Version: 0.1.0
# Last Update: 2024-12-15
# Module: oturum
# Description: SONTECHSP oturum yönetimi ve bağlam kontrolü
# Changelog:
# - 0.1.0: İlk versiyon - OturumBilgisi dataclass ve oturum yönetimi

"""
SONTECHSP Oturum Yönetimi Modülü

Bu modül kullanıcı oturumlarını ve çalışma bağlamını yönetir.
Firma, mağaza, terminal ve kullanıcı bilgilerini tutar.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from threading import Lock


@dataclass
class OturumBilgisi:
    """Aktif kullanıcı oturumu ve bağlam bilgileri"""
    kullanici_id: int
    kullanici_adi: str
    firma_id: int
    magaza_id: int
    terminal_id: Optional[int] = None
    roller: List[str] = field(default_factory=list)
    oturum_baslangic: datetime = field(default_factory=datetime.now)
    son_aktivite: datetime = field(default_factory=datetime.now)
    ek_bilgiler: Dict[str, Any] = field(default_factory=dict)


class OturumYoneticisi:
    """Oturum yönetimi ve bağlam kontrolü sınıfı"""
    
    def __init__(self):
        self._aktif_oturum: Optional[OturumBilgisi] = None
        self._oturum_kilidi = Lock()
        self._oturum_gecmisi: List[OturumBilgisi] = []
    
    def oturum_baslat(self, kullanici_id: int, kullanici_adi: str,
                      firma_id: int, magaza_id: int, 
                      terminal_id: Optional[int] = None,
                      roller: Optional[List[str]] = None) -> OturumBilgisi:
        """Yeni oturum başlatır"""
        with self._oturum_kilidi:
            # Mevcut oturumu sonlandır
            if self._aktif_oturum:
                self.oturum_sonlandir()
            
            # Yeni oturum oluştur
            self._aktif_oturum = OturumBilgisi(
                kullanici_id=kullanici_id,
                kullanici_adi=kullanici_adi,
                firma_id=firma_id,
                magaza_id=magaza_id,
                terminal_id=terminal_id,
                roller=roller or []
            )
            
            return self._aktif_oturum
    
    def baglam_guncelle(self, **kwargs) -> bool:
        """Oturum bağlamını günceller"""
        with self._oturum_kilidi:
            if not self._aktif_oturum:
                return False
            
            # Güncellenebilir alanlar
            guncellenebilir = {
                'firma_id', 'magaza_id', 'terminal_id', 'roller'
            }
            
            for anahtar, deger in kwargs.items():
                if anahtar in guncellenebilir:
                    setattr(self._aktif_oturum, anahtar, deger)
            
            # Son aktiviteyi güncelle
            self._aktif_oturum.son_aktivite = datetime.now()
            return True
    
    def oturum_sonlandir(self) -> bool:
        """Aktif oturumu sonlandırır"""
        with self._oturum_kilidi:
            if not self._aktif_oturum:
                return False
            
            # Geçmişe ekle
            self._oturum_gecmisi.append(self._aktif_oturum)
            
            # Aktif oturumu temizle
            self._aktif_oturum = None
            return True
    
    def aktif_oturum_al(self) -> Optional[OturumBilgisi]:
        """Aktif oturum bilgisini döndürür"""
        return self._aktif_oturum
    
    def oturum_aktif_mi(self) -> bool:
        """Oturum aktif mi kontrol eder"""
        return self._aktif_oturum is not None
    
    def baglan_bilgisi_al(self, anahtar: str) -> Any:
        """Bağlam bilgisi alır"""
        if not self._aktif_oturum:
            return None
        
        if hasattr(self._aktif_oturum, anahtar):
            return getattr(self._aktif_oturum, anahtar)
        
        return self._aktif_oturum.ek_bilgiler.get(anahtar)
    
    def baglan_bilgisi_ayarla(self, anahtar: str, deger: Any) -> bool:
        """Ek bağlam bilgisi ayarlar"""
        with self._oturum_kilidi:
            if not self._aktif_oturum:
                return False
            
            self._aktif_oturum.ek_bilgiler[anahtar] = deger
            self._aktif_oturum.son_aktivite = datetime.now()
            return True
    
    def coklu_terminal_destegi(self, terminal_listesi: List[int]) -> bool:
        """Çoklu terminal desteği için terminal listesi ayarlar"""
        return self.baglan_bilgisi_ayarla('desteklenen_terminaller', 
                                          terminal_listesi)
    
    def terminal_degistir(self, yeni_terminal_id: int) -> bool:
        """Aktif terminali değiştirir"""
        return self.baglam_guncelle(terminal_id=yeni_terminal_id)
    
    def oturum_suresi_al(self) -> Optional[int]:
        """Oturum süresini saniye cinsinden döndürür"""
        if not self._aktif_oturum:
            return None
        
        sure = datetime.now() - self._aktif_oturum.oturum_baslangic
        return int(sure.total_seconds())
    
    def son_aktivite_suresi_al(self) -> Optional[int]:
        """Son aktiviteden bu yana geçen süreyi saniye cinsinden döndürür"""
        if not self._aktif_oturum:
            return None
        
        sure = datetime.now() - self._aktif_oturum.son_aktivite
        return int(sure.total_seconds())


# Global oturum yöneticisi instance
_oturum_yoneticisi = None


def oturum_yoneticisi_al() -> OturumYoneticisi:
    """Global oturum yöneticisi instance'ını döndürür"""
    global _oturum_yoneticisi
    if _oturum_yoneticisi is None:
        _oturum_yoneticisi = OturumYoneticisi()
    return _oturum_yoneticisi


def aktif_oturum() -> Optional[OturumBilgisi]:
    """Aktif oturum bilgisini döndürür (kısayol fonksiyon)"""
    return oturum_yoneticisi_al().aktif_oturum_al()


def oturum_baslat(kullanici_id: int, kullanici_adi: str,
                  firma_id: int, magaza_id: int, 
                  terminal_id: Optional[int] = None,
                  roller: Optional[List[str]] = None) -> OturumBilgisi:
    """Yeni oturum başlatır (kısayol fonksiyon)"""
    return oturum_yoneticisi_al().oturum_baslat(
        kullanici_id, kullanici_adi, firma_id, magaza_id, 
        terminal_id, roller
    )


def oturum_sonlandir() -> bool:
    """Aktif oturumu sonlandırır (kısayol fonksiyon)"""
    return oturum_yoneticisi_al().oturum_sonlandir()


def oturum_baglamini_al() -> Optional[OturumBilgisi]:
    """Oturum bağlamını döndürür (kısayol fonksiyon)"""
    return oturum_yoneticisi_al().aktif_oturum_al()