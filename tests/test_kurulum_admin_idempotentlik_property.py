# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.test_kurulum_admin_idempotentlik_property
# Description: Admin kullanıcı idempotentlik property testleri
# Changelog:
# - Admin kullanıcı oluşturma idempotentlik property testleri eklendi
# - Import path'leri tam modül yolları ile güncellendi
# - Hypothesis assume import'u eklendi

"""
Admin Kullanıcı İdempotentlik Property Testleri

Bu modül, admin kullanıcı oluşturma işlemlerinin idempotentlik özelliğini
property-based testing ile doğrular.

**Feature: kurulum-bootstrap-altyapisi, Property 9: Admin Kullanıcı İdempotentliği**
**Validates: Requirements 5.2**
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from hypothesis import assume, given, settings, strategies as st
from sqlalchemy.orm import Session

from uygulama.kurulum import KullaniciHatasi
from uygulama.kurulum.admin_olusturucu import (
    admin_olustur, admin_varsa_gec, sifre_hash_olustur
)


class TestAdminIdempotentlikProperty:
    """Admin kullanıcı idempotentlik property testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.mock_session = Mock(spec=Session)
        self.mock_kullanici_depo = Mock()
        
    def teardown_method(self):
        """Her test sonrası çalışır"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    @given(
        kullanici_adi=st.text(min_size=1, max_size=20).filter(
            lambda x: x.strip() and x.isalnum()
        ),
        sifre=st.text(min_size=3, max_size=50).filter(
            lambda x: x.strip() and len(x.strip()) >= 3
        )
    )
    @settings(max_examples=100, deadline=5000)
    def test_admin_olusturma_idempotentlik_property(self, kullanici_adi, sifre):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 9: Admin Kullanıcı İdempotentliği**
        **Validates: Requirements 5.2**
        
        Herhangi bir veritabanı durumu için, admin oluşturma işlemini iki kez 
        çalıştırmak, mevcut admin kullanıcısını korumalı
        """
        
        with patch('uygulama.kurulum.admin_olusturucu.SQLALCHEMY_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.MODELS_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.PASSLIB_AVAILABLE', True), \
             patch('sontechsp.uygulama.veritabani.depolar.kullanici_depo.KullaniciDepo') as mock_depo_class, \
             patch('sontechsp.uygulama.veritabani.modeller.kullanici_yetki.Kullanici') as mock_kullanici_class, \
             patch('uygulama.kurulum.admin_olusturucu.pwd_context') as mock_pwd_context:
            
            # Mock setup
            mock_depo = Mock()
            mock_depo_class.return_value = mock_depo
            mock_pwd_context.hash.return_value = f"hashed_{sifre}"
            
            # İlk durumda admin yok
            mock_depo.kullanici_adi_ile_getir.return_value = None
            mock_kullanici_instance = Mock()
            mock_kullanici_class.return_value = mock_kullanici_instance
            
            # İlk çalıştırma - admin oluşturulmalı
            admin_olustur(self.mock_session, kullanici_adi, sifre)
            
            # Doğrulamalar - ilk çalıştırma
            assert mock_depo.kullanici_adi_ile_getir.called
            assert self.mock_session.add.called
            assert self.mock_session.commit.called
            
            # İkinci durumda admin var
            mock_depo.kullanici_adi_ile_getir.return_value = mock_kullanici_instance
            self.mock_session.reset_mock()
            
            # İkinci çalıştırma - admin oluşturulmamalı (idempotentlik)
            admin_olustur(self.mock_session, kullanici_adi, sifre)
            
            # Doğrulamalar - ikinci çalıştırma
            assert mock_depo.kullanici_adi_ile_getir.called
            assert not self.mock_session.add.called  # Yeni kullanıcı eklenmemeli
            assert not self.mock_session.commit.called  # Commit yapılmamalı
    
    @given(
        kullanici_adi=st.text(min_size=1, max_size=20).filter(
            lambda x: x.strip() and x.isalnum()
        )
    )
    @settings(max_examples=100, deadline=5000)
    def test_admin_varsa_gec_tutarlilik_property(self, kullanici_adi):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 9: Admin Kullanıcı İdempotentliği**
        **Validates: Requirements 5.2**
        
        admin_varsa_gec fonksiyonu aynı session için tutarlı sonuç döndürmeli
        """
        assume(len(kullanici_adi.strip()) > 0)
        
        with patch('uygulama.kurulum.admin_olusturucu.SQLALCHEMY_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.MODELS_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.KullaniciDepo') as mock_depo_class:
            
            mock_depo = Mock()
            mock_depo_class.return_value = mock_depo
            
            # Admin var durumu
            mock_kullanici = Mock()
            mock_depo.kullanici_adi_ile_getir.return_value = mock_kullanici
            
            # Birden fazla çağrı yapıldığında aynı sonuç dönmeli
            sonuc1 = admin_varsa_gec(self.mock_session)
            sonuc2 = admin_varsa_gec(self.mock_session)
            sonuc3 = admin_varsa_gec(self.mock_session)
            
            assert sonuc1 == sonuc2 == sonuc3 == True
            
            # Admin yok durumu
            mock_depo.kullanici_adi_ile_getir.return_value = None
            
            sonuc4 = admin_varsa_gec(self.mock_session)
            sonuc5 = admin_varsa_gec(self.mock_session)
            
            assert sonuc4 == sonuc5 == False
    
    @given(
        sifre=st.text(min_size=3, max_size=100).filter(
            lambda x: x.strip() and len(x.strip()) >= 3
        )
    )
    @settings(max_examples=100, deadline=5000)
    def test_sifre_hash_idempotentlik_property(self, sifre):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 9: Admin Kullanıcı İdempotentliği**
        **Validates: Requirements 5.2**
        
        Aynı şifre için hash oluşturma işlemi her zaman geçerli hash döndürmeli
        """
        assume(len(sifre.strip()) >= 3)
        
        with patch('uygulama.kurulum.admin_olusturucu.PASSLIB_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.pwd_context') as mock_pwd_context:
            
            expected_hash = f"bcrypt_hash_{hash(sifre)}"
            mock_pwd_context.hash.return_value = expected_hash
            
            # Aynı şifre için hash oluştur
            hash1 = sifre_hash_olustur(sifre)
            hash2 = sifre_hash_olustur(sifre)
            
            # Her iki hash de geçerli olmalı (bcrypt her seferinde farklı salt kullanır)
            assert hash1 == expected_hash
            assert hash2 == expected_hash
            assert len(hash1) >= 10
            assert len(hash2) >= 10
    
    @given(
        kullanici_adi=st.text(min_size=1, max_size=20).filter(
            lambda x: x.strip() and x.isalnum()
        ),
        sifre=st.text(min_size=3, max_size=50).filter(
            lambda x: x.strip() and len(x.strip()) >= 3
        )
    )
    @settings(max_examples=100, deadline=5000)
    def test_admin_olusturma_hata_durumu_idempotentlik_property(self, kullanici_adi, sifre):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 9: Admin Kullanıcı İdempotentliği**
        **Validates: Requirements 5.2**
        
        Hata durumunda bile idempotentlik korunmalı - mevcut admin etkilenmemeli
        """
        assume(len(kullanici_adi.strip()) > 0)
        assume(len(sifre.strip()) >= 3)
        
        with patch('uygulama.kurulum.admin_olusturucu.SQLALCHEMY_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.MODELS_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.PASSLIB_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.KullaniciDepo') as mock_depo_class:
            
            mock_depo = Mock()
            mock_depo_class.return_value = mock_depo
            
            # Mevcut admin var
            mock_kullanici = Mock()
            mock_depo.kullanici_adi_ile_getir.return_value = mock_kullanici
            
            # Admin oluşturma çağrısı - mevcut admin korunmalı
            admin_olustur(self.mock_session, kullanici_adi, sifre)
            
            # Mevcut admin etkilenmemeli
            assert not self.mock_session.add.called
            assert not self.mock_session.commit.called
            assert not self.mock_session.rollback.called
    
    @given(
        gecersiz_sifre=st.one_of(
            st.just(""),
            st.just("  "),
            st.text(max_size=2),
            st.just(None)
        )
    )
    @settings(max_examples=100, deadline=5000)
    def test_gecersiz_sifre_hata_property(self, gecersiz_sifre):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 9: Admin Kullanıcı İdempotentliği**
        **Validates: Requirements 5.2**
        
        Geçersiz şifre ile admin oluşturma girişimi hata fırlatmalı
        """
        with patch('uygulama.kurulum.admin_olusturucu.PASSLIB_AVAILABLE', True):
            
            if gecersiz_sifre is None:
                with pytest.raises(KullaniciHatasi, match="Geçersiz şifre"):
                    sifre_hash_olustur(gecersiz_sifre)
            elif isinstance(gecersiz_sifre, str) and len(gecersiz_sifre.strip()) < 3:
                with pytest.raises(KullaniciHatasi, match="Şifre çok kısa"):
                    sifre_hash_olustur(gecersiz_sifre)
    
    @settings(max_examples=100, deadline=5000)
    def test_bagimliliklarin_olmamasi_durumu_property(self):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 9: Admin Kullanıcı İdempotentliği**
        **Validates: Requirements 5.2**
        
        Gerekli bağımlılıklar yoksa uygun hata mesajları verilmeli
        """
        # SQLAlchemy yok
        with patch('uygulama.kurulum.admin_olusturucu.SQLALCHEMY_AVAILABLE', False):
            with pytest.raises(KullaniciHatasi, match="SQLAlchemy.*bulunamadı"):
                admin_varsa_gec(self.mock_session)
        
        # Passlib yok
        with patch('uygulama.kurulum.admin_olusturucu.PASSLIB_AVAILABLE', False):
            with pytest.raises(KullaniciHatasi, match="passlib.*bulunamadı"):
                sifre_hash_olustur("test123")
        
        # Modeller yok
        with patch('uygulama.kurulum.admin_olusturucu.SQLALCHEMY_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.MODELS_AVAILABLE', False):
            with pytest.raises(KullaniciHatasi, match="kullanıcı modelleri.*bulunamadı"):
                admin_varsa_gec(self.mock_session)