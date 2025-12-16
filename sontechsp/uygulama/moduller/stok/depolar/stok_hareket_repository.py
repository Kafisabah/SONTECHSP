# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.depolar.stok_hareket_repository
# Description: Stok hareket repository implementasyonu
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Stok Hareket Repository

Bu modül stok hareket veri erişim işlemlerini gerçekleştirir.
PostgreSQL SELECT FOR UPDATE ile eş zamanlı erişim kontrolü yapar.
"""

from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from sontechsp.uygulama.veritabani.modeller.stok import StokHareket, StokBakiye
from sontechsp.uygulama.veritabani.baglanti import VeriTabaniBaglanti
from ..dto import StokHareketDTO, StokHareketFiltreDTO
from ..hatalar import EsZamanliErisimError
from .arayuzler import IStokHareketRepository


class StokHareketRepository(IStokHareketRepository):
    """Stok hareket repository implementasyonu"""
    
    def __init__(self):
        self.db = VeriTabaniBaglanti()
    
    def hareket_ekle(self, hareket: StokHareketDTO) -> int:
        """Yeni stok hareketi ekler"""
        # Doğrulama
        hatalar = hareket.validate()
        if hatalar:
            raise ValueError(f"Hareket doğrulama hatası: {', '.join(hatalar)}")
        
        session = self.db.oturum_olustur()
        try:
            # Yeni hareket oluştur
            yeni_hareket = StokHareket(
                urun_id=hareket.urun_id,
                magaza_id=hareket.magaza_id,
                depo_id=hareket.depo_id,
                hareket_tipi=hareket.hareket_tipi,
                miktar=hareket.miktar,
                birim_fiyat=hareket.birim_fiyat,
                toplam_tutar=hareket.toplam_tutar,
                referans_tablo=hareket.referans_tablo,
                referans_id=hareket.referans_id,
                aciklama=hareket.aciklama,
                kullanici_id=hareket.kullanici_id
            )
            
            session.add(yeni_hareket)
            session.commit()
            return yeni_hareket.id
            
        except IntegrityError as e:
            session.rollback()
            raise ValueError(f"Hareket kaydedilemedi: {str(e)}")
        finally:
            session.close()
    
    def hareket_listesi(self, filtre: StokHareketFiltreDTO) -> List[StokHareketDTO]:
        """Filtrelenmiş hareket listesi getirir"""
        # Filtre doğrulama
        hatalar = filtre.validate()
        if hatalar:
            raise ValueError(f"Filtre doğrulama hatası: {', '.join(hatalar)}")
        
        session = self.db.oturum_olustur()
        try:
            query = session.query(StokHareket)
            
            # Filtreleri uygula
            if filtre.urun_id:
                query = query.filter(StokHareket.urun_id == filtre.urun_id)
            if filtre.magaza_id:
                query = query.filter(StokHareket.magaza_id == filtre.magaza_id)
            if filtre.depo_id:
                query = query.filter(StokHareket.depo_id == filtre.depo_id)
            if filtre.hareket_tipi:
                query = query.filter(StokHareket.hareket_tipi == filtre.hareket_tipi)
            if filtre.baslangic_tarihi:
                query = query.filter(StokHareket.olusturma_tarihi >= filtre.baslangic_tarihi)
            if filtre.bitis_tarihi:
                query = query.filter(StokHareket.olusturma_tarihi <= filtre.bitis_tarihi)
            
            # Sayfalama
            offset = (filtre.sayfa - 1) * filtre.sayfa_boyutu
            hareketler = query.order_by(StokHareket.olusturma_tarihi.desc())\
                            .offset(offset).limit(filtre.sayfa_boyutu).all()
            
            return [self._model_to_dto(h) for h in hareketler]
            
        finally:
            session.close()
    
    def kilitle_ve_bakiye_getir(self, urun_id: int, magaza_id: int, 
                               depo_id: Optional[int] = None) -> Decimal:
        """Stok bakiyesini kilitler ve getirir (SELECT FOR UPDATE)"""
        session = self.db.oturum_olustur()
        try:
            # PostgreSQL SELECT FOR UPDATE kullan
            query = session.query(StokBakiye).filter(
                StokBakiye.urun_id == urun_id,
                StokBakiye.magaza_id == magaza_id
            )
            
            if depo_id:
                query = query.filter(StokBakiye.depo_id == depo_id)
            else:
                query = query.filter(StokBakiye.depo_id.is_(None))
            
            # Kilit uygula
            bakiye = query.with_for_update(nowait=False).first()
            
            if not bakiye:
                return Decimal('0.0000')
            
            return bakiye.kullanilabilir_miktar
            
        except Exception as e:
            session.rollback()
            raise EsZamanliErisimError(f"Stok kilitleme hatası: {str(e)}")
        finally:
            session.close()
    
    def _model_to_dto(self, hareket: StokHareket) -> StokHareketDTO:
        """Model'i DTO'ya çevirir"""
        return StokHareketDTO(
            id=hareket.id,
            urun_id=hareket.urun_id,
            magaza_id=hareket.magaza_id,
            depo_id=hareket.depo_id,
            hareket_tipi=hareket.hareket_tipi,
            miktar=hareket.miktar,
            birim_fiyat=hareket.birim_fiyat,
            toplam_tutar=hareket.toplam_tutar,
            referans_tablo=hareket.referans_tablo,
            referans_id=hareket.referans_id,
            aciklama=hareket.aciklama,
            kullanici_id=hareket.kullanici_id,
            olusturma_tarihi=hareket.olusturma_tarihi
        )