# Version: 0.1.0
# Last Update: 2025-12-17
# Module: kod_kalitesi.test_entegrasyon
# Description: Test entegrasyonu ve doğrulama sistemleri
# Changelog:
# - İlk versiyon: Test entegrasyon modülü oluşturuldu

"""
Test Entegrasyonu ve Doğrulama

Refactoring işlemleri sırasında testlerin korunması,
güncellenmesi ve doğrulanması için sistemler.
"""

from .test_guncelleyici import (
    TestGuncelleyici,
    DosyaDegisikligi,
    TestGuncellemeBilgisi
)
from .test_dogrulayici import (
    TestDogrulayici,
    TestSonucu,
    CoverageRaporu
)

__all__ = [
    'TestGuncelleyici',
    'DosyaDegisikligi',
    'TestGuncellemeBilgisi',
    'TestDogrulayici',
    'TestSonucu',
    'CoverageRaporu',
]
