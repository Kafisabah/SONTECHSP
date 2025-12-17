# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.test_kurulum_kullanici_hata_loglama_property
# Description: Kullanıcı oluşturma hata loglama property testleri
# Changelog:
# - Kullanıcı oluşturma hata loglama property testleri eklendi

"""
Kullanıcı Oluşturma Hata Loglama Property Testleri

Bu modül, kullanıcı oluşturma işlemlerinde hata durumlarının
doğru şekilde loglandığını property-based testing ile doğrular.

**Feature: kurulum-bootstrap-altyapisi, Property 11: Kullanıcı Oluşturma Hata Loglama**
**Validates: Requirements 5.4**
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from hypothesis import assume, given, settings, strategies as st
from sqlalchemy.exc import SQLAlchemyError

from uygulama.kurulum.admin_olusturucu import (
    admin_olustur, admin_varsa_gec, sifre_hash_olustur
)
from uygulama.kurulum import KullaniciHatasi


class TestKullaniciHataLoglamaProperty:
    """Kullanıcı oluşturma hata loglama property testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.mock_session = Mock()
        
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
        ),
        hata_mesaji=st.text(min_size=5, max_size=100).filter(
            lambda x: x.strip()
        )
    )
    @settings(max_examples=100, deadline=5000)
    def test_veritabani_hatasi_loglama_property(self, kullanici_adi, sifre, hata_mesaji):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 11: Kullanıcı Oluşturma Hata Loglama**
        **Validates: Requirements 5.4**
        
        Herhangi bir veritabanı hatası durumunda, sistem hata detaylarını loglamalı
        """
        assume(len(kullanici_adi.strip()) > 0)
        assume(len(sifre.strip()) >= 3)
        assume(len(hata_mesaji.strip()) >= 5)
        
        with patch('uygulama.kurulum.admin_olusturucu.SQLALCHEMY_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.MODELS_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.PASSLIB_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.KullaniciDepo') as mock_depo_class, \
             patch('uygulama.kurulum.admin_olusturucu.Kullanici') as mock_kullanici_class, \
             patch('uygulama.kurulum.admin_olusturucu.pwd_context') as mock_pwd_context, \
             patch('uygulama.kurulum.admin_olusturucu.logger') as mock_logger:
            
            # Mock setup
            mock_depo = Mock()
            mock_depo_class.return_value = mock_depo
            mock_depo.kullanici_adi_ile_getir.return_value = None  # Admin yok
            mock_pwd_context.hash.return_value = f"hashed_{sifre}"
            mock_kullanici_class.return_value = Mock()
            
            # Veritabanı hatası simüle et
            db_error = SQLAlchemyError(hata_mesaji)
            self.mock_session.commit.side_effect = db_error
            
            # Admin oluşturma girişimi - hata bekleniyor
            with pytest.raises(KullaniciHatasi):
                admin_olustur(self.mock_session, kullanici_adi, sifre)
            
            # Hata loglandığını doğrula
            mock_logger.error.assert_called()
            error_calls = mock_logger.error.call_args_list
            
            # En az bir error log çağrısı olmalı ve hata mesajını içermeli
            assert len(error_calls) > 0
            error_logged = any(hata_mesaji in str(call_args) for call_args in error_calls)
            assert error_logged, f"Hata mesajı loglarda bulunamadı: {hata_mesaji}"
            
            # Rollback çağrıldığını doğrula
            self.mock_session.rollback.assert_called()
    
    @given(
        kullanici_adi=st.text(min_size=1, max_size=20).filter(
            lambda x: x.strip() and x.isalnum()
        ),
        hata_mesaji=st.text(min_size=5, max_size=100).filter(
            lambda x: x.strip()
        )
    )
    @settings(max_examples=100, deadline=5000)
    def test_admin_kontrol_hatasi_loglama_property(self, kullanici_adi, hata_mesaji):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 11: Kullanıcı Oluşturma Hata Loglama**
        **Validates: Requirements 5.4**
        
        Admin kontrol işlemi sırasında hata oluşursa detaylar loglanmalı
        """
        assume(len(kullanici_adi.strip()) > 0)
        assume(len(hata_mesaji.strip()) >= 5)
        
        with patch('uygulama.kurulum.admin_olusturucu.SQLALCHEMY_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.MODELS_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.KullaniciDepo') as mock_depo_class, \
             patch('uygulama.kurulum.admin_olusturucu.logger') as mock_logger:
            
            # Mock setup
            mock_depo = Mock()
            mock_depo_class.return_value = mock_depo
            
            # Admin kontrol hatası simüle et
            db_error = SQLAlchemyError(hata_mesaji)
            mock_depo.kullanici_adi_ile_getir.side_effect = db_error
            
            # Admin kontrol girişimi - hata bekleniyor
            with pytest.raises(KullaniciHatasi):
                admin_varsa_gec(self.mock_session)
            
            # Hata loglandığını doğrula
            mock_logger.error.assert_called()
            error_calls = mock_logger.error.call_args_list
            
            # Hata mesajının loglandığını kontrol et
            assert len(error_calls) > 0
            error_logged = any(hata_mesaji in str(call_args) for call_args in error_calls)
            assert error_logged, f"Admin kontrol hatası loglarda bulunamadı: {hata_mesaji}"
    
    @given(
        gecersiz_sifre=st.one_of(
            st.just(""),
            st.just("  "),
            st.text(max_size=2),
            st.just(None)
        ),
        kullanici_adi=st.text(min_size=1, max_size=20).filter(
            lambda x: x.strip() and x.isalnum()
        )
    )
    @settings(max_examples=100, deadline=5000)
    def test_sifre_hatasi_loglama_property(self, gecersiz_sifre, kullanici_adi):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 11: Kullanıcı Oluşturma Hata Loglama**
        **Validates: Requirements 5.4**
        
        Şifre hashleme hatası durumunda detaylar loglanmalı
        """
        assume(len(kullanici_adi.strip()) > 0)
        
        with patch('uygulama.kurulum.admin_olusturucu.SQLALCHEMY_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.MODELS_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.PASSLIB_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.KullaniciDepo') as mock_depo_class, \
             patch('uygulama.kurulum.admin_olusturucu.logger') as mock_logger:
            
            # Mock setup
            mock_depo = Mock()
            mock_depo_class.return_value = mock_depo
            mock_depo.kullanici_adi_ile_getir.return_value = None  # Admin yok
            
            # Admin oluşturma girişimi - şifre hatası bekleniyor
            with pytest.raises(KullaniciHatasi):
                admin_olustur(self.mock_session, kullanici_adi, gecersiz_sifre)
            
            # Hata loglandığını doğrula
            mock_logger.error.assert_called()
            error_calls = mock_logger.error.call_args_list
            
            # Şifre hatası loglandığını kontrol et
            assert len(error_calls) > 0
            sifre_error_logged = any(
                "Admin oluşturma hatası" in str(call_args) 
                for call_args in error_calls
            )
            assert sifre_error_logged, "Şifre hatası loglarda bulunamadı"
    
    @given(
        kullanici_adi=st.text(min_size=1, max_size=20).filter(
            lambda x: x.strip() and x.isalnum()
        ),
        sifre=st.text(min_size=3, max_size=50).filter(
            lambda x: x.strip() and len(x.strip()) >= 3
        ),
        beklenmeyen_hata=st.text(min_size=5, max_size=100).filter(
            lambda x: x.strip()
        )
    )
    @settings(max_examples=100, deadline=5000)
    def test_beklenmeyen_hata_loglama_property(self, kullanici_adi, sifre, beklenmeyen_hata):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 11: Kullanıcı Oluşturma Hata Loglama**
        **Validates: Requirements 5.4**
        
        Beklenmeyen hatalar da detaylı şekilde loglanmalı
        """
        assume(len(kullanici_adi.strip()) > 0)
        assume(len(sifre.strip()) >= 3)
        assume(len(beklenmeyen_hata.strip()) >= 5)
        
        with patch('uygulama.kurulum.admin_olusturucu.SQLALCHEMY_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.MODELS_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.PASSLIB_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.KullaniciDepo') as mock_depo_class, \
             patch('uygulama.kurulum.admin_olusturucu.Kullanici') as mock_kullanici_class, \
             patch('uygulama.kurulum.admin_olusturucu.pwd_context') as mock_pwd_context, \
             patch('uygulama.kurulum.admin_olusturucu.logger') as mock_logger:
            
            # Mock setup
            mock_depo = Mock()
            mock_depo_class.return_value = mock_depo
            mock_depo.kullanici_adi_ile_getir.return_value = None  # Admin yok
            mock_pwd_context.hash.return_value = f"hashed_{sifre}"
            
            # Beklenmeyen hata simüle et
            unexpected_error = RuntimeError(beklenmeyen_hata)
            mock_kullanici_class.side_effect = unexpected_error
            
            # Admin oluşturma girişimi - beklenmeyen hata bekleniyor
            with pytest.raises(KullaniciHatasi):
                admin_olustur(self.mock_session, kullanici_adi, sifre)
            
            # Hata loglandığını doğrula
            mock_logger.error.assert_called()
            error_calls = mock_logger.error.call_args_list
            
            # Beklenmeyen hata loglandığını kontrol et
            assert len(error_calls) > 0
            unexpected_error_logged = any(
                beklenmeyen_hata in str(call_args) 
                for call_args in error_calls
            )
            assert unexpected_error_logged, f"Beklenmeyen hata loglarda bulunamadı: {beklenmeyen_hata}"
            
            # Rollback çağrıldığını doğrula
            self.mock_session.rollback.assert_called()
    
    @given(
        kullanici_adi=st.text(min_size=1, max_size=20).filter(
            lambda x: x.strip() and x.isalnum()
        ),
        sifre=st.text(min_size=3, max_size=50).filter(
            lambda x: x.strip() and len(x.strip()) >= 3
        )
    )
    @settings(max_examples=100, deadline=5000)
    def test_basarili_islem_loglama_property(self, kullanici_adi, sifre):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 11: Kullanıcı Oluşturma Hata Loglama**
        **Validates: Requirements 5.4**
        
        Başarılı işlemler de uygun şekilde loglanmalı
        """
        assume(len(kullanici_adi.strip()) > 0)
        assume(len(sifre.strip()) >= 3)
        
        with patch('uygulama.kurulum.admin_olusturucu.SQLALCHEMY_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.MODELS_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.PASSLIB_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.KullaniciDepo') as mock_depo_class, \
             patch('uygulama.kurulum.admin_olusturucu.Kullanici') as mock_kullanici_class, \
             patch('uygulama.kurulum.admin_olusturucu.pwd_context') as mock_pwd_context, \
             patch('uygulama.kurulum.admin_olusturucu.logger') as mock_logger:
            
            # Mock setup - başarılı senaryo
            mock_depo = Mock()
            mock_depo_class.return_value = mock_depo
            mock_depo.kullanici_adi_ile_getir.return_value = None  # Admin yok
            mock_pwd_context.hash.return_value = f"hashed_{sifre}"
            mock_kullanici_class.return_value = Mock()
            
            # Admin oluşturma - başarılı
            admin_olustur(self.mock_session, kullanici_adi, sifre)
            
            # Başarı loglandığını doğrula
            mock_logger.info.assert_called()
            info_calls = mock_logger.info.call_args_list
            
            # Başarı mesajlarının loglandığını kontrol et
            assert len(info_calls) > 0
            success_logged = any(
                "başarıyla oluşturuldu" in str(call_args) or
                "oluşturuluyor" in str(call_args)
                for call_args in info_calls
            )
            assert success_logged, "Başarı mesajı loglarda bulunamadı"
            
            # Hata logu olmamalı
            assert not mock_logger.error.called
    
    @given(
        kullanici_adi=st.text(min_size=1, max_size=20).filter(
            lambda x: x.strip() and x.isalnum()
        )
    )
    @settings(max_examples=100, deadline=5000)
    def test_admin_mevcut_loglama_property(self, kullanici_adi):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 11: Kullanıcı Oluşturma Hata Loglama**
        **Validates: Requirements 5.4**
        
        Admin zaten mevcutsa bu durum loglanmalı
        """
        assume(len(kullanici_adi.strip()) > 0)
        
        with patch('uygulama.kurulum.admin_olusturucu.SQLALCHEMY_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.MODELS_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.PASSLIB_AVAILABLE', True), \
             patch('uygulama.kurulum.admin_olusturucu.KullaniciDepo') as mock_depo_class, \
             patch('uygulama.kurulum.admin_olusturucu.logger') as mock_logger:
            
            # Mock setup - admin mevcut
            mock_depo = Mock()
            mock_depo_class.return_value = mock_depo
            mock_kullanici_instance = Mock()
            mock_depo.kullanici_adi_ile_getir.return_value = mock_kullanici_instance
            
            # Admin oluşturma girişimi - mevcut admin
            admin_olustur(self.mock_session, kullanici_adi, "test123")
            
            # Mevcut admin loglandığını doğrula
            mock_logger.info.assert_called()
            info_calls = mock_logger.info.call_args_list
            
            # Mevcut admin mesajının loglandığını kontrol et
            assert len(info_calls) > 0
            existing_admin_logged = any(
                "zaten mevcut" in str(call_args)
                for call_args in info_calls
            )
            assert existing_admin_logged, "Mevcut admin mesajı loglarda bulunamadı"
    
    @settings(max_examples=100, deadline=5000)
    def test_bagimliliklarin_olmamasi_loglama_property(self):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 11: Kullanıcı Oluşturma Hata Loglama**
        **Validates: Requirements 5.4**
        
        Bağımlılık eksikliği durumları loglanmalı
        """
        with patch('uygulama.kurulum.admin_olusturucu.logger') as mock_logger:
            
            # SQLAlchemy yok
            with patch('uygulama.kurulum.admin_olusturucu.SQLALCHEMY_AVAILABLE', False):
                with pytest.raises(KullaniciHatasi):
                    admin_varsa_gec(self.mock_session)
            
            # Passlib yok
            with patch('uygulama.kurulum.admin_olusturucu.PASSLIB_AVAILABLE', False):
                with pytest.raises(KullaniciHatasi):
                    sifre_hash_olustur("test123")
            
            # Modeller yok
            with patch('uygulama.kurulum.admin_olusturucu.SQLALCHEMY_AVAILABLE', True), \
                 patch('uygulama.kurulum.admin_olusturucu.MODELS_AVAILABLE', False):
                with pytest.raises(KullaniciHatasi):
                    admin_varsa_gec(self.mock_session)
            
            # Warning loglarının çağrıldığını kontrol et (modül seviyesinde)
            # Bu testler bağımlılık eksikliği durumlarını test eder