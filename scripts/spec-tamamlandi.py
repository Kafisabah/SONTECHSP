#!/usr/bin/env python3
# Version: 0.1.0
# Last Update: 2024-12-15
# Module: spec_completion_automation
# Description: Spec tamamlama otomatik commit ve versiyonlama scripti
# Changelog:
# - İlk versiyon: otomatik commit, versiyonlama ve branch yönetimi

"""
Spec tamamlama otomatik commit ve versiyonlama scripti
"""

import argparse
import subprocess
import sys
from datetime import datetime
from typing import Optional

def run_command(cmd: str, cwd: Optional[str] = None) -> Optional[str]:
    """Komut çalıştır ve sonucu döndür"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Hata: {e}")
        print(f"Stderr: {e.stderr}")
        return None

def get_current_version() -> str:
    """Mevcut versiyonu al"""
    try:
        with open('VERSION', 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.1.0"

def bump_version(version_type: str = 'minor') -> str:
    """Versiyon artır"""
    current = get_current_version()
    major, minor, patch = map(int, current.split('.'))
    
    if version_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif version_type == 'minor':
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    new_version = f"{major}.{minor}.{patch}"
    
    # VERSION dosyasını güncelle
    with open('VERSION', 'w', encoding='utf-8') as f:
        f.write(new_version)
    
    return new_version

def main() -> None:
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description='Spec tamamlama otomatik commit')
    parser.add_argument('spec_name', help='Tamamlanan spec adı')
    parser.add_argument('--version-type', choices=['patch', 'minor', 'major'], 
                       default='minor', help='Version artırım tipi')
    parser.add_argument('--message', help='Ek commit mesajı')
    
    args = parser.parse_args()
    
    # Git durumunu kontrol et
    status = run_command('git status --porcelain')
    if not status:
        print("Değişiklik bulunamadı. Commit yapılacak bir şey yok.")
        return
    
    # Mevcut branch'i al
    current_branch = run_command('git branch --show-current')
    
    # Feature branch oluştur
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    feature_branch = f"feature/spec-{args.spec_name}-{timestamp}"
    
    print(f"Feature branch oluşturuluyor: {feature_branch}")
    run_command(f'git checkout -b {feature_branch}')
    
    # Değişiklikleri ekle
    run_command('git add .')
    
    # Versiyon artır
    new_version = bump_version(args.version_type)
    print(f"Versiyon güncellendi: {new_version}")
    
    # Commit mesajı oluştur
    commit_msg = f"""✅ Spec tamamlandı: {args.spec_name} (v{new_version})

📋 Spec Detayları:
- Spec Adı: {args.spec_name}
- Yeni Versiyon: v{new_version}
- Tamamlanma Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Branch: {feature_branch}

🔄 Değişiklikler:
- Spec görevleri tamamlandı
- Kod implementasyonu yapıldı
- Testler eklendi/güncellendi
- Dokümantasyon güncellendi

🤖 Otomatik oluşturuldu: Kiro AI Spec Workflow"""

    if args.message:
        commit_msg += f"\n\n📝 Ek Notlar:\n{args.message}"
    
    # Commit yap
    run_command(f'git commit -m "{commit_msg}"')
    
    # VERSION dosyasını da commit et
    run_command('git add VERSION')
    run_command(f'git commit --amend --no-edit')
    
    # Feature branch'i push et
    print(f"Feature branch push ediliyor...")
    run_command(f'git push -u origin {feature_branch}')
    
    # Ana branch'e geri dön
    run_command(f'git checkout {current_branch}')
    
    print(f"""
🎉 Spec tamamlama işlemi başarılı!

📊 Özet:
- Spec: {args.spec_name}
- Yeni Versiyon: v{new_version}
- Feature Branch: {feature_branch}
- GitHub'da PR oluşturulabilir

🔗 GitHub'da görüntüle:
https://github.com/Kafisabah/SONTECHSP/tree/{feature_branch}

💡 Sonraki adımlar:
1. GitHub'da Pull Request oluştur
2. Code review yap
3. Main branch'e merge et
4. Tag oluştur: git tag v{new_version}
""")

if __name__ == '__main__':
    main()