# Version: 0.1.0
# Last Update: 2024-12-18
# Module: tests.test_stub_servis_basit
# Description: Stub servis loglama basit testleri
# Changelog:
# - İlk versiyon: Basit stub servis testleri

import unittest

from uygulama.arayuz.log_sistemi import (
    LogDurumu,
    stub_servis_loglama,
    log_kayitlarini_listele,
    log_kayitlarini_temizle,
    log_sayisi,
)


class TestStubServisBasit(unittest.TestCase):
    """Stub servis loglama basit testleri"""

    def setUp(self):
        """Her test öncesi log kayıtlarını temizle"""
        log_kayitlarini_temizle()

    def tearDown(self):
        """Her test sonrası log kayıtlarını temizle"""
        log_kayitlarini_temizle()

    def test_stub_servis_temel_loglama(self):
        """Temel stub servis loglama testi"""
        # Başlangıç durumu
        self.assertEqual(log_sayisi(), 0)

        # Stub servis loglama
        stub_servis_loglama(
            ekran_adi="Test Ekranı",
            buton_adi="Test Butonu",
            handler_adi="test_handler",
            servis_metodu="test_stub_servis",
        )

        # Kontrol
        self.assertEqual(log_sayisi(), 1)

        log_kayitlari = log_kayitlarini_listele()
        log_kaydi = log_kayitlari[0]

        self.assertEqual(log_kaydi["ekran_adi"], "Test Ekranı")
        self.assertEqual(log_kaydi["buton_adi"], "Test Butonu")
        self.assertEqual(log_kaydi["handler_adi"], "test_handler")
        self.assertEqual(log_kaydi["servis_metodu"], "test_stub_servis")
        self.assertEqual(log_kaydi["durum"], LogDurumu.STUB.value)
        self.assertEqual(log_kaydi["detay"], "stub çağrıldı")

    def test_stub_servis_ozel_detay(self):
        """Özel detay ile stub servis loglama testi"""
        # Başlangıç durumu
        self.assertEqual(log_sayisi(), 0)

        ozel_detay = "Özel test detayı"

        # Stub servis loglama
        stub_servis_loglama(
            ekran_adi="Test Ekranı",
            buton_adi="Test Butonu",
            handler_adi="test_handler",
            servis_metodu="test_stub_servis",
            detay=ozel_detay,
        )

        # Kontrol
        self.assertEqual(log_sayisi(), 1)

        log_kayitlari = log_kayitlarini_listele()
        log_kaydi = log_kayitlari[0]

        self.assertEqual(log_kaydi["detay"], ozel_detay)
        self.assertEqual(log_kaydi["durum"], LogDurumu.STUB.value)


if __name__ == "__main__":
    unittest.main()
