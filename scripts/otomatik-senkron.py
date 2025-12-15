#!/usr/bin/env python3
"""
Otomatik GitHub senkronizasyon scripti
Her 30 dakikada bir değişiklikleri kontrol eder ve push yapar
"""
import os
import sys
import subprocess
import time
from datetime import datetime
import schedule

def run_command(cmd, cwd=None):
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
        return None

def check_and_sync():
    """Değişiklikleri kontrol et ve senkronize et"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Değişiklikler kontrol ediliyor...")
    
    # Git durumunu kontrol et
    status = run_command('git status --porcelain')
    
    if not status:
        print("Değişiklik bulunamadı.")
        return
    
    print(f"Değişiklikler bulundu:\n{status}")
    
    # Değişiklikleri ekle
    run_command('git add .')
    
    # Commit yap
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    commit_msg = f"""🔄 Otomatik senkronizasyon: {timestamp}

📝 Değişiklikler:
{status}

🤖 Otomatik commit: Kiro AI Auto-Sync"""
    
    result = run_command(f'git commit -m "{commit_msg}"')
    if result is None:
        print("Commit başarısız.")
        return
    
    # Push yap
    result = run_command('git push')
    if result is None:
        print("Push başarısız.")
        return
    
    print(f"✅ Değişiklikler başarıyla GitHub'a yüklendi!")

def main():
    print("🚀 SONTECHSP Otomatik Senkronizasyon Başlatıldı")
    print("📅 Her 30 dakikada bir değişiklikler kontrol edilecek")
    print("⏹️  Durdurmak için Ctrl+C basın\n")
    
    # Her 30 dakikada bir çalıştır
    schedule.every(30).minutes.do(check_and_sync)
    
    # İlk kontrolü hemen yap
    check_and_sync()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Her dakika kontrol et
    except KeyboardInterrupt:
        print("\n🛑 Otomatik senkronizasyon durduruldu.")

if __name__ == '__main__':
    main()