# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.test_cli_entegrasyonu
# Description: CLI arayüzü entegrasyon testleri
# Changelog:
# - İlk sürüm: CLI entegrasyon testleri

import os
import tempfile
import shutil
import subprocess
from pathlib import Path
import pytest

from sontechsp.uygulama.kod_kalitesi.cli_arayuzu import KodKalitesiCLI, CLIKonfigurasyonu


class TestCLIEntegrasyonu:
    """CLI arayüzü entegrasyon testleri"""
    
    @pytest.fixture
    def test_projesi(self):
        """Test için geçici proje oluştur"""
        temp_dir = tempfile.mkdtemp(prefix='kod_kalitesi_test_')
        
        # Basit Python dosyaları oluştur
        test_dosyasi = Path(temp_dir) / 'test_modulu.py'
        test_dosyasi.write_text('''# Test modülü
def basit_fonksiyon():
    return "merhaba"

def uzun_fonksiyon():
    # Bu fonksiyon 25 satırdan uzun olacak
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
''', encoding='utf-8')
        
        yield temp_dir
        
        # Temizlik
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_cli_help_komutu(self):
        """CLI help komutunun çalışması"""
        result = subprocess.run([
            'python', 'scripts/kod-kalitesi-cli.py', '--help'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert 'SONTECHSP Kod Kalitesi' in result.stdout
        assert 'proje_yolu' in result.stdout
    
    def test_cli_analiz_modu(self, test_projesi):
        """CLI analiz modunun çalışması"""
        config = CLIKonfigurasyonu(
            proje_yolu=test_projesi,
            sadece_analiz=True,
            otomatik_onay=True
        )
        
        cli = KodKalitesiCLI(config)
        
        # Analiz modunu test et (hata vermemeli)
        try:
            sonuc = cli._sadece_analiz_yap()
            assert sonuc == 0  # Başarılı çıkış kodu
        except Exception as e:
            pytest.fail(f"Analiz modu hatası: {e}")
    
    def test_cli_proje_dogrulama(self, test_projesi):
        """CLI proje doğrulama işlemi"""
        config = CLIKonfigurasyonu(proje_yolu=test_projesi)
        cli = KodKalitesiCLI(config)
        
        # Geçerli proje doğrulaması
        assert cli._proje_dogrula() == True
        
        # Geçersiz proje doğrulaması
        config_gecersiz = CLIKonfigurasyonu(proje_yolu='/gecersiz/yol')
        cli_gecersiz = KodKalitesiCLI(config_gecersiz)
        assert cli_gecersiz._proje_dogrula() == False
    
    def test_cli_konfigürasyon_entegrasyonu(self, test_projesi):
        """CLI konfigürasyon entegrasyonu"""
        config = CLIKonfigurasyonu(proje_yolu=test_projesi)
        cli = KodKalitesiCLI(config)
        
        # Konfigürasyon yöneticisinin çalışması
        assert cli.config_yoneticisi is not None
        
        # Konfigürasyon yükleme
        kod_config = cli.config_yoneticisi.konfigürasyonu_yukle()
        assert kod_config is not None
        assert kod_config.dosya_kurallari.max_satir_sayisi > 0
    
    def test_cli_ilerleme_metre(self):
        """İlerleme metre sınıfının çalışması"""
        from sontechsp.uygulama.kod_kalitesi.cli_arayuzu import IlerlemeMetre
        
        metre = IlerlemeMetre(toplam_adim=5)
        
        # İlerleme güncellemesi (hata vermemeli)
        try:
            metre.guncelle(1, "Test adımı 1")
            metre.guncelle(3, "Test adımı 3")
            metre.guncelle(5, "Tamamlandı")
        except Exception as e:
            pytest.fail(f"İlerleme metre hatası: {e}")
    
    def test_cli_hata_yonetimi(self):
        """CLI hata yönetimi"""
        # Geçersiz proje yolu ile CLI oluştur
        config = CLIKonfigurasyonu(proje_yolu='/gecersiz/yol')
        cli = KodKalitesiCLI(config)
        
        # Hata durumunda uygun çıkış kodu dönmeli
        sonuc = cli.calistir()
        assert sonuc != 0  # Hata çıkış kodu
    
    def test_cli_script_entegrasyonu(self, test_projesi):
        """CLI script entegrasyonu"""
        # Script dosyasının varlığını kontrol et
        script_yolu = Path('scripts/kod-kalitesi-cli.py')
        assert script_yolu.exists()
        
        # Script çalıştırma (sadece analiz modu)
        result = subprocess.run([
            'python', str(script_yolu), test_projesi, '--analiz'
        ], capture_output=True, text=True, timeout=30)
        
        # Script hata vermemeli (analiz modu güvenli)
        assert result.returncode in [0, 1]  # 0: başarılı, 1: sorun bulundu
    
    @pytest.mark.slow
    def test_cli_buyuk_proje_performansi(self):
        """CLI büyük proje performans testi"""
        # Geçici büyük proje oluştur
        temp_dir = tempfile.mkdtemp(prefix='buyuk_proje_test_')
        
        try:
            # 50 dosya oluştur
            for i in range(50):
                dosya = Path(temp_dir) / f'modul_{i}.py'
                dosya.write_text(f'''# Modül {i}
def fonksiyon_{i}():
    return {i}

class Sinif_{i}:
    def metod_{i}(self):
        return {i}
''', encoding='utf-8')
            
            # CLI analiz performansını test et
            config = CLIKonfigurasyonu(
                proje_yolu=temp_dir,
                sadece_analiz=True
            )
            cli = KodKalitesiCLI(config)
            
            import time
            baslangic = time.time()
            sonuc = cli._sadece_analiz_yap()
            bitis = time.time()
            
            # 30 saniyeden az sürmeli
            sure = bitis - baslangic
            assert sure < 30, f"Analiz çok yavaş: {sure:.2f} saniye"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestCLIKomutSatiri:
    """CLI komut satırı testleri"""
    
    def test_argparse_konfigürasyonu(self):
        """Argparse konfigürasyonunun doğruluğu"""
        # Help çıktısını kontrol et
        result = subprocess.run([
            'python', 'scripts/kod-kalitesi-cli.py', '--help'
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        
        # Gerekli parametrelerin varlığını kontrol et
        help_text = result.stdout
        assert 'proje_yolu' in help_text
        assert '--analiz' in help_text
        assert '--otomatik' in help_text
        assert '--verbose' in help_text
        assert '--max-dosya' in help_text
        assert '--max-fonksiyon' in help_text
    
    def test_gecersiz_parametreler(self):
        """Geçersiz parametrelerle çalıştırma"""
        # Eksik proje yolu
        result = subprocess.run([
            'python', 'scripts/kod-kalitesi-cli.py'
        ], capture_output=True, text=True)
        
        assert result.returncode != 0  # Hata bekleniyor
        assert 'required' in result.stderr.lower() or 'error' in result.stderr.lower()
    
    def test_gecerli_parametreler(self):
        """Geçerli parametrelerle çalıştırma"""
        # Geçici test dizini
        temp_dir = tempfile.mkdtemp()
        test_dosya = Path(temp_dir) / 'test.py'
        test_dosya.write_text('# Test dosyası\nprint("merhaba")\n')
        
        try:
            result = subprocess.run([
                'python', 'scripts/kod-kalitesi-cli.py', 
                temp_dir, '--analiz', '--verbose'
            ], capture_output=True, text=True, timeout=15)
            
            # Hata vermemeli veya kontrollü hata vermeli
            assert result.returncode in [0, 1]
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)