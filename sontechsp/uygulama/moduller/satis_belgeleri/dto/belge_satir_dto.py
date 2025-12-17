# Version: 0.1.0
# Last Update: 2024-12-17
# Module: satis_belgeleri.dto.belge_satir_dto
# Description: Belge satır veri transfer nesnesi
# Changelog:
# - 0.1.0: İlk sürüm - BelgeSatirDTO

"""
Belge Satır DTO Sınıfı

Bu modül belge satır verilerinin transfer edilmesi için DTO sınıfını içerir.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class BelgeSatirDTO:
    """Belge satır veri transfer nesnesi"""
    
    id: int
    belge_id: int
    urun_id: int
    miktar: Decimal
    birim_fiyat: Decimal
    kdv_orani: Decimal
    satir_tutari: Decimal
    kdv_tutari: Decimal
    satir_toplami: Decimal
    sira_no: int
    
    def __init__(self, satir_model):
        """Model nesnesinden DTO oluştur"""
        self.id = satir_model.id
        self.belge_id = satir_model.belge_id
        self.urun_id = satir_model.urun_id
        self.miktar = satir_model.miktar
        self.birim_fiyat = satir_model.birim_fiyat
        self.kdv_orani = satir_model.kdv_orani
        self.satir_tutari = satir_model.satir_tutari
        self.kdv_tutari = satir_model.kdv_tutari
        self.satir_toplami = satir_model.satir_toplami
        self.sira_no = satir_model.sira_no
    
    @classmethod
    def from_model(cls, satir_model) -> 'BelgeSatirDTO':
        """Model nesnesinden DTO oluştur"""
        return cls(satir_model)
    
    def to_dict(self) -> dict:
        """DTO'yu dictionary'ye çevir"""
        return {
            'id': self.id,
            'belge_id': self.belge_id,
            'urun_id': self.urun_id,
            'miktar': float(self.miktar) if self.miktar is not None else None,
            'birim_fiyat': float(self.birim_fiyat) if self.birim_fiyat is not None else None,
            'kdv_orani': float(self.kdv_orani) if self.kdv_orani is not None else None,
            'satir_tutari': float(self.satir_tutari) if self.satir_tutari is not None else None,
            'kdv_tutari': float(self.kdv_tutari) if self.kdv_tutari is not None else None,
            'satir_toplami': float(self.satir_toplami) if self.satir_toplami is not None else None,
            'sira_no': self.sira_no
        }