# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.kurulum.conftest
# Description: Kurulum testleri için pytest yapılandırması
# Changelog:
# - Pytest fixtures oluşturuldu

"""
Kurulum testleri için pytest yapılandırması ve fixtures
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def gecici_dizin():
    """Her test için geçici dizin oluştur ve test sonrası temizle"""
    test_dir = Path(tempfile.mkdtemp())
    yield test_dir
    if test_dir.exists():
        shutil.rmtree(test_dir)


@pytest.fixture
def gecici_proje_koku(gecici_dizin):
    """Proje kök dizini simülasyonu için geçici dizin"""
    return gecici_dizin


@pytest.fixture
def mock_veritabani_url():
    """Test için mock veritabanı URL'i"""
    return "postgresql://test:test@localhost:5432/test_db"


@pytest.fixture
def varsayilan_ayarlar():
    """Test için varsayılan ayarlar"""
    return {
        "veritabani_url": "postgresql://test:test@localhost:5432/test_db",
        "ortam": "test",
        "log_seviyesi": "DEBUG"
    }