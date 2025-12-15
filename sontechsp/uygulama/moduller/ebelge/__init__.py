# Version: 0.1.0
# Last Update: 2024-12-15
# Module: ebelge
# Description: E-belge sistemi modülü (ebelge_ajani sorumluluğu)
# Changelog:
# - İlk oluşturma
# - Alt modül yapısı eklendi

"""
SONTECHSP E-belge Modülü

Bu modül e-belge işlemlerini yönetir:
- E-fatura sistemi
- E-arşiv işlemleri
- E-irsaliye yönetimi
- Outbox kuyruk sistemi
- Durum senkronizasyonu
- Retry mekanizması

Katmanlı yapı:
- servisler/: İş mantığı katmanı
- depolar/: Repository katmanı
- modeller/: Veri modelleri katmanı
"""

# Alt modülleri import et
from . import servisler
from . import depolar
from . import modeller

__version__ = "0.1.0"
__all__ = ["servisler", "depolar", "modeller"]