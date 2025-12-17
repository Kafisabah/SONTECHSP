# Version: 0.1.0
# Last Update: 2024-12-17
# Module: kod_kalitesi.kurulum_yoneticisi
# Description: Kod kalitesi sistemi otomatik kurulum ve entegrasyon yöneticisi
# Changelog:
# - İlk sürüm: Otomatik kurulum ve proje entegrasyonu

import os
import shutil
import subprocess
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json

from .konfigürasyon import KonfigürasyonYoneticisi, KodKalitesiKonfigurasyonu


class KurulumYoneticisi:
    """Kod kalitesi sistemi kurulum ve entegrasyon yöneticisi"""
    
    def __init__(self, proje_yolu: str):
        self.proje_yolu = Path(proje_yolu)
        self.config_yoneticisi = KonfigürasyonYoneticisi(str(self.proje_yolu))
        
    def tam_kurulum_yap(self) -> bool:
        """Tam kurulum işlemini gerçekleştir"""
        print("🚀 Kod Kalitesi Sistemi Kurulumu Başlatılıyor...")
        print("=" * 60)
        
        try:
            # 1. Proje yapısını doğrula
            if not self._proje_yapisini_dogrula():
                return False
            
            # 2. Gerekli klasörleri oluştur
            self._gerekli_klasorleri_olustur()
            
            # 3. Konfigürasyon dosyası oluştur
            self._konfigürasyon_dosyasi_olustur()
            
            # 4. Git hooks kurulumu (opsiyonel)
            self._git_hooks_kurulumu()
            
            # 5. IDE entegrasyonu (opsiyonel)
            self._ide_entegrasyonu()
            
            # 6. Test kurulumu doğrula
            self._test_kurulumunu_dogrula()
            
            print("\n✅ Kod Kalitesi Sistemi başarıyla kuruldu!")
            print("📋 Kullanım için: python scripts/kod-kalitesi-cli.py --help")
            return True
            
        except Exception as e:
            print(f"\n❌ Kurulum hatası: {e}")
            return False
    
    def _proje_yapisini_dogrula(self) -> bool:
        """Proje yapısının uygunluğunu doğrula"""
        print("1️⃣ Proje yapısı doğrulanıyor...")
        
        # Python dosyalarının varlığını kontrol et
        python_dosyalari = list(self.proje_yolu.rglob("*.py"))
        if not python_dosyalari:
            print("❌ Proje klasöründe Python dosyası bulunamadı")
            return False
        
        # Temel klasörlerin varlığını kontrol et
        gerekli_klasorler = ['sontechsp', 'tests']
        eksik_klasorler = []
        
        for klasor in gerekli_klasorler:
            if not (self.proje_yolu / klasor).exists():
                eksik_klasorler.append(klasor)
        
        if eksik_klasorler:
            print(f"⚠️ Eksik klasörler: {', '.join(eksik_klasorler)}")
            print("📝 Bu klasörler otomatik oluşturulacak...")
        
        print(f"✅ {len(python_dosyalari)} Python dosyası bulundu")
        return True
    
    def _gerekli_klasorleri_olustur(self):
        """Gerekli klasör yapısını oluştur"""
        print("2️⃣ Gerekli klasörler oluşturuluyor...")
        
        gerekli_klasorler = [
            '.kod-kalitesi-backup',
            'kod-kalitesi-raporlar',
            'ortak',  # Ortak modüller için
            'scripts'  # CLI scriptleri için
        ]
        
        for klasor in gerekli_klasorler:
            klasor_yolu = self.proje_yolu / klasor
            if not klasor_yolu.exists():
                klasor_yolu.mkdir(parents=True, exist_ok=True)
                print(f"📁 Oluşturuldu: {klasor}")
            else:
                print(f"✅ Mevcut: {klasor}")
    
    def _konfigürasyon_dosyasi_olustur(self):
        """Konfigürasyon dosyası oluştur"""
        print("3️⃣ Konfigürasyon dosyası hazırlanıyor...")
        
        if not self.config_yoneticisi.konfigürasyon_dosyasi_var_mi():
            config_yolu = self.config_yoneticisi.varsayilan_konfigürasyon_olustur()
            print(f"📝 Konfigürasyon oluşturuldu: {config_yolu}")
        else:
            print("✅ Konfigürasyon dosyası mevcut")
        
        # Konfigürasyon doğrulaması
        hatalar = self.config_yoneticisi.konfigürasyon_dogrula()
        if hatalar:
            print("⚠️ Konfigürasyon uyarıları:")
            for hata in hatalar:
                print(f"  • {hata}")
        else:
            print("✅ Konfigürasyon doğrulandı")
    
    def _git_hooks_kurulumu(self):
        """Git hooks kurulumu (opsiyonel)"""
        print("4️⃣ Git hooks entegrasyonu kontrol ediliyor...")
        
        git_klasoru = self.proje_yolu / '.git'
        if not git_klasoru.exists():
            print("⚠️ Git repository bulunamadı, hooks atlanıyor")
            return
        
        hooks_klasoru = git_klasoru / 'hooks'
        hooks_klasoru.mkdir(exist_ok=True)
        
        # Pre-commit hook oluştur
        pre_commit_hook = hooks_klasoru / 'pre-commit'
        if not pre_commit_hook.exists():
            hook_icerik = self._pre_commit_hook_icerigini_olustur()
            with open(pre_commit_hook, 'w', encoding='utf-8') as f:
                f.write(hook_icerik)
            
            # Executable yap (Unix sistemlerde)
            try:
                os.chmod(pre_commit_hook, 0o755)
            except:
                pass  # Windows'ta chmod çalışmayabilir
            
            print("✅ Pre-commit hook oluşturuldu")
        else:
            print("✅ Pre-commit hook mevcut")
    
    def _pre_commit_hook_icerigini_olustur(self) -> str:
        """Pre-commit hook içeriği oluştur"""
        return '''#!/bin/sh
# Kod Kalitesi Pre-commit Hook
# Bu hook commit öncesi kod kalitesi kontrolü yapar

echo "🔍 Kod kalitesi kontrolü yapılıyor..."

# Kod kalitesi CLI'yi çalıştır (sadece analiz modu)
python scripts/kod-kalitesi-cli.py . --analiz

if [ $? -ne 0 ]; then
    echo "❌ Kod kalitesi kontrolü başarısız!"
    echo "💡 Lütfen 'python scripts/kod-kalitesi-cli.py .' komutu ile sorunları düzeltin"
    exit 1
fi

echo "✅ Kod kalitesi kontrolü başarılı"
exit 0
'''
    
    def _ide_entegrasyonu(self):
        """IDE entegrasyonu ayarları"""
        print("5️⃣ IDE entegrasyonu kontrol ediliyor...")
        
        # VS Code ayarları
        vscode_klasoru = self.proje_yolu / '.vscode'
        if vscode_klasoru.exists() or self._kullanici_onayini_al("VS Code entegrasyonu eklensin mi?"):
            self._vscode_entegrasyonu_olustur()
        
        # PyCharm ayarları (opsiyonel)
        pycharm_klasoru = self.proje_yolu / '.idea'
        if pycharm_klasoru.exists():
            print("💡 PyCharm projesi tespit edildi")
            print("📝 External Tools menüsünden kod kalitesi aracını ekleyebilirsiniz")
    
    def _vscode_entegrasyonu_olustur(self):
        """VS Code entegrasyonu oluştur"""
        vscode_klasoru = self.proje_yolu / '.vscode'
        vscode_klasoru.mkdir(exist_ok=True)
        
        # Tasks.json oluştur
        tasks_dosyasi = vscode_klasoru / 'tasks.json'
        if not tasks_dosyasi.exists():
            tasks_icerik = {
                "version": "2.0.0",
                "tasks": [
                    {
                        "label": "Kod Kalitesi Analizi",
                        "type": "shell",
                        "command": "python",
                        "args": ["scripts/kod-kalitesi-cli.py", ".", "--analiz"],
                        "group": "build",
                        "presentation": {
                            "echo": True,
                            "reveal": "always",
                            "focus": False,
                            "panel": "shared"
                        },
                        "problemMatcher": []
                    },
                    {
                        "label": "Kod Kalitesi Refactoring",
                        "type": "shell", 
                        "command": "python",
                        "args": ["scripts/kod-kalitesi-cli.py", "."],
                        "group": "build",
                        "presentation": {
                            "echo": True,
                            "reveal": "always",
                            "focus": True,
                            "panel": "shared"
                        },
                        "problemMatcher": []
                    }
                ]
            }
            
            with open(tasks_dosyasi, 'w', encoding='utf-8') as f:
                json.dump(tasks_icerik, f, indent=2, ensure_ascii=False)
            
            print("✅ VS Code tasks.json oluşturuldu")
        
        # Launch.json oluştur (debug konfigürasyonu)
        launch_dosyasi = vscode_klasoru / 'launch.json'
        if not launch_dosyasi.exists():
            launch_icerik = {
                "version": "0.2.0",
                "configurations": [
                    {
                        "name": "Kod Kalitesi CLI Debug",
                        "type": "python",
                        "request": "launch",
                        "program": "${workspaceFolder}/scripts/kod-kalitesi-cli.py",
                        "args": [".", "--analiz", "--verbose"],
                        "console": "integratedTerminal",
                        "cwd": "${workspaceFolder}"
                    }
                ]
            }
            
            with open(launch_dosyasi, 'w', encoding='utf-8') as f:
                json.dump(launch_icerik, f, indent=2, ensure_ascii=False)
            
            print("✅ VS Code launch.json oluşturuldu")
    
    def _test_kurulumunu_dogrula(self):
        """Test kurulumunu doğrula"""
        print("6️⃣ Test kurulumu doğrulanıyor...")
        
        # Test klasörünün varlığını kontrol et
        test_klasoru = self.proje_yolu / 'tests'
        if not test_klasoru.exists():
            test_klasoru.mkdir(exist_ok=True)
            print("📁 Tests klasörü oluşturuldu")
        
        # Pytest konfigürasyonu kontrol et
        pytest_ini = self.proje_yolu / 'pytest.ini'
        if not pytest_ini.exists():
            pytest_icerik = '''[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    property: marks tests as property-based tests
'''
            with open(pytest_ini, 'w', encoding='utf-8') as f:
                f.write(pytest_icerik)
            print("✅ pytest.ini oluşturuldu")
        
        # Basit test çalıştırma
        try:
            result = subprocess.run(['python', '-m', 'pytest', '--version'], 
                                  capture_output=True, text=True, cwd=self.proje_yolu)
            if result.returncode == 0:
                print("✅ Pytest kurulu ve çalışıyor")
            else:
                print("⚠️ Pytest kurulu değil veya çalışmıyor")
        except:
            print("⚠️ Pytest durumu kontrol edilemedi")
    
    def _kullanici_onayini_al(self, mesaj: str) -> bool:
        """Kullanıcıdan onay al"""
        while True:
            cevap = input(f"🤔 {mesaj} (e/h): ").lower().strip()
            if cevap in ['e', 'evet', 'y', 'yes']:
                return True
            elif cevap in ['h', 'hayır', 'n', 'no']:
                return False
            else:
                print("❌ Lütfen 'e' (evet) veya 'h' (hayır) giriniz.")
    
    def kurulum_durumunu_kontrol_et(self) -> Dict[str, bool]:
        """Kurulum durumunu kontrol et"""
        durum = {
            'konfigürasyon_dosyasi': self.config_yoneticisi.konfigürasyon_dosyasi_var_mi(),
            'backup_klasoru': (self.proje_yolu / '.kod-kalitesi-backup').exists(),
            'scripts_klasoru': (self.proje_yolu / 'scripts').exists(),
            'cli_scripti': (self.proje_yolu / 'scripts' / 'kod-kalitesi-cli.py').exists(),
            'git_hooks': (self.proje_yolu / '.git' / 'hooks' / 'pre-commit').exists(),
            'vscode_entegrasyonu': (self.proje_yolu / '.vscode' / 'tasks.json').exists()
        }
        
        return durum
    
    def kurulum_raporunu_goster(self):
        """Kurulum durumu raporunu göster"""
        durum = self.kurulum_durumunu_kontrol_et()
        
        print("\n📊 Kod Kalitesi Sistemi Kurulum Durumu")
        print("=" * 50)
        
        for bileşen, kurulu in durum.items():
            durum_ikonu = "✅" if kurulu else "❌"
            bileşen_adi = bileşen.replace('_', ' ').title()
            print(f"{durum_ikonu} {bileşen_adi}")
        
        kurulu_sayisi = sum(durum.values())
        toplam_sayisi = len(durum)
        yuzde = (kurulu_sayisi / toplam_sayisi) * 100
        
        print(f"\n📈 Kurulum Tamamlanma: {kurulu_sayisi}/{toplam_sayisi} (%{yuzde:.1f})")
        
        if kurulu_sayisi == toplam_sayisi:
            print("🎉 Sistem tamamen kurulu ve hazır!")
        else:
            print("💡 Eksik bileşenler için tam kurulum çalıştırın")


def ana_kurulum():
    """Ana kurulum fonksiyonu"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Kod Kalitesi Sistemi Kurulum Aracı")
    parser.add_argument('proje_yolu', nargs='?', default='.', 
                       help='Kurulum yapılacak proje klasörü')
    parser.add_argument('--durum', action='store_true',
                       help='Sadece kurulum durumunu göster')
    
    args = parser.parse_args()
    
    kurulum = KurulumYoneticisi(args.proje_yolu)
    
    if args.durum:
        kurulum.kurulum_raporunu_goster()
    else:
        kurulum.tam_kurulum_yap()


if __name__ == "__main__":
    ana_kurulum()