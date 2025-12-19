# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.kurulum.test_bootstrap_hata_property
# Description: Bootstrap hata yönetimi property testleri
# Changelog:
# - Bootstrap hata yönetimi property testleri eklendi

"""
Bootstrap Hata Yönetimi Property Testleri

**Özellik: kurulum-bootstrap-altyapisi, Özellik 12: Bootstrap Hata Yönetimi**
**Doğrular: Gereksinimler 6.2**

Bu modül, bootstrap sürecinde hata yönetiminin doğru çalıştığını
property-based testing ile doğrular.
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from sontechsp.uygulama.kurulum.baslat import ilk_calistirma_hazirla
from sontechsp.uygulama.kurulum import (
    KurulumHatasi,
    KlasorHatasi,
    AyarHatasi,
    DogrulamaHatasi,
    MigrationHatasi,
    KullaniciHatasi,
)


class TestBootstrapHataYonetimi:
    """Bootstrap hata yönetimi property testleri"""

    @given(
        klasor_hatasi_mesaji=st.text(min_size=1, max_size=100),
        proje_adi=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")), min_size=3, max_size=20),
    )
    @settings(max_examples=100)
    def test_klasor_hatasi_anlasilir_mesaj_property(self, klasor_hatasi_mesaji, proje_adi):
        """
        **Özellik: kurulum-bootstrap-altyapisi, Özellik 12: Bootstrap Hata Yönetimi**
        **Doğrular: Gereksinimler 6.2**

        Herhangi bir klasör hatası durumunda, sistem anlaşılır hata mesajı ile
        işlemi durdurmalı
        """
        # Geçici dizin oluştur
        with tempfile.TemporaryDirectory() as temp_dir:
            proje_koku = Path(temp_dir) / proje_adi

            # Klasör oluşturma işlemini mock'la ve hata fırlat
            with patch("uygulama.kurulum.baslat.klasorleri_olustur") as mock_klasor:
                mock_klasor.side_effect = KlasorHatasi(klasor_hatasi_mesaji)

                # Bootstrap işlemini çalıştır ve hata bekle
                with pytest.raises(KurulumHatasi) as exc_info:
                    ilk_calistirma_hazirla(proje_koku)

                # Hata mesajının anlaşılır olduğunu doğrula
                hata_mesaji = str(exc_info.value)
                assert "KlasorHatasi" in hata_mesaji
                assert klasor_hatasi_mesaji in hata_mesaji
                assert len(hata_mesaji) > 10  # Anlaşılır uzunlukta

    @given(
        ayar_hatasi_mesaji=st.text(min_size=1, max_size=100),
        proje_adi=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")), min_size=3, max_size=20),
    )
    @settings(max_examples=100)
    def test_ayar_hatasi_anlasilir_mesaj_property(self, ayar_hatasi_mesaji, proje_adi):
        """
        **Özellik: kurulum-bootstrap-altyapisi, Özellik 12: Bootstrap Hata Yönetimi**
        **Doğrular: Gereksinimler 6.2**

        Herhangi bir ayar hatası durumunda, sistem anlaşılır hata mesajı ile
        işlemi durdurmalı
        """
        # Geçici dizin oluştur
        with tempfile.TemporaryDirectory() as temp_dir:
            proje_koku = Path(temp_dir) / proje_adi

            # Ayar işlemlerini mock'la
            with (
                patch("uygulama.kurulum.baslat.klasorleri_olustur"),
                patch("uygulama.kurulum.baslat.klasor_var_mi", return_value=True),
                patch("uygulama.kurulum.baslat.ayar_dosyasi_olustur") as mock_ayar,
            ):

                mock_ayar.side_effect = AyarHatasi(ayar_hatasi_mesaji)

                # Bootstrap işlemini çalıştır ve hata bekle
                with pytest.raises(KurulumHatasi) as exc_info:
                    ilk_calistirma_hazirla(proje_koku)

                # Hata mesajının anlaşılır olduğunu doğrula
                hata_mesaji = str(exc_info.value)
                assert "AyarHatasi" in hata_mesaji
                assert ayar_hatasi_mesaji in hata_mesaji
                assert len(hata_mesaji) > 10  # Anlaşılır uzunlukta

    @given(
        veritabani_hatasi_mesaji=st.text(min_size=1, max_size=100),
        proje_adi=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")), min_size=3, max_size=20),
    )
    @settings(max_examples=100)
    def test_veritabani_hatasi_anlasilir_mesaj_property(self, veritabani_hatasi_mesaji, proje_adi):
        """
        **Özellik: kurulum-bootstrap-altyapisi, Özellik 12: Bootstrap Hata Yönetimi**
        **Doğrular: Gereksinimler 6.2**

        Herhangi bir veritabanı hatası durumunda, sistem anlaşılır hata mesajı ile
        işlemi durdurmalı
        """
        # Geçici dizin oluştur
        with tempfile.TemporaryDirectory() as temp_dir:
            proje_koku = Path(temp_dir) / proje_adi

            # Önceki adımları mock'la, veritabanı testinde hata fırlat
            with (
                patch("uygulama.kurulum.baslat.klasorleri_olustur"),
                patch("uygulama.kurulum.baslat.klasor_var_mi", return_value=True),
                patch("uygulama.kurulum.baslat.ayar_dosyasi_olustur"),
                patch("uygulama.kurulum.baslat.ayar_dosyasi_var_mi", return_value=True),
                patch("uygulama.kurulum.baslat.ayarlari_yukle") as mock_yukle,
                patch("uygulama.kurulum.baslat.baglanti_test_et") as mock_baglanti,
            ):

                # Ayarları mock'la
                mock_yukle.return_value = {"veritabani_url": "postgresql://test"}
                mock_baglanti.side_effect = DogrulamaHatasi(veritabani_hatasi_mesaji)

                # Bootstrap işlemini çalıştır ve hata bekle
                with pytest.raises(KurulumHatasi) as exc_info:
                    ilk_calistirma_hazirla(proje_koku)

                # Hata mesajının anlaşılır olduğunu doğrula
                hata_mesaji = str(exc_info.value)
                assert "DogrulamaHatasi" in hata_mesaji
                assert veritabani_hatasi_mesaji in hata_mesaji
                assert len(hata_mesaji) > 10  # Anlaşılır uzunlukta

    @given(
        migration_hatasi_mesaji=st.text(min_size=1, max_size=100),
        proje_adi=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")), min_size=3, max_size=20),
    )
    @settings(max_examples=100)
    def test_migration_hatasi_anlasilir_mesaj_property(self, migration_hatasi_mesaji, proje_adi):
        """
        **Özellik: kurulum-bootstrap-altyapisi, Özellik 12: Bootstrap Hata Yönetimi**
        **Doğrular: Gereksinimler 6.2**

        Herhangi bir migration hatası durumunda, sistem anlaşılır hata mesajı ile
        işlemi durdurmalı
        """
        # Geçici dizin oluştur
        with tempfile.TemporaryDirectory() as temp_dir:
            proje_koku = Path(temp_dir) / proje_adi

            # Önceki adımları mock'la, migration'da hata fırlat
            with (
                patch("uygulama.kurulum.baslat.klasorleri_olustur"),
                patch("uygulama.kurulum.baslat.klasor_var_mi", return_value=True),
                patch("uygulama.kurulum.baslat.ayar_dosyasi_olustur"),
                patch("uygulama.kurulum.baslat.ayar_dosyasi_var_mi", return_value=True),
                patch("uygulama.kurulum.baslat.ayarlari_yukle") as mock_yukle,
                patch("uygulama.kurulum.baslat.baglanti_test_et"),
                patch("uygulama.kurulum.baslat.gocleri_calistir") as mock_migration,
            ):

                # Ayarları mock'la
                mock_yukle.return_value = {"veritabani_url": "postgresql://test"}
                mock_migration.side_effect = MigrationHatasi(migration_hatasi_mesaji)

                # Bootstrap işlemini çalıştır ve hata bekle
                with pytest.raises(KurulumHatasi) as exc_info:
                    ilk_calistirma_hazirla(proje_koku)

                # Hata mesajının anlaşılır olduğunu doğrula
                hata_mesaji = str(exc_info.value)
                assert "MigrationHatasi" in hata_mesaji
                assert migration_hatasi_mesaji in hata_mesaji
                assert len(hata_mesaji) > 10  # Anlaşılır uzunlukta

    @given(
        kullanici_hatasi_mesaji=st.text(min_size=1, max_size=100),
        proje_adi=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")), min_size=3, max_size=20),
    )
    @settings(max_examples=100)
    def test_kullanici_hatasi_anlasilir_mesaj_property(self, kullanici_hatasi_mesaji, proje_adi):
        """
        **Özellik: kurulum-bootstrap-altyapisi, Özellik 12: Bootstrap Hata Yönetimi**
        **Doğrular: Gereksinimler 6.2**

        Herhangi bir kullanıcı oluşturma hatası durumunda, sistem anlaşılır hata mesajı ile
        işlemi durdurmalı
        """
        # Geçici dizin oluştur
        with tempfile.TemporaryDirectory() as temp_dir:
            proje_koku = Path(temp_dir) / proje_adi

            # Önceki adımları mock'la, admin oluşturmada hata fırlat
            with (
                patch("uygulama.kurulum.baslat.klasorleri_olustur"),
                patch("uygulama.kurulum.baslat.klasor_var_mi", return_value=True),
                patch("uygulama.kurulum.baslat.ayar_dosyasi_olustur"),
                patch("uygulama.kurulum.baslat.ayar_dosyasi_var_mi", return_value=True),
                patch("uygulama.kurulum.baslat.ayarlari_yukle") as mock_yukle,
                patch("uygulama.kurulum.baslat.baglanti_test_et"),
                patch("uygulama.kurulum.baslat.gocleri_calistir"),
                patch("uygulama.kurulum.baslat.admin_olustur") as mock_admin,
            ):

                # Ayarları mock'la
                mock_yukle.return_value = {"veritabani_url": "postgresql://test"}
                mock_admin.side_effect = KullaniciHatasi(kullanici_hatasi_mesaji)

                # Bootstrap işlemini çalıştır ve hata bekle
                with pytest.raises(KurulumHatasi) as exc_info:
                    ilk_calistirma_hazirla(proje_koku)

                # Hata mesajının anlaşılır olduğunu doğrula
                hata_mesaji = str(exc_info.value)
                assert "KullaniciHatasi" in hata_mesaji
                assert kullanici_hatasi_mesaji in hata_mesaji
                assert len(hata_mesaji) > 10  # Anlaşılır uzunlukta

    @given(
        beklenmeyen_hata_mesaji=st.text(min_size=1, max_size=100),
        proje_adi=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")), min_size=3, max_size=20),
    )
    @settings(max_examples=100)
    def test_beklenmeyen_hata_yonetimi_property(self, beklenmeyen_hata_mesaji, proje_adi):
        """
        **Özellik: kurulum-bootstrap-altyapisi, Özellik 12: Bootstrap Hata Yönetimi**
        **Doğrular: Gereksinimler 6.2**

        Herhangi bir beklenmeyen hata durumunda, sistem anlaşılır hata mesajı ile
        işlemi durdurmalı
        """
        # Geçici dizin oluştur
        with tempfile.TemporaryDirectory() as temp_dir:
            proje_koku = Path(temp_dir) / proje_adi

            # Beklenmeyen hata fırlat
            with patch("uygulama.kurulum.baslat.klasorleri_olustur") as mock_klasor:
                mock_klasor.side_effect = RuntimeError(beklenmeyen_hata_mesaji)

                # Bootstrap işlemini çalıştır ve hata bekle
                with pytest.raises(KurulumHatasi) as exc_info:
                    ilk_calistirma_hazirla(proje_koku)

                # Hata mesajının anlaşılır olduğunu doğrula
                hata_mesaji = str(exc_info.value)
                assert "Beklenmeyen kurulum hatası" in hata_mesaji or "KlasorHatasi" in hata_mesaji
                assert len(hata_mesaji) > 10  # Anlaşılır uzunlukta

    @given(proje_adi=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")), min_size=3, max_size=20))
    @settings(max_examples=50)
    def test_hata_durumunda_islem_durdurma_property(self, proje_adi):
        """
        **Özellik: kurulum-bootstrap-altyapisi, Özellik 12: Bootstrap Hata Yönetimi**
        **Doğrular: Gereksinimler 6.2**

        Herhangi bir adımda hata oluştuğunda, sistem işlemi durdurmalı ve
        sonraki adımları çalıştırmamalı
        """
        # Geçici dizin oluştur
        with tempfile.TemporaryDirectory() as temp_dir:
            proje_koku = Path(temp_dir) / proje_adi

            # İlk adımda hata fırlat, sonraki adımları mock'la
            with (
                patch("uygulama.kurulum.baslat.klasorleri_olustur") as mock_klasor,
                patch("uygulama.kurulum.baslat.ayar_dosyasi_olustur") as mock_ayar,
                patch("uygulama.kurulum.baslat.baglanti_test_et") as mock_baglanti,
                patch("uygulama.kurulum.baslat.gocleri_calistir") as mock_migration,
                patch("uygulama.kurulum.baslat.admin_olustur") as mock_admin,
            ):

                # İlk adımda hata fırlat
                mock_klasor.side_effect = KlasorHatasi("Test hatası")

                # Bootstrap işlemini çalıştır ve hata bekle
                with pytest.raises(KurulumHatasi):
                    ilk_calistirma_hazirla(proje_koku)

                # İlk adım çağrıldı
                assert mock_klasor.called

                # Sonraki adımlar çağrılmadı (işlem durdu)
                assert not mock_ayar.called
                assert not mock_baglanti.called
                assert not mock_migration.called
                assert not mock_admin.called

    @given(proje_adi=st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")), min_size=3, max_size=20))
    @settings(max_examples=20)
    def test_herhangi_adimda_hata_durdurma_property(self, proje_adi):
        """
        **Özellik: kurulum-bootstrap-altyapisi, Özellik 12: Bootstrap Hata Yönetimi**
        **Doğrular: Gereksinimler 6.2**

        Herhangi bir adımda hata oluştuğunda, sistem işlemi durdurmalı
        """
        # Geçici dizin oluştur
        with tempfile.TemporaryDirectory() as temp_dir:
            proje_koku = Path(temp_dir) / proje_adi

            # İlk adımda hata fırlat ve işlemin durduğunu test et
            with (
                patch("uygulama.kurulum.baslat.klasorleri_olustur") as mock_klasor,
                patch("uygulama.kurulum.baslat.ayar_dosyasi_olustur") as mock_ayar,
                patch("uygulama.kurulum.baslat.baglanti_test_et") as mock_baglanti,
            ):

                # İlk adımda hata fırlat
                mock_klasor.side_effect = KlasorHatasi("Test hatası")

                # Bootstrap işlemini çalıştır ve hata bekle
                with pytest.raises(KurulumHatasi):
                    ilk_calistirma_hazirla(proje_koku)

                # İlk adım çağrıldı
                assert mock_klasor.called

                # Sonraki adımlar çağrılmadı (işlem durdu)
                assert not mock_ayar.called
                assert not mock_baglanti.called
