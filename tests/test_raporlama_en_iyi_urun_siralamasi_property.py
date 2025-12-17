# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.test_raporlama_en_iyi_urun_siralamasi_property
# Description: En iyi ürün sıralaması property testi
# Changelog:
# - İlk oluşturma

"""
**Feature: raporlama-modulu, Property 9: En iyi ürün sıralaması**
**Validates: Requirements 3.1**
"""

import pytest
from hypothesis import given, strategies as st
from unittest.mock import Mock
from sqlalchemy.orm import Session
from decimal import Decimal

from sontechsp.uygulama.moduller.raporlar.sorgular import en_cok_satan_urunler
from sontechsp.uygulama.moduller.raporlar.dto import TarihAraligiDTO
from datetime import date


@given(
    urun_sayisi=st.integers(min_value=1, max_value=5)
)
def test_en_iyi_urun_siralamasi_property(urun_sayisi):
    """Property: En iyi ürün sıralaması"""
    # Arrange
    mock_session = Mock(spec=Session)
    mock_results = []
    
    for i in range(urun_sayisi):
        mock_row = Mock()
        mock_row.urun_id = i + 1
        mock_row.urun_adi = f"Ürün {i + 1}"
        mock_row.miktar_toplam = (urun_sayisi - i) * 10  # Azalan sıra
        mock_row.ciro_toplam = Decimal(str((urun_sayisi - i) * 100))
        mock_results.append(mock_row)
    
    mock_session.execute.return_value.fetchall.return_value = mock_results
    
    tarih_araligi = TarihAraligiDTO(date(2024, 1, 1), date(2024, 1, 31))
    
    # Act
    sonuclar = en_cok_satan_urunler(mock_session, 1, tarih_araligi, 10)
    
    # Assert: Sıralama kontrolü
    for i in range(len(sonuclar) - 1):
        assert sonuclar[i]['miktar_toplam'] >= sonuclar[i + 1]['miktar_toplam']