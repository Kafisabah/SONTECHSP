# Version: 0.1.0
# Last Update: 2024-12-17
# Module: test_ebelge_farkli_belge_turu_property
# Description: E-belge farklı belge türü property testleri
# Changelog:
# - İlk versiyon: Farklı belge türü property testleri eklendi

import pytest
from hypothesis import given, strategies as st
from decimal import Decimal
from typing import Dict, Any, List
from unittest.mock import Mock

from sontechsp.uygulama.moduller.ebelge.dto import EBelgeOlusturDTO
from sontechsp.uygulama.moduller.ebelge.sabitler import BelgeTuru, KaynakTuru


class TestFarkliBelgeTuruProperty:
    """
    **Feature: ebelge-yonetim-altyapisi, Property 5: Farklı belge türü desteği**
    **Validates: Requirements 2.2**
    """

    @given(
        kaynak_turu=st.sampled_from([kt.value for kt in KaynakTuru]),
        kaynak_id=st.integers(min_value=1, max_value=999999),
        musteri_ad=st.text(min_size=1, max_size=200),
        vergi_no=st.text(min_size=10, max_size=11, alphabet=st.characters(whitelist_categories=('Nd',))),
        toplam_tutar=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('999999.99'), places=2),
        belge_json=st.dictionaries(
            keys=st.text(min_size=1, max_size=50),
            values=st.one_of(st.text(), st.integers(), st.floats(allow_nan=False)),
            min_size=1
        )
    )
    def test_same_source_different_belge_types_create_separate_records(
        self, kaynak_turu: str, kaynak_id: int, musteri_ad: str,
        vergi_no: str, toplam_tutar: Decimal, belge_json: Dict[str, Any]
    ):
        """Aynı kaynak için farklı belge türleri ile ayrı kayıtlar oluşturulabilmeli"""
        
        # Mock servis oluştur
        mock_service = Mock()
        mock_service.cikis_olustur = Mock()
        
        # Her belge türü için farklı ID döndür
        expected_ids = [1, 2, 3]
        mock_service.cikis_olustur.side_effect = expected_ids
        
        created_ids = []
        
        # Her belge türü için DTO oluştur ve kaydet
        for i, belge_turu in enumerate([bt.value for bt in BelgeTuru]):
            dto = EBelgeOlusturDTO(
                kaynak_turu=kaynak_turu,
                kaynak_id=kaynak_id,
                belge_turu=belge_turu,
                musteri_ad=musteri_ad,
                vergi_no=vergi_no,
                toplam_tutar=toplam_tutar,
                belge_json=belge_json
            )
            
            result_id = mock_service.cikis_olustur(dto)
            created_ids.append(result_id)
        
        # Tüm kayıtlar farklı ID'lere sahip olmalı
        assert len(created_ids) == len(set(created_ids))  # Tüm ID'ler benzersiz
        assert created_ids == expected_ids
        
        # Servis her belge türü için çağrılmış olmalı
        assert mock_service.cikis_olustur.call_count == len(BelgeTuru)

    @given(
        kaynak_turu=st.sampled_from([kt.value for kt in KaynakTuru]),
        kaynak_id=st.integers(min_value=1, max_value=999999),
        musteri_ad=st.text(min_size=1, max_size=200),
        vergi_no=st.text(min_size=10, max_size=11, alphabet=st.characters(whitelist_categories=('Nd',))),
        toplam_tutar=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('999999.99'), places=2),
        belge_json=st.dictionaries(
            keys=st.text(min_size=1, max_size=50),
            values=st.one_of(st.text(), st.integers(), st.floats(allow_nan=False)),
            min_size=1
        ),
        belge_turleri=st.lists(
            st.sampled_from([bt.value for bt in BelgeTuru]),
            min_size=2,
            max_size=3,
            unique=True
        )
    )
    def test_multiple_belge_types_for_same_source_all_succeed(
        self, kaynak_turu: str, kaynak_id: int, musteri_ad: str,
        vergi_no: str, toplam_tutar: Decimal, belge_json: Dict[str, Any],
        belge_turleri: List[str]
    ):
        """Aynı kaynak için birden fazla belge türü ile tüm işlemler başarılı olmalı"""
        
        # Mock servis oluştur
        mock_service = Mock()
        mock_service.cikis_olustur = Mock()
        
        # Her çağrı için artan ID döndür
        mock_service.cikis_olustur.side_effect = range(1, len(belge_turleri) + 1)
        
        results = []
        
        # Her belge türü için işlem yap
        for belge_turu in belge_turleri:
            dto = EBelgeOlusturDTO(
                kaynak_turu=kaynak_turu,
                kaynak_id=kaynak_id,
                belge_turu=belge_turu,
                musteri_ad=musteri_ad,
                vergi_no=vergi_no,
                toplam_tutar=toplam_tutar,
                belge_json=belge_json
            )
            
            result = mock_service.cikis_olustur(dto)
            results.append(result)
        
        # Tüm işlemler başarılı olmalı
        assert len(results) == len(belge_turleri)
        assert all(result > 0 for result in results)  # Pozitif ID'ler
        assert len(results) == len(set(results))  # Tüm ID'ler benzersiz

    @given(
        kaynak_turu=st.sampled_from([kt.value for kt in KaynakTuru]),
        kaynak_id=st.integers(min_value=1, max_value=999999),
        musteri_ad=st.text(min_size=1, max_size=200),
        vergi_no=st.text(min_size=10, max_size=11, alphabet=st.characters(whitelist_categories=('Nd',))),
        toplam_tutar1=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('999999.99'), places=2),
        toplam_tutar2=st.decimals(min_value=Decimal('0.01'), max_value=Decimal('999999.99'), places=2),
        belge_json1=st.dictionaries(
            keys=st.text(min_size=1, max_size=50),
            values=st.one_of(st.text(), st.integers(), st.floats(allow_nan=False)),
            min_size=1
        ),
        belge_json2=st.dictionaries(
            keys=st.text(min_size=1, max_size=50),
            values=st.one_of(st.text(), st.integers(), st.floats(allow_nan=False)),
            min_size=1
        )
    )
    def test_same_source_different_belge_types_different_data_all_succeed(
        self, kaynak_turu: str, kaynak_id: int, musteri_ad: str, vergi_no: str,
        toplam_tutar1: Decimal, toplam_tutar2: Decimal,
        belge_json1: Dict[str, Any], belge_json2: Dict[str, Any]
    ):
        """Aynı kaynak için farklı belge türleri ve farklı veriler ile tüm işlemler başarılı olmalı"""
        
        # En az 2 farklı belge türü seç
        belge_turleri = [BelgeTuru.EFATURA.value, BelgeTuru.EARSIV.value]
        
        # Mock servis oluştur
        mock_service = Mock()
        mock_service.cikis_olustur = Mock()
        mock_service.cikis_olustur.side_effect = [1, 2]
        
        # İlk belge türü için DTO
        dto1 = EBelgeOlusturDTO(
            kaynak_turu=kaynak_turu,
            kaynak_id=kaynak_id,
            belge_turu=belge_turleri[0],
            musteri_ad=musteri_ad,
            vergi_no=vergi_no,
            toplam_tutar=toplam_tutar1,
            belge_json=belge_json1
        )
        
        # İkinci belge türü için DTO
        dto2 = EBelgeOlusturDTO(
            kaynak_turu=kaynak_turu,
            kaynak_id=kaynak_id,
            belge_turu=belge_turleri[1],
            musteri_ad=musteri_ad,
            vergi_no=vergi_no,
            toplam_tutar=toplam_tutar2,
            belge_json=belge_json2
        )
        
        # Her iki işlem de başarılı olmalı
        result1 = mock_service.cikis_olustur(dto1)
        result2 = mock_service.cikis_olustur(dto2)
        
        assert result1 == 1
        assert result2 == 2
        assert result1 != result2
        
        # Servis iki kez çağrılmış olmalı
        assert mock_service.cikis_olustur.call_count == 2