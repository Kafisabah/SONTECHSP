# Version: 0.1.0
# Last Update: 2024-12-18
# Module: test_hizli_urun_basit
# Description: Hızlı ürün paneli basit testleri
# Changelog:
# - İlk oluşturma - Basit hızlı ürün paneli testleri

"""
Hızlı Ürün Paneli Basit Testleri

Temel fonksiyonalite testleri
"""

import pytest
from PyQt6.QtWidgets import QApplication
import sys

from sontechsp.uygulama.moduller.pos.ui.bilesenler.hizli_urun_paneli import HizliUrunPaneli
from sontechsp.uygulama.moduller.pos.ui.handlers.pos_sinyalleri import POSSinyalleri


class TestHizliUrunBasit:
    """Hızlı ürün paneli basit testleri"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Test kurulumu"""
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()

        self.sinyaller = POSSinyalleri()
        self.panel = HizliUrunPaneli(self.sinyaller)
        yield

        # Temizlik
        self.panel.close()
        self.panel.deleteLater()

    def test_panel_olusturma(self):
        """Panel oluşturma testi"""
        assert self.panel is not None
        assert len(self.panel._butonlar) == 12  # Varsayılan buton sayısı

    def test_buton_sayisi_degistirme(self):
        """Buton sayısı değiştirme testi"""
        # 16 buton seç
        self.panel.buton_sayisi_combo.setCurrentText("16")
        self.app.processEvents()

        assert len(self.panel._butonlar) == 16

        # 24 buton seç
        self.panel.buton_sayisi_combo.setCurrentText("24")
        self.app.processEvents()

        assert len(self.panel._butonlar) == 24

    def test_bos_butonlar_tanimsiz_etiketi(self):
        """Boş butonların 'Tanımsız' etiketi göstermesi testi"""
        for buton in self.panel._butonlar:
            if not buton.property("productData"):
                assert buton.text() == "Tanımsız"

    def test_kategori_combo_varsayilan(self):
        """Kategori combo varsayılan durumu testi"""
        # En az "Tümü" seçeneği olmalı
        assert self.panel.kategori_combo.count() >= 1
        assert self.panel.kategori_combo.itemText(0) == "Tümü"
