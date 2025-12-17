# Version: 0.1.0
# Last Update: 2024-12-17
# Module: kargo.tasiyici_fabrikasi
# Description: Taşıyıcı implementasyonları için fabrika sınıfı
# Changelog:
# - TasiyiciFabrikasi class'ı eklendi
# - MVP aşaması için DummyTasiyici döndürme eklendi
# - Gelecekte gerçek taşıyıcılar için genişletilebilir yapı

"""
Taşıyıcı implementasyonları için fabrika sınıfı.

Bu modül, taşıyıcı koduna göre uygun carrier implementasyonu
döndüren fabrika sınıfını içerir.
"""

from typing import Dict, Type

from .tasiyici_arayuzu import TasiyiciArayuzu
from .dummy_tasiyici import DummyTasiyici
from .sabitler import Tasiyicilar


class TasiyiciFabrikasi:
    """
    Taşıyıcı implementasyonları için fabrika sınıfı.
    
    Taşıyıcı koduna göre uygun carrier implementasyonu döndürür.
    MVP aşamasında tüm taşıyıcılar için DummyTasiyici kullanılır.
    """
    
    # Taşıyıcı kod -> implementasyon mapping'i
    _tasiyici_mapping: Dict[str, Type[TasiyiciArayuzu]] = {
        Tasiyicilar.YURTICI: DummyTasiyici,
        Tasiyicilar.ARAS: DummyTasiyici,
        Tasiyicilar.MNG: DummyTasiyici,
        Tasiyicilar.PTT: DummyTasiyici,
        Tasiyicilar.SURAT: DummyTasiyici,
    }
    
    @classmethod
    def tasiyici_olustur(cls, tasiyici_kodu: str) -> TasiyiciArayuzu:
        """
        Taşıyıcı koduna göre uygun carrier implementasyonu oluşturur.
        
        Args:
            tasiyici_kodu: Taşıyıcı kodu (Tasiyicilar sınıfından)
        
        Returns:
            TasiyiciArayuzu: Taşıyıcı implementasyonu
        
        Raises:
            ValueError: Desteklenmeyen taşıyıcı kodu durumunda
        """
        if not Tasiyicilar.gecerli_mi(tasiyici_kodu):
            raise ValueError(f"Desteklenmeyen taşıyıcı kodu: {tasiyici_kodu}")
        
        tasiyici_class = cls._tasiyici_mapping.get(tasiyici_kodu)
        if not tasiyici_class:
            raise ValueError(f"Taşıyıcı implementasyonu bulunamadı: {tasiyici_kodu}")
        
        return tasiyici_class()
    
    @classmethod
    def desteklenen_tasiyicilar(cls) -> list:
        """
        Desteklenen tüm taşıyıcı kodlarını döndürür.
        
        Returns:
            list: Desteklenen taşıyıcı kodları listesi
        """
        return list(cls._tasiyici_mapping.keys())
    
    @classmethod
    def tasiyici_ekle(cls, tasiyici_kodu: str, 
                      tasiyici_class: Type[TasiyiciArayuzu]) -> None:
        """
        Yeni taşıyıcı implementasyonu ekler.
        
        Gelecekte gerçek taşıyıcı implementasyonları eklemek için kullanılır.
        
        Args:
            tasiyici_kodu: Taşıyıcı kodu
            tasiyici_class: Taşıyıcı implementasyon sınıfı
        
        Raises:
            ValueError: Geçersiz taşıyıcı sınıfı durumunda
        """
        if not issubclass(tasiyici_class, TasiyiciArayuzu):
            raise ValueError(
                f"Taşıyıcı sınıfı TasiyiciArayuzu'nden türetilmelidir: "
                f"{tasiyici_class}"
            )
        
        cls._tasiyici_mapping[tasiyici_kodu] = tasiyici_class