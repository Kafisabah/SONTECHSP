# Version: 0.1.0
# Last Update: 2024-12-17
# Module: kargo.depolar
# Description: Kargo modülü repository katmanı
# Changelog:
# - KargoDeposu class'ı eklendi
# - Temel CRUD metodları implement edildi
# - etiket_kaydi_olustur, etiket_getir, etiket_durum_guncelle metodları eklendi

"""
Kargo modülü repository katmanı.

Bu modül, kargo verilerinin veritabanı erişim işlemlerini içerir.
Tüm SQL sorguları ve ORM işlemleri burada yapılır.
"""

from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ...veritabani.modeller.kargo import KargoEtiketleri, KargoTakipleri
from .dto import KargoEtiketOlusturDTO
from .sabitler import EtiketDurumlari


class KargoDeposu:
    """
    Kargo verileri için repository sınıfı.
    
    Veritabanı erişim işlemlerini ve CRUD operasyonlarını yönetir.
    """
    
    def __init__(self, session: Session):
        """
        Repository'yi başlatır.
        
        Args:
            session: SQLAlchemy session
        """
        self.session = session
    
    def etiket_kaydi_olustur(self, dto: KargoEtiketOlusturDTO) -> KargoEtiketleri:
        """
        Yeni etiket kaydı oluşturur.
        
        Args:
            dto: Etiket oluşturma verisi
        
        Returns:
            KargoEtiketleri: Oluşturulan etiket kaydı
        
        Raises:
            IntegrityError: Benzersizlik kısıtlaması ihlali durumunda
        """
        etiket = KargoEtiketleri(
            kaynak_turu=dto.kaynak_turu,
            kaynak_id=dto.kaynak_id,
            tasiyici=dto.tasiyici,
            servis_kodu=dto.servis_kodu,
            alici_ad=dto.alici_ad,
            alici_telefon=dto.alici_telefon,
            alici_adres=dto.alici_adres,
            alici_il=dto.alici_il,
            alici_ilce=dto.alici_ilce,
            paket_agirlik_kg=dto.paket_agirlik_kg,
            durum=EtiketDurumlari.BEKLIYOR,
            deneme_sayisi=0
        )
        
        self.session.add(etiket)
        self.session.flush()  # ID'yi almak için flush
        
        return etiket
    
    def etiket_getir(self, etiket_id: int) -> Optional[KargoEtiketleri]:
        """
        ID ile etiket getirir.
        
        Args:
            etiket_id: Etiket ID'si
        
        Returns:
            Optional[KargoEtiketleri]: Etiket kaydı veya None
        """
        return self.session.query(KargoEtiketleri).filter(
            KargoEtiketleri.id == etiket_id
        ).first()
    
    def etiket_durum_guncelle(self, etiket_id: int, durum: str,
                             mesaj: Optional[str] = None,
                             takip_no: Optional[str] = None) -> bool:
        """
        Etiket durumunu günceller.
        
        Args:
            etiket_id: Etiket ID'si
            durum: Yeni durum
            mesaj: Hata/bilgi mesajı
            takip_no: Takip numarası
        
        Returns:
            bool: Güncelleme başarılı ise True
        """
        etiket = self.etiket_getir(etiket_id)
        if not etiket:
            return False
        
        etiket.durum = durum
        etiket.mesaj = mesaj
        etiket.guncellenme_zamani = datetime.now()
        
        if takip_no:
            etiket.takip_no = takip_no
        
        return True
    
    def deneme_sayisi_artir(self, etiket_id: int) -> bool:
        """
        Etiketin deneme sayısını artırır.
        
        Args:
            etiket_id: Etiket ID'si
        
        Returns:
            bool: Güncelleme başarılı ise True
        """
        etiket = self.etiket_getir(etiket_id)
        if not etiket:
            return False
        
        etiket.deneme_sayisi += 1
        etiket.guncellenme_zamani = datetime.now()
        
        return True
    
    def takip_kaydi_ekle(self, etiket_id: int, takip_no: str, durum: str,
                        aciklama: Optional[str] = None,
                        zaman: Optional[datetime] = None) -> KargoTakipleri:
        """
        Takip geçmişi kaydı ekler.
        
        Args:
            etiket_id: Etiket ID'si
            takip_no: Takip numarası
            durum: Takip durumu
            aciklama: Durum açıklaması
            zaman: Durum zamanı
        
        Returns:
            KargoTakipleri: Oluşturulan takip kaydı
        """
        takip = KargoTakipleri(
            etiket_id=etiket_id,
            takip_no=takip_no,
            durum=durum,
            aciklama=aciklama,
            zaman=zaman or datetime.now()
        )
        
        self.session.add(takip)
        self.session.flush()
        
        return takip
    
    def bekleyen_etiketleri_al(self, limit: int = 20) -> List[KargoEtiketleri]:
        """
        Yeniden deneme için bekleyen etiketleri getirir.
        
        Args:
            limit: Maksimum kayıt sayısı
        
        Returns:
            List[KargoEtiketleri]: Bekleyen etiketler listesi
        """
        return self.session.query(KargoEtiketleri).filter(
            KargoEtiketleri.durum.in_([
                EtiketDurumlari.BEKLIYOR,
                EtiketDurumlari.HATA
            ])
        ).order_by(
            KargoEtiketleri.olusturulma_zamani
        ).limit(limit).all()
    
    def etiket_kaynaktan_bul(self, kaynak_turu: str, kaynak_id: int,
                            tasiyici: str) -> Optional[KargoEtiketleri]:
        """
        Kaynak bilgileri ile etiket arar (benzersizlik kontrolü).
        
        Args:
            kaynak_turu: Kaynak türü
            kaynak_id: Kaynak ID'si
            tasiyici: Taşıyıcı kodu
        
        Returns:
            Optional[KargoEtiketleri]: Bulunan etiket veya None
        """
        return self.session.query(KargoEtiketleri).filter(
            KargoEtiketleri.kaynak_turu == kaynak_turu,
            KargoEtiketleri.kaynak_id == kaynak_id,
            KargoEtiketleri.tasiyici == tasiyici
        ).first()
    
    def etiket_takip_no_ile_bul(self, takip_no: str) -> Optional[KargoEtiketleri]:
        """
        Takip numarası ile etiket arar.
        
        Args:
            takip_no: Takip numarası
        
        Returns:
            Optional[KargoEtiketleri]: Bulunan etiket veya None
        """
        return self.session.query(KargoEtiketleri).filter(
            KargoEtiketleri.takip_no == takip_no
        ).first()
    
    def takip_gecmisi_getir(self, etiket_id: int) -> List[KargoTakipleri]:
        """
        Etiketin takip geçmişini getirir.
        
        Args:
            etiket_id: Etiket ID'si
        
        Returns:
            List[KargoTakipleri]: Takip geçmişi listesi
        """
        return self.session.query(KargoTakipleri).filter(
            KargoTakipleri.etiket_id == etiket_id
        ).order_by(
            KargoTakipleri.olusturulma_zamani.desc()
        ).all()
    
    def durum_bazli_etiketler(self, durum: str, 
                             limit: int = 100) -> List[KargoEtiketleri]:
        """
        Durum bazlı etiket listesi getirir.
        
        Args:
            durum: Etiket durumu
            limit: Maksimum kayıt sayısı
        
        Returns:
            List[KargoEtiketleri]: Etiket listesi
        """
        return self.session.query(KargoEtiketleri).filter(
            KargoEtiketleri.durum == durum
        ).order_by(
            KargoEtiketleri.olusturulma_zamani.desc()
        ).limit(limit).all()