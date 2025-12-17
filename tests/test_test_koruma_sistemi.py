# Version: 0.1.0
# Last Update: 2025-12-18
# Module: tests.test_test_koruma_sistemi
# Description: TestKorumaSistemi sınıfı için testler
# Changelog:
# - İlk versiyon: Temel testler oluşturuldu

"""
Test Koruma Sistemi Testleri

TestKorumaSistemi sınıfının temel fonksiyonalitesini test eder.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from sontechsp.uygulama.kod_kalitesi.refactoring_altyapi.test_koruma_sistemi import (
    TestKorumaSistemi, TestTuru, TestDurumu
)


class TestTestKorumaSistemi(unittest.TestCase):
    """TestKorumaSistemi test sınıfı"""
    
    def setUp(self):
        """Test kurulumu"""
        # Geçici klasörler oluştur
        self.test_klasoru = Path(tempfile.mkdtemp())
        self.proje_klasoru = self.test_klasoru / "test_proje"
        self.test_dosyalari_klasoru = self.proje_klasoru / "tests"
        
        # Proje yapısı oluştur
        self.proje_klasoru.mkdir(parents=True)
        self.test_dosyalari_klasoru.mkdir(parents=True)
        
        # Test dosyaları oluştur
        self._test_dosyalari_olustur()
        
        # TestKorumaSistemi oluştur
        self.test_koruma = TestKorumaSistemi(
            proje_yolu=str(self.proje_klasoru),
            test_klasoru="tests"
        )
    
    def tearDown(self):
        """Test temizliği"""
        # Logger'ları kapat
        if hasattr(self, 'test_koruma'):
            for handler in self.test_koruma.logger.handlers[:]:
                handler.close()
                self.test_koruma.logger.removeHandler(handler)
        
        if self.test_klasoru.exists():
            shutil.rmtree(self.test_klasoru)
    
    def _test_dosyalari_olustur(self):
        """Test dosyalarını oluşturur"""
        # Unit test dosyası
        unit_test = '''
import unittest
from sontechsp.uygulama.moduller import test_modulu

class TestModul(unittest.TestCase):
    def test_basic_function(self):
        """Temel fonksiyon testi"""
        self.assertTrue(True)
    
    def test_another_function(self):
        """Başka bir fonksiyon testi"""
        self.assertEqual(1, 1)

if __name__ == '__main__':
    unittest.main()
'''
        
        # Property test dosyası
        property_test = '''
import unittest
from hypothesis import given, strategies as st

class TestPropertyTests(unittest.TestCase):
    def test_property_example(self):
        """Property test örneği"""
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
'''
        
        # Integration test dosyası
        integration_test = '''
import unittest

class TestIntegration(unittest.TestCase):
    def test_integration_example(self):
        """Integration test örneği"""
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
'''
        
        # Test dosyalarını yaz
        (self.test_dosyalari_klasoru / "test_modul.py").write_text(
            unit_test, encoding='utf-8'
        )
        (self.test_dosyalari_klasoru / "test_property_example.py").write_text(
            property_test, encoding='utf-8'
        )
        (self.test_dosyalari_klasoru / "test_integration_example.py").write_text(
            integration_test, encoding='utf-8'
        )
    
    def test_mevcut_testleri_analiz_et(self):
        """Mevcut testleri analiz etme testi"""
        # Testleri analiz et
        test_bilgileri = self.test_koruma.mevcut_testleri_analiz_et()
        
        # Kontroller
        self.assertGreater(len(test_bilgileri), 0)
        
        # Test türlerini kontrol et
        test_turleri = [bilgi.test_turu for bilgi in test_bilgileri.values()]
        self.assertIn(TestTuru.UNIT, test_turleri)
        self.assertIn(TestTuru.PROPERTY, test_turleri)
        self.assertIn(TestTuru.INTEGRATION, test_turleri)
        
        # Test adlarını kontrol et
        test_adlari = [bilgi.test_adi for bilgi in test_bilgileri.values()]
        self.assertIn('test_basic_function', test_adlari)
        self.assertIn('test_property_example', test_adlari)
        self.assertIn('test_integration_example', test_adlari)
    
    def test_test_guncelleme_plani_olustur(self):
        """Test güncelleme planı oluşturma testi"""
        # Önce testleri analiz et
        self.test_koruma.mevcut_testleri_analiz_et()
        
        # Güncelleme planı oluştur
        degisen_dosyalar = ["sontechsp/uygulama/moduller/test_modulu.py"]
        yeni_dosyalar = ["sontechsp/uygulama/moduller/yeni_modul.py"]
        silinen_dosyalar = ["sontechsp/uygulama/moduller/eski_modul.py"]
        
        plan = self.test_koruma.refactoring_sonrasi_test_guncelleme_plani_olustur(
            degisen_dosyalar=degisen_dosyalar,
            yeni_dosyalar=yeni_dosyalar,
            silinen_dosyalar=silinen_dosyalar
        )
        
        # Kontroller
        self.assertIsNotNone(plan)
        self.assertIsInstance(plan.guncellenecek_testler, list)
        self.assertIsInstance(plan.yeni_testler, list)
        self.assertIsInstance(plan.silinecek_testler, list)
        self.assertIsInstance(plan.import_guncellemeleri, dict)
        
        # Yeni test dosyası oluşturulmalı
        self.assertIn("test_yeni_modul.py", plan.yeni_testler)
    
    def test_test_durumu_raporu_olustur(self):
        """Test durumu raporu oluşturma testi"""
        # Önce testleri analiz et
        self.test_koruma.mevcut_testleri_analiz_et()
        
        # Rapor oluştur
        rapor = self.test_koruma.test_durumu_raporu_olustur()
        
        # Kontroller
        self.assertIn('toplam_test', rapor)
        self.assertIn('gecen_testler', rapor)
        self.assertIn('basarisiz_testler', rapor)
        self.assertIn('basari_orani', rapor)
        self.assertIn('test_turleri', rapor)
        self.assertIn('coverage', rapor)
        
        # Test sayıları
        self.assertGreater(rapor['toplam_test'], 0)
        self.assertGreaterEqual(rapor['basari_orani'], 0)
        self.assertLessEqual(rapor['basari_orani'], 100)
        
        # Test türleri
        self.assertIn('unit', rapor['test_turleri'])
        self.assertIn('property', rapor['test_turleri'])
        self.assertIn('integration', rapor['test_turleri'])
    
    def test_yeni_test_dosyasi_olustur(self):
        """Yeni test dosyası oluşturma testi"""
        # Yeni test dosyası oluştur
        yeni_test_dosyasi = "test_yeni_modul.py"
        self.test_koruma._yeni_test_dosyasi_olustur(yeni_test_dosyasi)
        
        # Dosya oluşturulmuş mu kontrol et
        test_yolu = self.test_dosyalari_klasoru / yeni_test_dosyasi
        self.assertTrue(test_yolu.exists())
        
        # Dosya içeriği kontrol et
        icerik = test_yolu.read_text(encoding='utf-8')
        self.assertIn('class TestYeniModul', icerik)
        self.assertIn('def test_placeholder', icerik)
        self.assertIn('unittest.TestCase', icerik)


if __name__ == '__main__':
    unittest.main()