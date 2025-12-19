# Version: 0.1.0
# Last Update: 2024-12-19
# Module: test_hizli_urun_butonlari_ozellik5_property
# Description: Hızlı ürün butonları Özellik 5 testleri
# Changelog:
# - İlk oluşturma - Özellik 5: Hızlı Ürün Butonları property testleri

"""
Hızlı Ürün Butonları Özellik 5 Testleri

**Feature: pos-yeni-ekran-tasarimi, Property 5: Hızlı Ürün Butonları**
**Validates: Requirements 6.4, 6.5**

Özellik: Herhangi bir hızlı ürün panelinde, sistem 12-24 arası buton grid'i göstermeli,
kategori değişiminde butonları güncellemeli ve buton tıklamasında ürünü sepete eklemeli.
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import sys
from typing import Dict, List, Any
from decimal import Decimal

from sontechsp.uygulama.arayuz.ekranlar.pos.hizli_urunler_sekmesi import HizliUrunlerSekmesi, HizliUrunButonu


class TestHizliUrunButonlariOzellik5Property:
    """Hızlı ürün butonları Özellik 5 testleri"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Test kurulumu"""
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()

        self.sekme = HizliUrunlerSekmesi()
        yield

        # Temizlik
        self.sekme.close()
        self.sekme.deleteLater()

    @given(
        kategori_sayisi=st.integers(min_value=1, max_value=5),
        urun_sayisi=st.integers(min_value=0, max_value=24),
    )
    @settings(max_examples=100, deadline=None)
    def test_hizli_urun_butonlari_grid_property(self, kategori_sayisi: int, urun_sayisi: int):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 5: Hızlı Ürün Butonları**
        **Validates: Requirements 6.4, 6.5**

        Özellik: Herhangi bir hızlı ürün panelinde, sistem 12-24 arası buton grid'i göstermeli,
        kategori değişiminde butonları güncellemeli ve buton tıklamasında ürünü sepete eklemeli.
        """
        # Geçerli veri kontrolü
        assume(1 <= kategori_sayisi <= 5)
        assume(0 <= urun_sayisi <= 24)

        # Test kategorileri oluştur
        kategoriler = []
        for i in range(kategori_sayisi):
            kategoriler.append({"id": i + 1, "ad": f"Kategori {i + 1}", "aktif": True})

        # Test ürünleri oluştur
        hizli_urunler = []
        for i in range(urun_sayisi):
            kategori_id = (i % kategori_sayisi) + 1
            hizli_urun = HizliUrunButonu(
                pozisyon=i,
                urun_id=i + 1,
                urun_adi=f"Ürün {i + 1}",
                barkod=f"123456789{i:03d}",
                fiyat=Decimal(f"{10 + i}.50"),
                kategori_id=kategori_id,
                aktif=True,
            )
            hizli_urunler.append(hizli_urun)

        # Kategorileri ekle
        for kategori in kategoriler:
            self.sekme.kategori_ekle(kategori["id"], kategori["ad"])

        # Hızlı ürünleri yükle
        self.sekme.hizli_urunleri_yukle(hizli_urunler)
        self.app.processEvents()

        # Özellik 1: 12-24 arası buton grid kontrolü
        buton_sayisi = self.sekme.buton_layout.count()
        assert 12 <= buton_sayisi <= 24, f"Buton sayısı {buton_sayisi}, beklenen aralık: 12-24"
        assert buton_sayisi == 24, f"Grid sistemde 24 buton olmalı, gerçek: {buton_sayisi}"

        # Özellik 2: Kategori değişiminde buton güncelleme kontrolü
        if kategoriler:
            # İlk kategoriyi seç (index 1, çünkü 0 "Tüm Kategoriler")
            self.sekme.kategori_combo.setCurrentIndex(1)
            self.app.processEvents()

            # Seçilen kategoriye ait ürünleri kontrol et
            secilen_kategori_id = kategoriler[0]["id"]
            kategori_urunleri = [u for u in hizli_urunler if u.kategori_id == secilen_kategori_id]

            # Grid'deki butonları kontrol et
            for i in range(24):
                buton = self.sekme.buton_layout.itemAt(i).widget()

                # Bu pozisyonda kategori ürünü var mı?
                pozisyon_urunu = next((u for u in kategori_urunleri if u.pozisyon == i), None)

                if pozisyon_urunu:
                    # Buton aktif olmalı ve ürün adını göstermeli
                    assert buton.isEnabled(), f"Pozisyon {i}'daki buton aktif olmalı"
                    assert (
                        pozisyon_urunu.urun_adi in buton.text()
                    ), f"Pozisyon {i}'daki buton '{pozisyon_urunu.urun_adi}' içermeli"
                else:
                    # Boş buton olmalı
                    assert not buton.isEnabled() or "Boş" in buton.text(), f"Pozisyon {i}'daki buton boş olmalı"

        # Özellik 3: Buton tıklamasında sinyal gönderme kontrolü
        if hizli_urunler:
            # Sinyal yakalama için flag
            sinyal_yakalandi = False
            yakalanan_barkod = None

            def sinyal_yakala(barkod):
                nonlocal sinyal_yakalandi, yakalanan_barkod
                sinyal_yakalandi = True
                yakalanan_barkod = barkod

            # Sinyali bağla
            self.sekme.hizli_urun_secildi.connect(sinyal_yakala)

            # İlk ürünün butonuna tıkla
            ilk_urun = hizli_urunler[0]
            buton = self.sekme.buton_layout.itemAt(ilk_urun.pozisyon).widget()

            if buton.isEnabled():
                buton.click()
                self.app.processEvents()

                # Sinyalin gönderildiğini kontrol et
                assert sinyal_yakalandi, "Hızlı ürün seçildi sinyali gönderilmeli"
                assert (
                    yakalanan_barkod == ilk_urun.barkod
                ), f"Gönderilen barkod '{ilk_urun.barkod}' olmalı, gerçek: '{yakalanan_barkod}'"

    @given(
        kategori_id=st.integers(min_value=1, max_value=10),
        kategori_adi=st.text(min_size=1, max_size=20),
    )
    @settings(max_examples=100, deadline=None)
    def test_kategori_degisimi_buton_guncelleme_property(self, kategori_id: int, kategori_adi: str):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 5: Hızlı Ürün Butonları**
        **Validates: Requirements 6.5**

        Özellik: Kategori değiştirildiğinde sistem butonları yeni kategori ürünleri ile güncellemeli.
        """
        # Geçerli veri kontrolü
        assume(1 <= kategori_id <= 10)
        assume(len(kategori_adi.strip()) > 0)

        # Test kategorisi ekle
        self.sekme.kategori_ekle(kategori_id, kategori_adi)

        # Test ürünleri oluştur - bazıları bu kategoride, bazıları farklı kategoride
        hizli_urunler = []
        for i in range(6):  # 6 ürün oluştur
            urun_kategori_id = kategori_id if i < 3 else kategori_id + 1
            hizli_urun = HizliUrunButonu(
                pozisyon=i,
                urun_id=i + 1,
                urun_adi=f"Ürün {i + 1}",
                barkod=f"123456789{i:03d}",
                fiyat=Decimal(f"{10 + i}.50"),
                kategori_id=urun_kategori_id,
                aktif=True,
            )
            hizli_urunler.append(hizli_urun)

        # Diğer kategoriyi de ekle
        self.sekme.kategori_ekle(kategori_id + 1, f"Diğer Kategori")

        # Hızlı ürünleri yükle
        self.sekme.hizli_urunleri_yukle(hizli_urunler)
        self.app.processEvents()

        # Önce "Tüm Kategoriler" seçili - tüm ürünler görünür olmalı
        self.sekme.kategori_combo.setCurrentIndex(0)  # Tüm Kategoriler
        self.app.processEvents()

        tum_urunler_gorunur = 0
        for i in range(6):
            buton = self.sekme.buton_layout.itemAt(i).widget()
            if buton.isEnabled() and "Ürün" in buton.text():
                tum_urunler_gorunur += 1

        assert (
            tum_urunler_gorunur == 6
        ), f"Tüm kategoriler seçildiğinde 6 ürün görünür olmalı, gerçek: {tum_urunler_gorunur}"

        # Şimdi belirli kategoriyi seç
        # Kategori combo'da kategoriyi bul
        kategori_index = -1
        for i in range(self.sekme.kategori_combo.count()):
            if self.sekme.kategori_combo.itemData(i) == kategori_id:
                kategori_index = i
                break

        if kategori_index > 0:  # Kategori bulunduysa
            self.sekme.kategori_combo.setCurrentIndex(kategori_index)
            self.app.processEvents()

            # Sadece seçilen kategoriye ait ürünler görünür olmalı
            kategori_urunleri_gorunur = 0
            for i in range(6):
                buton = self.sekme.buton_layout.itemAt(i).widget()
                if buton.isEnabled() and "Ürün" in buton.text():
                    # Bu ürün seçilen kategoriye ait mi?
                    urun = hizli_urunler[i]
                    if urun.kategori_id == kategori_id:
                        kategori_urunleri_gorunur += 1

            beklenen_kategori_urun_sayisi = len([u for u in hizli_urunler if u.kategori_id == kategori_id])
            assert (
                kategori_urunleri_gorunur == beklenen_kategori_urun_sayisi
            ), f"Kategori seçildiğinde {beklenen_kategori_urun_sayisi} ürün görünür olmalı, gerçek: {kategori_urunleri_gorunur}"

    @given(
        pozisyon=st.integers(min_value=0, max_value=23),
        barkod=st.text(min_size=8, max_size=20),
        urun_adi=st.text(min_size=1, max_size=30),
        fiyat=st.floats(min_value=0.01, max_value=1000.0),
    )
    @settings(max_examples=100, deadline=None)
    def test_buton_tiklama_sepete_ekleme_property(self, pozisyon: int, barkod: str, urun_adi: str, fiyat: float):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 5: Hızlı Ürün Butonları**
        **Validates: Requirements 6.4**

        Özellik: Buton tıklamasında ürünü sepete eklemeli (sinyal gönderme).
        """
        # Geçerli veri kontrolü
        assume(0 <= pozisyon <= 23)
        assume(len(barkod.strip()) >= 8)
        assume(len(urun_adi.strip()) > 0)
        assume(0.01 <= fiyat <= 1000.0)

        # Test ürünü oluştur
        hizli_urun = HizliUrunButonu(
            pozisyon=pozisyon,
            urun_id=1,
            urun_adi=urun_adi.strip(),
            barkod=barkod.strip(),
            fiyat=Decimal(str(round(fiyat, 2))),
            kategori_id=1,
            aktif=True,
        )

        # Ürünü yükle
        self.sekme.hizli_urunleri_yukle([hizli_urun])
        self.app.processEvents()

        # Sinyal yakalama için flag
        sinyal_yakalandi = False
        yakalanan_barkod = None

        def sinyal_yakala(barkod_param):
            nonlocal sinyal_yakalandi, yakalanan_barkod
            sinyal_yakalandi = True
            yakalanan_barkod = barkod_param

        # Sinyali bağla
        self.sekme.hizli_urun_secildi.connect(sinyal_yakala)

        # Butona tıkla
        buton = self.sekme.buton_layout.itemAt(pozisyon).widget()

        if buton and buton.isEnabled():
            buton.click()
            self.app.processEvents()

            # Sinyalin gönderildiğini kontrol et
            assert sinyal_yakalandi, f"Pozisyon {pozisyon}'daki buton tıklandığında sinyal gönderilmeli"
            assert (
                yakalanan_barkod == hizli_urun.barkod
            ), f"Gönderilen barkod '{hizli_urun.barkod}' olmalı, gerçek: '{yakalanan_barkod}'"
