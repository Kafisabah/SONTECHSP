# Version: 0.1.0
# Last Update: 2024-12-17
# Module: satis_belgeleri.dto.belge_dto
# Description: Belge veri transfer nesnesi
# Changelog:
# - 0.1.0: İlk sürüm - BelgeDTO ve BelgeDurumGecmisiDTO

"""
Belge DTO Sınıfları

Bu modül belge verilerinin transfer edilmesi için DTO sınıflarını içerir.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from ..modeller import BelgeTuru, BelgeDurumu


@dataclass
class BelgeDurumGecmisiDTO:
    """Belge durum geçmişi DTO"""
    
    id: int
    belge_id: int
    eski_durum: Optional[BelgeDurumu]
    yeni_durum: BelgeDurumu
    degisiklik_tarihi: datetime
    degistiren_kullanici_id: int
    aciklama: Optional[str] = None


@dataclass
class BelgeDTO:
    """Belge veri transfer nesnesi"""
    
    id: int
    belge_numarasi: str
    belge_turu: BelgeTuru
    belge_durumu: BelgeDurumu
    magaza_id: int
    musteri_id: Optional[int]
    toplam_tutar: Decimal
    kdv_tutari: Decimal
    genel_toplam: Decimal
    olusturma_tarihi: datetime
    guncelleme_tarihi: datetime
    olusturan_kullanici_id: int
    kaynak_belge_id: Optional[int] = None
    kaynak_belge_turu: Optional[str] = None
    iptal_nedeni: Optional[str] = None
    
    def __init__(self, belge_model):
        """Model nesnesinden DTO oluştur"""
        self.id = belge_model.id
        self.belge_numarasi = belge_model.belge_numarasi
        self.belge_turu = belge_model.belge_turu
        self.belge_durumu = belge_model.belge_durumu
        self.magaza_id = belge_model.magaza_id
        self.musteri_id = belge_model.musteri_id
        self.toplam_tutar = belge_model.toplam_tutar
        self.kdv_tutari = belge_model.kdv_tutari
        self.genel_toplam = belge_model.genel_toplam
        self.olusturma_tarihi = belge_model.olusturma_tarihi
        self.guncelleme_tarihi = belge_model.guncelleme_tarihi
        self.olusturan_kullanici_id = belge_model.olusturan_kullanici_id
        self.kaynak_belge_id = belge_model.kaynak_belge_id
        self.kaynak_belge_turu = belge_model.kaynak_belge_turu
        self.iptal_nedeni = belge_model.iptal_nedeni
    
    @classmethod
    def from_model(cls, belge_model) -> 'BelgeDTO':
        """Model nesnesinden DTO oluştur"""
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
            'toplam_tutar': float(self.toplam_tutar) if self.toplam_tutar else None,
            'kdv_tutari': float(self.kdv_tutari) if self.kdv_tutari else None,
            'genel_toplam': float(self.genel_toplam) if self.genel_toplam else None,
            'olusturma_tarihi': self.olusturma_tarihi.isoformat() if self.olusturma_tarihi else None,
            'guncelleme_tarihi': self.guncelleme_tarihi.isoformat() if self.guncelleme_tarihi else None,
            'olusturan_kullanici_id': self.olusturan_kullanici_id,
            'kaynak_belge_id': self.kaynak_belge_id,
            'kaynak_belge_turu': self.kaynak_belge_turu,
            'iptal_nedeni': self.iptal_nedeni
        }