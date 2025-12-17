# Version: 0.1.0
# Last Update: 2025-12-18
# Module: tests.test_import_guncelleme_sistemi
# Description: ImportGuncellemeSistemi sınıfı için testler
# Changelog:
# - İlk versiyon: Temel testler oluşturuldu

"""
Import Güncelleme Sistemi Testleri

ImportGuncellemeSistemi sınıfının temel fonksiyonalitesini test eder.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from sontechsp.uygulama.kod_kalitesi.refactoring_altyapi.import_guncelleme_sistemi import (
    ImportGuncellemeSistemi, ImportTuru, BagimlilikTuru
)


class TestImportGuncellemeSistemi(unittest.TestCase):
    """ImportGuncellemeSistemi test sınıfı"""
    
    def setUp(self):
        """Test kurulumu"""
        # Geçici klasörler oluştur
        self.test_klasoru = Path(tempfile.mkdtemp())
        self.proje_klasoru = self.test_klasoru / "test_proje"
        
        # Proje yapısı oluştur
        self.proje_klasoru.mkdir(parents=True)
        
        # Test dosyaları oluştur
        self._test_dosyalari_olustur()
        
        # ImportGuncellemeSistemi oluştur
        self.import_sistemi = ImportGuncellemeSistemi(
            proje_yolu=str(self.proje_klasoru),
            proje_paketi="test_proje"
        )
    
    def tearDown(self):
        """Test temizliği"""
        # Logger'ları kapat
        if hasattr(self, 'import_sistemi'):
            for handler in self.import_sistemi.logger.handlers[:]:
                handler.close()
                self.import_sistemi.logger.removeHandler(handler)
        
        if self.test_klasoru.exists():
            shutil.rmtree(self.test_klasoru)
    
    def _test_dosyalari_olustur(self):
        """Test dosyalarını oluşturur"""
        # Ana modül
        ana_modul = '''
import os
import json
from pathlib import Path
from test_proje.moduller import yardimci_modul
from test_proje.servisler.ana_servis import AnaServis
from .yerel_modul import yerel_fonksiyon

class AnaModul:
    def __init__(self):
        self.servis = AnaServis()
'''
        
        # Yardımcı modül
        yardimci_modul = '''
import sys
from typing import List, Dict
from test_proje.utils import helper

def yardimci_fonksiyon():
    return "yardım"
'''
        
        # Yerel modül
        yerel_modul = '''
from datetime import datetime

def yerel_fonksiyon():
    return datetime.now()
'''
        
        # Servis modülü
        servis_modul = '''
import logging
from test_proje.moduller.yardimci_modul import yardimci_fonksiyon

class AnaServis:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
'''
        
        # Klasör yapısını oluştur
        moduller_klasoru = self.proje_klasoru / "moduller"
        moduller_klasoru.mkdir(parents=True)
        
        servisler_klasoru = self.proje_klasoru / "servisler"
        servisler_klasoru.mkdir(parents=True)
        
        # Dosyaları yaz
        (self.proje_klasoru / "ana_modul.py").write_text(ana_modul, encoding='utf-8')
        (self.proje_klasoru / "yerel_modul.py").write_text(yerel_modul, encoding='utf-8')
        (moduller_klasoru / "yardimci_modul.py").write_text(yardimci_modul, encoding='utf-8')
        (servisler_klasoru / "ana_servis.py").write_text(servis_modul, encoding='utf-8')
        
        # __init__.py dosyaları
        (moduller_klasoru / "__init__.py").write_text("", encoding='utf-8')
        (servisler_klasoru / "__init__.py").write_text("", encoding='utf-8')
    
    def test_proje_importlarini_analiz_et(self):
        """Proje import analizi testi"""
        # Import'ları analiz et
        import_bilgileri = self.import_sistemi.proje_importlarini_analiz_et()
        
        # Kontroller
        self.assertGreater(len(import_bilgileri), 0)
        
        # Ana modül import'larını kontrol et
        ana_modul_dosyasi = None
        for dosya_yolu in import_bilgileri.keys():
            if "ana_modul.py" in dosya_yolu:
                ana_modul_dosyasi = dosya_yolu
                break
        
        self.assertIsNotNone(ana_modul_dosyasi)
        
        ana_modul_importlari = import_bilgileri[ana_modul_dosyasi]
        self.assertGreater(len(ana_modul_importlari), 0)
        
        # Import türlerini kontrol et
        import_turleri = [imp.import_turu for imp in ana_modul_importlari]
        self.assertIn(ImportTuru.DIRECT, import_turleri)
        self.assertIn(ImportTuru.FROM, import_turleri)
        self.assertIn(ImportTuru.RELATIVE, import_turleri)
        
        # Bağımlılık türlerini kontrol et
        bagimlilik_turleri = [imp.bagimlilik_turu for imp in ana_modul_importlari]
        self.assertIn(BagimlilikTuru.STANDARD, bagimlilik_turleri)
        self.assertIn(BagimlilikTuru.INTERNAL, bagimlilik_turleri)
    
    def test_bagimlilik_grafi_olustur(self):
        """Bağımlılık grafı oluşturma testi"""
        # Önce import'ları analiz et
        self.import_sistemi.proje_importlarini_analiz_et()
        
        # Bağımlılık grafı oluştur
        grafi = self.import_sistemi.bagimlilik_grafi_olustur()
        
        # Kontroller
        self.assertGreater(len(grafi.dugumler), 0)
        self.assertIsInstance(grafi.kenarlar, dict)
        
        # Düğümlerin varlığını kontrol et
        dugum_adlari = list(grafi.dugumler)
        self.assertTrue(any("ana_modul" in dugum for dugum in dugum_adlari))
        self.assertTrue(any("yardimci_modul" in dugum for dugum in dugum_adlari))
    
    def test_donguleri_tespit_et(self):
        """Döngüsel import tespiti testi"""
        # Önce analiz ve grafi oluştur
        self.import_sistemi.proje_importlarini_analiz_et()
        self.import_sistemi.bagimlilik_grafi_olustur()
        
        # Döngüleri tespit et
        dongular = self.import_sistemi.donguleri_tespit_et()
        
        # Kontroller
        self.assertIsInstance(dongular, list)
        # Bu test verilerinde döngü olmamalı
        self.assertEqual(len(dongular), 0)
    
    def test_import_guncelleme_plani_olustur(self):
        """Import güncelleme planı oluşturma testi"""
        # Önce import'ları analiz et
        self.import_sistemi.proje_importlarini_analiz_et()
        
        # Dosya değişiklikleri tanımla
        dosya_degisiklikleri = {
            str(self.proje_klasoru / "moduller" / "yardimci_modul.py"): 
            str(self.proje_klasoru / "moduller" / "yeni_yardimci_modul.py")
        }
        
        # Güncelleme planı oluştur
        plan = self.import_sistemi.refactoring_sonrasi_import_guncelleme_plani_olustur(
            dosya_degisiklikleri=dosya_degisiklikleri
        )
        
        # Kontroller
        self.assertIsNotNone(plan)
        self.assertIsInstance(plan.guncellenecek_importlar, dict)
        self.assertIsInstance(plan.silinecek_importlar, dict)
        self.assertIsInstance(plan.yeniden_organize_edilecek_dosyalar, list)
        
        # Güncelleme olmalı
        self.assertGreater(len(plan.guncellenecek_importlar), 0)
    
    def test_import_analiz_raporu_olustur(self):
        """Import analiz raporu oluşturma testi"""
        # Önce analiz et
        self.import_sistemi.proje_importlarini_analiz_et()
        self.import_sistemi.bagimlilik_grafi_olustur()
        self.import_sistemi.donguleri_tespit_et()
        
        # Rapor oluştur
        rapor = self.import_sistemi.import_analiz_raporu_olustur()
        
        # Kontroller
        self.assertIn('toplam_dosya', rapor)
        self.assertIn('toplam_import', rapor)
        self.assertIn('bagimlilik_dagilimi', rapor)
        self.assertIn('import_turu_dagilimi', rapor)
        self.assertIn('dongular', rapor)
        
        # Sayısal değerler
        self.assertGreater(rapor['toplam_dosya'], 0)
        self.assertGreater(rapor['toplam_import'], 0)
        self.assertGreaterEqual(rapor['ortalama_import_per_dosya'], 0)
        
        # Dağılım verileri
        self.assertIn('internal', rapor['bagimlilik_dagilimi'])
        self.assertIn('external', rapor['bagimlilik_dagilimi'])
        self.assertIn('standard', rapor['bagimlilik_dagilimi'])
        
        self.assertIn('direct', rapor['import_turu_dagilimi'])
        self.assertIn('from', rapor['import_turu_dagilimi'])
        self.assertIn('relative', rapor['import_turu_dagilimi'])


if __name__ == '__main__':
    unittest.main()