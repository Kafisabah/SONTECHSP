# Version: 0.1.0
# Last Update: 2025-12-16
# Module: tests.pos.conftest
# Description: POS testleri için pytest konfigürasyonu
# Changelog:
# - İlk oluşturma

"""
POS Testleri Pytest Konfigürasyonu

Bu modül POS testleri için gerekli fixture'ları ve konfigürasyonu sağlar.
"""

import pytest
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, List
from unittest.mock import Mock, MagicMock

from sontechsp.uygulama.moduller.pos.arayuzler import (
    SepetDurum, SatisDurum, OdemeTuru, IslemTuru, KuyrukDurum
)


@pytest.fixture
def mock_sepet_repository():
    """Mock sepet repository fixture"""
    mock_repo = Mock()
    mock_repo.sepet_olustur.return_value = 1
    mock_repo.sepet_getir.return_value = {
        'id': 1,
        'terminal_id': 1,
        'kasiyer_id': 1,
        'durum': SepetDurum.AKTIF,
        'toplam_tutar': Decimal('0.00')
    }
    mock_repo.sepet_satiri_ekle.return_value = 1
    mock_repo.sepet_satiri_guncelle.return_value = True
    mock_repo.sepet_satiri_sil.return_value = True
    mock_repo.sepet_bosalt.return_value = True
    return mock_repo


@pytest.fixture
def mock_satis_repository():
    """Mock satış repository fixture"""
    mock_repo = Mock()
    mock_repo.satis_olustur.return_value = 1
    mock_repo.satis_getir.return_value = {
        'id': 1,
        'sepet_id': 1,
        'terminal_id': 1,
        'kasiyer_id': 1,
        'toplam_tutar': Decimal('100.00'),
        'durum': SatisDurum.BEKLEMEDE
    }
    mock_repo.satis_odeme_ekle.return_value = 1
    mock_repo.satis_tamamla.return_value = True
    return mock_repo


@pytest.fixture
def mock_iade_repository():
    """Mock iade repository fixture"""
    mock_repo = Mock()
    mock_repo.iade_olustur.return_value = 1
    mock_repo.iade_satiri_ekle.return_value = 1
    mock_repo.iade_tamamla.return_value = True
    return mock_repo


@pytest.fixture
def mock_offline_kuyruk_repository():
    """Mock offline kuyruk repository fixture"""
    mock_repo = Mock()
    mock_repo.kuyruga_ekle.return_value = 1
    mock_repo.bekleyen_islemler.return_value = []
    mock_repo.islem_tamamla.return_value = True
    mock_repo.islem_hata.return_value = True
    return mock_repo


@pytest.fixture
def mock_stok_service():
    """Mock stok service fixture"""
    mock_service = Mock()
    mock_service.urun_bilgisi_getir.return_value = {
        'id': 1,
        'ad': 'Test Ürün',
        'barkod': '1234567890',
        'fiyat': Decimal('10.00'),
        'stok_miktari': 100
    }
    mock_service.stok_kontrol.return_value = True
    mock_service.stok_rezerve_et.return_value = True
    mock_service.stok_dusur.return_value = True
    mock_service.stok_artir.return_value = True
    return mock_service


@pytest.fixture
def sample_sepet_data():
    """Örnek sepet verisi"""
    return {
        'id': 1,
        'terminal_id': 1,
        'kasiyer_id': 1,
        'olusturma_tarihi': datetime.now(),
        'durum': SepetDurum.AKTIF,
        'toplam_tutar': Decimal('50.00'),
        'satirlar': [
            {
                'id': 1,
                'urun_id': 1,
                'barkod': '1234567890',
                'adet': 2,
                'birim_fiyat': Decimal('10.00'),
                'toplam_tutar': Decimal('20.00')
            },
            {
                'id': 2,
                'urun_id': 2,
                'barkod': '0987654321',
                'adet': 3,
                'birim_fiyat': Decimal('10.00'),
                'toplam_tutar': Decimal('30.00')
            }
        ]
    }


@pytest.fixture
def sample_satis_data():
    """Örnek satış verisi"""
    return {
        'id': 1,
        'sepet_id': 1,
        'terminal_id': 1,
        'kasiyer_id': 1,
        'satis_tarihi': datetime.now(),
        'toplam_tutar': Decimal('100.00'),
        'durum': SatisDurum.TAMAMLANDI,
        'fis_no': 'FIS001',
        'odemeler': [
            {
                'id': 1,
                'odeme_turu': OdemeTuru.NAKIT,
                'tutar': Decimal('60.00')
            },
            {
                'id': 2,
                'odeme_turu': OdemeTuru.KART,
                'tutar': Decimal('40.00')
            }
        ]
    }


@pytest.fixture
def sample_iade_data():
    """Örnek iade verisi"""
    return {
        'id': 1,
        'orijinal_satis_id': 1,
        'terminal_id': 1,
        'kasiyer_id': 1,
        'iade_tarihi': datetime.now(),
        'toplam_tutar': Decimal('30.00'),
        'neden': 'Müşteri talebi',
        'satirlar': [
            {
                'id': 1,
                'urun_id': 1,
                'adet': 1,
                'birim_fiyat': Decimal('10.00'),
                'toplam_tutar': Decimal('10.00')
            }
        ]
    }


# Hypothesis stratejileri
from hypothesis import strategies as st

# Temel veri türleri için stratejiler
barkod_strategy = st.text(
    alphabet='0123456789',
    min_size=8,
    max_size=13
)

pozitif_decimal_strategy = st.decimals(
    min_value=Decimal('0.01'),
    max_value=Decimal('9999.99'),
    places=2
)

pozitif_int_strategy = st.integers(min_value=1, max_value=1000)

terminal_id_strategy = st.integers(min_value=1, max_value=10)
kasiyer_id_strategy = st.integers(min_value=1, max_value=100)
urun_id_strategy = st.integers(min_value=1, max_value=10000)

odeme_turu_strategy = st.sampled_from(list(OdemeTuru))
sepet_durum_strategy = st.sampled_from(list(SepetDurum))
satis_durum_strategy = st.sampled_from(list(SatisDurum))