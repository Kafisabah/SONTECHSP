# Version: 0.1.0
# Last Update: 2024-12-18
# Module: tests.test_negatif_stok_tutarlılığı_property
# Description: Negatif stok tutarlılığı property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Negatif Stok Tutarlılığı Property Testleri

Bu modül negatif stok kontrol kurallarının tutarlılığını test eder.
Requirements 2.4'e göre:
- Her ürün için negatif stok kontrol kuralları tutarlı şekilde uygulanmalı

Hypothesis kütüphanesi kullanılarak yazılmıştır.
"""

import pytest
from decimal import Decimal
from hypothesis import given, strategies as st, settings, assume

from sontechsp.uygulama.moduller.stok.servisler.negatif_stok_kontrol import NegatifStokKontrol
from sontechsp.uygulama.moduller.stok.hatalar.stok_hatalari import NegatifStokError


class TestNegatifStokTutarlılığıProperty:
    """Negatif stok tutarlılığı property testleri"""

    @given(
        urun_id=st.integers(min_value=1, max_value=1000),
        mevcut_stok=st.decimals(min_value=Decimal("-10"), max_value=Decimal("100"), places=4),
        talep_miktar=st.decimals(min_value=Decimal("0.0001"), max_value=Decimal("50"), places=4),
    )
    @settings(max_examples=100, deadline=10000)
    def test_property_negatif_stok_tutarlılığı(self, urun_id, mevcut_stok, talep_miktar):
        """
        **Feature: test-stabilizasyon-paketi, Property 6: Negatif stok tutarlılığı**
        **Validates: Requirements 2.4**

        For any ürün, negatif stok kontrol kuralları tutarlı şekilde uygulanmalı
        """
        kontrol = NegatifStokKontrol()

        # Sonuç stok seviyesini hesapla
        sonuc_stok = mevcut_stok - talep_miktar

        # Aynı ürün için aynı stok seviyesinde iki kez kontrol yap
        try:
            izin_1 = kontrol.kontrol_yap(urun_id, talep_miktar, mevcut_stok)
        except NegatifStokError:
            izin_1 = False

        try:
            izin_2 = kontrol.kontrol_yap(urun_id, talep_miktar, mevcut_stok)
        except NegatifStokError:
            izin_2 = False

        # İki sonuç aynı olmalı (tutarlılık)
        assert (
            izin_1 == izin_2
        ), f"Ürün {urun_id} için aynı stok seviyesinde ({sonuc_stok}) farklı sonuçlar: {izin_1} vs {izin_2}"

    @given(
        urun_id=st.integers(min_value=1, max_value=100),
        ozel_limit=st.decimals(min_value=Decimal("-20"), max_value=Decimal("-1"), places=4),
    )
    @settings(max_examples=100)
    def test_property_urun_bazlı_limit_tutarlılığı(self, urun_id, ozel_limit):
        """
        **Feature: test-stabilizasyon-paketi, Property 6: Negatif stok tutarlılığı**
        **Validates: Requirements 2.4**

        For any ürün with custom limit, that limit should be consistently applied
        """
        kontrol = NegatifStokKontrol()

        # Ürün için özel limit belirle
        kontrol.limit_belirle(urun_id, ozel_limit)

        # Limitin hemen üstünde bir talep
        mevcut_stok = Decimal("0")
        talep_miktar = abs(ozel_limit) - Decimal("0.0001")

        # Birden fazla kez kontrol yap - hepsi aynı sonucu vermeli
        sonuclar = []
        for _ in range(3):
            try:
                izin = kontrol.kontrol_yap(urun_id, talep_miktar, mevcut_stok)
                sonuclar.append(izin)
            except NegatifStokError:
                sonuclar.append(False)

        # Tüm sonuçlar aynı olmalı
        assert len(set(sonuclar)) == 1, f"Ürün {urun_id} için özel limit ({ozel_limit}) tutarsız sonuçlar: {sonuclar}"
        assert all(sonuclar), f"Özel limit ({ozel_limit}) içinde kalıyorsa her zaman izin verilmeli"

    @given(urun_id=st.integers(min_value=1, max_value=100))
    @settings(max_examples=100)
    def test_property_varsayılan_limit_tutarlılığı(self, urun_id):
        """
        **Feature: test-stabilizasyon-paketi, Property 6: Negatif stok tutarlılığı**
        **Validates: Requirements 2.4**

        For any ürün without custom limit, default limit should be consistently applied
        """
        kontrol = NegatifStokKontrol()

        # Varsayılan limitin tam sınırında test
        mevcut_stok = Decimal("0")
        talep_miktar = Decimal("5")  # Sonuç: -5 (varsayılan limit)

        # Birden fazla kez kontrol yap - hepsi aynı sonucu vermeli
        sonuclar = []
        for _ in range(3):
            try:
                izin = kontrol.kontrol_yap(urun_id, talep_miktar, mevcut_stok)
                sonuclar.append(izin)
            except NegatifStokError:
                sonuclar.append(False)

        # Tüm sonuçlar aynı olmalı
        assert len(set(sonuclar)) == 1, f"Ürün {urun_id} için varsayılan limit tutarsız sonuçlar: {sonuclar}"
        assert all(sonuclar), "Varsayılan limit (-5) sınırında izin verilmeli"

    @given(
        urun_id_1=st.integers(min_value=1, max_value=50),
        urun_id_2=st.integers(min_value=51, max_value=100),
        stok_seviyesi=st.decimals(min_value=Decimal("-4"), max_value=Decimal("-1"), places=4),
    )
    @settings(max_examples=100)
    def test_property_farklı_urunler_aynı_kurallar(self, urun_id_1, urun_id_2, stok_seviyesi):
        """
        **Feature: test-stabilizasyon-paketi, Property 6: Negatif stok tutarlılığı**
        **Validates: Requirements 2.4**

        For any two different products without custom limits, same rules should apply
        """
        kontrol = NegatifStokKontrol()

        # Aynı stok seviyesinde iki farklı ürün için kontrol yap
        mevcut_stok = Decimal("0")
        talep_miktar = abs(stok_seviyesi)

        try:
            izin_1 = kontrol.kontrol_yap(urun_id_1, talep_miktar, mevcut_stok)
        except NegatifStokError:
            izin_1 = False

        try:
            izin_2 = kontrol.kontrol_yap(urun_id_2, talep_miktar, mevcut_stok)
        except NegatifStokError:
            izin_2 = False

        # İki ürün için aynı sonuç olmalı (özel limit yoksa)
        assert (
            izin_1 == izin_2
        ), f"Farklı ürünler ({urun_id_1}, {urun_id_2}) için aynı stok seviyesinde ({stok_seviyesi}) farklı sonuçlar"

    @given(
        urun_id=st.integers(min_value=1, max_value=100),
        limit_1=st.decimals(min_value=Decimal("-20"), max_value=Decimal("-10"), places=4),
        limit_2=st.decimals(min_value=Decimal("-9"), max_value=Decimal("-1"), places=4),
    )
    @settings(max_examples=100)
    def test_property_limit_değişikliği_tutarlılığı(self, urun_id, limit_1, limit_2):
        """
        **Feature: test-stabilizasyon-paketi, Property 6: Negatif stok tutarlılığı**
        **Validates: Requirements 2.4**

        For any ürün, when limit changes, new limit should be consistently applied
        """
        kontrol = NegatifStokKontrol()

        # İlk limit belirle
        kontrol.limit_belirle(urun_id, limit_1)

        # İlk limitin hemen üstünde test
        mevcut_stok = Decimal("0")
        talep_miktar = abs(limit_1) - Decimal("0.0001")

        try:
            izin_1 = kontrol.kontrol_yap(urun_id, talep_miktar, mevcut_stok)
        except NegatifStokError:
            izin_1 = False

        # Limit değiştir
        kontrol.limit_belirle(urun_id, limit_2)

        # Aynı talep ile tekrar test
        try:
            izin_2 = kontrol.kontrol_yap(urun_id, talep_miktar, mevcut_stok)
        except NegatifStokError:
            izin_2 = False

        # Sonuçlar farklı olabilir (limit değişti)
        # Ama her limit için tutarlı olmalı
        sonuc_stok = mevcut_stok - talep_miktar

        if sonuc_stok >= limit_1:
            assert izin_1 is True, f"İlk limit ({limit_1}) içinde izin verilmeliydi"

        if sonuc_stok >= limit_2:
            assert izin_2 is True, f"İkinci limit ({limit_2}) içinde izin verilmeliydi"
        else:
            assert izin_2 is False, f"İkinci limit ({limit_2}) dışında işlem engellenmeliydi"
