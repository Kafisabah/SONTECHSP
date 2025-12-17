# Version: 0.1.0
# Last Update: 2024-12-17
# Module: crm_sabitler
# Description: CRM modülü için sabit değerler ve enum tanımları
# Changelog:
# - İlk oluşturma: PuanIslemTuru ve ReferansTuru enum'ları

from enum import Enum


class PuanIslemTuru(Enum):
    """Puan işlemlerinin türünü belirten sabit değerler"""
    KAZANIM = "KAZANIM"
    HARCAMA = "HARCAMA"
    DUZELTME = "DUZELTME"


class ReferansTuru(Enum):
    """Puan işlemlerinin hangi sistemden kaynaklandığını belirten değerler"""
    POS_SATIS = "POS_SATIS"
    SATIS_BELGESI = "SATIS_BELGESI"
    MANUEL_DUZELTME = "MANUEL_DUZELTME"


# Varsayılan değerler
VARSAYILAN_PUAN_HAREKET_LIMIT = 100
PUAN_HESAPLAMA_ORANI = 1  # 1 TL = 1 puan