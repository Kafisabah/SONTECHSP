# Version: 0.1.0
# Last Update: 2024-12-17
# Module: raporlar.servisler
# Description: Raporlar modülü servis katmanı
# Changelog:
# - İlk oluşturma
# - RaporServisi eklendi

"""
SONTECHSP Raporlar Servis Katmanı

Bu katman raporlar modülünün iş mantığını içerir:
- Satış rapor servisleri
- Stok rapor servisleri
- Mali rapor servisleri
- Analitik rapor servisleri
- Rapor export servisleri (CSV/PDF)

Katman kuralları:
- UI katmanından çağrılır
- Repository katmanını kullanır
- Rapor iş mantığını uygular
- Export formatlarını yönetir
"""

from .rapor_servisi import RaporServisi

__version__ = "0.1.0"
__all__ = ["RaporServisi"]