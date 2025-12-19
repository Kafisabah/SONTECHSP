# Version: 0.1.0
# Last Update: 2025-12-16
# Module: test_pos_ui
# Description: POS UI katmanı birim testleri
# Changelog:
# - İlk oluşturma

"""
POS UI Katmanı Birim Testleri

Ekran yükleme, signal/slot bağlantıları ve service çağrı testleri.
Requirements: 1.1, 3.1, 4.1
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from sontechsp.uygulama.moduller.pos.ui.sepet_ekrani import SepetEkrani
from sontechsp.uygulama.moduller.pos.ui.odeme_ekrani import OdemeEkrani
from sontechsp.uygulama.moduller.pos.ui.iade_ekrani import IadeEkrani


@pytest.fixture(scope="session")
def qapp():
    """PyQt6 uygulama fixture'ı"""
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    yield app


@pytest.fixture
def mock_oturum():
    """Mock oturum fixture'ı"""
    oturum = Mock()
    oturum.terminal_id = 1
    oturum.kullanici_id = 1
    oturum.kullanici_adi = "Test Kasiyer"
    return oturum


@pytest.fixture
def mock_sepet_service():
    """Mock sepet service fixture'ı"""
    service = Mock()
    service.yeni_sepet_olustur.return_value = 1
    service.sepet_bilgisi_getir.return_value = {"id": 1, "toplam_tutar": Decimal("50.00"), "durum": "AKTIF"}
    service.barkod_ekle.return_value = True
    service.urun_adedi_degistir.return_value = True
    service.satir_sil.return_value = True
    service.sepet_bosalt.return_value = True
    service.indirim_uygula.return_value = True
    return service


@pytest.fixture
def mock_odeme_service():
    """Mock ödeme service fixture'ı"""
    service = Mock()
    service.odeme_tamamla.return_value = True
    return service


@pytest.fixture
def mock_iade_service():
    """Mock iade service fixture'ı"""
    service = Mock()
    service.satis_bilgisi_getir.return_value = {
        "id": 1,
        "satis_tarihi": "2025-12-16",
        "kasiyer_adi": "Test Kasiyer",
        "toplam_tutar": Decimal("100.00"),
        "durum": "TAMAMLANDI",
    }
    service.iade_olustur.return_value = True
    return service


class TestSepetEkrani:
    """Sepet ekranı testleri"""

    @patch("sontechsp.uygulama.moduller.pos.ui.sepet_ekrani.oturum_baglamini_al")
    @patch("sontechsp.uygulama.moduller.pos.ui.sepet_ekrani.sepet_service_al")
    def test_sepet_ekrani_yukleme(self, mock_service, mock_oturum_func, qapp, mock_oturum, mock_sepet_service):
        """Sepet ekranı yükleme testi"""
        # Mock'ları ayarla
        mock_oturum_func.return_value = mock_oturum
        mock_service.return_value = mock_sepet_service

        # Ekranı oluştur
        ekran = SepetEkrani()

        # Temel kontroller
        assert ekran is not None
        assert hasattr(ekran, "sepet_service")

        # Temizlik
        ekran.close()
