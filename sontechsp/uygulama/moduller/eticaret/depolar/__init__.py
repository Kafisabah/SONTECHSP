# Version: 0.1.0
# Last Update: 2024-12-15
# Module: eticaret.depolar
# Description: E-ticaret modülü repository katmanı
# Changelog:
# - İlk oluşturma

"""
SONTECHSP E-ticaret Repository Katmanı

Bu katman e-ticaret modülünün veri erişim katmanını içerir:
- Pazaryeri hesap repository'leri
- E-ticaret sipariş repository'leri
- Ürün aktarım repository'leri
- Senkronizasyon log repository'leri

Katman kuralları:
- Servis katmanından çağrılır
- Veritabanı erişimini yönetir
- Entegrasyon verilerini yönetir
- Senkronizasyon durumlarını takip eder
"""

__version__ = "0.1.0"