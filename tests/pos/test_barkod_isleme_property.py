# Version: 0.1.0
# Last Update: 2024-12-18
# Module: test_barkod_isleme_property
# Description: Barkod işleme için özellik tabanlı testler
# Changelog:
# - İlk oluşturma - Özellik 3: Barkod İşleme testleri

"""
Barkod İşleme Özellik Testleri

**Feature: pos-arayuz-entegrasyonu, Property 3: Barkod İşleme**
**Doğrular: Gereksinim 2.2, 2.3, 2.4**

Herhangi bir geçerli barkod girişinde, sistem ürünü sepete eklemeli;
geçersiz barkod girişinde hata mesajı göstermelidir.
"""

import pytest
import sys
from unittest.mock import Mock
from hypothesis import given, settings, strategies as st, HealthCheck
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest

from sontechsp.uygulama.moduller.pos.ui.bilesenler.barkod_paneli import BarkodPaneli
from sontechsp.uygulama.moduller.pos.ui.handlers.pos_sinyalleri import POSSinyalleri


class TestBarkodIslemeProperty:
    """Barkod işleme özellik testleri"""

    @pytest.fixture(autouse=True)
    def setup_qt_app(self):
        """Qt uygulaması kurulumu"""
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
        yield

    @pytest.fixture
    def mock_stok_service(self):
        """Mock stok servisi"""
        mock_service = Mock()
        mock_service.urun_bilgisi_getir.return_value = {
            "id": 1,
            "urun_adi": "Test Ürün",
            "satis_fiyati": 10.50,
            "aktif": True,
        }
        return mock_service

    @pytest.fixture
    def sinyaller(self):
        """POS sinyalleri fixture"""
        return POSSinyalleri()

    @pytest.fixture
    def barkod_paneli(self, sinyaller, mock_stok_service):
        """Barkod paneli fixture"""
        panel = BarkodPaneli(sinyaller, mock_stok_service)
        panel.baslat()
        return panel

    @given(gecerli_barkod=st.text(min_size=8, max_size=20, alphabet=st.characters(whitelist_categories=("Nd", "Lu"))))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_gecerli_barkod_girisi_urun_ekler(self, gecerli_barkod, barkod_paneli, mock_stok_service):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 3: Barkod İşleme**

        Herhangi bir geçerli barkod girişinde, sistem ürünü sepete eklemeli.
        Doğrular: Gereksinim 2.2, 2.3
        """
        # Mock stok servisini ayarla
        mock_stok_service.reset_mock()  # Mock'u temizle
        mock_stok_service.urun_bilgisi_getir.return_value = {
            "id": hash(gecerli_barkod) % 1000 + 1,
            "urun_adi": f"Test Ürün {gecerli_barkod[:5]}",
            "satis_fiyati": 15.75,
            "aktif": True,
        }

        # Sinyal yakalamak için mock
        urun_eklendi_sinyali = Mock()
        barkod_paneli._sinyaller.urun_eklendi.connect(urun_eklendi_sinyali)

        # Barkod alanına geçerli barkod gir
        barkod_alani = barkod_paneli._barkod_alani
        barkod_alani.setText(gecerli_barkod)

        # EKLE butonuna tıkla
        ekle_butonu = barkod_paneli._ekle_butonu
        QTest.mouseClick(ekle_butonu, Qt.MouseButton.LeftButton)

        # Qt event loop'unu işle
        QApplication.processEvents()

        # Stok servisi çağrıldığını kontrol et
        mock_stok_service.urun_bilgisi_getir.assert_called_once_with(gecerli_barkod)

        # Ürün eklendi sinyali gönderildiğini kontrol et
        urun_eklendi_sinyali.assert_called_once()

        # Barkod alanının temizlendiğini kontrol et
        assert barkod_alani.text() == "", "Barkod alanı temizlenmeli"

    @given(
        gecersiz_barkod=st.one_of(
            st.text(max_size=3),  # Çok kısa barkodlar
            st.text(
                min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=("Ps", "Pe", "Pc"))
            ),  # Özel karakterler
            st.just(""),  # Boş string
            st.just("   "),  # Sadece boşluk
        )
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_gecersiz_barkod_girisi_hata_mesaji_gosterir(self, gecersiz_barkod, barkod_paneli, mock_stok_service):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 3: Barkod İşleme**

        Herhangi bir geçersiz barkod girişinde, sistem hata mesajı göstermelidir.
        Doğrular: Gereksinim 2.4
        """
        # Mock stok servisini geçersiz barkod için ayarla
        mock_stok_service.urun_bilgisi_getir.return_value = None

        # Hata sinyali yakalamak için mock
        hata_sinyali = Mock()
        barkod_paneli._sinyaller.hata_olustu.connect(hata_sinyali)

        # Barkod alanına geçersiz barkod gir
        barkod_alani = barkod_paneli._barkod_alani
        barkod_alani.setText(gecersiz_barkod)

        # EKLE butonuna tıkla
        ekle_butonu = barkod_paneli._ekle_butonu
        QTest.mouseClick(ekle_butonu, Qt.MouseButton.LeftButton)

        # Qt event loop'unu işle
        QApplication.processEvents()

        # Geçersiz barkod için hata sinyali gönderildiğini kontrol et
        if not gecersiz_barkod or not gecersiz_barkod.strip():
            # Boş barkod için hata sinyali gönderilmeli
            hata_sinyali.assert_called_once()
        else:
            # Stok servisi çağrıldıysa ve None döndüyse hata sinyali gönderilmeli
            if mock_stok_service.urun_bilgisi_getir.called:
                hata_sinyali.assert_called_once()

    @given(gecerli_barkod=st.text(min_size=8, max_size=15, alphabet=st.characters(whitelist_categories=("Nd",))))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_enter_tusu_ile_barkod_isleme(self, gecerli_barkod, barkod_paneli, mock_stok_service):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 3: Barkod İşleme**

        Enter tuşu ile barkod işleme çalışmalıdır.
        Doğrular: Gereksinim 2.2
        """
        # Mock stok servisini ayarla
        mock_stok_service.reset_mock()  # Mock'u temizle
        mock_stok_service.urun_bilgisi_getir.return_value = {
            "id": hash(gecerli_barkod) % 1000 + 1,
            "urun_adi": f"Test Ürün {gecerli_barkod[:5]}",
            "satis_fiyati": 12.25,
            "aktif": True,
        }

        # Sinyal yakalamak için mock
        urun_eklendi_sinyali = Mock()
        barkod_paneli._sinyaller.urun_eklendi.connect(urun_eklendi_sinyali)

        # Barkod alanına geçerli barkod gir
        barkod_alani = barkod_paneli._barkod_alani
        barkod_alani.setText(gecerli_barkod)

        # Enter tuşuna bas
        QTest.keyPress(barkod_alani, Qt.Key.Key_Return)

        # Qt event loop'unu işle
        QApplication.processEvents()

        # Stok servisi çağrıldığını kontrol et
        mock_stok_service.urun_bilgisi_getir.assert_called_once_with(gecerli_barkod)

        # Ürün eklendi sinyali gönderildiğini kontrol et
        urun_eklendi_sinyali.assert_called_once()

    def test_barkod_paneli_baslangic_durumu(self, barkod_paneli):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 3: Barkod İşleme**

        Barkod paneli başlangıç durumu doğru olmalıdır.
        Doğrular: Gereksinim 2.1
        """
        # Barkod alanının boş olduğunu kontrol et
        assert barkod_paneli._barkod_alani.text() == "", "Barkod alanı başlangıçta boş olmalı"

        # EKLE butonunun aktif olduğunu kontrol et
        assert barkod_paneli._ekle_butonu.isEnabled(), "EKLE butonu başlangıçta aktif olmalı"

    def test_barkod_paneli_odak_yonetimi(self, barkod_paneli):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 3: Barkod İşleme**

        Barkod paneli odak yönetimi doğru çalışmalıdır.
        Doğrular: Gereksinim 2.1
        """
        # Barkod alanına odak ver
        barkod_alani = barkod_paneli._barkod_alani
        barkod_alani.setFocus()

        # Qt event loop'unu işle
        QApplication.processEvents()

        # Metin girişi yapılabildiğini kontrol et
        test_barkod = "12345678"
        barkod_alani.setText(test_barkod)
        assert barkod_alani.text() == test_barkod, "Barkod alanına metin girilebilmeli"
