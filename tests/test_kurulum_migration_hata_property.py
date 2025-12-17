# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.test_kurulum_migration_hata_property
# Description: Kurulum bootstrap migration hata yönetimi property testleri
# Changelog:
# - İlk oluşturma

"""
Kurulum Bootstrap Migration Hata Yönetimi Property Testleri

Bu modül kurulum sırasında migration hata yönetimi için property-based testleri içerir.
Hypothesis kütüphanesi kullanılarak yazılmıştır.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck

from uygulama.kurulum.veritabani_kontrol import (
    gocleri_calistir, 
    alembic_config_yolunu_bul,
    migration_durumunu_kontrol_et
)
from uygulama.kurulum import MigrationHatasi


class TestMigrationHataYonetimi:
    """Migration hata yönetimi property testleri"""
    
    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=5, deadline=None)
    def test_migration_hata_yonetimi_property(self, hata_mesaji):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 8: Migration Hata Yönetimi**
        
        For any migration error, system should throw exception with error details
        **Validates: Requirements 4.2**
        """
        assume(len(hata_mesaji.strip()) > 0)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Alembic config dosyası olmayan bir dizin oluştur
            proje_koku = Path(temp_dir) / "test_proje"
            proje_koku.mkdir()
            
            # Migration çalıştırmayı dene - hata bekleniyor
            with pytest.raises(MigrationHatasi) as exc_info:
                gocleri_calistir(proje_koku)
            
            # Hata mesajı anlaşılır olmalı
            hata_mesaji_str = str(exc_info.value)
            assert len(hata_mesaji_str) > 0, "Hata mesajı boş olmamalı"
            
            # Migration hatası ile ilgili anahtar kelimeler
            migration_kelimeleri = [
                "config", "alembic", "migration", "bulunamadı", 
                "dosya", "hata", "hatası"
            ]
            
            mesaj_lower = hata_mesaji_str.lower()
            assert any(kelime in mesaj_lower for kelime in migration_kelimeleri), \
                f"Hata mesajı migration ile ilgili olmalı: {hata_mesaji_str}"
    
    def test_config_dosyasi_bulunamama_hatasi(self):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 8: Migration Hata Yönetimi**
        
        For any missing config file, system should throw MigrationHatasi
        **Validates: Requirements 4.2**
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Geçersiz proje kök dizini - mevcut dizinden farklı
            proje_koku = Path(temp_dir) / "isolated_test_dir"
            proje_koku.mkdir()
            
            # Mevcut çalışma dizinini değiştir
            import os
            original_cwd = os.getcwd()
            try:
                os.chdir(str(proje_koku))
                
                # Config dosyası arama - hata bekleniyor
                with pytest.raises(MigrationHatasi) as exc_info:
                    alembic_config_yolunu_bul(proje_koku)
                
                # Hata mesajı config dosyası ile ilgili olmalı
                hata_mesaji = str(exc_info.value)
                assert "config" in hata_mesaji.lower() or "bulunamadı" in hata_mesaji.lower(), \
                    "Hata mesajı config dosyası bulunamama ile ilgili olmalı"
            finally:
                os.chdir(original_cwd)
    
    @patch('uygulama.kurulum.veritabani_kontrol.command')
    def test_alembic_command_hatasi_yonetimi(self, mock_command):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 8: Migration Hata Yönetimi**
        
        For any Alembic command error, system should throw MigrationHatasi with details
        **Validates: Requirements 4.2**
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Alembic config dosyası oluştur
            proje_koku = Path(temp_dir)
            config_dosyasi = proje_koku / "alembic.ini"
            config_dosyasi.write_text("""
[alembic]
script_location = migrations
sqlalchemy.url = sqlite:///test.db
""")
            
            # Migrations dizini oluştur
            migrations_dir = proje_koku / "migrations"
            migrations_dir.mkdir()
            
            # Alembic command'ın hata fırlatmasını sağla
            mock_command.upgrade.side_effect = Exception("Test migration hatası")
            
            # Migration çalıştırmayı dene - hata bekleniyor
            with pytest.raises(MigrationHatasi) as exc_info:
                gocleri_calistir(proje_koku)
            
            # Hata mesajı detayları içermeli
            hata_mesaji = str(exc_info.value)
            assert "migration" in hata_mesaji.lower() or "hatası" in hata_mesaji.lower(), \
                "Hata mesajı migration hatası ile ilgili olmalı"
    
    @given(st.text(min_size=1, max_size=20))
    @settings(max_examples=5, deadline=None)
    def test_migration_durum_kontrol_hatasi(self, hata_tipi):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 8: Migration Hata Yönetimi**
        
        For any migration status check error, system should handle gracefully
        **Validates: Requirements 4.2**
        """
        assume(len(hata_tipi.strip()) > 0)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Geçersiz proje kök dizini
            proje_koku = Path(temp_dir) / "nonexistent"
            
            # Migration durum kontrolü - hata bekleniyor
            with pytest.raises(MigrationHatasi) as exc_info:
                migration_durumunu_kontrol_et(proje_koku)
            
            # Hata mesajı anlaşılır olmalı
            hata_mesaji = str(exc_info.value)
            assert len(hata_mesaji) > 0, "Hata mesajı boş olmamalı"
    
    def test_migration_hata_mesaji_tutarliligi(self):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 8: Migration Hata Yönetimi**
        
        For any repeated migration error, error message should be consistent
        **Validates: Requirements 4.2**
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Geçersiz proje kök dizini
            proje_koku = Path(temp_dir) / "test_tutarlilik"
            proje_koku.mkdir()
            
            # Aynı hatayı birden fazla kez oluştur
            hata_mesajlari = []
            for i in range(3):
                try:
                    gocleri_calistir(proje_koku)
                except MigrationHatasi as e:
                    hata_mesajlari.append(str(e))
            
            # Tüm hata mesajları aynı olmalı
            assert len(set(hata_mesajlari)) == 1, \
                "Aynı hata durumu için mesajlar tutarlı olmalı"
    
    @patch('uygulama.kurulum.veritabani_kontrol.ALEMBIC_AVAILABLE', False)
    def test_alembic_bulunmama_hatasi(self):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 8: Migration Hata Yönetimi**
        
        For missing Alembic library, system should throw appropriate error
        **Validates: Requirements 4.2**
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            proje_koku = Path(temp_dir)
            
            # Alembic bulunamadığında hata bekleniyor
            with pytest.raises(MigrationHatasi) as exc_info:
                gocleri_calistir(proje_koku)
            
            # Hata mesajı Alembic eksikliği ile ilgili olmalı
            hata_mesaji = str(exc_info.value)
            assert "alembic" in hata_mesaji.lower(), \
                "Hata mesajı Alembic eksikliği ile ilgili olmalı"


class TestMigrationHataDetaylari:
    """Migration hata detayları property testleri"""
    
    @given(st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=3))
    @settings(max_examples=5, deadline=None)
    def test_hata_detay_icerik_kontrolu(self, hata_detaylari):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 8: Migration Hata Yönetimi**
        
        For any migration error, error details should contain useful information
        **Validates: Requirements 4.2**
        """
        # Her hata detayının geçerli olduğunu varsay
        for detay in hata_detaylari:
            assume(len(detay.strip()) > 0)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Geçersiz proje kök dizini
            proje_koku = Path(temp_dir) / "hata_detay_test"
            
            # Migration hatası oluştur
            try:
                gocleri_calistir(proje_koku)
            except MigrationHatasi as e:
                hata_mesaji = str(e)
                
                # Hata mesajı bilgilendirici olmalı
                assert len(hata_mesaji) >= 10, "Hata mesajı yeterince detaylı olmalı"
                
                # Türkçe karakter kontrolü (isteğe bağlı)
                # Hata mesajında en az bir anlamlı kelime olmalı
                anlamli_kelimeler = [
                    'config', 'dosya', 'bulunamadı', 'hata', 'migration', 
                    'alembic', 'dizin', 'yol', 'klasör'
                ]
                
                mesaj_lower = hata_mesaji.lower()
                assert any(kelime in mesaj_lower for kelime in anlamli_kelimeler), \
                    "Hata mesajı anlamlı kelimeler içermeli"
    
    def test_hata_tipi_kontrolu(self):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 8: Migration Hata Yönetimi**
        
        For any migration error, correct exception type should be raised
        **Validates: Requirements 4.2**
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            proje_koku = Path(temp_dir) / "hata_tipi_test"
            proje_koku.mkdir()
            
            # Migration hatası oluştur
            with pytest.raises(Exception) as exc_info:
                gocleri_calistir(proje_koku)
            
            # Doğru hata tipi fırlatılmalı
            assert isinstance(exc_info.value, MigrationHatasi), \
                "Migration hataları MigrationHatasi tipinde olmalı"
    
    @patch('uygulama.kurulum.veritabani_kontrol.logger')
    def test_hata_loglama_kontrolu(self, mock_logger):
        """
        **Feature: kurulum-bootstrap-altyapisi, Property 8: Migration Hata Yönetimi**
        
        For any migration error, error should be logged appropriately
        **Validates: Requirements 4.2**
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            proje_koku = Path(temp_dir) / "log_test"
            proje_koku.mkdir()
            
            # Migration hatası oluştur
            try:
                gocleri_calistir(proje_koku)
            except MigrationHatasi:
                pass  # Hata bekleniyor
            
            # Logger çağrıldığını kontrol et (info veya error seviyesinde)
            assert mock_logger.info.called or mock_logger.error.called or mock_logger.warning.called, \
                "Migration işlemi sırasında loglama yapılmalı"