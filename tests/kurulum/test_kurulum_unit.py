# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.kurulum.test_kurulum_unit
# Description: Kurulum modülü unit testleri
# Changelog:
# - Temel unit testler oluşturuldu

"""
Kurulum modülü unit testleri
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from sontechsp.uygulama.kurulum import (
    KurulumHatasi,
    DogrulamaHatasi,
    KlasorHatasi,
    AyarHatasi,
    MigrationHatasi,
    KullaniciHatasi,
    logger,
)


class TestKurulumHatalari(unittest.TestCase):
    """Kurulum hata sınıfları için unit testler"""

    def test_kurulum_hatasi_temel_sinif(self):
        """KurulumHatasi temel sınıfının çalıştığını test et"""
        hata = KurulumHatasi("Test hatası")
        self.assertEqual(str(hata), "Test hatası")
        self.assertIsInstance(hata, Exception)

    def test_dogrulama_hatasi(self):
        """DogrulamaHatasi sınıfının çalıştığını test et"""
        hata = DogrulamaHatasi("Veritabanı bağlantı hatası")
        self.assertEqual(str(hata), "Veritabanı bağlantı hatası")
        self.assertIsInstance(hata, KurulumHatasi)

    def test_klasor_hatasi(self):
        """KlasorHatasi sınıfının çalıştığını test et"""
        hata = KlasorHatasi("Klasör oluşturulamadı")
        self.assertEqual(str(hata), "Klasör oluşturulamadı")
        self.assertIsInstance(hata, KurulumHatasi)

    def test_ayar_hatasi(self):
        """AyarHatasi sınıfının çalıştığını test et"""
        hata = AyarHatasi("Ayar dosyası okunamadı")
        self.assertEqual(str(hata), "Ayar dosyası okunamadı")
        self.assertIsInstance(hata, KurulumHatasi)

    def test_migration_hatasi(self):
        """MigrationHatasi sınıfının çalıştığını test et"""
        hata = MigrationHatasi("Migration başarısız")
        self.assertEqual(str(hata), "Migration başarısız")
        self.assertIsInstance(hata, KurulumHatasi)

    def test_kullanici_hatasi(self):
        """KullaniciHatasi sınıfının çalıştığını test et"""
        hata = KullaniciHatasi("Kullanıcı oluşturulamadı")
        self.assertEqual(str(hata), "Kullanıcı oluşturulamadı")
        self.assertIsInstance(hata, KurulumHatasi)


class TestKurulumLogger(unittest.TestCase):
    """Kurulum logger testi"""

    def test_logger_mevcut(self):
        """Logger'ın mevcut olduğunu test et"""
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "uygulama.kurulum")


class TestYardimcilar(unittest.TestCase):
    """Test yardımcı fonksiyonları"""

    def setUp(self):
        """Her test öncesi geçici dizin oluştur"""
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Her test sonrası geçici dizini temizle"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_gecici_dizin_olusturma(self):
        """Geçici dizin oluşturma yardımcısını test et"""
        self.assertTrue(self.test_dir.exists())
        self.assertTrue(self.test_dir.is_dir())

    def test_gecici_dosya_olusturma(self):
        """Geçici dosya oluşturma yardımcısını test et"""
        test_file = self.test_dir / "test.txt"
        test_file.write_text("test içeriği")

        self.assertTrue(test_file.exists())
        self.assertEqual(test_file.read_text(), "test içeriği")


if __name__ == "__main__":
    unittest.main()
