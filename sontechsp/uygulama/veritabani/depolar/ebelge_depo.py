# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.depolar.ebelge_depo
# Description: SONTECHSP e-belge repository sınıfları
# Changelog:
# - İlk oluşturma

from .taban import TemelDepo
from ..modeller.ebelge import EbelgeCikisKuyruk, EbelgeDurum


class EbelgeCikisKuyrukDepo(TemelDepo[EbelgeCikisKuyruk]):
    def __init__(self):
        super().__init__(EbelgeCikisKuyruk)


class EbelgeDurumDepo(TemelDepo[EbelgeDurum]):
    def __init__(self):
        super().__init__(EbelgeDurum)