# Version: 0.1.0
# Last Update: 2024-12-17
# Module: kargo
# Description: Kargo entegrasyon altyapısı ana modülü
# Changelog:
# - Kargo modülü temel yapısı oluşturuldu
# - DTO, servis ve depo export'ları tanımlandı

"""
Kargo Entegrasyon Altyapısı

Bu modül, taşıyıcı-bağımsız kargo yönetimi için gerekli bileşenleri sağlar.
Etiket oluşturma, takip etme ve durum yönetimi işlemlerini destekler.
"""

from .dto import (
    KargoEtiketOlusturDTO,
    KargoEtiketSonucDTO,
    KargoDurumDTO
)

from .sabitler import (
    KaynakTurleri,
    EtiketDurumlari,
    TakipDurumlari,
    Tasiyicilar
)

from .servisler import KargoServisi
from .depolar import KargoDeposu
from .tasiyici_arayuzu import TasiyiciArayuzu
from .tasiyici_fabrikasi import TasiyiciFabrikasi

__all__ = [
    # DTO'lar
    'KargoEtiketOlusturDTO',
    'KargoEtiketSonucDTO', 
    'KargoDurumDTO',
    
    # Sabitler
    'KaynakTurleri',
    'EtiketDurumlari',
    'TakipDurumlari',
    'Tasiyicilar',
    
    # Servisler
    'KargoServisi',
    'KargoDeposu',
    
    # Taşıyıcı arayüzü
    'TasiyiciArayuzu',
    'TasiyiciFabrikasi'
]