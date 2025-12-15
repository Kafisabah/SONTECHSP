# Version: 0.1.0
# Last Update: 2024-12-15
# Module: tests.test_migration_unit
# Description: SONTECHSP migration unit testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Migration Unit Testleri

Bu modül Alembic migration işlemleri için unit testleri içerir.
"""

import pytest
import tempfile
import os
import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import StaticPool
from alembic.runtime.migration import MigrationContext
from alembic.operations import Operations


class TestMigrationUpgradeDowngrade:
    """Migration upgrade/downgrade unit testleri"""
    
    @pytest.fixture
    def temp_db_engine(self):
        """Geçici SQLite veritabanı engine'i"""
        # Geçici dosya oluştur
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name
        
        # Engine oluştur
        engine = create_engine(
            f"sqlite:///{db_path}",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )
        
        yield engine
        
        # Temizlik
        engine.dispose()
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def _import_migration_module(self):
        """Migration modülünü import et"""
        # Migration dosyasının yolunu bul
        current_dir = os.path.dirname(__file__)
        migration_path = os.path.join(
            current_dir, '..', 'sontechsp', 'uygulama', 
            'veritabani', 'gocler', 'versions'
        )
        migration_path = os.path.abspath(migration_path)
        
        # Path'e ekle
        if migration_path not in sys.path:
            sys.path.insert(0, migration_path)
        
        # Migration modülünü import et
        try:
            from importlib import import_module
            migration_module = import_module('20241215_1200_001_ilk_migration')
            return migration_module
        except ImportError as e:
            pytest.skip(f"Migration modülü import edilemedi: {e}")
    
    def test_ilk_migration_upgrade(self, temp_db_engine):
        """
        İlk migration upgrade testini yaz
        
        Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5
        """
        migration_module = self._import_migration_module()
        
        # Migration'ı çalıştır
        with temp_db_engine.connect() as connection:
            context = MigrationContext.configure(connection)
            
            # Upgrade fonksiyonunu çalıştır
            with connection.begin():
                # Alembic context'ini ayarla
                context._migration_context = context
                migration_module.upgrade()
        
        # Tabloların oluşturulduğunu kontrol et
        inspector = inspect(temp_db_engine)
        table_names = inspector.get_table_names()
        
        expected_tables = [
            'firmalar', 'magazalar', 'terminaller', 
            'kullanicilar', 'roller', 'yetkiler',
            'kullanici_rolleri', 'rol_yetkileri'
        ]
        
        for table_name in expected_tables:
            assert table_name in table_names, f"Tablo '{table_name}' oluşturulmalı"
    
    def test_kullanicilar_tablosu_yapisi(self, temp_db_engine):
        """
        Kullanıcılar tablosu yapısını test et
        
        Validates: Requirements 2.1
        """
        migration_module = self._import_migration_module()
        
        # Migration'ı çalıştır
        with temp_db_engine.connect() as connection:
            context = MigrationContext.configure(connection)
            
            with connection.begin():
                migration_module.upgrade()
        
        # Kullanıcılar tablosu kolonlarını kontrol et
        inspector = inspect(temp_db_engine)
        columns = inspector.get_columns('kullanicilar')
        column_names = [col['name'] for col in columns]
        
        expected_columns = [
            'id', 'olusturma_tarihi', 'guncelleme_tarihi',
            'kullanici_adi', 'email', 'sifre_hash', 
            'ad', 'soyad', 'telefon', 'aktif',
            'son_giris_tarihi', 'sifre_degisim_tarihi'
        ]
        
        for col_name in expected_columns:
            assert col_name in column_names, f"Kolon '{col_name}' kullanicilar tablosunda olmalı"
    
    def test_roller_tablosu_yapisi(self, temp_db_engine):
        """
        Roller tablosu yapısını test et
        
        Validates: Requirements 2.2
        """
        migration_module = self._import_migration_module()
        
        # Migration'ı çalıştır
        with temp_db_engine.connect() as connection:
            context = MigrationContext.configure(connection)
            
            with connection.begin():
                migration_module.upgrade()
        
        # Roller tablosu kolonlarını kontrol et
        inspector = inspect(temp_db_engine)
        columns = inspector.get_columns('roller')
        column_names = [col['name'] for col in columns]
        
        expected_columns = [
            'id', 'olusturma_tarihi', 'guncelleme_tarihi',
            'rol_adi', 'aciklama', 'aktif', 'sistem_rolu'
        ]
        
        for col_name in expected_columns:
            assert col_name in column_names, f"Kolon '{col_name}' roller tablosunda olmalı"
    
    def test_firmalar_tablosu_yapisi(self, temp_db_engine):
        """
        Firmalar tablosu yapısını test et
        
        Validates: Requirements 2.3
        """
        migration_module = self._import_migration_module()
        
        # Migration'ı çalıştır
        with temp_db_engine.connect() as connection:
            context = MigrationContext.configure(connection)
            
            with connection.begin():
                migration_module.upgrade()
        
        # Firmalar tablosu kolonlarını kontrol et
        inspector = inspect(temp_db_engine)
        columns = inspector.get_columns('firmalar')
        column_names = [col['name'] for col in columns]
        
        expected_columns = [
            'id', 'olusturma_tarihi', 'guncelleme_tarihi',
            'firma_adi', 'ticaret_unvani', 'vergi_dairesi',
            'vergi_no', 'tc_kimlik_no', 'adres', 'telefon',
            'email', 'website', 'aktif'
        ]
        
        for col_name in expected_columns:
            assert col_name in column_names, f"Kolon '{col_name}' firmalar tablosunda olmalı"
    
    def test_magazalar_tablosu_yapisi(self, temp_db_engine):
        """
        Mağazalar tablosu yapısını test et
        
        Validates: Requirements 2.4
        """
        migration_module = self._import_migration_module()
        
        # Migration'ı çalıştır
        with temp_db_engine.connect() as connection:
            context = MigrationContext.configure(connection)
            
            with connection.begin():
                migration_module.upgrade()
        
        # Mağazalar tablosu kolonlarını kontrol et
        inspector = inspect(temp_db_engine)
        columns = inspector.get_columns('magazalar')
        column_names = [col['name'] for col in columns]
        
        expected_columns = [
            'id', 'olusturma_tarihi', 'guncelleme_tarihi',
            'firma_id', 'magaza_adi', 'magaza_kodu',
            'adres', 'sehir', 'ilce', 'posta_kodu',
            'telefon', 'email', 'alan_m2', 'personel_sayisi', 'aktif'
        ]
        
        for col_name in expected_columns:
            assert col_name in column_names, f"Kolon '{col_name}' magazalar tablosunda olmalı"
        
        # Foreign key kontrolü
        foreign_keys = inspector.get_foreign_keys('magazalar')
        fk_columns = []
        for fk in foreign_keys:
            fk_columns.extend(fk['constrained_columns'])
        
        assert 'firma_id' in fk_columns, "firma_id foreign key olmalı"
    
    def test_terminaller_tablosu_yapisi(self, temp_db_engine):
        """
        Terminaller tablosu yapısını test et
        
        Validates: Requirements 2.5
        """
        migration_module = self._import_migration_module()
        
        # Migration'ı çalıştır
        with temp_db_engine.connect() as connection:
            context = MigrationContext.configure(connection)
            
            with connection.begin():
                migration_module.upgrade()
        
        # Terminaller tablosu kolonlarını kontrol et
        inspector = inspect(temp_db_engine)
        columns = inspector.get_columns('terminaller')
        column_names = [col['name'] for col in columns]
        
        expected_columns = [
            'id', 'olusturma_tarihi', 'guncelleme_tarihi',
            'magaza_id', 'terminal_adi', 'terminal_kodu',
            'ip_adresi', 'mac_adresi', 'isletim_sistemi',
            'yazici_modeli', 'barkod_okuyucu', 'aktif', 'online'
        ]
        
        for col_name in expected_columns:
            assert col_name in column_names, f"Kolon '{col_name}' terminaller tablosunda olmalı"
        
        # Foreign key kontrolü
        foreign_keys = inspector.get_foreign_keys('terminaller')
        fk_columns = []
        for fk in foreign_keys:
            fk_columns.extend(fk['constrained_columns'])
        
        assert 'magaza_id' in fk_columns, "magaza_id foreign key olmalı"
    
    def test_migration_downgrade(self, temp_db_engine):
        """
        Migration downgrade testini yaz
        
        Validates: Requirements 5.1, 5.2
        """
        migration_module = self._import_migration_module()
        
        # Önce upgrade yap
        with temp_db_engine.connect() as connection:
            context = MigrationContext.configure(connection)
            
            with connection.begin():
                migration_module.upgrade()
        
        # Tabloların oluşturulduğunu kontrol et
        inspector = inspect(temp_db_engine)
        table_names_before = inspector.get_table_names()
        assert len(table_names_before) > 0, "Upgrade sonrası tablolar olmalı"
        
        # Şimdi downgrade yap
        with temp_db_engine.connect() as connection:
            context = MigrationContext.configure(connection)
            
            with connection.begin():
                migration_module.downgrade()
        
        # Tabloların kaldırıldığını kontrol et
        inspector = inspect(temp_db_engine)
        table_names_after = inspector.get_table_names()
        
        expected_tables = [
            'firmalar', 'magazalar', 'terminaller', 
            'kullanicilar', 'roller', 'yetkiler',
            'kullanici_rolleri', 'rol_yetkileri'
        ]
        
        for table_name in expected_tables:
            assert table_name not in table_names_after, f"Tablo '{table_name}' downgrade sonrası kaldırılmalı"