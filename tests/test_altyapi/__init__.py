# Version: 0.1.0
# Last Update: 2025-12-18
# Module: tests.test_altyapi
# Description: Test altyapısı modülü - Ortak test araçları ve yardımcılar
# Changelog:
# - İlk oluşturma

"""
Test Altyapısı Modülü

Bu modül test altyapısı için gerekli ortak araçları sağlar:
- Test konfigürasyonu
- Mock servisler
- Test veri üreticileri
- Test sonuç raporlama

Görev 8: Test altyapısı ve mock servisleri oluştur
"""

from tests.test_altyapi.konfigurasyon import TestConfig, TestResult
from tests.test_altyapi.mock_servisler import DummySaglayici, MockNetworkService
from tests.test_altyapi.veri_uretici import TestVeriUretici

__all__ = [
    "TestConfig",
    "TestResult",
    "DummySaglayici",
    "MockNetworkService",
    "TestVeriUretici",
]
