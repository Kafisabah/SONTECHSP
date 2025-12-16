# Version: 0.1.0
# Last Update: 2025-12-16
# Module: pos.hatalar
# Description: POS modülü özel hata sınıfları
# Changelog:
# - İlk oluşturma

"""
POS Modülü Özel Hata Sınıfları

Bu modül POS sisemlerinin özel hata sınıflarını tanımlar.
Barkod, stok, ödeme, iade ve yazdırma hatalarını kapsar.
"""

from sontechsp.uygulama.cekirdek.hatalar import SontechHatasi


class BarkodHatasi(SontechHatasi):
    """Barkod işlemleri ile ilgili hatalar"""
    
    def __init__(self, mesaj: str, barkod: str = None):
        super().__init__(mesaj)
        self.barkod = barkod


class StokHatasi(SontechHatasi):
    """Stok işlemleri ile ilgili hatalar"""
    
    def __init__(self, mesaj: str, urun_id: int = None, mevcut_stok: int = None):
        super().__init__(mesaj)
        self.urun_id = urun_id
        self.mevcut_stok = mevcut_stok


class OdemeHatasi(SontechHatasi):
    """Ödeme işlemleri ile ilgili hatalar"""
    
    def __init__(self, mesaj: str, sepet_id: int = None, tutar: float = None):
        super().__init__(mesaj)
        self.sepet_id = sepet_id
        self.tutar = tutar


class IadeHatasi(SontechHatasi):
    """İade işlemleri ile ilgili hatalar"""
    
    def __init__(self, mesaj: str, satis_id: int = None, iade_id: int = None):
        super().__init__(mesaj)
        self.satis_id = satis_id
        self.iade_id = iade_id


class NetworkHatasi(SontechHatasi):
    """Network bağlantısı ile ilgili hatalar"""
    
    def __init__(self, mesaj: str, endpoint: str = None):
        super().__init__(mesaj)
        self.endpoint = endpoint


class YazdirmaHatasi(SontechHatasi):
    """Fiş yazdırma ile ilgili hatalar"""
    
    def __init__(self, mesaj: str, yazici_adi: str = None):
        super().__init__(mesaj)
        self.yazici_adi = yazici_adi