# Version: 0.1.0
# Last Update: 2025-12-15
# Module: stok.servisler
# Description: Stok modülü servis katmanı
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Stok Servis Katmanı

Bu katman stok modülünün iş mantığını içerir:
- Ürün servisleri
- Barkod servisleri
- Stok hareket servisleri
- Stok sayım servisleri
- Transfer servisleri
- Negatif stok eşik servisleri

Katman kuralları:
- UI katmanından çağrılır
- Repository katmanını kullanır
- İş kurallarını uygular
"""

from .arayuzler import (
    IUrunService,
    IBarkodService,
    IStokHareketService,
    INegatifStokKontrol
)
from .urun_service import UrunService
from .barkod_service import BarkodService
from .negatif_stok_kontrol import NegatifStokKontrol
from .stok_hareket_service import StokHareketService
from .stok_yonetim_service import StokYonetimService

__all__ = [
    'IUrunService',
    'IBarkodService', 
    'IStokHareketService',
    'INegatifStokKontrol',
    'UrunService',
    'BarkodService',
    'NegatifStokKontrol',
    'StokHareketService',
    'StokYonetimService'
]

__version__ = "0.1.0"