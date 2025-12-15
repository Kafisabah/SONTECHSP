# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.depolar.pos_depo
# Description: SONTECHSP POS repository sınıfları
# Changelog:
# - İlk oluşturma

from .taban import TemelDepo
from ..modeller.pos import PosSatis, OdemeKayit


class PosSatisDepo(TemelDepo[PosSatis]):
    def __init__(self):
        super().__init__(PosSatis)


class OdemeKayitDepo(TemelDepo[OdemeKayit]):
    def __init__(self):
        super().__init__(OdemeKayit)