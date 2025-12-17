# Version: 0.1.0
# Last Update: 2024-12-16
# Module: satis_belgeleri.depolar.belge_satir_deposu
# Description: Belge satır repository
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Belge Satır Repository

Bu modül belge satır veri erişim katmanını içerir.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_

from ....cekirdek.hatalar import VeriTabaniHatasi
from ....veritabani.modeller.belgeler import BelgeSatiri as BelgeSatiriDB
from ..modeller import BelgeSatiri

logger = logging.getLogger(__name__)


class IBelgeSatirDeposu(ABC):
    """Belge satır repository arayüzü"""
    
    @abstractmethod
    def ekle(self, satir: BelgeSatiri) -> BelgeSatiri:
        """Yeni satır ekle"""
        pass
    
    @abstractmethod
    def guncelle(self, satir: BelgeSatiri) -> BelgeSatiri:
        """Satırı güncelle"""
        pass
    
    @abstractmethod
    def bul(self, satir_id: int) -> Optional[BelgeSatiri]:
        """ID ile satır bul"""
        pass
    
    @abstractmethod
    def belge_satirlari_al(self, belge_id: int) -> List[BelgeSatiri]:
        """Belgeye ait tüm satırları al"""
        pass
    
    @abstractmethod
    def sil(self, satir_id: int) -> bool:
        """Satırı sil"""
        pass
    
    @abstractmethod
    def belge_satirlari_sil(self, belge_id: int) -> int:
        """Belgeye ait tüm satırları sil"""
        pass
    
    @abstractmethod
    def toplu_ekle(self, satirlar: List[BelgeSatiri]) -> List[BelgeSatiri]:
        """Birden fazla satır ekle"""
        pass


class BelgeSatirDeposu(IBelgeSatirDeposu):
    """Belge satır repository implementasyonu"""
    
    def __init__(self, session: Session):
        self._session = session
    
    def ekle(self, satir: BelgeSatiri) -> BelgeSatiri:
        """Yeni satır ekle"""
        try:
            db_satir = satir.to_db_model()
            self._session.add(db_satir)
            self._session.flush()  # ID'yi al
            
            # Güncellenmiş modeli döndür
            satir.satir_id = db_satir.id
            
            logger.debug(f"Belge satırı eklendi: ID {db_satir.id}")
            return satir
            
        except SQLAlchemyError as e:
            logger.error(f"Belge satırı ekleme hatası: {e}")
            raise VeriTabaniHatasi(f"Belge satırı eklenemedi: {e}")
    
    def guncelle(self, satir: BelgeSatiri) -> BelgeSatiri:
        """Satırı güncelle"""
        try:
            if not satir.satir_id:
                raise VeriTabaniHatasi("Güncellenecek satırın ID'si bulunamadı")
            
            db_satir = self._session.get(BelgeSatiriDB, satir.satir_id)
            if not db_satir:
                raise VeriTabaniHatasi(f"Belge satırı bulunamadı: ID {satir.satir_id}")
            
            # Alanları güncelle
            db_satir.miktar = satir.miktar
            db_satir.birim_fiyat = satir.birim_fiyat
            db_satir.kdv_orani = satir.kdv_orani
            db_satir.satir_tutari = satir.satir_tutari
            db_satir.kdv_tutari = satir.kdv_tutari
            db_satir.satir_toplami = satir.satir_toplami
            db_satir.sira_no = satir.sira_no
            
            self._session.flush()
            
            logger.debug(f"Belge satırı güncellendi: ID {satir.satir_id}")
            return satir
            
        except SQLAlchemyError as e:
            logger.error(f"Belge satırı güncelleme hatası: {e}")
            raise VeriTabaniHatasi(f"Belge satırı güncellenemedi: {e}")
    
    def bul(self, satir_id: int) -> Optional[BelgeSatiri]:
        """ID ile satır bul"""
        try:
            db_satir = self._session.get(BelgeSatiriDB, satir_id)
            if db_satir:
                return BelgeSatiri.from_db_model(db_satir)
            return None
            
        except SQLAlchemyError as e:
            logger.error(f"Belge satırı bulma hatası: {e}")
            raise VeriTabaniHatasi(f"Belge satırı bulunamadı: {e}")
    
    def belge_satirlari_al(self, belge_id: int) -> List[BelgeSatiri]:
        """Belgeye ait tüm satırları al"""
        try:
            db_satirlar = (
                self._session.query(BelgeSatiriDB)
                .filter(BelgeSatiriDB.belge_id == belge_id)
                .order_by(BelgeSatiriDB.sira_no.asc())
                .all()
            )
            
            return [
                BelgeSatiri.from_db_model(db_satir) 
                for db_satir in db_satirlar
            ]
            
        except SQLAlchemyError as e:
            logger.error(f"Belge satırları alma hatası: {e}")
            raise VeriTabaniHatasi(f"Belge satırları alınamadı: {e}")
    
    def sil(self, satir_id: int) -> bool:
        """Satırı sil"""
        try:
            db_satir = self._session.get(BelgeSatiriDB, satir_id)
            if not db_satir:
                return False
            
            self._session.delete(db_satir)
            self._session.flush()
            
            logger.debug(f"Belge satırı silindi: ID {satir_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Belge satırı silme hatası: {e}")
            raise VeriTabaniHatasi(f"Belge satırı silinemedi: {e}")
    
    def belge_satirlari_sil(self, belge_id: int) -> int:
        """Belgeye ait tüm satırları sil"""
        try:
            silinen_sayisi = (
                self._session.query(BelgeSatiriDB)
                .filter(BelgeSatiriDB.belge_id == belge_id)
                .delete()
            )
            
            self._session.flush()
            
            logger.debug(f"Belge satırları silindi: Belge ID {belge_id}, Sayı {silinen_sayisi}")
            return silinen_sayisi
            
        except SQLAlchemyError as e:
            logger.error(f"Belge satırları silme hatası: {e}")
            raise VeriTabaniHatasi(f"Belge satırları silinemedi: {e}")
    
    def toplu_ekle(self, satirlar: List[BelgeSatiri]) -> List[BelgeSatiri]:
        """Birden fazla satır ekle"""
        try:
            eklenen_satirlar = []
            
            for satir in satirlar:
                db_satir = satir.to_db_model()
                self._session.add(db_satir)
                self._session.flush()  # ID'yi al
                
                satir.satir_id = db_satir.id
                eklenen_satirlar.append(satir)
            
            logger.debug(f"Toplu belge satırı eklendi: {len(eklenen_satirlar)} adet")
            return eklenen_satirlar
            
        except SQLAlchemyError as e:
            logger.error(f"Toplu belge satırı ekleme hatası: {e}")
            raise VeriTabaniHatasi(f"Toplu belge satırı eklenemedi: {e}")
    
    def belge_satir_sayisi_al(self, belge_id: int) -> int:
        """Belgeye ait satır sayısını al"""
        try:
            sayisi = (
                self._session.query(BelgeSatiriDB)
                .filter(BelgeSatiriDB.belge_id == belge_id)
                .count()
            )
            
            return sayisi
            
        except SQLAlchemyError as e:
            logger.error(f"Belge satır sayısı alma hatası: {e}")
            raise VeriTabaniHatasi(f"Belge satır sayısı alınamadı: {e}")
    
    def son_sira_no_al(self, belge_id: int) -> int:
        """Belgeye ait son sıra numarasını al"""
        try:
            son_satir = (
                self._session.query(BelgeSatiriDB)
                .filter(BelgeSatiriDB.belge_id == belge_id)
                .order_by(BelgeSatiriDB.sira_no.desc())
                .first()
            )
            
            return son_satir.sira_no if son_satir else 0
            
        except SQLAlchemyError as e:
            logger.error(f"Son sıra numarası alma hatası: {e}")
            return 0