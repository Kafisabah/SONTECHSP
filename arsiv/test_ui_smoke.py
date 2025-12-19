# Version: 1.0.0
# Last Update: 2024-12-18
# Module: tests.test_ui_smoke
# Description: UI smoke testleri - mevcut altyapı genişletmesi
# Changelog:
# - İlk sürüm: Mevcut smoke_test_calistir.py altyapısını kullanan genişletilmiş kontroller

"""
UI Smoke Testleri

Bu modül mevcut smoke_test_calistir.py altyapısını kullanarak genişletilmiş kontroller sağlar.
Tüm ana modüllerin import edilebilirliği ve kritik servislerin başlatılabilirliği kontrolü yapar.
"""

import os
import sys
from typing import Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest

# Test edilecek modülü import et
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestUISmokeGenisletilmis:
    """Genişletilmiş UI Smoke Testleri - Requirements 7.1, 7.2, 7.3, 7.4"""

    def test_ana_moduller_import_kontrolu(self):
        """
        Tüm ana modüllerin import edilebilir olduğunu kontrol eder
        Requirements 7.1: Tüm ana modüllerin import edilebilirliği kontrol edilmeli
        """
        # Ana modül listesi
        ana_moduller = [
            "uygulama.arayuz.uygulama",
            "uygulama.arayuz.ana_pencere",
            "uygulama.arayuz.servis_fabrikasi",
            "sontechsp.uygulama.cekirdek.ayarlar",
            "sontechsp.uygulama.cekirdek.kayit",
            "sontechsp.uygulama.veritabani.baglanti",
        ]

        basarisiz_moduller = []

        for modul_adi in ana_moduller:
            try:
                __import__(modul_adi)
            except (ImportError, ModuleNotFoundError) as e:
                basarisiz_moduller.append(f"{modul_adi}: {e}")

        # Tüm ana modüller import edilebilir olmalı
        assert len(basarisiz_moduller) == 0, f"Import edilemeyen modüller: {basarisiz_moduller}"

    def test_kritik_servisler_baslatma_kontrolu(self):
        """
        Kritik servislerin başlatılabilir olduğunu kontrol eder
        Requirements 7.2: Kritik servislerin başlatılabilirliği doğrulanmalı
        """
        basarisiz_servisler = []

        # ServisFabrikasi kontrolü
        try:
            from uygulama.arayuz.servis_fabrikasi import ServisFabrikasi

            fabrika = ServisFabrikasi()
            assert fabrika is not None
        except Exception as e:
            basarisiz_servisler.append(f"ServisFabrikasi: {e}")

        # UygulamaBaslatici kontrolü
        try:
            from uygulama.arayuz.uygulama import UygulamaBaslatici

            baslatici = UygulamaBaslatici()
            assert baslatici is not None
        except Exception as e:
            basarisiz_servisler.append(f"UygulamaBaslatici: {e}")

        # Tüm kritik servisler başlatılabilir olmalı
        assert len(basarisiz_servisler) == 0, f"Başlatılamayan servisler: {basarisiz_servisler}"

    def test_mevcut_smoke_test_altyapisi_kullanimi(self):
        """
        Mevcut smoke_test_calistir.py altyapısının kullanıldığını doğrular
        Requirements 7.4: Mevcut altyapı kullanılmalı
        """
        # Mevcut smoke test modülünün import edilebilirliği
        import uygulama.arayuz.smoke_test_calistir as smoke_module

        # Ana fonksiyonların varlığını kontrol et
        assert hasattr(smoke_module, "smoke_test_calistir")
        assert hasattr(smoke_module, "ekran_gecis_testi")
        assert hasattr(smoke_module, "temiz_kapanis")
        assert hasattr(smoke_module, "standart_giris_noktasi_dogrula")

        # Buton eşleştirme altyapısının kullanıldığını kontrol et
        try:
            from uygulama.arayuz.buton_eslestirme_kaydi import (
                tablo_formatinda_cikti,
                csv_formatinda_cikti,
                csv_dosyasina_kaydet,
                kayitlari_temizle,
            )

            # Bu fonksiyonlar mevcut altyapının parçası
            assert callable(tablo_formatinda_cikti)
            assert callable(csv_formatinda_cikti)
            assert callable(csv_dosyasina_kaydet)
            assert callable(kayitlari_temizle)
        except ImportError:
            pytest.fail("Mevcut buton eşleştirme altyapısı bulunamadı")

    def test_smoke_test_ozet_rapor_uretimi(self):
        """
        Smoke test'in özet rapor ürettiğini doğrular
        Requirements 7.3: Özet rapor sunulmalı
        """
        from uygulama.arayuz.smoke_test_calistir import smoke_test_calistir

        # Mock tüm PyQt ve sistem bileşenlerini
        with patch("uygulama.arayuz.smoke_test_calistir.QApplication"):
            with patch("uygulama.arayuz.smoke_test_calistir.UygulamaBaslatici"):
                with patch("uygulama.arayuz.smoke_test_calistir.ekran_gecis_testi") as mock_gecis:
                    with patch("uygulama.arayuz.smoke_test_calistir.temiz_kapanis"):
                        with patch("uygulama.arayuz.smoke_test_calistir.standart_giris_noktasi_dogrula") as mock_giris:
                            with patch("uygulama.arayuz.smoke_test_calistir.tablo_formatinda_cikti") as mock_tablo:

                                # Mock başarılı durumları
                                mock_gecis.return_value = True
                                mock_giris.return_value = (True, "uygulama.arayuz.uygulama")
                                mock_tablo.return_value = "Test Raporu\n==========\nBaşarılı: 5\nBaşarısız: 0"

                                # Smoke test çalıştır (verbose=True ile rapor üretilmeli)
                                result = smoke_test_calistir(verbose=True)

                                # Test başarılı olmalı
                                assert result == 0

                                # Rapor fonksiyonu çağrılmalı
                                mock_tablo.assert_called_once()

    def test_temel_fonksiyon_kontrolleri(self):
        """
        Temel fonksiyon kontrollerini yapar
        Requirements 7.1, 7.2: Temel fonksiyon kontrollerini uygula
        """
        # Smoke test modülünün temel fonksiyonlarını kontrol et
        import uygulama.arayuz.smoke_test_calistir as smoke_module

        # Ana fonksiyonların çağrılabilir olduğunu kontrol et
        assert callable(smoke_module.smoke_test_calistir)
        assert callable(smoke_module.ekran_gecis_testi)
        assert callable(smoke_module.temiz_kapanis)
        assert callable(smoke_module.standart_giris_noktasi_dogrula)

        # main() fonksiyonunun var olduğunu kontrol et
        assert hasattr(smoke_module, "main")
        assert callable(smoke_module.main)

    def test_genisletilmis_modul_kontrolleri(self):
        """
        Genişletilmiş modül kontrollerini yapar
        """
        # Ek modül kontrolleri
        ek_moduller = [
            "sontechsp.uygulama.cekirdek.hatalar",
            "sontechsp.uygulama.cekirdek.oturum",
            "sontechsp.uygulama.cekirdek.yetki",
        ]

        basarisiz_moduller = []

        for modul_adi in ek_moduller:
            try:
                __import__(modul_adi)
            except (ImportError, ModuleNotFoundError) as e:
                basarisiz_moduller.append(f"{modul_adi}: {e}")

        # Ek modüller de import edilebilir olmalı
        assert len(basarisiz_moduller) == 0, f"Import edilemeyen ek modüller: {basarisiz_moduller}"

    def test_csv_rapor_uretimi(self):
        """
        CSV rapor üretimini test eder
        """
        from uygulama.arayuz.smoke_test_calistir import smoke_test_calistir

        # Mock tüm PyQt ve sistem bileşenlerini
        with patch("uygulama.arayuz.smoke_test_calistir.QApplication"):
            with patch("uygulama.arayuz.smoke_test_calistir.UygulamaBaslatici"):
                with patch("uygulama.arayuz.smoke_test_calistir.ekran_gecis_testi") as mock_gecis:
                    with patch("uygulama.arayuz.smoke_test_calistir.temiz_kapanis"):
                        with patch("uygulama.arayuz.smoke_test_calistir.standart_giris_noktasi_dogrula") as mock_giris:
                            with patch("uygulama.arayuz.smoke_test_calistir.csv_formatinda_cikti") as mock_csv:

                                # Mock başarılı durumları
                                mock_gecis.return_value = True
                                mock_giris.return_value = (True, "uygulama.arayuz.uygulama")
                                mock_csv.return_value = "Ekran,Durum\npos_satis,Başarılı\nurunler_stok,Başarılı"

                                # Smoke test çalıştır (CSV export ile)
                                result = smoke_test_calistir(verbose=True, csv_export=True)

                                # Test başarılı olmalı
                                assert result == 0

                                # CSV fonksiyonu çağrılmalı
                                mock_csv.assert_called_once()

    def test_smoke_test_parametrik_calisma(self):
        """
        Smoke test'in farklı parametrelerle çalıştığını test eder
        """
        from uygulama.arayuz.smoke_test_calistir import smoke_test_calistir

        # Farklı parametre kombinasyonları
        test_parametreleri = [
            {"verbose": True, "csv_export": False},
            {"verbose": False, "csv_export": True},
            {"verbose": True, "csv_export": True},
        ]

        for params in test_parametreleri:
            # Mock tüm PyQt ve sistem bileşenlerini
            with patch("uygulama.arayuz.smoke_test_calistir.QApplication"):
                with patch("uygulama.arayuz.smoke_test_calistir.UygulamaBaslatici"):
                    with patch("uygulama.arayuz.smoke_test_calistir.ekran_gecis_testi") as mock_gecis:
                        with patch("uygulama.arayuz.smoke_test_calistir.temiz_kapanis"):
                            with patch(
                                "uygulama.arayuz.smoke_test_calistir.standart_giris_noktasi_dogrula"
                            ) as mock_giris:

                                # Mock başarılı durumları
                                mock_gecis.return_value = True
                                mock_giris.return_value = (True, "uygulama.arayuz.uygulama")

                                # Smoke test çalıştır
                                result = smoke_test_calistir(**params)

                                # Test başarılı olmalı
                                assert result == 0


if __name__ == "__main__":
    pytest.main([__file__])
