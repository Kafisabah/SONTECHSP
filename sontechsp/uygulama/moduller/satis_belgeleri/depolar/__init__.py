# Version: 0.2.0
# Last Update: 2024-12-16
# Module: satis_belgeleri.depolar
# Description: Satış belgeleri modülü repository katmanı
# Changelog:
# - İlk oluşturma
# - NumaraSayacDeposu eklendi

"""
SONTECHSP Satış Belgeleri Repository Katmanı

Bu katman satış belgeleri modülünün veri erişim katmanını içerir:
- Sipariş repository'leri
- İrsaliye repository'leri
- Fatura repository'leri
- Belge durum repository'leri
- Numara sayacı repository'si

Katman kuralları:
- Servis katmanından çağrılır
- Veritabanı erişimini yönetir
- Belge CRUD işlemlerini gerçekleştirir
- Belge veri bütünlüğünü sağlar
"""

from .numara_sayac_deposu import INumaraSayacDeposu, NumaraSayacDeposu
from .belge_durum_gecmisi_deposu import IBelgeDurumGecmisiDeposu, BelgeDurumGecmisiDeposu
from .belge_deposu import IBelgeDeposu, BelgeDeposu
from .belge_satir_deposu import IBelgeSatirDeposu, BelgeSatirDeposu

__version__ = "0.2.0"
__all__ = [
    'INumaraSayacDeposu',
    'NumaraSayacDeposu',
    'IBelgeDurumGecmisiDeposu',
    'BelgeDurumGecmisiDeposu',
    'IBelgeDeposu',
    'BelgeDeposu',
    'IBelgeSatirDeposu',
    'BelgeSatirDeposu'
]