# Version: 0.1.0
# Last Update: 2024-12-15
# Module: satis_belgeleri.depolar
# Description: Satış belgeleri modülü repository katmanı
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Satış Belgeleri Repository Katmanı

Bu katman satış belgeleri modülünün veri erişim katmanını içerir:
- Sipariş repository'leri
- İrsaliye repository'leri
- Fatura repository'leri
- Belge durum repository'leri

Katman kuralları:
- Servis katmanından çağrılır
- Veritabanı erişimini yönetir
- Belge CRUD işlemlerini gerçekleştirir
- Belge veri bütünlüğünü sağlar
"""

__version__ = "0.1.0"