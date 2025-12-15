# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.depolar.crm_depo
# Description: SONTECHSP CRM repository sınıfları
# Changelog:
# - İlk oluşturma

from .taban import TemelDepo
from ..modeller.crm import Musteri, SadakatPuan


class MusteriDepo(TemelDepo[Musteri]):
    def __init__(self):
        super().__init__(Musteri)


class SadakatPuanDepo(TemelDepo[SadakatPuan]):
    def __init__(self):
        super().__init__(SadakatPuan)