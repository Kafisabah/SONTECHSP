# Version: 0.1.0
# Last Update: 2024-12-18
# Module: kod_kalitesi_metrikleri_dogrulama
# Description: Refactoring sonrası kod kalitesi metriklerini doğrulama scripti
# Changelog:
# - İlk sürüm oluşturuldu

import os
import ast
import json
import subprocess
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import re

class KodKalitesiMetrikDogrulayici:
    """Kod kalitesi metriklerini doğrulayan sınıf"""
    
    def __init__(self):
        self.sonuclar = {
            'test_tarihi': datetime.now().isoformat(),
            'hedefler': {
                'max_dosya_satir': 120,
                'max_fonksiyon_satir': 25,
                'hedef_dosya_sayisi': 30,  # 106 → 30 (%70 azalma)
                'hedef_fonksiyon_sayisi': 220  # 544 → 220 (%60 azalma)
            },
            'metrikler': {},
            'pep8_sonuclari': {},
            'ozet': {}
        }
        
        # Kontrol edilecek dizinler
        self.kontrol_dizinleri = [
            'uygulama/arayuz/ekranlar/ebelge',
            'uygulama/arayuz/ekranlar/raporlar',
            'uygulama/arayuz/ekranlar/ayarlar',
            'uygulama/pos/repositories/satis_repository',
            'uygulama/pos/repositories/offline_kuyruk_repository', 
            'uygulama/pos/repositories/iade_repository',
            'uygulama/pos/services',
            'kod_kalitesi_araclari'
        ]
    
    def dosya_metriklerini_hesapla(self):
        """Dosya metriklerini hesapla"""
        print("🔍 Dosya metrikleri hesaplanıyor...")
        
        dosya_metrikleri = {
            'toplam_dosya': 0,
            'hedef_altinda_dosya': 0,
            'buyuk_dosyalar': [],
            'dosya_boyut_dagilimi': defaultdict(int)
        }
        
        for dizin in self.kontrol_dizinleri:
            if os.path.exists(dizin):
                for root, dirs, files in os.walk(dizin):
                    for file in files:
                        if file.endswith('.py') and not file.startswith('__'):
                            dosya_yolu = os.path.join(root, file)
                            
                            try:
                                with open(dosya_yolu, 'r', encoding='utf-8') as f:
                                    icerik = f.read()
                                
                                # Satır sayısını hesapla (boş satırlar ve yorumlar hariç)
                                satirlar = [line.strip() for line in icerik.split('\n')]
                                kod_satirlari = [line for line in satirlar 
                                               if line and not line.startswith('#')]
                                satir_sayisi = len(kod_satirlari)
                                
                                dosya_metrikleri['toplam_dosya'] += 1
                                
                                # Boyut kategorisi
                                if satir_sayisi <= 50:
                                    dosya_metrikleri['dosya_boyut_dagilimi']['0-50'] += 1
                                elif satir_sayisi <= 120:
                                    dosya_metrikleri['dosya_boyut_dagilimi']['51-120'] += 1
                                elif satir_sayisi <= 200:
                                    dosya_metrikleri['dosya_boyut_dagilimi']['121-200'] += 1
                                else:
                                    dosya_metrikleri['dosya_boyut_dagilimi']['200+'] += 1
                                
                                # Hedef kontrolü
                                if satir_sayisi <= self.sonuclar['hedefler']['max_dosya_satir']:
                                    dosya_metrikleri['hedef_altinda_dosya'] += 1
                                else:
                                    dosya_metrikleri['buyuk_dosyalar'].append({
                                        'dosya': dosya_yolu,
                                        'satir_sayisi': satir_sayisi,
                                        'hedef_asimi': satir_sayisi - self.sonuclar['hedefler']['max_dosya_satir']
                                    })
                                    
                            except Exception as e:
                                print(f"⚠️ Dosya okuma hatası {dosya_yolu}: {e}")
        
        # Başarı oranını hesapla
        if dosya_metrikleri['toplam_dosya'] > 0:
            basari_orani = (dosya_metrikleri['hedef_altinda_dosya'] / 
                           dosya_metrikleri['toplam_dosya'] * 100)
        else:
            basari_orani = 0
        
        dosya_metrikleri['hedef_basari_orani'] = basari_orani
        dosya_metrikleri['durum'] = 'BASARILI' if basari_orani >= 70 else 'UYARI'
        
        self.sonuclar['metrikler']['dosya_metrikleri'] = dosya_metrikleri
        
        print(f"✅ Dosya analizi tamamlandı: {dosya_metrikleri['toplam_dosya']} dosya")
        print(f"   Hedef altında: {dosya_metrikleri['hedef_altinda_dosya']} (%{basari_orani:.1f})")
        
        return dosya_metrikleri
    
    def fonksiyon_metriklerini_hesapla(self):
        """Fonksiyon metriklerini hesapla"""
        print("🔍 Fonksiyon metrikleri hesaplanıyor...")
        
        fonksiyon_metrikleri = {
            'toplam_fonksiyon': 0,
            'hedef_altinda_fonksiyon': 0,
            'buyuk_fonksiyonlar': [],
            'fonksiyon_boyut_dagilimi': defaultdict(int)
        }
        
        for dizin in self.kontrol_dizinleri:
            if os.path.exists(dizin):
                for root, dirs, files in os.walk(dizin):
                    for file in files:
                        if file.endswith('.py') and not file.startswith('__'):
                            dosya_yolu = os.path.join(root, file)
                            
                            try:
                                with open(dosya_yolu, 'r', encoding='utf-8') as f:
                                    icerik = f.read()
                                
                                # AST ile fonksiyonları analiz et
                                tree = ast.parse(icerik)
                                
                                for node in ast.walk(tree):
                                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                        # Fonksiyon satır sayısını hesapla
                                        baslangic = node.lineno
                                        bitis = node.end_lineno if hasattr(node, 'end_lineno') else baslangic
                                        
                                        if bitis:
                                            satir_sayisi = bitis - baslangic + 1
                                            
                                            # Boş satırları ve yorumları çıkar
                                            fonksiyon_satirlari = icerik.split('\n')[baslangic-1:bitis]
                                            kod_satirlari = [line.strip() for line in fonksiyon_satirlari
                                                           if line.strip() and not line.strip().startswith('#')]
                                            gercek_satir_sayisi = len(kod_satirlari)
                                            
                                            fonksiyon_metrikleri['toplam_fonksiyon'] += 1
                                            
                                            # Boyut kategorisi
                                            if gercek_satir_sayisi <= 10:
                                                fonksiyon_metrikleri['fonksiyon_boyut_dagilimi']['0-10'] += 1
                                            elif gercek_satir_sayisi <= 25:
                                                fonksiyon_metrikleri['fonksiyon_boyut_dagilimi']['11-25'] += 1
                                            elif gercek_satir_sayisi <= 50:
                                                fonksiyon_metrikleri['fonksiyon_boyut_dagilimi']['26-50'] += 1
                                            else:
                                                fonksiyon_metrikleri['fonksiyon_boyut_dagilimi']['50+'] += 1
                                            
                                            # Hedef kontrolü
                                            if gercek_satir_sayisi <= self.sonuclar['hedefler']['max_fonksiyon_satir']:
                                                fonksiyon_metrikleri['hedef_altinda_fonksiyon'] += 1
                                            else:
                                                fonksiyon_metrikleri['buyuk_fonksiyonlar'].append({
                                                    'dosya': dosya_yolu,
                                                    'fonksiyon': node.name,
                                                    'satir_sayisi': gercek_satir_sayisi,
                                                    'hedef_asimi': gercek_satir_sayisi - self.sonuclar['hedefler']['max_fonksiyon_satir']
                                                })
                                    
                            except Exception as e:
                                print(f"⚠️ AST analiz hatası {dosya_yolu}: {e}")
        
        # Başarı oranını hesapla
        if fonksiyon_metrikleri['toplam_fonksiyon'] > 0:
            basari_orani = (fonksiyon_metrikleri['hedef_altinda_fonksiyon'] / 
                           fonksiyon_metrikleri['toplam_fonksiyon'] * 100)
        else:
            basari_orani = 0
        
        fonksiyon_metrikleri['hedef_basari_orani'] = basari_orani
        fonksiyon_metrikleri['durum'] = 'BASARILI' if basari_orani >= 60 else 'UYARI'
        
        self.sonuclar['metrikler']['fonksiyon_metrikleri'] = fonksiyon_metrikleri
        
        print(f"✅ Fonksiyon analizi tamamlandı: {fonksiyon_metrikleri['toplam_fonksiyon']} fonksiyon")
        print(f"   Hedef altında: {fonksiyon_metrikleri['hedef_altinda_fonksiyon']} (%{basari_orani:.1f})")
        
        return fonksiyon_metrikleri
    
    def pep8_uyumluluğu_kontrol(self):
        """PEP8 uyumluluğunu kontrol et"""
        print("🔍 PEP8 uyumluluğu kontrol ediliyor...")
        
        pep8_sonuclari = {
            'kontrol_edilen_dosyalar': 0,
            'hata_sayisi': 0,
            'uyari_sayisi': 0,
            'temiz_dosyalar': 0,
            'detaylar': []
        }
        
        # flake8 veya pycodestyle kullanmaya çalış
        for dizin in self.kontrol_dizinleri:
            if os.path.exists(dizin):
                try:
                    # flake8 ile kontrol et
                    result = subprocess.run(
                        ['flake8', '--max-line-length=120', '--ignore=E501,W503', dizin],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        # Hata yok
                        for root, dirs, files in os.walk(dizin):
                            for file in files:
                                if file.endswith('.py'):
                                    pep8_sonuclari['kontrol_edilen_dosyalar'] += 1
                                    pep8_sonuclari['temiz_dosyalar'] += 1
                    else:
                        # Hatalar var
                        hatalar = result.stdout.split('\n')
                        for hata in hatalar:
                            if hata.strip():
                                pep8_sonuclari['detaylar'].append(hata.strip())
                                if ':E' in hata:
                                    pep8_sonuclari['hata_sayisi'] += 1
                                elif ':W' in hata:
                                    pep8_sonuclari['uyari_sayisi'] += 1
                        
                        # Dosya sayısını hesapla
                        for root, dirs, files in os.walk(dizin):
                            for file in files:
                                if file.endswith('.py'):
                                    pep8_sonuclari['kontrol_edilen_dosyalar'] += 1
                    
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    # flake8 bulunamadı, manuel kontrol yap
                    print(f"⚠️ flake8 bulunamadı, {dizin} için manuel kontrol yapılıyor")
                    self.manuel_pep8_kontrol(dizin, pep8_sonuclari)
        
        # Başarı oranını hesapla
        if pep8_sonuclari['kontrol_edilen_dosyalar'] > 0:
            temiz_oran = (pep8_sonuclari['temiz_dosyalar'] / 
                         pep8_sonuclari['kontrol_edilen_dosyalar'] * 100)
        else:
            temiz_oran = 0
        
        pep8_sonuclari['temiz_dosya_orani'] = temiz_oran
        pep8_sonuclari['durum'] = 'BASARILI' if temiz_oran >= 80 else 'UYARI'
        
        self.sonuclar['pep8_sonuclari'] = pep8_sonuclari
        
        print(f"✅ PEP8 kontrolü tamamlandı: {pep8_sonuclari['kontrol_edilen_dosyalar']} dosya")
        print(f"   Temiz dosya oranı: %{temiz_oran:.1f}")
        
        return pep8_sonuclari
    
    def manuel_pep8_kontrol(self, dizin, sonuclar):
        """Manuel PEP8 kontrol (flake8 yoksa)"""
        for root, dirs, files in os.walk(dizin):
            for file in files:
                if file.endswith('.py'):
                    dosya_yolu = os.path.join(root, file)
                    sonuclar['kontrol_edilen_dosyalar'] += 1
                    
                    try:
                        with open(dosya_yolu, 'r', encoding='utf-8') as f:
                            satirlar = f.readlines()
                        
                        hata_var = False
                        
                        for i, satir in enumerate(satirlar, 1):
                            # Uzun satır kontrolü
                            if len(satir.rstrip()) > 120:
                                sonuclar['detaylar'].append(f"{dosya_yolu}:{i}: E501 line too long")
                                sonuclar['hata_sayisi'] += 1
                                hata_var = True
                            
                            # Tab karakteri kontrolü
                            if '\t' in satir:
                                sonuclar['detaylar'].append(f"{dosya_yolu}:{i}: W191 indentation contains tabs")
                                sonuclar['uyari_sayisi'] += 1
                                hata_var = True
                            
                            # Satır sonu boşluk kontrolü
                            if satir.endswith(' \n') or satir.endswith(' \r\n'):
                                sonuclar['detaylar'].append(f"{dosya_yolu}:{i}: W291 trailing whitespace")
                                sonuclar['uyari_sayisi'] += 1
                                hata_var = True
                        
                        if not hata_var:
                            sonuclar['temiz_dosyalar'] += 1
                            
                    except Exception as e:
                        print(f"⚠️ Manuel PEP8 kontrol hatası {dosya_yolu}: {e}")
    
    def karmasiklik_analizi(self):
        """Kod karmaşıklığı analizi"""
        print("🔍 Kod karmaşıklığı analiz ediliyor...")
        
        karmasiklik_sonuclari = {
            'ortalama_karmasiklik': 0,
            'yuksek_karmasiklik_fonksiyonlar': [],
            'karmasiklik_dagilimi': defaultdict(int)
        }
        
        toplam_karmasiklik = 0
        fonksiyon_sayisi = 0
        
        for dizin in self.kontrol_dizinleri:
            if os.path.exists(dizin):
                for root, dirs, files in os.walk(dizin):
                    for file in files:
                        if file.endswith('.py') and not file.startswith('__'):
                            dosya_yolu = os.path.join(root, file)
                            
                            try:
                                with open(dosya_yolu, 'r', encoding='utf-8') as f:
                                    icerik = f.read()
                                
                                tree = ast.parse(icerik)
                                
                                for node in ast.walk(tree):
                                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                        karmasiklik = self.hesapla_karmasiklik(node)
                                        toplam_karmasiklik += karmasiklik
                                        fonksiyon_sayisi += 1
                                        
                                        # Karmaşıklık kategorisi
                                        if karmasiklik <= 5:
                                            karmasiklik_sonuclari['karmasiklik_dagilimi']['1-5'] += 1
                                        elif karmasiklik <= 10:
                                            karmasiklik_sonuclari['karmasiklik_dagilimi']['6-10'] += 1
                                        elif karmasiklik <= 15:
                                            karmasiklik_sonuclari['karmasiklik_dagilimi']['11-15'] += 1
                                        else:
                                            karmasiklik_sonuclari['karmasiklik_dagilimi']['15+'] += 1
                                        
                                        # Yüksek karmaşıklık kontrolü
                                        if karmasiklik > 10:
                                            karmasiklik_sonuclari['yuksek_karmasiklik_fonksiyonlar'].append({
                                                'dosya': dosya_yolu,
                                                'fonksiyon': node.name,
                                                'karmasiklik': karmasiklik
                                            })
                                            
                            except Exception as e:
                                print(f"⚠️ Karmaşıklık analiz hatası {dosya_yolu}: {e}")
        
        if fonksiyon_sayisi > 0:
            karmasiklik_sonuclari['ortalama_karmasiklik'] = toplam_karmasiklik / fonksiyon_sayisi
        
        karmasiklik_sonuclari['durum'] = ('BASARILI' if karmasiklik_sonuclari['ortalama_karmasiklik'] <= 8 
                                         else 'UYARI')
        
        self.sonuclar['metrikler']['karmasiklik_analizi'] = karmasiklik_sonuclari
        
        print(f"✅ Karmaşıklık analizi tamamlandı")
        print(f"   Ortalama karmaşıklık: {karmasiklik_sonuclari['ortalama_karmasiklik']:.2f}")
        
        return karmasiklik_sonuclari
    
    def hesapla_karmasiklik(self, node):
        """Fonksiyon karmaşıklığını hesapla (McCabe)"""
        karmasiklik = 1  # Temel karmaşıklık
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                karmasiklik += 1
            elif isinstance(child, ast.ExceptHandler):
                karmasiklik += 1
            elif isinstance(child, ast.With):
                karmasiklik += 1
            elif isinstance(child, ast.BoolOp):
                karmasiklik += len(child.values) - 1
        
        return karmasiklik
    
    def ozet_hesapla(self):
        """Genel özet hesapla"""
        print("📊 Özet hesaplanıyor...")
        
        ozet = {
            'toplam_test': 0,
            'basarili_test': 0,
            'uyari_test': 0,
            'hata_test': 0,
            'genel_basari_orani': 0,
            'hedef_karsilama_durumu': {}
        }
        
        # Test sonuçlarını say
        for kategori, veriler in self.sonuclar['metrikler'].items():
            ozet['toplam_test'] += 1
            durum = veriler.get('durum', 'BİLİNMEYEN')
            
            if durum == 'BASARILI':
                ozet['basarili_test'] += 1
            elif durum == 'UYARI':
                ozet['uyari_test'] += 1
            else:
                ozet['hata_test'] += 1
        
        # PEP8 sonuçları
        if self.sonuclar['pep8_sonuclari']:
            ozet['toplam_test'] += 1
            durum = self.sonuclar['pep8_sonuclari'].get('durum', 'BİLİNMEYEN')
            
            if durum == 'BASARILI':
                ozet['basarili_test'] += 1
            elif durum == 'UYARI':
                ozet['uyari_test'] += 1
            else:
                ozet['hata_test'] += 1
        
        # Genel başarı oranı
        if ozet['toplam_test'] > 0:
            ozet['genel_basari_orani'] = (ozet['basarili_test'] / ozet['toplam_test'] * 100)
        
        # Hedef karşılama durumu
        dosya_metrikleri = self.sonuclar['metrikler'].get('dosya_metrikleri', {})
        fonksiyon_metrikleri = self.sonuclar['metrikler'].get('fonksiyon_metrikleri', {})
        
        ozet['hedef_karsilama_durumu'] = {
            'dosya_boyutu_hedefi': {
                'hedef': f"≤{self.sonuclar['hedefler']['max_dosya_satir']} satır",
                'mevcut_oran': f"%{dosya_metrikleri.get('hedef_basari_orani', 0):.1f}",
                'durum': dosya_metrikleri.get('durum', 'BİLİNMEYEN')
            },
            'fonksiyon_boyutu_hedefi': {
                'hedef': f"≤{self.sonuclar['hedefler']['max_fonksiyon_satir']} satır",
                'mevcut_oran': f"%{fonksiyon_metrikleri.get('hedef_basari_orani', 0):.1f}",
                'durum': fonksiyon_metrikleri.get('durum', 'BİLİNMEYEN')
            }
        }
        
        self.sonuclar['ozet'] = ozet
        
        return ozet
    
    def rapor_olustur(self):
        """Detaylı rapor oluştur"""
        rapor_dosyasi = f"kod_kalitesi_metrikleri_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(rapor_dosyasi, 'w', encoding='utf-8') as f:
                json.dump(self.sonuclar, f, indent=2, ensure_ascii=False)
            
            print(f"\n📋 Kod kalitesi metrikleri raporu oluşturuldu: {rapor_dosyasi}")
            
            # Özet yazdır
            self.ozet_yazdir()
            
        except Exception as e:
            print(f"❌ Rapor oluşturma hatası: {e}")
    
    def ozet_yazdir(self):
        """Test sonuçlarının özetini yazdır"""
        print("\n" + "="*70)
        print("📊 KOD KALİTESİ METRİKLERİ ÖZETİ")
        print("="*70)
        
        ozet = self.sonuclar['ozet']
        
        # Genel durum
        print(f"🎯 Genel Başarı Oranı: %{ozet['genel_basari_orani']:.1f}")
        print(f"   Başarılı: {ozet['basarili_test']}, Uyarı: {ozet['uyari_test']}, Hata: {ozet['hata_test']}")
        
        print("\n📏 Hedef Karşılama Durumu:")
        for hedef, bilgi in ozet['hedef_karsilama_durumu'].items():
            durum_emoji = "✅" if bilgi['durum'] == 'BASARILI' else "⚠️"
            print(f"   {durum_emoji} {hedef.replace('_', ' ').title()}: {bilgi['mevcut_oran']} (Hedef: {bilgi['hedef']})")
        
        # Detaylı metrikler
        print("\n📊 Detaylı Metrikler:")
        
        dosya_metrikleri = self.sonuclar['metrikler'].get('dosya_metrikleri', {})
        if dosya_metrikleri:
            print(f"   📁 Dosyalar: {dosya_metrikleri['toplam_dosya']} toplam")
            print(f"      Hedef altında: {dosya_metrikleri['hedef_altinda_dosya']} (%{dosya_metrikleri['hedef_basari_orani']:.1f})")
            print(f"      Büyük dosya: {len(dosya_metrikleri['buyuk_dosyalar'])}")
        
        fonksiyon_metrikleri = self.sonuclar['metrikler'].get('fonksiyon_metrikleri', {})
        if fonksiyon_metrikleri:
            print(f"   🔧 Fonksiyonlar: {fonksiyon_metrikleri['toplam_fonksiyon']} toplam")
            print(f"      Hedef altında: {fonksiyon_metrikleri['hedef_altinda_fonksiyon']} (%{fonksiyon_metrikleri['hedef_basari_orani']:.1f})")
            print(f"      Büyük fonksiyon: {len(fonksiyon_metrikleri['buyuk_fonksiyonlar'])}")
        
        pep8_sonuclari = self.sonuclar['pep8_sonuclari']
        if pep8_sonuclari:
            print(f"   📋 PEP8: {pep8_sonuclari['kontrol_edilen_dosyalar']} dosya kontrol edildi")
            print(f"      Temiz dosya: {pep8_sonuclari['temiz_dosyalar']} (%{pep8_sonuclari['temiz_dosya_orani']:.1f})")
            print(f"      Hata: {pep8_sonuclari['hata_sayisi']}, Uyarı: {pep8_sonuclari['uyari_sayisi']}")
        
        karmasiklik = self.sonuclar['metrikler'].get('karmasiklik_analizi', {})
        if karmasiklik:
            print(f"   🧮 Karmaşıklık: Ortalama {karmasiklik['ortalama_karmasiklik']:.2f}")
            print(f"      Yüksek karmaşıklık: {len(karmasiklik['yuksek_karmasiklik_fonksiyonlar'])} fonksiyon")
        
        # Genel değerlendirme
        print(f"\n🎉 Genel Değerlendirme:")
        if ozet['genel_basari_orani'] >= 80:
            print("   Mükemmel! Kod kalitesi hedefleri büyük ölçüde karşılandı.")
        elif ozet['genel_basari_orani'] >= 60:
            print("   İyi! Kod kalitesi kabul edilebilir seviyede, bazı iyileştirmeler yapılabilir.")
        else:
            print("   Dikkat! Kod kalitesi hedefleri karşılanmadı, ciddi iyileştirmeler gerekli.")
    
    def tum_metrikleri_hesapla(self):
        """Tüm metrikleri hesapla"""
        print("🚀 Kod kalitesi metrikleri doğrulama başlatılıyor...\n")
        
        # Metrikleri hesapla
        self.dosya_metriklerini_hesapla()
        self.fonksiyon_metriklerini_hesapla()
        self.pep8_uyumluluğu_kontrol()
        self.karmasiklik_analizi()
        
        # Özet hesapla
        self.ozet_hesapla()
        
        # Rapor oluştur
        self.rapor_olustur()


def main():
    """Ana fonksiyon"""
    dogrulayici = KodKalitesiMetrikDogrulayici()
    dogrulayici.tum_metrikleri_hesapla()


if __name__ == "__main__":
    main()