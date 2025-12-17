# Version: 0.1.0
# Last Update: 2024-12-17
# Module: raporlar.dto
# Description: Raporlama modülü veri transfer nesneleri
# Changelog:
# - İlk oluşturma
# - TarihAraligiDTO, SatisOzetiDTO, UrunPerformansDTO, KritikStokDTO eklendi
# - RaporSatirDTO, DisariAktarDTO eklendi

"""
SONTECHSP Raporlar DTO Katmanı

Bu modül raporlama sisteminin veri transfer nesnelerini içerir:
- Tarih aralığı DTO'su
- Satış özeti DTO'su
- Ürün performans DTO'su
- Kritik stok DTO'su
- Rapor satır DTO'su
- Dışa aktarım DTO'su

Tüm DTO'lar güçlü tipli ve doğrulama kuralları içerir.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any, Optional


class RaporTuru(Enum):
    """Rapor türleri enum'u"""
    SATIS_OZETI = "satis_ozeti"
    KRITIK_STOK = "kritik_stok"
    EN_COK_SATAN = "en_cok_satan"
    KARLILIK = "karlilik"


class DisariAktarFormat(Enum):
    """Dışa aktarım formatları enum'u"""
    CSV = "csv"
    PDF = "pdf"


@dataclass
class TarihAraligiDTO:
    """Tarih aralığı veri transfer nesnesi"""
    baslangic_tarihi: date
    bitis_tarihi: date
    
    def __post_init__(self):
        """Tarih aralığı doğrulaması"""
        if self.baslangic_tarihi > self.bitis_tarihi:
            raise ValueError("Başlangıç tarihi bitiş tarihinden büyük olamaz")


@dataclass
class SatisOzetiDTO:
    """Satış özeti veri transfer nesnesi"""
    magaza_id: int
    brut_satis: Decimal
    indirim_toplam: Decimal
    net_satis: Decimal
    satis_adedi: int
    iade_toplam: Decimal = Decimal('0')
    
    def __post_init__(self):
        """Satış özeti doğrulaması"""
        if self.magaza_id <= 0:
            raise ValueError("Mağaza ID pozitif olmalıdır")
        if self.satis_adedi < 0:
            raise ValueError("Satış adedi negatif olamaz")


@dataclass
class UrunPerformansDTO:
    """Ürün performans veri transfer nesnesi"""
    urun_id: int
    urun_adi: str
    miktar_toplam: int
    ciro_toplam: Decimal
    
    def __post_init__(self):
        """Ürün performans doğrulaması"""
        if self.urun_id <= 0:
            raise ValueError("Ürün ID pozitif olmalıdır")
        if not self.urun_adi.strip():
            raise ValueError("Ürün adı boş olamaz")
        if self.miktar_toplam < 0:
            raise ValueError("Miktar toplamı negatif olamaz")


@dataclass
class KritikStokDTO:
    """Kritik stok veri transfer nesnesi"""
    urun_id: int
    urun_adi: str
    depo_id: int
    miktar: int
    kritik_seviye: int
    
    def __post_init__(self):
        """Kritik stok doğrulaması"""
        if self.urun_id <= 0:
            raise ValueError("Ürün ID pozitif olmalıdır")
        if self.depo_id <= 0:
            raise ValueError("Depo ID pozitif olmalıdır")
        if not self.urun_adi.strip():
            raise ValueError("Ürün adı boş olamaz")


@dataclass
class RaporSatirDTO:
    """Genel rapor satır veri transfer nesnesi"""
    id: int
    ad: str
    deger1: Optional[Any] = None
    deger2: Optional[Any] = None
    deger3: Optional[Any] = None
    aciklama: Optional[str] = None


@dataclass
class DisariAktarDTO:
    """Dışa aktarım parametreleri veri transfer nesnesi"""
    format: DisariAktarFormat
    dosya_adi: Optional[str] = None
    klasor_yolu: Optional[str] = None
    baslik: Optional[str] = None
    
    def __post_init__(self):
        """Dışa aktarım doğrulaması"""
        if self.dosya_adi and not self.dosya_adi.strip():
            raise ValueError("Dosya adı boş olamaz")