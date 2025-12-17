# Version: 0.1.0
# Last Update: 2024-12-17
# Module: satis_belgeleri.dto.belge_ozet_dto
# Description: Belge özet veri transfer nesnesi
# Changelog:
# - 0.1.0: İlk sürüm - BelgeOzetDTO

"""
Belge Özet DTO Sınıfı

Bu modül belge özet verilerinin transfer edilmesi için DTO sınıfını içerir.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from ..modeller import BelgeTuru, BelgeDurumu


@dataclass
class BelgeOzetDTO:
    """Belge özet veri transfer nesnesi - liste görünümü için"""
    
    id: int
    belge_numarasi: str
    belge_turu: BelgeTuru
    belge_durumu: BelgeDurumu
    magaza_id: int
    musteri_id: Optional[int]
    genel_toplam: Decimal
    olusturma_tarihi: datetime
    olusturan_kullanici_id: int
    
    def __init__(self, belge_model):
        """Model nesnesinden özet DTO oluştur"""
        self.id = belge_model.id
        self.belge_numarasi = belge_model.belge_numarasi
        self.belge_turu = belge_model.belge_turu
        self.belge_durumu = belge_model.belge_durumu
        self.magaza_id = belge_model.magaza_id
        self.musteri_id = belge_model.musteri_id
        self.genel_toplam = belge_model.genel_toplam
        self.olusturma_tarihi = belge_model.olusturma_tarihi
        self.olusturan_kullanici_id = belge_model.olusturan_kullanici_id
    
    @classmethod
    def from_model(cls, belge_model) -> 'BelgeOzetDTO':
        """Model nesnesinden özet DTO oluştur"""
        return cls(belge_model)
    
    def to_dict(self) -> dict:
        """DTO'yu dictionary'ye çevir"""
        return {
            'id': self.id,
            'belge_numarasi': self.belge_numarasi,
            'belge_turu': self.belge_turu.value if self.belge_turu else None,
            'belge_durumu': self.belge_durumu.value if self.belge_durumu else None,
            'magaza_id': self.magaza_id,
            'musteri_id': self.musteri_id,
            'genel_toplam': float(self.genel_toplam) if self.genel_toplam else None,
            'olusturma_tarihi': self.olusturma_tarihi.isoformat() if self.olusturma_tarihi else None,
            'olusturan_kullanici_id': self.olusturan_kullanici_id
        }