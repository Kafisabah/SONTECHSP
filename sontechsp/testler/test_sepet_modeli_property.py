# Version: 0.1.0
# Last Update: 2024-12-19
# Module: test_sepet_modeli_property
# Description: Sepet modeli için özellik tabanlı testler
# Changelog:
# - İlk oluşturma
# - Syntax hatası düzeltildi ve import düzenlemesi yapıldı

"""
Sepet Modeli Özellik Tabanlı Testler

**Feature: pos-yeni-ekran-tasarimi, Property 3: Sepet Yönetimi**
**Validates: Requirements 3.3, 5.4**

Sepet işlemlerinde (satır seçimi, adet değiştirme, silme), sistem QTableView ile
doğru kolonları göstermeli, seçili satırda adet değiştirme imkanı sunmalı ve
sepet altında işlem butonlarını göstermelidir.
"""

import sys
from decimal import Decimal
from typing import List

import pytest
from hypothesis import given, strategies as st, assume
from PyQt6.QtCore import Qt, QModelIndex
from PyQt6.QtWidgets import QApplication

from sontechsp.uygulama.arayuz.ekranlar.pos.sepet_modeli import SepetModeli, SepetOgesi


@pytest.fixture(scope="session")
def qapp():
    """PyQt6 uygulama fixture'ı"""
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    yield app


# Test veri üreticileri
@st.composite
def sepet_ogesi_uretici(draw):
    """Geçerli sepet öğesi üretir"""
    barkod = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("Nd", "Lu"))))
    urun_adi = draw(
        st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs")))
    )
    adet = draw(st.integers(min_value=1, max_value=999))
    birim_fiyat = draw(st.decimals(min_value=Decimal("0.01"), max_value=Decimal("9999.99"), places=2))
    indirim_orani_decimal = draw(st.decimals(min_value=Decimal("0.0"), max_value=Decimal("0.99"), places=2))
    indirim_orani = float(indirim_orani_decimal)

    toplam_fiyat = birim_fiyat * adet * (Decimal("1") - indirim_orani_decimal)

    return SepetOgesi(
        barkod=barkod,
        urun_adi=urun_adi,
        adet=adet,
        birim_fiyat=birim_fiyat,
        toplam_fiyat=toplam_fiyat,
        indirim_orani=indirim_orani,
    )


@st.composite
def sepet_ogesi_listesi_uretici(draw):
    """Sepet öğesi listesi üretir"""
    return draw(st.lists(sepet_ogesi_uretici(), min_size=0, max_size=20))


class TestSepetModeliProperty:
    """Sepet modeli özellik tabanlı testleri"""

    @given(sepet_ogesi_listesi_uretici())
    def test_kolon_yapisi_tutarliligi(self, qapp, sepet_ogeleri: List[SepetOgesi]):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 3: Sepet Yönetimi**
        **Validates: Requirements 3.3, 5.4**

        Herhangi bir sepet durumunda, model doğru kolon sayısını ve isimlerini göstermelidir.
        """
        model = SepetModeli()

        # Sepet öğelerini ekle
        for oge in sepet_ogeleri:
            model.oge_ekle(oge)

        # Kolon sayısı kontrolü
        assert model.columnCount() == 6, "Model 6 kolon göstermeli"

        # Kolon isimleri kontrolü
        beklenen_kolonlar = ["Barkod", "Ürün", "Adet", "Fiyat", "Tutar", "Sil"]
        for i, kolon_adi in enumerate(beklenen_kolonlar):
            assert model.headerData(i, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole) == kolon_adi

        # Satır sayısı kontrolü
        assert model.rowCount() == len(sepet_ogeleri), "Satır sayısı sepet öğe sayısına eşit olmalı"

    @given(sepet_ogesi_uretici())
    def test_oge_ekleme_ve_veri_tutarliligi(self, qapp, sepet_ogesi: SepetOgesi):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 3: Sepet Yönetimi**
        **Validates: Requirements 3.3, 5.4**

        Herhangi bir geçerli sepet öğesi eklendiğinde, model doğru veriyi göstermelidir.
        """
        model = SepetModeli()
        model.oge_ekle(sepet_ogesi)

        # Satır sayısı kontrolü
        assert model.rowCount() == 1, "Bir öğe eklendikten sonra satır sayısı 1 olmalı"

        # Veri kontrolü
        index_barkod = model.index(0, 0)
        index_urun = model.index(0, 1)
        index_adet = model.index(0, 2)
        index_fiyat = model.index(0, 3)
        index_tutar = model.index(0, 4)

        assert model.data(index_barkod, Qt.ItemDataRole.DisplayRole) == sepet_ogesi.barkod
        assert model.data(index_urun, Qt.ItemDataRole.DisplayRole) == sepet_ogesi.urun_adi
        assert model.data(index_adet, Qt.ItemDataRole.DisplayRole) == str(sepet_ogesi.adet)
        assert model.data(index_fiyat, Qt.ItemDataRole.DisplayRole) == f"{sepet_ogesi.birim_fiyat:.2f} ₺"
        assert model.data(index_tutar, Qt.ItemDataRole.DisplayRole) == f"{sepet_ogesi.toplam_hesapla():.2f} ₺"

    @given(sepet_ogesi_uretici(), st.integers(min_value=1, max_value=999))
    def test_adet_degistirme_ozelligi(self, qapp, sepet_ogesi: SepetOgesi, yeni_adet: int):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 3: Sepet Yönetimi**
        **Validates: Requirements 3.3, 5.4**

        Herhangi bir sepet öğesinde adet değiştirildiğinde, toplam tutar yeniden hesaplanmalıdır.
        """
        model = SepetModeli()
        model.oge_ekle(sepet_ogesi)

        # Adet kolonunun düzenlenebilir olduğunu kontrol et
        adet_index = model.index(0, 2)
        flags = model.flags(adet_index)
        assert flags & Qt.ItemFlag.ItemIsEditable, "Adet kolonu düzenlenebilir olmalı"

        # Adeti değiştir
        basarili = model.setData(adet_index, yeni_adet, Qt.ItemDataRole.EditRole)
        assert basarili, "Adet değiştirme başarılı olmalı"

        # Yeni adet kontrolü
        assert model.data(adet_index, Qt.ItemDataRole.DisplayRole) == str(yeni_adet)

        # Toplam tutar yeniden hesaplanmalı
        tutar_index = model.index(0, 4)
        beklenen_tutar = sepet_ogesi.birim_fiyat * yeni_adet * (1 - sepet_ogesi.indirim_orani)
        assert model.data(tutar_index, Qt.ItemDataRole.DisplayRole) == f"{beklenen_tutar:.2f} ₺"

    @given(sepet_ogesi_listesi_uretici())
    def test_oge_silme_tutarliligi(self, qapp, sepet_ogeleri: List[SepetOgesi]):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 3: Sepet Yönetimi**
        **Validates: Requirements 3.3, 5.4**

        Herhangi bir sepet öğesi silindiğinde, model tutarlı kalmalıdır.
        """
        assume(len(sepet_ogeleri) > 0)  # En az bir öğe olmalı

        model = SepetModeli()

        # Tüm öğeleri ekle
        for oge in sepet_ogeleri:
            model.oge_ekle(oge)

        baslangic_satir_sayisi = model.rowCount()

        # Rastgele bir satırı sil
        silinecek_satir = len(sepet_ogeleri) // 2 if len(sepet_ogeleri) > 1 else 0
        model.oge_sil(silinecek_satir)

        # Satır sayısı bir azalmalı
        assert model.rowCount() == baslangic_satir_sayisi - 1, "Silme sonrası satır sayısı bir azalmalı"

    @given(sepet_ogesi_listesi_uretici())
    def test_sepet_temizleme_ozelligi(self, qapp, sepet_ogeleri: List[SepetOgesi]):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 3: Sepet Yönetimi**
        **Validates: Requirements 3.3, 5.4**

        Sepet temizlendiğinde, tüm öğeler silinmeli ve toplam sıfır olmalıdır.
        """
        model = SepetModeli()

        # Öğeleri ekle
        for oge in sepet_ogeleri:
            model.oge_ekle(oge)

        # Sepeti temizle
        model.sepeti_temizle()

        # Kontroller
        assert model.rowCount() == 0, "Temizleme sonrası satır sayısı sıfır olmalı"
        assert model.genel_toplam() == Decimal("0"), "Temizleme sonrası genel toplam sıfır olmalı"

    @given(sepet_ogesi_listesi_uretici())
    def test_genel_toplam_hesaplama(self, qapp, sepet_ogeleri: List[SepetOgesi]):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 3: Sepet Yönetimi**
        **Validates: Requirements 3.3, 5.4**

        Genel toplam, tüm sepet öğelerinin toplamına eşit olmalıdır.
        """
        model = SepetModeli()

        # Öğeleri ekle
        for oge in sepet_ogeleri:
            model.oge_ekle(oge)

        # Manuel toplam hesapla
        manuel_toplam = sum(oge.toplam_hesapla() for oge in sepet_ogeleri)

        # Model toplamı ile karşılaştır
        assert model.genel_toplam() == manuel_toplam, "Genel toplam manuel hesaplama ile eşit olmalı"

    @given(sepet_ogesi_uretici())
    def test_satir_renklendirme_ozelligi(self, qapp, sepet_ogesi: SepetOgesi):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 3: Sepet Yönetimi**
        **Validates: Requirements 3.3, 5.4**

        Satırlar alternatif renklerde gösterilmelidir (zebra striping).
        """
        model = SepetModeli()
        model.oge_ekle(sepet_ogesi)

        # İlk satır için arka plan rengi kontrolü
        index = model.index(0, 0)
        arka_plan_rengi = model.data(index, Qt.ItemDataRole.BackgroundRole)

        assert arka_plan_rengi is not None, "Satır arka plan rengi tanımlanmalı"

    def test_gecersiz_adet_degistirme(self, qapp):
        """
        **Feature: pos-yeni-ekran-tasarimi, Property 3: Sepet Yönetimi**
        **Validates: Requirements 3.3, 5.4**

        Geçersiz adet değerleri reddedilmelidir.
        """
        model = SepetModeli()
        sepet_ogesi = SepetOgesi(
            barkod="TEST123", urun_adi="Test Ürün", adet=1, birim_fiyat=Decimal("10.00"), toplam_fiyat=Decimal("10.00")
        )
        model.oge_ekle(sepet_ogesi)

        adet_index = model.index(0, 2)

        # Sıfır adet - reddedilmeli
        basarili = model.setData(adet_index, 0, Qt.ItemDataRole.EditRole)
        assert not basarili, "Sıfır adet reddedilmeli"

        # Negatif adet - reddedilmeli
        basarili = model.setData(adet_index, -1, Qt.ItemDataRole.EditRole)
        assert not basarili, "Negatif adet reddedilmeli"

        # Geçersiz string - reddedilmeli
        basarili = model.setData(adet_index, "abc", Qt.ItemDataRole.EditRole)
        assert not basarili, "Geçersiz string adet reddedilmeli"
