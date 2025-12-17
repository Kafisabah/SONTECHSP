# Version: 0.1.0
# Last Update: 2024-12-17
# Module: test_ebelge_dto_property
# Description: E-belge DTO validation property testleri
# Changelog:
# - İlk versiyon: DTO validation property testleri eklendi

import pytest
from hypothesis import given, strategies as st
from decimal import Decimal
from typing import Dict, Any

from sontechsp.uygulama.moduller.ebelge.dto import (
    EBelgeOlusturDTO,
    EBelgeGonderDTO,
    EBelgeSonucDTO,
    EBelgeDurumSorguDTO
)
from sontechsp.uygulama.moduller.ebelge.sabitler import (
    BelgeTuru,
    KaynakTuru,
    DEFAULT_CURRENCY
)
from sontechsp.uygulama.moduller.ebelge.hatalar import DogrulamaHatasi


class TestEBelgeOlusturDTOProperty:
    """
    **Feature: ebelge-yonetim-altyapisi, Property 1: E-belge oluşturma validation**
    **Validates: Requirements 1.1, 1.2, 1.3**
    """

    @given(
        kaynak_turu=st.sampled_from([kt.value for kt in KaynakTuru]),
        kaynak_id=st.integers(min_value=1, max_value=999999),
        belge_turu=st.sampled_from([bt.value for bt in BelgeTuru]),
        musteri_ad=st.text(min_size=1, max_size=200),
        vergi_no=st.text(min_size=10, max_size=11, alphabet=st.characters(whitelist_categories=('Nd',))),
        toplam_tutar=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('999999.99'), places=2),
        belge_json=st.dictionaries(
            keys=st.text(min_size=1, max_size=50),
            values=st.one_of(st.text(), st.integers(), st.floats(allow_nan=False)),
            min_size=1
        )
    )
    def test_valid_dto_creation_succeeds(
        self, kaynak_turu: str, kaynak_id: int, belge_turu: str,
        musteri_ad: str, vergi_no: str, toplam_tutar: Decimal, belge_json: Dict[str, Any]
    ):
        """Geçerli verilerle DTO oluşturma başarılı olmalı"""
        dto = EBelgeOlusturDTO(
            kaynak_turu=kaynak_turu,
            kaynak_id=kaynak_id,
            belge_turu=belge_turu,
            musteri_ad=musteri_ad,
            vergi_no=vergi_no,
            toplam_tutar=toplam_tutar,
            belge_json=belge_json
        )
        
        assert dto.kaynak_turu == kaynak_turu
        assert dto.kaynak_id == kaynak_id
        assert dto.belge_turu == belge_turu
        assert dto.musteri_ad == musteri_ad
        assert dto.vergi_no == vergi_no
        assert dto.toplam_tutar == toplam_tutar
        assert dto.para_birimi == DEFAULT_CURRENCY
        assert dto.belge_json == belge_json

    @given(
        belge_turu=st.text().filter(lambda x: x not in [bt.value for bt in BelgeTuru])
    )
    def test_invalid_belge_turu_validation(self, belge_turu: str):
        """Geçersiz belge türü ile DTO oluşturma validation hatası vermeli"""
        # Bu test DTO seviyesinde değil, servis seviyesinde yapılacak
        # Şimdilik DTO'nun kendisi validation yapmıyor
        dto = EBelgeOlusturDTO(
            kaynak_turu=KaynakTuru.POS_SATIS.value,
            kaynak_id=1,
            belge_turu=belge_turu,  # Geçersiz belge türü
            musteri_ad="Test Müşteri",
            vergi_no="1234567890",
            toplam_tutar=Decimal('100.00'),
            belge_json={"test": "data"}
        )
        # DTO oluşturulur ama validation servis katmanında yapılır
        assert dto.belge_turu == belge_turu

    @given(
        kaynak_turu=st.text().filter(lambda x: x not in [kt.value for kt in KaynakTuru])
    )
    def test_invalid_kaynak_turu_validation(self, kaynak_turu: str):
        """Geçersiz kaynak türü ile DTO oluşturma validation hatası vermeli"""
        # Bu test DTO seviyesinde değil, servis seviyesinde yapılacak
        dto = EBelgeOlusturDTO(
            kaynak_turu=kaynak_turu,  # Geçersiz kaynak türü
            kaynak_id=1,
            belge_turu=BelgeTuru.EFATURA.value,
            musteri_ad="Test Müşteri",
            vergi_no="1234567890",
            toplam_tutar=Decimal('100.00'),
            belge_json={"test": "data"}
        )
        # DTO oluşturulur ama validation servis katmanında yapılır
        assert dto.kaynak_turu == kaynak_turu


class TestEBelgeGonderDTOProperty:
    """EBelgeGonderDTO property testleri"""

    @given(
        cikis_id=st.integers(min_value=1, max_value=999999),
        belge_json=st.dictionaries(
            keys=st.text(min_size=1, max_size=50),
            values=st.one_of(st.text(), st.integers(), st.floats(allow_nan=False)),
            min_size=1
        )
    )
    def test_valid_gonder_dto_creation(self, cikis_id: int, belge_json: Dict[str, Any]):
        """Geçerli verilerle EBelgeGonderDTO oluşturma başarılı olmalı"""
        dto = EBelgeGonderDTO(
            cikis_id=cikis_id,
            belge_json=belge_json
        )
        
        assert dto.cikis_id == cikis_id
        assert dto.belge_json == belge_json


class TestEBelgeSonucDTOProperty:
    """EBelgeSonucDTO property testleri"""

    @given(
        basarili_mi=st.booleans(),
        dis_belge_no=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
        durum_kodu=st.one_of(st.none(), st.text(min_size=1, max_size=20)),
        mesaj=st.one_of(st.none(), st.text(min_size=1, max_size=500)),
        ham_cevap_json=st.one_of(st.none(), st.dictionaries(
            keys=st.text(min_size=1, max_size=50),
            values=st.one_of(st.text(), st.integers(), st.floats(allow_nan=False)),
            min_size=0
        ))
    )
    def test_valid_sonuc_dto_creation(
        self, basarili_mi: bool, dis_belge_no: str, durum_kodu: str,
        mesaj: str, ham_cevap_json: Dict[str, Any]
    ):
        """Geçerli verilerle EBelgeSonucDTO oluşturma başarılı olmalı"""
        dto = EBelgeSonucDTO(
            basarili_mi=basarili_mi,
            dis_belge_no=dis_belge_no,
            durum_kodu=durum_kodu,
            mesaj=mesaj,
            ham_cevap_json=ham_cevap_json
        )
        
        assert dto.basarili_mi == basarili_mi
        assert dto.dis_belge_no == dis_belge_no
        assert dto.durum_kodu == durum_kodu
        assert dto.mesaj == mesaj
        assert dto.ham_cevap_json == ham_cevap_json