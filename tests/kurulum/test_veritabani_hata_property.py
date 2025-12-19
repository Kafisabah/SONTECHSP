# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.kurulum.test_veritabani_hata_property
# Description: Veritabanı bağlantı hata yönetimi property testleri
# Changelog:
# - Veritabanı bağlantı hata yönetimi property testleri oluşturuldu

"""
Veritabanı bağlantı hata yönetimi property testleri

**Özellik: kurulum-bootstrap-altyapisi, Özellik 7: Veritabanı Bağlantı Hata Yönetimi**
"""

import pytest
from unittest.mock import patch, MagicMock
from hypothesis import given, strategies as st, settings, HealthCheck

from sontechsp.uygulama.kurulum.veritabani_kontrol import (
    baglanti_test_et,
    veritabani_baglantisini_dogrula,
    alembic_config_yolunu_bul,
    migration_durumunu_kontrol_et,
)
from sontechsp.uygulama.kurulum import DogrulamaHatasi, MigrationHatasi


class TestVeritabaniBaglantiHataYonetimi:
    """
    **Özellik: kurulum-bootstrap-altyapisi, Özellik 7: Veritabanı Bağlantı Hata Yönetimi**
    **Doğrular: Gereksinimler 3.2**
    """

    def test_gecersiz_url_dogrulama_hatasi(self):
        """Geçersiz veritabanı URL'i için DogrulamaHatasi fırlatılmalı"""
        gecersiz_urller = [
            "",
            None,
            "gecersiz_url",
            "mysql://user:pass@localhost/db",  # MySQL desteklenmiyor
            "sqlite:///test.db",  # SQLite desteklenmiyor
            "http://example.com",  # HTTP URL
            "postgresql://",  # Eksik bilgiler
            "postgres",  # Çok kısa
            123,  # Sayı
            [],  # Liste
        ]

        for gecersiz_url in gecersiz_urller:
            with pytest.raises(DogrulamaHatasi) as exc_info:
                baglanti_test_et(gecersiz_url)

            # Hata mesajının anlaşılır olduğunu kontrol et
            hata_mesaji = str(exc_info.value)
            assert len(hata_mesaji) > 0
            assert isinstance(exc_info.value, DogrulamaHatasi)

    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_rastgele_gecersiz_url_hata_yonetimi(self, gecersiz_url):
        """Rastgele geçersiz URL'ler için uygun hata yönetimi"""
        # PostgreSQL formatında olmayan URL'ler için hata beklenir
        if not gecersiz_url.startswith(("postgresql://", "postgres://")):
            with pytest.raises(DogrulamaHatasi) as exc_info:
                baglanti_test_et(gecersiz_url)

            assert isinstance(exc_info.value, DogrulamaHatasi)
            hata_mesaji = str(exc_info.value)
            assert len(hata_mesaji) > 0

    @patch("uygulama.kurulum.veritabani_kontrol.SQLALCHEMY_AVAILABLE", False)
    def test_sqlalchemy_eksik_hatasi(self):
        """SQLAlchemy eksikse DogrulamaHatasi fırlatılmalı"""
        with pytest.raises(DogrulamaHatasi) as exc_info:
            baglanti_test_et("postgresql://test:test@localhost:5432/test")

        hata_mesaji = str(exc_info.value)
        assert "SQLAlchemy bulunamadı" in hata_mesaji

    @patch("uygulama.kurulum.veritabani_kontrol.create_engine")
    def test_sqlalchemy_baglanti_hatasi(self, mock_create_engine):
        """SQLAlchemy bağlantı hatası için uygun hata mesajı"""
        from sqlalchemy.exc import OperationalError

        # Bağlantı hatası simüle et
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_engine.connect.side_effect = OperationalError("could not connect to server", None, None)

        with pytest.raises(DogrulamaHatasi) as exc_info:
            baglanti_test_et("postgresql://test:test@localhost:5432/test")

        hata_mesaji = str(exc_info.value)
        assert "bağlanılamadı" in hata_mesaji.lower()

    @patch("uygulama.kurulum.veritabani_kontrol.create_engine")
    def test_kimlik_dogrulama_hatasi(self, mock_create_engine):
        """Kimlik doğrulama hatası için uygun hata mesajı"""
        from sqlalchemy.exc import OperationalError

        # Kimlik doğrulama hatası simüle et
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_engine.connect.side_effect = OperationalError("authentication failed for user", None, None)

        with pytest.raises(DogrulamaHatasi) as exc_info:
            baglanti_test_et("postgresql://test:test@localhost:5432/test")

        hata_mesaji = str(exc_info.value)
        assert "kimlik doğrulama" in hata_mesaji.lower()

    @patch("uygulama.kurulum.veritabani_kontrol.create_engine")
    def test_veritabani_mevcut_degil_hatasi(self, mock_create_engine):
        """Veritabanı mevcut değil hatası için uygun hata mesajı"""
        from sqlalchemy.exc import OperationalError

        # Veritabanı mevcut değil hatası simüle et
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_engine.connect.side_effect = OperationalError('database "test_db" does not exist', None, None)

        with pytest.raises(DogrulamaHatasi) as exc_info:
            baglanti_test_et("postgresql://test:test@localhost:5432/test_db")

        hata_mesaji = str(exc_info.value)
        assert "veritabanı mevcut değil" in hata_mesaji.lower()

    @patch("uygulama.kurulum.veritabani_kontrol.create_engine")
    def test_genel_sqlalchemy_hatasi(self, mock_create_engine):
        """Genel SQLAlchemy hatası için uygun hata mesajı"""
        from sqlalchemy.exc import SQLAlchemyError

        # Genel SQLAlchemy hatası simüle et
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_engine.connect.side_effect = SQLAlchemyError("Genel veritabanı hatası")

        with pytest.raises(DogrulamaHatasi) as exc_info:
            baglanti_test_et("postgresql://test:test@localhost:5432/test")

        hata_mesaji = str(exc_info.value)
        assert "veritabanı bağlantı hatası" in hata_mesaji.lower()

    def test_veritabani_dogrulama_fonksiyonu(self):
        """Veritabanı doğrulama fonksiyonu hata fırlatmamalı"""
        # Geçersiz URL'ler için False döndürmeli
        gecersiz_urller = ["", "gecersiz_url", "mysql://user:pass@localhost/db", None]

        for gecersiz_url in gecersiz_urller:
            result = veritabani_baglantisini_dogrula(gecersiz_url)
            assert result == False

    @patch("uygulama.kurulum.veritabani_kontrol.create_engine")
    def test_basarili_baglanti_testi(self, mock_create_engine):
        """Başarılı bağlantı testi için hata olmamalı"""
        # Başarılı bağlantı simüle et
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection

        mock_result = MagicMock()
        mock_result.scalar.return_value = 1
        mock_connection.execute.return_value = mock_result

        # Hata fırlatmamalı
        try:
            baglanti_test_et("postgresql://test:test@localhost:5432/test")
        except DogrulamaHatasi:
            pytest.fail("Başarılı bağlantı için hata fırlatılmamalı")

    @patch("uygulama.kurulum.veritabani_kontrol.create_engine")
    def test_beklenmeyen_hata_yonetimi(self, mock_create_engine):
        """Beklenmeyen hatalar için uygun hata yönetimi"""
        # Beklenmeyen hata simüle et
        mock_create_engine.side_effect = RuntimeError("Beklenmeyen hata")

        with pytest.raises(DogrulamaHatasi) as exc_info:
            baglanti_test_et("postgresql://test:test@localhost:5432/test")

        hata_mesaji = str(exc_info.value)
        assert "beklenmeyen" in hata_mesaji.lower()


class TestMigrationHataYonetimi:
    """Migration hata yönetimi testleri"""

    def test_alembic_config_bulunamadi_hatasi(self, gecici_dizin):
        """Alembic config dosyası bulunamazsa MigrationHatasi fırlatılmalı"""
        # Alembic mevcut olduğunda config bulunamadığında hata vermeli
        with pytest.raises(MigrationHatasi) as exc_info:
            alembic_config_yolunu_bul(gecici_dizin)

        hata_mesaji = str(exc_info.value)
        assert "config dosyası bulunamadı" in hata_mesaji.lower()

    @patch("uygulama.kurulum.veritabani_kontrol.ALEMBIC_AVAILABLE", False)
    def test_alembic_eksik_hatasi(self, gecici_dizin):
        """Alembic eksikse MigrationHatasi fırlatılmalı"""
        from sontechsp.uygulama.kurulum.veritabani_kontrol import gocleri_calistir

        with pytest.raises(MigrationHatasi) as exc_info:
            gocleri_calistir(gecici_dizin)

        hata_mesaji = str(exc_info.value)
        assert "Alembic bulunamadı" in hata_mesaji

    def test_migration_durum_kontrol_hatasi(self, gecici_dizin):
        """Migration durum kontrolü hatası"""
        with pytest.raises(MigrationHatasi):
            migration_durumunu_kontrol_et(gecici_dizin)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
