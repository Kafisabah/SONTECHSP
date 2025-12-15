# Version: 0.1.0
# Last Update: 2024-12-15
# Module: kargo
# Description: Kargo yönetimi modülü (kargo_ajani sorumluluğu)
# Changelog:
# - İlk oluşturma
# - Alt modül yapısı eklendi

"""
SONTECHSP Kargo Modülü

Bu modül kargo işlemlerini yönetir:
- Kargo etiket oluşturma
- Kargo takip sistemi
- Kargo sağlayıcı entegrasyonları

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