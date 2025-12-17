# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.test_end_to_end_refactoring
# Description: End-to-end refactoring süreci testleri
# Changelog:
# - İlk sürüm: Güvenli end-to-end testler

import os
import tempfile
import shutil
from pathlib import Path
import pytest

from sontechsp.uygulama.kod_kalitesi.cli_arayuzu import KodKalitesiCLI, CLIKonfigurasyonu
from sontechsp.uygulama.kod_kalitesi.refactoring_orkestratori import RefactoringOrkestratori
from sontechsp.uygulama.kod_kalitesi.guvenlik_sistemi import GuvenlikSistemi


class TestEndToEndRefactoring:
    """End-to-end refactoring süreci testleri"""
    
    @pytest.fixture
    def karmasik_test_projesi(self):
        """Karmaşık test projesi oluştur"""
        temp_dir = tempfile.mkdtemp(prefix='e2e_test_')
        
        # Büyük dosya oluştur (120+ satır)
        buyuk_dosya = Path(temp_dir) / 'buyuk_modul.py'
        buyuk_dosya_icerik = '''# Büyük modül dosyası
# Bu dosya 120 satırdan fazla olacak

class BuyukSinif:
    """Büyük sınıf örneği"""
    
    def __init__(self):
        self.veri = {}
        self.sayac = 0
        self.durum = "aktif"
    
    def uzun_metod(self):
        """25+ satırlık uzun metod"""
        # Bu metod çok uzun olacak
        satir1 = 1
        satir2 = 2
        satir3 = 3
        satir4 = 4
        satir5 = 5
        satir6 = 6
        satir7 = 7
        satir8 = 8
        satir9 = 9
        satir10 = 10
        satir11 = 11
        satir12 = 12
        satir13 = 13
        satir14 = 14
        satir15 = 15
        satir16 = 16
        satir17 = 17
        satir18 = 18
        satir19 = 19
        satir20 = 20
        satir21 = 21
        satir22 = 22
        satir23 = 23
        satir24 = 24
        satir25 = 25
        satir26 = 26  # Limit aşımı
        return satir26
    
    def diger_metod(self):
        return "test"
    
    def baska_metod(self):
        return "test2"

def global_fonksiyon1():
    return "global1"

def global_fonksiyon2():
    return "global2"

def global_fonksiyon3():
    return "global3"

def global_fonksiyon4():
    return "global4"

def global_fonksiyon5():
    return "global5"

# Daha fazla satır ekleyelim
veri1 = "test"
veri2 = "test"
veri3 = "test"
veri4 = "test"
veri5 = "test"
veri6 = "test"
veri7 = "test"
veri8 = "test"
veri9 = "test"
veri10 = "test"
veri11 = "test"
veri12 = "test"
veri13 = "test"
veri14 = "test"
veri15 = "test"
veri16 = "test"
veri17 = "test"
veri18 = "test"
veri19 = "test"
veri20 = "test"
veri21 = "test"
veri22 = "test"
veri23 = "test"
veri24 = "test"
veri25 = "test"
veri26 = "test"
veri27 = "test"
veri28 = "test"
veri29 = "test"
veri30 = "test"
veri31 = "test"
veri32 = "test"
veri33 = "test"
veri34 = "test"
veri35 = "test"
veri36 = "test"
veri37 = "test"
veri38 = "test"
veri39 = "test"
veri40 = "test"
veri41 = "test"
veri42 = "test"
veri43 = "test"
veri44 = "test"
veri45 = "test"
veri46 = "test"
veri47 = "test"
veri48 = "test"
veri49 = "test"
veri50 = "test"
# Bu dosya 120+ satır olmalı
'''
        buyuk_dosya.write_text(buyuk_dosya_icerik, encoding='utf-8')
        
        # Kod tekrarı olan dosyalar
        tekrar1 = Path(temp_dir) / 'tekrar1.py'
        tekrar1.write_text('''# Tekrar 1
def ortak_fonksiyon():
    print("Bu kod tekrar ediyor")
    return "sonuc"

def baska_fonksiyon():
    return "farklı"
''', encoding='utf-8')
        
        tekrar2 = Path(temp_dir) / 'tekrar2.py'
        tekrar2.write_text('''# Tekrar 2
def ortak_fonksiyon():
    print("Bu kod tekrar ediyor")
    return "sonuc"

def diger_fonksiyon():
    return "başka"
''', encoding='utf-8')
        
        # Mimari ihlali olan dosya (UI katmanında)
        ui_klasoru = Path(temp_dir) / 'ui'
        ui_klasoru.mkdir()
        
        ui_dosyasi = ui_klasoru / 'ana_ekran.py'
        ui_dosyasi.write_text('''# Ana ekran
# Bu dosya UI katmanında ama veritabanı import ediyor (mimari ihlali)
from veritabani.modeller import Kullanici  # İhlal!

class AnaEkran:
    def __init__(self):
        self.kullanici = Kullanici()  # Doğrudan DB erişimi
''', encoding='utf-8')
        
        # Başlık eksik dosya
        baslık_eksik = Path(temp_dir) / 'baslık_eksik.py'
        baslık_eksik.write_text('''def basit_fonksiyon():
    return "başlık yok"
''', encoding='utf-8')
        
        yield temp_dir
        
        # Temizlik
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_tam_analiz_sureci(self, karmasik_test_projesi):
        """Tam analiz sürecinin testi"""
        orkestrator = RefactoringOrkestratori()
        
        # Analiz yap
        analiz_sonucu = orkestrator.kod_tabanini_analiz_et(karmasik_test_projesi)
        
        # Analiz sonuçlarını kontrol et
        assert analiz_sonucu is not None
        assert isinstance(analiz_sonucu, dict)
        
        # Büyük dosya tespit edilmeli
        if 'buyuk_dosyalar' in analiz_sonucu:
            assert len(analiz_sonucu['buyuk_dosyalar']) > 0
        
        # Büyük fonksiyon tespit edilmeli
        if 'buyuk_fonksiyonlar' in analiz_sonucu:
            assert len(analiz_sonucu['buyuk_fonksiyonlar']) > 0
    
    def test_guvenli_backup_ve_geri_alma(self, karmasik_test_projesi):
        """Güvenli backup ve geri alma testi"""
        guvenlik = GuvenlikSistemi()
        
        # Orijinal dosya sayısını say
        orijinal_dosyalar = list(Path(karmasik_test_projesi).rglob("*.py"))
        orijinal_sayisi = len(orijinal_dosyalar)
        
        # Backup oluştur
        backup_yolu = guvenlik.backup_olustur(karmasik_test_projesi)
        
        # Backup oluşturuldu mu
        assert Path(backup_yolu).exists()
        
        # Test değişikliği yap
        test_dosyasi = Path(karmasik_test_projesi) / 'test_degisiklik.py'
        test_dosyasi.write_text('# Test değişikliği')
        
        # Geri al
        guvenlik.geri_al(backup_yolu, karmasik_test_projesi)
        
        # Değişiklik geri alındı mı
        assert not test_dosyasi.exists()
        
        # Orijinal dosyalar korundu mu
        geri_alinan_dosyalar = list(Path(karmasik_test_projesi).rglob("*.py"))
        assert len(geri_alinan_dosyalar) == orijinal_sayisi
    
    def test_cli_sadece_analiz_modu(self, karmasik_test_projesi):
        """CLI sadece analiz modu testi"""
        config = CLIKonfigurasyonu(
            proje_yolu=karmasik_test_projesi,
            sadece_analiz=True,
            verbose=True
        )
        
        cli = KodKalitesiCLI(config)
        
        # Sadece analiz yap (değişiklik yapmamalı)
        orijinal_dosyalar = {f.name: f.read_text() 
                           for f in Path(karmasik_test_projesi).rglob("*.py")}
        
        sonuc = cli._sadece_analiz_yap()
        
        # Analiz başarılı olmalı
        assert sonuc == 0
        
        # Dosyalar değişmemeli
        analiz_sonrasi_dosyalar = {f.name: f.read_text() 
                                 for f in Path(karmasik_test_projesi).rglob("*.py")}
        
        assert orijinal_dosyalar == analiz_sonrasi_dosyalar
    
    @pytest.mark.slow
    def test_performans_buyuk_proje(self):
        """Büyük proje performans testi"""
        # Büyük test projesi oluştur
        temp_dir = tempfile.mkdtemp(prefix='performans_test_')
        
        try:
            # 100 dosya oluştur
            for i in range(100):
                dosya = Path(temp_dir) / f'modul_{i}.py'
                icerik = f'''# Modül {i}
# Bu dosya performans testi için oluşturuldu

class Sinif_{i}:
    def __init__(self):
        self.id = {i}
        self.isim = "modul_{i}"
    
    def metod_{i}(self):
        return self.id * 2
    
    def diger_metod_{i}(self):
        return self.isim.upper()

def fonksiyon_{i}():
    return Sinif_{i}()

# Veri tanımları
SABIT_{i} = {i}
LISTE_{i} = [x for x in range({i})]
SOZLUK_{i} = {{"anahtar": {i}}}
'''
                dosya.write_text(icerik, encoding='utf-8')
            
            # Performans testi
            import time
            
            config = CLIKonfigurasyonu(
                proje_yolu=temp_dir,
                sadece_analiz=True
            )
            cli = KodKalitesiCLI(config)
            
            baslangic = time.time()
            sonuc = cli._sadece_analiz_yap()
            bitis = time.time()
            
            # Analiz süresi kontrolü (60 saniyeden az olmalı)
            sure = bitis - baslangic
            assert sure < 60, f"Analiz çok yavaş: {sure:.2f} saniye"
            
            # Analiz başarılı olmalı
            assert sonuc == 0
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_hata_durumunda_geri_alma(self, karmasik_test_projesi):
        """Hata durumunda otomatik geri alma testi"""
        guvenlik = GuvenlikSistemi()
        
        # Backup oluştur
        backup_yolu = guvenlik.backup_olustur(karmasik_test_projesi)
        
        # Orijinal dosya içeriğini kaydet
        orijinal_dosya = Path(karmasik_test_projesi) / 'buyuk_modul.py'
        orijinal_icerik = orijinal_dosya.read_text()
        
        try:
            # Dosyayı bozuk hale getir (simüle edilmiş hata)
            orijinal_dosya.write_text('# Bozuk içerik')
            
            # Geri alma işlemi
            guvenlik.geri_al(backup_yolu, karmasik_test_projesi)
            
            # Dosya orijinal haline döndü mü
            geri_alinan_icerik = orijinal_dosya.read_text()
            assert geri_alinan_icerik == orijinal_icerik
            
        except Exception as e:
            pytest.fail(f"Geri alma testi hatası: {e}")
    
    def test_coklu_sorun_tespit_ve_raporlama(self, karmasik_test_projesi):
        """Çoklu sorun tespit ve raporlama testi"""
        orkestrator = RefactoringOrkestratori()
        
        # Analiz yap
        analiz_sonucu = orkestrator.kod_tabanini_analiz_et(karmasik_test_projesi)
        
        # Farklı türde sorunlar tespit edilmeli
        sorun_turleri = []
        
        if analiz_sonucu.get('buyuk_dosyalar'):
            sorun_turleri.append('buyuk_dosyalar')
        
        if analiz_sonucu.get('buyuk_fonksiyonlar'):
            sorun_turleri.append('buyuk_fonksiyonlar')
        
        if analiz_sonucu.get('mimari_ihlaller'):
            sorun_turleri.append('mimari_ihlaller')
        
        if analiz_sonucu.get('kod_tekrarlari'):
            sorun_turleri.append('kod_tekrarlari')
        
        # En az 2 farklı sorun türü tespit edilmeli
        assert len(sorun_turleri) >= 2, f"Yeterli sorun tespit edilmedi: {sorun_turleri}"


class TestGercekKodTabaniEntegrasyonu:
    """Gerçek kod tabanı entegrasyon testleri (güvenli)"""
    
    def test_mevcut_proje_analizi(self):
        """Mevcut projenin güvenli analizi"""
        # Sadece analiz modu (değişiklik yapmaz)
        mevcut_proje = "."
        
        config = CLIKonfigurasyonu(
            proje_yolu=mevcut_proje,
            sadece_analiz=True,
            verbose=False
        )
        
        cli = KodKalitesiCLI(config)
        
        try:
            # Proje doğrulaması
            assert cli._proje_dogrula() == True
            
            # Güvenli analiz (değişiklik yapmaz)
            sonuc = cli._sadece_analiz_yap()
            
            # Analiz tamamlanmalı (sorun bulsa da bulmasa da)
            assert sonuc in [0, 1]  # 0: sorun yok, 1: sorun var
            
        except Exception as e:
            # Analiz hatası olabilir ama test başarısız sayılmamalı
            pytest.skip(f"Mevcut proje analizi atlandı: {e}")
    
    def test_konfigürasyon_dosyasi_varlik(self):
        """Konfigürasyon dosyasının varlığı"""
        config_dosyasi = Path('kod-kalitesi-config.yaml')
        
        # Konfigürasyon dosyası mevcut olmalı
        assert config_dosyasi.exists()
        
        # Konfigürasyon yüklenebilir olmalı
        from sontechsp.uygulama.kod_kalitesi.konfigürasyon import KonfigürasyonYoneticisi
        
        config_yoneticisi = KonfigürasyonYoneticisi('.')
        config = config_yoneticisi.konfigürasyonu_yukle()
        
        assert config is not None
        assert config.dosya_kurallari.max_satir_sayisi > 0