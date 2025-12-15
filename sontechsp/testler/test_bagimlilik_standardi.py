# Version: 0.1.0
# Last Update: 2024-12-15
# Module: test_bagimlilik_standardi
# Description: SONTECHSP bağımlılık standardı property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Bağımlılık Standardı Property Testleri

Bu dosya pyproject.toml dosyasındaki bağımlılıkların
SONTECHSP standartlarına uygunluğunu property-based testing ile kontrol eder.

Gerekli bağımlılıklar:
- PyQt6: GUI framework
- SQLAlchemy: ORM
- Alembic: Database migration
- FastAPI: Web framework
- pytest: Test framework
- hypothesis: Property-based testing
"""

import os
import pytest
import toml
from hypothesis import given, strategies as st
from pathlib import Path


class TestBagimlilikStandardi:
    """SONTECHSP bağımlılık standardı testleri"""
    
    @pytest.mark.critical
    @pytest.mark.unit
    def test_pyproject_toml_mevcut(self):
        """
        pyproject.toml dosyasının mevcut olduğunu kontrol eder
        """
        assert os.path.exists("pyproject.toml"), "pyproject.toml dosyası mevcut değil"
        assert os.path.isfile("pyproject.toml"), "pyproject.toml yolu bir dosya değil"
    
    @pytest.mark.critical
    @pytest.mark.integration
    def test_sontechsp_bagimlilik_standardi(self):
        """
        **Feature: sontechsp-proje-iskeleti, Property 4: SONTECHSP bağımlılık standardı**
        
        Herhangi bir pyproject.toml dosyası, PyQt6, SQLAlchemy, Alembic, FastAPI, 
        pytest, hypothesis bağımlılıklarını tanımlamalıdır
        **Doğrular: Gereksinim 2.1**
        """
        # pyproject.toml dosyasını oku
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            config = toml.load(f)
        
        # Temel bağımlılıkları kontrol et
        dependencies = config.get("project", {}).get("dependencies", [])
        dependencies_str = " ".join(dependencies).lower()
        
        # Zorunlu bağımlılıklar
        zorunlu_bagimliliklar = [
            "pyqt6",        # GUI Framework
            "sqlalchemy",   # ORM
            "alembic",      # Database Migration
            "fastapi",      # Web Framework
            "psycopg2",     # PostgreSQL driver
        ]
        
        for bagimlilik in zorunlu_bagimliliklar:
            assert bagimlilik in dependencies_str, f"Zorunlu bağımlılık eksik: {bagimlilik}"
        
        # Development bağımlılıklarını kontrol et
        dev_dependencies = config.get("project", {}).get("optional-dependencies", {}).get("dev", [])
        dev_dependencies_str = " ".join(dev_dependencies).lower()
        
        # Test bağımlılıkları
        test_bagimliliklar = [
            "pytest",      # Test Framework
            "hypothesis",  # Property-Based Testing
        ]
        
        for bagimlilik in test_bagimliliklar:
            assert bagimlilik in dev_dependencies_str, f"Test bağımlılığı eksik: {bagimlilik}"
        
        # Build bağımlılıklarını kontrol et
        build_dependencies = config.get("project", {}).get("optional-dependencies", {}).get("build", [])
        build_dependencies_str = " ".join(build_dependencies).lower()
        
        assert "pyinstaller" in build_dependencies_str, "PyInstaller bağımlılığı eksik"
    
    def test_python_surum_gereksinimleri(self):
        """
        Python sürüm gereksinimlerinin doğru tanımlandığını kontrol eder
        """
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            config = toml.load(f)
        
        requires_python = config.get("project", {}).get("requires-python", "")
        assert requires_python, "Python sürüm gereksinimi tanımlanmamış"
        assert "3.9" in requires_python, "Python 3.9+ gereksinimi belirtilmemiş"
    
    def test_proje_metadata(self):
        """
        Proje metadata bilgilerinin doğru tanımlandığını kontrol eder
        """
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            config = toml.load(f)
        
        project = config.get("project", {})
        
        # Temel metadata alanları
        assert project.get("name") == "sontechsp", "Proje adı yanlış"
        assert project.get("version"), "Proje sürümü tanımlanmamış"
        assert project.get("description"), "Proje açıklaması tanımlanmamış"
        assert project.get("requires-python"), "Python sürüm gereksinimi tanımlanmamış"
    
    def test_pyinstaller_yapilandirmasi(self):
        """
        PyInstaller yapılandırmasının mevcut olduğunu kontrol eder
        """
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            config = toml.load(f)
        
        pyinstaller_config = config.get("tool", {}).get("pyinstaller", {})
        assert pyinstaller_config, "PyInstaller yapılandırması tanımlanmamış"
        
        # PyInstaller temel ayarları
        assert pyinstaller_config.get("name"), "PyInstaller uygulama adı tanımlanmamış"
        assert "hidden-imports" in pyinstaller_config, "PyInstaller hidden-imports tanımlanmamış"
        
        # PyQt6 hidden imports kontrolü
        hidden_imports = pyinstaller_config.get("hidden-imports", [])
        hidden_imports_str = " ".join(hidden_imports).lower()
        assert "pyqt6" in hidden_imports_str, "PyQt6 hidden-imports eksik"
    
    def test_test_yapilandirmasi(self):
        """
        Test yapılandırmasının doğru tanımlandığını kontrol eder
        """
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            config = toml.load(f)
        
        # pytest yapılandırması
        pytest_config = config.get("tool", {}).get("pytest", {}).get("ini_options", {})
        assert pytest_config, "pytest yapılandırması tanımlanmamış"
        
        testpaths = pytest_config.get("testpaths", [])
        assert "sontechsp/testler" in testpaths, "Test klasörü yolu yanlış"
        
        # hypothesis yapılandırması
        hypothesis_config = config.get("tool", {}).get("hypothesis", {})
        assert hypothesis_config, "hypothesis yapılandırması tanımlanmamış"
        
        max_examples = hypothesis_config.get("max_examples", 0)
        assert max_examples >= 100, "hypothesis max_examples 100'den az"
    
    @given(st.sampled_from([
        "pyqt6", "sqlalchemy", "alembic", "fastapi", "psycopg2"
    ]))
    def test_zorunlu_bagimlilik_property(self, bagimlilik_adi):
        """
        Property test: Herhangi bir zorunlu bağımlılık için varlık kontrolü
        """
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            config = toml.load(f)
        
        dependencies = config.get("project", {}).get("dependencies", [])
        dependencies_str = " ".join(dependencies).lower()
        
        assert bagimlilik_adi in dependencies_str, f"Zorunlu bağımlılık eksik: {bagimlilik_adi}"
    
    @given(st.sampled_from([
        "pytest", "hypothesis"
    ]))
    def test_test_bagimlilik_property(self, test_bagimlilik):
        """
        Property test: Herhangi bir test bağımlılığı için varlık kontrolü
        """
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            config = toml.load(f)
        
        dev_dependencies = config.get("project", {}).get("optional-dependencies", {}).get("dev", [])
        dev_dependencies_str = " ".join(dev_dependencies).lower()
        
        assert test_bagimlilik in dev_dependencies_str, f"Test bağımlılığı eksik: {test_bagimlilik}"
    
    @given(st.sampled_from([
        ("project", "name"),
        ("project", "version"), 
        ("project", "description"),
        ("project", "requires-python")
    ]))
    def test_metadata_alanlari_property(self, alan_bilgisi):
        """
        Property test: Herhangi bir metadata alanı için varlık kontrolü
        """
        section, field = alan_bilgisi
        
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            config = toml.load(f)
        
        section_data = config.get(section, {})
        assert field in section_data, f"Metadata alanı eksik: {section}.{field}"
        assert section_data[field], f"Metadata alanı boş: {section}.{field}"
    
    def test_veritabani_gereksinimleri(self):
        """
        PostgreSQL ve SQLite veritabanı gereksinimlerinin belirtildiğini kontrol eder
        """
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            config = toml.load(f)
        
        dependencies = config.get("project", {}).get("dependencies", [])
        dependencies_str = " ".join(dependencies).lower()
        
        # PostgreSQL driver kontrolü
        assert "psycopg2" in dependencies_str, "PostgreSQL driver (psycopg2) eksik"
        
        # SQLAlchemy kontrolü (SQLite desteği dahil)
        assert "sqlalchemy" in dependencies_str, "SQLAlchemy (SQLite desteği için) eksik"
        
        # PyInstaller hidden imports'ta veritabanı driver'ları
        pyinstaller_config = config.get("tool", {}).get("pyinstaller", {})
        hidden_imports = pyinstaller_config.get("hidden-imports", [])
        hidden_imports_str = " ".join(hidden_imports).lower()
        
        assert "postgresql" in hidden_imports_str, "PostgreSQL dialect hidden-import eksik"
        assert "sqlite" in hidden_imports_str, "SQLite dialect hidden-import eksik"