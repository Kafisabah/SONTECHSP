# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.dto
# Description: Stok modülü DTO sınıfları
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Stok DTO Sınıfları

Bu modül stok modülünün veri transfer objelerini içerir:
- UrunDTO: Ürün veri transfer objesi
- BarkodDTO: Barkod veri transfer objesi
- StokHareketDTO: Stok hareket veri transfer objesi
- StokRaporDTO: Stok rapor veri transfer objesi
"""

from .urun_dto import UrunDTO
from .barkod_dto import BarkodDTO
from .stok_hareket_dto import StokHareketDTO, StokHareketFiltreDTO
from .stok_rapor_dto import StokDurumRaporDTO, StokHareketRaporDTO, StokRaporFiltreDTO
from .stok_bakiye_dto import StokBakiyeDTO

__all__ = [
    'UrunDTO',
    'BarkodDTO', 
    'StokHareketDTO',
    'StokHareketFiltreDTO',
    'StokBakiyeDTO',
    'StokDurumRaporDTO',
    'StokHareketRaporDTO',
    'StokRaporFiltreDTO'
]

__version__ = "0.1.0"