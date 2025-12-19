# Version: 0.1.0
# Last Update: 2024-12-18
# Module: test_hizli_urun_butonlari_property
# Description: Hızlı ürün butonları özellik testleri
# Changelog:
# - İlk oluşturma - Hızlı ürün butonları property testleri

"""
Hızlı Ürün Butonları Özellik Testleri

**Feature: pos-arayuz-entegrasyonu, Property 6: Hızlı Ürün Butonları**
**Validates: Requirements 5.1, 5.2, 5.4, 5.5**

Özellik: Herhangi bir hızlı ürün panelinde, sistem 12-24 arası buton göstermeli,
kategori değişiminde butonları güncellemeli ve boş butonlarda "Tanımsız" etiketi göstermelidir.
"""

import pytest
from hypothesis import given, strategies as st, assume
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import sys
from typing import Dict, List, Any

from sontechsp.uygulama.moduller.pos.ui.bilesenler.hizli_urun_paneli import HizliUrunPaneli
from sontechsp.uygulama.moduller.pos.ui.handlers.pos_sinyalleri import POSSinyalleri


class TestHizliUrunButonlariProperty:
    """Hızlı ürün butonları özellik testleri"""

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

    @given(
        buton_sayisi=st.integers(min_value=12, max_value=24),
        kategoriler=st.lists(
            st.fixed_dictionaries(
                {"id": st.text(min_size=1, max_size=10), "ad": st.text(min_size=1, max_size=20), "aktif": st.booleans()}
            ),
            min_size=1,
            max_size=10,
        ),
        hizli_urunler=st.lists(
            st.fixed_dictionaries(
                {
                    "id": st.text(min_size=1, max_size=10),
                    "barkod": st.text(min_size=8, max_size=20),
                    "urun_adi": st.text(min_size=1, max_size=50),
                    "birim_fiyat": st.floats(min_value=0.01, max_value=1000.0),
                    "kategori_id": st.text(min_size=1, max_size=10),
                    "pozisyon": st.integers(min_value=0, max_value=23),
                }
            ),
            min_size=0,
            max_size=24,
        ),
    )
    def test_hizli_urun_butonlari_property(self, buton_sayisi: int, kategoriler: List[Dict], hizli_urunler: List[Dict]):
        """
        **Feature: pos-arayuz-entegrasyonu, Property 6: Hızlı Ürün Butonları**
        **Validates: Requirements 5.1, 5.2, 5.4, 5.5**

        Özellik: Herhangi bir hızlı ürün panelinde, sistem 12-24 arası buton göstermeli,
        kategori değişiminde butonları güncellemeli ve boş butonlarda "Tanımsız" etiketi göstermelidir.
        """
        # Geçerli veri kontrolü
        assume(12 <= buton_sayisi <= 24)
        assume(len(kategoriler) > 0)
        assume(all(kategori["id"] and kategori["ad"] for kategori in kategoriler))

        # Kategori ID'lerinin benzersiz olduğunu kontrol et
        kategori_idleri = [k["id"] for k in kategoriler]
        assume(len(kategori_idleri) == len(set(kategori_idleri)))

        # Hızlı ürünlerin pozisyonlarının geçerli aralıkta olduğunu kontrol et
        for urun in hizli_urunler:
            assume(0 <= urun["pozisyon"] < buton_sayisi)
            assume(urun["birim_fiyat"] > 0)
            assume(urun["barkod"] and urun["urun_adi"])

        # Buton sayısını ayarla
        self.panel.buton_sayisi_combo.setCurrentText(str(buton_sayisi))
        self.app.processEvents()

        # Kategorileri güncelle
        self.panel._kategoriler_guncellendi(kategoriler)
        self.app.processEvents()

        # Hızlı ürünleri güncelle
        self.panel._hizli_urunler_guncellendi(hizli_urunler)
        self.app.processEvents()

        # Özellik 1: 12-24 arası buton sayısı kontrolü
        gercek_buton_sayisi = len(self.panel._butonlar)
        assert 12 <= gercek_buton_sayisi <= 24, f"Buton sayısı {gercek_buton_sayisi}, beklenen aralık: 12-24"
        assert gercek_buton_sayisi == buton_sayisi, f"Buton sayısı {gercek_buton_sayisi}, beklenen: {buton_sayisi}"

        # Özellik 2: Boş butonlarda "Tanımsız" etiketi kontrolü
        for i, buton in enumerate(self.panel._butonlar):
            urun_verisi = buton.property("productData")
            if not urun_verisi:
                assert (
                    buton.text() == "Tanımsız"
                ), f"Boş buton {i} 'Tanımsız' etiketi göstermeli, gösterilen: '{buton.text()}'"

        # Özellik 3: Kategori değişiminde buton güncelleme kontrolü
        aktif_kategoriler = [k for k in kategoriler if k.get("aktif", True)]
        if aktif_kategoriler:
            # İlk kategoriyi seç
            test_kategori = aktif_kategoriler[0]

            # Kategori combo'da kategoriyi bul ve seç
            for i in range(self.panel.kategori_combo.count()):
                if self.panel.kategori_combo.itemData(i) == test_kategori["id"]:
                    self.panel.kategori_combo.setCurrentIndex(i)
                    break

            self.app.processEvents()

            # Seçilen kategoriye ait ürünleri kontrol et
            kategori_urunleri = [u for u in hizli_urunler if u["kategori_id"] == test_kategori["id"]]

            for urun in kategori_urunleri:
                pozisyon = urun["pozisyon"]
                if pozisyon < len(self.panel._butonlar):
                    buton = self.panel._butonlar[pozisyon]
                    assert (
                        buton.text() == urun["urun_adi"]
                    ), f"Pozisyon {pozisyon}'daki buton '{urun['urun_adi']}' göstermeli, gösterilen: '{buton.text()}'"
                    assert buton.property("hasProduct") is True, f"Pozisyon {pozisyon}'daki buton ürün verisi içermeli"

        # Özellik 4: Tüm kategoriler seçeneği kontrolü
        # "Tümü" seçeneğini seç (index 0)
        self.panel.kategori_combo.setCurrentIndex(0)
        self.app.processEvents()

        # Tüm ürünlerin görünür olduğunu kontrol et
        for urun in hizli_urunler:
            pozisyon = urun["pozisyon"]
            if pozisyon < len(self.panel._butonlar):
                buton = self.panel._butonlar[pozisyon]
                assert (
                    buton.text() == urun["urun_adi"]
                ), f"'Tümü' seçildiğinde pozisyon {pozisyon}'daki buton '{urun['urun_adi']}' göstermeli"

    @given(
        pozisyon=st.integers(min_value=0, max_value=23),
        urun_verisi=st.fixed_dictionaries(
            {
                "id": st.text(min_size=1, max_size=10),
                "barkod": st.text(min_size=8, max_size=20),
                "urun_adi": st.text(min_size=1, max_size=50),
                "birim_fiyat": st.floats(min_value=0.01, max_value=1000.0),
                "kategori_id": st.text(min_size=1, max_size=10),
                "pozisyon": st.integers(min_value=0, max_value=23),
            }
        ),
    )
    def test_hizli_urun_buton_tiklama_property(self, pozisyon: int, urun_verisi: Dict):
        """
        Hızlı ürün buton tıklama özellik testi

        Özellik: Herhangi bir hızlı ürün butonuna tıklandığında,
        sistem ürünü sepete ekleme sinyali göndermeli.
        """
        # Geçerli veri kontrolü
        assume(0 <= pozisyon < 24)
        assume(urun_verisi["birim_fiyat"] > 0)
        assume(urun_verisi["barkod"] and urun_verisi["urun_adi"])
        urun_verisi["pozisyon"] = pozisyon

        # Sinyal yakalama için flag
        sinyal_yakalandi = False
        yakalanan_veri = None

        def sinyal_yakala(veri):
            nonlocal sinyal_yakalandi, yakalanan_veri
            sinyal_yakalandi = True
            yakalanan_veri = veri

        # Sinyali bağla
        self.panel.hizli_urun_secildi.connect(sinyal_yakala)

        # Ürünü panele ekle
        self.panel._hizli_urunler_guncellendi([urun_verisi])
        self.app.processEvents()

        # Pozisyon geçerliyse buton tıklama testi
        if pozisyon < len(self.panel._butonlar):
            buton = self.panel._butonlar[pozisyon]

            # Butonun ürün verisi içerdiğini kontrol et
            assert buton.property("hasProduct") is True, "Buton ürün verisi içermeli"
            assert buton.property("productData") == urun_verisi, "Buton doğru ürün verisini içermeli"

            # Butona tıkla
            buton.click()
            self.app.processEvents()

            # Sinyalin gönderildiğini kontrol et
            assert sinyal_yakalandi, "Hızlı ürün seçildi sinyali gönderilmeli"
            assert yakalanan_veri == urun_verisi, "Gönderilen veri doğru olmalı"

    @given(
        buton_sayisi_1=st.integers(min_value=12, max_value=24), buton_sayisi_2=st.integers(min_value=12, max_value=24)
    )
    def test_dinamik_buton_sayisi_degisimi_property(self, buton_sayisi_1: int, buton_sayisi_2: int):
        """
        Dinamik buton sayısı değişimi özellik testi

        Özellik: Buton sayısı değiştirildiğinde, sistem yeni sayıda buton oluşturmalı.
        """
        assume(12 <= buton_sayisi_1 <= 24)
        assume(12 <= buton_sayisi_2 <= 24)

        # İlk buton sayısını ayarla
        self.panel.buton_sayisi_combo.setCurrentText(str(buton_sayisi_1))
        self.app.processEvents()

        assert (
            len(self.panel._butonlar) == buton_sayisi_1
        ), f"İlk buton sayısı {buton_sayisi_1} olmalı, gerçek: {len(self.panel._butonlar)}"

        # İkinci buton sayısını ayarla
        self.panel.buton_sayisi_combo.setCurrentText(str(buton_sayisi_2))
        self.app.processEvents()

        assert (
            len(self.panel._butonlar) == buton_sayisi_2
        ), f"İkinci buton sayısı {buton_sayisi_2} olmalı, gerçek: {len(self.panel._butonlar)}"

        # Tüm butonların "Tanımsız" olduğunu kontrol et (ürün verisi yoksa)
        for i, buton in enumerate(self.panel._butonlar):
            if not buton.property("productData"):
                assert buton.text() == "Tanımsız", f"Boş buton {i} 'Tanımsız' göstermeli, gösterilen: '{buton.text()}'"

    def test_kategori_combo_guncelleme_property(self):
        """
        Kategori combo güncelleme özellik testi

        Özellik: Kategoriler güncellendiğinde, kategori combo box'ı güncellenmelidir.
        """
        # Test kategorileri
        kategoriler = [
            {"id": "1", "ad": "Test Kategori 1", "aktif": True},
            {"id": "2", "ad": "Test Kategori 2", "aktif": True},
            {"id": "3", "ad": "Test Kategori 3", "aktif": False},  # Pasif kategori
        ]

        # Kategorileri güncelle
        self.panel._kategoriler_guncellendi(kategoriler)
        self.app.processEvents()

        # Combo box'ta "Tümü" + aktif kategoriler olmalı
        beklenen_item_sayisi = 1 + len([k for k in kategoriler if k.get("aktif", True)])
        assert (
            self.panel.kategori_combo.count() == beklenen_item_sayisi
        ), f"Kategori combo'da {beklenen_item_sayisi} item olmalı, gerçek: {self.panel.kategori_combo.count()}"

        # İlk item "Tümü" olmalı
        assert self.panel.kategori_combo.itemText(0) == "Tümü", "İlk kategori 'Tümü' olmalı"
        assert self.panel.kategori_combo.itemData(0) == "", "İlk kategori verisi boş string olmalı"

        # Aktif kategorilerin combo'da olduğunu kontrol et
        combo_kategorileri = []
        for i in range(1, self.panel.kategori_combo.count()):  # 0. index "Tümü"
            combo_kategorileri.append(
                {"ad": self.panel.kategori_combo.itemText(i), "id": self.panel.kategori_combo.itemData(i)}
            )

        aktif_kategoriler = [k for k in kategoriler if k.get("aktif", True)]
        for kategori in aktif_kategoriler:
            combo_kategori = next((k for k in combo_kategorileri if k["id"] == kategori["id"]), None)
            assert combo_kategori is not None, f"Aktif kategori '{kategori['ad']}' combo'da bulunmalı"
            assert (
                combo_kategori["ad"] == kategori["ad"]
            ), f"Kategori adı '{kategori['ad']}' olmalı, gerçek: '{combo_kategori['ad']}'"
