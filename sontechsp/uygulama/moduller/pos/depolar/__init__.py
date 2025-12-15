# Version: 0.1.0
# Last Update: 2024-12-15
# Module: pos.depolar
# Description: POS modülü repository katmanı
# Changelog:
# - İlk oluşturma

"""
SONTECHSP POS Repository Katmanı

Bu katman POS modülünün veri erişim katmanını içerir:
- Sepet repository'leri
- Ödeme repository'leri
- İade repository'leri
- Bekletme repository'leri
- Fiş repository'leri
- Offline kuyruk repository'leri

Katman kuralları:
- Servis katmanından çağrılır
- PostgreSQL ve SQLite erişimi
- Transaction yönetimi
- Offline kuyruk yönetimi
"""

__version__ = "0.1.0"