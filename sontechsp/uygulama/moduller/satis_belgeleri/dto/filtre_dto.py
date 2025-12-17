# Version: 0.1.0
# Last Update: 2024-12-17
# Module: satis_belgeleri.dto.filtre_dto
# Description: Filtreleme ve sayfalama DTO'ları
# Changelog:
# - 0.1.0: İlk sürüm - Filtre ve sayfalama DTO'ları

"""
Filtreleme ve Sayfalama DTO Sınıfları

Bu modül belge sorgulama işlemleri için filtreleme ve sayfalama DTO'larını içerir.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Generic, TypeVar

from ..modeller import BelgeTuru, BelgeDurumu

T = TypeVar('T')


@dataclass
class BelgeFiltresiDTO:
    """Belge filtreleme kriterleri"""
    
    belge_turu: Optional[BelgeTuru] = None
    belge_durumu: Optional[BelgeDurumu] = None
    magaza_id: Optional[int] = None
    musteri_id: Optional[int] = None
    baslangic_tarihi: Optional[datetime] = None
    bitis_tarihi: Optional[datetime] = None
    belge_numarasi: Optional[str] = None
    olusturan_kullanici_id: Optional[int] = None
    
    def to_dict(self) -> dict:
        """Filtreyi dictionary'ye çevir"""
        return {
            'belge_turu': self.belge_turu.value if self.belge_turu else None,
            'belge_durumu': self.belge_durumu.value if self.belge_durumu else None,
            'magaza_id': self.magaza_id,
            'musteri_id': self.musteri_id,
            'baslangic_tarihi': self.baslangic_tarihi.isoformat() if self.baslangic_tarihi else None,
            'bitis_tarihi': self.bitis_tarihi.isoformat() if self.bitis_tarihi else None,
            'belge_numarasi': self.belge_numarasi,
            'olusturan_kullanici_id': self.olusturan_kullanici_id
        }


@dataclass
class SayfalamaDTO:
    """Sayfalama parametreleri"""
    
    sayfa: int = 1
    sayfa_boyutu: int = 20
    siralama_alani: Optional[str] = None
    siralama_yonu: str = 'ASC'  # ASC veya DESC
    
    @property
    def offset(self) -> int:
        """Offset değerini hesapla"""
        return (self.sayfa - 1) * self.sayfa_boyutu
    
    @property
    def limit(self) -> int:
        """Limit değerini döndür"""
        return self.sayfa_boyutu
    
    def to_dict(self) -> dict:
        """Sayfalamayı dictionary'ye çevir"""
        return {
            'sayfa': self.sayfa,
            'sayfa_boyutu': self.sayfa_boyutu,
            'siralama_alani': self.siralama_alani,
            'siralama_yonu': self.siralama_yonu,
            'offset': self.offset,
            'limit': self.limit
        }


@dataclass
class SayfaliSonucDTO(Generic[T]):
    """Sayfalı sorgu sonucu"""
    
    veriler: List[T]
    toplam_kayit: int
    sayfa: int
    sayfa_boyutu: int
    toplam_sayfa: int
    
    def __init__(self, veriler: List[T], toplam_kayit: int, sayfa: int, sayfa_boyutu: int):
        self.veriler = veriler
        self.toplam_kayit = toplam_kayit
        self.sayfa = sayfa
        self.sayfa_boyutu = sayfa_boyutu
        self.toplam_sayfa = (toplam_kayit + sayfa_boyutu - 1) // sayfa_boyutu
    
    @property
    def has_next(self) -> bool:
        """Sonraki sayfa var mı?"""
        return self.sayfa < self.toplam_sayfa
    
    @property
    def has_previous(self) -> bool:
        """Önceki sayfa var mı?"""
        return self.sayfa > 1
    
    def to_dict(self) -> dict:
        """Sonucu dictionary'ye çevir"""
        return {
            'veriler': [item.to_dict() if hasattr(item, 'to_dict') else item for item in self.veriler],
            'toplam_kayit': self.toplam_kayit,
            'sayfa': self.sayfa,
            'sayfa_boyutu': self.sayfa_boyutu,
            'toplam_sayfa': self.toplam_sayfa,
            'has_next': self.has_next,
            'has_previous': self.has_previous
        }