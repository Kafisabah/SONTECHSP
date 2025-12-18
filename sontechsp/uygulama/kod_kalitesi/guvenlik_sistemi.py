# Version: 0.1.0
# Last Update: 2025-12-18
# Module: kod_kalitesi.guvenlik_sistemi
# Description: Ana güvenlik sistemi facade
# Changelog:
# - Refactoring: Koordinatör pattern'e geçiş

"""
Güvenlik Sistemi Ana Facade

Refactoring işlemleri için güvenlik önlemlerini sağlar.
Koordinatör pattern kullanarak alt sistemleri yönetir.
"""

import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List

from .guvenlik import BackupBilgisi, IslemTuru
from .guvenlik.koordinator import GuvenlikKoordinatoru


class GuvenlikSistemi:
    """
    Güvenlik Sistemi Ana Facade
    
    Refactoring işlemleri için güvenlik önlemleri sağlar:
    - Backup ve restore mekanizması
    - İşlem logları ve audit trail
    - Dosya bütünlüğü kontrolü
    - Geri alma işlemleri
    """
    
    def __init__(
        self,
        proje_yolu: str,
        guvenlik_klasoru: str = None,
        log_seviyesi: int = logging.INFO
    ):
        """
        Args:
            proje_yolu: Korunacak proje yolu
            guvenlik_klasoru: Güvenlik dosyalarının saklanacağı klasör
            log_seviyesi: Log seviyesi
        """
        self.proje_yolu = Path(proje_yolu)
        self.guvenlik_klasoru = Path(
            guvenlik_klasoru or self.proje_yolu / ".guvenlik"
        )
        
        # Güvenlik klasörünü oluştur
        self.guvenlik_klasoru.mkdir(parents=True, exist_ok=True)
        
        # Log klasörünü oluştur
        self.log_klasoru = self.guvenlik_klasoru / "logs"
        self.log_klasoru.mkdir(exist_ok=True)
        
        # Logger kurulumu
        self.logger = self._logger_kurulumu(log_seviyesi)
        
        # Koordinatörü başlat
        self.koordinator = GuvenlikKoordinatoru(
            str(self.proje_yolu),
            str(self.guvenlik_klasoru),
            self.logger
        )
        
        self.logger.info(f"GuvenlikSistemi başlatıldı: {self.proje_yolu}")
    
    def _logger_kurulumu(self, log_seviyesi: int) -> logging.Logger:
        """Logger kurulumu yapar"""
        logger = logging.getLogger(f"GuvenlikSistemi_{id(self)}")
        logger.setLevel(log_seviyesi)
        
        if not logger.handlers:
            # Dosya handler
            log_dosyasi = self.log_klasoru / f"guvenlik_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_dosyasi, encoding='utf-8')
            file_handler.setLevel(log_seviyesi)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_seviyesi)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def backup_olustur(
        self,
        aciklama: str = "",
        hariç_tutulacaklar: List[str] = None
    ) -> BackupBilgisi:
        """
        Proje backup'ı oluşturur.
        
        Args:
            aciklama: Backup açıklaması
            hariç_tutulacaklar: Hariç tutulacak dosya/klasör desenleri
            
        Returns:
            Backup bilgisi
        """
        return self.koordinator.backup_olustur(aciklama, hariç_tutulacaklar)
    
    def geri_al(self, backup_id: str) -> bool:
        """
        Backup'tan geri alma yapar.
        
        Args:
            backup_id: Geri alınacak backup ID'si
            
        Returns:
            Başarı durumu
        """
        return self.koordinator.geri_al(backup_id)
    
    def dosya_butunlugu_kontrol_et(self, dosya_yolu: str) -> bool:
        """
        Dosya bütünlüğünü kontrol eder.
        
        Args:
            dosya_yolu: Kontrol edilecek dosya yolu
            
        Returns:
            Bütünlük durumu
        """
        return self.koordinator.dosya_butunlugu_kontrol_et(dosya_yolu)
    
    def backup_listesi_al(self) -> List[BackupBilgisi]:
        """
        Tüm backup'ların listesini alır.
        
        Returns:
            Backup listesi
        """
        return self.koordinator.backup_listesi_al()
    
    def audit_raporu_olustur(
        self,
        baslangic_tarihi: datetime = None,
        bitis_tarihi: datetime = None
    ):
        """
        Audit raporu oluşturur.
        
        Args:
            baslangic_tarihi: Rapor başlangıç tarihi
            bitis_tarihi: Rapor bitiş tarihi
            
        Returns:
            Audit raporu
        """
        return self.koordinator.audit_raporu_olustur(baslangic_tarihi, bitis_tarihi)
    
    def temizlik_yap(self, gun_sayisi: int = 30):
        """
        Eski backup ve log dosyalarını temizler.
        
        Args:
            gun_sayisi: Kaç günden eski dosyalar silinecek
        """
        kesim_tarihi = datetime.now().replace(hour=0, minute=0, second=0)
        kesim_tarihi = kesim_tarihi.replace(day=kesim_tarihi.day - gun_sayisi)
        
        self.logger.info(f"Temizlik başlatılıyor: {kesim_tarihi} öncesi")
        
        # Eski backup'ları al
        tum_backuplar = self.backup_listesi_al()
        silinen_backup_sayisi = 0
        
        for backup in tum_backuplar:
            if backup.olusturma_zamani < kesim_tarihi:
                try:
                    backup_yolu = Path(backup.backup_yolu)
                    if backup_yolu.exists():
                        shutil.rmtree(backup_yolu)
                    silinen_backup_sayisi += 1
                except Exception as e:
                    self.logger.warning(f"Backup silme hatası {backup.backup_id}: {e}")
        
        self.logger.info(f"Temizlik tamamlandı: {silinen_backup_sayisi} backup silindi")