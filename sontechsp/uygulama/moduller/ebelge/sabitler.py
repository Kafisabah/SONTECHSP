# Version: 0.1.0
# Last Update: 2024-12-17
# Module: ebelge.sabitler
# Description: E-belge modülü sabit değerleri ve enum'ları
# Changelog:
# - İlk versiyon: Sabit değerler ve enum'lar tanımlandı

from enum import Enum


class BelgeTuru(str, Enum):
    """E-belge türleri"""
    EFATURA = "EFATURA"
    EARSIV = "EARSIV"
    EIRSALIYE = "EIRSALIYE"


class KaynakTuru(str, Enum):
    """Belge kaynağı türleri"""
    POS_SATIS = "POS_SATIS"
    SATIS_BELGESI = "SATIS_BELGESI"
    IADE_BELGESI = "IADE_BELGESI"


class OutboxDurumu(str, Enum):
    """Outbox kuyruk durumları"""
    BEKLIYOR = "BEKLIYOR"
    GONDERILIYOR = "GONDERILIYOR"
    GONDERILDI = "GONDERILDI"
    HATA = "HATA"
    IPTAL = "IPTAL"


# Konfigürasyon sabitleri
MAX_RETRY_COUNT = 3
DEFAULT_BATCH_SIZE = 10
DEFAULT_CURRENCY = "TRY"

# Timeout değerleri (saniye)
PROVIDER_TIMEOUT = 30
RETRY_BACKOFF_BASE = 2

# Veritabanı sabitleri
MAX_MESSAGE_LENGTH = 1000
MAX_EXTERNAL_DOC_NO_LENGTH = 100