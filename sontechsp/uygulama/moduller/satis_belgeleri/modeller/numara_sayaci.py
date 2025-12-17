# Version: 0.1.0
# Last Update: 2024-12-16
# Module: satis_belgeleri.modeller.numara_sayaci
# Description: Numara sayacı modeli
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Numara Sayacı Modeli

Bu modül belge numarası üretimi için sayaç modelini içerir.
"""

from typing import Optional

from ....veritabani.modeller.belgeler import NumaraSayaci as NumaraSayaciDB
from .satis_belgesi import BelgeTuru


class NumaraSayaci:
    """
    Numara sayacı iş modeli
    
    Bu sınıf belge numarası üretimi için sayaç mantığını içerir.
    """
    
    def __init__(
        self,
        sayac_id: Optional[int] = None,
        magaza_id: Optional[int] = None,
        belge_turu: Optional[BelgeTuru] = None,
        yil: Optional[int] = None,
        ay: Optional[int] = None,
        son_numara: int = 0
    ):
        self.sayac_id = sayac_id
        self.magaza_id = magaza_id
        self.belge_turu = belge_turu
        self.yil = yil
        self.ay = ay
        self.son_numara = son_numara
    
    def sonraki_numara(self) -> int:
        """Sonraki numarayı al ve sayacı artır"""
        self.son_numara += 1
        return self.son_numara
    
    def numara_formatla(self, magaza_kodu: str, numara: int) -> str:
        """
        Belge numarasını formatla
        Format: MGZ-YYYY-MM-NNNN
        """
        return f"{magaza_kodu}-{self.yil:04d}-{self.ay:02d}-{numara:04d}"
    
    def sifirla(self) -> None:
        """Sayacı sıfırla (yeni ay için)"""
        self.son_numara = 0
    
    def dogrula(self) -> list[str]:
        """Sayaç doğrulaması yap, hata listesi döndür"""
        hatalar = []
        
        if not self.magaza_id:
            hatalar.append("Mağaza ID zorunludur")
        
        if not self.belge_turu:
            hatalar.append("Belge türü zorunludur")
        
        if not self.yil or self.yil < 2000 or self.yil > 9999:
            hatalar.append("Geçerli bir yıl belirtilmelidir")
        
        if not self.ay or self.ay < 1 or self.ay > 12:
            hatalar.append("Ay 1-12 arasında olmalıdır")
        
        if self.son_numara < 0:
            hatalar.append("Son numara negatif olamaz")
        
        return hatalar
    
    @classmethod
    def from_db_model(cls, db_model: NumaraSayaciDB) -> 'NumaraSayaci':
        """Veritabanı modelinden iş modeli oluştur"""
        return cls(
            sayac_id=db_model.id,
            magaza_id=db_model.magaza_id,
            belge_turu=BelgeTuru(db_model.belge_turu),
            yil=db_model.yil,
            ay=db_model.ay,
            son_numara=db_model.son_numara
        )
    
    def to_db_model(self) -> NumaraSayaciDB:
        """İş modelinden veritabanı modeli oluştur"""
        return NumaraSayaciDB(
            id=self.sayac_id,
            magaza_id=self.magaza_id,
            belge_turu=self.belge_turu.value if self.belge_turu else None,
            yil=self.yil,
            ay=self.ay,
            son_numara=self.son_numara
        )
    
    def __repr__(self) -> str:
        return f"<NumaraSayaci(magaza_id={self.magaza_id}, tur={self.belge_turu}, yil={self.yil}, ay={self.ay}, son={self.son_numara})>"