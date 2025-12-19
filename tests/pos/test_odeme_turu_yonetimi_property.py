# Version: 0.1.0
# Last Update: 2024-12-19
# Module: test_odeme_turu_yonetimi_property
# Description: Ödeme türü yönetimi özellik tabanlı testleri
# Changelog:
# - İlk oluşturma - Özellik 4: Ödeme Türü Yönetimi testleri

"""
Ödeme Türü Yönetimi Özellik Testleri

**Feature: pos-yeni-ekran-tasarimi, Property 4: Ödeme Türü Yönetimi**
**Doğrular: Gereksinim 4.2**

Herhangi bir ödeme türü seçiminde, sistem büyük fontla genel toplam göstermeli,
ara toplam/indirim/KDV bilgilerini göstermeli ve seçilen ödeme türüne göre
uygun arayüzü (nakit için para üstü, parçalı için dialog) göstermelidir.
"""

import pytest
import sys
from decimal import Decimal
from hypothesis import given, settings, strategies as st
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton
from PyQt6.QtGui import QFont

from sontechsp.uygulama.arayuz.ekranlar.pos.odeme_paneli import OdemePaneli


class TestOdemeTuruYonetimiProperty:
    """Ödeme türü yönetimi özellik testleri"""

    @pytest.fixture(autouse=True)
    def setup_qt_app(self):
        """Qt uygulaması kurulumu"""
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
        yield

    @given(tutar=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("9999.99"), places=2))
    @settings(max_examples=100, deadline=5000)
    def test_genel_toplam_buyuk_font_gosterimi_property(self, tutar):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 4: Ödeme Türü Yönetimi**

        Herhangi bir tutar için genel toplam büyük fontla gösterilmelidir.
        Doğrular: Gereksinim 4.2
        """
        # Ödeme paneli oluştur
        odeme_paneli = OdemePaneli()

        # Genel toplam label'ının varlığını kontrol et
        assert hasattr(odeme_paneli, "genel_toplam_label"), "Genel toplam label'ı olmalı"
        assert isinstance(odeme_paneli.genel_toplam_label, QLabel), "Genel toplam QLabel olmalı"

        # Font boyutunun büyük olduğunu kontrol et
        font = odeme_paneli.genel_toplam_label.font()
        assert font.pointSize() >= 20, f"Font boyutu en az 20 olmalı, mevcut: {font.pointSize()}"
        assert font.bold(), "Font kalın olmalı"

        # Tutarı güncelle ve doğru gösterildiğini kontrol et
        odeme_paneli.genel_toplami_guncelle(tutar)
        beklenen_metin = f"{tutar:.2f} ₺"
        assert (
            odeme_paneli.genel_toplam_label.text() == beklenen_metin
        ), f"Genel toplam metni '{beklenen_metin}' olmalı, mevcut: '{odeme_paneli.genel_toplam_label.text()}'"

    @given(tutar=st.decimals(min_value=Decimal("1.18"), max_value=Decimal("9999.99"), places=2))  # En az KDV'li tutar
    @settings(max_examples=100, deadline=5000)
    def test_ara_toplam_indirim_kdv_gosterimi_property(self, tutar):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 4: Ödeme Türü Yönetimi**

        Herhangi bir tutar için ara toplam, indirim ve KDV bilgileri gösterilmelidir.
        Doğrular: Gereksinim 4.2
        """
        # Ödeme paneli oluştur
        odeme_paneli = OdemePaneli()

        # Gerekli label'ların varlığını kontrol et
        assert hasattr(odeme_paneli, "ara_toplam_label"), "Ara toplam label'ı olmalı"
        assert hasattr(odeme_paneli, "indirim_label"), "İndirim label'ı olmalı"
        assert hasattr(odeme_paneli, "kdv_label"), "KDV label'ı olmalı"

        # Tutarı güncelle
        odeme_paneli.genel_toplami_guncelle(tutar)

        # Ara toplam hesaplamasını kontrol et (KDV %18 varsayımı)
        beklenen_ara_toplam = tutar / Decimal("1.18")
        beklenen_kdv = tutar - beklenen_ara_toplam

        ara_toplam_metin = odeme_paneli.ara_toplam_label.text()
        kdv_metin = odeme_paneli.kdv_label.text()

        assert "Ara Toplam:" in ara_toplam_metin, "Ara toplam metni 'Ara Toplam:' içermeli"
        assert (
            f"{beklenen_ara_toplam:.2f}" in ara_toplam_metin
        ), f"Ara toplam doğru hesaplanmalı: {beklenen_ara_toplam:.2f}"

        assert "KDV:" in kdv_metin, "KDV metni 'KDV:' içermeli"
        assert f"{beklenen_kdv:.2f}" in kdv_metin, f"KDV doğru hesaplanmalı: {beklenen_kdv:.2f}"

    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=100, deadline=5000)
    def test_odeme_butonlari_varligi_property(self, test_iterasyon):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 4: Ödeme Türü Yönetimi**

        Ödeme panelinde tüm ödeme türü butonları mevcut olmalıdır.
        Doğrular: Gereksinim 4.2
        """
        # Ödeme paneli oluştur
        odeme_paneli = OdemePaneli()

        # Gerekli butonların varlığını kontrol et
        gerekli_butonlar = ["nakit_btn", "kart_btn", "parcali_btn", "acik_hesap_btn"]

        for buton_adi in gerekli_butonlar:
            assert hasattr(odeme_paneli, buton_adi), f"{buton_adi} butonu olmalı"
            buton = getattr(odeme_paneli, buton_adi)
            assert isinstance(buton, QPushButton), f"{buton_adi} QPushButton olmalı"
            assert buton.text(), f"{buton_adi} butonunun metni olmalı"

    @given(
        alinan_para=st.decimals(min_value=Decimal("0.00"), max_value=Decimal("10000.00"), places=2),
        toplam_tutar=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("9999.99"), places=2),
    )
    @settings(max_examples=100, deadline=5000)
    def test_nakit_odeme_para_ustu_hesaplama_property(self, alinan_para, toplam_tutar):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 4: Ödeme Türü Yönetimi**

        Nakit ödeme seçildiğinde para üstü doğru hesaplanmalıdır.
        Doğrular: Gereksinim 4.2
        """
        # Ödeme paneli oluştur
        odeme_paneli = OdemePaneli()

        # Toplam tutarı ayarla
        odeme_paneli.genel_toplami_guncelle(toplam_tutar)

        # Nakit alanını göster
        odeme_paneli.nakit_alanini_goster(True)

        # Alınan parayı gir
        odeme_paneli.alinan_para_edit.setText(str(alinan_para))

        # Para üstü hesaplamasını tetikle
        odeme_paneli.para_ustu_hesapla()

        # Para üstü label'ının varlığını kontrol et
        assert hasattr(odeme_paneli, "para_ustu_label"), "Para üstü label'ı olmalı"

        para_ustu_metin = odeme_paneli.para_ustu_label.text()
        beklenen_para_ustu = alinan_para - toplam_tutar

        if beklenen_para_ustu >= 0:
            assert "Para Üstü:" in para_ustu_metin, "Para üstü metni 'Para Üstü:' içermeli"
            assert (
                f"{beklenen_para_ustu:.2f}" in para_ustu_metin
            ), f"Para üstü doğru hesaplanmalı: {beklenen_para_ustu:.2f}"
        else:
            assert "Eksik:" in para_ustu_metin, "Eksik tutar metni 'Eksik:' içermeli"
            assert (
                f"{abs(beklenen_para_ustu):.2f}" in para_ustu_metin
            ), f"Eksik tutar doğru hesaplanmalı: {abs(beklenen_para_ustu):.2f}"

    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=100, deadline=5000)
    def test_nakit_alani_gosterme_gizleme_property(self, test_iterasyon):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 4: Ödeme Türü Yönetimi**

        Nakit alanı gösterme/gizleme işlevi doğru çalışmalıdır.
        Doğrular: Gereksinim 4.2
        """
        # Ödeme paneli oluştur ve göster (PyQt visibility için gerekli)
        odeme_paneli = OdemePaneli()
        odeme_paneli.show()

        # Nakit frame'inin varlığını kontrol et
        assert hasattr(odeme_paneli, "nakit_frame"), "Nakit frame'i olmalı"

        # Başlangıçta gizli olmalı
        assert not odeme_paneli.nakit_frame.isVisible(), "Nakit frame'i başlangıçta gizli olmalı"

        # Göster
        odeme_paneli.nakit_alanini_goster(True)
        assert odeme_paneli.nakit_frame.isVisible(), "Nakit frame'i gösterildiğinde görünür olmalı"

        # Gizle
        odeme_paneli.nakit_alanini_goster(False)
        assert not odeme_paneli.nakit_frame.isVisible(), "Nakit frame'i gizlendiğinde görünmez olmalı"

    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=100, deadline=5000)
    def test_sekme_sistemi_varligi_property(self, test_iterasyon):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 4: Ödeme Türü Yönetimi**

        Ödeme panelinde sekme sistemi mevcut olmalıdır.
        Doğrular: Gereksinim 4.2
        """
        # Ödeme paneli oluştur
        odeme_paneli = OdemePaneli()

        # Sekme widget'ının varlığını kontrol et
        assert hasattr(odeme_paneli, "tab_widget"), "Sekme widget'ı olmalı"

        # En az 2 sekme olmalı (Ödeme ve Hızlı Ürünler)
        assert odeme_paneli.tab_widget.count() >= 2, "En az 2 sekme olmalı"

        # Sekme isimlerini kontrol et
        sekme_isimleri = []
        for i in range(odeme_paneli.tab_widget.count()):
            sekme_isimleri.append(odeme_paneli.tab_widget.tabText(i))

        assert "Ödeme" in sekme_isimleri, "Ödeme sekmesi olmalı"
        assert "Hızlı Ürünler" in sekme_isimleri, "Hızlı Ürünler sekmesi olmalı"
