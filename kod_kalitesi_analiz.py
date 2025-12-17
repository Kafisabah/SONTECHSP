# Version: 0.1.0
# Last Update: 2024-12-18
# Module: kod_kalitesi_analiz
# Description: Kod kalitesi analizi ve raporlama aracı
# Changelog:
# - İlk versiyon: kod analizi ve rapor üretimi

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ast
import json
import os
from datetime import datetime


def kod_kalitesi_analizi():
    """Kod kalitesi analizi yapar"""
    print("=== KOD KALİTESİ ANALİZİ BAŞLATIYOR ===")
    print(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    buyuk_dosyalar = []uk_dosyalar = []
    buyuk_fonksiyonlar = []
    toplam_dosya = 0
    mimari_ihlaller = []

    for root, dirs, files in os.walk('.'):
        # Test, cache ve git klasörlerini atla
        if any(skip in root for skip in ['test', '.kiro', '__pycache__', '.git', '.hypothesis', 'htmlcov']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                toplam_dosya += 1
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.splitlines()
                    
                    # Yorum olmayan satırları say
                    non_comment_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
                    
                    # Büyük dosyaları tespit et
                    if len(non_comment_lines) > 120:
                        buyuk_dosyalar.append({
                            'dosya': file_path,
                            'satir_sayisi': len(non_comment_lines),
                            'limit_asimi': len(non_comment_lines) - 120
                        })
                    
                    # Fonksiyon analizi
                    try:
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                func_lines = node.end_lineno - node.lineno + 1
                                if func_lines > 25:
                                    buyuk_fonksiyonlar.append({
                                        'dosya': file_path,
                                        'fonksiyon': node.name,
                                        'satir_sayisi': func_lines,
                                        'limit_asimi': func_lines - 25
                                    })
                    except:
                        pass
                    
                    # Mimari ihlal kontrolü (basit)
                    if 'ui' in file_path or 'arayuz' in file_path:
                        if 'from sqlalchemy' in content or 'import sqlalchemy' in content:
                            mimari_ihlaller.append({
                                'dosya': file_path,
                                'ihlal': 'UI katmanında doğrudan SQLAlchemy kullanımı',
                                'tip': 'mimari_ihlal'
                            })
                        
                except Exception as e:
                    print(f"Hata {file_path}: {e}")

    # Sıralama
    buyuk_dosyalar.sort(key=lambda x: x['satir_sayisi'], reverse=True)
    buyuk_fonksiyonlar.sort(key=lambda x: x['satir_sayisi'], reverse=True)

    # Sonuçları yazdır
    print(f"Toplam Python Dosyası: {toplam_dosya}")
    print(f"120+ Satırlı Dosya: {len(buyuk_dosyalar)}")
    print(f"25+ Satırlı Fonksiyon: {len(buyuk_fonksiyonlar)}")
    print(f"Mimari İhlal: {len(mimari_ihlaller)}")
    print()

    print("=== EN SORUNLU 15 DOSYA ===")
    for i, dosya in enumerate(buyuk_dosyalar[:15]):
        print(f"{i+1:2d}. {dosya['dosya']:60} {dosya['satir_sayisi']:4d} satır (+{dosya['limit_asimi']:3d})")

    print()
    print("=== EN SORUNLU 15 FONKSIYON ===")
    for i, fonk in enumerate(buyuk_fonksiyonlar[:15]):
        print(f"{i+1:2d}. {fonk['dosya']:40}::{fonk['fonksiyon']:20} {fonk['satir_sayisi']:3d} satır (+{fonk['limit_asimi']:2d})")

    if mimari_ihlaller:
        print()
        print("=== MIMARİ İHLALLER ===")
        for i, ihlal in enumerate(mimari_ihlaller[:10]):
            print(f"{i+1:2d}. {ihlal['dosya']:50} - {ihlal['ihlal']}")

    # Rapor oluştur
    rapor = {
        'analiz_tarihi': datetime.now().isoformat(),
        'toplam_dosya': toplam_dosya,
        'buyuk_dosya_sayisi': len(buyuk_dosyalar),
        'buyuk_fonksiyon_sayisi': len(buyuk_fonksiyonlar),
        'mimari_ihlal_sayisi': len(mimari_ihlaller),
        'buyuk_dosyalar': buyuk_dosyalar,
        'buyuk_fonksiyonlar': buyuk_fonksiyonlar,
        'mimari_ihlaller': mimari_ihlaller,
        'oneriler': [
            "En büyük dosyaları öncelikle bölün",
            "En büyük fonksiyonları yardımcı fonksiyonlara ayırın", 
            "UI katmanındaki mimari ihlalleri düzeltin",
            "Kod tekrarlarını ortak modüllere taşıyın"
        ]
    }

    # JSON dosyasına kaydet
    with open('kod_kalitesi_raporu.json', 'w', encoding='utf-8') as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)

    print()
    print("=== RAPOR KAYDEDİLDİ ===")
    print("Detaylı rapor: kod_kalitesi_raporu.json")
    
    return rapor

if __name__ == "__main__":
    kod_kalitesi_analizi()