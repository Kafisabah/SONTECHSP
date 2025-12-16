# Version: 0.1.0
# Last Update: 2024-12-16
# Module: tests.test_veritabani_property
# Description: SONTECHSP veritabanı property testleri
# Changelog:
# - İlk oluşturma
# - Syntax hatası düzeltildi

"""
SONTECHSP Veritabanı Property Testleri

Bu modül veritabanı altyapısı için property-based testleri içerir.
Hypothesis kütüphanesi kullanılarak yazılmıştır.
"""

import os
import re
import tempfile
import logging
import pytest
from hypothesis import given, strategies as st, settings
from sqlalchemy import inspect, MetaData
from sqlalchemy.exc import IntegrityError

from sontechsp.uygulama.veritabani.taban import Taban
from sontechsp.uygulama.veritabani.modeller import (
    Kullanici, Rol, Yetki, KullaniciRol, RolYetki,
    Firma, Magaza, Terminal, Depo
)
from sontechsp.uygulama.veritabani.baglanti import sqlite_session


class TestTabloIsimlendirmeStandardi:
    """Tablo isimlendirme standardı property testleri"""
    
    @given(st.sampled_from([
        Kullanici, Rol, Yetki, KullaniciRol, RolYetki,
        Firma, Magaza, Terminal, Depo
    ]))
    @settings(max_examples=10, deadline=5000)
    def test_tablo_isimleri_turkce_ascii_snake_case(self, model_class):
        """
        **Feature: veritabani-migration-tamamlama, Property 4: Tablo İsimlendirme Standardı**
        
        For any model class, table name should use Turkish ASCII characters and snake_case format
        """
        table_name = model_class.__tablename__
        
        # Türkçe ASCII karakterler kontrolü (a-z, 0-9, _, ç, ğ, ı, ö, ş, ü)
        turkce_ascii_pattern = r'^[a-z0-9_çğıöşü]+$'
        assert re.match(turkce_ascii_pattern, table_name), \
            f"Tablo adı '{table_name}' Türkçe ASCII standardına uygun değil"
        
        # snake_case formatı kontrolü
        snake_case_pattern = r'^[a-z0-9çğıöşü]+(_[a-z0-9çğıöşü]+)*$'
        assert re.match(snake_case_pattern, table_name), \
            f"Tablo adı '{table_name}' snake_case formatında değil"
        
        # Büyük harf kontrolü
        assert table_name.islower(), \
            f"Tablo adı '{table_name}' küçük harf olmalı"
    
    @given(st.sampled_from([
        Kullanici, Rol, Yetki, KullaniciRol, RolYetki,
        Firma, Magaza, Terminal, Depo
    ]))
    @settings(max_examples=10, deadline=5000)
    def test_kolon_isimleri_snake_case(self, model_class):
        """
        **Feature: veritabani-migration-tamamlama, Property 4: Tablo İsimlendirme Standardı**
        
        For any model class, column names should be in snake_case format
        """
        # Model sınıfının kolonlarını al
        columns = [col.name for col in model_class.__table__.columns]
        
        for column_name in columns:
            # snake_case formatı kontrolü
            snake_case_pattern = r'^[a-z0-9çğıöşü]+(_[a-z0-9çğıöşü]+)*$'
            assert re.match(snake_case_pattern, column_name), \
                f"Kolon adı '{column_name}' snake_case formatında değil"
            
            # Büyük harf kontrolü
            assert column_name.islower(), \
                f"Kolon adı '{column_name}' küçük harf olmalı"


class TestForeignKeyButunlugu:
    """Foreign key bütünlüğü property testleri"""
    
    @pytest.fixture
    def test_db_session(self):
        """Test için SQLite session"""
        with sqlite_session() as session:
            # Test tabloları oluştur
            Taban.metadata.create_all(session.bind)
            yield session
            # Test sonrası temizlik
            Taban.metadata.drop_all(session.bind)
    
    @given(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters=' -.'
    )))
    @settings(max_examples=50)
    def test_firma_magaza_foreign_key_butunlugu(self, test_db_session, firma_adi):
        """
        **Feature: veritabani-migration-tamamlama, Property 5: Foreign Key Bütünlüğü**
        
        For any firma-magaza relationship, foreign key integrity should be maintained
        """
        session = test_db_session
        
        # Firma oluştur
        firma = Firma(firma_adi=firma_adi)
        session.add(firma)
        session.commit()
        
        # Mağaza oluştur
        magaza = Magaza(
            firma_id=firma.id,
            magaza_adi=f"{firma_adi} Mağaza",
            magaza_kodu="MG001"
        )
        session.add(magaza)
        session.commit()
        
        # Foreign key ilişkisini kontrol et
        assert magaza.firma_id == firma.id
        assert magaza.firma == firma
        assert magaza in firma.magazalar


class TestUniqueConstraintKorunumu:
    """Unique constraint korunumu property testleri"""
    
    @pytest.fixture
    def test_db_session(self):
        """Test için SQLite session"""
        with sqlite_session() as session:
            # Test tabloları oluştur
            Taban.metadata.create_all(session.bind)
            yield session
            # Test sonrası temizlik
            Taban.metadata.drop_all(session.bind)
    
    @given(st.text(min_size=3, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters='_-'
    )))
    @settings(max_examples=50)
    def test_kullanici_adi_unique_constraint(self, test_db_session, kullanici_adi):
        """
        **Feature: veritabani-migration-tamamlama, Property 6: Unique Constraint Korunumu**
        
        For any unique constraint field, duplicate values should be rejected
        """
        session = test_db_session
        
        # İlk kullanıcı oluştur
        kullanici1 = Kullanici(
            kullanici_adi=kullanici_adi,
            email=f"{kullanici_adi}@test.com",
            sifre_hash="hash123",
            ad="Test",
            soyad="User"
        )
        session.add(kullanici1)
        session.commit()
        
        # Aynı kullanıcı adıyla ikinci kullanıcı oluşturmaya çalış
        kullanici2 = Kullanici(
            kullanici_adi=kullanici_adi,  # Aynı kullanıcı adı
            email=f"{kullanici_adi}2@test.com",
            sifre_hash="hash456",
            ad="Test2",
            soyad="User2"
        )
        session.add(kullanici2)
        
        # Unique constraint ihlali bekleniyor
        with pytest.raises(IntegrityError):
            session.commit()


class TestBaglantiTestTutarliligi:
    """Bağlantı test tutarlılığı property testleri"""
    
    @given(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters='_-.'
    )))
    @settings(max_examples=50)
    def test_sqlite_baglanti_test_tutarliligi(self, db_dosya_adi):
        """
        **Feature: veritabani-migration-tamamlama, Property 1: Bağlantı Test Tutarlılığı**
        
        For any valid database connection parameters, connection test should be consistent
        """
        from sontechsp.uygulama.veritabani.baglanti_yardimci import sqlite_engine_olustur, baglanti_test_et_yardimci
        import tempfile
        import os
        
        # Geçici dosya oluştur
        with tempfile.NamedTemporaryFile(suffix=f"_{db_dosya_adi}.db", delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            # Engine oluştur
            engine = sqlite_engine_olustur(db_path)
            
            # İlk test
            result1 = baglanti_test_et_yardimci(engine, "SQLite")
            
            # İkinci test (aynı parametrelerle)
            result2 = baglanti_test_et_yardimci(engine, "SQLite")
            
            # Tutarlılık kontrolü
            assert result1 == result2, "Bağlantı test sonuçları tutarlı olmalı"
            assert result1 is True, "Geçerli parametrelerle bağlantı başarılı olmalı"
            
        finally:
            # Temizlik
            if os.path.exists(db_path):
                os.unlink(db_path)