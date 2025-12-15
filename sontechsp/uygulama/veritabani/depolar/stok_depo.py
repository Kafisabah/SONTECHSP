# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.depolar.stok_depo
# Description: SONTECHSP stok repository sınıfları
# Changelog:
# - İlk oluşturma

from .taban import TemelDepo
from ..modeller.stok import Urun, StokBakiye, StokHareket


class UrunDepo(TemelDepo[Urun]):
    def __init__(self):
        super().__init__(Urun)


class StokBakiyeDepo(TemelDepo[StokBakiye]):
    def __init__(self):
        super().__init__(StokBakiye)


class StokHareketDepo(TemelDepo[StokHareket]):
    def __init__(self):
        super().__init__(StokHareket)