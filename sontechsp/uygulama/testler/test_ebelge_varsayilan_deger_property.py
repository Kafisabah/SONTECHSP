# Version: 0.1.0
# Last Update: 2024-12-17
# Module: test_ebelge_varsayilan_deger_property
# Description: E-belge varsayılan değer property testleri
# Changelog:
# - İlk versiyon: Varsayılan değer property testleri eklendi

import pytest
from hypothesis import given, strategies as st
from decimal import Decimal
from typing import Dict, Any

from sontechsp.uygulama.moduller.ebelge.dto import EBelgeOlusturDTO
from sontechsp.uygulama.moduller.ebelge.sabitler import (
    BelgeTuru,
    KaynakTuru,
    DEFAULT_CURRENCY
)


class TestVarsayilanDegerProperty:
    """
    **Feature: ebelge-yonetim-altyapisi, Property 3: Varsayılan değer atama**
    **Validates: Requirements 1.5**
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
    def test_default_currency_assignment(
        self, kaynak_turu: str, kaynak_id: int, belge_turu: str,
        musteri_ad: str, vergi_no: str, toplam_tutar: Decimal, belge_json: Dict[str, Any]
    ):
        """Para birimi belirtilmediğinde varsayılan olarak TRY atanmalı"""
        # Para birimi belirtmeden DTO oluştur
        dto = EBelgeOlusturDTO(
            kaynak_turu=kaynak_turu,
            kaynak_id=kaynak_id,
            belge_turu=belge_turu,
            musteri_ad=musteri_ad,
            vergi_no=vergi_no,
            toplam_tutar=toplam_tutar,
            belge_json=belge_json
            # para_birimi parametresi belirtilmedi
        )
        
        # Varsayılan değer atanmış olmalı
        assert dto.para_birimi == DEFAULT_CURRENCY
        assert dto.para_birimi == "TRY"

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
        ),
        para_birimi=st.sampled_from(["USD", "EUR", "GBP", "TRY"])
    )
    def test_explicit_currency_assignment(
        self, kaynak_turu: str, kaynak_id: int, belge_turu: str,
        musteri_ad: str, vergi_no: str, toplam_tutar: Decimal, 
        belge_json: Dict[str, Any], para_birimi: str
    ):
        """Para birimi açıkça belirtildiğinde o değer kullanılmalı"""
        # Para birimi belirterek DTO oluştur
        dto = EBelgeOlusturDTO(
            kaynak_turu=kaynak_turu,
            kaynak_id=kaynak_id,
            belge_turu=belge_turu,
            musteri_ad=musteri_ad,
            vergi_no=vergi_no,
            toplam_tutar=toplam_tutar,
            belge_json=belge_json,
            para_birimi=para_birimi
        )
        
        # Belirtilen değer kullanılmış olmalı
        assert dto.para_birimi == para_birimi

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
        ),
        aciklama=st.one_of(st.none(), st.text(min_size=1, max_size=500))
    )
    def test_optional_fields_default_values(
        self, kaynak_turu: str, kaynak_id: int, belge_turu: str,
        musteri_ad: str, vergi_no: str, toplam_tutar: Decimal, 
        belge_json: Dict[str, Any], aciklama: str
    ):
        """İsteğe bağlı alanlar için varsayılan değerler doğru atanmalı"""
        dto = EBelgeOlusturDTO(
            kaynak_turu=kaynak_turu,
            kaynak_id=kaynak_id,
            belge_turu=belge_turu,
            musteri_ad=musteri_ad,
            vergi_no=vergi_no,
            toplam_tutar=toplam_tutar,
            belge_json=belge_json,
            aciklama=aciklama
        )
        
        # Para birimi varsayılan değer almalı
        assert dto.para_birimi == DEFAULT_CURRENCY
        # Açıklama belirtilen değer olmalı (None dahil)
        assert dto.aciklama == aciklama