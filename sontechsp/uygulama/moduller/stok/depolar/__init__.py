# Version: 0.1.0
# Last Update: 2024-12-15
# Module: stok.depolar
# Description: Stok modülü repository katmanı
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Stok Repository Katmanı

Bu katman stok modülünün veri erişim katmanını içerir:
- Ürün repository'leri
- Barkod repository'leri
- Stok hareket repository'leri
- Stok sayım repository'leri
- Transfer repository'leri

Katman kuralları:
- Servis katmanından çağrılır
- Veritabanı erişimini yönetir
- CRUD işlemlerini gerçekleştirir
- Transaction yönetimi
"""

from .arayuzler import (
    IUrunRepository,
    IBarkodRepository, 
    IStokHareketRepository,
    IStokBakiyeRepository
)
from .urun_repository import UrunRepository
from .barkod_repository import BarkodRepository
from .stok_hareket_repository import StokHareketRepository
from .stok_bakiye_repository import StokBakiyeRepository

__all__ = [
    'IUrunRepository',
    'IBarkodRepository',
    'IStokHareketRepository', 
    'IStokBakiyeRepository',
    'UrunRepository',
    'BarkodRepository',
    'StokHareketRepository',
    'StokBakiyeRepository'
]

__version__ = "0.1.0"