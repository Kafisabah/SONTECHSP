# Version: 0.1.0
# Last Update: 2024-12-15
# Module: stok
# Description: Stok yönetimi modülü (stok_ajani sorumluluğu)
# Changelog:
# - İlk oluşturma
# - Alt modül yapısı eklendi

"""
SONTECHSP Stok Modülü

Bu modül stok yönetimi işlemlerini içerir:
- Ürün yönetimi
- Barkod sistemi
- Stok hareketleri
- Stok sayımı
- Transfer işlemleri
- Negatif stok eşiği kontrolü

Katmanlı yapı:
- servisler/: İş mantığı katmanı
- depolar/: Repository katmanı
- modeller/: Veri modelleri katmanı
"""

# Ana servis sınıfları
from .servisler import StokYonetimService, UrunService, BarkodService, NegatifStokKontrol

# DTO sınıfları
from .dto import UrunDTO, BarkodDTO, StokHareketDTO, StokDurumRaporDTO

# Hata sınıfları
from .hatalar import (
    StokHatasiBase,
    UrunValidationError,
    BarkodValidationError,
    NegatifStokError,
    StokYetersizError
)

# Alt modülleri import et
from . import servisler
from . import depolar
from . import modeller

__version__ = "0.1.0"
__all__ = [
    # Servisler
    "StokYonetimService",
    "UrunService",
    "BarkodService",
    "NegatifStokKontrol",
    
    # DTO'lar
    "UrunDTO",
    "BarkodDTO",
    "StokHareketDTO", 
    "StokDurumRaporDTO",
    
    # Hatalar
    "StokHatasiBase",
    "UrunValidationError",
    "BarkodValidationError",
    "NegatifStokError",
    "StokYetersizError",
    
    # Alt modüller
    "servisler", 
    "depolar", 
    "modeller"
]