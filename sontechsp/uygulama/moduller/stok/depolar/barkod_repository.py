# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.depolar.barkod_repository
# Description: Barkod repository implementasyonu
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Barkod Repository

Bu modül barkod veri erişim işlemlerini gerçekleştirir.
Barkod CRUD işlemleri ve benzersizlik kontrolü yapar.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from sontechsp.uygulama.veritabani.modeller.stok import UrunBarkod
from sontechsp.uygulama.veritabani.baglanti import VeriTabaniBaglanti
from ..dto import BarkodDTO
from ..hatalar import BarkodValidationError
from .arayuzler import IBarkodRepository


class BarkodRepository(IBarkodRepository):
    """Barkod repository implementasyonu"""
    
    def __init__(self):
        self.db = VeriTabaniBaglanti()
    
    def ekle(self, barkod: BarkodDTO) -> int:
        """Yeni barkod ekler"""
        # Doğrulama
        hatalar = barkod.validate()
        if hatalar:
            raise BarkodValidationError("Barkod doğrulama hatası", barkod.barkod)
        
        session = self.db.oturum_olustur()
        try:
            # Benzersizlik kontrolü
            mevcut = session.query(UrunBarkod).filter_by(barkod=barkod.barkod).first()
            if mevcut:
                raise BarkodValidationError(f"'{barkod.barkod}' barkodu zaten kullanılıyor")
            
            # Yeni barkod oluştur
            yeni_barkod = UrunBarkod(
                urun_id=barkod.urun_id,
                barkod=barkod.barkod,
                barkod_tipi=barkod.barkod_tipi,
                birim=barkod.birim,
                carpan=barkod.carpan,
                aktif=barkod.aktif,
                ana_barkod=barkod.ana_barkod
            )
            
            session.add(yeni_barkod)
            session.commit()
            return yeni_barkod.id
            
        except IntegrityError as e:
            session.rollback()
            raise BarkodValidationError(f"Barkod kaydedilemedi: {str(e)}")
        finally:
            session.close()
    
    def sil(self, barkod_id: int) -> bool:
        """Barkod siler (minimum barkod kontrolü ile)"""
        session = self.db.oturum_olustur()
        try:
            barkod = session.query(UrunBarkod).filter_by(id=barkod_id).first()
            if not barkod:
                return False
            
            # Minimum barkod kontrolü
            urun_barkod_sayisi = session.query(UrunBarkod).filter_by(
                urun_id=barkod.urun_id, aktif=True
            ).count()
            
            if urun_barkod_sayisi <= 1:
                raise BarkodValidationError("Ürünün en az bir aktif barkodu olmalıdır")
            
            session.delete(barkod)
            session.commit()
            return True
            
        finally:
            session.close()
    
    def barkod_ile_ara(self, barkod: str) -> Optional[BarkodDTO]:
        """Barkod ile arama yapar"""
        session = self.db.oturum_olustur()
        try:
            barkod_obj = session.query(UrunBarkod).filter_by(
                barkod=barkod, aktif=True
            ).first()
            
            if not barkod_obj:
                return None
            
            return self._model_to_dto(barkod_obj)
            
        finally:
            session.close()
    
    def urun_barkodlari_getir(self, urun_id: int) -> List[BarkodDTO]:
        """Ürünün tüm barkodlarını getirir"""
        session = self.db.oturum_olustur()
        try:
            barkodlar = session.query(UrunBarkod).filter_by(
                urun_id=urun_id, aktif=True
            ).all()
            
            return [self._model_to_dto(b) for b in barkodlar]
            
        finally:
            session.close()
    
    def _model_to_dto(self, barkod: UrunBarkod) -> BarkodDTO:
        """Model'i DTO'ya çevirir"""
        return BarkodDTO(
            id=barkod.id,
            urun_id=barkod.urun_id,
            barkod=barkod.barkod,
            barkod_tipi=barkod.barkod_tipi,
            birim=barkod.birim,
            carpan=barkod.carpan,
            aktif=barkod.aktif,
            ana_barkod=barkod.ana_barkod,
            olusturma_tarihi=barkod.olusturma_tarihi,
            guncelleme_tarihi=barkod.guncelleme_tarihi
        )