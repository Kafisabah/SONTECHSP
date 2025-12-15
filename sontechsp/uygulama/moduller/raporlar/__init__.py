# Version: 0.1.0
# Last Update: 2024-12-15
# Module: raporlar
# Description: Raporlama sistemi modülü (rapor_ajani sorumluluğu)
# Changelog:
# - İlk oluşturma
# - Alt modül yapısı eklendi

"""
SONTECHSP Raporlar Modülü

Bu modül raporlama işlemlerini yönetir:
- Satış raporları
- Stok raporları
- Mali raporlar
- Analitik raporlar
- Rapor export işlemleri (CSV/PDF)

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