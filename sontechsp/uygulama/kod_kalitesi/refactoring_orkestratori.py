# Version: 0.1.0
# Last Update: 2025-12-17
# Module: kod_kalitesi.refactoring_orkestratori
# Description: Tüm refactoring işlemlerini koordine eden ana sistem
# Changelog:
# - İlk versiyon: RefactoringOrkestratori sınıfı oluşturuldu

"""
Refactoring Orkestratörü

Tüm kod kalitesi refactoring işlemlerini koordine eder.
Güvenli refactoring süreci ve geri alma mekanizmaları sağlar.
"""

import json
import logging
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set

# Analizör import'ları
from uygulama.moduller.kod_kalitesi.analizorler.dosya_boyut_analizoru import (
    DosyaBoyutAnalizoru, DosyaRaporu
)
from uygulama.moduller.kod_kalitesi.analizorler.fonksiyon_boyut_analizoru import (
    FonksiyonBoyutAnalizoru, FonksiyonRaporu
)
from uygulama.moduller.kod_kalitesi.analizorler.import_yapisi_analizoru import (
    ImportYapisiAnalizoru
)
from uygulama.moduller.kod_kalitesi.analizorler.kod_tekrari_analizoru import (
    KodTekrariAnalizoru
)
from uygulama.moduller.kod_kalitesi.analizorler.baslik_analizoru import (
    BaslikAnalizoru
)

# Refactoring araçları import'ları
from uygulama.moduller.kod_kalitesi.refactoring.dosya_bolucu import (
    DosyaBolucu, BolmeStratejisi
)
from uygulama.moduller.kod_kalitesi.refactoring.fonksiyon_bolucu import (
    FonksiyonBolucu
)
from uygulama.moduller.kod_kalitesi.refactoring.import_duzenleyici import (
    ImportDuzenleyici
)

# Güvenlik sistemi import'u
from .guvenlik_sistemi import GuvenlikSistemi, IslemTuru


class RefactoringAsamasi(Enum):
    """Refactoring aşamaları"""
    ANALIZ = "analiz"
    PLANLAMA = "planlama"
    BACKUP = "backup"
    UYGULAMA = "uygulama"
    DOGRULAMA = "dogrulama"
    TAMAMLANDI = "tamamlandi"
    HATA = "hata"


class RefactoringSonucu(Enum):
    """Refactoring sonuçları"""
    BASARILI = "basarili"
    BASARISIZ = "basarisiz"
    KISMI_BASARILI = "kismi_basarili"
    IPTAL_EDILDI = "iptal_edildi"


@dataclass
class RefactoringAdimi:
    """Refactoring adımı bilgisi"""
    adim_id: str
    aciklama: str
    hedef_dosyalar: List[str]
    durum: str = "bekliyor"
    hata_mesaji: Optional[str] = None
    baslangic_zamani: Optional[datetime] = None
    bitis_zamani: Optional[datetime] = None


@dataclass
class RefactoringPlani:
    """Refactoring planı"""
    plan_id: str
    proje_yolu: str
    hedef_klasorler: List[str]
    adimlar: List[RefactoringAdimi] = field(default_factory=list)
    toplam_dosya_sayisi: int = 0
    sorunlu_dosya_sayisi: int = 0
    tahmini_sure: int = 0  # dakika cinsinden


@dataclass
class RefactoringRaporu:
    """Refactoring raporu"""
    plan_id: str
    baslangic_zamani: datetime
    bitis_zamani: Optional[datetime] = None
    durum: RefactoringSonucu = RefactoringSonucu.BASARISIZ
    islenen_dosya_sayisi: int = 0
    basarili_adim_sayisi: int = 0
    basarisiz_adim_sayisi: int = 0
    hata_mesajlari: List[str] = field(default_factory=list)
    backup_yolu: Optional[str] = None


class RefactoringOrkestratori:
    """
    Refactoring Orkestratörü
    
    Tüm kod kalitesi refactoring işlemlerini koordine eder.
    Adım adım güvenli refactoring süreci yönetir ve
    hata durumunda geri alma mekanizması sağlar.
    """
    
    def __init__(
        self,
        proje_yolu: str,
        backup_klasoru: str = None,
        log_seviyesi: int = logging.INFO
    ):
        """
        Args:
            proje_yolu: Refactoring yapılacak proje yolu
            backup_klasoru: Backup dosyalarının saklanacağı klasör
            log_seviyesi: Log seviyesi
        """
        self.proje_yolu = Path(proje_yolu)
        self.backup_klasoru = Path(backup_klasoru or self.proje_yolu / ".refactoring_backup")
        self.log_seviyesi = log_seviyesi
        
        # Logger kurulumu
        self.logger = self._logger_kurulumu(log_seviyesi)
        
        # Analizör ve araçları başlat
        self._aracları_baslat()
        
        # Durum takibi
        self.mevcut_plan: Optional[RefactoringPlani] = None
        self.mevcut_rapor: Optional[RefactoringRaporu] = None
        self.mevcut_asama = RefactoringAsamasi.ANALIZ
        
        self.logger.info(f"RefactoringOrkestratori başlatıldı: {self.proje_yolu}")
    
    def _logger_kurulumu(self, log_seviyesi: int) -> logging.Logger:
        """Logger kurulumu yapar"""
        logger = logging.getLogger(f"RefactoringOrkestratori_{id(self)}")
        logger.setLevel(log_seviyesi)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _aracları_baslat(self):
        """Analizör ve refactoring araçlarını başlatır"""
        # Analizörler
        self.dosya_analizoru = DosyaBoyutAnalizoru()
        self.fonksiyon_analizoru = FonksiyonBoyutAnalizoru()
        self.import_analizoru = ImportYapisiAnalizoru()
        self.kod_tekrari_analizoru = KodTekrariAnalizoru()
        self.baslik_analizoru = BaslikAnalizoru()
        
        # Refactoring araçları
        self.dosya_bolucu = DosyaBolucu()
        self.fonksiyon_bolucu = FonksiyonBolucu()
        self.import_duzenleyici = ImportDuzenleyici()
        
        # Güvenlik sistemi
        self.guvenlik_sistemi = GuvenlikSistemi(
            proje_yolu=str(self.proje_yolu),
            guvenlik_klasoru=str(self.backup_klasoru.parent / "guvenlik"),
            log_seviyesi=self.log_seviyesi
        )
    
    def tam_refactoring_yap(
        self,
        hedef_klasorler: List[str] = None,
        kullanici_onayı_gerekli: bool = True
    ) -> RefactoringRaporu:
        """
        Tam refactoring süreci yürütür.
        
        Args:
            hedef_klasorler: Refactoring yapılacak klasörler (None ise tüm proje)
            kullanici_onayı_gerekli: Her adım için kullanıcı onayı istenir
            
        Returns:
            Refactoring raporu
        """
        try:
            self.logger.info("Tam refactoring süreci başlatılıyor...")
            
            # 1. Analiz aşaması
            self._asama_guncelle(RefactoringAsamasi.ANALIZ)
            plan = self.kod_tabanini_analiz_et(hedef_klasorler)
            
            if not plan.adimlar:
                self.logger.info("Refactoring gerektiren sorun bulunamadı.")
                return self._rapor_olustur(RefactoringSonucu.BASARILI)
            
            # 2. Planlama aşaması
            self._asama_guncelle(RefactoringAsamasi.PLANLAMA)
            if kullanici_onayı_gerekli:
                onay = self._kullanici_onayı_al(plan)
                if not onay:
                    return self._rapor_olustur(RefactoringSonucu.IPTAL_EDILDI)
            
            # 3. Backup aşaması
            self._asama_guncelle(RefactoringAsamasi.BACKUP)
            backup_yolu = self._backup_olustur()
            
            # 4. Uygulama aşaması
            self._asama_guncelle(RefactoringAsamasi.UYGULAMA)
            basarili_adimlar = self._plani_uygula(plan)
            
            # 5. Doğrulama aşaması
            self._asama_guncelle(RefactoringAsamasi.DOGRULAMA)
            dogrulama_sonucu = self._degisiklikleri_dogrula()
            
            # Sonuç belirleme
            if dogrulama_sonucu and basarili_adimlar == len(plan.adimlar):
                sonuc = RefactoringSonucu.BASARILI
                self._asama_guncelle(RefactoringAsamasi.TAMAMLANDI)
            elif basarili_adimlar > 0:
                sonuc = RefactoringSonucu.KISMI_BASARILI
            else:
                sonuc = RefactoringSonucu.BASARISIZ
                self._geri_al(backup_yolu)
            
            return self._rapor_olustur(sonuc)
            
        except Exception as e:
            self.logger.error(f"Refactoring sırasında hata: {e}")
            self._asama_guncelle(RefactoringAsamasi.HATA)
            
            # Hata durumunda geri al
            if hasattr(self, '_son_backup_yolu'):
                self._geri_al(self._son_backup_yolu)
            
            return self._rapor_olustur(RefactoringSonucu.BASARISIZ, str(e))
    
    def kod_tabanini_analiz_et(
        self,
        hedef_klasorler: List[str] = None
    ) -> RefactoringPlani:
        """
        Kod tabanını analiz eder ve refactoring planı oluşturur.
        
        Args:
            hedef_klasorler: Analiz edilecek klasörler
            
        Returns:
            Refactoring planı
        """
        self.logger.info("Kod tabanı analizi başlatılıyor...")
        
        if hedef_klasorler is None:
            hedef_klasorler = [str(self.proje_yolu)]
        
        plan = RefactoringPlani(
            plan_id=f"refactoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            proje_yolu=str(self.proje_yolu),
            hedef_klasorler=hedef_klasorler
        )
        
        # Dosya boyut analizi
        self._dosya_boyut_analizi_ekle(plan, hedef_klasorler)
        
        # Fonksiyon boyut analizi
        self._fonksiyon_boyut_analizi_ekle(plan, hedef_klasorler)
        
        # Import yapısı analizi
        self._import_yapisi_analizi_ekle(plan, hedef_klasorler)
        
        # Kod tekrarı analizi
        self._kod_tekrari_analizi_ekle(plan, hedef_klasorler)
        
        # Başlık standardizasyon analizi
        self._baslik_analizi_ekle(plan, hedef_klasorler)
        
        self.mevcut_plan = plan
        self.logger.info(f"Analiz tamamlandı. {len(plan.adimlar)} adım planlandı.")
        
        return plan
    
    def _dosya_boyut_analizi_ekle(
        self,
        plan: RefactoringPlani,
        hedef_klasorler: List[str]
    ):
        """Dosya boyut analizi adımlarını plana ekler"""
        for klasor in hedef_klasorler:
            buyuk_dosyalar = self.dosya_analizoru.buyuk_dosyalari_tespit_et(klasor)
            
            for dosya_raporu in buyuk_dosyalar:
                adim = RefactoringAdimi(
                    adim_id=f"dosya_bol_{len(plan.adimlar)}",
                    aciklama=f"Dosya bölme: {dosya_raporu.dosya_yolu} "
                             f"({dosya_raporu.satir_sayisi} satır)",
                    hedef_dosyalar=[dosya_raporu.dosya_yolu]
                )
                plan.adimlar.append(adim)
                plan.sorunlu_dosya_sayisi += 1
    
    def _fonksiyon_boyut_analizi_ekle(
        self,
        plan: RefactoringPlani,
        hedef_klasorler: List[str]
    ):
        """Fonksiyon boyut analizi adımlarını plana ekler"""
        for klasor in hedef_klasorler:
            klasor_yolu = Path(klasor)
            for py_dosya in klasor_yolu.rglob('*.py'):
                buyuk_fonksiyonlar = self.fonksiyon_analizoru.buyuk_fonksiyonlari_tespit_et(
                    str(py_dosya)
                )
                
                for fonk_raporu in buyuk_fonksiyonlar:
                    adim = RefactoringAdimi(
                        adim_id=f"fonksiyon_bol_{len(plan.adimlar)}",
                        aciklama=f"Fonksiyon bölme: {fonk_raporu.fonksiyon_adi} "
                                 f"({fonk_raporu.satir_sayisi} satır)",
                        hedef_dosyalar=[fonk_raporu.dosya_yolu]
                    )
                    plan.adimlar.append(adim)
    
    def _import_yapisi_analizi_ekle(
        self,
        plan: RefactoringPlani,
        hedef_klasorler: List[str]
    ):
        """Import yapısı analizi adımlarını plana ekler"""
        for klasor in hedef_klasorler:
            ihlaller = self.import_analizoru.mimari_ihlalleri_tespit_et(klasor)
            
            for ihlal in ihlaller:
                adim = RefactoringAdimi(
                    adim_id=f"import_duzelt_{len(plan.adimlar)}",
                    aciklama=f"Import düzeltme: {ihlal.kaynak_dosya} -> {ihlal.hedef_dosya}",
                    hedef_dosyalar=[ihlal.kaynak_dosya]
                )
                plan.adimlar.append(adim)
    
    def _kod_tekrari_analizi_ekle(
        self,
        plan: RefactoringPlani,
        hedef_klasorler: List[str]
    ):
        """Kod tekrarı analizi adımlarını plana ekler"""
        for klasor in hedef_klasorler:
            tekrarlar = self.kod_tekrari_analizoru.kod_tekrarlarini_tara(klasor)
            
            for tekrar in tekrarlar:
                hedef_dosyalar = [tekrar.blok1.dosya_yolu, tekrar.blok2.dosya_yolu]
                adim = RefactoringAdimi(
                    adim_id=f"kod_tekrar_cikart_{len(plan.adimlar)}",
                    aciklama=f"Kod tekrarı çıkarma: {tekrar.blok1.fonksiyon_adi} ve "
                             f"{tekrar.blok2.fonksiyon_adi} ({tekrar.benzerlik_orani:.1%} benzerlik)",
                    hedef_dosyalar=hedef_dosyalar
                )
                plan.adimlar.append(adim)
    
    def _baslik_analizi_ekle(
        self,
        plan: RefactoringPlani,
        hedef_klasorler: List[str]
    ):
        """Başlık standardizasyon analizi adımlarını plana ekler"""
        for klasor in hedef_klasorler:
            baslik_raporlari = self.baslik_analizoru.klasor_basliklarini_analiz_et(klasor)
            
            for rapor in baslik_raporlari:
                if not rapor.baslik_var or not rapor.standart_uyumlu:
                    adim = RefactoringAdimi(
                        adim_id=f"baslik_ekle_{len(plan.adimlar)}",
                        aciklama=f"Başlık ekleme/güncelleme: {rapor.dosya_yolu}",
                        hedef_dosyalar=[rapor.dosya_yolu]
                    )
                    plan.adimlar.append(adim)
    
    def _kullanici_onayı_al(self, plan: RefactoringPlani) -> bool:
        """
        Kullanıcıdan refactoring planı için onay alır.
        
        Args:
            plan: Refactoring planı
            
        Returns:
            Kullanıcı onayı (True/False)
        """
        print("\n" + "="*60)
        print("REFACTORING PLANI")
        print("="*60)
        print(f"Proje: {plan.proje_yolu}")
        print(f"Toplam adım sayısı: {len(plan.adimlar)}")
        print(f"Sorunlu dosya sayısı: {plan.sorunlu_dosya_sayisi}")
        print("\nPlanlanmış adımlar:")
        
        for i, adim in enumerate(plan.adimlar, 1):
            print(f"{i:2d}. {adim.aciklama}")
        
        print("\n" + "="*60)
        
        while True:
            cevap = input("Bu refactoring planını onaylıyor musunuz? (e/h): ").lower().strip()
            if cevap in ['e', 'evet', 'yes', 'y']:
                return True
            elif cevap in ['h', 'hayır', 'no', 'n']:
                return False
            else:
                print("Lütfen 'e' (evet) veya 'h' (hayır) giriniz.")
    
    def _backup_olustur(self) -> str:
        """
        Proje backup'ı oluşturur.
        
        Returns:
            Backup klasör yolu
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_yolu = self.backup_klasoru / f"backup_{timestamp}"
        
        self.logger.info(f"Backup oluşturuluyor: {backup_yolu}")
        
        # Backup klasörünü oluştur
        backup_yolu.mkdir(parents=True, exist_ok=True)
        
        # Proje dosyalarını kopyala
        shutil.copytree(
            self.proje_yolu,
            backup_yolu / "proje",
            ignore=shutil.ignore_patterns(
                '__pycache__', '*.pyc', '.git', '.pytest_cache',
                'venv', 'env', '.hypothesis'
            )
        )
        
        # Backup bilgilerini kaydet
        backup_bilgi = {
            'timestamp': timestamp,
            'proje_yolu': str(self.proje_yolu),
            'plan_id': self.mevcut_plan.plan_id if self.mevcut_plan else None
        }
        
        with open(backup_yolu / "backup_info.json", 'w', encoding='utf-8') as f:
            json.dump(backup_bilgi, f, indent=2, ensure_ascii=False)
        
        self._son_backup_yolu = str(backup_yolu)
        self.logger.info(f"Backup oluşturuldu: {backup_yolu}")
        
        return str(backup_yolu)
    
    def _plani_uygula(self, plan: RefactoringPlani) -> int:
        """
        Refactoring planını uygular.
        
        Args:
            plan: Refactoring planı
            
        Returns:
            Başarılı adım sayısı
        """
        basarili_adimlar = 0
        
        for adim in plan.adimlar:
            try:
                self.logger.info(f"Adım uygulanıyor: {adim.aciklama}")
                adim.baslangic_zamani = datetime.now()
                adim.durum = "uygulanıyor"
                
                # Adım türüne göre uygun aracı çağır
                if adim.adim_id.startswith('dosya_bol_'):
                    self._dosya_bolme_adimi_uygula(adim)
                elif adim.adim_id.startswith('fonksiyon_bol_'):
                    self._fonksiyon_bolme_adimi_uygula(adim)
                elif adim.adim_id.startswith('import_duzelt_'):
                    self._import_duzeltme_adimi_uygula(adim)
                elif adim.adim_id.startswith('kod_tekrar_cikart_'):
                    self._kod_tekrar_cikarma_adimi_uygula(adim)
                elif adim.adim_id.startswith('baslik_ekle_'):
                    self._baslik_ekleme_adimi_uygula(adim)
                
                adim.durum = "tamamlandı"
                adim.bitis_zamani = datetime.now()
                basarili_adimlar += 1
                
                self.logger.info(f"Adım tamamlandı: {adim.aciklama}")
                
            except Exception as e:
                adim.durum = "hata"
                adim.hata_mesaji = str(e)
                adim.bitis_zamani = datetime.now()
                
                self.logger.error(f"Adım hatası: {adim.aciklama} - {e}")
        
        return basarili_adimlar
    
    def _dosya_bolme_adimi_uygula(self, adim: RefactoringAdimi):
        """Dosya bölme adımını uygular"""
        dosya_yolu = adim.hedef_dosyalar[0]
        yeni_dosyalar = self.dosya_bolucu.dosyayi_bol(dosya_yolu)
        
        # Yeni dosyaları diske yaz
        for yeni_dosya in yeni_dosyalar:
            with open(yeni_dosya.dosya_yolu, 'w', encoding='utf-8') as f:
                f.write(yeni_dosya.icerik)
        
        # __init__.py'yi güncelle
        modul_yolu = str(Path(dosya_yolu).parent)
        self.dosya_bolucu.init_dosyasini_guncelle(modul_yolu, yeni_dosyalar)
        
        # Orijinal dosyayı sil
        os.remove(dosya_yolu)
    
    def _fonksiyon_bolme_adimi_uygula(self, adim: RefactoringAdimi):
        """Fonksiyon bölme adımını uygular"""
        dosya_yolu = adim.hedef_dosyalar[0]
        
        # Dosyayı oku
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            icerik = f.read()
        
        # Büyük fonksiyonları böl
        yeni_icerik = self.fonksiyon_bolucu.buyuk_fonksiyonlari_bol(icerik)
        
        # Dosyayı güncelle
        with open(dosya_yolu, 'w', encoding='utf-8') as f:
            f.write(yeni_icerik)
    
    def _import_duzeltme_adimi_uygula(self, adim: RefactoringAdimi):
        """Import düzeltme adımını uygular"""
        dosya_yolu = adim.hedef_dosyalar[0]
        self.import_duzenleyici.dosya_importlarini_duzenle(dosya_yolu)
    
    def _kod_tekrar_cikarma_adimi_uygula(self, adim: RefactoringAdimi):
        """Kod tekrarı çıkarma adımını uygular"""
        # Bu adım daha karmaşık olduğu için şimdilik placeholder
        self.logger.warning(f"Kod tekrarı çıkarma henüz uygulanmadı: {adim.aciklama}")
    
    def _baslik_ekleme_adimi_uygula(self, adim: RefactoringAdimi):
        """Başlık ekleme adımını uygular"""
        dosya_yolu = adim.hedef_dosyalar[0]
        # Dosya yolundan modül adını çıkar
        from pathlib import Path
        dosya_adi = Path(dosya_yolu).stem
        self.baslik_analizoru.baslik_ekle(dosya_yolu, dosya_adi, "Otomatik oluşturuldu")
    
    def _degisiklikleri_dogrula(self) -> bool:
        """
        Yapılan değişiklikleri doğrular.
        
        Returns:
            Doğrulama sonucu
        """
        try:
            self.logger.info("Değişiklikler doğrulanıyor...")
            
            # Syntax kontrolü
            for py_dosya in self.proje_yolu.rglob('*.py'):
                try:
                    with open(py_dosya, 'r', encoding='utf-8') as f:
                        compile(f.read(), str(py_dosya), 'exec')
                except SyntaxError as e:
                    self.logger.error(f"Syntax hatası: {py_dosya} - {e}")
                    return False
            
            # Import kontrolü
            # Bu kısım daha detaylı olabilir, şimdilik temel kontrol
            
            self.logger.info("Doğrulama başarılı")
            return True
            
        except Exception as e:
            self.logger.error(f"Doğrulama hatası: {e}")
            return False
    
    def _geri_al(self, backup_yolu: str):
        """
        Backup'tan geri alma yapar.
        
        Args:
            backup_yolu: Backup klasör yolu
        """
        try:
            self.logger.info(f"Geri alma işlemi başlatılıyor: {backup_yolu}")
            
            backup_proje_yolu = Path(backup_yolu) / "proje"
            
            if backup_proje_yolu.exists():
                # Mevcut projeyi sil
                shutil.rmtree(self.proje_yolu)
                
                # Backup'tan geri yükle
                shutil.copytree(backup_proje_yolu, self.proje_yolu)
                
                self.logger.info("Geri alma işlemi tamamlandı")
            else:
                self.logger.error(f"Backup bulunamadı: {backup_proje_yolu}")
                
        except Exception as e:
            self.logger.error(f"Geri alma hatası: {e}")
    
    def _asama_guncelle(self, yeni_asama: RefactoringAsamasi):
        """Mevcut aşamayı günceller"""
        self.mevcut_asama = yeni_asama
        self.logger.info(f"Aşama güncellendi: {yeni_asama.value}")
    
    def _rapor_olustur(
        self,
        sonuc: RefactoringSonucu,
        hata_mesaji: str = None
    ) -> RefactoringRaporu:
        """
        Refactoring raporu oluşturur.
        
        Args:
            sonuc: Refactoring sonucu
            hata_mesaji: Hata mesajı (varsa)
            
        Returns:
            Refactoring raporu
        """
        if not self.mevcut_rapor:
            self.mevcut_rapor = RefactoringRaporu(
                plan_id=self.mevcut_plan.plan_id if self.mevcut_plan else "bilinmiyor",
                baslangic_zamani=datetime.now()
            )
        
        self.mevcut_rapor.bitis_zamani = datetime.now()
        self.mevcut_rapor.durum = sonuc
        
        if self.mevcut_plan:
            self.mevcut_rapor.basarili_adim_sayisi = sum(
                1 for adim in self.mevcut_plan.adimlar 
                if adim.durum == "tamamlandı"
            )
            self.mevcut_rapor.basarisiz_adim_sayisi = sum(
                1 for adim in self.mevcut_plan.adimlar 
                if adim.durum == "hata"
            )
        
        if hata_mesaji:
            self.mevcut_rapor.hata_mesajlari.append(hata_mesaji)
        
        if hasattr(self, '_son_backup_yolu'):
            self.mevcut_rapor.backup_yolu = self._son_backup_yolu
        
        return self.mevcut_rapor
    
    def raporu_yazdir(self, rapor: RefactoringRaporu):
        """
        Refactoring raporunu yazdırır.
        
        Args:
            rapor: Refactoring raporu
        """
        print("\n" + "="*60)
        print("REFACTORING RAPORU")
        print("="*60)
        print(f"Plan ID: {rapor.plan_id}")
        print(f"Başlangıç: {rapor.baslangic_zamani.strftime('%Y-%m-%d %H:%M:%S')}")
        if rapor.bitis_zamani:
            sure = rapor.bitis_zamani - rapor.baslangic_zamani
            print(f"Bitiş: {rapor.bitis_zamani.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Süre: {sure.total_seconds():.1f} saniye")
        
        print(f"Durum: {rapor.durum.value.upper()}")
        print(f"Başarılı adım: {rapor.basarili_adim_sayisi}")
        print(f"Başarısız adım: {rapor.basarisiz_adim_sayisi}")
        
        if rapor.hata_mesajlari:
            print("\nHata mesajları:")
            for hata in rapor.hata_mesajlari:
                print(f"  - {hata}")
        
        if rapor.backup_yolu:
            print(f"\nBackup yolu: {rapor.backup_yolu}")
        
        print("="*60)