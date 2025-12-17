# Version: 0.1.0
# Last Update: 2024-12-17
# Module: kargo.dto
# Description: Kargo modülü veri transfer objeleri
# Changelog:
# - KargoEtiketOlusturDTO eklendi
# - KargoEtiketSonucDTO eklendi
# - KargoDurumDTO eklendi

"""
Kargo modülü veri transfer objeleri (DTO).

Bu modül, kargo işlemlerinde kullanılan veri yapılarını içerir.
Etiket oluşturma, sonuç ve durum bilgileri için DTO'lar tanımlanır.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from decimal import Decimal

from .sabitler import VARSAYILAN_PAKET_AGIRLIK_KG


@dataclass
class KargoEtiketOlusturDTO:
    """Kargo etiket oluşturma için giriş verisi."""
    
    # Zorunlu alanlar
    kaynak_turu: str
    kaynak_id: int
    alici_ad: str
    alici_telefon: str
    alici_adres: str
    alici_il: str
    alici_ilce: str
    tasiyici: str
    
    # Opsiyonel alanlar
    gonderen_ad: Optional[str] = None
    gonderen_telefon: Optional[str] = None
    paket_agirlik_kg: Decimal = Decimal(str(VARSAYILAN_PAKET_AGIRLIK_KG))
    servis_kodu: Optional[str] = None
    aciklama: Optional[str] = None
    
    def __post_init__(self):
        """Veri doğrulama ve normalizasyon."""
        # Paket ağırlığını Decimal'e çevir
        if not isinstance(self.paket_agirlik_kg, Decimal):
            self.paket_agirlik_kg = Decimal(str(self.paket_agirlik_kg))
        
        # Boş string'leri None'a çevir
        if self.gonderen_ad == "":
            self.gonderen_ad = None
        if self.gonderen_telefon == "":
            self.gonderen_telefon = None
        if self.servis_kodu == "":
            self.servis_kodu = None
        if self.aciklama == "":
            self.aciklama = None


@dataclass
class KargoEtiketSonucDTO:
    """Kargo etiket oluşturma sonucu."""
    
    etiket_id: int
    durum: str
    takip_no: Optional[str] = None
    mesaj: Optional[str] = None
    
    def __post_init__(self):
        """Veri doğrulama."""
        # Boş string'leri None'a çevir
        if self.takip_no == "":
            self.takip_no = None
        if self.mesaj == "":
            self.mesaj = None


@dataclass
class KargoDurumDTO:
    """Kargo takip durum bilgisi."""
    
    etiket_id: int
    takip_no: str
    durum: str
    aciklama: Optional[str] = None
    zaman: Optional[datetime] = None
    
    def __post_init__(self):
        """Veri doğrulama."""
        # Boş string'i None'a çevir
        if self.aciklama == "":
            self.aciklama = None