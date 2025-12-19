# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.test_performans_bellek
# Description: Performans ve bellek kullanımı testleri
# Changelog:
# - İlk sürüm: Performans ve bellek testleri

import os
import time
import tempfile
import shutil
import psutil
import gc
from pathlib import Path
import pytest
from typing import List, Dict

from sontechsp.uygulama.kod_kalitesi.cli_arayuzu import KodKalitesiCLI, CLIKonfigurasyonu
from sontechsp.uygulama.kod_kalitesi.refactoring_orkestratori import RefactoringOrkestratori


class PerformansOlcucu:
    """Performans ölçüm yardımcı sınıfı"""
    
    def __init__(self):
        self.baslangic_zamani = None
        self.baslangic_bellek = None
        self.process = psutil.Process()
    
    def baslat(self):
        """Ölçümü başlat"""
        gc.collect()  # Garbage collection
        self.baslangic_zamani = time.time()
        self.baslangic_bellek = self.process.memory_info().rss
    
    def bitir(self) -> Dict[str, float]:
        """Ölçümü bitir ve sonuçları döndür"""
        bitis_zamani = time.time()
        bitis_bellek = self.process.memory_info().rss
        
        return {
            'sure_saniye': bitis_zamani - self.baslangic_zamani,
            'bellek_mb': (bitis_bellek - self.baslangic_bellek) / (1024 * 1024),
            'toplam_bellek_mb': bitis_bellek / (1024 * 1024)
        }


class TestPerformansAnalizi:
    """Performans analizi testleri"""
    
    def _buyuk_proje_olustur(self, dosya_sayisi: int, dosya_boyutu: int) -> str:
        """Test için büyük proje oluştur"""
        temp_dir = tempfile.mkdtemp(prefix=f'perf_test_{dosya_sayisi}_')
        
        for i in range(dosya_sayisi):
            dosya = Path(temp_dir) / f'modul_{i}.py'
            
            # Belirtilen boyutta dosya oluştur
            satirlar = []
            satirlar.append(f'# Modül {i}')
            satirlar.append(f'# Bu dosya performans testi için oluşturuldu')
            satirlar.append('')
            
            for j in range(dosya_boyutu - 10):  # Header için 10 satır ayrıldı
                if j % 10 == 0:
                    satirlar.append(f'def fonksiyon_{j}():')
                    satirlar.append(f'    return {j}')
                    satirlar.append('')
                else:
                    satirlar.append(f'# Satır {j}')
            
            dosya.write_text('\n'.join(satirlar), encoding='utf-8')
        
        return temp_dir
    
    @pytest.mark.slow
    def test_kucuk_proje_performansi(self):
        """Küçük proje performans testi (10 dosya, 50 satır)"""
        olcucu = PerformansOlcucu()
        temp_dir = None
        
        try:
            temp_dir = self._buyuk_proje_olustur(dosya_sayisi=10, dosya_boyutu=50)
            
            config = CLIKonfigurasyonu(
                proje_yolu=temp_dir,
                sadece_analiz=True
            )
            cli = KodKalitesiCLI(config)
            
            olcucu.baslat()
            sonuc = cli._sadece_analiz_yap()
            metrikler = olcucu.bitir()
            
            # Performans kriterleri
            assert sonuc == 0, "Analiz başarısız"
            assert metrikler['sure_saniye'] < 5, f"Çok yavaş: {metrikler['sure_saniye']:.2f}s"
            assert metrikler['bellek_mb'] < 50, f"Çok fazla bellek: {metrikler['bellek_mb']:.2f}MB"
            
            print(f"Küçük proje: {metrikler['sure_saniye']:.2f}s, {metrikler['bellek_mb']:.2f}MB")
            
        finally:
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.slow
    def test_orta_proje_performansi(self):
        """Orta proje performans testi (50 dosya, 100 satır)"""
        olcucu = PerformansOlcucu()
        temp_dir = None
        
        try:
            temp_dir = self._buyuk_proje_olustur(dosya_sayisi=50, dosya_boyutu=100)
            
            config = CLIKonfigurasyonu(
                proje_yolu=temp_dir,
                sadece_analiz=True
            )
            cli = KodKalitesiCLI(config)
            
            olcucu.baslat()
            sonuc = cli._sadece_analiz_yap()
            metrikler = olcucu.bitir()
            
            # Performans kriterleri
            assert sonuc == 0, "Analiz başarısız"
            assert metrikler['sure_saniye'] < 15, f"Çok yavaş: {metrikler['sure_saniye']:.2f}s"
            assert metrikler['bellek_mb'] < 100, f"Çok fazla bellek: {metrikler['bellek_mb']:.2f}MB"
            
            print(f"Orta proje: {metrikler['sure_saniye']:.2f}s, {metrikler['bellek_mb']:.2f}MB")
            
        finally:
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.slow
    def test_buyuk_proje_performansi(self):
        """Büyük proje performans testi (100 dosya, 200 satır)"""
        olcucu = PerformansOlcucu()
        temp_dir = None
        
        try:
            temp_dir = self._buyuk_proje_olustur(dosya_sayisi=100, dosya_boyutu=200)
            
            config = CLIKonfigurasyonu(
                proje_yolu=temp_dir,
                sadece_analiz=True
            )
            cli = KodKalitesiCLI(config)
            
            olcucu.baslat()
            sonuc = cli._sadece_analiz_yap()
            metrikler = olcucu.bitir()
            
            # Performans kriterleri (daha gevşek)
            assert sonuc == 0, "Analiz başarısız"
            assert metrikler['sure_saniye'] < 60, f"Çok yavaş: {metrikler['sure_saniye']:.2f}s"
            assert metrikler['bellek_mb'] < 200, f"Çok fazla bellek: {metrikler['bellek_mb']:.2f}MB"
            
            print(f"Büyük proje: {metrikler['sure_saniye']:.2f}s, {metrikler['bellek_mb']:.2f}MB")
            
        finally:
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)


class TestBellekYonetimi:
    """Bellek yönetimi testleri"""
    
    def test_bellek_sizintisi_kontrolu(self):
        """Bellek sızıntısı kontrolü"""
        olcucu = PerformansOlcucu()
        temp_dir = None
        
        try:
            # Küçük test projesi
            temp_dir = tempfile.mkdtemp(prefix='bellek_test_')
            test_dosya = Path(temp_dir) / 'test.py'
            test_dosya.write_text('def test(): return "test"')
            
            config = CLIKonfigurasyonu(
                proje_yolu=temp_dir,
                sadece_analiz=True
            )
            
            # Çoklu analiz çalıştır
            baslangic_bellek = psutil.Process().memory_info().rss
            
            for i in range(10):
                cli = KodKalitesiCLI(config)
                cli._sadece_analiz_yap()
                
                # Her 5 iterasyonda garbage collection
                if i % 5 == 0:
                    gc.collect()
            
            bitis_bellek = psutil.Process().memory_info().rss
            bellek_artisi = (bitis_bellek - baslangic_bellek) / (1024 * 1024)
            
            # Bellek artışı 20MB'dan az olmalı
            assert bellek_artisi < 20, f"Bellek sızıntısı şüphesi: {bellek_artisi:.2f}MB"
            
        finally:
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_buyuk_dosya_bellek_kullanimi(self):
        """Büyük dosya bellek kullanımı"""
        olcucu = PerformansOlcucu()
        temp_dir = None
        
        try:
            # Çok büyük dosya oluştur (1000+ satır)
            temp_dir = tempfile.mkdtemp(prefix='buyuk_dosya_test_')
            buyuk_dosya = Path(temp_dir) / 'cok_buyuk.py'
            
            satirlar = ['# Çok büyük dosya']
            for i in range(1000):
                satirlar.append(f'veri_{i} = "test_{i}"')
            
            buyuk_dosya.write_text('\n'.join(satirlar), encoding='utf-8')
            
            config = CLIKonfigurasyonu(
                proje_yolu=temp_dir,
                sadece_analiz=True
            )
            cli = KodKalitesiCLI(config)
            
            olcucu.baslat()
            sonuc = cli._sadece_analiz_yap()
            metrikler = olcucu.bitir()
            
            # Büyük dosya için bellek kullanımı makul olmalı
            assert sonuc == 0, "Analiz başarısız"
            assert metrikler['bellek_mb'] < 100, f"Büyük dosya için çok fazla bellek: {metrikler['bellek_mb']:.2f}MB"
            
        finally:
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)


class TestEsZamanliPerformans:
    """Eş zamanlı performans testleri"""
    
    def test_coklu_analiz_performansi(self):
        """Çoklu analiz performansı"""
        import threading
        import queue
        
        temp_dir = None
        
        try:
            # Test projesi oluştur
            temp_dir = tempfile.mkdtemp(prefix='coklu_test_')
            for i in range(20):
                dosya = Path(temp_dir) / f'modul_{i}.py'
                dosya.write_text(f'def fonksiyon_{i}(): return {i}')
            
            # Sonuç kuyruğu
            sonuc_kuyrugu = queue.Queue()
            
            def analiz_yap():
                """Analiz thread fonksiyonu"""
                try:
                    config = CLIKonfigurasyonu(
                        proje_yolu=temp_dir,
                        sadece_analiz=True
                    )
                    cli = KodKalitesiCLI(config)
                    
                    baslangic = time.time()
                    sonuc = cli._sadece_analiz_yap()
                    bitis = time.time()
                    
                    sonuc_kuyrugu.put({
                        'sonuc': sonuc,
                        'sure': bitis - baslangic,
                        'hata': None
                    })
                except Exception as e:
                    sonuc_kuyrugu.put({
                        'sonuc': -1,
                        'sure': 0,
                        'hata': str(e)
                    })
            
            # 3 thread başlat
            threadler = []
            for i in range(3):
                thread = threading.Thread(target=analiz_yap)
                threadler.append(thread)
                thread.start()
            
            # Threadleri bekle
            for thread in threadler:
                thread.join(timeout=30)
            
            # Sonuçları kontrol et
            sonuclar = []
            while not sonuc_kuyrugu.empty():
                sonuclar.append(sonuc_kuyrugu.get())
            
            assert len(sonuclar) == 3, "Tüm threadler tamamlanmadı"
            
            for sonuc in sonuclar:
                assert sonuc['hata'] is None, f"Thread hatası: {sonuc['hata']}"
                assert sonuc['sonuc'] == 0, "Analiz başarısız"
                assert sonuc['sure'] < 10, f"Thread çok yavaş: {sonuc['sure']:.2f}s"
            
        finally:
            if temp_dir:
                shutil.rmtree(temp_dir, ignore_errors=True)


class TestPerformansRegresyonu:
    """Performans regresyon testleri"""
    
    def test_performans_baseline(self):
        """Performans baseline testi"""
        # Standart test projesi
        temp_dir = tempfile.mkdtemp(prefix='baseline_test_')
        
        try:
            # 25 dosya, 75 satır (orta boyut)
            for i in range(25):
                dosya = Path(temp_dir) / f'modul_{i}.py'
                satirlar = [f'# Modül {i}']
                
                for j in range(70):
                    if j % 5 == 0:
                        satirlar.append(f'def fonksiyon_{j}():')
                        satirlar.append(f'    return {j}')
                    else:
                        satirlar.append(f'# Satır {j}')
                
                dosya.write_text('\n'.join(satirlar), encoding='utf-8')
            
            # Performans ölçümü
            olcucu = PerformansOlcucu()
            config = CLIKonfigurasyonu(
                proje_yolu=temp_dir,
                sadece_analiz=True
            )
            cli = KodKalitesiCLI(config)
            
            olcucu.baslat()
            sonuc = cli._sadece_analiz_yap()
            metrikler = olcucu.bitir()
            
            # Baseline kriterler
            assert sonuc == 0, "Baseline analiz başarısız"
            assert metrikler['sure_saniye'] < 10, f"Baseline çok yavaş: {metrikler['sure_saniye']:.2f}s"
            assert metrikler['bellek_mb'] < 75, f"Baseline çok fazla bellek: {metrikler['bellek_mb']:.2f}MB"
            
            # Performans metriklerini kaydet (gerçek uygulamada dosyaya yazılabilir)
            print(f"Baseline performans: {metrikler['sure_saniye']:.2f}s, {metrikler['bellek_mb']:.2f}MB")
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_performans_kararliligi(self):
        """Performans kararlılığı testi"""
        temp_dir = tempfile.mkdtemp(prefix='kararlilık_test_')
        
        try:
            # Sabit test projesi
            for i in range(10):
                dosya = Path(temp_dir) / f'modul_{i}.py'
                dosya.write_text(f'def fonksiyon_{i}(): return {i}')
            
            # 5 kez analiz yap
            sureler = []
            bellek_kullanimi = []
            
            for i in range(5):
                olcucu = PerformansOlcucu()
                config = CLIKonfigurasyonu(
                    proje_yolu=temp_dir,
                    sadece_analiz=True
                )
                cli = KodKalitesiCLI(config)
                
                olcucu.baslat()
                sonuc = cli._sadece_analiz_yap()
                metrikler = olcucu.bitir()
                
                assert sonuc == 0, f"Analiz {i+1} başarısız"
                sureler.append(metrikler['sure_saniye'])
                bellek_kullanimi.append(metrikler['bellek_mb'])
                
                # Garbage collection
                gc.collect()
            
            # Kararlılık kontrolü
            ortalama_sure = sum(sureler) / len(sureler)
            max_sure = max(sureler)
            min_sure = min(sureler)
            
            # Maksimum %50 varyasyon kabul edilebilir
            varyasyon = (max_sure - min_sure) / ortalama_sure
            assert varyasyon < 0.5, f"Performans çok değişken: %{varyasyon*100:.1f}"
            
            print(f"Performans kararlılığı: Ort={ortalama_sure:.2f}s, Var=%{varyasyon*100:.1f}")
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)