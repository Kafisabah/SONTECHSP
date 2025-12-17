# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.kurulum.test_migration_hata_property
# Description: Migration hata yönetimi property testleri
# Changelog:
# - Migration hata yönetimi property testleri oluşturuldu
# - Import düzenlemesi ve kod standardizasyonu yapıldı

"""
Migration hata yönetimi property testleri

**Özellik: kurulum-bootstrap-altyapisi, Özellik 8: Migration Hata Yönetimi**
"""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

from uygulama.kurulum.veritabani_kontrol import (
    gocleri_calistir,
    alembic_config_yolunu_bul,
    migration_durumunu_kontrol_et
)
from uygulama.kurulum.sabitler import ALEMBIC_CONFIG_DOSYASI
from uygulama.kurulum import MigrationHatasi


class TestMigrationHataYonetimi:
    """
    **Özellik: kurulum-bootstrap-altyapisi, Özellik 8: Migration Hata Yönetimi**
    **Doğrular: Gereksinimler 4.2**
    """

    def test_alembic_config_bulunamadi_hatasi(self, gecici_dizin):
        """Alembic config dosyası bulunamazsa MigrationHatasi fırlatılmalı"""
        # Geçici dizini mevcut dizin olarak ayarla ve alembic.ini'yi gizle
        original_cwd = os.getcwd()
        try:
            os.chdir(gecici_dizin)
            # Alembic mevcut olduğunda config bulunamadığında hata vermeli
            with pytest.raises(MigrationHatasi) as exc_info:
                alembic_config_yolunu_bul(gecici_dizin)
            
            hata_mesaji = str(exc_info.value)
            assert "config dosyası bulunamadı" in hata_mesaji.lower()
            assert isinstance(exc_info.value, MigrationHatasi)
        finally:
            os.chdir(original_cwd)

    def test_migration_calistirma_config_eksik_hatasi(self, gecici_dizin):
        """Migration çalıştırma sırasında config eksikse hata"""
        with pytest.raises(MigrationHatasi):
            gocleri_calistir(gecici_dizin)

    @patch('uygulama.kurulum.veritabani_kontrol.ALEMBIC_AVAILABLE', False)
    def test_alembic_eksik_migration_hatasi(self, gecici_dizin):
        """Alembic eksikse MigrationHatasi fırlatılmalı"""
        with pytest.raises(MigrationHatasi) as exc_info:
            gocleri_calistir(gecici_dizin)
        
        hata_mesaji = str(exc_info.value)
        assert "Alembic bulunamadı" in hata_mesaji

    @patch('uygulama.kurulum.veritabani_kontrol.ALEMBIC_AVAILABLE', False)
    def test_alembic_eksik_durum_kontrol_hatasi(self, gecici_dizin):
        """Alembic eksikse durum kontrolü hatası"""
        with pytest.raises(MigrationHatasi) as exc_info:
            migration_durumunu_kontrol_et(gecici_dizin)
        
        hata_mesaji = str(exc_info.value)
        assert "Alembic bulunamadı" in hata_mesaji

    def test_gecerli_config_dosyasi_bulma(self, gecici_dizin):
        """Geçerli config dosyası bulunduğunda hata olmamalı"""
        # Geçici config dosyası oluştur
        config_dosyasi = gecici_dizin / ALEMBIC_CONFIG_DOSYASI
        config_dosyasi.write_text("[alembic]\nscript_location = migrations")
        
        # Hata fırlatmamalı
        try:
            bulunan_yol = alembic_config_yolunu_bul(gecici_dizin)
            assert bulunan_yol == config_dosyasi
        except MigrationHatasi:
            pytest.fail("Geçerli config dosyası için hata fırlatılmamalı")

    @patch('uygulama.kurulum.veritabani_kontrol.command.upgrade')
    @patch('uygulama.kurulum.veritabani_kontrol.Config')
    def test_migration_upgrade_hatasi(self, mock_config, mock_upgrade, gecici_dizin):
        """Migration upgrade hatası için uygun hata yönetimi"""
        # Config dosyası oluştur
        config_dosyasi = gecici_dizin / ALEMBIC_CONFIG_DOSYASI
        config_dosyasi.write_text("[alembic]\nscript_location = migrations")
        
        # Migration dizini oluştur
        migration_dir = gecici_dizin / "migrations"
        if not migration_dir.exists():
            migration_dir.mkdir()
        
        # Mock config
        mock_alembic_cfg = MagicMock()
        mock_alembic_cfg.get_main_option.return_value = "migrations"
        mock_config.return_value = mock_alembic_cfg
        
        # Upgrade hatası simüle et
        mock_upgrade.side_effect = Exception("Migration upgrade hatası")
        
        with pytest.raises(MigrationHatasi) as exc_info:
            gocleri_calistir(gecici_dizin)
        
        hata_mesaji = str(exc_info.value)
        assert "migration hatası" in hata_mesaji.lower()

    @patch('uygulama.kurulum.veritabani_kontrol.command.upgrade')
    @patch('uygulama.kurulum.veritabani_kontrol.Config')
    def test_migration_dizini_eksik_hatasi(self, mock_config, mock_upgrade, gecici_dizin):
        """Migration dizini eksikse hata"""
        # Config dosyası oluştur
        config_dosyasi = gecici_dizin / ALEMBIC_CONFIG_DOSYASI
        config_dosyasi.write_text("[alembic]\nscript_location = migrations")
        
        # Mock config - migration dizini mevcut değil
        mock_alembic_cfg = MagicMock()
        mock_alembic_cfg.get_main_option.return_value = "migrations"
        mock_config.return_value = mock_alembic_cfg
        
        with pytest.raises(MigrationHatasi) as exc_info:
            gocleri_calistir(gecici_dizin)
        
        hata_mesaji = str(exc_info.value)
        assert "migration dizini bulunamadı" in hata_mesaji.lower()

    @patch('uygulama.kurulum.veritabani_kontrol.command.upgrade')
    @patch('uygulama.kurulum.veritabani_kontrol.Config')
    def test_basarili_migration_calistirma(self, mock_config, mock_upgrade, gecici_dizin):
        """Başarılı migration çalıştırma için hata olmamalı"""
        # Config dosyası oluştur
        config_dosyasi = gecici_dizin / ALEMBIC_CONFIG_DOSYASI
        config_dosyasi.write_text("[alembic]\nscript_location = migrations")
        
        # Migration dizini oluştur
        migration_dir = gecici_dizin / "migrations"
        if not migration_dir.exists():
            migration_dir.mkdir()
        
        # Mock config
        mock_alembic_cfg = MagicMock()
        mock_alembic_cfg.get_main_option.return_value = "migrations"
        mock_config.return_value = mock_alembic_cfg
        
        # Başarılı upgrade simüle et
        mock_upgrade.return_value = None
        
        # Hata fırlatmamalı
        try:
            gocleri_calistir(gecici_dizin)
        except MigrationHatasi:
            pytest.fail("Başarılı migration için hata fırlatılmamalı")

    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_rastgele_migration_hatalari(self, gecici_dizin, hata_mesaji):
        """Rastgele migration hataları için uygun hata yönetimi"""
        # Config dosyası oluştur
        config_dosyasi = gecici_dizin / ALEMBIC_CONFIG_DOSYASI
        config_dosyasi.write_text("[alembic]\nscript_location = migrations")
        
        # Migration dizini oluştur
        migration_dir = gecici_dizin / "migrations"
        if not migration_dir.exists():
            migration_dir.mkdir()
        
        with patch('uygulama.kurulum.veritabani_kontrol.Config') as mock_config:
            with patch('uygulama.kurulum.veritabani_kontrol.command.upgrade') as mock_upgrade:
                # Mock config
                mock_alembic_cfg = MagicMock()
                mock_alembic_cfg.get_main_option.return_value = "migrations"
                mock_config.return_value = mock_alembic_cfg
                
                # Rastgele hata simüle et
                mock_upgrade.side_effect = Exception(hata_mesaji)
                
                with pytest.raises(MigrationHatasi) as exc_info:
                    gocleri_calistir(gecici_dizin)
                
                # Hata mesajının MigrationHatasi olduğunu kontrol et
                assert isinstance(exc_info.value, MigrationHatasi)
                hata_str = str(exc_info.value)
                assert len(hata_str) > 0

    def test_ozel_migration_hata_mesajlari(self, gecici_dizin):
        """Özel migration hata mesajları için uygun yönetim"""
        # Config dosyası oluştur
        config_dosyasi = gecici_dizin / ALEMBIC_CONFIG_DOSYASI
        config_dosyasi.write_text("[alembic]\nscript_location = migrations")
        
        # Migration dizini oluştur
        migration_dir = gecici_dizin / "migrations"
        if not migration_dir.exists():
            migration_dir.mkdir()
        
        ozel_hatalar = [
            ("No such file or directory", "migration dosyaları bulunamadı"),
            ("Target database is not up to date", "veritabanı güncel değil"),
            ("Can't locate revision identified by", "migration revision bulunamadı")
        ]
        
        for hata_metni, beklenen_mesaj in ozel_hatalar:
            with patch('uygulama.kurulum.veritabani_kontrol.Config') as mock_config:
                with patch('uygulama.kurulum.veritabani_kontrol.command.upgrade') as mock_upgrade:
                    # Mock config
                    mock_alembic_cfg = MagicMock()
                    mock_alembic_cfg.get_main_option.return_value = "migrations"
                    mock_config.return_value = mock_alembic_cfg
                    
                    # Özel hata simüle et
                    mock_upgrade.side_effect = Exception(hata_metni)
                    
                    with pytest.raises(MigrationHatasi) as exc_info:
                        gocleri_calistir(gecici_dizin)
                    
                    hata_mesaji = str(exc_info.value)
                    assert beklenen_mesaj.lower() in hata_mesaji.lower()

    @patch('uygulama.kurulum.veritabani_kontrol.ScriptDirectory.from_config')
    @patch('uygulama.kurulum.veritabani_kontrol.Config')
    def test_migration_durum_kontrol_basarili(self, mock_config, mock_script_dir, gecici_dizin):
        """Başarılı migration durum kontrolü"""
        # Config dosyası oluştur
        config_dosyasi = gecici_dizin / ALEMBIC_CONFIG_DOSYASI
        config_dosyasi.write_text("[alembic]\nscript_location = migrations")
        
        # Mock config
        mock_alembic_cfg = MagicMock()
        mock_config.return_value = mock_alembic_cfg
        
        # Mock script directory
        mock_script = MagicMock()
        mock_script.dir = str(gecici_dizin / "migrations")
        mock_script.get_current_head.return_value = "abc123"
        mock_script_dir.return_value = mock_script
        
        # Hata fırlatmamalı
        try:
            durum = migration_durumunu_kontrol_et(gecici_dizin)
            assert durum["head_revision"] == "abc123"
            assert durum["migration_mevcut"] == True
        except MigrationHatasi:
            pytest.fail("Başarılı durum kontrolü için hata fırlatılmamalı")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])