# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.dto.urun_dto
# Description: Ürün DTO sınıfı
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Ürün DTO

Bu modül ürün veri transfer objelerini içerir.
Katmanlar arası veri aktarımı için kullanılır.
"""

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import Optional, List


@dataclass
class UrunDTO:
    """Ürün veri transfer objesi"""
    
    # Temel bilgiler
    id: Optional[int] = None
    urun_kodu: str = ""
    urun_adi: str = ""
    aciklama: Optional[str] = None
    
    # Kategori bilgileri
    kategori: Optional[str] = None
    alt_kategori: Optional[str] = None
    marka: Optional[str] = None
    
    # Birim bilgileri
    birim: str = "adet"
    
    # Fiyat bilgileri
    alis_fiyati: Optional[Decimal] = None
    satis_fiyati: Optional[Decimal] = None
    kdv_orani: Decimal = Decimal('18.00')
    
    # Stok kontrol bilgileri
    stok_takip: bool = True
    negatif_stok_izin: bool = False
    minimum_stok: Optional[Decimal] = None
    maksimum_stok: Optional[Decimal] = None
    
    # Durum bilgileri
    aktif: bool = True
    
    # Zaman damgaları
    olusturma_tarihi: Optional[datetime] = None
    guncelleme_tarihi: Optional[datetime] = None
    
    def validate(self) -> List[str]:
        """DTO doğrulama kuralları"""
        hatalar = []
        
        if not self.urun_kodu or not self.urun_kodu.strip():
            hatalar.append("Ürün kodu boş olamaz")
            
        if not self.urun_adi or not self.urun_adi.strip():
            hatalar.append("Ürün adı boş olamaz")
            
        if len(self.urun_kodu) > 50:
            hatalar.append("Ürün kodu 50 karakterden uzun olamaz")
            
        if len(self.urun_adi) > 200:
            hatalar.append("Ürün adı 200 karakterden uzun olamaz")
            
        if self.kdv_orani < 0 or self.kdv_orani > 100:
            hatalar.append("KDV oranı 0-100 arasında olmalıdır")
            
        if self.minimum_stok and self.minimum_stok < 0:
            hatalar.append("Minimum stok negatif olamaz")
            
        if self.maksimum_stok and self.maksimum_stok < 0:
            hatalar.append("Maksimum stok negatif olamaz")
            
        return hatalar