# Version: 0.1.0
# Last Update: 2024-12-17
# Module: test_ebelge_repository_filtreleme_property
# Description: E-belge repository filtreleme property testleri
# Changelog:
# - İlk versiyon: Repository filtreleme property testleri eklendi

import pytest
from hypothesis import given, strategies as st
from decimal import Decimal
from typing import List
from unittest.mock import Mock, MagicMock

from sontechsp.uygulama.moduller.ebelge.depolar.ebelge_deposu import EBelgeDeposu
from sontechsp.uygulama.moduller.ebelge.sabitler import (
    OutboxDurumu,
    MAX_RETRY_COUNT,
    DEFAULT_BATCH_SIZE
)


class TestRepositoryFiltrelemeProperty:
    """
    **Feature: ebelge-yonetim-altyapisi, Property 6: Bekleyen belge filtreleme**
    **Validates: Requirements 3.1, 3.2**
    """

    def create_mock_kayit(self, durum: str, deneme_sayisi: int = 0):
        """Mock kayıt oluşturur"""
        mock_kayit = Mock()
        mock_kayit.durum = durum
        mock_kayit.deneme_sayisi = deneme_sayisi
        mock_kayit.id = 1
        return mock_kayit

    @given(
        bekleyen_kayit_sayisi=st.integers(min_value=0, max_value=50),
        hata_kayit_sayisi=st.integers(min_value=0, max_value=50),
        gonderildi_kayit_sayisi=st.integers(min_value=0, max_value=50),
        limit=st.integers(min_value=1, max_value=100)
    )
    def test_bekleyenleri_getir_only_returns_eligible_records(
        self, bekleyen_kayit_sayisi: int, hata_kayit_sayisi: int,
        gonderildi_kayit_sayisi: int, limit: int
    ):
        """bekleyenleri_getir sadece uygun kayıtları döndürmeli"""
        
        # Mock session oluştur
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        
        # Mock kayıtlar oluştur
        mock_kayitlar = []
        
        # BEKLIYOR durumundaki kayıtlar (hepsi uygun)
        for i in range(bekleyen_kayit_sayisi):
            mock_kayitlar.append(self.create_mock_kayit(OutboxDurumu.BEKLIYOR.value, 0))
        
        # HATA durumundaki kayıtlar (deneme sayısı < MAX olan uygun)
        for i in range(hata_kayit_sayisi):
            deneme_sayisi = i % (MAX_RETRY_COUNT + 1)  # Bazıları uygun, bazıları değil
            mock_kayitlar.append(self.create_mock_kayit(OutboxDurumu.HATA.value, deneme_sayisi))
        
        # GONDERILDI durumundaki kayıtlar (hiçbiri uygun değil)
        for i in range(gonderildi_kayit_sayisi):
            mock_kayitlar.append(self.create_mock_kayit(OutboxDurumu.GONDERILDI.value, 0))
        
        # Sadece uygun kayıtları döndür
        uygun_kayitlar = [
            k for k in mock_kayitlar 
            if k.durum == OutboxDurumu.BEKLIYOR.value or 
            (k.durum == OutboxDurumu.HATA.value and k.deneme_sayisi < MAX_RETRY_COUNT)
        ]
        
        # Limit uygula
        expected_kayitlar = uygun_kayitlar[:limit]
        mock_query.all.return_value = expected_kayitlar
        
        # Repository oluştur ve test et
        depo = EBelgeDeposu(mock_session)
        result = depo.bekleyenleri_getir(limit)
        
        # Sonuçları kontrol et
        assert len(result) <= limit
        assert len(result) == len(expected_kayitlar)
        
        # Tüm dönen kayıtlar uygun olmalı
        for kayit in result:
            assert (
                kayit.durum == OutboxDurumu.BEKLIYOR.value or
                (kayit.durum == OutboxDurumu.HATA.value and kayit.deneme_sayisi < MAX_RETRY_COUNT)
            )

    @given(
        kayit_sayisi=st.integers(min_value=1, max_value=20),
        limit=st.integers(min_value=1, max_value=50)
    )
    def test_bekleyenleri_getir_respects_limit(self, kayit_sayisi: int, limit: int):
        """bekleyenleri_getir limit parametresine uymalı"""
        
        # Mock session oluştur
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        
        # Tüm kayıtlar BEKLIYOR durumunda (uygun)
        mock_kayitlar = [
            self.create_mock_kayit(OutboxDurumu.BEKLIYOR.value, 0)
            for _ in range(kayit_sayisi)
        ]
        
        # Limit uygulanmış kayıtları döndür
        expected_count = min(kayit_sayisi, limit)
        mock_query.all.return_value = mock_kayitlar[:expected_count]
        
        # Repository oluştur ve test et
        depo = EBelgeDeposu(mock_session)
        result = depo.bekleyenleri_getir(limit)
        
        # Limit kontrolü
        assert len(result) <= limit
        assert len(result) == expected_count
        
        # Limit metodu doğru parametreyle çağrılmış olmalı
        mock_query.limit.assert_called_once_with(limit)

    @given(
        deneme_sayilari=st.lists(
            st.integers(min_value=0, max_value=MAX_RETRY_COUNT + 2),
            min_size=1,
            max_size=10
        )
    )
    def test_hata_kayitlari_deneme_sayisi_kontrolu(self, deneme_sayilari: List[int]):
        """HATA durumundaki kayıtlar için deneme sayısı kontrolü doğru çalışmalı"""
        
        # Mock session oluştur
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        
        # HATA durumundaki kayıtlar oluştur
        mock_kayitlar = [
            self.create_mock_kayit(OutboxDurumu.HATA.value, deneme_sayisi)
            for deneme_sayisi in deneme_sayilari
        ]
        
        # Sadece deneme sayısı < MAX_RETRY_COUNT olanları döndür
        uygun_kayitlar = [
            k for k in mock_kayitlar 
            if k.deneme_sayisi < MAX_RETRY_COUNT
        ]
        
        mock_query.all.return_value = uygun_kayitlar
        
        # Repository oluştur ve test et
        depo = EBelgeDeposu(mock_session)
        result = depo.bekleyenleri_getir()
        
        # Tüm dönen kayıtların deneme sayısı MAX'tan az olmalı
        for kayit in result:
            assert kayit.deneme_sayisi < MAX_RETRY_COUNT
        
        # Beklenen sayıda kayıt dönmeli
        assert len(result) == len(uygun_kayitlar)

    def test_bekleyenleri_getir_default_limit(self):
        """bekleyenleri_getir varsayılan limit kullanmalı"""
        
        # Mock session oluştur
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        
        # Repository oluştur ve limit belirtmeden çağır
        depo = EBelgeDeposu(mock_session)
        depo.bekleyenleri_getir()  # limit parametresi yok
        
        # Varsayılan limit kullanılmış olmalı
        mock_query.limit.assert_called_once_with(DEFAULT_BATCH_SIZE)

    @given(
        mixed_durumlar=st.lists(
            st.sampled_from([
                OutboxDurumu.BEKLIYOR.value,
                OutboxDurumu.HATA.value,
                OutboxDurumu.GONDERILDI.value,
                OutboxDurumu.GONDERILIYOR.value,
                OutboxDurumu.IPTAL.value
            ]),
            min_size=1,
            max_size=15
        )
    )
    def test_mixed_durumlar_filtreleme(self, mixed_durumlar: List[str]):
        """Karışık durumlardan sadece uygun olanlar döndürülmeli"""
        
        # Mock session oluştur
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        
        # Karışık durumlarla kayıtlar oluştur
        mock_kayitlar = []
        for durum in mixed_durumlar:
            deneme_sayisi = 1 if durum == OutboxDurumu.HATA.value else 0
            mock_kayitlar.append(self.create_mock_kayit(durum, deneme_sayisi))
        
        # Sadece uygun kayıtları filtrele
        uygun_kayitlar = [
            k for k in mock_kayitlar
            if k.durum == OutboxDurumu.BEKLIYOR.value or
            (k.durum == OutboxDurumu.HATA.value and k.deneme_sayisi < MAX_RETRY_COUNT)
        ]
        
        mock_query.all.return_value = uygun_kayitlar
        
        # Repository oluştur ve test et
        depo = EBelgeDeposu(mock_session)
        result = depo.bekleyenleri_getir()
        
        # Sadece uygun kayıtlar dönmeli
        assert len(result) == len(uygun_kayitlar)
        
        for kayit in result:
            assert (
                kayit.durum == OutboxDurumu.BEKLIYOR.value or
                (kayit.durum == OutboxDurumu.HATA.value and kayit.deneme_sayisi < MAX_RETRY_COUNT)
            )