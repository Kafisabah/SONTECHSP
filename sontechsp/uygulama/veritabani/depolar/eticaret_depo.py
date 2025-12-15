# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.depolar.eticaret_depo
# Description: SONTECHSP e-ticaret repository sınıfları
# Changelog:
# - İlk oluşturma

from .taban import TemelDepo
from ..modeller.eticaret import EticaretHesap, EticaretSiparis


class EticaretHesapDepo(TemelDepo[EticaretHesap]):
    def __init__(self):
        super().__init__(EticaretHesap)


class EticaretSiparisDepo(TemelDepo[EticaretSiparis]):
    def __init__(self):
        super().__init__(EticaretSiparis)