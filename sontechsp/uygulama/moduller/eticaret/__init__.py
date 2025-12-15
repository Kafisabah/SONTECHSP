# Version: 0.1.0
# Last Update: 2024-12-15
# Module: eticaret
# Description: E-ticaret entegrasyonu modülü (eticaret_ajani sorumluluğu)
# Changelog:
# - İlk oluşturma
# - Alt modül yapısı eklendi

"""
SONTECHSP E-ticaret Modülü

Bu modül e-ticaret entegrasyonlarını yönetir:
- Pazaryeri entegrasyonları
- E-ticaret sitesi bağlantıları
- Sipariş senkronizasyonu
- Ürün aktarımı

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