# Version: 0.2.0
# Last Update: 2024-12-16
# Module: satis_belgeleri.servisler
# Description: Satış belgeleri modülü servis katmanı
# Changelog:
# - İlk oluşturma
# - NumaraServisi eklendi

"""
SONTECHSP Satış Belgeleri Servis Katmanı

Bu katman satış belgeleri modülünün iş mantığını içerir:
- Sipariş servisleri
- İrsaliye servisleri
- Fatura servisleri
- Belge durum akış servisleri
- Numara üretim servisi

Katman kuralları:
- UI katmanından çağrılır
- Repository katmanını kullanır
- Belge iş süreçlerini yönetir
- Durum geçişlerini kontrol eder
"""

from .numara_servisi import NumaraServisi
from .durum_akis_servisi import DurumAkisServisi
from .dogrulama_servisi import DogrulamaServisi
from .belge_servisi import BelgeServisi, SiparisBilgileriDTO, BelgeDTO
from .sorgu_servisi import SorguServisi

__version__ = "0.4.0"
__all__ = [
    'NumaraServisi',
    'DurumAkisServisi',
    'DogrulamaServisi',
    'BelgeServisi',
    'SiparisBilgileriDTO',
    'BelgeDTO',
    'SorguServisi'
]