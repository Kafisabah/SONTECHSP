# Version: 0.1.0
# Last Update: 2025-12-18
# Module: pos.repositories.iade_repository
# Description: İade repository modül paketi
# Changelog:
# - Refactoring: Büyük dosya modüllere bölündü

"""
İade Repository Modül Paketi

Bu paket iade repository işlemlerini mantıklı modüllere böler:
- iade_crud: Temel iade CRUD işlemleri
- is_kurallari: İade iş kuralları ve doğrulama
- raporlar: İade raporları ve listeler
"""

from .iade_crud import IadeCrud
from .is_kurallari import IsKurallari
from .raporlar import Raporlar

class IadeRepository(IadeCrud, IsKurallari, Raporlar):
    """
    İade repository ana sınıfı
    
    Tüm iade repository işlemlerini birleştirir.
    Mixin pattern ile modüler yapı sağlar.
    """
    
    def __init__(self):
        """Repository'yi başlatır"""
        super().__init__()

# Geriye uyumluluk için
__all__ = ['IadeRepository']