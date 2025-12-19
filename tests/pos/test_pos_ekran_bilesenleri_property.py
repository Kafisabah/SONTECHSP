# Version: 0.1.0
# Last Update: 2024-12-19
# Module: test_pos_ekran_bilesenleri_property
# Description: POS ekran bileşenleri için özellik tabanlı testler
# Changelog:
# - İlk oluşturma - Özellik 2: POS Ekran Bileşenleri testleri

"""
POS Ekran Bileşenleri Özellik Testleri

**Feature: pos-arayuz-entegrasyonu, Property 2: POS Ekran Bileşenleri**
**Doğrular: Gereksinim 2.1, 3.2, 4.1, 4.2, 5.1, 6.1**

Herhangi bir POS ekranı açılışında, sistem barkod alanı, sepet tablosu,
ödeme paneli, hızlı ürün paneli ve işlem kısayolları panelini göstermelidir.
"""

import pytest
import sys
from hypothesis import given, settings, strategies as st
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QFrame, QLabel, QWidget

from sontechsp.uygulama.moduller.pos.ui.pos_ana_ekran import POSAnaEkran


class TestPOSEkranBilesenleriProperty:
    """POS ekran bileşenleri özellik testleri"""

    @pytest.fixture(autouse=True)
    def setup_qt_app(self):
        """Qt uygulaması kurulumu"""
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
        yield
        # Cleanup gerekirse burada yapılır

    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=100, deadline=None)
    def test_pos_ekrani_acilisinda_temel_bilesenler_mevcut(self, test_iterasyon):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 2: POS Ekran Bileşenleri**

        Herhangi bir POS ekranı açılışında, sistem temel bileşenleri göstermelidir.
        Doğrular: Gereksinim 2.1, 3.2, 4.1, 4.2, 5.1, 6.1
        """
        # POS ana ekranı oluştur
        pos_ekrani = POSAnaEkran()

        # Temel bileşen container'larının varlığını kontrol et
        assert hasattr(pos_ekrani, "_bilesenler"), "POS ekranı bileşen referanslarına sahip olmalı"

        # Gerekli container'ların varlığını kontrol et
        gerekli_containerlar = [
            "barkod_container",
            "sepet_container",
            "odeme_container",
            "hizli_urun_container",
            "islem_container",
        ]

        for container_adi in gerekli_containerlar:
            assert container_adi in pos_ekrani._bilesenler, f"{container_adi} container'ı mevcut olmalı"
            container = pos_ekrani._bilesenler[container_adi]
            assert isinstance(container, QFrame), f"{container_adi} QFrame tipinde olmalı"
            # Container'lar oluşturulduğunda görünür olmalı (parent widget gösterilmese bile)
            # isVisible() parent'a bağlı olduğu için burada sadece varlığını kontrol edelim

    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=100, deadline=None)
    def test_barkod_container_yapisi(self, test_iterasyon):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 2: POS Ekran Bileşenleri**

        Barkod container'ı uygun yapıda olmalıdır.
        Doğrular: Gereksinim 2.1
        """
        pos_ekrani = POSAnaEkran()
        barkod_container = pos_ekrani._bilesenler["barkod_container"]

        # Container'ın layout'u olmalı
        assert barkod_container.layout() is not None, "Barkod container'ının layout'u olmalı"

        # Container'da başlık olmalı
        layout = barkod_container.layout()
        assert layout.count() >= 1, "Barkod container'ında en az başlık olmalı"

        # İlk widget başlık olmalı
        baslik_widget = layout.itemAt(0).widget()
        assert isinstance(baslik_widget, QLabel), "İlk widget başlık (QLabel) olmalı"
        assert "Barkod" in baslik_widget.text(), "Başlık 'Barkod' içermeli"

    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=100, deadline=None)
    def test_sepet_container_yapisi(self, test_iterasyon):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 2: POS Ekran Bileşenleri**

        Sepet container'ı uygun yapıda olmalıdır.
        Doğrular: Gereksinim 3.2
        """
        pos_ekrani = POSAnaEkran()
        sepet_container = pos_ekrani._bilesenler["sepet_container"]

        # Container'ın layout'u olmalı
        assert sepet_container.layout() is not None, "Sepet container'ının layout'u olmalı"

        # Container'da başlık olmalı
        layout = sepet_container.layout()
        assert layout.count() >= 1, "Sepet container'ında en az başlık olmalı"

        # İlk widget başlık olmalı
        baslik_widget = layout.itemAt(0).widget()
        assert isinstance(baslik_widget, QLabel), "İlk widget başlık (QLabel) olmalı"
        assert "Sepet" in baslik_widget.text(), "Başlık 'Sepet' içermeli"

    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=100, deadline=None)
    def test_odeme_container_yapisi(self, test_iterasyon):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 2: POS Ekran Bileşenleri**

        Ödeme container'ı uygun yapıda olmalıdır.
        Doğrular: Gereksinim 4.1, 4.2
        """
        pos_ekrani = POSAnaEkran()
        odeme_container = pos_ekrani._bilesenler["odeme_container"]

        # Container'ın layout'u olmalı
        assert odeme_container.layout() is not None, "Ödeme container'ının layout'u olmalı"

        # Container'da başlık olmalı
        layout = odeme_container.layout()
        assert layout.count() >= 1, "Ödeme container'ında en az başlık olmalı"

        # İlk widget başlık olmalı
        baslik_widget = layout.itemAt(0).widget()
        assert isinstance(baslik_widget, QLabel), "İlk widget başlık (QLabel) olmalı"
        assert "Ödeme" in baslik_widget.text(), "Başlık 'Ödeme' içermeli"

    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=100, deadline=None)
    def test_hizli_urun_container_yapisi(self, test_iterasyon):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 2: POS Ekran Bileşenleri**

        Hızlı ürün container'ı uygun yapıda olmalıdır.
        Doğrular: Gereksinim 5.1
        """
        pos_ekrani = POSAnaEkran()
        hizli_urun_container = pos_ekrani._bilesenler["hizli_urun_container"]

        # Container'ın layout'u olmalı
        assert hizli_urun_container.layout() is not None, "Hızlı ürün container'ının layout'u olmalı"

        # Container'da başlık olmalı
        layout = hizli_urun_container.layout()
        assert layout.count() >= 1, "Hızlı ürün container'ında en az başlık olmalı"

        # İlk widget başlık olmalı
        baslik_widget = layout.itemAt(0).widget()
        assert isinstance(baslik_widget, QLabel), "İlk widget başlık (QLabel) olmalı"
        assert "Hızlı Ürün" in baslik_widget.text(), "Başlık 'Hızlı Ürün' içermeli"

    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=100, deadline=None)
    def test_islem_container_yapisi(self, test_iterasyon):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 2: POS Ekran Bileşenleri**

        İşlem kısayolları container'ı uygun yapıda olmalıdır.
        Doğrular: Gereksinim 6.1
        """
        pos_ekrani = POSAnaEkran()
        islem_container = pos_ekrani._bilesenler["islem_container"]

        # Container'ın layout'u olmalı
        assert islem_container.layout() is not None, "İşlem container'ının layout'u olmalı"

        # Container'da başlık olmalı
        layout = islem_container.layout()
        assert layout.count() >= 1, "İşlem container'ında en az başlık olmalı"

        # İlk widget başlık olmalı
        baslik_widget = layout.itemAt(0).widget()
        assert isinstance(baslik_widget, QLabel), "İlk widget başlık (QLabel) olmalı"
        assert "İşlem" in baslik_widget.text(), "Başlık 'İşlem' içermeli"
