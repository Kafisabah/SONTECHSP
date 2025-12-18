# Version: 0.1.0
# Last Update: 2025-12-18
# Module: kod_kalitesi.orkestrator.analiz_yoneticisi
# Description: Kod analizi ve plan oluşturma
# Changelog:
# - İlk versiyon: Analiz yöneticisi sınıfı

"""
Analiz Yöneticisi

Kod tabanını analiz eder ve refactoring planı oluşturur.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List

from uygulama.moduller.kod_kalitesi.analizorler.dosya_boyut_analizoru import (
    DosyaBoyutAnalizoru
)
from uygulama.moduller.kod_kalitesi.analizorler.fonksiyon_boyut_analizoru import (
    FonksiyonBoyutAnalizoru
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

from .veri_yapilari import RefactoringPlani, RefactoringAdimi


class AnalizYoneticisi:
    """
    Analiz Yöneticisi
    
    Kod tabanını analiz eder ve refactoring planı oluşturur.
    Çeşitli analizörleri koordine eder.
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Args:
            logger: Logger instance
        """
        self.logger = logger
        
        # Analizörleri başlat
        self.dosya_analizoru = DosyaBoyutAnalizoru()
        self.fonksiyon_analizoru = FonksiyonBoyutAnalizoru()
        self.import_analizoru = ImportYapisiAnalizoru()
        self.kod_tekrari_analizoru = KodTekrariAnalizoru()
        self.baslik_analizoru = BaslikAnalizoru()
    
    def kod_tabanini_analiz_et(
        self,
        proje_yolu: str,
        hedef_klasorler: List[str] = None
    ) -> RefactoringPlani:
        """
        Kod tabanını analiz eder ve refactoring planı oluşturur.
        
        Args:
            proje_yolu: Proje yolu
            hedef_klasorler: Analiz edilecek klasörler
            
        Returns:
            Refactoring planı
        """
        self.logger.info("Kod tabanı analizi başlatılıyor...")
        
        if hedef_klasorler is None:
            hedef_klasorler = [proje_yolu]
        
        plan = RefactoringPlani(
            plan_id=f"refactoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            proje_yolu=proje_yolu,
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