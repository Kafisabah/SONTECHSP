# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.dto.stok_hareket_dto
# Description: Stok hareket DTO sınıfları
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Stok Hareket DTO

Bu modül stok hareket veri transfer objelerini içerir.
Stok hareketleri ve filtreleme için kullanılır.
"""

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from enum import Enum


class HareketTipi(Enum):
    """Stok hareket tipleri"""
    GIRIS = "GIRIS"
    CIKIS = "CIKIS"
    SAYIM = "SAYIM"
    TRANSFER = "TRANSFER"


@dataclass
class StokHareketDTO:
    """Stok hareket veri transfer objesi"""
    
    # Temel bilgiler
    id: Optional[int] = None
    urun_id: int = 0
    magaza_id: int = 0
    depo_id: Optional[int] = None
    
    # Hareket bilgileri
    hareket_tipi: str = HareketTipi.GIRIS.value
    miktar: Decimal = Decimal('0.0000')
    birim_fiyat: Optional[Decimal] = None
    toplam_tutar: Optional[Decimal] = None
    
    # Referans bilgileri
    referans_tablo: Optional[str] = None
    referans_id: Optional[int] = None
    aciklama: Optional[str] = None
    kullanici_id: Optional[int] = None
    
    # Zaman damgası
    olusturma_tarihi: Optional[datetime] = None
    
    def validate(self) -> List[str]:
        """DTO doğrulama kuralları"""
        hatalar = []
        
        if self.urun_id <= 0:
            hatalar.append("Geçerli ürün ID gereklidir")
            
        if self.magaza_id <= 0:
            hatalar.append("Geçerli mağaza ID gereklidir")
            
        if self.hareket_tipi not in [t.value for t in HareketTipi]:
            hatalar.append("Geçersiz hareket tipi")
            
        if self.miktar == 0:
            hatalar.append("Miktar sıfır olamaz")
            
        # Hareket tipi kontrolü
        if self.hareket_tipi == HareketTipi.GIRIS.value and self.miktar < 0:
            hatalar.append("Giriş hareketi pozitif miktar olmalıdır")
            
        if self.hareket_tipi == HareketTipi.CIKIS.value and self.miktar > 0:
            hatalar.append("Çıkış hareketi negatif miktar olmalıdır")
            
        return hatalar


@dataclass
class StokHareketFiltreDTO:
    """Stok hareket filtreleme DTO"""
    
    # Filtre kriterleri
    urun_id: Optional[int] = None
    magaza_id: Optional[int] = None
    depo_id: Optional[int] = None
    hareket_tipi: Optional[str] = None
    
    # Tarih aralığı
    baslangic_tarihi: Optional[datetime] = None
    bitis_tarihi: Optional[datetime] = None
    
    # Sayfalama
    sayfa: int = 1
    sayfa_boyutu: int = 50
    
    def validate(self) -> List[str]:
        """Filtre doğrulama kuralları"""
        hatalar = []
        
        if self.sayfa < 1:
            hatalar.append("Sayfa numarası 1'den küçük olamaz")
            
        if self.sayfa_boyutu < 1 or self.sayfa_boyutu > 1000:
            hatalar.append("Sayfa boyutu 1-1000 arasında olmalıdır")
            
        if (self.baslangic_tarihi and self.bitis_tarihi and 
            self.baslangic_tarihi > self.bitis_tarihi):
            hatalar.append("Başlangıç tarihi bitiş tarihinden büyük olamaz")
            
        return hatalar