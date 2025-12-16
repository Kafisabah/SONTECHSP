# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.servisler.barkod_service
# Description: Barkod servis implementasyonu
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Barkod Servisi

Bu modül barkod iş kurallarını uygular.
Repository katmanını kullanarak barkod işlemlerini gerçekleştirir.
"""

from typing import List, Optional
import re

from ..dto import BarkodDTO
from ..depolar.barkod_repository import BarkodRepository
from ..hatalar import BarkodValidationError
from .arayuzler import IBarkodService


class BarkodService(IBarkodService):
    """Barkod servis implementasyonu"""
    
    def __init__(self, barkod_repository: Optional[BarkodRepository] = None):
        self.barkod_repository = barkod_repository or BarkodRepository()
    
    def barkod_ekle(self, barkod: BarkodDTO) -> int:
        """Barkod ekler"""
        # İş kuralları doğrulaması
        self._barkod_is_kurallari_dogrula(barkod)
        
        # Barkod format doğrulaması
        self._barkod_format_dogrula(barkod.barkod)
        
        # Repository'ye yönlendir
        return self.barkod_repository.ekle(barkod)
    
    def barkod_sil(self, barkod_id: int) -> bool:
        """Barkod siler"""
        if barkod_id <= 0:
            raise BarkodValidationError("Geçersiz barkod ID")
        
        # Repository'ye yönlendir (minimum barkod kontrolü repository'de)
        return self.barkod_repository.sil(barkod_id)
    
    def barkod_ara(self, barkod: str) -> Optional[BarkodDTO]:
        """Barkod arar"""
        if not barkod or not barkod.strip():
            raise BarkodValidationError("Barkod boş olamaz")
        
        # Barkod format kontrolü
        temiz_barkod = barkod.strip()
        self._barkod_format_dogrula(temiz_barkod)
        
        # Repository'ye yönlendir
        return self.barkod_repository.barkod_ile_ara(temiz_barkod)
    
    def barkod_dogrula(self, barkod: str) -> bool:
        """Barkod format doğrulaması yapar"""
        try:
            self._barkod_format_dogrula(barkod)
            return True
        except BarkodValidationError:
            return False
    
    def urun_barkodlari_getir(self, urun_id: int) -> List[BarkodDTO]:
        """Ürünün tüm barkodlarını getirir"""
        if urun_id <= 0:
            raise BarkodValidationError("Geçersiz ürün ID")
        
        return self.barkod_repository.urun_barkodlari_getir(urun_id)
    
    def _barkod_is_kurallari_dogrula(self, barkod: BarkodDTO) -> None:
        """Barkod iş kuralları doğrulaması"""
        # DTO doğrulaması
        hatalar = barkod.validate()
        if hatalar:
            raise BarkodValidationError("Barkod doğrulama hatası", barkod.barkod)
        
        # İş kuralları
        if barkod.carpan <= 0:
            raise BarkodValidationError("Çarpan pozitif olmalıdır")
    
    def _barkod_format_dogrula(self, barkod: str) -> None:
        """Barkod format doğrulaması"""
        if not barkod:
            raise BarkodValidationError("Barkod boş olamaz")
        
        # Uzunluk kontrolü
        if len(barkod) < 8 or len(barkod) > 50:
            raise BarkodValidationError("Barkod 8-50 karakter arasında olmalıdır")
        
        # Sadece rakam kontrolü
        if not barkod.isdigit():
            raise BarkodValidationError("Barkod sadece rakamlardan oluşmalıdır")
        
        # EAN13 kontrolü (13 haneli ise)
        if len(barkod) == 13:
            self._ean13_kontrol_dogrula(barkod)
    
    def _ean13_kontrol_dogrula(self, barkod: str) -> None:
        """EAN13 kontrol hanesi doğrulaması"""
        if len(barkod) != 13:
            return
        
        try:
            # EAN13 kontrol hanesi algoritması
            toplam = 0
            for i in range(12):
                rakam = int(barkod[i])
                if i % 2 == 0:
                    toplam += rakam
                else:
                    toplam += rakam * 3
            
            kontrol_hanesi = (10 - (toplam % 10)) % 10
            
            if kontrol_hanesi != int(barkod[12]):
                raise BarkodValidationError("EAN13 kontrol hanesi hatalı")
                
        except (ValueError, IndexError):
            raise BarkodValidationError("Geçersiz EAN13 barkod formatı")