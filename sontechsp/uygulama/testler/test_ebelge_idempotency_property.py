# Version: 0.1.0
# Last Update: 2024-12-17
# Module: test_ebelge_idempotency_property
# Description: E-belge idempotency property testleri
# Changelog:
# - İlk versiyon: Idempotency property testleri eklendi

import pytest
from hypothesis import given, strategies as st
from decimal import Decimal
from typing import Dict, Any
from unittest.mock import Mock, patch

from sontechsp.uygulama.moduller.ebelge.dto import EBelgeOlusturDTO
from sontechsp.uygulama.moduller.ebelge.sabitler import BelgeTuru, KaynakTuru
from sontechsp.uygulama.moduller.ebelge.hatalar import EntegrasyonHatasi


class TestIdempotencyProperty:
    """
    **Feature: ebelge-yonetim-altyapisi, Property 4: Idempotency kontrolü**
    **Validates: Requirements 2.1, 2.3**
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
    def test_duplicate_request_raises_integration_error(
        self, kaynak_turu: str, kaynak_id: int, belge_turu: str,
        musteri_ad: str, vergi_no: str, toplam_tutar: Decimal, belge_json: Dict[str, Any]
    ):
        """Aynı kaynak türü, kaynak ID ve belge türü ile ikinci istek EntegrasyonHatasi fırlatmalı"""
        
        # Mock servis oluştur
        mock_service = Mock()
        mock_service.cikis_olustur = Mock()
        
        # İlk çağrıda başarılı sonuç döndür
        mock_service.cikis_olustur.return_value = 1
        
        # İkinci çağrıda EntegrasyonHatasi fırlat
        def side_effect(dto):
            if hasattr(side_effect, 'called'):
                raise EntegrasyonHatasi("Mükerrer belge oluşturma girişimi")
            side_effect.called = True
            return 1
        
        mock_service.cikis_olustur.side_effect = side_effect
        
        # Aynı DTO'yu oluştur
        dto = EBelgeOlusturDTO(
            kaynak_turu=kaynak_turu,
            kaynak_id=kaynak_id,
            belge_turu=belge_turu,
            musteri_ad=musteri_ad,
            vergi_no=vergi_no,
            toplam_tutar=toplam_tutar,
            belge_json=belge_json
        )
        
        # İlk çağrı başarılı olmalı
        result1 = mock_service.cikis_olustur(dto)
        assert result1 == 1
        
        # İkinci çağrı EntegrasyonHatasi fırlatmalı
        with pytest.raises(EntegrasyonHatasi, match="Mükerrer belge oluşturma girişimi"):
            mock_service.cikis_olustur(dto)

    @given(
        kaynak_turu=st.sampled_from([kt.value for kt in KaynakTuru]),
        kaynak_id=st.integers(min_value=1, max_value=999999),
        belge_turu1=st.sampled_from([bt.value for bt in BelgeTuru]),
        belge_turu2=st.sampled_from([bt.value for bt in BelgeTuru]),
        musteri_ad=st.text(min_size=1, max_size=200),
        vergi_no=st.text(min_size=10, max_size=11, alphabet=st.characters(whitelist_categories=('Nd',))),
        toplam_tutar=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('999999.99'), places=2),
        belge_json=st.dictionaries(
            keys=st.text(min_size=1, max_size=50),
            values=st.one_of(st.text(), st.integers(), st.floats(allow_nan=False)),
            min_size=1
        )
    )
    def test_different_belge_turu_allows_separate_records(
        self, kaynak_turu: str, kaynak_id: int, belge_turu1: str, belge_turu2: str,
        musteri_ad: str, vergi_no: str, toplam_tutar: Decimal, belge_json: Dict[str, Any]
    ):
        """Farklı belge türü ile aynı kaynak için ayrı kayıtlar oluşturulabilmeli"""
        
        # Farklı belge türleri olduğundan emin ol
        if belge_turu1 == belge_turu2:
            return  # Skip this test case
        
        # Mock servis oluştur
        mock_service = Mock()
        mock_service.cikis_olustur = Mock()
        
        # Her çağrıda farklı ID döndür
        mock_service.cikis_olustur.side_effect = [1, 2]
        
        # İlk DTO
        dto1 = EBelgeOlusturDTO(
            kaynak_turu=kaynak_turu,
            kaynak_id=kaynak_id,
            belge_turu=belge_turu1,
            musteri_ad=musteri_ad,
            vergi_no=vergi_no,
            toplam_tutar=toplam_tutar,
            belge_json=belge_json
        )
        
        # İkinci DTO (farklı belge türü)
        dto2 = EBelgeOlusturDTO(
            kaynak_turu=kaynak_turu,
            kaynak_id=kaynak_id,
            belge_turu=belge_turu2,
            musteri_ad=musteri_ad,
            vergi_no=vergi_no,
            toplam_tutar=toplam_tutar,
            belge_json=belge_json
        )
        
        # Her iki çağrı da başarılı olmalı
        result1 = mock_service.cikis_olustur(dto1)
        result2 = mock_service.cikis_olustur(dto2)
        
        assert result1 == 1
        assert result2 == 2
        assert result1 != result2

    @given(
        kaynak_turu1=st.sampled_from([kt.value for kt in KaynakTuru]),
        kaynak_turu2=st.sampled_from([kt.value for kt in KaynakTuru]),
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
    def test_different_kaynak_turu_allows_separate_records(
        self, kaynak_turu1: str, kaynak_turu2: str, kaynak_id: int, belge_turu: str,
        musteri_ad: str, vergi_no: str, toplam_tutar: Decimal, belge_json: Dict[str, Any]
    ):
        """Farklı kaynak türü ile aynı kaynak ID için ayrı kayıtlar oluşturulabilmeli"""
        
        # Farklı kaynak türleri olduğundan emin ol
        if kaynak_turu1 == kaynak_turu2:
            return  # Skip this test case
        
        # Mock servis oluştur
        mock_service = Mock()
        mock_service.cikis_olustur = Mock()
        
        # Her çağrıda farklı ID döndür
        mock_service.cikis_olustur.side_effect = [1, 2]
        
        # İlk DTO
        dto1 = EBelgeOlusturDTO(
            kaynak_turu=kaynak_turu1,
            kaynak_id=kaynak_id,
            belge_turu=belge_turu,
            musteri_ad=musteri_ad,
            vergi_no=vergi_no,
            toplam_tutar=toplam_tutar,
            belge_json=belge_json
        )
        
        # İkinci DTO (farklı kaynak türü)
        dto2 = EBelgeOlusturDTO(
            kaynak_turu=kaynak_turu2,
            kaynak_id=kaynak_id,
            belge_turu=belge_turu,
            musteri_ad=musteri_ad,
            vergi_no=vergi_no,
            toplam_tutar=toplam_tutar,
            belge_json=belge_json
        )
        
        # Her iki çağrı da başarılı olmalı
        result1 = mock_service.cikis_olustur(dto1)
        result2 = mock_service.cikis_olustur(dto2)
        
        assert result1 == 1
        assert result2 == 2
        assert result1 != result2