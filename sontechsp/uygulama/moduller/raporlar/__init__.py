# Version: 0.1.0
# Last Update: 2024-12-17
# Module: raporlar
# Description: Raporlama sistemi modülü (rapor_ajani sorumluluğu)
# Changelog:
# - İlk oluşturma
# - Alt modül yapısı eklendi
# - DTO, sabitler, sorgular, dışa aktarım modülleri eklendi

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
- dto.py: Veri transfer nesneleri
- sabitler.py: Sabitler ve enum'lar
- sorgular.py: Optimize edilmiş veritabanı sorguları
- disari_aktarim.py: Dışa aktarım işlemleri
"""

# Alt modülleri import et
from . import servisler
from . import depolar
from . import modeller
from . import dto
from . import sabitler
from . import sorgular
from . import disari_aktarim

# Ana sınıfları import et
from .servisler import RaporServisi

__version__ = "0.1.0"
__all__ = [
    "servisler", "depolar", "modeller", 
    "dto", "sabitler", "sorgular", "disari_aktarim",
    "RaporServisi"
]