# Version: 0.1.0
# Last Update: 2025-12-18
# Module: tests.test_altyapi.pytest_markers
# Description: Pytest marker sistemi ve test kategorileri
# Changelog:
# - İlk oluşturma

"""
Pytest Marker Sistemi

Bu modül test kategorileri için pytest marker sistemini sağlar:
- Test kategorileri (smoke, fast, slow, critical)
- Marker dekoratörleri
- Test filtreleme yardımcıları

Görev 8: Test altyapısı ve mock servisleri oluştur
Requirements: Test kategorileri marker sistemi
"""

import pytest
from typing import Callable, Any
from functools import wraps


# Test kategorileri için marker dekoratörleri
def smoke_test(func: Callable) -> Callable:
    """
    Smoke test marker

    Temel sistem fonksiyonlarının çalışırlığını kontrol eden hızlı testler.
    Süre: < 30 saniye
    """
    return pytest.mark.smoke(func)


def fast_test(func: Callable) -> Callable:
    """
    Fast test marker

    Hızlı unit testler ve basit entegrasyon testleri.
    Süre: < 2 dakika
    """
    return pytest.mark.fast(func)


def slow_test(func: Callable) -> Callable:
    """
    Slow test marker

    Kapsamlı entegrasyon testleri ve uzun süren işlemler.
    Süre: < 10 dakika
    """
    return pytest.mark.slow(func)


def critical_test(func: Callable) -> Callable:
    """
    Critical test marker

    Kritik iş kuralları ve güvenlik testleri.
    Süre: < 5 dakika
    """
    return pytest.mark.critical(func)


def unit_test(func: Callable) -> Callable:
    """
    Unit test marker

    İzole birim testler.
    """
    return pytest.mark.unit(func)


def integration_test(func: Callable) -> Callable:
    """
    Integration test marker

    Modüller arası entegrasyon testleri.
    """
    return pytest.mark.integration(func)


def property_test(func: Callable) -> Callable:
    """
    Property-based test marker

    Hypothesis ile property-based testler.
    """
    return pytest.mark.property(func)


# Kombinasyon dekoratörleri
def smoke_unit_test(func: Callable) -> Callable:
    """Smoke + Unit test kombinasyonu"""
    return smoke_test(unit_test(func))


def fast_unit_test(func: Callable) -> Callable:
    """Fast + Unit test kombinasyonu"""
    return fast_test(unit_test(func))


def critical_integration_test(func: Callable) -> Callable:
    """Critical + Integration test kombinasyonu"""
    return critical_test(integration_test(func))


def slow_property_test(func: Callable) -> Callable:
    """Slow + Property test kombinasyonu"""
    return slow_test(property_test(func))


# Test kategorisi kontrol yardımcıları
class TestKategoriKontrol:
    """Test kategorisi kontrol sınıfı"""

    @staticmethod
    def is_smoke_test(test_item) -> bool:
        """Test smoke kategorisinde mi?"""
        return test_item.get_closest_marker("smoke") is not None

    @staticmethod
    def is_fast_test(test_item) -> bool:
        """Test fast kategorisinde mi?"""
        return test_item.get_closest_marker("fast") is not None

    @staticmethod
    def is_slow_test(test_item) -> bool:
        """Test slow kategorisinde mi?"""
        return test_item.get_closest_marker("slow") is not None

    @staticmethod
    def is_critical_test(test_item) -> bool:
        """Test critical kategorisinde mi?"""
        return test_item.get_closest_marker("critical") is not None

    @staticmethod
    def is_property_test(test_item) -> bool:
        """Test property-based mi?"""
        return test_item.get_closest_marker("property") is not None

    @staticmethod
    def get_test_categories(test_item) -> list:
        """Test kategorilerini listele"""
        categories = []

        if TestKategoriKontrol.is_smoke_test(test_item):
            categories.append("smoke")
        if TestKategoriKontrol.is_fast_test(test_item):
            categories.append("fast")
        if TestKategoriKontrol.is_slow_test(test_item):
            categories.append("slow")
        if TestKategoriKontrol.is_critical_test(test_item):
            categories.append("critical")
        if TestKategoriKontrol.is_property_test(test_item):
            categories.append("property")

        return categories


# Pytest hook'ları
def pytest_configure(config):
    """Pytest konfigürasyonu - marker'ları kaydet"""
    config.addinivalue_line("markers", "smoke: Temel sistem fonksiyon testleri (< 30s)")
    config.addinivalue_line("markers", "fast: Hızlı unit testler (< 2min)")
    config.addinivalue_line("markers", "slow: Kapsamlı entegrasyon testleri (< 10min)")
    config.addinivalue_line("markers", "critical: Kritik iş kuralı testleri (< 5min)")
    config.addinivalue_line("markers", "unit: İzole birim testler")
    config.addinivalue_line("markers", "integration: Modül entegrasyon testleri")
    config.addinivalue_line("markers", "property: Property-based testler")


def pytest_collection_modifyitems(config, items):
    """Test koleksiyonu modifikasyonu - otomatik marker ekleme"""
    for item in items:
        # Dosya adına göre otomatik marker ekleme
        if "smoke" in item.nodeid:
            item.add_marker(pytest.mark.smoke)
        elif "property" in item.nodeid:
            item.add_marker(pytest.mark.property)
        elif "integration" in item.nodeid or "entegrasyon" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "unit" in item.nodeid or "birim" in item.nodeid:
            item.add_marker(pytest.mark.unit)

        # Varsayılan olarak fast marker ekle (eğer başka marker yoksa)
        markers = [marker.name for marker in item.iter_markers()]
        if not any(cat in markers for cat in ["smoke", "fast", "slow", "critical"]):
            item.add_marker(pytest.mark.fast)


# Test filtreleme yardımcıları
class TestFiltreleme:
    """Test filtreleme yardımcı sınıfı"""

    @staticmethod
    def sadece_smoke_testler():
        """Sadece smoke testleri çalıştır"""
        return "-m smoke"

    @staticmethod
    def sadece_fast_testler():
        """Sadece fast testleri çalıştır"""
        return "-m fast"

    @staticmethod
    def sadece_critical_testler():
        """Sadece critical testleri çalıştır"""
        return "-m critical"

    @staticmethod
    def slow_testler_haric():
        """Slow testler hariç tümü"""
        return "-m 'not slow'"

    @staticmethod
    def sadece_property_testler():
        """Sadece property-based testler"""
        return "-m property"

    @staticmethod
    def hizli_testler():
        """Hızlı testler (smoke + fast)"""
        return "-m 'smoke or fast'"

    @staticmethod
    def yavas_testler():
        """Yavaş testler (slow + critical)"""
        return "-m 'slow or critical'"


# Test süre kontrolü dekoratörü
def max_execution_time(seconds: int):
    """
    Test maksimum çalışma süresi kontrolü

    Args:
        seconds: Maksimum süre (saniye)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time

            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                if execution_time > seconds:
                    pytest.fail(f"Test {seconds} saniyeden uzun sürdü: {execution_time:.2f}s")

                return result
            except Exception as e:
                execution_time = time.time() - start_time
                print(f"Test {execution_time:.2f} saniye sonra hata verdi: {e}")
                raise

        return wrapper

    return decorator


# Örnek kullanım dekoratörleri
def smoke_max_30s(func: Callable) -> Callable:
    """Smoke test - maksimum 30 saniye"""
    return smoke_test(max_execution_time(30)(func))


def fast_max_120s(func: Callable) -> Callable:
    """Fast test - maksimum 120 saniye"""
    return fast_test(max_execution_time(120)(func))


def critical_max_300s(func: Callable) -> Callable:
    """Critical test - maksimum 300 saniye"""
    return critical_test(max_execution_time(300)(func))


# Test raporu için marker bilgileri
def get_marker_info() -> dict:
    """Marker bilgilerini döndür"""
    return {
        "smoke": {
            "description": "Temel sistem fonksiyon testleri",
            "max_duration": "30 saniye",
            "purpose": "Hızlı sistem sağlık kontrolü",
        },
        "fast": {
            "description": "Hızlı unit testler",
            "max_duration": "2 dakika",
            "purpose": "Geliştirme sırasında hızlı feedback",
        },
        "slow": {
            "description": "Kapsamlı entegrasyon testleri",
            "max_duration": "10 dakika",
            "purpose": "Detaylı sistem doğrulama",
        },
        "critical": {
            "description": "Kritik iş kuralı testleri",
            "max_duration": "5 dakika",
            "purpose": "Üretim öncesi zorunlu kontroller",
        },
        "property": {
            "description": "Property-based testler",
            "max_duration": "Değişken",
            "purpose": "Kapsamlı edge case keşfi",
        },
    }
