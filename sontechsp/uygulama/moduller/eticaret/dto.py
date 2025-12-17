# Version: 0.1.0
# Last Update: 2024-12-17
# Module: eticaret.dto
# Description: E-ticaret entegrasyonu için veri transfer nesneleri
# Changelog:
# - İlk oluşturma
# - MagazaHesabiOlusturDTO, SiparisDTO ve diğer DTO'lar eklendi

"""
E-ticaret entegrasyonu için veri transfer nesneleri (DTO).
Katmanlar arası veri transferi için tür güvenliği ve doğrulama sağlar.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any

from .sabitler import VARSAYILAN_PARA_BIRIMI


@dataclass
class MagazaHesabiOlusturDTO:
    """Yeni mağaza hesabı oluşturma için DTO"""
    platform: str
    magaza_adi: str
    kimlik_json: Dict[str, Any]
    aktif_mi: bool = True
    ayar_json: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.platform:
            raise ValueError("Platform boş olamaz")
        if not self.magaza_adi:
            raise ValueError("Mağaza adı boş olamaz")
        if not self.kimlik_json:
            raise ValueError("Kimlik bilgileri boş olamaz")


@dataclass
class MagazaHesabiGuncelleDTO:
    """Mağaza hesabı güncelleme için DTO"""
    magaza_adi: Optional[str] = None
    kimlik_json: Optional[Dict[str, Any]] = None
    ayar_json: Optional[Dict[str, Any]] = None
    aktif_mi: Optional[bool] = None


@dataclass
class SiparisDTO:
    """Sipariş verisi için DTO"""
    platform: str
    dis_siparis_no: str
    magaza_hesabi_id: int
    siparis_zamani: datetime
    musteri_ad_soyad: str
    toplam_tutar: Decimal
    durum: str
    ham_veri_json: Dict[str, Any]
    para_birimi: str = VARSAYILAN_PARA_BIRIMI
    kargo_tasiyici: Optional[str] = None
    takip_no: Optional[str] = None
    
    def __post_init__(self):
        if not self.platform:
            raise ValueError("Platform boş olamaz")
        if not self.dis_siparis_no:
            raise ValueError("Dış sipariş numarası boş olamaz")
        if not self.musteri_ad_soyad:
            raise ValueError("Müşteri adı soyadı boş olamaz")
        if self.toplam_tutar < 0:
            raise ValueError("Toplam tutar negatif olamaz")


@dataclass
class StokGuncelleDTO:
    """Stok güncelleme için DTO"""
    urun_id: int
    depo_id: int
    miktar: int
    
    def __post_init__(self):
        if self.urun_id <= 0:
            raise ValueError("Ürün ID pozitif olmalıdır")
        if self.depo_id <= 0:
            raise ValueError("Depo ID pozitif olmalıdır")
        if self.miktar < 0:
            raise ValueError("Miktar negatif olamaz")


@dataclass
class FiyatGuncelleDTO:
    """Fiyat güncelleme için DTO"""
    urun_id: int
    fiyat: Decimal
    para_birimi: str = VARSAYILAN_PARA_BIRIMI
    
    def __post_init__(self):
        if self.urun_id <= 0:
            raise ValueError("Ürün ID pozitif olmalıdır")
        if self.fiyat < 0:
            raise ValueError("Fiyat negatif olamaz")


@dataclass
class JobDTO:
    """İş kuyruğu için DTO"""
    magaza_hesabi_id: int
    tur: str
    payload_json: Dict[str, Any]
    durum: str = "BEKLIYOR"
    hata_mesaji: Optional[str] = None
    deneme_sayisi: int = 0
    sonraki_deneme: Optional[datetime] = None
    
    def __post_init__(self):
        if self.magaza_hesabi_id <= 0:
            raise ValueError("Mağaza hesabı ID pozitif olmalıdır")
        if not self.tur:
            raise ValueError("İş türü boş olamaz")
        if not self.payload_json:
            raise ValueError("Payload boş olamaz")


@dataclass
class JobSonucDTO:
    """İş sonucu için DTO"""
    job_id: int
    basarili: bool
    hata_mesaji: Optional[str] = None
    sonuc_verisi: Optional[Dict[str, Any]] = None