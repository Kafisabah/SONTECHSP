# Version: 0.1.0
# Last Update: 2024-12-15
# Module: pos.servisler
# Description: POS modülü servis katmanı
# Changelog:
# - İlk oluşturma

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

__version__ = "0.1.0"