# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.depolar.urun_repository
# Description: Ürün repository implementasyonu
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Ürün Repository

Bu modül ürün veri erişim işlemlerini gerçekleştirir.
Ürün CRUD işlemleri ve iş kuralları kontrolü yapar.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

from sontechsp.uygulama.veritabani.modeller.stok import Urun, StokHareket
from sontechsp.uygulama.veritabani.baglanti import VeriTabaniBaglanti
from ..dto import UrunDTO
from ..hatalar import UrunValidationError
from .arayuzler import IUrunRepository


class UrunRepository(IUrunRepository):
    """Ürün repository implementasyonu"""
    
    def __init__(self):
        self.db = VeriTabaniBaglanti()
    
    def ekle(self, urun: UrunDTO) -> int:
        """Yeni ürün ekler"""
        # Doğrulama
        hatalar = urun.validate()
        if hatalar:
            raise UrunValidationError("Ürün doğrulama hatası", hatalar)
        
        session = self.db.oturum_olustur()
        try:
            # Stok kodu benzersizlik kontrolü
            mevcut = session.query(Urun).filter_by(urun_kodu=urun.urun_kodu).first()
            if mevcut:
                raise UrunValidationError(f"'{urun.urun_kodu}' stok kodu zaten kullanılıyor")
            
            # Yeni ürün oluştur
            yeni_urun = Urun(
                urun_kodu=urun.urun_kodu,
                urun_adi=urun.urun_adi,
                aciklama=urun.aciklama,
                kategori=urun.kategori,
                alt_kategori=urun.alt_kategori,
                marka=urun.marka,
                birim=urun.birim,
                alis_fiyati=urun.alis_fiyati,
                satis_fiyati=urun.satis_fiyati,
                kdv_orani=urun.kdv_orani,
                stok_takip=urun.stok_takip,
                negatif_stok_izin=urun.negatif_stok_izin,
                minimum_stok=urun.minimum_stok,
                maksimum_stok=urun.maksimum_stok,
                aktif=urun.aktif
            )
            
            session.add(yeni_urun)
            session.commit()
            return yeni_urun.id
            
        except IntegrityError as e:
            session.rollback()
            raise UrunValidationError(f"Ürün kaydedilemedi: {str(e)}")
        finally:
            session.close()
    
    def guncelle(self, urun_id: int, urun: UrunDTO) -> bool:
        """Ürün bilgilerini günceller"""
        # Doğrulama
        hatalar = urun.validate()
        if hatalar:
            raise UrunValidationError("Ürün doğrulama hatası", hatalar)
        
        session = self.db.oturum_olustur()
        try:
            mevcut_urun = session.query(Urun).filter_by(id=urun_id).first()
            if not mevcut_urun:
                return False
            
            # Stok kodu benzersizlik kontrolü (kendisi hariç)
            if mevcut_urun.urun_kodu != urun.urun_kodu:
                diger = session.query(Urun).filter(
                    Urun.urun_kodu == urun.urun_kodu,
                    Urun.id != urun_id
                ).first()
                if diger:
                    raise UrunValidationError(f"'{urun.urun_kodu}' stok kodu zaten kullanılıyor")
            
            # Güncelleme
            mevcut_urun.urun_kodu = urun.urun_kodu
            mevcut_urun.urun_adi = urun.urun_adi
            mevcut_urun.aciklama = urun.aciklama
            mevcut_urun.kategori = urun.kategori
            mevcut_urun.alt_kategori = urun.alt_kategori
            mevcut_urun.marka = urun.marka
            mevcut_urun.birim = urun.birim
            mevcut_urun.alis_fiyati = urun.alis_fiyati
            mevcut_urun.satis_fiyati = urun.satis_fiyati
            mevcut_urun.kdv_orani = urun.kdv_orani
            mevcut_urun.stok_takip = urun.stok_takip
            mevcut_urun.negatif_stok_izin = urun.negatif_stok_izin
            mevcut_urun.minimum_stok = urun.minimum_stok
            mevcut_urun.maksimum_stok = urun.maksimum_stok
            mevcut_urun.aktif = urun.aktif
            
            session.commit()
            return True
            
        except IntegrityError as e:
            session.rollback()
            raise UrunValidationError(f"Ürün güncellenemedi: {str(e)}")
        finally:
            session.close()
    
    def sil(self, urun_id: int) -> bool:
        """Ürünü siler (stok hareketi kontrolü ile)"""
        session = self.db.oturum_olustur()
        try:
            urun = session.query(Urun).filter_by(id=urun_id).first()
            if not urun:
                return False
            
            # Stok hareketi kontrolü
            hareket_sayisi = session.query(StokHareket).filter_by(urun_id=urun_id).count()
            if hareket_sayisi > 0:
                raise UrunValidationError(
                    f"'{urun.urun_kodu}' ürünü silinemez. Stok hareketi bulunuyor."
                )
            
            session.delete(urun)
            session.commit()
            return True
            
        finally:
            session.close()
    
    def id_ile_getir(self, urun_id: int) -> Optional[UrunDTO]:
        """ID ile ürün getirir"""
        session = self.db.oturum_olustur()
        try:
            urun = session.query(Urun).filter_by(id=urun_id).first()
            if not urun:
                return None
            
            return self._model_to_dto(urun)
            
        finally:
            session.close()
    
    def stok_kodu_ile_getir(self, stok_kodu: str) -> Optional[UrunDTO]:
        """Stok kodu ile ürün getirir"""
        session = self.db.oturum_olustur()
        try:
            urun = session.query(Urun).filter_by(urun_kodu=stok_kodu).first()
            if not urun:
                return None
            
            return self._model_to_dto(urun)
            
        finally:
            session.close()
    
    def ara(self, arama_terimi: str) -> List[UrunDTO]:
        """Ürün adı veya kodu ile arama yapar"""
        session = self.db.oturum_olustur()
        try:
            arama = f"%{arama_terimi}%"
            urunler = session.query(Urun).filter(
                or_(
                    Urun.urun_kodu.ilike(arama),
                    Urun.urun_adi.ilike(arama)
                )
            ).filter_by(aktif=True).limit(100).all()
            
            return [self._model_to_dto(urun) for urun in urunler]
            
        finally:
            session.close()
    
    def _model_to_dto(self, urun: Urun) -> UrunDTO:
        """Model'i DTO'ya çevirir"""
        return UrunDTO(
            id=urun.id,
            urun_kodu=urun.urun_kodu,
            urun_adi=urun.urun_adi,
            aciklama=urun.aciklama,
            kategori=urun.kategori,
            alt_kategori=urun.alt_kategori,
            marka=urun.marka,
            birim=urun.birim,
            alis_fiyati=urun.alis_fiyati,
            satis_fiyati=urun.satis_fiyati,
            kdv_orani=urun.kdv_orani,
            stok_takip=urun.stok_takip,
            negatif_stok_izin=urun.negatif_stok_izin,
            minimum_stok=urun.minimum_stok,
            maksimum_stok=urun.maksimum_stok,
            aktif=urun.aktif,
            olusturma_tarihi=urun.olusturma_tarihi,
            guncelleme_tarihi=urun.guncelleme_tarihi
        )