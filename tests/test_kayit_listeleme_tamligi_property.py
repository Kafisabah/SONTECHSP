# Version: 0.1.0
# Last Update: 2024-12-18
# Module: tests.test_kayit_listeleme_tamligi_property
# Description: Kayıt listeleme tamlığı property-based testleri
# Changelog:
# - İlk oluşturma

"""
UI Smoke Test Altyapısı - Kayıt Listeleme Tamlığı Property-Based Testleri

Bu modül buton eşleştirme kayıt sisteminin listeleme tamlığı özelliklerini test eder.
"""

from typing import Any, Dict, List

import pytest
from hypothesis import given, settings, strategies as st

from uygulama.arayuz.buton_eslestirme_kaydi import (
    kayit_ekle,
    kayitlari_listele,
    kayitlari_temizle,
)


class TestKayitListelemeTamligi:
    """Kayıt listeleme tamlığı property-based testleri"""

    def setup_method(self):
        """Her test öncesi kayıtları temizle"""
        kayitlari_temizle()

    @given(
        kayit_sayisi=st.integers(min_value=0, max_value=50),
        ekran_adi=st.text(
            min_size=1,
            max_size=20,
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), min_codepoint=32, max_codepoint=126),
        ).filter(lambda x: x.strip()),
    )
    @settings(max_examples=100, deadline=10000)
    def test_property_kayit_listeleme_tamligi(self, kayit_sayisi: int, ekran_adi: str):
        """
        **Feature: ui-smoke-test-altyapisi, Property 5: Kayıt Listeleme Tamlığı**

        Herhangi bir buton eşleştirme sorgusu yapıldığında, sistem tüm kayıtlı
        eşleştirmelerin tam listesini döndürmelidir
        **Validates: Requirements 2.2**
        """
        # Arrange - Belirli sayıda kayıt ekle
        eklenen_kayitlar = []
        for i in range(kayit_sayisi):
            kayit_bilgisi = {
                "ekran_adi": ekran_adi,
                "buton_adi": f"buton_{i}",
                "handler_adi": f"handler_{i}",
                "servis_metodu": f"servis_{i}" if i % 3 == 0 else None,
            }
            eklenen_kayitlar.append(kayit_bilgisi)
            kayit_ekle(**kayit_bilgisi)

        # Act - Kayıtları listele
        listelenen_kayitlar = kayitlari_listele()

        # Assert - Tamlık kontrolleri
        # 1. Listelenen kayıt sayısı eklenen kayıt sayısına eşit olmalı
        assert len(listelenen_kayitlar) == kayit_sayisi

        # 2. Her eklenen kayıt listede bulunmalı
        for i, eklenen in enumerate(eklenen_kayitlar):
            listelenen = listelenen_kayitlar[i]

            # Zorunlu alanlar eşleşmeli
            assert listelenen["ekran_adi"] == eklenen["ekran_adi"]
            assert listelenen["buton_adi"] == eklenen["buton_adi"]
            assert listelenen["handler_adi"] == eklenen["handler_adi"]
            assert listelenen["servis_metodu"] == eklenen["servis_metodu"]

            # Otomatik alanlar mevcut olmalı
            assert "kayit_zamani" in listelenen
            assert "cagrilma_sayisi" in listelenen

        # 3. Hiçbir kayıt eksik olmamalı
        assert len(listelenen_kayitlar) == len(eklenen_kayitlar)

    @given(
        ilk_grup_sayisi=st.integers(min_value=1, max_value=20),
        ikinci_grup_sayisi=st.integers(min_value=1, max_value=20),
    )
    @settings(max_examples=50, deadline=10000)
    def test_property_artan_kayit_tamligi(self, ilk_grup_sayisi: int, ikinci_grup_sayisi: int):
        """
        **Feature: ui-smoke-test-altyapisi, Property 5: Kayıt Listeleme Tamlığı**

        Herhangi bir zamanda yeni kayıtlar eklendiğinde, listeleme tüm kayıtları
        içermelidir (artımlı tamlık)
        **Validates: Requirements 2.2**
        """
        # Arrange & Act - İlk grup kayıt ekle
        for i in range(ilk_grup_sayisi):
            kayit_ekle(
                ekran_adi="ekran_1",
                buton_adi=f"buton_1_{i}",
                handler_adi=f"handler_1_{i}",
            )

        # İlk listeleme
        ilk_liste = kayitlari_listele()
        ilk_liste_sayisi = len(ilk_liste)

        # İkinci grup kayıt ekle
        for i in range(ikinci_grup_sayisi):
            kayit_ekle(
                ekran_adi="ekran_2",
                buton_adi=f"buton_2_{i}",
                handler_adi=f"handler_2_{i}",
            )

        # İkinci listeleme
        ikinci_liste = kayitlari_listele()

        # Assert - Artımlı tamlık kontrolleri
        # 1. İkinci liste ilk listeden daha uzun olmalı
        assert len(ikinci_liste) == ilk_liste_sayisi + ikinci_grup_sayisi

        # 2. İlk listedeki tüm kayıtlar ikinci listede de olmalı
        for i in range(ilk_liste_sayisi):
            assert ikinci_liste[i] == ilk_liste[i]

        # 3. Yeni eklenen kayıtlar ikinci listede bulunmalı
        yeni_kayitlar = ikinci_liste[ilk_liste_sayisi:]
        assert len(yeni_kayitlar) == ikinci_grup_sayisi

        for i, kayit in enumerate(yeni_kayitlar):
            assert kayit["ekran_adi"] == "ekran_2"
            assert kayit["buton_adi"] == f"buton_2_{i}"
            assert kayit["handler_adi"] == f"handler_2_{i}"

    @given(kayit_sayisi=st.integers(min_value=1, max_value=30))
    @settings(max_examples=50, deadline=10000)
    def test_property_listeleme_sira_tamligi(self, kayit_sayisi: int):
        """
        **Feature: ui-smoke-test-altyapisi, Property 5: Kayıt Listeleme Tamlığı**

        Herhangi bir kayıt sırası için, listeleme kayıtları ekleme sırasına göre
        döndürmelidir (sıralı tamlık)
        **Validates: Requirements 2.2**
        """
        # Arrange & Act - Sıralı kayıt ekle
        for i in range(kayit_sayisi):
            kayit_ekle(
                ekran_adi=f"ekran_{i}",
                buton_adi=f"buton_{i}",
                handler_adi=f"handler_{i}",
                servis_metodu=f"servis_{i}",
            )

        # Kayıtları listele
        kayitlar = kayitlari_listele()

        # Assert - Sıralı tamlık kontrolleri
        # 1. Kayıt sayısı doğru olmalı
        assert len(kayitlar) == kayit_sayisi

        # 2. Kayıtlar ekleme sırasına göre olmalı
        for i in range(kayit_sayisi):
            kayit = kayitlar[i]
            assert kayit["ekran_adi"] == f"ekran_{i}"
            assert kayit["buton_adi"] == f"buton_{i}"
            assert kayit["handler_adi"] == f"handler_{i}"
            assert kayit["servis_metodu"] == f"servis_{i}"

        # 3. Hiçbir kayıt atlanmamalı
        ekran_adlari = [k["ekran_adi"] for k in kayitlar]
        beklenen_ekran_adlari = [f"ekran_{i}" for i in range(kayit_sayisi)]
        assert ekran_adlari == beklenen_ekran_adlari

    def test_property_bos_liste_tamligi(self):
        """
        **Feature: ui-smoke-test-altyapisi, Property 5: Kayıt Listeleme Tamlığı**

        Herhangi bir kayıt yokken, listeleme boş liste döndürmelidir
        **Validates: Requirements 2.2**
        """
        # Arrange - Kayıtlar zaten temizlenmiş (setup_method)

        # Act - Kayıtları listele
        kayitlar = kayitlari_listele()

        # Assert - Boş liste tamlığı
        assert isinstance(kayitlar, list)
        assert len(kayitlar) == 0
        assert kayitlar == []

    @given(
        kayit_sayisi=st.integers(min_value=1, max_value=20),
        sorgu_sayisi=st.integers(min_value=2, max_value=5),
    )
    @settings(max_examples=30, deadline=10000)
    def test_property_coklu_sorgu_tamligi(self, kayit_sayisi: int, sorgu_sayisi: int):
        """
        **Feature: ui-smoke-test-altyapisi, Property 5: Kayıt Listeleme Tamlığı**

        Herhangi bir sayıda sorgu yapıldığında, her sorgu aynı tam listeyi
        döndürmelidir (tutarlı tamlık)
        **Validates: Requirements 2.2**
        """
        # Arrange - Kayıt ekle
        for i in range(kayit_sayisi):
            kayit_ekle(
                ekran_adi="ekran",
                buton_adi=f"buton_{i}",
                handler_adi=f"handler_{i}",
            )

        # Act - Birden fazla sorgu yap
        sorgular = []
        for _ in range(sorgu_sayisi):
            sorgular.append(kayitlari_listele())

        # Assert - Tutarlı tamlık kontrolleri
        # 1. Tüm sorgular aynı sayıda kayıt döndürmeli
        for sorgu in sorgular:
            assert len(sorgu) == kayit_sayisi

        # 2. Tüm sorgular aynı içeriği döndürmeli
        ilk_sorgu = sorgular[0]
        for sorgu in sorgular[1:]:
            assert len(sorgu) == len(ilk_sorgu)
            for i in range(len(sorgu)):
                assert sorgu[i]["ekran_adi"] == ilk_sorgu[i]["ekran_adi"]
                assert sorgu[i]["buton_adi"] == ilk_sorgu[i]["buton_adi"]
                assert sorgu[i]["handler_adi"] == ilk_sorgu[i]["handler_adi"]
                assert sorgu[i]["servis_metodu"] == ilk_sorgu[i]["servis_metodu"]
