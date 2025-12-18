# Version: 0.1.0
# Last Update: 2025-12-18
# Module: kod_kalitesi.orkestrator.faz_kontrolcu
# Description: Refactoring faz kontrolü
# Changelog:
# - İlk versiyon: Faz kontrolcü sınıfı

"""
Faz Kontrolcü

Refactoring sürecinin fazlarını kontrol eder ve yönetir.
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ..guvenlik_sistemi import GuvenlikSistemi
from .veri_yapilari import (
    RefactoringAsamasi, 
    RefactoringSonucu, 
    RefactoringPlani, 
    RefactoringRaporu
)
from .analiz_yoneticisi import AnalizYoneticisi
from .uygulama_yoneticisi import UygulamaYoneticisi
from .ilerleme_takipci import IlerlemeTakipci


class FazKontrolcu:
    """
    Faz Kontrolcü
    
    Refactoring sürecinin fazlarını kontrol eder ve
    alt sistemleri koordine eder.
    """
    
    def __init__(
        self,
        proje_yolu: str,
        backup_klasoru: str,
        logger: logging.Logger
    ):
        """
        Args:
            proje_yolu: Refactoring yapılacak proje yolu
            backup_klasoru: Backup klasörü
            logger: Logger instance
        """
        self.proje_yolu = Path(proje_yolu)
        self.backup_klasoru = Path(backup_klasoru)
        self.logger = logger
        
        # Alt sistemleri başlat
        self.analiz_yoneticisi = AnalizYoneticisi(logger)
        self.uygulama_yoneticisi = UygulamaYoneticisi(logger)
        self.ilerleme_takipci = IlerlemeTakipci(logger)
        
        # Güvenlik sistemi
        self.guvenlik_sistemi = GuvenlikSistemi(
            proje_yolu=str(self.proje_yolu),
            guvenlik_klasoru=str(self.backup_klasoru.parent / "guvenlik"),
            log_seviyesi=logger.level
        )
        
        # Durum takibi
        self.mevcut_asama = RefactoringAsamasi.ANALIZ
    
    def tam_refactoring_yap(
        self,
        hedef_klasorler: List[str] = None,
        kullanici_onayı_gerekli: bool = True
    ) -> RefactoringRaporu:
        """
        Tam refactoring süreci yürütür.
        
        Args:
            hedef_klasorler: Refactoring yapılacak klasörler
            kullanici_onayı_gerekli: Kullanıcı onayı gerekli mi
            
        Returns:
            Refactoring raporu
        """
        try:
            self.logger.info("Tam refactoring süreci başlatılıyor...")
            
            # 1. Analiz aşaması
            self._asama_guncelle(RefactoringAsamasi.ANALIZ)
            plan = self.analiz_yoneticisi.kod_tabanini_analiz_et(
                str(self.proje_yolu), 
                hedef_klasorler
            )
            
            if not plan.adimlar:
                self.logger.info("Refactoring gerektiren sorun bulunamadı.")
                return self.ilerleme_takipci.rapor_olustur(
                    plan, RefactoringSonucu.BASARILI
                )
            
            # 2. Planlama aşaması
            self._asama_guncelle(RefactoringAsamasi.PLANLAMA)
            if kullanici_onayı_gerekli:
                onay = self._kullanici_onayı_al(plan)
                if not onay:
                    return self.ilerleme_takipci.rapor_olustur(
                        plan, RefactoringSonucu.IPTAL_EDILDI
                    )
            
            # 3. Backup aşaması
            self._asama_guncelle(RefactoringAsamasi.BACKUP)
            backup_yolu = self._backup_olustur()
            
            # 4. Uygulama aşaması
            self._asama_guncelle(RefactoringAsamasi.UYGULAMA)
            basarili_adimlar = self.uygulama_yoneticisi.plani_uygula(plan)
            
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
            
            return self.ilerleme_takipci.rapor_olustur(plan, sonuc, backup_yolu)
            
        except Exception as e:
            self.logger.error(f"Refactoring sırasında hata: {e}")
            self._asama_guncelle(RefactoringAsamasi.HATA)
            
            # Hata durumunda geri al
            if hasattr(self, '_son_backup_yolu'):
                self._geri_al(self._son_backup_yolu)
            
            return self.ilerleme_takipci.rapor_olustur(
                plan if 'plan' in locals() else None, 
                RefactoringSonucu.BASARISIZ, 
                hata_mesaji=str(e)
            )
    
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
        backup_bilgi = self.guvenlik_sistemi.backup_olustur(
            "Refactoring öncesi otomatik backup"
        )
        
        self._son_backup_yolu = backup_bilgi.backup_yolu
        self.logger.info(f"Backup oluşturuldu: {backup_bilgi.backup_yolu}")
        
        return backup_bilgi.backup_yolu
    
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