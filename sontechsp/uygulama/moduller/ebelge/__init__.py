# Version: 0.1.0
# Last Update: 2024-12-17
# Module: ebelge
# Description: E-belge sistemi modülü (ebelge_ajani sorumluluğu)
# Changelog:
# - İlk oluşturma
# - Alt modül yapısı eklendi
# - DTO, sabitler ve hata sınıfları eklendi

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
- dto: Veri transfer nesneleri
- sabitler: Enum ve sabit değerler
- hatalar: Özel hata sınıfları
"""

# Ana bileşenleri import et
from .dto import (
    EBelgeOlusturDTO,
    EBelgeGonderDTO,
    EBelgeSonucDTO,
    EBelgeDurumSorguDTO
)
from .sabitler import (
    BelgeTuru,
    KaynakTuru,
    OutboxDurumu,
    MAX_RETRY_COUNT,
    DEFAULT_BATCH_SIZE,
    DEFAULT_CURRENCY
)
from .hatalar import (
    EntegrasyonHatasi,
    BaglantiHatasi,
    DogrulamaHatasi,
    KonfigurasyonHatasi,
    JSONHatasi
)

# Sağlayıcı bileşenleri import et
from .saglayici_arayuzu import SaglayiciArayuzu
from .saglayici_fabrikasi import SaglayiciFabrikasi, DummySaglayici

# Alt modülleri import et
from . import servisler
from . import depolar
from . import modeller

__version__ = "0.1.0"
__all__ = [
    # DTO sınıfları
    "EBelgeOlusturDTO",
    "EBelgeGonderDTO", 
    "EBelgeSonucDTO",
    "EBelgeDurumSorguDTO",
    # Enum ve sabitler
    "BelgeTuru",
    "KaynakTuru",
    "OutboxDurumu",
    "MAX_RETRY_COUNT",
    "DEFAULT_BATCH_SIZE",
    "DEFAULT_CURRENCY",
    # Hata sınıfları
    "EntegrasyonHatasi",
    "BaglantiHatasi",
    "DogrulamaHatasi",
    "KonfigurasyonHatasi",
    "JSONHatasi",
    # Sağlayıcı bileşenleri
    "SaglayiciArayuzu",
    "SaglayiciFabrikasi",
    "DummySaglayici",
    # Alt modüller
    "servisler",
    "depolar",
    "modeller"
]