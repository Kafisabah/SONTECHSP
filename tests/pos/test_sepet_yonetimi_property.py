# Version: 0.1.0
# Last Update: 2024-12-18
# Module: test_sepet_yonetimi_property
# Description: Sepet yönetimi özellik tabanlı testleri
# Changelog:
# - İlk oluşturma - Sepet yönetimi property testleri

"""
**Feature: pos-arayuz-entegrasyonu, Property 4: Sepet Yönetimi**

Sepet yönetimi özellik tabanlı testleri.
Herhangi bir sepet işleminde sistem sepet tablosunu güncellemeli
ve boş durumda "Sepet boş" mesajını göstermelidir.

**Doğrular: Gereksinim 3.1, 3.4, 3.5**
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from decimal import Decimal
import os

# Qt için headless mod
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt6.QtWidgets import QApplication

from sontechsp.uygulama.moduller.pos.ui.bilesenler.sepet_tablosu import SepetTablosu
from sontechsp.uygulama.moduller.pos.ui.handlers.pos_sinyalleri import POSSinyalleri


# Test stratejileri
sepet_ogesi_strategy = st.fixed_dictionaries(
    {
        "barkod": st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("Nd", "Lu", "Ll"))),
        "urun_adi": st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Zs"))),
        "adet": st.integers(min_value=1, max_value=100),
        "birim_fiyat": st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000.00"), places=2),
        "toplam_fiyat": st.decimals(min_value=Decimal("0.01"), max_value=Decimal("100000.00"), places=2),
    }
)

sepet_listesi_strategy = st.lists(sepet_ogesi_strategy, min_size=0, max_size=20)


class TestSepetYonetimiProperty:
    """Sepet yönetimi özellik tabanlı testleri"""

    @pytest.fixture(autouse=True)
    def setup_qt(self):
        """Qt uygulamasını kurar"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()

        self.sinyaller = POSSinyalleri()
        self.sepet_tablosu = SepetTablosu(self.sinyaller)

        yield

        # Temizlik
        try:
            self.sepet_tablosu.close()
        except:
            pass

    def test_sepet_temizleme_property(self):
        """
        Property: Sepet temizlendiğinde boş mesaj görünmeli

        Sepet temizlendikten sonra:
        - "Sepet boş" mesajı görünmelidir
        - Tablo gizlenmelidir
        """
        # Önce dolu sepet ayarla
        test_verisi = [
            {
                "barkod": "123456",
                "urun_adi": "Test Ürün",
                "adet": 1,
                "birim_fiyat": Decimal("10.00"),
                "toplam_fiyat": Decimal("10.00"),
            }
        ]

        self.sepet_tablosu._sepet_guncellendi(test_verisi)
        self.app.processEvents()

        # Dolu sepet kontrolü
        assert not self.sepet_tablosu.bos_sepet_label.isVisible()
        assert self.sepet_tablosu.tablo.isVisible()

        # Sepeti temizle
        self.sepet_tablosu._sepet_temizlendi()
        self.app.processEvents()

        # Boş sepet kontrolü
        assert self.sepet_tablosu.bos_sepet_label.isVisible()
        assert not self.sepet_tablosu.tablo.isVisible()
        assert self.sepet_tablosu.bos_sepet_label.text() == "Sepet boş"

    @given(sepet_verileri=sepet_listesi_strategy)
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_sepet_guncelleme_property(self, sepet_verileri):
        """
        Property: Sepet güncellendiğinde tablo güncellenmeli

        Herhangi bir sepet verisi için:
        - Sepet boşsa "Sepet boş" mesajı görünmeli
        - Sepet doluysa tablo görünmeli ve doğru veri göstermeli
        """
        # Sepet verilerini güncelle
        self.sepet_tablosu._sepet_guncellendi(sepet_verileri)
        self.app.processEvents()

        if not sepet_verileri:
            # Boş sepet durumu - Gereksinim 3.5
            assert self.sepet_tablosu.bos_sepet_label.isVisible()
            assert not self.sepet_tablosu.tablo.isVisible()
            assert self.sepet_tablosu.bos_sepet_label.text() == "Sepet boş"
        else:
            # Dolu sepet durumu - Gereksinim 3.1
            assert not self.sepet_tablosu.bos_sepet_label.isVisible()
            assert self.sepet_tablosu.tablo.isVisible()
            assert self.sepet_tablosu.tablo.rowCount() == len(sepet_verileri)

            # Tablo verilerini kontrol et
            for satir, veri in enumerate(sepet_verileri):
                barkod_item = self.sepet_tablosu.tablo.item(satir, 0)
                urun_item = self.sepet_tablosu.tablo.item(satir, 1)
                adet_item = self.sepet_tablosu.tablo.item(satir, 2)

                assert barkod_item.text() == str(veri["barkod"])
                assert urun_item.text() == str(veri["urun_adi"])
                assert adet_item.text() == str(veri["adet"])

    @given(urun_verisi=sepet_ogesi_strategy)
    @settings(max_examples=25, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_urun_ekleme_property(self, urun_verisi):
        """
        Property: Ürün eklendiğinde sepet güncellenmeli

        Herhangi bir ürün verisi için:
        - Ürün sepete eklenmelidir
        - Tablo güncellenmelidir
        """
        # Başlangıçta boş sepet
        self.sepet_tablosu._sepet_guncellendi([])
        self.app.processEvents()

        # Boş sepet kontrolü
        assert self.sepet_tablosu.bos_sepet_label.isVisible()

        # Ürün ekle
        self.sepet_tablosu._urun_eklendi(urun_verisi)
        self.app.processEvents()

        # Ürün eklendikten sonra kontrol
        assert not self.sepet_tablosu.bos_sepet_label.isVisible()
        assert self.sepet_tablosu.tablo.isVisible()
        assert self.sepet_tablosu.tablo.rowCount() == 1

        # Eklenen ürün verilerini kontrol et
        barkod_item = self.sepet_tablosu.tablo.item(0, 0)
        urun_item = self.sepet_tablosu.tablo.item(0, 1)
        adet_item = self.sepet_tablosu.tablo.item(0, 2)

        assert barkod_item.text() == str(urun_verisi["barkod"])
        assert urun_item.text() == str(urun_verisi["urun_adi"])
        assert adet_item.text() == str(urun_verisi["adet"])

    @given(sepet_verileri=sepet_listesi_strategy.filter(lambda x: len(x) > 0))
    @settings(max_examples=25, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_satir_silme_property(self, sepet_verileri):
        """
        Property: Satır silindiğinde sepet güncellenmeli

        Herhangi bir dolu sepet için:
        - Satır silme işlemi çalışmalı - Gereksinim 3.4
        - Sepet verisi güncellenmelidir
        """
        # Sepet verilerini ayarla
        self.sepet_tablosu._sepet_guncellendi(sepet_verileri)
        self.app.processEvents()

        # İlk satırı sil
        if len(sepet_verileri) > 0:
            ilk_satir_index = 0

            # Silme sinyalini dinle
            silinen_satirlar = []
            self.sepet_tablosu.satir_silindi.connect(lambda idx: silinen_satirlar.append(idx))

            # Sil butonuna tıkla
            self.sepet_tablosu._sil_butonu_tiklandi(ilk_satir_index)
            self.app.processEvents()

            # Silme sinyalinin gönderildiğini kontrol et
            assert len(silinen_satirlar) == 1
            assert silinen_satirlar[0] == ilk_satir_index
