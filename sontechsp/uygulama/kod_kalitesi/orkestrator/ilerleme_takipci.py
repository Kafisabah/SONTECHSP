# Version: 0.1.0
# Last Update: 2025-12-18
# Module: kod_kalitesi.orkestrator.ilerleme_takipci
# Description: İlerleme takibi ve raporlama
# Changelog:
# - İlk versiyon: İlerleme takipci sınıfı

"""
İlerleme Takipci

Refactoring sürecinin ilerlemesini takip eder ve
raporlar oluşturur.
"""

import logging
from datetime import datetime
from typing import Optional

from .veri_yapilari import (
    RefactoringPlani, 
    RefactoringRaporu, 
    RefactoringSonucu
)


class IlerlemeTakipci:
    """
    İlerleme Takipci
    
    Refactoring sürecinin ilerlemesini takip eder,
    raporlar oluşturur ve yazdırır.
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Args:
            logger: Logger instance
        """
        self.logger = logger
        self.mevcut_rapor: Optional[RefactoringRaporu] = None
    
    def rapor_olustur(
        self,
        plan: Optional[RefactoringPlani],
        sonuc: RefactoringSonucu,
        backup_yolu: str = None,
        hata_mesaji: str = None
    ) -> RefactoringRaporu:
        """
        Refactoring raporu oluşturur.
        
        Args:
            plan: Refactoring planı
            sonuc: Refactoring sonucu
            backup_yolu: Backup yolu
            hata_mesaji: Hata mesajı (varsa)
            
        Returns:
            Refactoring raporu
        """
        if not self.mevcut_rapor:
            self.mevcut_rapor = RefactoringRaporu(
                plan_id=plan.plan_id if plan else "bilinmiyor",
                baslangic_zamani=datetime.now()
            )
        
        self.mevcut_rapor.bitis_zamani = datetime.now()
        self.mevcut_rapor.durum = sonuc
        
        if plan:
            self.mevcut_rapor.basarili_adim_sayisi = sum(
                1 for adim in plan.adimlar 
                if adim.durum == "tamamlandı"
            )
            self.mevcut_rapor.basarisiz_adim_sayisi = sum(
                1 for adim in plan.adimlar 
                if adim.durum == "hata"
            )
        
        if hata_mesaji:
            self.mevcut_rapor.hata_mesajlari.append(hata_mesaji)
        
        if backup_yolu:
            self.mevcut_rapor.backup_yolu = backup_yolu
        
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
    
    def ilerleme_guncelle(self, mesaj: str, yuzde: int = None):
        """
        İlerleme durumunu günceller.
        
        Args:
            mesaj: İlerleme mesajı
            yuzde: Tamamlanma yüzdesi
        """
        if yuzde is not None:
            self.logger.info(f"İlerleme %{yuzde}: {mesaj}")
        else:
            self.logger.info(f"İlerleme: {mesaj}")
    
    def adim_basladi(self, adim_aciklama: str):
        """
        Adım başladığında çağrılır.
        
        Args:
            adim_aciklama: Adım açıklaması
        """
        self.logger.info(f"Adım başladı: {adim_aciklama}")
    
    def adim_tamamlandi(self, adim_aciklama: str, sure: float):
        """
        Adım tamamlandığında çağrılır.
        
        Args:
            adim_aciklama: Adım açıklaması
            sure: Adım süresi (saniye)
        """
        self.logger.info(f"Adım tamamlandı: {adim_aciklama} ({sure:.1f}s)")
    
    def adim_hatasi(self, adim_aciklama: str, hata: str):
        """
        Adım hatası durumunda çağrılır.
        
        Args:
            adim_aciklama: Adım açıklaması
            hata: Hata mesajı
        """
        self.logger.error(f"Adım hatası: {adim_aciklama} - {hata}")