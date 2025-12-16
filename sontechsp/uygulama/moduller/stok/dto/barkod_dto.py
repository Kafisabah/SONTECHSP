# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.dto.barkod_dto
# Description: Barkod DTO sınıfı
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Barkod DTO

Bu modül barkod veri transfer objelerini içerir.
Barkod yönetimi için kullanılır.
"""

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import Optional, List


@dataclass
class BarkodDTO:
    """Barkod veri transfer objesi"""
    
    # Temel bilgiler
    id: Optional[int] = None
    urun_id: int = 0
    barkod: str = ""
    barkod_tipi: str = "EAN13"
    
    # Birim bilgileri
    birim: str = "adet"
    carpan: Decimal = Decimal('1.0000')
    
    # Durum bilgileri
    aktif: bool = True
    ana_barkod: bool = False
    
    # Zaman damgaları
    olusturma_tarihi: Optional[datetime] = None
    guncelleme_tarihi: Optional[datetime] = None
    
    def validate(self) -> List[str]:
        """DTO doğrulama kuralları"""
        hatalar = []
        
        if not self.barkod or not self.barkod.strip():
            hatalar.append("Barkod boş olamaz")
            
        if len(self.barkod) > 50:
            hatalar.append("Barkod 50 karakterden uzun olamaz")
            
        if len(self.barkod) < 8:
            hatalar.append("Barkod en az 8 karakter olmalıdır")
            
        if self.urun_id <= 0:
            hatalar.append("Geçerli ürün ID gereklidir")
            
        if self.carpan <= 0:
            hatalar.append("Çarpan pozitif olmalıdır")
            
        # Barkod format kontrolü (sadece rakam)
        if not self.barkod.isdigit():
            hatalar.append("Barkod sadece rakamlardan oluşmalıdır")
            
        return hatalar