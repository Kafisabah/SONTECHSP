# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.depolar.taban
# Description: SONTECHSP Repository pattern temel sınıfı
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Repository Pattern Temel Sınıfı

Bu modül tüm repository sınıflarının türetileceği abstract base class'ı içerir.
CRUD operasyonları ve ortak veritabanı işlemleri için standart arayüz sağlar.
"""

from abc import ABC
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ...cekirdek.hatalar import VeritabaniHatasi, DogrulamaHatasi
from ..taban import Taban
from .taban_crud import (
    olustur_kayit, id_ile_getir_kayit, filtre_ile_getir_kayitlar,
    tumu_getir_kayitlar, guncelle_kayit, sil_kayit, sayim_kayit
)

ModelType = TypeVar('ModelType', bound=Taban)


class TemelDepo(Generic[ModelType], ABC):
    """SONTECHSP Repository pattern temel sınıfı"""
    
    def __init__(self, model: Type[ModelType]):
        """Repository başlatma"""
        self.model = model
    
    def olustur(self, session: Session, **kwargs) -> ModelType:
        """Yeni kayıt oluştur"""
        instance = olustur_kayit(session, self.model, **kwargs)
        self._dogrula(instance)
        return instance
    
    def id_ile_getir(self, session: Session, kayit_id: int) -> Optional[ModelType]:
        """ID ile kayıt getir"""
        return id_ile_getir_kayit(session, self.model, kayit_id)
    
    def filtre_ile_getir(self, session: Session, **filtreler) -> List[ModelType]:
        """Filtre ile kayıtları getir"""
        return filtre_ile_getir_kayitlar(session, self.model, **filtreler)
    
    def tumu_getir(
        self, 
        session: Session, 
        sayfa: int = 1, 
        sayfa_boyutu: int = 50,
        siralama: Optional[str] = None,
        azalan: bool = False
    ) -> List[ModelType]:
        """Tüm kayıtları getir (sayfalama ile)"""
        return tumu_getir_kayitlar(session, self.model, sayfa, sayfa_boyutu, siralama, azalan)
    
    def guncelle(self, session: Session, kayit_id: int, **kwargs) -> Optional[ModelType]:
        """Kayıt güncelle"""
        instance = guncelle_kayit(session, self.model, kayit_id, **kwargs)
        if instance:
            self._dogrula(instance)
        return instance
    
    def sil(self, session: Session, kayit_id: int) -> bool:
        """Kayıt sil"""
        instance = self.id_ile_getir(session, kayit_id)
        if instance:
            self._silme_oncesi_kontrol(session, instance)
        return sil_kayit(session, self.model, kayit_id)
    
    def toplu_olustur(self, session: Session, kayitlar: List[Dict[str, Any]]) -> List[ModelType]:
        """Toplu kayıt oluştur"""
        try:
            instances = []
            for kayit_verisi in kayitlar:
                instance = self.model(**kayit_verisi)
                self._dogrula(instance)
                instances.append(instance)
            
            session.add_all(instances)
            session.flush()
            return instances
            
        except SQLAlchemyError as e:
            raise VeritabaniHatasi(f"Toplu kayıt oluşturma hatası: {e}")
        except Exception as e:
            raise DogrulamaHatasi(f"Geçersiz toplu veri: {e}")
    
    def sayim(self, session: Session, **filtreler) -> int:
        """Kayıt sayısını getir"""
        return sayim_kayit(session, self.model, **filtreler)
    
    def var_mi(self, session: Session, **filtreler) -> bool:
        """Kayıt var mı kontrol et"""
        return self.sayim(session, **filtreler) > 0
    
    def _dogrula(self, instance: ModelType) -> None:
        """Model instance doğrulama"""
        pass
    
    def _silme_oncesi_kontrol(self, session: Session, instance: ModelType) -> None:
        """Silme öncesi kontroller"""
        pass