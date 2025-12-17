# Version: 0.1.0
# Last Update: 2024-12-17
# Module: crm_dto
# Description: CRM modülü için veri transfer objeleri (DTO)
# Changelog:
# - İlk oluşturma: Müşteri ve puan işlemleri için DTO sınıfları

from dataclasses import dataclass
from typing import Optional

try:
    from .sabitler import ReferansTuru
except ImportError:
    from sabitler import ReferansTuru


@dataclass
class MusteriOlusturDTO:
    """Yeni müşteri oluşturma için veri transfer objesi"""
    ad: str
    soyad: str
    telefon: Optional[str] = None
    eposta: Optional[str] = None
    vergi_no: Optional[str] = None
    adres: Optional[str] = None
    aktif_mi: bool = True


@dataclass
class MusteriGuncelleDTO:
    """Müşteri güncelleme için opsiyonel alanlar"""
    ad: Optional[str] = None
    soyad: Optional[str] = None
    telefon: Optional[str] = None
    eposta: Optional[str] = None
    vergi_no: Optional[str] = None
    adres: Optional[str] = None
    aktif_mi: Optional[bool] = None


@dataclass
class PuanIslemDTO:
    """Puan işlemleri için veri transfer objesi"""
    musteri_id: int
    puan: int
    aciklama: Optional[str] = None
    referans_turu: Optional[ReferansTuru] = None
    referans_id: Optional[int] = None


@dataclass
class MusteriAraDTO:
    """Müşteri arama kriterleri için veri transfer objesi"""
    ad: Optional[str] = None
    soyad: Optional[str] = None
    telefon: Optional[str] = None
    eposta: Optional[str] = None
    aktif_mi: Optional[bool] = None