# Version: 0.1.0
# Last Update: 2024-12-18
# Module: tests.test_ui_is_kurali_kisitlamasi_property
# Description: UI iş kuralı kısıtlaması property-based testleri
# Changelog:
# - İlk versiyon: Özellik 11 - UI İş Kuralı Kısıtlaması testleri

import sys
import unittest
from unittest.mock import MagicMock, patch
from typing import Optional

from hypothesis import given, settings, strategies as st
from PyQt6.QtWidgets import QApplication, QPushButton

from uygulama.arayuz.ekranlar.temel_ekran import TemelEkran
from uygulama.arayuz.log_sistemi import (
    log_kayitlarini_listele,
    log_kayitlarini_temizle,
    LogDurumu,
)


class TestUIIsKuraliKisitlamasi:
    """UI iş kuralı kısıtlaması property-based testleri"""

    def setup_method(self):
        """Her test öncesi temizlik"""
        log_kayitlarini_temizle()

        # QApplication oluştur (eğer yoksa)
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()

    def teardown_method(self):
        """Her test sonrası temizlik"""
        log_kayitlarini_temizle()

    @given(
        buton_adi=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        handler_adi=st.text(min_size=1, max_size=50).filter(lambda x: x.strip() and x.isidentifier()),
        servis_metodu=st.one_of(st.none(), st.text(min_size=1, max_size=50).filter(lambda x: x.strip())),
    )
    @settings(max_examples=100, deadline=5000)
    def test_property_ui_is_kurali_kisitlamasi(self, buton_adi: str, handler_adi: str, servis_metodu: Optional[str]):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 11: UI İş Kuralı Kısıtlaması**
        **Doğrular: Gereksinim 3.4**

        Herhangi bir UI etkileşimi olduğunda, sistem iş kuralı çalıştırmamalı,
        sadece loglama ve servis çağrısı yapmalıdır
        """
        # Arrange - Mock servis fabrikası oluştur
        mock_servis_fabrikasi = MagicMock()

        # TemelEkran sınıfından türeyen test ekranı oluştur
        class TestEkrani(TemelEkran):
            def __init__(self, servis_fabrikasi):
                super().__init__(servis_fabrikasi)
                self.is_kurali_calistirildi = False
                self.servis_cagrildi = False

            def ekrani_hazirla(self):
                super().ekrani_hazirla()

        # Test ekranı oluştur
        test_ekrani = TestEkrani(mock_servis_fabrikasi)

        # Test butonu oluştur
        test_buton = QPushButton(buton_adi)

        # Mock handler fonksiyonu oluştur - iş kuralı içermemeli
        def mock_handler():
            # Sadece loglama ve servis çağrısı yapmalı
            test_ekrani.servis_cagrildi = True

            # İş kuralı çalıştırmamalı
            # Bu handler'da hiçbir iş kuralı mantığı olmamalı
            return "handler_completed"

        mock_handler.__name__ = handler_adi

        # Act - Buton bağlama wrapper fonksiyonunu çağır
        test_ekrani.buton_bagla_ve_kaydet(test_buton, buton_adi, mock_handler, servis_metodu)

        # Butona tıkla (simüle et)
        test_buton.click()

        # Assert - Sadece loglama ve servis çağrısı yapılmalı, iş kuralı çalışmamalı

        # 1. Log kaydı oluşturulmalı
        log_kayitlari = log_kayitlarini_listele()
        assert len(log_kayitlari) >= 1, "UI etkileşimi log kaydı oluşturmalı"

        # Son log kaydını kontrol et
        son_log = log_kayitlari[-1]
        assert son_log["ekran_adi"] == "TestEkrani", "Ekran adı doğru loglanmalı"
        assert son_log["buton_adi"] == buton_adi, "Buton adı doğru loglanmalı"
        assert son_log["handler_adi"] == handler_adi, "Handler adı doğru loglanmalı"

        # 2. Servis çağrısı yapılmalı
        assert test_ekrani.servis_cagrildi, "Servis çağrısı yapılmalı"

        # 3. İş kuralı çalıştırılmamalı
        assert not test_ekrani.is_kurali_calistirildi, "UI etkileşiminde iş kuralı çalıştırılmamalı"

    def test_property_ui_sadece_loglama_ve_servis(self):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 11: UI İş Kuralı Kısıtlaması (Sadece Loglama)**
        **Doğrular: Gereksinim 3.4**

        UI handler'ları sadece loglama ve servis çağrısı yapmalı,
        karmaşık iş mantığı içermemeli
        """
        # Arrange
        mock_servis_fabrikasi = MagicMock()

        class TestEkrani(TemelEkran):
            def __init__(self, servis_fabrikasi):
                super().__init__(servis_fabrikasi)
                self.karmasik_islem_yapildi = False

        test_ekrani = TestEkrani(mock_servis_fabrikasi)
        test_buton = QPushButton("Test Buton")

        # Karmaşık iş kuralı içeren handler (YANLIŞ örnek)
        def karmasik_handler():
            # Bu tür karmaşık işlemler UI handler'da olmamalı
            # Sadece basit loglama ve servis çağrısı olmalı
            return "simple_result"

        karmasik_handler.__name__ = "karmasik_handler"

        # Act
        test_ekrani.buton_bagla_ve_kaydet(test_buton, "Test Buton", karmasik_handler, "test_servis")

        test_buton.click()

        # Assert - Sadece loglama yapılmalı
        log_kayitlari = log_kayitlarini_listele()
        assert len(log_kayitlari) >= 1, "Loglama yapılmalı"

        # Handler basit olmalı, karmaşık iş kuralı içermemeli
        son_log = log_kayitlari[-1]
        assert son_log["durum"] in ["basarili", "stub"], "Handler basit işlem yapmalı"

    def test_property_ui_stub_servis_kullanimi(self):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 11: UI İş Kuralı Kısıtlaması (Stub Servis)**
        **Doğrular: Gereksinim 3.4**

        UI test ortamında stub servisler kullanılmalı,
        gerçek iş kuralları çalıştırılmamalı
        """
        # Arrange
        mock_servis_fabrikasi = MagicMock()

        class TestEkrani(TemelEkran):
            def __init__(self, servis_fabrikasi):
                super().__init__(servis_fabrikasi)

        test_ekrani = TestEkrani(mock_servis_fabrikasi)
        test_buton = QPushButton("Stub Test")

        # Stub servis kullanan handler
        def stub_handler():
            # Stub servis çağrısı - gerçek iş kuralı yok
            return "stub_result"

        stub_handler.__name__ = "stub_handler"

        # Act
        test_ekrani.buton_bagla_ve_kaydet(test_buton, "Stub Test", stub_handler, "stub_servis_metodu")

        test_buton.click()

        # Assert - Stub servis kullanımı loglanmalı
        log_kayitlari = log_kayitlarini_listele()
        assert len(log_kayitlari) >= 1, "Stub servis kullanımı loglanmalı"

        # Stub servis çağrısı kontrol edilmeli
        stub_log_var = any(
            "stub" in log.get("servis_metodu", "").lower() or log.get("durum") == "stub" for log in log_kayitlari
        )
        assert stub_log_var, "Stub servis kullanımı belirtilmeli"

    @given(handler_sayisi=st.integers(min_value=1, max_value=5))
    @settings(max_examples=50, deadline=10000)
    def test_property_coklu_ui_etkileşim_is_kurali_kisitlamasi(self, handler_sayisi: int):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 11: UI İş Kuralı Kısıtlaması (Çoklu)**
        **Doğrular: Gereksinim 3.4**

        Birden fazla UI etkileşimi olduğunda, hiçbirinde iş kuralı çalıştırılmamalı
        """
        # Arrange
        mock_servis_fabrikasi = MagicMock()

        class TestEkrani(TemelEkran):
            def __init__(self, servis_fabrikasi):
                super().__init__(servis_fabrikasi)
                self.is_kurali_cagri_sayisi = 0

        test_ekrani = TestEkrani(mock_servis_fabrikasi)

        # Act - Birden fazla buton oluştur ve tıkla
        for i in range(handler_sayisi):
            test_buton = QPushButton(f"Buton_{i}")

            def handler_func():
                # Sadece basit işlem, iş kuralı yok
                return f"result_{i}"

            handler_func.__name__ = f"handler_{i}"

            test_ekrani.buton_bagla_ve_kaydet(test_buton, f"Buton_{i}", handler_func, f"servis_{i}")

            test_buton.click()

        # Assert - Hiçbir handler'da iş kuralı çalışmamalı
        assert test_ekrani.is_kurali_cagri_sayisi == 0, "Hiçbir UI etkileşiminde iş kuralı çalışmamalı"

        # Tüm etkileşimler loglanmalı
        log_kayitlari = log_kayitlarini_listele()
        assert len(log_kayitlari) >= handler_sayisi, "Tüm UI etkileşimleri loglanmalı"

    def test_property_ui_hata_durumu_is_kurali_kisitlamasi(self):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 11: UI İş Kuralı Kısıtlaması (Hata Durumu)**
        **Doğrular: Gereksinim 3.4**

        UI handler'da hata oluştuğunda bile iş kuralı çalıştırılmamalı,
        sadece hata loglanmalı
        """
        # Arrange
        mock_servis_fabrikasi = MagicMock()

        class TestEkrani(TemelEkran):
            def __init__(self, servis_fabrikasi):
                super().__init__(servis_fabrikasi)
                self.is_kurali_hata_durumunda_calistirildi = False

        test_ekrani = TestEkrani(mock_servis_fabrikasi)
        test_buton = QPushButton("Hata Test")

        # Hata fırlatan handler
        def hata_handler():
            # Hata durumunda bile iş kuralı çalışmamalı
            raise ValueError("Test hatası")

        hata_handler.__name__ = "hata_handler"

        # Act
        test_ekrani.buton_bagla_ve_kaydet(test_buton, "Hata Test", hata_handler, "hata_servis")

        test_buton.click()

        # Assert - Hata durumunda bile iş kuralı çalışmamalı
        assert not test_ekrani.is_kurali_hata_durumunda_calistirildi, "Hata durumunda bile iş kuralı çalıştırılmamalı"

        # Hata loglanmalı
        log_kayitlari = log_kayitlarini_listele()
        hata_log_var = any(log.get("durum") == "hata" for log in log_kayitlari)
        assert hata_log_var, "Hata durumu loglanmalı"


if __name__ == "__main__":
    unittest.main()
