# Version: 0.1.0
# Last Update: 2024-12-15
# Module: test_veritabani_gereksinimleri
# Description: SONTECHSP veritabanı gereksinim belirtimi property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Veritabanı Gereksinim Belirtimi Property Testleri

Bu dosya PostgreSQL ve SQLite veritabanı gereksinimlerinin
doğru şekilde belirtildiğini property-based testing ile kontrol eder.

Veritabanı gereksinimleri:
- PostgreSQL: Ana veritabanı (çoklu PC eş zamanlı erişim)
- SQLite: POS offline cache
- psycopg2: PostgreSQL driver
- SQLAlchemy: ORM (her iki veritabanı için)
"""

import os
import pytest
import toml
from hypothesis import given, strategies as st
from pathlib import Path


class TestVeritabaniGereksinimleri:
    """SONTECHSP veritabanı gereksinim belirtimi testleri"""
    
    def test_veritabani_gereksinim_belirtimi(self):
        """
        **Feature: sontechsp-proje-iskeleti, Property 6: Veritabanı gereksinim belirtimi**
        
        Herhangi bir proje yapılandırmasında, PostgreSQL ve SQLite veritabanı gereksinimleri 
        belirtilmeli ve Windows üzerinde yüklenebilir olmalıdır
        **Doğrular: Gereksinim 2.3, 2.4**
        """
        # pyproject.toml dosyasını oku
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            config = toml.load(f)
        
        # Ana bağımlılıkları kontrol et
        dependencies = config.get("project", {}).get("dependencies", [])
        dependencies_str = " ".join(dependencies).lower()
        
        # PostgreSQL gereksinimleri
        assert "psycopg2" in dependencies_str, "PostgreSQL driver (psycopg2-binary) eksik"
        assert "sqlalchemy" in dependencies_str, "SQLAlchemy ORM eksik"
        
        # SQLite desteği (SQLAlchemy ile birlikte gelir, ayrı paket gerekmez)
        # Ancak PyInstaller hidden-imports'ta belirtilmeli
        pyinstaller_config = config.get("tool", {}).get("pyinstaller", {})
        hidden_imports = pyinstaller_config.get("hidden-imports", [])
        hidden_imports_str = " ".join(hidden_imports).lower()
        
        assert "postgresql" in hidden_imports_str, "PostgreSQL dialect hidden-import eksik"
        assert "sqlite" in hidden_imports_str, "SQLite dialect hidden-import eksik"
    
    def test_postgresql_driver_gereksinimleri(self):
        """
        PostgreSQL driver gereksinimlerinin Windows uyumlu olduğunu kontrol eder
        """
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            config = toml.load(f)
        
        dependencies = config.get("project", {}).get("dependencies", [])
        
        # psycopg2-binary kontrolü (Windows için önerilen)
        psycopg2_found = False
        for dep in dependencies:
            if "psycopg2" in dep.lower():
                psycopg2_found = True
                # Windows için psycopg2-binary önerilir
                assert "binary" in dep.lower(), "Windows için psycopg2-binary kullanılmalı"
                break
        
        assert psycopg2_found, "PostgreSQL driver (psycopg2) bulunamadı"
    
    def test_sqlalchemy_orm_gereksinimleri(self):
        """
        SQLAlchemy ORM gereksinimlerinin doğru sürümde olduğunu kontrol eder
        """
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            config = toml.load(f)
        
        dependencies = config.get("project", {}).get("dependencies", [])
        
        # SQLAlchemy kontrolü
        sqlalchemy_found = False
        for dep in dependencies:
            if "sqlalchemy" in dep.lower():
                sqlalchemy_found = True
                # SQLAlchemy 2.0+ gerekli (modern async desteği için)
                if ">=" in dep:
                    version_part = dep.split(">=")[1].strip().replace('"', '').replace("'", "")
                    major_version = int(version_part.split(".")[0])
                    assert major_version >= 2, "SQLAlchemy 2.0+ gerekli"
                break
        
        assert sqlalchemy_found, "SQLAlchemy ORM bulunamadı"
    
    def test_alembic_migration_gereksinimleri(self):
        """
        Alembic migration gereksinimlerinin mevcut olduğunu kontrol eder
        """
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            config = toml.load(f)
        
        dependencies = config.get("project", {}).get("dependencies", [])
        dependencies_str = " ".join(dependencies).lower()
        
        assert "alembic" in dependencies_str, "Alembic migration aracı eksik"
    
    def test_pyinstaller_veritabani_yapilandirmasi(self):
        """
        PyInstaller'da veritabanı ile ilgili yapılandırmaların doğru olduğunu kontrol eder
        """
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            config = toml.load(f)
        
        pyinstaller_config = config.get("tool", {}).get("pyinstaller", {})
        assert pyinstaller_config, "PyInstaller yapılandırması bulunamadı"
        
        # Hidden imports kontrolü
        hidden_imports = pyinstaller_config.get("hidden-imports", [])
        hidden_imports_str = " ".join(hidden_imports).lower()
        
        # Veritabanı dialect'ları
        assert "sqlalchemy.dialects.postgresql" in hidden_imports_str, "PostgreSQL dialect eksik"
        assert "sqlalchemy.dialects.sqlite" in hidden_imports_str, "SQLite dialect eksik"
        
        # PostgreSQL driver
        assert "psycopg2" in hidden_imports_str, "psycopg2 hidden-import eksik"
        
        # Alembic runtime
        assert "alembic.runtime.migration" in hidden_imports_str, "Alembic runtime eksik"
    
    def test_windows_uyumlulugu(self):
        """
        Veritabanı bağımlılıklarının Windows üzerinde yüklenebilir olduğunu kontrol eder
        """
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            config = toml.load(f)
        
        # Proje metadata'sında Windows desteği belirtilmeli
        classifiers = config.get("project", {}).get("classifiers", [])
        classifiers_str = " ".join(classifiers).lower()
        
        assert "windows" in classifiers_str, "Windows desteği classifier'da belirtilmemiş"
        
        # psycopg2-binary Windows için gerekli
        dependencies = config.get("project", {}).get("dependencies", [])
        dependencies_str = " ".join(dependencies).lower()
        assert "psycopg2-binary" in dependencies_str, "Windows için psycopg2-binary gerekli"
    
    @given(st.sampled_from([
        "psycopg2", "sqlalchemy", "alembic"
    ]))
    def test_veritabani_bagimlilik_property(self, bagimlilik_adi):
        """
        Property test: Herhangi bir veritabanı bağımlılığı için varlık kontrolü
        """
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            config = toml.load(f)
        
        dependencies = config.get("project", {}).get("dependencies", [])
        dependencies_str = " ".join(dependencies).lower()
        
        assert bagimlilik_adi in dependencies_str, f"Veritabanı bağımlılığı eksik: {bagimlilik_adi}"
    
    @given(st.sampled_from([
        "sqlalchemy.dialects.postgresql",
        "sqlalchemy.dialects.sqlite", 
        "psycopg2",
        "alembic.runtime.migration"
    ]))
    def test_pyinstaller_hidden_imports_property(self, hidden_import):
        """
        Property test: Herhangi bir veritabanı hidden-import için varlık kontrolü
        """
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            config = toml.load(f)
        
        pyinstaller_config = config.get("tool", {}).get("pyinstaller", {})
        hidden_imports = pyinstaller_config.get("hidden-imports", [])
        hidden_imports_str = " ".join(hidden_imports).lower()
        
        assert hidden_import.lower() in hidden_imports_str, f"Hidden-import eksik: {hidden_import}"
    
    def test_coklu_veritabani_desteği(self):
        """
        Hem PostgreSQL hem SQLite desteğinin aynı anda mevcut olduğunu kontrol eder
        """
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            config = toml.load(f)
        
        # PyInstaller hidden-imports'ta her iki dialect de olmalı
        pyinstaller_config = config.get("tool", {}).get("pyinstaller", {})
        hidden_imports = pyinstaller_config.get("hidden-imports", [])
        hidden_imports_str = " ".join(hidden_imports).lower()
        
        # Her iki veritabanı dialect'ı da mevcut olmalı
        postgresql_support = "postgresql" in hidden_imports_str
        sqlite_support = "sqlite" in hidden_imports_str
        
        assert postgresql_support, "PostgreSQL desteği eksik"
        assert sqlite_support, "SQLite desteği eksik"
        assert postgresql_support and sqlite_support, "Çoklu veritabanı desteği eksik"
    
    def test_offline_pos_sqlite_gereksinimleri(self):
        """
        Offline POS için SQLite gereksinimlerinin karşılandığını kontrol eder
        """
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            config = toml.load(f)
        
        # SQLite Python'da built-in, ek paket gerekmez
        # Ancak SQLAlchemy dialect'ı PyInstaller'da olmalı
        pyinstaller_config = config.get("tool", {}).get("pyinstaller", {})
        hidden_imports = pyinstaller_config.get("hidden-imports", [])
        hidden_imports_str = " ".join(hidden_imports).lower()
        
        assert "sqlite" in hidden_imports_str, "SQLite dialect PyInstaller'da eksik"
        
        # SQLAlchemy ORM mevcut olmalı (SQLite için de gerekli)
        dependencies = config.get("project", {}).get("dependencies", [])
        dependencies_str = " ".join(dependencies).lower()
        assert "sqlalchemy" in dependencies_str, "SQLite için SQLAlchemy ORM eksik"
    
    @given(st.sampled_from([
        ("PostgreSQL", "psycopg2"),
        ("SQLite", "sqlalchemy"),
        ("Migration", "alembic")
    ]))
    def test_veritabani_teknoloji_eslestirmesi_property(self, teknoloji_bagimlilik):
        """
        Property test: Herhangi bir veritabanı teknolojisi için bağımlılık eşleştirmesi
        """
        teknoloji, bagimlilik = teknoloji_bagimlilik
        
        with open("pyproject.toml", "r", encoding="utf-8") as f:
            config = toml.load(f)
        
        dependencies = config.get("project", {}).get("dependencies", [])
        dependencies_str = " ".join(dependencies).lower()
        
        assert bagimlilik in dependencies_str, f"{teknoloji} için {bagimlilik} bağımlılığı eksik"