# Version: 0.1.0
# Last Update: 2024-12-16
# Module: satis_belgeleri.modeller.belge_durum_gecmisi
# Description: Belge durum geçmişi modeli
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Belge Durum Geçmişi Modeli

Bu modül belge durum değişiklik geçmişi modelini içerir.
"""

from datetime import datetime
from typing import Optional

from ....veritabani.modeller.belgeler import BelgeDurumGecmisi as BelgeDurumGecmisiDB


class BelgeDurumGecmisi:
    """
    Belge durum geçmişi iş modeli
    
    Bu sınıf belge durum değişiklik geçmişi bilgilerini içerir.
    """
    
    def __init__(
        self,
        gecmis_id: Optional[int] = None,
        belge_id: Optional[int] = None,
        eski_durum: Optional[str] = None,
        yeni_durum: Optional[str] = None,
        degistiren_kullanici_id: Optional[int] = None,
        aciklama: Optional[str] = None,
        olusturma_tarihi: Optional[datetime] = None
    ):
        self.gecmis_id = gecmis_id
        self.belge_id = belge_id
        self.eski_durum = eski_durum
        self.yeni_durum = yeni_durum
        self.degistiren_kullanici_id = degistiren_kullanici_id
        self.aciklama = aciklama
        self.olusturma_tarihi = olusturma_tarihi or datetime.now()
    
    def dogrula(self) -> list[str]:
        """Geçmiş kaydı doğrulaması yap, hata listesi döndür"""
        hatalar = []
        
        # Zorunlu alanlar
        if not self.belge_id:
            hatalar.append("Belge ID zorunludur")
        
        if not self.yeni_durum:
            hatalar.append("Yeni durum zorunludur")
        
        if not self.degistiren_kullanici_id:
            hatalar.append("Değiştiren kullanıcı ID zorunludur")
        
        return hatalar
    
    @classmethod
    def from_db_model(cls, db_model: BelgeDurumGecmisiDB) -> 'BelgeDurumGecmisi':
        """Veritabanı modelinden iş modeli oluştur"""
        return cls(
            gecmis_id=db_model.id,
            belge_id=db_model.belge_id,
            eski_durum=db_model.eski_durum,
            yeni_durum=db_model.yeni_durum,
            degistiren_kullanici_id=db_model.degistiren_kullanici_id,
            aciklama=db_model.aciklama,
            olusturma_tarihi=db_model.olusturma_tarihi
        )
    
    def to_db_model(self) -> BelgeDurumGecmisiDB:
        """İş modelinden veritabanı modeli oluştur"""
        return BelgeDurumGecmisiDB(
            id=self.gecmis_id,
            belge_id=self.belge_id,
            eski_durum=self.eski_durum,
            yeni_durum=self.yeni_durum,
            degistiren_kullanici_id=self.degistiren_kullanici_id,
            aciklama=self.aciklama
        )
    
    def __repr__(self) -> str:
        return f"<BelgeDurumGecmisi(belge_id={self.belge_id}, {self.eski_durum}->{self.yeni_durum})>"