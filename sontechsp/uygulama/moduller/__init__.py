# Version: 0.1.0
# Last Update: 2024-12-15
# Module: moduller
# Description: SONTECHSP iş modülleri ana dizini
# Changelog:
# - İlk oluşturma
# - Alt modül yapıları tamamlandı

"""
SONTECHSP İş Modülleri

Bu dizin ajan bazlı iş modüllerini içerir:
- stok: Stok yönetimi (stok_ajani)
- pos: Hızlı satış sistemi (pos_ajani)
- crm: Müşteri ilişkileri (crm_ajani)
- satis_belgeleri: Satış belgeleri (satis_belge_ajani)
- eticaret: E-ticaret entegrasyonu (eticaret_ajani)
- ebelge: E-belge sistemi (ebelge_ajani)
- kargo: Kargo yönetimi (kargo_ajani)
- raporlar: Raporlama sistemi (rapor_ajani)

Her modül katmanlı yapıya sahiptir:
- servisler/: İş mantığı katmanı
- depolar/: Repository katmanı  
- modeller/: Veri modelleri katmanı

Katman bağımlılık kuralları:
UI -> Servisler -> Depolar -> Veritabanı
"""

# Tüm iş modüllerini import et
from . import stok
from . import pos
from . import crm
from . import satis_belgeleri
from . import eticaret
from . import ebelge
from . import kargo
from . import raporlar

__version__ = "0.1.0"
__all__ = [
    "stok", 
    "pos", 
    "crm", 
    "satis_belgeleri", 
    "eticaret", 
    "ebelge", 
    "kargo", 
    "raporlar"
]