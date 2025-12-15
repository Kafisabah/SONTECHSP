# Version: 0.1.0
# Last Update: 2024-12-15
# Module: ebelge.depolar
# Description: E-belge modülü repository katmanı
# Changelog:
# - İlk oluşturma

"""
SONTECHSP E-belge Repository Katmanı

Bu katman e-belge modülünün veri erişim katmanını içerir:
- E-belge outbox repository'leri
- E-belge durum repository'leri
- Retry kuyruk repository'leri
- Sağlayıcı log repository'leri

Katman kuralları:
- Servis katmanından çağrılır
- Veritabanı erişimini yönetir
- Kuyruk verilerini yönetir
- Durum takibini gerçekleştirir
"""

__version__ = "0.1.0"