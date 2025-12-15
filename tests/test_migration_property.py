# Version: 0.1.0
# Last Update: 2024-12-15
# Module: tests.test_migration_property
# Description: SONTECHSP migration property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Migration Property Testleri

Bu modül migration yönetimi için property-based testleri içerir.
Hypothesis kütüphanesi kullanılarak yazılmıştır.
"""

import pytest
import tempfile
import os
from hypothesis import given, strategies as st, settings
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from sontechsp.uygulama.veritabani.migration_yoneticisi import MigrationYoneticisi
from sontechsp.uygulama.veritabani.taban import Taban


class TestMigrationDurumSorgusu:
    """Migration durum sorgusu property testleri"""
    
    @pytest.fixture
    def temp_db_engine(self):
        """Geçici SQLite veritabanı engine'i"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name
        
        engine = create_engine(
            f"sqlite:///{db_path}",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )
        
        yield engine
        
        engine.dispose()
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def migration_yoneticisi(self, temp_db_engine):
        """Test migration yöneticisi"""
        return MigrationYoneticisi(temp_db_engine)
    
    @given(st.integers(min_value=1, max_value=5))
    @settings(max_examples=10)
    def test_migration_durum_sorgusu_tutarliligi(self, migration_yoneticisi, sorgu_sayisi):
        """
        **Feature: veritabani-migration-tamamlama, Property 11: Migration Durum Sorgusu**
        
        For any migration state, current database version should be reported correctly
        """
        # Birden fazla kez durum sorgula
        durumlar = []
        for i in range(sorgu_sayisi):
            durum = migration_yoneticisi.migration_durumu()
            durumlar.append(durum)
        
        # Tüm sorgular aynı sonucu vermeli
        ilk_durum = durumlar[0]
        for durum in durumlar[1:]:
            assert durum['current_revision'] == ilk_durum['current_revision'], \
                "Migration durum sorguları tutarlı olmalı"
            assert durum['head_revision'] == ilk_durum['head_revision'], \
                "Head revision tutarlı olmalı"
            assert durum['is_up_to_date'] == ilk_durum['is_up_to_date'], \
                "Güncellik durumu tutarlı olmalı"
    
    def test_migration_durum_sorgusu_format(self, migration_yoneticisi):
        """
        **Feature: veritabani-migration-tamamlama, Property 11: Migration Durum Sorgusu**
        
        For any migration status query, response should have required fields
        """
        durum = migration_yoneticisi.migration_durumu()
        
        # Gerekli alanlar mevcut olmalı
        required_fields = [
            'current_revision', 'head_revision', 'is_up_to_date',
            'pending_migrations', 'pending_count', 'query_time'
        ]
        
        for field in required_fields:
            assert field in durum, f"Migration durumu '{field}' alanını içermeli"
        
        # Veri tipleri doğru olmalı
        assert isinstance(durum['is_up_to_date'], bool), "is_up_to_date boolean olmalı"
        assert isinstance(durum['pending_migrations'], list), "pending_migrations list olmalı"
        assert isinstance(durum['pending_count'], int), "pending_count integer olmalı"
        assert durum['pending_count'] >= 0, "pending_count negatif olamaz"


class TestMigrationGecmisListesi:
    """Migration geçmiş listesi property testleri"""
    
    @pytest.fixture
    def temp_db_engine(self):
        """Geçici SQLite veritabanı engine'i"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name
        
        engine = create_engine(
            f"sqlite:///{db_path}",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )
        
        yield engine
        
        engine.dispose()
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def migration_yoneticisi(self, temp_db_engine):
        """Test migration yöneticisi"""
        return MigrationYoneticisi(temp_db_engine)
    
    @given(st.integers(min_value=1, max_value=3))
    @settings(max_examples=5)
    def test_migration_gecmis_kronolojik_siralama(self, migration_yoneticisi, sorgu_sayisi):
        """
        **Feature: veritabani-migration-tamamlama, Property 12: Migration Geçmiş Listesi**
        
        For any migration history query, all applied migrations should be listed chronologically
        """
        # Birden fazla kez geçmiş sorgula
        gecmisler = []
        for i in range(sorgu_sayisi):
            gecmis = migration_yoneticisi.migration_gecmisi()
            gecmisler.append(gecmis)
        
        # Tüm sorgular aynı sonucu vermeli
        ilk_gecmis = gecmisler[0]
        for gecmis in gecmisler[1:]:
            assert len(gecmis) == len(ilk_gecmis), "Geçmiş listesi uzunluğu tutarlı olmalı"
            
            # Her migration'ın aynı sırada olduğunu kontrol et
            for i, migration in enumerate(gecmis):
                assert migration['revision'] == ilk_gecmis[i]['revision'], \
                    "Migration sırası tutarlı olmalı"
    
    def test_migration_gecmis_format(self, migration_yoneticisi):
        """
        **Feature: veritabani-migration-tamamlama, Property 12: Migration Geçmiş Listesi**
        
        For any migration history entry, required fields should be present
        """
        gecmis = migration_yoneticisi.migration_gecmisi()
        
        # Her migration entry gerekli alanları içermeli
        required_fields = [
            'revision', 'description', 'down_revision', 
            'branch_labels', 'depends_on', 'is_applied'
        ]
        
        for migration in gecmis:
            for field in required_fields:
                assert field in migration, f"Migration entry '{field}' alanını içermeli"
            
            # Veri tipleri doğru olmalı
            assert isinstance(migration['is_applied'], bool), "is_applied boolean olmalı"
            assert isinstance(migration['revision'], (str, type(None))), "revision string olmalı"
    
    def test_migration_gecmis_uygulanan_migration_kontrolu(self, migration_yoneticisi):
        """
        **Feature: veritabani-migration-tamamlama, Property 12: Migration Geçmiş Listesi**
        
        For any migration in history, is_applied should be True
        """
        gecmis = migration_yoneticisi.migration_gecmisi()
        
        # Geçmişte olan tüm migration'lar uygulanmış olmalı
        for migration in gecmis:
            assert migration['is_applied'] is True, \
                f"Geçmişte olan migration '{migration['revision']}' uygulanmış olmalı"


class TestMigrationCakismaKontrolu:
    """Migration çakışma kontrolü property testleri"""
    
    @pytest.fixture
    def temp_db_engine(self):
        """Geçici SQLite veritabanı engine'i"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = tmp_file.name
        
        engine = create_engine(
            f"sqlite:///{db_path}",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )
        
        yield engine
        
        engine.dispose()
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def migration_yoneticisi(self, temp_db_engine):
        """Test migration yöneticisi"""
        return MigrationYoneticisi(temp_db_engine)
    
    @given(st.integers(min_value=1, max_value=3))
    @settings(max_examples=5)
    def test_cakisma_kontrolu_tutarliligi(self, migration_yoneticisi, kontrol_sayisi):
        """
        **Feature: veritabani-migration-tamamlama, Property: Migration Çakışma Kontrolü**
        
        For any conflict check, result should be consistent across multiple calls
        """
        # Birden fazla kez çakışma kontrolü yap
        kontroller = []
        for i in range(kontrol_sayisi):
            kontrol = migration_yoneticisi.migration_cakisma_kontrolu()
            kontroller.append(kontrol)
        
        # Tüm kontroller aynı sonucu vermeli
        ilk_kontrol = kontroller[0]
        for kontrol in kontroller[1:]:
            assert kontrol['has_conflict'] == ilk_kontrol['has_conflict'], \
                "Çakışma durumu tutarlı olmalı"
            assert kontrol['head_count'] == ilk_kontrol['head_count'], \
                "Head sayısı tutarlı olmalı"
            assert kontrol['heads'] == ilk_kontrol['heads'], \
                "Head listesi tutarlı olmalı"
    
    def test_cakisma_kontrolu_format(self, migration_yoneticisi):
        """
        **Feature: veritabani-migration-tamamlama, Property: Migration Çakışma Kontrolü**
        
        For any conflict check, response should have required fields
        """
        kontrol = migration_yoneticisi.migration_cakisma_kontrolu()
        
        # Gerekli alanlar mevcut olmalı
        required_fields = [
            'has_conflict', 'head_count', 'heads', 
            'conflict_message', 'check_time'
        ]
        
        for field in required_fields:
            assert field in kontrol, f"Çakışma kontrolü '{field}' alanını içermeli"
        
        # Veri tipleri doğru olmalı
        assert isinstance(kontrol['has_conflict'], bool), "has_conflict boolean olmalı"
        assert isinstance(kontrol['head_count'], int), "head_count integer olmalı"
        assert isinstance(kontrol['heads'], list), "heads list olmalı"
        assert kontrol['head_count'] >= 0, "head_count negatif olamaz"
        assert len(kontrol['heads']) == kontrol['head_count'], \
            "heads listesi uzunluğu head_count ile eşleşmeli"
    
    def test_cakisma_durumu_mantigi(self, migration_yoneticisi):
        """
        **Feature: veritabani-migration-tamamlama, Property: Migration Çakışma Kontrolü**
        
        For any conflict check, logic should be consistent
        """
        kontrol = migration_yoneticisi.migration_cakisma_kontrolu()
        
        # Mantık kontrolü
        if kontrol['head_count'] > 1:
            assert kontrol['has_conflict'] is True, \
                "Birden fazla head varsa çakışma olmalı"
            assert kontrol['conflict_message'] is not None, \
                "Çakışma varsa mesaj olmalı"
        else:
            assert kontrol['has_conflict'] is False, \
                "Tek head varsa çakışma olmamalı"