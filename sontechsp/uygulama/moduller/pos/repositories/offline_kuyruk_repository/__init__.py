# Version: 0.1.0
# Last Update: 2025-12-18
# Module: pos.repositories.offline_kuyruk_repository
# Description: Offline kuyruk repository modül paketi
# Changelog:
# - Refactoring: Büyük dosya modüllere bölündü

"""
Offline Kuyruk Repository Modül Paketi

Bu paket offline kuyruk repository işlemlerini mantıklı modüllere böler:
- kuyruk_islemleri: Temel kuyruk CRUD işlemleri
- senkronizasyon: Senkronizasyon ve durum yönetimi
- monitoring: İstatistikler ve izleme
"""

from .kuyruk_islemleri import KuyrukIslemleri
from .senkronizasyon import Senkronizasyon
from .monitoring import Monitoring

class OfflineKuyrukRepository(KuyrukIslemleri, Senkronizasyon, Monitoring):
    """
    Offline kuyruk repository ana sınıfı
    
    Tüm offline kuyruk repository işlemlerini birleştirir.
    Mixin pattern ile modüler yapı sağlar.
    """
    
    def __init__(self):
        """Repository'yi başlatır"""
        super().__init__()

# Geriye uyumluluk için
__all__ = ['OfflineKuyrukRepository']