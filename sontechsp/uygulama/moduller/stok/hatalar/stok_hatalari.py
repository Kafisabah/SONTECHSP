# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.hatalar.stok_hatalari
# Description: Stok modülü hata sınıfları
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Stok Hata Sınıfları

Bu modül stok modülünün özel hata sınıflarını içerir.
İş kuralları ihlalleri ve doğrulama hataları için kullanılır.
"""

from typing import List, Optional
from decimal import Decimal


class StokHatasiBase(Exception):
    """Stok modülü temel hata sınıfı"""
    
    def __init__(self, mesaj: str, hata_kodu: Optional[str] = None):
        self.mesaj = mesaj
        self.hata_kodu = hata_kodu
        super().__init__(self.mesaj)


class UrunValidationError(StokHatasiBase):
    """Ürün doğrulama hatası"""
    
    def __init__(self, mesaj: str, dogrulama_hatalari: Optional[List[str]] = None):
        super().__init__(mesaj, "URUN_VALIDATION_ERROR")
        self.dogrulama_hatalari = dogrulama_hatalari or []


class BarkodValidationError(StokHatasiBase):
    """Barkod doğrulama hatası"""
    
    def __init__(self, mesaj: str, barkod: Optional[str] = None):
        super().__init__(mesaj, "BARKOD_VALIDATION_ERROR")
        self.barkod = barkod


class NegatifStokError(StokHatasiBase):
    """Negatif stok hatası"""
    
    def __init__(
        self, 
        mesaj: str, 
        urun_kodu: str,
        mevcut_stok: Decimal,
        talep_edilen_miktar: Decimal,
        limit: Optional[Decimal] = None
    ):
        super().__init__(mesaj, "NEGATIF_STOK_ERROR")
        self.urun_kodu = urun_kodu
        self.mevcut_stok = mevcut_stok
        self.talep_edilen_miktar = talep_edilen_miktar
        self.limit = limit


class StokYetersizError(StokHatasiBase):
    """Yetersiz stok hatası"""
    
    def __init__(
        self, 
        mesaj: str, 
        urun_kodu: str,
        kullanilabilir_stok: Decimal,
        talep_edilen_miktar: Decimal
    ):
        super().__init__(mesaj, "STOK_YETERSIZ_ERROR")
        self.urun_kodu = urun_kodu
        self.kullanilabilir_stok = kullanilabilir_stok
        self.talep_edilen_miktar = talep_edilen_miktar


class EsZamanliErisimError(StokHatasiBase):
    """Eş zamanlı erişim hatası"""
    
    def __init__(self, mesaj: str, kaynak: Optional[str] = None):
        super().__init__(mesaj, "ES_ZAMANLI_ERISIM_ERROR")
        self.kaynak = kaynak


class StokValidationError(StokHatasiBase):
    """Stok validasyon hatası"""
    
    def __init__(self, mesaj: str, dogrulama_hatalari: Optional[List[str]] = None):
        super().__init__(mesaj, "STOK_VALIDATION_ERROR")
        self.dogrulama_hatalari = dogrulama_hatalari or []


class StokSayimError(StokHatasiBase):
    """Stok sayım hatası"""
    
    def __init__(self, mesaj: str, sayim_id: Optional[str] = None):
        super().__init__(mesaj, "STOK_SAYIM_ERROR")
        self.sayim_id = sayim_id


class StokKilitError(StokHatasiBase):
    """Stok kilitleme hatası"""
    
    def __init__(self, mesaj: str, kaynak: Optional[str] = None):
        super().__init__(mesaj, "STOK_KILIT_ERROR")
        self.kaynak = kaynak