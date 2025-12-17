# Version: 0.1.0
# Last Update: 2024-12-16
# Module: satis_belgeleri.modeller.belge_satiri
# Description: Belge satırı modeli
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Belge Satırı Modeli

Bu modül belge satırı modelini içerir.
Satır bazlı hesaplamalar ve doğrulama mantığı içerir.
"""

from decimal import Decimal
from typing import Optional

from ....veritabani.modeller.belgeler import BelgeSatiri as BelgeSatiriDB


class BelgeSatiri:
    """
    Belge satırı iş modeli
    
    Bu sınıf belge satırı iş kurallarını ve hesaplama mantığını içerir.
    """
    
    def __init__(
        self,
        satir_id: Optional[int] = None,
        belge_id: Optional[int] = None,
        urun_id: Optional[int] = None,
        sira_no: Optional[int] = None,
        miktar: Decimal = Decimal('1.0000'),
        birim_fiyat: Decimal = Decimal('0.0000'),
        kdv_orani: Decimal = Decimal('18.00'),
        satir_tutari: Optional[Decimal] = None,
        kdv_tutari: Optional[Decimal] = None,
        satir_toplami: Optional[Decimal] = None
    ):
        self.satir_id = satir_id
        self.belge_id = belge_id
        self.urun_id = urun_id
        self.sira_no = sira_no
        self.miktar = miktar
        self.birim_fiyat = birim_fiyat
        self.kdv_orani = kdv_orani
        
        # Tutarları hesapla
        self._tutarlari_hesapla()
    
    def _tutarlari_hesapla(self) -> None:
        """Satır tutarlarını hesapla"""
        # Satır tutarı = miktar * birim_fiyat
        self.satir_tutari = self.miktar * self.birim_fiyat
        
        # KDV tutarı = satır_tutarı * (kdv_oranı / 100)
        self.kdv_tutari = self.satir_tutari * (self.kdv_orani / Decimal('100'))
        
        # Satır toplamı = satır_tutarı + kdv_tutarı
        self.satir_toplami = self.satir_tutari + self.kdv_tutari
    
    def miktar_guncelle(self, yeni_miktar: Decimal) -> None:
        """Miktarı güncelle ve tutarları yeniden hesapla"""
        if yeni_miktar <= 0:
            raise ValueError("Miktar sıfırdan büyük olmalıdır")
        
        self.miktar = yeni_miktar
        self._tutarlari_hesapla()
    
    def birim_fiyat_guncelle(self, yeni_fiyat: Decimal) -> None:
        """Birim fiyatı güncelle ve tutarları yeniden hesapla"""
        if yeni_fiyat < 0:
            raise ValueError("Birim fiyat negatif olamaz")
        
        self.birim_fiyat = yeni_fiyat
        self._tutarlari_hesapla()
    
    def kdv_orani_guncelle(self, yeni_oran: Decimal) -> None:
        """KDV oranını güncelle ve tutarları yeniden hesapla"""
        if yeni_oran < 0 or yeni_oran > 100:
            raise ValueError("KDV oranı 0-100 arasında olmalıdır")
        
        self.kdv_orani = yeni_oran
        self._tutarlari_hesapla()
    
    def dogrula(self) -> list[str]:
        """Satır doğrulaması yap, hata listesi döndür"""
        hatalar = []
        
        # Zorunlu alanlar
        if not self.urun_id:
            hatalar.append("Ürün ID zorunludur")
        
        if self.miktar <= 0:
            hatalar.append("Miktar sıfırdan büyük olmalıdır")
        
        if self.birim_fiyat < 0:
            hatalar.append("Birim fiyat negatif olamaz")
        
        if self.kdv_orani < 0 or self.kdv_orani > 100:
            hatalar.append("KDV oranı 0-100 arasında olmalıdır")
        
        return hatalar
    
    @classmethod
    def from_db_model(cls, db_model: BelgeSatiriDB) -> 'BelgeSatiri':
        """Veritabanı modelinden iş modeli oluştur"""
        return cls(
            satir_id=db_model.id,
            belge_id=db_model.belge_id,
            urun_id=db_model.urun_id,
            sira_no=db_model.sira_no,
            miktar=db_model.miktar,
            birim_fiyat=db_model.birim_fiyat,
            kdv_orani=db_model.kdv_orani,
            satir_tutari=db_model.satir_tutari,
            kdv_tutari=db_model.kdv_tutari,
            satir_toplami=db_model.satir_toplami
        )
    
    def to_db_model(self) -> BelgeSatiriDB:
        """İş modelinden veritabanı modeli oluştur"""
        return BelgeSatiriDB(
            id=self.satir_id,
            belge_id=self.belge_id,
            urun_id=self.urun_id,
            sira_no=self.sira_no,
            miktar=self.miktar,
            birim_fiyat=self.birim_fiyat,
            kdv_orani=self.kdv_orani,
            satir_tutari=self.satir_tutari,
            kdv_tutari=self.kdv_tutari,
            satir_toplami=self.satir_toplami
        )
    
    def __repr__(self) -> str:
        return f"<BelgeSatiri(id={self.satir_id}, urun_id={self.urun_id}, miktar={self.miktar})>"