# Version: 0.1.0
# Last Update: 2024-12-15
# Module: crm
# Description: Müşteri ilişkileri modülü (crm_ajani sorumluluğu)
# Changelog:
# - İlk oluşturma
# - Alt modül yapısı eklendi

"""
SONTECHSP CRM Modülü

Bu modül müşteri ilişkileri yönetimini içerir:
- Müşteri yönetimi
- Sadakat puanı sistemi
- Müşteri segmentasyonu

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