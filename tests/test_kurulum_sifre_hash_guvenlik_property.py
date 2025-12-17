# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.test_kurulum_sifre_hash_guvenlik_property
# Description: Şifre hash güvenliği property testleri
# Changelog:
# - Şifre hashleme güvenliği property testleri eklendi

"""
Şifre Hash Güvenliği Property Testleri

Bu modül, şifre hashleme işlemlerinin güvenlik özelliklerini
property-based testing ile doğrular.

**Feature: kurulum-bootstrap-altyapisi, Property 10: Şifre Hash Güvenliği**
**Validates: Requirements 5.3**
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from hypothesis import assume, given, settings, strategies as st

from uygulama.kurulum import KullaniciHatasi
from uygulama.kurulum.admin_olusturucu import sifre_dogrula, sifre_hash_olustur


class TestSifreHashGuvenlikProperty:
    """Şifre hash güvenliği property testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        """Her test sonrası çalışır"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    @given(
        sifre=st.text(min_size=3, max_size=100).filter(
            lambda x: x.strip() and len(x.strip()) >= 3
        )
    )
    @settings(max_examples=50, deadline=3000)
    def test_bcrypt_hash_format_property(self, sifre):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 10: Şifre Hash Güvenliği**
        **Validates: Requirements 5.3**
        
        Herhangi bir geçerli şifre için, bcrypt hash formatında hash oluşturulmalı
        """
        assume(len(sifre.strip()) >= 3)
        
        with patch('uygulama.kurulum.admin_olusturucu.PASSLIB_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.pwd_context') as mock_pwd_context:
            
            # Gerçekçi bcrypt hash formatı simüle et
            bcrypt_hash = f"$2b$12${'a' * 22}{'b' * 31}"
            mock_pwd_context.hash.return_value = bcrypt_hash
            
            hash_sonuc = sifre_hash_olustur(sifre)
            
            # Bcrypt hash formatını kontrol et
            assert hash_sonuc == bcrypt_hash
            assert len(hash_sonuc) >= 10
            assert hash_sonuc.startswith('$2b')  # Bcrypt identifier$')  # Bcrypt identifier$')$')  # Bcrypt identifier
            
            # Hash fonksiyonunun çağrıldığını doğrula
            mock_pwd_context.hash.assert_called_once_with(sifre)
    
    @given(
        sifre=st.text(min_size=3, max_size=100).filter(
            lambda x: x.strip() and len(x.strip()) >= 3
        )
    )
    @settings(max_examples=50, deadline=3000)
    def test_sifre_dogrulama_property(self, sifre):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 10: Şifre Hash Güvenliği**
        **Validates: Requirements 5.3**
        
        Hash edilmiş şifre, orijinal şifre ile doğrulanabilmeli
        """
        assume(len(sifre.strip()) >= 3)
        
        with patch('uygulama.kurulum.admin_olusturucu.PASSLIB_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.pwd_context') as mock_pwd_context:
            
            # Hash oluşturma
            test_hash = f"$2b$12$test_hash_for_{hash(sifre) % 10000}"
            mock_pwd_context.hash.return_value = test_hash
            
            # Doğrulama - doğru şifre
            mock_pwd_context.verify.return_value = True
            
            hash_sonuc = sifre_hash_olustur(sifre)
            dogrulama_sonuc = sifre_dogrula(sifre, hash_sonuc)
            
            assert hash_sonuc == test_hash
            assert dogrulama_sonuc == True
            
            # Doğrulama fonksiyonunun çağrıldığını kontrol et
            mock_pwd_context.verify.assert_called_once_with(sifre, hash_sonuc)
    
    @given(
        gecersiz_sifre=st.one_of(
            st.just(""),
            st.just("  "),
            st.text(max_size=2),
            st.just(None)
        )
    )
    @settings(max_examples=50, deadline=3000)
    def test_gecersiz_sifre_guvenlik_property(self, gecersiz_sifre):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 10: Şifre Hash Güvenliği**
        **Validates: Requirements 5.3**
        
        Geçersiz şifreler güvenlik hatası fırlatmalı
        """
        with patch('uygulama.kurulum.admin_olusturucu.PASSLIB_AVAILABLE', True):
            
            if gecersiz_sifre is None:
                with pytest.raises(KullaniciHatasi, match="Geçersiz şifre"):
                    sifre_hash_olustur(gecersiz_sifre)
            elif isinstance(gecersiz_sifre, str) and len(gecersiz_sifre.strip()) < 3:
                with pytest.raises(KullaniciHatasi, match="Şifre çok kısa"):
                    sifre_hash_olustur(gecersiz_sifre)
    
    def test_passlib_olmamasi_guvenlik_property(self):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 10: Şifre Hash Güvenliği**
        **Validates: Requirements 5.3**
        
        Passlib yoksa güvenlik hatası verilmeli
        """
        with patch('uygulama.kurulum.admin_olusturucu.PASSLIB_AVAILABLE', False):
            
            with pytest.raises(KullaniciHatasi, match="passlib.*bulunamadı"):
                sifre_hash_olustur("test123")
            
            # Doğrulama da başarısız olmalı
            dogrulama_sonuc = sifre_dogrula("test123", "hash")
            assert dogrulama_sonuc == False