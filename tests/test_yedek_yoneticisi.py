# Version: 0.1.0
# Last Update: 2025-12-18
# Module: tests.test_yedek_yoneticisi
# Description: YedekYoneticisi sınıfı için testler
# Changelog:
# - İlk versiyon: Temel testler oluşturuldu

"""
Yedek Yöneticisi Testleri

YedekYoneticisi sınıfının temel fonksiyonalitesini test eder.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from datetime import datetime

from sontechsp.uygulama.kod_kalitesi.refactoring_altyapi.yedek_yoneticisi import (
    YedekYoneticisi, YedekTuru, YedekDurumu
)


class TestYedekYoneticisi(unittest.TestCase):
    """YedekYoneticisi test sınıfı"""
    
    def setUp(self):
        """Test kurulumu"""
        # Geçici klasörler oluştur
        self.test_klasoru = Path(tempfile.mkdtemp())
        self.proje_klasoru = self.test_klasoru / "test_proje"
        self.yedek_klasoru = self.test_klasoru / "yedekler"
        
        # Test proje yapısı oluştur
        self.proje_klasoru.mkdir(parents=True)
        
        # Test dosyaları oluştur
        (self.proje_klasoru / "main.py").write_text(
            "# Test dosyası\nprint('Merhaba Dünya')\n",
            encoding='utf-8'
        )
        
        (self.proje_klasoru / "utils.py").write_text(
            "def test_fonksiyon():\n    return 'test'\n",
            encoding='utf-8'
        )
        
        # Alt klasör oluştur
        alt_klasor = self.proje_klasoru / "moduller"
        alt_klasor.mkdir()
        (alt_klasor / "helper.py").write_text(
            "class Helper:\n    pass\n",
            encoding='utf-8'
        )
        
        # YedekYoneticisi oluştur
        self.yedek_yoneticisi = YedekYoneticisi(
            proje_yolu=str(self.proje_klasoru),
            yedek_klasoru=str(self.yedek_klasoru),
            git_kullan=False  # Test için git kullanma
        )
    
    def tearDown(self):
        """Test temizliği"""
        # Logger'ları kapat
        if hasattr(self, 'yedek_yoneticisi'):
            for handler in self.yedek_yoneticisi.logger.handlers[:]:
                handler.close()
                self.yedek_yoneticisi.logger.removeHandler(handler)
        
        if self.test_klasoru.exists():
            shutil.rmtree(self.test_klasoru)
    
    def test_yedek_olustur(self):
        """Yedek oluşturma testi"""
        # Yedek oluştur
        yedek_bilgisi = self.yedek_yoneticisi.yedek_olustur(
            yedek_turu=YedekTuru.MANUEL,
            aciklama="Test yedegi",
            etiketler=["test", "manuel"]
        )
        
        # Kontroller
        self.assertIsNotNone(yedek_bilgisi)
        self.assertEqual(yedek_bilgisi.yedek_turu, YedekTuru.MANUEL)
        self.assertEqual(yedek_bilgisi.durum, YedekDurumu.TAMAMLANDI)
        self.assertEqual(yedek_bilgisi.aciklama, "Test yedegi")
        self.assertIn("test", yedek_bilgisi.etiketler)
        
        # Yedek dosyaları kontrol et
        yedek_yolu = Path(yedek_bilgisi.yedek_yolu)
        self.assertTrue(yedek_yolu.exists())
        
        proje_yedek = yedek_yolu / "proje"
        self.assertTrue(proje_yedek.exists())
        self.assertTrue((proje_yedek / "main.py").exists())
        self.assertTrue((proje_yedek / "utils.py").exists())
        self.assertTrue((proje_yedek / "moduller" / "helper.py").exists())
        
        # Metadata dosyası kontrol et
        metadata_dosyasi = yedek_yolu / "metadata.json"
        self.assertTrue(metadata_dosyasi.exists())
    
    def test_geri_alma(self):
        """Geri alma testi"""
        # İlk yedek oluştur
        yedek_bilgisi = self.yedek_yoneticisi.yedek_olustur(
            aciklama="Geri alma testi"
        )
        
        # Proje dosyalarını değiştir
        (self.proje_klasoru / "main.py").write_text(
            "# Değiştirilmiş dosya\nprint('Değişiklik')\n",
            encoding='utf-8'
        )
        
        # Yeni dosya ekle
        (self.proje_klasoru / "yeni_dosya.py").write_text(
            "# Yeni dosya\n",
            encoding='utf-8'
        )
        
        # Geri alma yap
        geri_alma_bilgisi = self.yedek_yoneticisi.geri_al(yedek_bilgisi.yedek_id)
        
        # Kontroller
        self.assertTrue(geri_alma_bilgisi.basarili)
        self.assertIsNone(geri_alma_bilgisi.hata_mesaji)
        
        # Dosya içeriği kontrol et
        main_icerik = (self.proje_klasoru / "main.py").read_text(encoding='utf-8')
        self.assertIn("Merhaba Dünya", main_icerik)
        self.assertNotIn("Değişiklik", main_icerik)
        
        # Yeni dosya silinmiş olmalı
        self.assertFalse((self.proje_klasoru / "yeni_dosya.py").exists())
    
    def test_yedek_listesi(self):
        """Yedek listesi testi"""
        # Birkaç yedek oluştur
        yedek1 = self.yedek_yoneticisi.yedek_olustur(
            yedek_turu=YedekTuru.MANUEL,
            etiketler=["test1"]
        )
        
        yedek2 = self.yedek_yoneticisi.yedek_olustur(
            yedek_turu=YedekTuru.OTOMATIK,
            etiketler=["test2"]
        )
        
        # Tüm yedekleri al
        tum_yedekler = self.yedek_yoneticisi.yedek_listesi_al()
        self.assertEqual(len(tum_yedekler), 2)
        
        # Türe göre filtrele
        manuel_yedekler = self.yedek_yoneticisi.yedek_listesi_al(
            yedek_turu=YedekTuru.MANUEL
        )
        self.assertEqual(len(manuel_yedekler), 1)
        self.assertEqual(manuel_yedekler[0].yedek_id, yedek1.yedek_id)
        
        # Etikete göre filtrele
        test2_yedekler = self.yedek_yoneticisi.yedek_listesi_al(etiket="test2")
        self.assertEqual(len(test2_yedekler), 1)
        self.assertEqual(test2_yedekler[0].yedek_id, yedek2.yedek_id)
    
    def test_yedek_sil(self):
        """Yedek silme testi"""
        # Yedek oluştur
        yedek_bilgisi = self.yedek_yoneticisi.yedek_olustur()
        yedek_yolu = Path(yedek_bilgisi.yedek_yolu)
        
        # Yedek var mı kontrol et
        self.assertTrue(yedek_yolu.exists())
        
        # Yedek sil
        basarili = self.yedek_yoneticisi.yedek_sil(yedek_bilgisi.yedek_id)
        self.assertTrue(basarili)
        
        # Yedek silinmiş mi kontrol et
        self.assertFalse(yedek_yolu.exists())
        
        # Kayıtlardan çıkmış mı kontrol et
        yedekler = self.yedek_yoneticisi.yedek_listesi_al()
        yedek_idleri = [y.yedek_id for y in yedekler]
        self.assertNotIn(yedek_bilgisi.yedek_id, yedek_idleri)
    
    def test_yedek_test_et(self):
        """Yedek test etme testi"""
        # Yedek oluştur
        yedek_bilgisi = self.yedek_yoneticisi.yedek_olustur()
        
        # Yedek test et
        test_sonucu = self.yedek_yoneticisi.yedek_test_et(yedek_bilgisi.yedek_id)
        self.assertTrue(test_sonucu)
        
        # Yedek dosyalarını boz
        yedek_yolu = Path(yedek_bilgisi.yedek_yolu)
        (yedek_yolu / "proje" / "main.py").unlink()
        
        # Test tekrar et
        test_sonucu = self.yedek_yoneticisi.yedek_test_et(yedek_bilgisi.yedek_id)
        self.assertFalse(test_sonucu)
    
    def test_kayit_kaliciligi(self):
        """Kayıt kalıcılığı testi"""
        # Yedek oluştur
        yedek_bilgisi = self.yedek_yoneticisi.yedek_olustur(
            aciklama="Kalıcılık testi"
        )
        
        # Yeni YedekYoneticisi oluştur (kayıtları yükler)
        yeni_yonetici = YedekYoneticisi(
            proje_yolu=str(self.proje_klasoru),
            yedek_klasoru=str(self.yedek_klasoru),
            git_kullan=False
        )
        
        # Yedek kayıtları yüklenmiş mi kontrol et
        yedekler = yeni_yonetici.yedek_listesi_al()
        self.assertEqual(len(yedekler), 1)
        self.assertEqual(yedekler[0].yedek_id, yedek_bilgisi.yedek_id)
        self.assertEqual(yedekler[0].aciklama, "Kalıcılık testi")


if __name__ == '__main__':
    unittest.main()