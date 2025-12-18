# Version: 0.1.0
# Last Update: 2024-12-18
# Module: performans_dogrulama
# Description: Refactoring sonrası performans doğrulama scripti
# Changelog:
# - İlk sürüm oluşturuldu
# - Dosya başlığı düzeltildi

import time
import psutil
import os
import sys
import json
from datetime import datetime
from pathlib import Path
import importlib.util
import tracemalloc
import gc

class PerformansDogrulayici:
    """Refactoring sonrası performans doğrulama sınıfı"""
    
    def __init__(self):
        self.sonuclar = {
            'test_tarihi': datetime.now().isoformat(),
            'sistem_bilgileri': self.sistem_bilgilerini_al(),
            'testler': {}
        }
        self.baseline_dosyasi = 'performans_baseline.json'
        
    def sistem_bilgilerini_al(self):
        """Sistem bilgilerini topla"""
        return {
            'cpu_sayisi': psutil.cpu_count(),
            'toplam_ram': psutil.virtual_memory().total,
            'python_versiyonu': sys.version,
            'platform': sys.platform
        }
    
    def bellek_kullanimi_test(self):
        """Bellek kullanımı testi"""
        print("🔍 Bellek kullanımı testi başlatılıyor...")
        
        # Başlangıç bellek durumu
        gc.collect()
        baslangic_bellek = psutil.Process().memory_info().rss
        
        # Tracemalloc başlat
        tracemalloc.start()
        
        try:
            # Ana modülleri import et
            self.ana_modulleri_yukle()
            
            # Bellek kullanımını ölç
            mevcut_bellek = psutil.Process().memory_info().rss
            bellek_farki = mevcut_bellek - baslangic_bellek
            
            # Tracemalloc sonuçları
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            sonuc = {
                'baslangic_bellek_mb': baslangic_bellek / 1024 / 1024,
                'mevcut_bellek_mb': mevcut_bellek / 1024 / 1024,
                'bellek_artisi_mb': bellek_farki / 1024 / 1024,
                'peak_bellek_mb': peak / 1024 / 1024,
                'durum': 'BASARILI' if bellek_farki < 100 * 1024 * 1024 else 'UYARI'  # 100MB limit
            }
            
            self.sonuclar['testler']['bellek_kullanimi'] = sonuc
            print(f"✅ Bellek kullanımı: {sonuc['bellek_artisi_mb']:.2f} MB")
            
            return sonuc
            
        except Exception as e:
            tracemalloc.stop()
            hata_sonuc = {
                'hata': str(e),
                'durum': 'HATA'
            }
            self.sonuclar['testler']['bellek_kullanimi'] = hata_sonuc
            print(f"❌ Bellek testi hatası: {e}")
            return hata_sonuc
    
    def ana_modulleri_yukle(self):
        """Ana modülleri yükle"""
        modul_yollari = [
            'uygulama.arayuz.ekranlar.ebelge',
            'uygulama.arayuz.ekranlar.raporlar',
            'uygulama.arayuz.ekranlar.ayarlar',
            'uygulama.pos.repositories.satis_repository',
            'uygulama.pos.repositories.offline_kuyruk_repository',
            'uygulama.pos.repositories.iade_repository'
        ]
        
        for modul_yolu in modul_yollari:
            try:
                # Modülü import et
                modul = importlib.import_module(modul_yolu)
                # Modülün ana sınıflarını çağır
                if hasattr(modul, '__all__'):
                    for sinif_adi in modul.__all__:
                        getattr(modul, sinif_adi)
            except ImportError:
                # Modül bulunamazsa geç
                continue
    
    def import_hizi_test(self):
        """Import hızı testi"""
        print("🔍 Import hızı testi başlatılıyor...")
        
        test_modulleri = [
            'uygulama.arayuz.ekranlar.ebelge.ebelge_ana',
            'uygulama.arayuz.ekranlar.raporlar.rapor_olusturma',
            'uygulama.arayuz.ekranlar.ayarlar.ayarlar',
            'uygulama.pos.repositories.satis_repository.satis_crud',
            'uygulama.pos.repositories.offline_kuyruk_repository.kuyruk_islemleri'
        ]
        
        import_sureleri = {}
        toplam_sure = 0
        
        for modul_adi in test_modulleri:
            try:
                baslangic = time.time()
                importlib.import_module(modul_adi)
                bitis = time.time()
                
                sure = (bitis - baslangic) * 1000  # milisaniye
                import_sureleri[modul_adi] = sure
                toplam_sure += sure
                
            except ImportError as e:
                import_sureleri[modul_adi] = f"HATA: {str(e)}"
        
        ortalama_sure = toplam_sure / len([s for s in import_sureleri.values() if isinstance(s, float)])
        
        sonuc = {
            'import_sureleri_ms': import_sureleri,
            'toplam_sure_ms': toplam_sure,
            'ortalama_sure_ms': ortalama_sure,
            'durum': 'BASARILI' if ortalama_sure < 100 else 'UYARI'  # 100ms limit
        }
        
        self.sonuclar['testler']['import_hizi'] = sonuc
        print(f"✅ Ortalama import süresi: {ortalama_sure:.2f} ms")
        
        return sonuc
    
    def dosya_boyutu_analizi(self):
        """Dosya boyutlarını analiz et"""
        print("🔍 Dosya boyutu analizi başlatılıyor...")
        
        # Refactor edilmiş dosyaları kontrol et
        kontrol_dizinleri = [
            'uygulama/arayuz/ekranlar/ebelge',
            'uygulama/arayuz/ekranlar/raporlar', 
            'uygulama/arayuz/ekranlar/ayarlar',
            'uygulama/pos/repositories/satis_repository',
            'uygulama/pos/repositories/offline_kuyruk_repository',
            'uygulama/pos/repositories/iade_repository'
        ]
        
        dosya_boyutlari = {}
        buyuk_dosyalar = []
        toplam_dosya = 0
        hedef_altinda = 0
        
        for dizin in kontrol_dizinleri:
            if os.path.exists(dizin):
                for root, dirs, files in os.walk(dizin):
                    for file in files:
                        if file.endswith('.py') and not file.startswith('__'):
                            dosya_yolu = os.path.join(root, file)
                            boyut = os.path.getsize(dosya_yolu)
                            
                            # Satır sayısını hesapla
                            try:
                                with open(dosya_yolu, 'r', encoding='utf-8') as f:
                                    satirlar = len([line for line in f if line.strip() and not line.strip().startswith('#')])
                            except:
                                satirlar = 0
                            
                            dosya_boyutlari[dosya_yolu] = {
                                'boyut_byte': boyut,
                                'satir_sayisi': satirlar
                            }
                            
                            toplam_dosya += 1
                            
                            # 120 satır hedefini kontrol et
                            if satirlar <= 120:
                                hedef_altinda += 1
                            else:
                                buyuk_dosyalar.append({
                                    'dosya': dosya_yolu,
                                    'satir_sayisi': satirlar
                                })
        
        hedef_yuzdesi = (hedef_altinda / toplam_dosya * 100) if toplam_dosya > 0 else 0
        
        sonuc = {
            'toplam_dosya': toplam_dosya,
            'hedef_altinda_dosya': hedef_altinda,
            'hedef_yuzdesi': hedef_yuzdesi,
            'buyuk_dosyalar': buyuk_dosyalar,
            'durum': 'BASARILI' if hedef_yuzdesi >= 70 else 'UYARI'  # %70 hedef
        }
        
        self.sonuclar['testler']['dosya_boyutu'] = sonuc
        print(f"✅ Hedef altında dosya oranı: %{hedef_yuzdesi:.1f}")
        
        return sonuc
    
    def cpu_kullanimi_test(self):
        """CPU kullanımı testi"""
        print("🔍 CPU kullanımı testi başlatılıyor...")
        
        # Başlangıç CPU durumu
        baslangic_cpu = psutil.cpu_percent(interval=1)
        
        try:
            # Yoğun işlem simülasyonu
            baslangic = time.time()
            
            # Modül import ve sınıf oluşturma işlemleri
            for i in range(10):
                self.ana_modulleri_yukle()
                gc.collect()
            
            bitis = time.time()
            
            # Bitiş CPU durumu
            bitis_cpu = psutil.cpu_percent(interval=1)
            
            islem_suresi = bitis - baslangic
            cpu_artisi = bitis_cpu - baslangic_cpu
            
            sonuc = {
                'baslangic_cpu_yuzde': baslangic_cpu,
                'bitis_cpu_yuzde': bitis_cpu,
                'cpu_artisi_yuzde': cpu_artisi,
                'islem_suresi_saniye': islem_suresi,
                'durum': 'BASARILI' if cpu_artisi < 50 else 'UYARI'  # %50 limit
            }
            
            self.sonuclar['testler']['cpu_kullanimi'] = sonuc
            print(f"✅ CPU artışı: %{cpu_artisi:.1f}")
            
            return sonuc
            
        except Exception as e:
            hata_sonuc = {
                'hata': str(e),
                'durum': 'HATA'
            }
            self.sonuclar['testler']['cpu_kullanimi'] = hata_sonuc
            print(f"❌ CPU testi hatası: {e}")
            return hata_sonuc
    
    def baseline_karsilastir(self):
        """Baseline ile karşılaştır"""
        if not os.path.exists(self.baseline_dosyasi):
            print("⚠️ Baseline dosyası bulunamadı, mevcut sonuçlar baseline olarak kaydediliyor")
            self.baseline_kaydet()
            return
        
        try:
            with open(self.baseline_dosyasi, 'r', encoding='utf-8') as f:
                baseline = json.load(f)
            
            print("\n📊 Baseline Karşılaştırması:")
            
            # Bellek karşılaştırması
            if 'bellek_kullanimi' in baseline.get('testler', {}):
                baseline_bellek = baseline['testler']['bellek_kullanimi'].get('bellek_artisi_mb', 0)
                mevcut_bellek = self.sonuclar['testler'].get('bellek_kullanimi', {}).get('bellek_artisi_mb', 0)
                
                if isinstance(baseline_bellek, (int, float)) and isinstance(mevcut_bellek, (int, float)):
                    fark = mevcut_bellek - baseline_bellek
                    yuzde_fark = (fark / baseline_bellek * 100) if baseline_bellek > 0 else 0
                    
                    print(f"  Bellek: {mevcut_bellek:.2f} MB (Baseline: {baseline_bellek:.2f} MB, Fark: {fark:+.2f} MB, %{yuzde_fark:+.1f})")
            
            # Import hızı karşılaştırması
            if 'import_hizi' in baseline.get('testler', {}):
                baseline_import = baseline['testler']['import_hizi'].get('ortalama_sure_ms', 0)
                mevcut_import = self.sonuclar['testler'].get('import_hizi', {}).get('ortalama_sure_ms', 0)
                
                if isinstance(baseline_import, (int, float)) and isinstance(mevcut_import, (int, float)):
                    fark = mevcut_import - baseline_import
                    yuzde_fark = (fark / baseline_import * 100) if baseline_import > 0 else 0
                    
                    print(f"  Import Hızı: {mevcut_import:.2f} ms (Baseline: {baseline_import:.2f} ms, Fark: {fark:+.2f} ms, %{yuzde_fark:+.1f})")
            
        except Exception as e:
            print(f"❌ Baseline karşılaştırma hatası: {e}")
    
    def baseline_kaydet(self):
        """Mevcut sonuçları baseline olarak kaydet"""
        try:
            with open(self.baseline_dosyasi, 'w', encoding='utf-8') as f:
                json.dump(self.sonuclar, f, indent=2, ensure_ascii=False)
            print(f"✅ Baseline kaydedildi: {self.baseline_dosyasi}")
        except Exception as e:
            print(f"❌ Baseline kaydetme hatası: {e}")
    
    def rapor_olustur(self):
        """Performans raporu oluştur"""
        rapor_dosyasi = f"performans_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(rapor_dosyasi, 'w', encoding='utf-8') as f:
                json.dump(self.sonuclar, f, indent=2, ensure_ascii=False)
            
            print(f"\n📋 Performans raporu oluşturuldu: {rapor_dosyasi}")
            
            # Özet yazdır
            self.ozet_yazdir()
            
        except Exception as e:
            print(f"❌ Rapor oluşturma hatası: {e}")
    
    def ozet_yazdir(self):
        """Test sonuçlarının özetini yazdır"""
        print("\n" + "="*60)
        print("📊 PERFORMANS TEST ÖZETİ")
        print("="*60)
        
        basarili_testler = 0
        toplam_testler = 0
        
        for test_adi, sonuc in self.sonuclar['testler'].items():
            toplam_testler += 1
            durum = sonuc.get('durum', 'BİLİNMEYEN')
            
            if durum == 'BASARILI':
                basarili_testler += 1
                print(f"✅ {test_adi.replace('_', ' ').title()}: {durum}")
            elif durum == 'UYARI':
                print(f"⚠️ {test_adi.replace('_', ' ').title()}: {durum}")
            else:
                print(f"❌ {test_adi.replace('_', ' ').title()}: {durum}")
        
        basari_orani = (basarili_testler / toplam_testler * 100) if toplam_testler > 0 else 0
        
        print(f"\n📈 Genel Başarı Oranı: %{basari_orani:.1f} ({basarili_testler}/{toplam_testler})")
        
        if basari_orani >= 80:
            print("🎉 Performans hedefleri büyük ölçüde karşılandı!")
        elif basari_orani >= 60:
            print("⚠️ Performans kabul edilebilir seviyede, iyileştirmeler yapılabilir")
        else:
            print("❌ Performans hedefleri karşılanmadı, optimizasyon gerekli")
    
    def tum_testleri_calistir(self):
        """Tüm performans testlerini çalıştır"""
        print("🚀 Performans doğrulama testleri başlatılıyor...\n")
        
        # Testleri çalıştır
        self.bellek_kullanimi_test()
        self.import_hizi_test()
        self.dosya_boyutu_analizi()
        self.cpu_kullanimi_test()
        
        # Baseline ile karşılaştır
        self.baseline_karsilastir()
        
        # Rapor oluştur
        self.rapor_olustur()


def main():
    """Ana fonksiyon"""
    dogrulayici = PerformansDogrulayici()
    dogrulayici.tum_testleri_calistir()


if __name__ == "__main__":
    main()