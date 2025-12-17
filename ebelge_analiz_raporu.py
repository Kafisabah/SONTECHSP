# Version: 0.1.0
# Last Update: 2024-12-18
# Module: ebelge_analiz_raporu
# Description: E-belge dosyası analiz raporu
# Changelog:
# - İlk sürüm oluşturuldu

import ast
import os
from typing import Dict, List, Tuple

class EbelgeAnalizoru:
    """E-belge dosyası analiz aracı"""
    
    def __init__(self, dosya_yolu: str):
        self.dosya_yolu = dosya_yolu
        self.fonksiyonlar = []
        self.siniflar = []
        self.import_listesi = []
        
    def analiz_et(self) -> Dict:
        """Dosyayı analiz et"""
        with open(self.dosya_yolu, 'r', encoding='utf-8') as f:
            icerik = f.read()
        
        tree = ast.parse(icerik)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self.fonksiyonlar.append({
                    'ad': node.name,
                    'satir_baslangic': node.lineno,
                    'satir_bitis': node.end_lineno,
                    'satir_sayisi': node.end_lineno - node.lineno + 1,
                    'docstring': ast.get_docstring(node),
                    'args': [arg.arg for arg in node.args.args]
                })
            elif isinstance(node, ast.ClassDef):
                self.siniflar.append({
                    'ad': node.name,
                    'satir_baslangic': node.lineno,
                    'satir_bitis': node.end_lineno,
                    'satir_sayisi': node.end_lineno - node.lineno + 1
                })
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    self.import_listesi.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        self.import_listesi.append(f"{node.module}.{alias.name}")
        
        return {
            'fonksiyonlar': self.fonksiyonlar,
            'siniflar': self.siniflar,
            'import_listesi': self.import_listesi,
            'toplam_satir': len(icerik.split('\n'))
        }
    
    def fonksiyonel_gruplama_yap(self) -> Dict[str, List]:
        """Fonksiyonları gruplara ayır"""
        gruplar = {
            'ana_ekran': [],
            'filtreler': [],
            'islemler': [],
            'durum': [],
            'tablolar': [],
            'yardimcilar': []
        }
        
        for fonk in self.fonksiyonlar:
            ad = fonk['ad']
            
            if any(kelime in ad for kelime in ['__init__', 'ekrani_hazirla', 'sol_panel', 'sag_panel']):
                gruplar['ana_ekran'].append(fonk)
            elif any(kelime in ad for kelime in ['filtre', 'Filtre']):
                gruplar['filtreler'].append(fonk)
            elif any(kelime in ad for kelime in ['islem', 'gonder', 'sorgula', 'dene', 'toplu', 'xml']):
                gruplar['islemler'].append(fonk)
            elif any(kelime in ad for kelime in ['durum', 'Durum', 'baslat', 'bitir']):
                gruplar['durum'].append(fonk)
            elif any(kelime in ad for kelime in ['tablo', 'liste', 'guncelle', 'yenile']):
                gruplar['tablolar'].append(fonk)
            else:
                gruplar['yardimcilar'].append(fonk)
        
        return gruplar

def main():
    """Ana fonksiyon"""
    analizor = EbelgeAnalizoru('uygulama/arayuz/ekranlar/ebelge.py')
    sonuc = analizor.analiz_et()
    gruplar = analizor.fonksiyonel_gruplama_yap()
    
    print("=== E-BELGE DOSYASI ANALİZ RAPORU ===")
    print(f"Toplam Satır: {sonuc['toplam_satir']}")
    print(f"Toplam Fonksiyon: {len(sonuc['fonksiyonlar'])}")
    print(f"Toplam Sınıf: {len(sonuc['siniflar'])}")
    print()
    
    print("=== BÜYÜK FONKSİYONLAR (25+ satır) ===")
    buyuk_fonksiyonlar = [f for f in sonuc['fonksiyonlar'] if f['satir_sayisi'] >= 25]
    for fonk in sorted(buyuk_fonksiyonlar, key=lambda x: x['satir_sayisi'], reverse=True):
        print(f"- {fonk['ad']}: {fonk['satir_sayisi']} satır (satır {fonk['satir_baslangic']}-{fonk['satir_bitis']})")
    print()
    
    print("=== FONKSİYONEL GRUPLAMA ===")
    for grup_ad, fonksiyonlar in gruplar.items():
        toplam_satir = sum(f['satir_sayisi'] for f in fonksiyonlar)
        print(f"{grup_ad.upper()}: {len(fonksiyonlar)} fonksiyon, {toplam_satir} satır")
        for fonk in fonksiyonlar:
            print(f"  - {fonk['ad']}: {fonk['satir_sayisi']} satır")
        print()
    
    print("=== BÖLME PLANI ÖNERİSİ ===")
    print("1. ebelge_ana.py (Ana ekran): ~150 satır")
    print("   - __init__, ekrani_hazirla, sol_panel_olustur, sag_panel_olustur")
    print()
    print("2. ebelge_filtreleri.py (Filtreler): ~120 satır")
    print("   - filtre_grubu_olustur, filtre_uygula")
    print()
    print("3. ebelge_islemleri.py (İşlemler): ~130 satır")
    print("   - islemler_grubu_olustur, belge_gonder, durum_sorgula, tekrar_dene, toplu_gonder, xml_goruntule")
    print()
    print("4. ebelge_durum.py (Durum): ~80 satır")
    print("   - durum_bilgisi_grubu_olustur, islem_baslat, islem_bitir")
    print()
    print("5. ebelge_tablolar.py (Tablolar): ~200 satır")
    print("   - Tüm tablo oluşturma ve güncelleme fonksiyonları")
    print()
    print("6. ebelge_yardimcilar.py (Yardımcılar): ~100 satır")
    print("   - verileri_yukle, verileri_temizle, tablo_ayarlarini_uygula")

if __name__ == "__main__":
    main()