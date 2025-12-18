# Version: 0.1.0
# Last Update: 2025-12-18
# Module: pos.repositories.satis_repository
# Description: Satış repository modül paketi
# Changelog:
# - Refactoring: Büyük dosya modüllere bölündü

"""
Satış Repository Modül Paketi

Bu paket satış repository işlemlerini mantıklı modüllere böler:
- crud: Temel CRUD işlemleri
- sorgular: Karmaşık sorgular ve listeler  
- raporlar: Özet ve rapor işlemleri
"""

from .satis_crud import SatisCrud
from .satis_raporlar import SatisRaporlar
from .satis_sorgular import SatisSorgular


class SatisRepository(SatisCrud, SatisSorgular, SatisRaporlar):
    """
    Satış repository ana sınıfı
    
    Tüm satış repository işlemlerini birleştirir.
    Mixin pattern ile modüler yapı sağlar.
    """
    
    def __init__(self):
        """Repository'yi başlatır"""
        super().__init__()


# Public API
__all__ = ['SatisRepository']