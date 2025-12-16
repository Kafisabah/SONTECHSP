# Version: 0.1.0
# Last Update: 2024-12-16
# Module: stok.hatalar
# Description: Stok modülü hata sınıfları
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Stok Hata Sınıfları

Bu modül stok modülünün hata yönetimi sınıflarını içerir:
- UrunValidationError: Ürün doğrulama hataları
- BarkodValidationError: Barkod doğrulama hataları
- NegatifStokError: Negatif stok hataları
- StokYetersizError: Yetersiz stok hataları
"""

from .stok_hatalari import (
    StokHatasiBase,
    UrunValidationError,
    BarkodValidationError,
    NegatifStokError,
    StokYetersizError,
    EsZamanliErisimError
)

__all__ = [
    'StokHatasiBase',
    'UrunValidationError',
    'BarkodValidationError',
    'NegatifStokError',
    'StokYetersizError',
    'EsZamanliErisimError'
]

__version__ = "0.1.0"