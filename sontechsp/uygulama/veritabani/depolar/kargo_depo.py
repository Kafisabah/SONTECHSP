# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.depolar.kargo_depo
# Description: SONTECHSP kargo repository sınıfları
# Changelog:
# - İlk oluşturma

from .taban import TemelDepo
from ..modeller.kargo import KargoEtiket, KargoTakip


class KargoEtiketDepo(TemelDepo[KargoEtiket]):
    def __init__(self):
        super().__init__(KargoEtiket)


class KargoTakipDepo(TemelDepo[KargoTakip]):
    def __init__(self):
        super().__init__(KargoTakip)