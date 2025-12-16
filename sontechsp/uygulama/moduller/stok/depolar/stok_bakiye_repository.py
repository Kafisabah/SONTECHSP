# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.depolar.stok_bakiye_repository
# Description: Stok bakiye repository implementasyonu
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Stok Bakiye Repository

Bu modül stok bakiye veri erişim işlemlerini gerçekleştirir.
Atomik bakiye güncelleme ve rezervasyon işlemleri yapar.
"""

from typing import Optional, List
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from sontechsp.uygulama.veritabani.modeller.stok import StokBakiye
from sontechsp.uygulama.veritabani.baglanti import VeriTabaniBaglanti
from ..hatalar import StokYetersizError
from ..dto import StokBakiyeDTO
from .arayuzler import IStokBakiyeRepository


class StokBakiyeRepository(IStokBakiyeRepository):
    """Stok bakiye repository implementasyonu"""
    
    def __init__(self):
        self.db = VeriTabaniBaglanti()
    
    def bakiye_getir(self, urun_id: int, magaza_id: int, 
                    depo_id: Optional[int] = None) -> Decimal:
        """Stok bakiyesini getirir"""
        session = self.db.oturum_olustur()
        try:
            query = session.query(StokBakiye).filter(
                StokBakiye.urun_id == urun_id,
                StokBakiye.magaza_id == magaza_id
            )
            
            if depo_id:
                query = query.filter(StokBakiye.depo_id == depo_id)
            else:
                query = query.filter(StokBakiye.depo_id.is_(None))
            
            bakiye = query.first()
            return bakiye.kullanilabilir_miktar if bakiye else Decimal('0.0000')
            
        finally:
            session.close()
    
    def bakiye_guncelle(self, urun_id: int, magaza_id: int, 
                       miktar_degisimi: Decimal, depo_id: Optional[int] = None) -> bool:
        """Stok bakiyesini günceller"""
        session = self.db.oturum_olustur()
        try:
            # Mevcut bakiyeyi bul veya oluştur
            query = session.query(StokBakiye).filter(
                StokBakiye.urun_id == urun_id,
                StokBakiye.magaza_id == magaza_id
            )
            
            if depo_id:
                query = query.filter(StokBakiye.depo_id == depo_id)
            else:
                query = query.filter(StokBakiye.depo_id.is_(None))
            
            bakiye = query.first()
            
            if not bakiye:
                # Yeni bakiye kaydı oluştur
                bakiye = StokBakiye(
                    urun_id=urun_id,
                    magaza_id=magaza_id,
                    depo_id=depo_id,
                    miktar=Decimal('0.0000'),
                    rezerve_miktar=Decimal('0.0000'),
                    kullanilabilir_miktar=Decimal('0.0000')
                )
                session.add(bakiye)
            
            # Bakiyeyi güncelle
            bakiye.miktar += miktar_degisimi
            bakiye.kullanilabilir_miktar = bakiye.miktar - bakiye.rezerve_miktar
            
            session.commit()
            return True
            
        except IntegrityError:
            session.rollback()
            return False
        finally:
            session.close()
    
    def rezervasyon_yap(self, urun_id: int, magaza_id: int, 
                       miktar: Decimal, depo_id: Optional[int] = None) -> bool:
        """Stok rezervasyonu yapar"""
        session = self.db.oturum_olustur()
        try:
            query = session.query(StokBakiye).filter(
                StokBakiye.urun_id == urun_id,
                StokBakiye.magaza_id == magaza_id
            )
            
            if depo_id:
                query = query.filter(StokBakiye.depo_id == depo_id)
            else:
                query = query.filter(StokBakiye.depo_id.is_(None))
            
            bakiye = query.with_for_update().first()
            
            if not bakiye:
                raise StokYetersizError(
                    "Stok bakiyesi bulunamadı",
                    f"urun_id:{urun_id}",
                    Decimal('0.0000'),
                    miktar
                )
            
            # Kullanılabilir stok kontrolü
            if bakiye.kullanilabilir_miktar < miktar:
                raise StokYetersizError(
                    "Yetersiz stok",
                    f"urun_id:{urun_id}",
                    bakiye.kullanilabilir_miktar,
                    miktar
                )
            
            # Rezervasyon yap
            bakiye.rezerve_miktar += miktar
            bakiye.kullanilabilir_miktar = bakiye.miktar - bakiye.rezerve_miktar
            
            session.commit()
            return True
            
        except StokYetersizError:
            session.rollback()
            raise
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()
    
    def rezervasyon_iptal(self, urun_id: int, magaza_id: int, 
                         miktar: Decimal, depo_id: Optional[int] = None) -> bool:
        """Stok rezervasyonunu iptal eder"""
        session = self.db.oturum_olustur()
        try:
            query = session.query(StokBakiye).filter(
                StokBakiye.urun_id == urun_id,
                StokBakiye.magaza_id == magaza_id
            )
            
            if depo_id:
                query = query.filter(StokBakiye.depo_id == depo_id)
            else:
                query = query.filter(StokBakiye.depo_id.is_(None))
            
            bakiye = query.with_for_update().first()
            
            if not bakiye:
                return False
            
            # Rezervasyon iptal et
            bakiye.rezerve_miktar = max(Decimal('0.0000'), bakiye.rezerve_miktar - miktar)
            bakiye.kullanilabilir_miktar = bakiye.miktar - bakiye.rezerve_miktar
            
            session.commit()
            return True
            
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()
    def tum_bakiyeler_getir(self, magaza_id: Optional[int] = None, 
                           depo_id: Optional[int] = None) -> List[StokBakiyeDTO]:
        """Tüm stok bakiyelerini getirir"""
        session = self.db.oturum_olustur()
        try:
            query = session.query(StokBakiye)
            
            if magaza_id:
                query = query.filter(StokBakiye.magaza_id == magaza_id)
            
            if depo_id:
                query = query.filter(StokBakiye.depo_id == depo_id)
            
            bakiyeler = query.all()
            
            # Model'den DTO'ya dönüştür
            dto_listesi = []
            for bakiye in bakiyeler:
                dto = StokBakiyeDTO(
                    id=bakiye.id,
                    urun_id=bakiye.urun_id,
                    magaza_id=bakiye.magaza_id,
                    depo_id=bakiye.depo_id,
                    miktar=bakiye.miktar,
                    rezerve_miktar=bakiye.rezerve_miktar,
                    kullanilabilir_miktar=bakiye.kullanilabilir_miktar,
                    ortalama_maliyet=bakiye.ortalama_maliyet,
                    son_alis_fiyati=bakiye.son_alis_fiyati,
                    son_hareket_tarihi=bakiye.son_hareket_tarihi,
                    olusturma_tarihi=bakiye.olusturma_tarihi,
                    guncelleme_tarihi=bakiye.guncelleme_tarihi
                )
                dto_listesi.append(dto)
            
            return dto_listesi
            
        finally:
            session.close()