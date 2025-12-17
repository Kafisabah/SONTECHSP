# Version: 0.1.0
# Last Update: 2024-12-16
# Module: satis_belgeleri.depolar.belge_deposu
# Description: Belge repository
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Belge Repository

Bu modül belge veri erişim katmanını içerir.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, desc, asc

from ....cekirdek.hatalar import VeriTabaniHatasi
from ....veritabani.modeller.belgeler import SatisBelgesi as SatisBelgesiDB
from ..modeller import SatisBelgesi, BelgeTuru, BelgeDurumu

logger = logging.getLogger(__name__)


class BelgeFiltresi:
    """Belge filtreleme kriterleri"""
    
    def __init__(
        self,
        belge_turu: Optional[BelgeTuru] = None,
        belge_durumu: Optional[BelgeDurumu] = None,
        magaza_id: Optional[int] = None,
        musteri_id: Optional[int] = None,
        baslangic_tarihi: Optional[str] = None,
        bitis_tarihi: Optional[str] = None,
        sayfa: int = 1,
        sayfa_boyutu: int = 50
    ):
        self.belge_turu = belge_turu
        self.belge_durumu = belge_durumu
        self.magaza_id = magaza_id
        self.musteri_id = musteri_id
        self.baslangic_tarihi = baslangic_tarihi
        self.bitis_tarihi = bitis_tarihi
        self.sayfa = max(1, sayfa)
        self.sayfa_boyutu = min(max(1, sayfa_boyutu), 100)  # Max 100 kayıt


class IBelgeDeposu(ABC):
    """Belge repository arayüzü"""
    
    @abstractmethod
    def ekle(self, belge: SatisBelgesi) -> SatisBelgesi:
        """Yeni belge ekle"""
        pass
    
    @abstractmethod
    def guncelle(self, belge: SatisBelgesi) -> SatisBelgesi:
        """Belgeyi güncelle"""
        pass
    
    @abstractmethod
    def bul(self, belge_id: int) -> Optional[SatisBelgesi]:
        """ID ile belge bul"""
        pass
    
    @abstractmethod
    def bul_numara_ile(self, belge_numarasi: str) -> Optional[SatisBelgesi]:
        """Belge numarası ile bul"""
        pass
    
    @abstractmethod
    def listele(self, filtre: BelgeFiltresi) -> List[SatisBelgesi]:
        """Filtreye göre belge listesi"""
        pass
    
    @abstractmethod
    def sayim_al(self, filtre: BelgeFiltresi) -> int:
        """Filtreye göre toplam kayıt sayısı"""
        pass
    
    @abstractmethod
    def sil(self, belge_id: int) -> bool:
        """Belgeyi sil"""
        pass
    
    @abstractmethod
    def bagli_belgeleri_bul(self, kaynak_belge_id: int) -> List[SatisBelgesi]:
        """Kaynak belgeye bağlı belgeleri bul"""
        pass
    
    @abstractmethod
    def toplam_sayisi(self, filtre) -> int:
        """Filtreye göre toplam kayıt sayısı"""
        pass
    
    @abstractmethod
    def sayfalanmis_listele(self, filtre, sayfalama) -> List[SatisBelgesi]:
        """Sayfalama ile belge listesi"""
        pass
    
    @abstractmethod
    def durum_gecmisi(self, belge_id: int) -> List:
        """Belge durum geçmişi"""
        pass


class BelgeDeposu(IBelgeDeposu):
    """Belge repository implementasyonu"""
    
    def __init__(self, session: Session):
        self._session = session
    
    def ekle(self, belge: SatisBelgesi) -> SatisBelgesi:
        """Yeni belge ekle"""
        try:
            db_belge = belge.to_db_model()
            self._session.add(db_belge)
            self._session.flush()  # ID'yi al
            
            # Güncellenmiş modeli döndür
            belge.belge_id = db_belge.id
            
            logger.debug(f"Belge eklendi: ID {db_belge.id}, Numara {belge.belge_numarasi}")
            return belge
            
        except SQLAlchemyError as e:
            logger.error(f"Belge ekleme hatası: {e}")
            raise VeriTabaniHatasi(f"Belge eklenemedi: {e}")
    
    def guncelle(self, belge: SatisBelgesi) -> SatisBelgesi:
        """Belgeyi güncelle"""
        try:
            if not belge.belge_id:
                raise VeriTabaniHatasi("Güncellenecek belgenin ID'si bulunamadı")
            
            db_belge = self._session.get(SatisBelgesiDB, belge.belge_id)
            if not db_belge:
                raise VeriTabaniHatasi(f"Belge bulunamadı: ID {belge.belge_id}")
            
            # Alanları güncelle
            db_belge.belge_durumu = belge.belge_durumu.value
            db_belge.toplam_tutar = belge.toplam_tutar
            db_belge.kdv_tutari = belge.kdv_tutari
            db_belge.genel_toplam = belge.genel_toplam
            db_belge.iptal_nedeni = belge.iptal_nedeni
            db_belge.iptal_tarihi = belge.iptal_tarihi
            
            self._session.flush()
            
            logger.debug(f"Belge güncellendi: ID {belge.belge_id}")
            return belge
            
        except SQLAlchemyError as e:
            logger.error(f"Belge güncelleme hatası: {e}")
            raise VeriTabaniHatasi(f"Belge güncellenemedi: {e}")
    
    def bul(self, belge_id: int) -> Optional[SatisBelgesi]:
        """ID ile belge bul"""
        try:
            db_belge = self._session.get(SatisBelgesiDB, belge_id)
            if db_belge:
                return SatisBelgesi.from_db_model(db_belge)
            return None
            
        except SQLAlchemyError as e:
            logger.error(f"Belge bulma hatası: {e}")
            raise VeriTabaniHatasi(f"Belge bulunamadı: {e}")
    
    def bul_numara_ile(self, belge_numarasi: str) -> Optional[SatisBelgesi]:
        """Belge numarası ile bul"""
        try:
            db_belge = (
                self._session.query(SatisBelgesiDB)
                .filter(SatisBelgesiDB.belge_numarasi == belge_numarasi)
                .first()
            )
            
            if db_belge:
                return SatisBelgesi.from_db_model(db_belge)
            return None
            
        except SQLAlchemyError as e:
            logger.error(f"Belge numara ile bulma hatası: {e}")
            raise VeriTabaniHatasi(f"Belge bulunamadı: {e}")
    
    def listele(self, filtre: BelgeFiltresi) -> List[SatisBelgesi]:
        """Filtreye göre belge listesi"""
        try:
            query = self._session.query(SatisBelgesiDB)
            
            # Filtreleri uygula
            query = self._filtre_uygula(query, filtre)
            
            # Sayfalama
            offset = (filtre.sayfa - 1) * filtre.sayfa_boyutu
            query = query.offset(offset).limit(filtre.sayfa_boyutu)
            
            # Sıralama (en yeni önce)
            query = query.order_by(desc(SatisBelgesiDB.olusturma_tarihi))
            
            db_belgeler = query.all()
            
            return [
                SatisBelgesi.from_db_model(db_belge) 
                for db_belge in db_belgeler
            ]
            
        except SQLAlchemyError as e:
            logger.error(f"Belge listeleme hatası: {e}")
            raise VeriTabaniHatasi(f"Belgeler listelenemedi: {e}")
    
    def sayim_al(self, filtre: BelgeFiltresi) -> int:
        """Filtreye göre toplam kayıt sayısı"""
        try:
            query = self._session.query(SatisBelgesiDB)
            query = self._filtre_uygula(query, filtre)
            
            return query.count()
            
        except SQLAlchemyError as e:
            logger.error(f"Belge sayım hatası: {e}")
            raise VeriTabaniHatasi(f"Belge sayımı alınamadı: {e}")
    
    def sil(self, belge_id: int) -> bool:
        """Belgeyi sil"""
        try:
            # Önce bağımlı kayıtları kontrol et
            bagli_belgeler = self.bagli_belgeleri_bul(belge_id)
            if bagli_belgeler:
                raise VeriTabaniHatasi(
                    f"Belge silinemez: {len(bagli_belgeler)} bağlı belge mevcut"
                )
            
            db_belge = self._session.get(SatisBelgesiDB, belge_id)
            if not db_belge:
                return False
            
            self._session.delete(db_belge)
            self._session.flush()
            
            logger.info(f"Belge silindi: ID {belge_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Belge silme hatası: {e}")
            raise VeriTabaniHatasi(f"Belge silinemedi: {e}")
    
    def bagli_belgeleri_bul(self, kaynak_belge_id: int) -> List[SatisBelgesi]:
        """Kaynak belgeye bağlı belgeleri bul"""
        try:
            db_belgeler = (
                self._session.query(SatisBelgesiDB)
                .filter(SatisBelgesiDB.kaynak_belge_id == kaynak_belge_id)
                .all()
            )
            
            return [
                SatisBelgesi.from_db_model(db_belge) 
                for db_belge in db_belgeler
            ]
            
        except SQLAlchemyError as e:
            logger.error(f"Bağlı belgeler bulma hatası: {e}")
            raise VeriTabaniHatasi(f"Bağlı belgeler bulunamadı: {e}")
    
    def _filtre_uygula(self, query, filtre: BelgeFiltresi):
        """Sorguya filtreleri uygula"""
        if filtre.belge_turu:
            query = query.filter(SatisBelgesiDB.belge_turu == filtre.belge_turu.value)
        
        if filtre.belge_durumu:
            query = query.filter(SatisBelgesiDB.belge_durumu == filtre.belge_durumu.value)
        
        if filtre.magaza_id:
            query = query.filter(SatisBelgesiDB.magaza_id == filtre.magaza_id)
        
        if filtre.musteri_id:
            query = query.filter(SatisBelgesiDB.musteri_id == filtre.musteri_id)
        
        if filtre.baslangic_tarihi:
            query = query.filter(SatisBelgesiDB.olusturma_tarihi >= filtre.baslangic_tarihi)
        
        if filtre.bitis_tarihi:
            query = query.filter(SatisBelgesiDB.olusturma_tarihi <= filtre.bitis_tarihi)
        
        return query