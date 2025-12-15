# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.depolar.belge_depo
# Description: SONTECHSP belge repository sınıfları
# Changelog:
# - İlk oluşturma

from .taban import TemelDepo
from ..modeller.belgeler import SatisBelge


class SatisBelgeDepo(TemelDepo[SatisBelge]):
    def __init__(self):
        super().__init__(SatisBelge)