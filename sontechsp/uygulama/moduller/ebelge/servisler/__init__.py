# Version: 0.1.0
# Last Update: 2024-12-15
# Module: ebelge.servisler
# Description: E-belge modülü servis katmanı
# Changelog:
# - İlk oluşturma

"""
SONTECHSP E-belge Servis Katmanı

Bu katman e-belge modülünün iş mantığını içerir:
- E-fatura servisleri
- E-arşiv servisleri
- E-irsaliye servisleri
- Outbox kuyruk servisleri
- Durum senkronizasyon servisleri
- Retry mekanizma servisleri

Katman kuralları:
- UI katmanından çağrılır
- Repository katmanını kullanır
- E-belge iş süreçlerini yönetir
- Kuyruk ve retry mantığını uygular
"""

__version__ = "0.1.0"