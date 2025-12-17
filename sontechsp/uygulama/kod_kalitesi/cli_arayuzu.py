# Version: 0.1.0
# Last Update: 2024-12-17
# Module: kod_kalitesi.cli_arayuzu
# Description: Kod kalitesi refactoring işlemleri için komut satırı arayüzü
# Changelog:
# - İlk sürüm: CLI arayüzü ve interaktif refactoring süreci

import os
import sys
import time
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import argparse
from dataclasses import dataclass

from .refactoring_orkestratori import RefactoringOrkestratori
from .guvenlik_sistemi import GuvenlikSistemi
from .konfigürasyon import KonfigürasyonYoneticisi


@dataclass
class CLIKonfigurasyonu:
    """CLI konfigürasyon ayarları"""
    proje_yolu: str
    otomatik_onay: bool = False
    verbose: bool = False
    sadece_analiz: bool = False
    backup_klasoru: Optional[str] = None
    max_dosya_boyutu: int = 120
    max_fonksiyon_boyutu: int = 25


class IlerlemeMetre:
    """İlerleme göstergesi sınıfı"""
    
    def __init__(self, toplam_adim: int, genislik: int = 50):
        self.toplam_adim = toplam_adim
        self.mevcut_adim = 0
        self.genislik = genislik
        self.baslangic_zamani = time.time()
    
    def guncelle(self, adim: int, mesaj: str = ""):
        """İlerleme çubuğunu güncelle"""
        self.mevcut_adim = adim
        yuzde = (adim / self.toplam_adim) * 100
        dolu_uzunluk = int(self.genislik * adim // self.toplam_adim)
        
        bar = '█' * dolu_uzunluk + '-' * (self.genislik - dolu_uzunluk)
        gecen_sure = time.time() - self.baslangic_zamani
        
        print(f'\r|{bar}| {yuzde:.1f}% ({adim}/{self.toplam_adim}) - {mesaj} [{gecen_sure:.1f}s]', 
              end='', flush=True)
        
        if adim == self.toplam_adim:
            print()  # Yeni satıra geç


class KodKalitesiCLI:
    """Kod kalitesi refactoring işlemleri için komut satırı arayüzü"""
    
    def __init__(self, konfigürasyon: CLIKonfigurasyonu):
        self.config = konfigürasyon
        self.config_yoneticisi = KonfigürasyonYoneticisi(self.config.proje_yolu)
        self.orkestrator = RefactoringOrkestratori(self.config.proje_yolu)
        self.guvenlik = GuvenlikSistemi()
        self.ilerleme = None
    
    def calistir(self) -> int:
        """Ana CLI çalıştırma fonksiyonu"""
        try:
            self._baslik_yazdir()
            
            if not self._proje_dogrula():
                return 1
            
            if self.config.sadece_analiz:
                return self._sadece_analiz_yap()
            
            return self._interaktif_refactoring()
            
        except KeyboardInterrupt:
            print("\n\n❌ İşlem kullanıcı tarafından iptal edildi.")
            return 130
        except Exception as e:
            print(f"\n❌ Beklenmeyen hata: {e}")
            if self.config.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    def _baslik_yazdir(self):
        """CLI başlık bilgilerini yazdır"""
        print("=" * 70)
        print("🔧 SONTECHSP Kod Kalitesi ve Standardizasyon Aracı")
        print("=" * 70)
        print(f"📁 Proje Yolu: {self.config.proje_yolu}")
        print(f"📏 Dosya Limit: {self.config.max_dosya_boyutu} satır")
        print(f"🔧 Fonksiyon Limit: {self.config.max_fonksiyon_boyutu} satır")
        print("-" * 70)
    
    def _proje_dogrula(self) -> bool:
        """Proje yapısını doğrula"""
        proje_yolu = Path(self.config.proje_yolu)
        
        if not proje_yolu.exists():
            print(f"❌ Proje yolu bulunamadı: {self.config.proje_yolu}")
            return False
        
        if not proje_yolu.is_dir():
            print(f"❌ Belirtilen yol bir klasör değil: {self.config.proje_yolu}")
            return False
        
        # Python dosyalarının varlığını kontrol et
        python_dosyalari = list(proje_yolu.rglob("*.py"))
        if not python_dosyalari:
            print(f"❌ Proje klasöründe Python dosyası bulunamadı")
            return False
        
        print(f"✅ Proje doğrulandı: {len(python_dosyalari)} Python dosyası bulundu")
        return True
    
    def _sadece_analiz_yap(self) -> int:
        """Sadece analiz modunda çalış"""
        print("\n🔍 Analiz Modu - Sadece sorunlar tespit edilecek\n")
        
        try:
            analiz_sonucu = self.orkestrator.kod_tabanini_analiz_et(self.config.proje_yolu)
            self._analiz_sonuclarini_goster(analiz_sonucu)
            return 0
        except Exception as e:
            print(f"❌ Analiz sırasında hata: {e}")
            return 1
    
    def _interaktif_refactoring(self) -> int:
        """İnteraktif refactoring süreci"""
        print("\n🚀 İnteraktif Refactoring Modu\n")
        
        # 1. Analiz yap
        print("1️⃣ Kod tabanı analiz ediliyor...")
        analiz_sonucu = self.orkestrator.kod_tabanini_analiz_et(self.config.proje_yolu)
        
        if not analiz_sonucu or not self._analiz_sonuclarini_goster(analiz_sonucu):
            print("✅ Kod tabanında sorun bulunamadı!")
            return 0
        
        # 2. Kullanıcı onayı al
        if not self._kullanici_onayini_al():
            print("❌ İşlem iptal edildi.")
            return 0
        
        # 3. Backup oluştur
        print("\n2️⃣ Güvenlik backup'ı oluşturuluyor...")
        backup_yolu = self.guvenlik.backup_olustur(self.config.proje_yolu)
        print(f"✅ Backup oluşturuldu: {backup_yolu}")
        
        # 4. Refactoring işlemlerini yap
        print("\n3️⃣ Refactoring işlemleri başlatılıyor...")
        return self._refactoring_islemlerini_yap(analiz_sonucu, backup_yolu)
    
    def _analiz_sonuclarini_goster(self, analiz_sonucu: Dict) -> bool:
        """Analiz sonuçlarını göster ve sorun var mı döndür"""
        sorun_var = False
        
        # Dosya boyut sorunları
        if analiz_sonucu.get('buyuk_dosyalar'):
            sorun_var = True
            print(f"\n📄 Büyük Dosyalar ({len(analiz_sonucu['buyuk_dosyalar'])} adet):")
            for dosya in analiz_sonucu['buyuk_dosyalar'][:5]:  # İlk 5'ini göster
                print(f"  • {dosya['dosya_yolu']} ({dosya['satir_sayisi']} satır)")
            if len(analiz_sonucu['buyuk_dosyalar']) > 5:
                print(f"  ... ve {len(analiz_sonucu['buyuk_dosyalar']) - 5} dosya daha")
        
        # Fonksiyon boyut sorunları
        if analiz_sonucu.get('buyuk_fonksiyonlar'):
            sorun_var = True
            print(f"\n🔧 Büyük Fonksiyonlar ({len(analiz_sonucu['buyuk_fonksiyonlar'])} adet):")
            for fonk in analiz_sonucu['buyuk_fonksiyonlar'][:5]:
                print(f"  • {fonk['dosya_yolu']}::{fonk['fonksiyon_adi']} ({fonk['satir_sayisi']} satır)")
            if len(analiz_sonucu['buyuk_fonksiyonlar']) > 5:
                print(f"  ... ve {len(analiz_sonucu['buyuk_fonksiyonlar']) - 5} fonksiyon daha")
        
        # Mimari ihlaller
        if analiz_sonucu.get('mimari_ihlaller'):
            sorun_var = True
            print(f"\n🏗️ Mimari İhlaller ({len(analiz_sonucu['mimari_ihlaller'])} adet):")
            for ihlal in analiz_sonucu['mimari_ihlaller'][:3]:
                print(f"  • {ihlal['kaynak_dosya']} -> {ihlal['hedef_dosya']}")
            if len(analiz_sonucu['mimari_ihlaller']) > 3:
                print(f"  ... ve {len(analiz_sonucu['mimari_ihlaller']) - 3} ihlal daha")
        
        # Kod tekrarları
        if analiz_sonucu.get('kod_tekrarlari'):
            sorun_var = True
            print(f"\n🔄 Kod Tekrarları ({len(analiz_sonucu['kod_tekrarlari'])} grup):")
            for tekrar in analiz_sonucu['kod_tekrarlari'][:3]:
                print(f"  • {len(tekrar['dosyalar'])} dosyada benzer kod")
        
        return sorun_var
    
    def _kullanici_onayini_al(self) -> bool:
        """Kullanıcıdan refactoring onayı al"""
        if self.config.otomatik_onay:
            return True
        
        print("\n" + "=" * 50)
        print("⚠️  UYARI: Refactoring işlemi kod dosyalarınızı değiştirecek!")
        print("📋 Yapılacak işlemler:")
        print("   • Büyük dosyalar bölünecek")
        print("   • Büyük fonksiyonlar parçalanacak") 
        print("   • Import yapıları düzenlenecek")
        print("   • Kod tekrarları ortak modüllere taşınacak")
        print("   • Dosya başlıkları standardize edilecek")
        print("\n💾 Backup otomatik oluşturulacak ve işlem geri alınabilir.")
        print("=" * 50)
        
        while True:
            cevap = input("\n🤔 Devam etmek istiyor musunuz? (e/h): ").lower().strip()
            if cevap in ['e', 'evet', 'y', 'yes']:
                return True
            elif cevap in ['h', 'hayır', 'n', 'no']:
                return False
            else:
                print("❌ Lütfen 'e' (evet) veya 'h' (hayır) giriniz.")
    
    def _refactoring_islemlerini_yap(self, analiz_sonucu: Dict, backup_yolu: str) -> int:
        """Refactoring işlemlerini gerçekleştir"""
        toplam_adim = 6
        self.ilerleme = IlerlemeMetre(toplam_adim)
        
        try:
            # Adım 1: Dosya bölme
            self.ilerleme.guncelle(1, "Büyük dosyalar bölünüyor...")
            if analiz_sonucu.get('buyuk_dosyalar'):
                self.orkestrator.buyuk_dosyalari_bol(analiz_sonucu['buyuk_dosyalar'])
            
            # Adım 2: Fonksiyon bölme
            self.ilerleme.guncelle(2, "Büyük fonksiyonlar bölünüyor...")
            if analiz_sonucu.get('buyuk_fonksiyonlar'):
                self.orkestrator.buyuk_fonksiyonlari_bol(analiz_sonucu['buyuk_fonksiyonlar'])
            
            # Adım 3: Import düzenleme
            self.ilerleme.guncelle(3, "Import yapıları düzenleniyor...")
            if analiz_sonucu.get('mimari_ihlaller'):
                self.orkestrator.import_yapilarini_duzenle(analiz_sonucu['mimari_ihlaller'])
            
            # Adım 4: Kod tekrarları
            self.ilerleme.guncelle(4, "Kod tekrarları düzenleniyor...")
            if analiz_sonucu.get('kod_tekrarlari'):
                self.orkestrator.kod_tekrarlarini_duzenle(analiz_sonucu['kod_tekrarlari'])
            
            # Adım 5: Başlık standardizasyonu
            self.ilerleme.guncelle(5, "Dosya başlıkları standardize ediliyor...")
            self.orkestrator.basliklari_standardize_et(self.config.proje_yolu)
            
            # Adım 6: Test doğrulama
            self.ilerleme.guncelle(6, "Testler çalıştırılıyor...")
            test_sonucu = self.orkestrator.testleri_calistir()
            
            print(f"\n\n✅ Refactoring işlemi başarıyla tamamlandı!")
            print(f"📊 Test Sonucu: {test_sonucu['basarili']}/{test_sonucu['toplam']} test başarılı")
            print(f"💾 Backup Yolu: {backup_yolu}")
            
            return 0
            
        except Exception as e:
            print(f"\n\n❌ Refactoring sırasında hata: {e}")
            print(f"🔄 Geri alma işlemi başlatılıyor...")
            
            try:
                self.guvenlik.geri_al(backup_yolu, self.config.proje_yolu)
                print("✅ Değişiklikler geri alındı.")
            except Exception as geri_alma_hatasi:
                print(f"❌ Geri alma hatası: {geri_alma_hatasi}")
                print(f"💾 Manuel geri alma için backup: {backup_yolu}")
            
            return 1


def ana_cli():
    """CLI entry point fonksiyonu"""
    parser = argparse.ArgumentParser(
        description="SONTECHSP Kod Kalitesi ve Standardizasyon Aracı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python kod-kalitesi-cli.py /path/to/project          # İnteraktif mod
  python kod-kalitesi-cli.py /path/to/project --analiz # Sadece analiz
  python kod-kalitesi-cli.py /path/to/project --otomatik # Otomatik onay
        """
    )
    
    parser.add_argument('proje_yolu', help='Analiz edilecek proje klasörü')
    parser.add_argument('--analiz', action='store_true', 
                       help='Sadece analiz yap, değişiklik yapma')
    parser.add_argument('--otomatik', action='store_true',
                       help='Kullanıcı onayı almadan otomatik çalış')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Detaylı çıktı göster')
    parser.add_argument('--backup', type=str,
                       help='Backup klasörü (varsayılan: otomatik)')
    parser.add_argument('--max-dosya', type=int, default=120,
                       help='Maksimum dosya boyutu (varsayılan: 120)')
    parser.add_argument('--max-fonksiyon', type=int, default=25,
                       help='Maksimum fonksiyon boyutu (varsayılan: 25)')
    
    args = parser.parse_args()
    
    # Konfigürasyon oluştur
    config = CLIKonfigurasyonu(
        proje_yolu=args.proje_yolu,
        otomatik_onay=args.otomatik,
        verbose=args.verbose,
        sadece_analiz=args.analiz,
        backup_klasoru=args.backup,
        max_dosya_boyutu=args.max_dosya,
        max_fonksiyon_boyutu=args.max_fonksiyon
    )
    
    # CLI çalıştır
    cli = KodKalitesiCLI(config)
    return cli.calistir()


if __name__ == "__main__":
    sys.exit(ana_cli())