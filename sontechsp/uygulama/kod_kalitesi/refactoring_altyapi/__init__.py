# Version: 0.1.0
# Last Update: 2025-12-18
# Module: kod_kalitesi.refactoring_altyapi
# Description: Refactoring altyapısı modülleri
# Changelog:
# - İlk versiyon: Refactoring altyapısı modülleri export edildi

"""
Refactoring Altyapısı

Kod kalitesi refactoring işlemleri için gerekli altyapı bileşenleri:
- YedekYoneticisi: Güvenli yedekleme ve geri alma
- TestKorumaSistemi: Test bütünlüğü koruma
- ImportGuncellemeSistemi: Import yapısı yönetimi
"""

from .yedek_yoneticisi import (
    YedekYoneticisi,
    YedekTuru,
    YedekDurumu,
    YedekBilgisi,
    GeriAlmaBilgisi
)

from .test_koruma_sistemi import (
    TestKorumaSistemi,
    TestTuru,
    TestDurumu,
    TestBilgisi,
    TestCoverageRaporu,
    TestGuncellemePlani
)

from .import_guncelleme_sistemi import (
    ImportGuncellemeSistemi,
    ImportTuru,
    BagimlilikTuru,
    ImportBilgisi,
    BagimlilikGrafi,
    ImportGuncellemePlani
)

__all__ = [
    # Yedek Yöneticisi
    'YedekYoneticisi',
    'YedekTuru',
    'YedekDurumu', 
    'YedekBilgisi',
    'GeriAlmaBilgisi',
    
    # Test Koruma Sistemi
    'TestKorumaSistemi',
    'TestTuru',
    'TestDurumu',
    'TestBilgisi',
    'TestCoverageRaporu',
    'TestGuncellemePlani',
    
    # Import Güncelleme Sistemi
    'ImportGuncellemeSistemi',
    'ImportTuru',
    'BagimlilikTuru',
    'ImportBilgisi',
    'BagimlilikGrafi',
    'ImportGuncellemePlani'
]