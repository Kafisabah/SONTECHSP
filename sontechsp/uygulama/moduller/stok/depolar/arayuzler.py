# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.depolar.arayuzler
# Description: Stok repository arayüzleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Stok Repository Arayüzleri

Bu modül stok modülünün repository arayüzlerini içerir.
Dependency injection ve test edilebilirlik için kullanılır.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from decimal import Decimal

from ..dto import UrunDTO, BarkodDTO, StokHareketDTO, StokHareketFiltreDTO, StokBakiyeDTO


class IUrunRepository(ABC):
    """Ürün repository arayüzü"""
    
    @abstractmethod
    def ekle(self, urun: UrunDTO) -> int:
        """Yeni ürün ekler"""
        pass
    
    @abstractmethod
    def guncelle(self, urun_id: int, urun: UrunDTO) -> bool:
        """Ürün bilgilerini günceller"""
        pass
    
    @abstractmethod
    def sil(self, urun_id: int) -> bool:
        """Ürünü siler (stok hareketi kontrolü ile)"""
        pass
    
    @abstractmethod
    def id_ile_getir(self, urun_id: int) -> Optional[UrunDTO]:
        """ID ile ürün getirir"""
        pass
    
    @abstractmethod
    def stok_kodu_ile_getir(self, stok_kodu: str) -> Optional[UrunDTO]:
        """Stok kodu ile ürün getirir"""
        pass
    
    @abstractmethod
    def ara(self, arama_terimi: str) -> List[UrunDTO]:
        """Ürün adı veya kodu ile arama yapar"""
        pass


class IBarkodRepository(ABC):
    """Barkod repository arayüzü"""
    
    @abstractmethod
    def ekle(self, barkod: BarkodDTO) -> int:
        """Yeni barkod ekler"""
        pass
    
    @abstractmethod
    def sil(self, barkod_id: int) -> bool:
        """Barkod siler (minimum barkod kontrolü ile)"""
        pass
    
    @abstractmethod
    def barkod_ile_ara(self, barkod: str) -> Optional[BarkodDTO]:
        """Barkod ile arama yapar"""
        pass
    
    @abstractmethod
    def urun_barkodlari_getir(self, urun_id: int) -> List[BarkodDTO]:
        """Ürünün tüm barkodlarını getirir"""
        pass


class IStokHareketRepository(ABC):
    """Stok hareket repository arayüzü"""
    
    @abstractmethod
    def hareket_ekle(self, hareket: StokHareketDTO) -> int:
        """Yeni stok hareketi ekler"""
        pass
    
    @abstractmethod
    def hareket_listesi(self, filtre: StokHareketFiltreDTO) -> List[StokHareketDTO]:
        """Filtrelenmiş hareket listesi getirir"""
        pass
    
    @abstractmethod
    def kilitle_ve_bakiye_getir(self, urun_id: int, magaza_id: int, 
                               depo_id: Optional[int] = None) -> Decimal:
        """Stok bakiyesini kilitler ve getirir (SELECT FOR UPDATE)"""
        pass


class IStokBakiyeRepository(ABC):
    """Stok bakiye repository arayüzü"""
    
    @abstractmethod
    def bakiye_getir(self, urun_id: int, magaza_id: int, 
                    depo_id: Optional[int] = None) -> Decimal:
        """Stok bakiyesini getirir"""
        pass
    
    @abstractmethod
    def bakiye_guncelle(self, urun_id: int, magaza_id: int, 
                       miktar_degisimi: Decimal, depo_id: Optional[int] = None) -> bool:
        """Stok bakiyesini günceller"""
        pass
    
    @abstractmethod
    def rezervasyon_yap(self, urun_id: int, magaza_id: int, 
                       miktar: Decimal, depo_id: Optional[int] = None) -> bool:
        """Stok rezervasyonu yapar"""
        pass
    
    @abstractmethod
    def rezervasyon_iptal(self, urun_id: int, magaza_id: int, 
                         miktar: Decimal, depo_id: Optional[int] = None) -> bool:
        """Stok rezervasyonunu iptal eder"""
        pass
    
    @abstractmethod
    def tum_bakiyeler_getir(self, magaza_id: Optional[int] = None, 
                           depo_id: Optional[int] = None) -> List[StokBakiyeDTO]:
        """Tüm stok bakiyelerini getirir"""
        pass