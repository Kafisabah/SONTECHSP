# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.depolar.firma_depo
# Description: SONTECHSP firma repository sınıfları
# Changelog:
# - İlk oluşturma

from .taban import TemelDepo
from ..modeller.firma_magaza import Firma, Magaza, Terminal


class FirmaDepo(TemelDepo[Firma]):
    def __init__(self):
        super().__init__(Firma)


class MagazaDepo(TemelDepo[Magaza]):
    def __init__(self):
        super().__init__(Magaza)


class TerminalDepo(TemelDepo[Terminal]):
    def __init__(self):
        super().__init__(Terminal)