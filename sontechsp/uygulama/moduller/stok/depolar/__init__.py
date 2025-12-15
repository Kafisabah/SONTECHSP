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

__version__ = "0.1.0"