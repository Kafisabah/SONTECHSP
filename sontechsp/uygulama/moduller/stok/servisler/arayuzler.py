# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.servisler.arayuzler
# Description: Stok servis arayüzleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Stok Servis Arayüzleri

Bu modül stok modülünün servis arayüzlerini içerir.
İş kuralları ve dependency injection için kullanılır.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from decimal import Decimal

from ..dto import UrunDTO, BarkodDTO, StokHareketDTO


class IUrunService(ABC):
    """Ürün servis arayüzü"""
    
    @abstractmethod
    def urun_ekle(self, urun: UrunDTO) -> int:
        """Yeni ürün ekler"""
        pass
    
    @abstractmethod
    def urun_guncelle(self, urun_id: int, urun: UrunDTO) -> bool:
        """Ürün günceller"""
        pass
    
    @abstractmethod
    def urun_sil(self, urun_id: int) -> bool:
        """Ürün siler"""
        pass
    
    @abstractmethod
    def urun_ara(self, arama_terimi: str) -> List[UrunDTO]:
        """Ürün arar"""
        pass


class IBarkodService(ABC):
    """Barkod servis arayüzü"""
    
    @abstractmethod
    def barkod_ekle(self, barkod: BarkodDTO) -> int:
        """Barkod ekler"""
        pass
    
    @abstractmethod
    def barkod_sil(self, barkod_id: int) -> bool:
        """Barkod siler"""
        pass
    
    @abstractmethod
    def barkod_ara(self, barkod: str) -> Optional[BarkodDTO]:
        """Barkod arar"""
        pass


class IStokHareketService(ABC):
    """Stok hareket servis arayüzü"""
    
    @abstractmethod
    def stok_girisi(self, hareket: StokHareketDTO) -> int:
        """Stok giriş işlemi"""
        pass
    
    @abstractmethod
    def stok_cikisi(self, hareket: StokHareketDTO) -> int:
        """Stok çıkış işlemi"""
        pass


class INegatifStokKontrol(ABC):
    """Negatif stok kontrol arayüzü"""
    
    @abstractmethod
    def kontrol_yap(self, urun_id: int, talep_miktar: Decimal, 
                   mevcut_stok: Decimal) -> bool:
        """Negatif stok kontrolü yapar"""
        pass