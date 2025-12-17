# Version: 0.1.0
# Last Update: 2024-12-16
# Module: satis_belgeleri.modeller.satis_belgesi
# Description: Satış belgesi ana modeli
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Satış Belgesi Modeli

Bu modül satış belgesi ana modelini içerir.
Veritabanı modelinden farklı olarak iş kuralları ve doğrulama mantığı içerir.
"""

from decimal import Decimal
from enum import Enum
from typing import List, Optional
from datetime import datetime

from ....veritabani.modeller.belgeler import (
    SatisBelgesi as SatisBelgesiDB,
    BelgeTuru as BelgeTuruEnum,
    BelgeDurumu as BelgeDurumuEnum
)


class BelgeTuru(Enum):
    """Belge türü enum"""
    SIPARIS = "SIPARIS"
    IRSALIYE = "IRSALIYE"
    FATURA = "FATURA"
    
    @classmethod
    def from_db_enum(cls, db_enum: BelgeTuruEnum) -> 'BelgeTuru':
        """Veritabanı enum'undan dönüştür"""
        return cls(db_enum.value)
    
    def to_db_enum(self) -> BelgeTuruEnum:
        """Veritabanı enum'una dönüştür"""
        return BelgeTuruEnum(self.value)


class BelgeDurumu(Enum):
    """Belge durumu enum"""
    TASLAK = "TASLAK"
    ONAYLANDI = "ONAYLANDI"
    FATURALANDI = "FATURALANDI"
    IPTAL = "IPTAL"
    
    @classmethod
    def from_db_enum(cls, db_enum: BelgeDurumuEnum) -> 'BelgeDurumu':
        """Veritabanı enum'undan dönüştür"""
        return cls(db_enum.value)
    
    def to_db_enum(self) -> BelgeDurumuEnum:
        """Veritabanı enum'una dönüştür"""
        return BelgeDurumuEnum(self.value)


class SatisBelgesi:
    """
    Satış belgesi iş modeli
    
    Bu sınıf satış belgesi iş kurallarını ve doğrulama mantığını içerir.
    Veritabanı modeli ile arayüz arasında köprü görevi görür.
    """
    
    def __init__(
        self,
        belge_id: Optional[int] = None,
        belge_numarasi: Optional[str] = None,
        belge_turu: BelgeTuru = BelgeTuru.SIPARIS,
        belge_durumu: BelgeDurumu = BelgeDurumu.TASLAK,
        magaza_id: Optional[int] = None,
        musteri_id: Optional[int] = None,
        olusturan_kullanici_id: Optional[int] = None,
        kaynak_belge_id: Optional[int] = None,
        kaynak_belge_turu: Optional[str] = None,
        toplam_tutar: Decimal = Decimal('0.0000'),
        kdv_tutari: Decimal = Decimal('0.0000'),
        genel_toplam: Decimal = Decimal('0.0000'),
        iptal_nedeni: Optional[str] = None,
        iptal_tarihi: Optional[datetime] = None,
        olusturma_tarihi: Optional[datetime] = None,
        guncelleme_tarihi: Optional[datetime] = None
    ):
        self.belge_id = belge_id
        self.belge_numarasi = belge_numarasi
        self.belge_turu = belge_turu
        self.belge_durumu = belge_durumu
        self.magaza_id = magaza_id
        self.musteri_id = musteri_id
        self.olusturan_kullanici_id = olusturan_kullanici_id
        self.kaynak_belge_id = kaynak_belge_id
        self.kaynak_belge_turu = kaynak_belge_turu
        self.toplam_tutar = toplam_tutar
        self.kdv_tutari = kdv_tutari
        self.genel_toplam = genel_toplam
        self.iptal_nedeni = iptal_nedeni
        self.iptal_tarihi = iptal_tarihi
        self.olusturma_tarihi = olusturma_tarihi
        self.guncelleme_tarihi = guncelleme_tarihi
        self._satirlar: List['BelgeSatiri'] = []
    
    @property
    def satirlar(self) -> List['BelgeSatiri']:
        """Belge satırları"""
        return self._satirlar.copy()
    
    def satir_ekle(self, satir: 'BelgeSatiri') -> None:
        """Belgeye satır ekle"""
        if satir.belge_id is None:
            satir.belge_id = self.belge_id
        
        # Sıra numarası ata
        if satir.sira_no is None:
            satir.sira_no = len(self._satirlar) + 1
        
        self._satirlar.append(satir)
        self._tutarlari_hesapla()
    
    def satir_sil(self, sira_no: int) -> bool:
        """Belirli sıra numarasındaki satırı sil"""
        for i, satir in enumerate(self._satirlar):
            if satir.sira_no == sira_no:
                del self._satirlar[i]
                self._sira_numaralarini_yeniden_duzenle()
                self._tutarlari_hesapla()
                return True
        return False
    
    def _sira_numaralarini_yeniden_duzenle(self) -> None:
        """Satır sıra numaralarını yeniden düzenle"""
        for i, satir in enumerate(self._satirlar):
            satir.sira_no = i + 1
    
    def _tutarlari_hesapla(self) -> None:
        """Belge tutarlarını hesapla"""
        self.toplam_tutar = Decimal('0.0000')
        self.kdv_tutari = Decimal('0.0000')
        
        for satir in self._satirlar:
            self.toplam_tutar += satir.satir_tutari
            self.kdv_tutari += satir.kdv_tutari
        
        self.genel_toplam = self.toplam_tutar + self.kdv_tutari
    
    def durum_degistirilebilir_mi(self, yeni_durum: BelgeDurumu) -> bool:
        """Belirtilen duruma geçiş yapılabilir mi kontrol et"""
        gecerli_gecisler = {
            BelgeDurumu.TASLAK: [BelgeDurumu.ONAYLANDI, BelgeDurumu.IPTAL],
            BelgeDurumu.ONAYLANDI: [BelgeDurumu.FATURALANDI, BelgeDurumu.IPTAL],
            BelgeDurumu.FATURALANDI: [BelgeDurumu.IPTAL],
            BelgeDurumu.IPTAL: []  # İptal durumundan çıkış yok
        }
        
        return yeni_durum in gecerli_gecisler.get(self.belge_durumu, [])
    
    def iptal_et(self, iptal_nedeni: str) -> None:
        """Belgeyi iptal et"""
        if not self.durum_degistirilebilir_mi(BelgeDurumu.IPTAL):
            raise ValueError(f"Belge {self.belge_durumu.value} durumundan iptal edilemez")
        
        self.belge_durumu = BelgeDurumu.IPTAL
        self.iptal_nedeni = iptal_nedeni
        self.iptal_tarihi = datetime.now()
    
    def dogrula(self) -> List[str]:
        """Belge doğrulaması yap, hata listesi döndür"""
        hatalar = []
        
        # Zorunlu alanlar
        if not self.magaza_id:
            hatalar.append("Mağaza ID zorunludur")
        
        if not self.olusturan_kullanici_id:
            hatalar.append("Oluşturan kullanıcı ID zorunludur")
        
        # Satır kontrolü
        if not self._satirlar:
            hatalar.append("En az bir satır bulunmalıdır")
        
        # Tutar kontrolü
        if self.genel_toplam < 0:
            hatalar.append("Genel toplam negatif olamaz")
        
        return hatalar
    
    @classmethod
    def from_db_model(cls, db_model: SatisBelgesiDB) -> 'SatisBelgesi':
        """Veritabanı modelinden iş modeli oluştur"""
        return cls(
            belge_id=db_model.id,
            belge_numarasi=db_model.belge_numarasi,
            belge_turu=BelgeTuru(db_model.belge_turu),
            belge_durumu=BelgeDurumu(db_model.belge_durumu),
            magaza_id=db_model.magaza_id,
            musteri_id=db_model.musteri_id,
            olusturan_kullanici_id=db_model.olusturan_kullanici_id,
            kaynak_belge_id=db_model.kaynak_belge_id,
            kaynak_belge_turu=db_model.kaynak_belge_turu,
            toplam_tutar=db_model.toplam_tutar,
            kdv_tutari=db_model.kdv_tutari,
            genel_toplam=db_model.genel_toplam,
            iptal_nedeni=db_model.iptal_nedeni,
            iptal_tarihi=db_model.iptal_tarihi,
            olusturma_tarihi=db_model.olusturma_tarihi,
            guncelleme_tarihi=db_model.guncelleme_tarihi
        )
    
    def to_db_model(self) -> SatisBelgesiDB:
        """İş modelinden veritabanı modeli oluştur"""
        return SatisBelgesiDB(
            id=self.belge_id,
            belge_numarasi=self.belge_numarasi,
            belge_turu=self.belge_turu.value,
            belge_durumu=self.belge_durumu.value,
            magaza_id=self.magaza_id,
            musteri_id=self.musteri_id,
            olusturan_kullanici_id=self.olusturan_kullanici_id,
            kaynak_belge_id=self.kaynak_belge_id,
            kaynak_belge_turu=self.kaynak_belge_turu,
            toplam_tutar=self.toplam_tutar,
            kdv_tutari=self.kdv_tutari,
            genel_toplam=self.genel_toplam,
            iptal_nedeni=self.iptal_nedeni,
            iptal_tarihi=self.iptal_tarihi
        )
    
    def __repr__(self) -> str:
        return f"<SatisBelgesi(id={self.belge_id}, numara={self.belge_numarasi}, tur={self.belge_turu.value})>"