# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.test_kurulum_entegrasyonu
# Description: Kurulum sistemi entegrasyon testleri
# Changelog:
# - İlk sürüm: Kurulum entegrasyon testleri

import os
import tempfile
import shutil
import json
from pathlib import Path
import pytest

from sontechsp.uygulama.kod_kalitesi.kurulum_yoneticisi import KurulumYoneticisi
from sontechsp.uygulama.kod_kalitesi.konfigürasyon import KonfigürasyonYoneticisi


class TestKurulumEntegrasyonu:
    """Kurulum sistemi entegrasyon testleri"""
    
    @pytest.fixture
    def test_projesi(self):
        """Test için geçici proje oluştur"""
        temp_dir = tempfile.mkdtemp(prefix='kurulum_test_')
        
        # Temel proje yapısı oluştur
        (Path(temp_dir) / 'sontechsp').mkdir()
        (Path(temp_dir) / 'sontechsp' / '__init__.py').write_text('# Ana modül')
        (Path(temp_dir) / 'tests').mkdir()
        (Path(temp_dir) / 'tests' / '__init__.py').write_text('# Test modülü')
        
        # Basit Python dosyası
        (Path(temp_dir) / 'ana.py').write_text('''# Ana dosya
def main():
    print("Merhaba dünya")

if __name__ == "__main__":
    main()
''')
        
        yield temp_dir
        
        # Temizlik
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_kurulum_yoneticisi_olusturma(self, test_projesi):
        """Kurulum yöneticisi oluşturma"""
        kurulum = KurulumYoneticisi(test_projesi)
        
        assert kurulum.proje_yolu == Path(test_projesi)
        assert kurulum.config_yoneticisi is not None
    
    def test_proje_yapisi_dogrulama(self, test_projesi):
        """Proje yapısı doğrulama"""
        kurulum = KurulumYoneticisi(test_projesi)
        
        # Geçerli proje yapısı
        assert kurulum._proje_yapisini_dogrula() == True
        
        # Geçersiz proje yapısı (Python dosyası yok)
        bos_dir = tempfile.mkdtemp()
        try:
            kurulum_bos = KurulumYoneticisi(bos_dir)
            assert kurulum_bos._proje_yapisini_dogrula() == False
        finally:
            shutil.rmtree(bos_dir, ignore_errors=True)
    
    def test_gerekli_klasorleri_olusturma(self, test_projesi):
        """Gerekli klasörlerin oluşturulması"""
        kurulum = KurulumYoneticisi(test_projesi)
        
        # Klasörleri oluştur
        kurulum._gerekli_klasorleri_olustur()
        
        # Oluşturulan klasörleri kontrol et
        beklenen_klasorler = [
            '.kod-kalitesi-backup',
            'kod-kalitesi-raporlar',
            'ortak',
            'scripts'
        ]
        
        for klasor in beklenen_klasorler:
            klasor_yolu = Path(test_projesi) / klasor
            assert klasor_yolu.exists(), f"Klasör oluşturulmadı: {klasor}"
            assert klasor_yolu.is_dir(), f"Klasör değil: {klasor}"
    
    def test_konfigürasyon_dosyasi_olusturma(self, test_projesi):
        """Konfigürasyon dosyası oluşturma"""
        kurulum = KurulumYoneticisi(test_projesi)
        
        # Konfigürasyon oluştur
        kurulum._konfigürasyon_dosyasi_olustur()
        
        # Konfigürasyon dosyasının varlığını kontrol et
        config_yolu = Path(test_projesi) / 'kod-kalitesi-config.yaml'
        assert config_yolu.exists()
        
        # Konfigürasyon yüklenebilir mi kontrol et
        config_yoneticisi = KonfigürasyonYoneticisi(test_projesi)
        config = config_yoneticisi.konfigürasyonu_yukle()
        assert config is not None
        assert config.dosya_kurallari.max_satir_sayisi > 0
    
    def test_git_hooks_kurulumu(self, test_projesi):
        """Git hooks kurulumu"""
        kurulum = KurulumYoneticisi(test_projesi)
        
        # Git repository simülasyonu
        git_klasoru = Path(test_projesi) / '.git'
        git_klasoru.mkdir()
        
        # Git hooks kurulumu
        kurulum._git_hooks_kurulumu()
        
        # Pre-commit hook kontrolü
        pre_commit_hook = git_klasoru / 'hooks' / 'pre-commit'
        assert pre_commit_hook.exists()
        
        # Hook içeriği kontrolü
        hook_icerik = pre_commit_hook.read_text(encoding='utf-8')
        assert 'kod-kalitesi-cli.py' in hook_icerik
        assert '--analiz' in hook_icerik
    
    def test_vscode_entegrasyonu(self, test_projesi):
        """VS Code entegrasyonu"""
        kurulum = KurulumYoneticisi(test_projesi)
        
        # VS Code entegrasyonu oluştur
        kurulum._vscode_entegrasyonu_olustur()
        
        # Tasks.json kontrolü
        tasks_dosyasi = Path(test_projesi) / '.vscode' / 'tasks.json'
        assert tasks_dosyasi.exists()
        
        tasks_icerik = json.loads(tasks_dosyasi.read_text(encoding='utf-8'))
        assert 'tasks' in tasks_icerik
        assert len(tasks_icerik['tasks']) >= 2  # Analiz ve refactoring taskları
        
        # Launch.json kontrolü
        launch_dosyasi = Path(test_projesi) / '.vscode' / 'launch.json'
        assert launch_dosyasi.exists()
        
        launch_icerik = json.loads(launch_dosyasi.read_text(encoding='utf-8'))
        assert 'configurations' in launch_icerik
    
    def test_test_kurulumu_dogrulama(self, test_projesi):
        """Test kurulumu doğrulama"""
        kurulum = KurulumYoneticisi(test_projesi)
        
        # Test kurulumu
        kurulum._test_kurulumunu_dogrula()
        
        # Pytest.ini kontrolü
        pytest_ini = Path(test_projesi) / 'pytest.ini'
        assert pytest_ini.exists()
        
        pytest_icerik = pytest_ini.read_text(encoding='utf-8')
        assert 'testpaths = tests' in pytest_icerik
        assert 'python_files = test_*.py' in pytest_icerik
    
    def test_kurulum_durumu_kontrolu(self, test_projesi):
        """Kurulum durumu kontrolü"""
        kurulum = KurulumYoneticisi(test_projesi)
        
        # İlk durum (hiçbir şey kurulu değil)
        durum = kurulum.kurulum_durumunu_kontrol_et()
        assert isinstance(durum, dict)
        assert 'konfigürasyon_dosyasi' in durum
        assert 'backup_klasoru' in durum
        
        # Kısmi kurulum yap
        kurulum._gerekli_klasorleri_olustur()
        kurulum._konfigürasyon_dosyasi_olustur()
        
        # Güncellenmiş durum
        yeni_durum = kurulum.kurulum_durumunu_kontrol_et()
        assert yeni_durum['konfigürasyon_dosyasi'] == True
        assert yeni_durum['backup_klasoru'] == True
    
    def test_tam_kurulum_sureci(self, test_projesi):
        """Tam kurulum sürecinin testi"""
        kurulum = KurulumYoneticisi(test_projesi)
        
        # Git repository oluştur (hooks için)
        (Path(test_projesi) / '.git').mkdir()
        
        # Tam kurulum yap (interaktif olmayan mod)
        # Not: Bu test gerçek kullanıcı etkileşimi gerektirmez
        try:
            # Kurulum bileşenlerini tek tek test et
            assert kurulum._proje_yapisini_dogrula() == True
            kurulum._gerekli_klasorleri_olustur()
            kurulum._konfigürasyon_dosyasi_olustur()
            kurulum._git_hooks_kurulumu()
            kurulum._test_kurulumunu_dogrula()
            
            # Final durum kontrolü
            durum = kurulum.kurulum_durumunu_kontrol_et()
            kurulu_sayisi = sum(durum.values())
            
            # En az yarısı kurulu olmalı
            assert kurulu_sayisi >= len(durum) // 2
            
        except Exception as e:
            pytest.fail(f"Tam kurulum hatası: {e}")


class TestKonfigürasyonEntegrasyonu:
    """Konfigürasyon sistemi entegrasyon testleri"""
    
    @pytest.fixture
    def test_projesi(self):
        """Test için geçici proje oluştur"""
        temp_dir = tempfile.mkdtemp(prefix='config_test_')
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_konfigürasyon_yoneticisi_olusturma(self, test_projesi):
        """Konfigürasyon yöneticisi oluşturma"""
        config_yoneticisi = KonfigürasyonYoneticisi(test_projesi)
        
        assert config_yoneticisi.proje_yolu == Path(test_projesi)
        assert config_yoneticisi.config_dosya_yolu.name == 'kod-kalitesi-config.yaml'
    
    def test_varsayilan_konfigürasyon_olusturma(self, test_projesi):
        """Varsayılan konfigürasyon oluşturma"""
        config_yoneticisi = KonfigürasyonYoneticisi(test_projesi)
        
        # Varsayılan konfigürasyon oluştur
        config_yolu = config_yoneticisi.varsayilan_konfigürasyon_olustur()
        
        assert Path(config_yolu).exists()
        assert Path(config_yolu).name == 'kod-kalitesi-config.yaml'
        
        # Konfigürasyon yüklenebilir mi
        config = config_yoneticisi.konfigürasyonu_yukle()
        assert config is not None
    
    def test_konfigürasyon_dogrulama(self, test_projesi):
        """Konfigürasyon doğrulama"""
        config_yoneticisi = KonfigürasyonYoneticisi(test_projesi)
        
        # Varsayılan konfigürasyon oluştur
        config_yoneticisi.varsayilan_konfigürasyon_olustur()
        
        # Doğrulama yap
        hatalar = config_yoneticisi.konfigürasyon_dogrula()
        
        # Varsayılan konfigürasyonda hata olmamalı
        assert len(hatalar) == 0
    
    def test_gecersiz_konfigürasyon_dogrulama(self, test_projesi):
        """Geçersiz konfigürasyon doğrulama"""
        from sontechsp.uygulama.kod_kalitesi.konfigürasyon import KodKalitesiKonfigurasyonu, DosyaKurallari
        
        config_yoneticisi = KonfigürasyonYoneticisi(test_projesi)
        
        # Geçersiz konfigürasyon oluştur
        gecersiz_config = KodKalitesiKonfigurasyonu.varsayilan()
        gecersiz_config.dosya_kurallari.max_satir_sayisi = -1  # Geçersiz değer
        
        # Konfigürasyonu kaydet
        config_yoneticisi.konfigürasyonu_guncelle(gecersiz_config)
        
        # Doğrulama yap
        hatalar = config_yoneticisi.konfigürasyon_dogrula()
        
        # Hata bulunmalı
        assert len(hatalar) > 0
        assert any('pozitif' in hata for hata in hatalar)


class TestScriptEntegrasyonu:
    """Script entegrasyonu testleri"""
    
    def test_kurulum_scripti_varlik(self):
        """Kurulum scriptinin varlığı"""
        script_yolu = Path('scripts/kod-kalitesi-kurulum.py')
        assert script_yolu.exists()
        
        # Script çalıştırılabilir mi
        import subprocess
        result = subprocess.run([
            'python', str(script_yolu), '--help'
        ], capture_output=True, text=True, timeout=10)
        
        # Help komutu çalışmalı
        assert result.returncode == 0 or 'help' in result.stdout.lower()
    
    def test_cli_scripti_varlik(self):
        """CLI scriptinin varlığı"""
        script_yolu = Path('scripts/kod-kalitesi-cli.py')
        assert script_yolu.exists()
        
        # Script çalıştırılabilir mi
        import subprocess
        result = subprocess.run([
            'python', str(script_yolu), '--help'
        ], capture_output=True, text=True, timeout=10)
        
        # Help komutu çalışmalı
        assert result.returncode == 0
        assert 'SONTECHSP' in result.stdout