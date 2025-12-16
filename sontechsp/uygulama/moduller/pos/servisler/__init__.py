# Version: 0.1.0
# Last Update: 2025-12-16
# Module: pos.servisler
# Description: POS modülü servis katmanı
# Changelog:
# - İlk oluşturma
# - SepetService eklendi

"""
SONTECHSP POS Servis Katmanı

Bu katman POS modülünün iş mantığını içerir:
- Sepet servisleri
- Ödeme servisleri
- İade servisleri
- Bekletme servisleri
- Fiş servisleri
- Offline kuyruk servisleri

Katman kuralları:
- UI katmanından çağrılır
- Repository katmanını kullanır
- İş kurallarını uygular
- Offline/online durumları yönetir
"""

from .sepet_service import SepetService, BarkodHatasi, StokHatasi
from .odeme_service import OdemeService, OdemeHatasi
from .iade_service import IadeService
from .fis_service import FisService

__version__ = "0.1.0"
__all__ = [
    'SepetService',
    'BarkodHatasi', 
    'StokHatasi',
    'OdemeService',
    'OdemeHatasi',
    'IadeService',
    'FisService'
]