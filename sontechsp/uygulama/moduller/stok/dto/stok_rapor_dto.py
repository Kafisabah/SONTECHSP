# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.dto.stok_rapor_dto
# Description: Stok rapor DTO sınıfları
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Stok Rapor DTO

Bu modül stok raporlama veri transfer objelerini içerir.
Rapor filtreleme ve sonuçları için kullanılır.
"""

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import Optional, List


@dataclass
class StokDurumRaporDTO:
    """Stok durum raporu DTO"""
    
    # Ürün bilgileri
    urun_id: int = 0
    urun_kodu: str = ""
    urun_adi: str = ""
    birim: str = ""
    
    # Stok bilgileri
    toplam_miktar: Decimal = Decimal('0.0000')
    rezerve_miktar: Decimal = Decimal('0.0000')
    kullanilabilir_miktar: Decimal = Decimal('0.0000')
    
    # Maliyet bilgileri
    ortalama_maliyet: Optional[Decimal] = None
    toplam_deger: Optional[Decimal] = None
    
    # Lokasyon bilgileri
    magaza_id: int = 0
    magaza_adi: str = ""
    depo_id: Optional[int] = None
    depo_adi: Optional[str] = None
    
    # Kritik stok bilgisi
    minimum_stok: Optional[Decimal] = None
    kritik_seviye: bool = False


@dataclass
class StokHareketRaporDTO:
    """Stok hareket raporu DTO"""
    
    # Hareket bilgileri
    hareket_id: int = 0
    hareket_tarihi: datetime = datetime.now()
    hareket_tipi: str = ""
    
    # Ürün bilgileri
    urun_kodu: str = ""
    urun_adi: str = ""
    
    # Miktar bilgileri
    miktar: Decimal = Decimal('0.0000')
    birim_fiyat: Optional[Decimal] = None
    toplam_tutar: Optional[Decimal] = None
    
    # Lokasyon bilgileri
    magaza_adi: str = ""
    depo_adi: Optional[str] = None
    
    # Açıklama
    aciklama: Optional[str] = None


@dataclass
class StokRaporFiltreDTO:
    """Stok rapor filtreleme DTO"""
    
    # Ürün filtreleri
    urun_id: Optional[int] = None
    kategori: Optional[str] = None
    marka: Optional[str] = None
    
    # Lokasyon filtreleri
    magaza_id: Optional[int] = None
    depo_id: Optional[int] = None
    
    # Tarih aralığı
    baslangic_tarihi: Optional[datetime] = None
    bitis_tarihi: Optional[datetime] = None
    
    # Stok durumu filtreleri
    sadece_kritik_stok: bool = False
    sadece_sifir_stok: bool = False
    
    def validate(self) -> List[str]:
        """Filtre doğrulama kuralları"""
        hatalar = []
        
        if (self.baslangic_tarihi and self.bitis_tarihi and 
            self.baslangic_tarihi > self.bitis_tarihi):
            hatalar.append("Başlangıç tarihi bitiş tarihinden büyük olamaz")
            
        return hatalar