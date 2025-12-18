# Version: 0.1.0
# Last Update: 2024-12-18
# Module: mimari_dogrulama
# Description: Refactoring sonrası mimari doğrulama scripti
# Changelog:
# - İlk sürüm oluşturuldu

import os
import ast
import json
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict, deque
import networkx as nx

class MimariDogrulayici:
    """Mimari kurallarını doğrulayan sınıf"""
    
    def __init__(self):
        self.sonuclar = {
            'test_tarihi': datetime.now().isoformat(),
            'mimari_kurallar': {
                'katman_sinirlari': 'ui -> services -> repositories -> database',
                'yasakli_bagimliliklar': [
                    'ui -> repositories',
                    'ui -> database', 
                    'services -> ui',
                    'repositories -> services',
                    'repositories -> ui'
                ]
            },
            'dogrulama_sonuclari': {},
            'ozet': {}
        }
        
        # Katman tanımları
        self.katmanlar = {
            'ui': ['uygulama/arayuz'],
            'services': ['uygulama/pos/services', 'uygulama/stok/services', 'uygulama/crm/services'],
            'repositories': ['uygulama/pos/repositories', 'uygulama/stok/repositories', 'uygulama/crm/repositories'],
            'database': ['uygulama/database', 'uygulama/cekirdek/database']
        }
        
        # Import grafiği
        self.import_grafigi = nx.DiGraph()
        self.dosya_katman_haritasi = {}
    
    def dosya_katman_haritasini_olustur(self):
        """Dosyaları katmanlara göre sınıflandır"""
        print("🔍 Dosya-katman haritası oluşturuluyor...")
        
        for katman, dizinler in self.katmanlar.items():
            for dizin in dizinler:
                if os.path.exists(dizin):
                    for root, dirs, files in os.walk(dizin):
                        for file in files:
                            if file.endswith('.py') and not file.startswith('__'):
                                dosya_yolu = os.path.join(root, file).replace('\\', '/')
                                self.dosya_katman_haritasi[dosya_yolu] = katman
        
        print(f"✅ {len(self.dosya_katman_haritasi)} dosya katmanlara atandı")
        
        # Katman dağılımını göster
        katman_sayilari = defaultdict(int)
        for katman in self.dosya_katman_haritasi.values():
            katman_sayilari[katman] += 1
        
        for katman, sayi in katman_sayilari.items():
            print(f"   {katman}: {sayi} dosya")
    
    def import_grafigini_olustur(self):
        """Import bağımlılık grafiğini oluştur"""
        print("🔍 Import bağımlılık grafiği oluşturuluyor...")
        
        import_sayisi = 0
        
        for dosya_yolu in self.dosya_katman_haritasi.keys():
            try:
                with open(dosya_yolu, 'r', encoding='utf-8') as f:
                    icerik = f.read()
                
                tree = ast.parse(icerik)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        import_edilen_moduller = []
                        
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                import_edilen_moduller.append(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                import_edilen_moduller.append(node.module)
                        
                        for modul in import_edilen_moduller:
                            # Modülü dosya yoluna çevir
                            hedef_dosya = self.modul_adini_dosya_yoluna_cevir(modul)
                            
                            if hedef_dosya and hedef_dosya in self.dosya_katman_haritasi:
                                self.import_grafigi.add_edge(dosya_yolu, hedef_dosya)
                                import_sayisi += 1
                                
            except Exception as e:
                print(f"⚠️ Import analiz hatası {dosya_yolu}: {e}")
        
        print(f"✅ {import_sayisi} import bağımlılığı tespit edildi")
    
    def modul_adini_dosya_yoluna_cevir(self, modul_adi):
        """Modül adını dosya yoluna çevir"""
        # uygulama.arayuz.ekranlar.ebelge -> uygulama/arayuz/ekranlar/ebelge.py
        yol_parcalari = modul_adi.split('.')
        
        # Farklı uzantıları dene
        olasi_yollar = [
            '/'.join(yol_parcalari) + '.py',
            '/'.join(yol_parcalari) + '/__init__.py',
            '/'.join(yol_parcalari[:-1]) + '/' + yol_parcalari[-1] + '.py'
        ]
        
        for yol in olasi_yollar:
            if os.path.exists(yol):
                return yol.replace('\\', '/')
        
        return None
    
    def katman_sinirlarini_kontrol(self):
        """Katman sınırlarını kontrol et"""
        print("🔍 Katman sınırları kontrol ediliyor...")
        
        katman_ihlalleri = []
        katman_gecisleri = defaultdict(int)
        
        # Katman hiyerarşisi tanımla
        katman_hiyerarsi = {
            'ui': 0,
            'services': 1, 
            'repositories': 2,
            'database': 3
        }
        
        for kaynak, hedef in self.import_grafigi.edges():
            kaynak_katman = self.dosya_katman_haritasi.get(kaynak)
            hedef_katman = self.dosya_katman_haritasi.get(hedef)
            
            if kaynak_katman and hedef_katman and kaynak_katman != hedef_katman:
                katman_gecisleri[f"{kaynak_katman} -> {hedef_katman}"] += 1
                
                # Hiyerarşi kontrolü
                kaynak_seviye = katman_hiyerarsi.get(kaynak_katman, -1)
                hedef_seviye = katman_hiyerarsi.get(hedef_katman, -1)
                
                # Geriye doğru bağımlılık kontrolü (yasak)
                if kaynak_seviye > hedef_seviye:
                    katman_ihlalleri.append({
                        'kaynak_dosya': kaynak,
                        'hedef_dosya': hedef,
                        'kaynak_katman': kaynak_katman,
                        'hedef_katman': hedef_katman,
                        'ihlal_tipi': 'geriye_bagimlilik',
                        'aciklama': f"{kaynak_katman} katmanı {hedef_katman} katmanına bağımlı olamaz"
                    })
                
                # Katman atlama kontrolü (ui -> repositories gibi)
                if kaynak_seviye + 1 < hedef_seviye:
                    katman_ihlalleri.append({
                        'kaynak_dosya': kaynak,
                        'hedef_dosya': hedef,
                        'kaynak_katman': kaynak_katman,
                        'hedef_katman': hedef_katman,
                        'ihlal_tipi': 'katman_atlama',
                        'aciklama': f"{kaynak_katman} katmanı {hedef_katman} katmanına doğrudan bağımlı olamaz"
                    })
        
        sonuc = {
            'toplam_katman_gecisi': sum(katman_gecisleri.values()),
            'katman_gecis_dagilimi': dict(katman_gecisleri),
            'ihlal_sayisi': len(katman_ihlalleri),
            'ihlaller': katman_ihlalleri,
            'durum': 'BASARILI' if len(katman_ihlalleri) == 0 else 'UYARI'
        }
        
        self.sonuclar['dogrulama_sonuclari']['katman_sinirlari'] = sonuc
        
        print(f"✅ Katman sınırları kontrolü tamamlandı")
        print(f"   Toplam katman geçişi: {sonuc['toplam_katman_gecisi']}")
        print(f"   İhlal sayısı: {sonuc['ihlal_sayisi']}")
        
        return sonuc
    
    def dongusel_import_kontrol(self):
        """Döngüsel import'ları kontrol et"""
        print("🔍 Döngüsel import'lar kontrol ediliyor...")
        
        dongusel_importlar = []
        
        try:
            # NetworkX ile döngüleri bul
            donguler = list(nx.simple_cycles(self.import_grafigi))
            
            for dongu in donguler:
                if len(dongu) > 1:  # Kendine referans değil
                    dongu_bilgisi = {
                        'dongu_uzunlugu': len(dongu),
                        'dosyalar': dongu,
                        'katmanlar': [self.dosya_katman_haritasi.get(dosya, 'bilinmeyen') for dosya in dongu]
                    }
                    dongusel_importlar.append(dongu_bilgisi)
            
        except Exception as e:
            print(f"⚠️ Döngüsel import analiz hatası: {e}")
        
        sonuc = {
            'dongu_sayisi': len(dongusel_importlar),
            'donguler': dongusel_importlar,
            'durum': 'BASARILI' if len(dongusel_importlar) == 0 else 'UYARI'
        }
        
        self.sonuclar['dogrulama_sonuclari']['dongusel_importlar'] = sonuc
        
        print(f"✅ Döngüsel import kontrolü tamamlandı")
        print(f"   Döngü sayısı: {sonuc['dongu_sayisi']}")
        
        return sonuc
    
    def dependency_injection_kontrol(self):
        """Dependency injection pattern'ini kontrol et"""
        print("🔍 Dependency injection pattern kontrol ediliyor...")
        
        di_ihlalleri = []
        di_uygulamalari = []
        
        for dosya_yolu in self.dosya_katman_haritasi.keys():
            try:
                with open(dosya_yolu, 'r', encoding='utf-8') as f:
                    icerik = f.read()
                
                tree = ast.parse(icerik)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Constructor analizi
                        init_method = None
                        for method in node.body:
                            if isinstance(method, ast.FunctionDef) and method.name == '__init__':
                                init_method = method
                                break
                        
                        if init_method:
                            # Constructor parametrelerini kontrol et
                            param_sayisi = len(init_method.args.args) - 1  # self hariç
                            
                            # DI pattern göstergeleri
                            di_gostergesi = False
                            
                            # Constructor'da servis/repository injection'ı var mı?
                            for arg in init_method.args.args[1:]:  # self hariç
                                if any(keyword in arg.arg.lower() for keyword in 
                                      ['service', 'repository', 'factory', 'provider']):
                                    di_gostergesi = True
                                    break
                            
                            # Constructor içinde doğrudan import/instantiation var mı?
                            dogrudan_bagimlilık = False
                            for stmt in ast.walk(init_method):
                                if isinstance(stmt, ast.Call):
                                    if isinstance(stmt.func, ast.Name):
                                        if stmt.func.id.endswith('Service') or stmt.func.id.endswith('Repository'):
                                            dogrudan_bagimlilık = True
                                            break
                            
                            if di_gostergesi:
                                di_uygulamalari.append({
                                    'dosya': dosya_yolu,
                                    'sinif': node.name,
                                    'parametre_sayisi': param_sayisi
                                })
                            elif dogrudan_bagimlilık:
                                di_ihlalleri.append({
                                    'dosya': dosya_yolu,
                                    'sinif': node.name,
                                    'ihlal_tipi': 'dogrudan_bagimlilık',
                                    'aciklama': 'Constructor içinde doğrudan bağımlılık oluşturma'
                                })
                                
            except Exception as e:
                print(f"⚠️ DI analiz hatası {dosya_yolu}: {e}")
        
        toplam_sinif = len(di_uygulamalari) + len(di_ihlalleri)
        di_orani = (len(di_uygulamalari) / toplam_sinif * 100) if toplam_sinif > 0 else 0
        
        sonuc = {
            'toplam_sinif': toplam_sinif,
            'di_uygulayan_sinif': len(di_uygulamalari),
            'di_ihlal_eden_sinif': len(di_ihlalleri),
            'di_uygulama_orani': di_orani,
            'di_uygulamalari': di_uygulamalari,
            'di_ihlalleri': di_ihlalleri,
            'durum': 'BASARILI' if di_orani >= 50 else 'UYARI'
        }
        
        self.sonuclar['dogrulama_sonuclari']['dependency_injection'] = sonuc
        
        print(f"✅ Dependency injection kontrolü tamamlandı")
        print(f"   DI uygulama oranı: %{di_orani:.1f}")
        
        return sonuc
    
    def modul_yapisi_kontrol(self):
        """Modül yapısını kontrol et"""
        print("🔍 Modül yapısı kontrol ediliyor...")
        
        modul_sorunlari = []
        modul_istatistikleri = {
            'toplam_modul': 0,
            'init_dosyasi_olan': 0,
            'public_api_tanimlayan': 0,
            'dokumantasyon_olan': 0
        }
        
        # Refactor edilmiş modülleri kontrol et
        refactor_modulleri = [
            'uygulama/arayuz/ekranlar/ebelge',
            'uygulama/arayuz/ekranlar/raporlar',
            'uygulama/arayuz/ekranlar/ayarlar',
            'uygulama/pos/repositories/satis_repository',
            'uygulama/pos/repositories/offline_kuyruk_repository',
            'uygulama/pos/repositories/iade_repository'
        ]
        
        for modul_yolu in refactor_modulleri:
            if os.path.exists(modul_yolu):
                modul_istatistikleri['toplam_modul'] += 1
                
                # __init__.py kontrolü
                init_dosyasi = os.path.join(modul_yolu, '__init__.py')
                if os.path.exists(init_dosyasi):
                    modul_istatistikleri['init_dosyasi_olan'] += 1
                    
                    try:
                        with open(init_dosyasi, 'r', encoding='utf-8') as f:
                            init_icerik = f.read()
                        
                        # __all__ tanımı var mı?
                        if '__all__' in init_icerik:
                            modul_istatistikleri['public_api_tanimlayan'] += 1
                        
                        # Dokümantasyon var mı?
                        if '"""' in init_icerik or "'''" in init_icerik:
                            modul_istatistikleri['dokumantasyon_olan'] += 1
                            
                    except Exception as e:
                        modul_sorunlari.append({
                            'modul': modul_yolu,
                            'sorun': f"__init__.py okuma hatası: {e}"
                        })
                else:
                    modul_sorunlari.append({
                        'modul': modul_yolu,
                        'sorun': '__init__.py dosyası eksik'
                    })
        
        # Başarı oranları
        init_orani = (modul_istatistikleri['init_dosyasi_olan'] / 
                     modul_istatistikleri['toplam_modul'] * 100) if modul_istatistikleri['toplam_modul'] > 0 else 0
        
        api_orani = (modul_istatistikleri['public_api_tanimlayan'] / 
                    modul_istatistikleri['toplam_modul'] * 100) if modul_istatistikleri['toplam_modul'] > 0 else 0
        
        sonuc = {
            'modul_istatistikleri': modul_istatistikleri,
            'init_dosyasi_orani': init_orani,
            'public_api_orani': api_orani,
            'modul_sorunlari': modul_sorunlari,
            'durum': 'BASARILI' if init_orani >= 80 and len(modul_sorunlari) == 0 else 'UYARI'
        }
        
        self.sonuclar['dogrulama_sonuclari']['modul_yapisi'] = sonuc
        
        print(f"✅ Modül yapısı kontrolü tamamlandı")
        print(f"   __init__.py oranı: %{init_orani:.1f}")
        print(f"   Public API oranı: %{api_orani:.1f}")
        
        return sonuc
    
    def ozet_hesapla(self):
        """Genel özet hesapla"""
        print("📊 Mimari doğrulama özeti hesaplanıyor...")
        
        ozet = {
            'toplam_test': 0,
            'basarili_test': 0,
            'uyari_test': 0,
            'hata_test': 0,
            'genel_basari_orani': 0,
            'kritik_sorunlar': [],
            'oneriler': []
        }
        
        # Test sonuçlarını say
        for test_adi, sonuc in self.sonuclar['dogrulama_sonuclari'].items():
            ozet['toplam_test'] += 1
            durum = sonuc.get('durum', 'BİLİNMEYEN')
            
            if durum == 'BASARILI':
                ozet['basarili_test'] += 1
            elif durum == 'UYARI':
                ozet['uyari_test'] += 1
            else:
                ozet['hata_test'] += 1
        
        # Genel başarı oranı
        if ozet['toplam_test'] > 0:
            ozet['genel_basari_orani'] = (ozet['basarili_test'] / ozet['toplam_test'] * 100)
        
        # Kritik sorunları topla
        katman_sonucu = self.sonuclar['dogrulama_sonuclari'].get('katman_sinirlari', {})
        if katman_sonucu.get('ihlal_sayisi', 0) > 0:
            ozet['kritik_sorunlar'].append(f"Katman sınırı ihlali: {katman_sonucu['ihlal_sayisi']} adet")
        
        dongu_sonucu = self.sonuclar['dogrulama_sonuclari'].get('dongusel_importlar', {})
        if dongu_sonucu.get('dongu_sayisi', 0) > 0:
            ozet['kritik_sorunlar'].append(f"Döngüsel import: {dongu_sonucu['dongu_sayisi']} adet")
        
        # Öneriler
        di_sonucu = self.sonuclar['dogrulama_sonuclari'].get('dependency_injection', {})
        if di_sonucu.get('di_uygulama_orani', 0) < 50:
            ozet['oneriler'].append("Dependency injection pattern'ini daha yaygın kullanın")
        
        modul_sonucu = self.sonuclar['dogrulama_sonuclari'].get('modul_yapisi', {})
        if modul_sonucu.get('init_dosyasi_orani', 0) < 80:
            ozet['oneriler'].append("Tüm modüllere __init__.py dosyası ekleyin")
        
        self.sonuclar['ozet'] = ozet
        
        return ozet
    
    def rapor_olustur(self):
        """Detaylı rapor oluştur"""
        rapor_dosyasi = f"mimari_dogrulama_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(rapor_dosyasi, 'w', encoding='utf-8') as f:
                json.dump(self.sonuclar, f, indent=2, ensure_ascii=False)
            
            print(f"\n📋 Mimari doğrulama raporu oluşturuldu: {rapor_dosyasi}")
            
            # Özet yazdır
            self.ozet_yazdir()
            
        except Exception as e:
            print(f"❌ Rapor oluşturma hatası: {e}")
    
    def ozet_yazdir(self):
        """Test sonuçlarının özetini yazdır"""
        print("\n" + "="*70)
        print("🏗️ MİMARİ DOĞRULAMA ÖZETİ")
        print("="*70)
        
        ozet = self.sonuclar['ozet']
        
        # Genel durum
        print(f"🎯 Genel Başarı Oranı: %{ozet['genel_basari_orani']:.1f}")
        print(f"   Başarılı: {ozet['basarili_test']}, Uyarı: {ozet['uyari_test']}, Hata: {ozet['hata_test']}")
        
        # Test sonuçları
        print("\n📊 Test Sonuçları:")
        for test_adi, sonuc in self.sonuclar['dogrulama_sonuclari'].items():
            durum = sonuc.get('durum', 'BİLİNMEYEN')
            durum_emoji = "✅" if durum == 'BASARILI' else "⚠️" if durum == 'UYARI' else "❌"
            print(f"   {durum_emoji} {test_adi.replace('_', ' ').title()}: {durum}")
        
        # Kritik sorunlar
        if ozet['kritik_sorunlar']:
            print("\n🚨 Kritik Sorunlar:")
            for sorun in ozet['kritik_sorunlar']:
                print(f"   ❌ {sorun}")
        
        # Öneriler
        if ozet['oneriler']:
            print("\n💡 Öneriler:")
            for oneri in ozet['oneriler']:
                print(f"   💡 {oneri}")
        
        # Genel değerlendirme
        print(f"\n🎉 Genel Değerlendirme:")
        if ozet['genel_basari_orani'] >= 80:
            print("   Mükemmel! Mimari kurallar büyük ölçüde uygulanıyor.")
        elif ozet['genel_basari_orani'] >= 60:
            print("   İyi! Mimari genel olarak sağlam, bazı iyileştirmeler yapılabilir.")
        else:
            print("   Dikkat! Mimari kurallar yeterince uygulanmıyor, ciddi iyileştirmeler gerekli.")
    
    def tum_dogrulamalari_calistir(self):
        """Tüm mimari doğrulamalarını çalıştır"""
        print("🚀 Mimari doğrulama testleri başlatılıyor...\n")
        
        # Hazırlık
        self.dosya_katman_haritasini_olustur()
        self.import_grafigini_olustur()
        
        # Doğrulamalar
        self.katman_sinirlarini_kontrol()
        self.dongusel_import_kontrol()
        self.dependency_injection_kontrol()
        self.modul_yapisi_kontrol()
        
        # Özet ve rapor
        self.ozet_hesapla()
        self.rapor_olustur()


def main():
    """Ana fonksiyon"""
    dogrulayici = MimariDogrulayici()
    dogrulayici.tum_dogrulamalari_calistir()


if __name__ == "__main__":
    main()