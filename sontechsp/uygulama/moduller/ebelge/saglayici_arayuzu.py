# Version: 0.1.0
# Last Update: 2024-12-17
# Module: ebelge.saglayici_arayuzu
# Description: E-belge sağlayıcı abstract base class
# Changelog:
# - İlk versiyon: SaglayiciArayuzu abstract sınıfı oluşturuldu

from abc import ABC, abstractmethod
from .dto import EBelgeGonderDTO, EBelgeSonucDTO


class SaglayiciArayuzu(ABC):
    """Tüm e-belge sağlayıcılarının uyması gereken arayüz"""
    
    @abstractmethod
    def gonder(self, dto: EBelgeGonderDTO) -> EBelgeSonucDTO:
        """Belgeyi entegratöre gönderir"""
        pass
    
    @abstractmethod
    def durum_sorgula(self, dis_belge_no: str) -> EBelgeSonucDTO:
        """Belge durumunu entegratörden sorgular"""
        pass