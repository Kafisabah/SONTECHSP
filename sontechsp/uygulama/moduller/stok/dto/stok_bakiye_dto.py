# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.dto.stok_bakiye_dto
# Description: Stok bakiye DTO sınıfları
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Stok Bakiye DTO

Bu modül stok bakiye veri transfer objelerini içerir.
Stok bakiye yönetimi için kullanılır.
"""

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import Optional, List


@dataclass
class StokBakiyeDTO:
    """Stok bakiye veri transfer objesi"""
    
    # Temel bilgiler
    id: Optional[int] = None
    urun_id: int = 0
    magaza_id: int = 0
    depo_id: Optional[int] = None
    
    # Stok bilgileri
    miktar: Decimal = Decimal('0.0000')
    rezerve_miktar: Decimal = Decimal('0.0000')
    kullanilabilir_miktar: Decimal = Decimal('0.0000')
    
    # Maliyet bilgileri
    ortalama_maliyet: Optional[Decimal] = None
    son_alis_fiyati: Optional[Decimal] = None
    
    # Zaman damgası
    son_hareket_tarihi: Optional[datetime] = None
    olusturma_tarihi: Optional[datetime] = None
    guncelleme_tarihi: Optional[datetime] = None
    
    def validate(self) -> List[str]:
        """DTO doğrulama kuralları"""
        hatalar = []
        
        if self.urun_id <= 0:
            hatalar.append("Geçerli ürün ID gereklidir")
            
        if self.magaza_id <= 0:
            hatalar.append("Geçerli mağaza ID gereklidir")
            
        if self.rezerve_miktar < 0:
            hatalar.append("Rezerve miktar negatif olamaz")
            
        if self.kullanilabilir_miktar != (self.miktar - self.rezerve_miktar):
            hatalar.append("Kullanılabilir miktar hesaplaması hatalı")
            
        return hatalar
    
    def hesapla_kullanilabilir_miktar(self) -> None:
        """Kullanılabilir miktarı hesaplar"""
        self.kullanilabilir_miktar = self.miktar - self.rezerve_miktar