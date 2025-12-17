# Version: 0.1.0
# Last Update: 2024-12-16
# Module: satis_belgeleri.depolar.numara_sayac_deposu
# Description: Numara sayacı repository
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Numara Sayacı Repository

Bu modül numara sayacı veri erişim katmanını içerir.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ....cekirdek.hatalar import VeriTabaniHatasi
from ....veritabani.modeller.belgeler import NumaraSayaci as NumaraSayaciDB
from ..modeller import NumaraSayaci, BelgeTuru

logger = logging.getLogger(__name__)


class INumaraSayacDeposu(ABC):
    """Numara sayacı repository arayüzü"""
    
    @abstractmethod
    def ekle(self, sayac: NumaraSayaci) -> NumaraSayaci:
        """Yeni sayaç ekle"""
        pass
    
    @abstractmethod
    def guncelle(self, sayac: NumaraSayaci) -> NumaraSayaci:
        """Sayacı güncelle"""
        pass
    
    @abstractmethod
    def bul(self, sayac_id: int) -> Optional[NumaraSayaci]:
        """ID ile sayaç bul"""
        pass
    
    @abstractmethod
    def bul_magaza_tur_yil_ay(
        self, 
        magaza_id: int, 
        belge_turu: BelgeTuru, 
        yil: int, 
        ay: int
    ) -> Optional[NumaraSayaci]:
        """Mağaza, tür, yıl, ay ile sayaç bul"""
        pass
    
    @abstractmethod
    def bul_son_sayac(
        self, 
        magaza_id: int, 
        belge_turu: BelgeTuru
    ) -> Optional[NumaraSayaci]:
        """Mağaza ve tür için en son sayacı bul"""
        pass


class NumaraSayacDeposu(INumaraSayacDeposu):
    """Numara sayacı repository implementasyonu"""
    
    def __init__(self, session: Session):
        self._session = session
    
    def ekle(self, sayac: NumaraSayaci) -> NumaraSayaci:
        """Yeni sayaç ekle"""
        try:
            db_sayac = sayac.to_db_model()
            self._session.add(db_sayac)
            self._session.flush()  # ID'yi al
            
            # Güncellenmiş modeli döndür
            sayac.sayac_id = db_sayac.id
            
            logger.debug(f"Sayaç eklendi: ID {db_sayac.id}")
            return sayac
            
        except SQLAlchemyError as e:
            logger.error(f"Sayaç ekleme hatası: {e}")
            raise VeriTabaniHatasi(f"Sayaç eklenemedi: {e}")
    
    def guncelle(self, sayac: NumaraSayaci) -> NumaraSayaci:
        """Sayacı güncelle"""
        try:
            if not sayac.sayac_id:
                raise VeriTabaniHatasi("Güncellenecek sayacın ID'si bulunamadı")
            
            db_sayac = self._session.get(NumaraSayaciDB, sayac.sayac_id)
            if not db_sayac:
                raise VeriTabaniHatasi(f"Sayaç bulunamadı: ID {sayac.sayac_id}")
            
            # Alanları güncelle
            db_sayac.son_numara = sayac.son_numara
            
            self._session.flush()
            
            logger.debug(f"Sayaç güncellendi: ID {sayac.sayac_id}")
            return sayac
            
        except SQLAlchemyError as e:
            logger.error(f"Sayaç güncelleme hatası: {e}")
            raise VeriTabaniHatasi(f"Sayaç güncellenemedi: {e}")
    
    def bul(self, sayac_id: int) -> Optional[NumaraSayaci]:
        """ID ile sayaç bul"""
        try:
            db_sayac = self._session.get(NumaraSayaciDB, sayac_id)
            if db_sayac:
                return NumaraSayaci.from_db_model(db_sayac)
            return None
            
        except SQLAlchemyError as e:
            logger.error(f"Sayaç bulma hatası: {e}")
            raise VeriTabaniHatasi(f"Sayaç bulunamadı: {e}")
    
    def bul_magaza_tur_yil_ay(
        self, 
        magaza_id: int, 
        belge_turu: BelgeTuru, 
        yil: int, 
        ay: int
    ) -> Optional[NumaraSayaci]:
        """Mağaza, tür, yıl, ay ile sayaç bul"""
        try:
            db_sayac = (
                self._session.query(NumaraSayaciDB)
                .filter(
                    NumaraSayaciDB.magaza_id == magaza_id,
                    NumaraSayaciDB.belge_turu == belge_turu.value,
                    NumaraSayaciDB.yil == yil,
                    NumaraSayaciDB.ay == ay
                )
                .first()
            )
            
            if db_sayac:
                return NumaraSayaci.from_db_model(db_sayac)
            return None
            
        except SQLAlchemyError as e:
            logger.error(f"Sayaç bulma hatası: {e}")
            raise VeriTabaniHatasi(f"Sayaç bulunamadı: {e}")
    
    def bul_son_sayac(
        self, 
        magaza_id: int, 
        belge_turu: BelgeTuru
    ) -> Optional[NumaraSayaci]:
        """Mağaza ve tür için en son sayacı bul"""
        try:
            db_sayac = (
                self._session.query(NumaraSayaciDB)
                .filter(
                    NumaraSayaciDB.magaza_id == magaza_id,
                    NumaraSayaciDB.belge_turu == belge_turu.value
                )
                .order_by(
                    NumaraSayaciDB.yil.desc(),
                    NumaraSayaciDB.ay.desc()
                )
                .first()
            )
            
            if db_sayac:
                return NumaraSayaci.from_db_model(db_sayac)
            return None
            
        except SQLAlchemyError as e:
            logger.error(f"Son sayaç bulma hatası: {e}")
            raise VeriTabaniHatasi(f"Son sayaç bulunamadı: {e}")