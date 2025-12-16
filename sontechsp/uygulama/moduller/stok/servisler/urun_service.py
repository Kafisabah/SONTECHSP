# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.servisler.urun_service
# Description: Ürün servis implementasyonu
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Ürün Servisi

Bu modül ürün iş kurallarını uygular.
Repository katmanını kullanarak ürün işlemlerini gerçekleştirir.
"""

from typing import List, Optional

from ..dto import UrunDTO
from ..depolar.urun_repository import UrunRepository
from ..hatalar import UrunValidationError
from .arayuzler import IUrunService


class UrunService(IUrunService):
    """Ürün servis implementasyonu"""
    
    def __init__(self, urun_repository: Optional[UrunRepository] = None):
        self.urun_repository = urun_repository or UrunRepository()
    
    def urun_ekle(self, urun: UrunDTO) -> int:
        """Yeni ürün ekler"""
        # İş kuralları doğrulaması
        self._urun_is_kurallari_dogrula(urun)
        
        # Repository'ye yönlendir
        return self.urun_repository.ekle(urun)
    
    def urun_guncelle(self, urun_id: int, urun: UrunDTO) -> bool:
        """Ürün günceller"""
        if urun_id <= 0:
            raise UrunValidationError("Geçersiz ürün ID")
        
        # İş kuralları doğrulaması
        self._urun_is_kurallari_dogrula(urun)
        
        # Repository'ye yönlendir
        return self.urun_repository.guncelle(urun_id, urun)
    
    def urun_sil(self, urun_id: int) -> bool:
        """Ürün siler"""
        if urun_id <= 0:
            raise UrunValidationError("Geçersiz ürün ID")
        
        # Repository'ye yönlendir (stok hareketi kontrolü repository'de)
        return self.urun_repository.sil(urun_id)
    
    def urun_ara(self, arama_terimi: str) -> List[UrunDTO]:
        """Ürün arar"""
        if not arama_terimi or len(arama_terimi.strip()) < 2:
            raise UrunValidationError("Arama terimi en az 2 karakter olmalıdır")
        
        # Repository'ye yönlendir
        return self.urun_repository.ara(arama_terimi.strip())
    
    def _urun_is_kurallari_dogrula(self, urun: UrunDTO) -> None:
        """Ürün iş kuralları doğrulaması"""
        # DTO doğrulaması
        hatalar = urun.validate()
        if hatalar:
            raise UrunValidationError("Ürün doğrulama hatası", hatalar)
        
        # İş kuralları
        if urun.minimum_stok and urun.maksimum_stok:
            if urun.minimum_stok > urun.maksimum_stok:
                raise UrunValidationError("Minimum stok maksimum stoktan büyük olamaz")
        
        # Fiyat kontrolleri
        if urun.alis_fiyati and urun.alis_fiyati < 0:
            raise UrunValidationError("Alış fiyatı negatif olamaz")
        
        if urun.satis_fiyati and urun.satis_fiyati < 0:
            raise UrunValidationError("Satış fiyatı negatif olamaz")