# Version: 0.1.0
# Last Update: 2024-12-15
# Module: tests.test_session_property
# Description: SONTECHSP session yönetimi property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Session Yönetimi Property Testleri

Bu modül session yönetimi için property-based testleri içerir.
Hypothesis kütüphanesi kullanılarak yazılmıştır.
"""

import pytest
from hypothesis import given, strategies as st, settings
from sqlalchemy.exc import IntegrityError

from sontechsp.uygulama.veritabani.taban import Taban
from sontechsp.uygulama.veritabani.modeller import Firma
from sontechsp.uygulama.veritabani.baglanti import sqlite_session


class TestSessionCommitDavranisi:
    """Session commit davranışı property testleri"""
    
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
    def test_basarili_islem_commit_edilir(self, test_db_session, firma_adi):
        """
        **Feature: veritabani-migration-tamamlama, Property 7: Session Commit Davranışı**
        
        For any successful database operation, session should be automatically committed
        """
        session = test_db_session
        
        # Firma oluştur
        firma = Firma(firma_adi=firma_adi)
        session.add(firma)
        
        # Session'dan çık (commit otomatik olmalı)
        session.commit()
        
        # Yeni session ile kontrol et
        with sqlite_session() as new_session:
            saved_firma = new_session.query(Firma).filter_by(firma_adi=firma_adi).first()
            assert saved_firma is not None, "Başarılı işlem commit edilmeli"
            assert saved_firma.firma_adi == firma_adi, "Veri doğru kaydedilmeli"
    
    @given(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters=' -.'
    )))
    @settings(max_examples=50)
    def test_context_manager_otomatik_commit(self, firma_adi):
        """
        **Feature: veritabani-migration-tamamlama, Property 7: Session Commit Davranışı**
        
        For any successful operation in context manager, commit should be automatic
        """
        # Context manager ile işlem yap
        with sqlite_session() as session:
            # Test tabloları oluştur
            Taban.metadata.create_all(session.bind)
            
            # Firma oluştur
            firma = Firma(firma_adi=firma_adi)
            session.add(firma)
            # Context manager çıkışında otomatik commit olmalı
        
        # Yeni session ile kontrol et
        with sqlite_session() as new_session:
            saved_firma = new_session.query(Firma).filter_by(firma_adi=firma_adi).first()
            assert saved_firma is not None, "Context manager otomatik commit yapmalı"
            assert saved_firma.firma_adi == firma_adi, "Veri doğru kaydedilmeli"


class TestSessionRollbackDavranisi:
    """Session rollback davranışı property testleri"""
    
    @given(st.text(min_size=3, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters='_-'
    )))
    @settings(max_examples=50)
    def test_hata_durumunda_rollback(self, firma_adi):
        """
        **Feature: veritabani-migration-tamamlama, Property 8: Session Rollback Davranışı**
        
        For any error condition, session should be automatically rolled back
        """
        # İlk firma oluştur
        with sqlite_session() as session:
            Taban.metadata.create_all(session.bind)
            firma1 = Firma(firma_adi=firma_adi)
            session.add(firma1)
        
        # Aynı isimle ikinci firma oluşturmaya çalış (hata olacak)
        try:
            with sqlite_session() as session:
                firma2 = Firma(firma_adi=firma_adi)  # Aynı isim
                session.add(firma2)
                # Hata burada oluşacak ve rollback yapılacak
        except Exception:
            pass  # Hata bekleniyor
        
        # Kontrol et - sadece ilk firma olmalı
        with sqlite_session() as session:
            firmalar = session.query(Firma).filter_by(firma_adi=firma_adi).all()
            assert len(firmalar) == 1, "Hata durumunda rollback yapılmalı"
    
    def test_exception_handling_rollback(self):
        """
        **Feature: veritabani-migration-tamamlama, Property 8: Session Rollback Davranışı**
        
        For any exception in context manager, rollback should be automatic
        """
        # Exception ile context manager test et
        try:
            with sqlite_session() as session:
                Taban.metadata.create_all(session.bind)
                
                # Firma oluştur
                firma = Firma(firma_adi="Test Firma")
                session.add(firma)
                
                # Kasıtlı exception fırlat
                raise ValueError("Test exception")
                
        except ValueError:
            pass  # Exception bekleniyor
        
        # Kontrol et - hiçbir veri kaydedilmemeli
        with sqlite_session() as session:
            firma_count = session.query(Firma).count()
            assert firma_count == 0, "Exception durumunda rollback yapılmalı"


class TestSessionKaynakTemizligi:
    """Session kaynak temizliği property testleri"""
    
    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=20)
    def test_session_kapanma_kaynak_temizligi(self, session_sayisi):
        """
        **Feature: veritabani-migration-tamamlama, Property 9: Session Kaynak Temizliği**
        
        For any session usage, resource cleanup should be performed on exit
        """
        sessions = []
        
        # Birden fazla session oluştur ve kapat
        for i in range(session_sayisi):
            with sqlite_session() as session:
                Taban.metadata.create_all(session.bind)
                
                # Session'ı listeye ekle (referans için)
                sessions.append(session)
                
                # Basit işlem yap
                firma = Firma(firma_adi=f"Test Firma {i}")
                session.add(firma)
                
                # Context manager çıkışında temizlik olmalı
        
        # Tüm session'lar kapatılmış olmalı
        for session in sessions:
            assert not session.is_active, "Session kapatılmış olmalı"
    
    def test_context_manager_finally_block(self):
        """
        **Feature: veritabani-migration-tamamlama, Property 9: Session Kaynak Temizliği**
        
        For context manager, cleanup should happen even with exceptions
        """
        session_ref = None
        
        # Exception ile context manager test et
        try:
            with sqlite_session() as session:
                Taban.metadata.create_all(session.bind)
                session_ref = session
                
                # Firma oluştur
                firma = Firma(firma_adi="Test Firma")
                session.add(firma)
                
                # Exception fırlat
                raise RuntimeError("Test exception")
                
        except RuntimeError:
            pass  # Exception bekleniyor
        
        # Session temizlenmiş olmalı
        assert session_ref is not None, "Session referansı alınmalı"
        assert not session_ref.is_active, "Exception sonrası session kapatılmalı"


class TestContextManagerExceptionHandling:
    """Context manager exception handling property testleri"""
    
    @given(st.sampled_from([
        ValueError, RuntimeError, TypeError, AttributeError
    ]))
    @settings(max_examples=20)
    def test_exception_turlerine_gore_handling(self, exception_type):
        """
        **Feature: veritabani-migration-tamamlama, Property 10: Context Manager Exception Handling**
        
        For any exception type in context manager, automatic rollback and cleanup should work
        """
        # Exception ile test et
        exception_occurred = False
        try:
            with sqlite_session() as session:
                Taban.metadata.create_all(session.bind)
                
                # Firma oluştur
                firma = Firma(firma_adi="Test Firma")
                session.add(firma)
                
                # Belirtilen exception tipini fırlat
                raise exception_type("Test exception")
                
        except exception_type:
            exception_occurred = True
        
        # Exception yakalandığını kontrol et
        assert exception_occurred, f"{exception_type.__name__} exception yakalanmalı"
        
        # Veri kaydedilmemiş olmalı (rollback yapılmış)
        with sqlite_session() as session:
            firma_count = session.query(Firma).count()
            assert firma_count == 0, "Exception durumunda rollback yapılmalı"