# Version: 0.1.0
# Last Update: 2024-12-16
# Module: satis_belgeleri.depolar.belge_durum_gecmisi_deposu
# Description: Belge durum geçmişi repository
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Belge Durum Geçmişi Repository

Bu modül belge durum geçmişi veri erişim katmanını içerir.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ....cekirdek.hatalar import VeriTabaniHatasi
from ....veritabani.modeller.belgeler import BelgeDurumGecmisi as BelgeDurumGecmisiDB
from ..modeller.belge_durum_gecmisi import BelgeDurumGecmisi

logger = logging.getLogger(__name__)


class IBelgeDurumGecmisiDeposu(ABC):
    """Belge durum geçmişi repository arayüzü"""
    
    @abstractmethod
    def ekle(self, gecmis: BelgeDurumGecmisi) -> BelgeDurumGecmisi:
        """Yeni geçmiş kaydı ekle"""
        pass
    
    @abstractmethod
    def bul(self, gecmis_id: int) -> Optional[BelgeDurumGecmisi]:
        """ID ile geçmiş kaydı bul"""
        pass
    
    @abstractmethod
    def belge_gecmisi_al(self, belge_id: int) -> List[BelgeDurumGecmisi]:
        """Belge için tüm geçmiş kayıtlarını al"""
        pass
    
    @abstractmethod
    def kullanici_gecmisi_al(self, kullanici_id: int) -> List[BelgeDurumGecmisi]:
        """Kullanıcının yaptığı tüm durum değişikliklerini al"""
        pass


class BelgeDurumGecmisiDeposu(IBelgeDurumGecmisiDeposu):
    """Belge durum geçmişi repository implementasyonu"""
    
    def __init__(self, session: Session):
        self._session = session
    
    def ekle(self, gecmis: BelgeDurumGecmisi) -> BelgeDurumGecmisi:
        """Yeni geçmiş kaydı ekle"""
        try:
            db_gecmis = gecmis.to_db_model()
            self._session.add(db_gecmis)
            self._session.flush()  # ID'yi al
            
            # Güncellenmiş modeli döndür
            gecmis.gecmis_id = db_gecmis.id
            
            logger.debug(f"Durum geçmişi eklendi: ID {db_gecmis.id}")
            return gecmis
            
        except SQLAlchemyError as e:
            logger.error(f"Durum geçmişi ekleme hatası: {e}")
            raise VeriTabaniHatasi(f"Durum geçmişi eklenemedi: {e}")
    
    def bul(self, gecmis_id: int) -> Optional[BelgeDurumGecmisi]:
        """ID ile geçmiş kaydı bul"""
        try:
            db_gecmis = self._session.get(BelgeDurumGecmisiDB, gecmis_id)
            if db_gecmis:
                return BelgeDurumGecmisi.from_db_model(db_gecmis)
            return None
            
        except SQLAlchemyError as e:
            logger.error(f"Durum geçmişi bulma hatası: {e}")
            raise VeriTabaniHatasi(f"Durum geçmişi bulunamadı: {e}")
    
    def belge_gecmisi_al(self, belge_id: int) -> List[BelgeDurumGecmisi]:
        """Belge için tüm geçmiş kayıtlarını al"""
        try:
            db_gecmis_listesi = (
                self._session.query(BelgeDurumGecmisiDB)
                .filter(BelgeDurumGecmisiDB.belge_id == belge_id)
                .order_by(BelgeDurumGecmisiDB.olusturma_tarihi.asc())
                .all()
            )
            
            return [
                BelgeDurumGecmisi.from_db_model(db_gecmis) 
                for db_gecmis in db_gecmis_listesi
            ]
            
        except SQLAlchemyError as e:
            logger.error(f"Belge geçmişi alma hatası: {e}")
            raise VeriTabaniHatasi(f"Belge geçmişi alınamadı: {e}")
    
    def kullanici_gecmisi_al(self, kullanici_id: int) -> List[BelgeDurumGecmisi]:
        """Kullanıcının yaptığı tüm durum değişikliklerini al"""
        try:
            db_gecmis_listesi = (
                self._session.query(BelgeDurumGecmisiDB)
                .filter(BelgeDurumGecmisiDB.degistiren_kullanici_id == kullanici_id)
                .order_by(BelgeDurumGecmisiDB.olusturma_tarihi.desc())
                .all()
            )
            
            return [
                BelgeDurumGecmisi.from_db_model(db_gecmis) 
                for db_gecmis in db_gecmis_listesi
            ]
            
        except SQLAlchemyError as e:
            logger.error(f"Kullanıcı geçmişi alma hatası: {e}")
            raise VeriTabaniHatasi(f"Kullanıcı geçmişi alınamadı: {e}")