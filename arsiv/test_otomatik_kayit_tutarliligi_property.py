# Version: 0.1.0
# Last Update: 2024-12-18
# Module: tests.test_otomatik_kayit_tutarliligi_property
# Description: Otomatik kayıt tutarlılığı property-based testleri
# Changelog:
# - İlk versiyon: Özellik 6 - Otomatik Kayıt Tutarlılığı testleri

import sys
import unittest
from unittest.mock import MagicMock, patch
from typing import Optional

from hypothesis import given, settings, strategies as st
from PyQt6.QtWidgets import QApplication, QPushButton

from uygulama.arayuz.ekranlar.temel_ekran import TemelEkran
from uygulama.arayuz.buton_eslestirme_kaydi import (
    kayitlari_listele,
    kayitlari_temizle,
    kayit_sayisi,
)


class TestOtomatikKayitTutarliligi:
    """Otomatik kayıt tutarlılığı property-based testleri"""

    def setup_method(self):
        """Her test öncesi temizlik"""
        kayitlari_temizle()

        # QApplication oluştur (eğer yoksa)
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()

    def teardown_method(self):
        """Her test sonrası temizlik"""
        kayitlari_temizle()

    @given(
        buton_adi=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        handler_adi=st.text(min_size=1, max_size=50).filter(lambda x: x.strip() and x.isidentifier()),
        servis_metodu=st.one_of(st.none(), st.text(min_size=1, max_size=50).filter(lambda x: x.strip())),
    )
    @settings(max_examples=100, deadline=5000)
    def test_property_otomatik_kayit_tutarliligi(self, buton_adi: str, handler_adi: str, servis_metodu: Optional[str]):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 6: Otomatik Kayıt Tutarlılığı**
        **Doğrular: Gereksinim 2.3**

        Herhangi bir kritik buton bağlandığında, sistem otomatik olarak eşleştirmeyi kaydetmelidir
        """
        # Arrange - Mock servis fabrikası oluştur
        mock_servis_fabrikasi = MagicMock()

        # TemelEkran sınıfından türeyen test ekranı oluştur
        class TestEkrani(TemelEkran):
            def __init__(self, servis_fabrikasi):
                super().__init__(servis_fabrikasi)

            def ekrani_hazirla(self):
                super().ekrani_hazirla()

        # Test ekranı oluştur
        test_ekrani = TestEkrani(mock_servis_fabrikasi)

        # Test butonu oluştur
        test_buton = QPushButton(buton_adi)

        # Mock handler fonksiyonu oluştur
        def mock_handler():
            return "test_result"

        mock_handler.__name__ = handler_adi

        # Başlangıç kayıt sayısını al
        baslangic_kayit_sayisi = kayit_sayisi()

        # Act - Buton bağlama wrapper fonksiyonunu çağır
        test_ekrani.buton_bagla_ve_kaydet(test_buton, buton_adi, mock_handler, servis_metodu)

        # Assert - Kayıt otomatik olarak eklenmiş olmalı
        son_kayit_sayisi = kayit_sayisi()
        assert son_kayit_sayisi == baslangic_kayit_sayisi + 1, "Buton bağlandığında otomatik kayıt eklenmeli"

        # Kayıt içeriğini kontrol et
        kayitlar = kayitlari_listele()
        son_kayit = kayitlar[-1]  # En son eklenen kayıt

        assert son_kayit["ekran_adi"] == "TestEkrani", "Ekran adı doğru kaydedilmeli"
        assert son_kayit["buton_adi"] == buton_adi, "Buton adı doğru kaydedilmeli"
        assert son_kayit["handler_adi"] == handler_adi, "Handler adı doğru kaydedilmeli"
        assert son_kayit["servis_metodu"] == servis_metodu, "Servis metodu doğru kaydedilmeli"

    @given(buton_sayisi=st.integers(min_value=1, max_value=10))
    @settings(max_examples=50, deadline=10000)
    def test_property_coklu_buton_otomatik_kayit(self, buton_sayisi: int):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 6: Otomatik Kayıt Tutarlılığı (Çoklu)**
        **Doğrular: Gereksinim 2.3**

        Birden fazla buton bağlandığında, her biri için otomatik kayıt oluşturulmalıdır
        """
        # Arrange
        mock_servis_fabrikasi = MagicMock()

        class TestEkrani(TemelEkran):
            def __init__(self, servis_fabrikasi):
                super().__init__(servis_fabrikasi)

        test_ekrani = TestEkrani(mock_servis_fabrikasi)

        baslangic_kayit_sayisi = kayit_sayisi()

        # Act - Birden fazla buton bağla
        for i in range(buton_sayisi):
            test_buton = QPushButton(f"Buton_{i}")

            def mock_handler():
                return f"result_{i}"

            mock_handler.__name__ = f"handler_{i}"

            test_ekrani.buton_bagla_ve_kaydet(test_buton, f"Buton_{i}", mock_handler, f"servis_metodu_{i}")

        # Assert
        son_kayit_sayisi = kayit_sayisi()
        assert son_kayit_sayisi == baslangic_kayit_sayisi + buton_sayisi, "Her buton için ayrı kayıt oluşturulmalı"

        # Son eklenen kayıtları kontrol et
        kayitlar = kayitlari_listele()
        son_kayitlar = kayitlar[-buton_sayisi:]

        for i, kayit in enumerate(son_kayitlar):
            assert kayit["buton_adi"] == f"Buton_{i}", f"Buton_{i} adı doğru kaydedilmeli"
            assert kayit["handler_adi"] == f"handler_{i}", f"Handler_{i} adı doğru kaydedilmeli"
            assert kayit["servis_metodu"] == f"servis_metodu_{i}", f"Servis metodu_{i} doğru kaydedilmeli"

    def test_property_ayni_buton_tekrar_baglanma(self):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 6: Otomatik Kayıt Tutarlılığı (Tekrar Bağlama)**
        **Doğrular: Gereksinim 2.3**

        Aynı buton tekrar bağlandığında, yeni kayıt oluşturulmalıdır
        """
        # Arrange
        mock_servis_fabrikasi = MagicMock()

        class TestEkrani(TemelEkran):
            def __init__(self, servis_fabrikasi):
                super().__init__(servis_fabrikasi)

        test_ekrani = TestEkrani(mock_servis_fabrikasi)
        test_buton = QPushButton("Test Buton")

        def mock_handler():
            return "test_result"

        mock_handler.__name__ = "test_handler"

        baslangic_kayit_sayisi = kayit_sayisi()

        # Act - Aynı butonu iki kez bağla
        test_ekrani.buton_bagla_ve_kaydet(test_buton, "Test Buton", mock_handler, "test_servis")
        test_ekrani.buton_bagla_ve_kaydet(test_buton, "Test Buton", mock_handler, "test_servis")

        # Assert - İki ayrı kayıt oluşturulmalı
        son_kayit_sayisi = kayit_sayisi()
        assert son_kayit_sayisi == baslangic_kayit_sayisi + 2, "Tekrar bağlama durumunda yeni kayıt oluşturulmalı"

    def test_property_farkli_ekranlar_ayri_kayit(self):
        """
        **Özellik: ui-smoke-test-altyapisi, Özellik 6: Otomatik Kayıt Tutarlılığı (Farklı Ekranlar)**
        **Doğrular: Gereksinim 2.3**

        Farklı ekranlardaki aynı isimli butonlar ayrı kayıtlar oluşturmalıdır
        """
        # Arrange
        mock_servis_fabrikasi = MagicMock()

        class TestEkrani1(TemelEkran):
            def __init__(self, servis_fabrikasi):
                super().__init__(servis_fabrikasi)

        class TestEkrani2(TemelEkran):
            def __init__(self, servis_fabrikasi):
                super().__init__(servis_fabrikasi)

        test_ekrani1 = TestEkrani1(mock_servis_fabrikasi)
        test_ekrani2 = TestEkrani2(mock_servis_fabrikasi)

        test_buton1 = QPushButton("Ortak Buton")
        test_buton2 = QPushButton("Ortak Buton")

        def mock_handler():
            return "test_result"

        mock_handler.__name__ = "ortak_handler"

        baslangic_kayit_sayisi = kayit_sayisi()

        # Act - Farklı ekranlarda aynı isimli butonları bağla
        test_ekrani1.buton_bagla_ve_kaydet(test_buton1, "Ortak Buton", mock_handler, "servis1")
        test_ekrani2.buton_bagla_ve_kaydet(test_buton2, "Ortak Buton", mock_handler, "servis2")

        # Assert
        son_kayit_sayisi = kayit_sayisi()
        assert son_kayit_sayisi == baslangic_kayit_sayisi + 2, "Farklı ekranlar için ayrı kayıtlar oluşturulmalı"

        # Kayıtları kontrol et
        kayitlar = kayitlari_listele()
        son_kayitlar = kayitlar[-2:]

        ekran_adlari = {kayit["ekran_adi"] for kayit in son_kayitlar}
        assert "TestEkrani1" in ekran_adlari, "TestEkrani1 kaydı bulunmalı"
        assert "TestEkrani2" in ekran_adlari, "TestEkrani2 kaydı bulunmalı"


if __name__ == "__main__":
    unittest.main()
