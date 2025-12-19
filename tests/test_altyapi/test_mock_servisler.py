# Version: 0.1.0
# Last Update: 2025-12-18
# Module: tests.test_altyapi.test_mock_servisler
# Description: Mock servisler test dosyası
# Changelog:
# - İlk oluşturma

"""
Mock Servisler Test Dosyası

Bu test dosyası mock servislerin doğru çalıştığını test eder.
"""

import pytest
from tests.test_altyapi.mock_servisler import DummySaglayici, MockNetworkService, MockStokService, MockServisFabrikasi
from tests.test_altyapi.pytest_markers import smoke_test, fast_test


@smoke_test
def test_dummy_saglayici_olusturma():
    """DummySaglayici oluşturma testi"""
    saglayici = DummySaglayici(hata_orani=0.0)  # Hata yok
    assert saglayici.hata_orani == 0.0
    assert saglayici.gonderim_sayaci == 0


@fast_test
def test_mock_network_service_olusturma():
    """MockNetworkService oluşturma testi"""
    network = MockNetworkService(baslangic_durumu=True)
    assert network.online is True
    assert network.network_durumu_kontrol() is True


@fast_test
def test_mock_stok_service_olusturma():
    """MockStokService oluşturma testi"""
    stok = MockStokService()
    assert stok.stok_bakiye_getir(1) == 0  # Varsayılan bakiye 0


@smoke_test
def test_mock_servis_fabrikasi():
    """MockServisFabrikasi testi"""
    ortam = MockServisFabrikasi.tam_mock_ortam_olustur()

    assert "dummy_saglayici" in ortam
    assert "network_service" in ortam
    assert "stok_service" in ortam
    assert "pos_service" in ortam
