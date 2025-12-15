# Version: 0.1.0
# Last Update: 2024-12-15
# Module: veritabani.depolar.taban_crud
# Description: SONTECHSP Repository CRUD operasyonları
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Repository CRUD Operasyonları

Bu modül temel CRUD operasyonlarını içerir.
Repository pattern için ortak işlemler burada tanımlanır.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar
from sqlalchemy import and_, desc, asc, func, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ...cekirdek.hatalar import VeritabaniHatasi, DogrulamaHatasi
from ..taban import Taban

ModelType = TypeVar('ModelType', bound=Taban)


def olustur_kayit(session: Session, model: Type[ModelType], **kwargs) -> ModelType:
    """Yeni kayıt oluştur"""
    try:
        instance = model(**kwargs)
        session.add(instance)
        session.flush()
        return instance
    except SQLAlchemyError as e:
        raise VeritabaniHatasi(f"Kayıt oluşturma hatası: {e}")
    except Exception as e:
        raise DogrulamaHatasi(f"Geçersiz veri: {e}")


def id_ile_getir_kayit(session: Session, model: Type[ModelType], kayit_id: int) -> Optional[ModelType]:
    """ID ile kayıt getir"""
    try:
        return session.get(model, kayit_id)
    except SQLAlchemyError as e:
        raise VeritabaniHatasi(f"Kayıt getirme hatası: {e}")


def filtre_ile_getir_kayitlar(session: Session, model: Type[ModelType], **filtreler) -> List[ModelType]:
    """Filtre ile kayıtları getir"""
    try:
        query = select(model)
        
        for alan, deger in filtreler.items():
            if hasattr(model, alan):
                query = query.where(getattr(model, alan) == deger)
        
        result = session.execute(query)
        return result.scalars().all()
        
    except SQLAlchemyError as e:
        raise VeritabaniHatasi(f"Kayıt filtreleme hatası: {e}")


def tumu_getir_kayitlar(
    session: Session, 
    model: Type[ModelType],
    sayfa: int = 1, 
    sayfa_boyutu: int = 50,
    siralama: Optional[str] = None,
    azalan: bool = False
) -> List[ModelType]:
    """Tüm kayıtları getir (sayfalama ile)"""
    try:
        query = select(model)
        
        # Sıralama
        if siralama and hasattr(model, siralama):
            alan = getattr(model, siralama)
            if azalan:
                query = query.order_by(desc(alan))
            else:
                query = query.order_by(asc(alan))
        
        # Sayfalama
        offset = (sayfa - 1) * sayfa_boyutu
        query = query.offset(offset).limit(sayfa_boyutu)
        
        result = session.execute(query)
        return result.scalars().all()
        
    except SQLAlchemyError as e:
        raise VeritabaniHatasi(f"Kayıt listeleme hatası: {e}")


def guncelle_kayit(session: Session, model: Type[ModelType], kayit_id: int, **kwargs) -> Optional[ModelType]:
    """Kayıt güncelle"""
    try:
        instance = id_ile_getir_kayit(session, model, kayit_id)
        if not instance:
            return None
        
        for alan, deger in kwargs.items():
            if hasattr(instance, alan):
                setattr(instance, alan, deger)
        
        session.flush()
        return instance
        
    except SQLAlchemyError as e:
        raise VeritabaniHatasi(f"Kayıt güncelleme hatası: {e}")
    except Exception as e:
        raise DogrulamaHatasi(f"Geçersiz güncelleme verisi: {e}")


def sil_kayit(session: Session, model: Type[ModelType], kayit_id: int) -> bool:
    """Kayıt sil"""
    try:
        instance = id_ile_getir_kayit(session, model, kayit_id)
        if not instance:
            return False
        
        session.delete(instance)
        session.flush()
        return True
        
    except SQLAlchemyError as e:
        raise VeritabaniHatasi(f"Kayıt silme hatası: {e}")


def sayim_kayit(session: Session, model: Type[ModelType], **filtreler) -> int:
    """Kayıt sayısını getir"""
    try:
        query = select(func.count(model.id))
        
        for alan, deger in filtreler.items():
            if hasattr(model, alan):
                query = query.where(getattr(model, alan) == deger)
        
        result = session.execute(query)
        return result.scalar() or 0
        
    except SQLAlchemyError as e:
        raise VeritabaniHatasi(f"Kayıt sayım hatası: {e}")