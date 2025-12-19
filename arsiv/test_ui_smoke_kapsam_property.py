# Version: 1.0.0
# Last Update: 2024-12-18
# Module: tests.test_ui_smoke_kapsam_property
# Description: Smoke test kapsamlılığı property-based testi
# Changelog:
# - İlk sürüm: Property 16 - Smoke test kapsamlılığı testi

"""
**Feature: test-stabilizasyon-paketi, Property 16: Smoke test kapsamlılığı**
**Validates: Requirements 7.1, 7.2**

Property 16: Smoke Test Kapsamlılığı
For any smoke test çalıştırması, tüm ana modüllerin import edilebilirliği
ve kritik servislerin başlatılabilirliği kontrol edilmeli
"""

import importlib
import os
import sys
from typing import List
from unittest.mock import MagicMock, patch

import pytest
from hypothesis import given, settings, strategies as st

# Test edilecek modülü import et
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# Ana modül listesi - sistemdeki kritik modüller
ANA_MODULLER = [
    "uygulama.arayuz.uygulama",
    "uygulama.arayuz.ana_pencere",
    "uygulama.arayuz.servis_fabrikasi",
    "sontechsp.uygulama.cekirdek.ayarlar",
    "sontechsp.uygulama.cekirdek.kayit",
    "sontechsp.uygulama.veritabani.baglanti",
]

# Kritik servis listesi
KRITIK_SERVISLER = [
    "ServisFabrikasi",
    "UygulamaBaslatici",
]


def modul_import_edilebilir_mi(modul_adi: str) -> bool:
    """
    Bir modülün import edilebilir olup olmadığını kontrol eder

    Args:
        modul_adi: Kontrol edilecek modül adı

    Returns:
        bool: Import edilebilirse True
    """
    try:
        importlib.import_module(modul_adi)
        return True
    except (ImportError, ModuleNotFoundError):
        return False


def servis_baslatilabilir_mi(servis_adi: str) -> bool:
    """
    Bir servisin başlatılabilir olup olmadığını kontrol eder

    Args:
        servis_adi: Kontrol edilecek servis adı

    Returns:
        bool: Başlatılabilirse True
    """
    try:
        if servis_adi == "ServisFabrikasi":
            from uygulama.arayuz.servis_fabrikasi import ServisFabrikasi

            fabrika = ServisFabrikasi()
            return fabrika is not None
        elif servis_adi == "UygulamaBaslatici":
            from uygulama.arayuz.uygulama import UygulamaBaslatici

            baslatici = UygulamaBaslatici()
            return baslatici is not None
        return False
    except Exception:
        return False


class TestSmokeTestKapsamliligi:
    """Property 16: Smoke Test Kapsamlılığı - Requirements 7.1, 7.2"""

    def test_ana_moduller_import_edilebilir(self):
        """
        Tüm ana modüllerin import edilebilir olduğunu doğrular
        Requirements 7.1: Tüm ana modüllerin import edilebilirliği kontrol edilmeli
        """
        basarisiz_moduller = []

        for modul_adi in ANA_MODULLER:
            if not modul_import_edilebilir_mi(modul_adi):
                basarisiz_moduller.append(modul_adi)

        # Tüm ana modüller import edilebilir olmalı
        assert len(basarisiz_moduller) == 0, f"Import edilemeyen modüller: {basarisiz_moduller}"

    def test_kritik_servisler_baslatilabilir(self):
        """
        Kritik servislerin başlatılabilir olduğunu doğrular
        Requirements 7.2: Kritik servislerin başlatılabilirliği doğrulanmalı
        """
        basarisiz_servisler = []

        for servis_adi in KRITIK_SERVISLER:
            if not servis_baslatilabilir_mi(servis_adi):
                basarisiz_servisler.append(servis_adi)

        # Tüm kritik servisler başlatılabilir olmalı
        assert len(basarisiz_servisler) == 0, f"Başlatılamayan servisler: {basarisiz_servisler}"

    @given(modul_listesi=st.lists(st.sampled_from(ANA_MODULLER), min_size=1, max_size=len(ANA_MODULLER)))
    @settings(max_examples=50, deadline=None)
    def test_modul_import_tutarliligi_property(self, modul_listesi: List[str]):
        """
        **Feature: test-stabilizasyon-paketi, Property 16: Smoke test kapsamlılığı**

        For any seçilen modül listesi, tüm modüller tutarlı şekilde import edilebilir olmalı
        """
        # Her modül için import kontrolü yap
        for modul_adi in modul_listesi:
            # Modül import edilebilir olmalı
            assert modul_import_edilebilir_mi(modul_adi), f"Modül import edilemedi: {modul_adi}"

            # Modül tekrar import edildiğinde aynı sonucu vermeli (tutarlılık)
            assert modul_import_edilebilir_mi(modul_adi), f"Modül tutarsız import davranışı: {modul_adi}"

    @given(servis_listesi=st.lists(st.sampled_from(KRITIK_SERVISLER), min_size=1, max_size=len(KRITIK_SERVISLER)))
    @settings(max_examples=30, deadline=None)
    def test_servis_baslatma_tutarliligi_property(self, servis_listesi: List[str]):
        """
        **Feature: test-stabilizasyon-paketi, Property 16: Smoke test kapsamlılığı**

        For any seçilen servis listesi, tüm servisler tutarlı şekilde başlatılabilir olmalı
        """
        # Her servis için başlatma kontrolü yap
        for servis_adi in servis_listesi:
            # Servis başlatılabilir olmalı
            assert servis_baslatilabilir_mi(servis_adi), f"Servis başlatılamadı: {servis_adi}"

            # Servis tekrar başlatıldığında aynı sonucu vermeli (tutarlılık)
            assert servis_baslatilabilir_mi(servis_adi), f"Servis tutarsız başlatma davranışı: {servis_adi}"

    def test_smoke_test_modulu_kapsam_kontrolu(self):
        """
        Smoke test modülünün gerekli kapsamlılık kontrollerini içerdiğini doğrular
        """
        import uygulama.arayuz.smoke_test_calistir as smoke_module

        # Modülde gerekli fonksiyonların var olduğunu kontrol et
        assert hasattr(smoke_module, "smoke_test_calistir")
        assert hasattr(smoke_module, "ekran_gecis_testi")
        assert hasattr(smoke_module, "standart_giris_noktasi_dogrula")

        # Fonksiyonların çağrılabilir olduğunu kontrol et
        assert callable(smoke_module.smoke_test_calistir)
        assert callable(smoke_module.ekran_gecis_testi)
        assert callable(smoke_module.standart_giris_noktasi_dogrula)

    @given(verbose=st.booleans(), ekran_sayisi=st.integers(min_value=0, max_value=5))
    @settings(max_examples=20, deadline=None)
    def test_smoke_test_parametrik_kapsam_property(self, verbose: bool, ekran_sayisi: int):
        """
        **Feature: test-stabilizasyon-paketi, Property 16: Smoke test kapsamlılığı**

        For any smoke test parametreleri, kapsamlılık kontrolü tutarlı şekilde çalışmalı
        """
        from uygulama.arayuz.smoke_test_calistir import smoke_test_calistir

        # Mock ekran listesi oluştur
        ekran_listesi = [f"ekran_{i}" for i in range(ekran_sayisi)] if ekran_sayisi > 0 else None

        # Mock tüm PyQt ve sistem bileşenlerini
        with patch("uygulama.arayuz.smoke_test_calistir.QApplication") as mock_app:
            with patch("uygulama.arayuz.smoke_test_calistir.UygulamaBaslatici") as mock_baslatici:
                with patch("uygulama.arayuz.smoke_test_calistir.ekran_gecis_testi") as mock_gecis:
                    with patch("uygulama.arayuz.smoke_test_calistir.temiz_kapanis"):
                        with patch("uygulama.arayuz.smoke_test_calistir.standart_giris_noktasi_dogrula") as mock_giris:

                            # Mock başarılı durumları
                            mock_gecis.return_value = True
                            mock_giris.return_value = (True, "uygulama.arayuz.uygulama")

                            # Mock nesneler oluştur
                            mock_app_instance = MagicMock()
                            mock_app.return_value = mock_app_instance

                            mock_baslatici_instance = MagicMock()
                            mock_baslatici.return_value = mock_baslatici_instance

                            # Smoke test çalıştır
                            result = smoke_test_calistir(
                                verbose=verbose, ekranlar=ekran_listesi, csv_export=False, csv_dosya=None
                            )

                            # Sonuç tutarlı olmalı
                            assert isinstance(result, int)
                            assert result == 0  # Başarılı durumda 0 dönmeli

                            # Gerekli fonksiyonlar çağrılmalı
                            mock_giris.assert_called_once()
                            mock_gecis.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
