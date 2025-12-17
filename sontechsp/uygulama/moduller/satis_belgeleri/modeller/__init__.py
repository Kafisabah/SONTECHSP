# Version: 0.2.0
# Last Update: 2024-12-16
# Module: satis_belgeleri.modeller
# Description: Satış belgeleri modülü veri modelleri
# Changelog:
# - İlk oluşturma
# - İş modelleri eklendi

"""
SONTECHSP Satış Belgeleri Veri Modelleri

Bu katman satış belgeleri modülünün iş modellerini içerir:
- SatisBelgesi: Ana belge modeli
- BelgeSatiri: Belge satır modeli
- NumaraSayaci: Numara üretim modeli
- BelgeTuru, BelgeDurumu: Enum modelleri

Katman kuralları:
- İş kuralları ve doğrulama mantığı
- Veritabanı modellerinden bağımsız
- Domain-driven design prensipleri
"""

from .satis_belgesi import SatisBelgesi, BelgeTuru, BelgeDurumu
from .belge_satiri import BelgeSatiri
from .numara_sayaci import NumaraSayaci
from .belge_durum_gecmisi import BelgeDurumGecmisi

__version__ = "0.2.0"
__all__ = [
    'SatisBelgesi',
    'BelgeSatiri', 
    'NumaraSayaci',
    'BelgeDurumGecmisi',
    'BelgeTuru',
    'BelgeDurumu'
]