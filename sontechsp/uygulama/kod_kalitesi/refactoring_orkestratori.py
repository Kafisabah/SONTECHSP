# Version: 0.1.0
# Last Update: 2025-12-18
# Module: kod_kalitesi.refactoring_orkestratori
# Description: Ana refactoring orkestratörü facade
# Changelog:
# - Refactoring: Modüler yapıya geçiş

"""
Refactoring Orkestratörü Ana Facade

Tüm kod kalitesi refactoring işlemlerini koordine eder.
Facade pattern kullanarak alt sistemleri yönetir.
"""

import logging
from pathlib import Path
from typing import List

from .orkestrator import (
    RefactoringRaporu,
    FazKontrolcu,
    IlerlemeTakipci
)


class RefactoringOrkestratori:
    """
    Refactoring Orkestratörü Ana Facade
    
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
        
        # Faz kontrolcüsünü başlat
        self.faz_kontrolcu = FazKontrolcu(
            str(self.proje_yolu),
            str(self.backup_klasoru),
            self.logger
        )
        
        # İlerleme takipci
        self.ilerleme_takipci = IlerlemeTakipci(self.logger)
        
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
        return self.faz_kontrolcu.tam_refactoring_yap(
            hedef_klasorler,
            kullanici_onayı_gerekli
        )
    
    def kod_tabanini_analiz_et(
        self,
        hedef_klasorler: List[str] = None
    ):
        """
        Kod tabanını analiz eder ve refactoring planı oluşturur.
        
        Args:
            hedef_klasorler: Analiz edilecek klasörler
            
        Returns:
            Refactoring planı
        """
        return self.faz_kontrolcu.analiz_yoneticisi.kod_tabanini_analiz_et(
            str(self.proje_yolu),
            hedef_klasorler
        )
    
    def raporu_yazdir(self, rapor: RefactoringRaporu):
        """
        Refactoring raporunu yazdırır.
        
        Args:
            rapor: Refactoring raporu
        """
        self.ilerleme_takipci.raporu_yazdir(rapor)