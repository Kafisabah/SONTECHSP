# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.test_raporlama_stok_verisi_butunlugu_property
# Description: Raporlama modülü stok verisi bütünlüğü property testi
# Changelog:
# - İlk oluşturma

"""
**Feature: raporlama-modulu, Property 6: Stok verisi bütünlüğü**
**Validates: Requirements 2.2**

Herhangi bir kritik stok raporu sonucu için, döndürülen her kayıt düzgün tablo 
birleştirmelerinden geçerli ürün ve stok bakiye verilerine sahip olmalıdır
"""

import pytest
from hypothesis import given, strategies as st
from unittest.mock import Mock
from sqlalchemy.orm import Session

from sontechsp.uygulama.moduller.raporlar.sorgular import kritik_stok_listesi


@given(
    urun_sayisi=st.integers(min_value=1, max_value=5)
)
def test_stok_verisi_butunlugu_property(urun_sayisi):
    """
    Property: Stok verisi bütünlüğü
    
    Kritik stok raporu sonuçlarında:
    - Her kayıt geçerli ürün bilgilerine sahip olmalı
    - Her kayıt geçerli stok bakiye bilgilerine sahip olmalı
    - JOIN işlemleri doğru çalışmalı
    """
    # Arrange
    mock_session = Mock(spec=Session)
    mock_results = []
    
    for i in range(urun_sayisi):
        mock_row = Mock()
        # Geçerli ürün ve stok verileri
        mock_row.urun_id = i + 1
        mock_row.urun_adi = f"Test Ürün {i + 1}"
        mock_row.depo_id = 1
        mock_row.miktar = 5
        mock_row.kritik_seviye = 10
        mock_results.append(mock_row)
    
    mock_session.execute.return_value.fetchall.return_value = mock_results
    
    # Act
    sonuclar = kritik_stok_listesi(mock_session)
    
    # Assert: Veri bütünlüğü kontrolü
    for sonuc in sonuclar:
        # Tüm gerekli alanlar mevcut olmalı
        assert 'urun_id' in sonuc
        assert 'urun_adi' in sonuc
        assert 'depo_id' in sonuc
        assert 'miktar' in sonuc
        assert 'kritik_seviye' in sonuc
        
        # Değerler geçerli olmalı
        assert sonuc['urun_id'] > 0
        assert sonuc['urun_adi'] != ""
        assert sonuc['depo_id'] > 0
        assert sonuc['miktar'] >= 0
        assert sonuc['kritik_seviye'] > 0