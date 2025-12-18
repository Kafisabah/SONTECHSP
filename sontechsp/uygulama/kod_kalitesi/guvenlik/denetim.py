# Version: 0.1.0
# Last Update: 2025-12-18
# Module: kod_kalitesi.guvenlik.denetim
# Description: Denetim ve audit sistemi
# Changelog:
# - Refactoring: Veritabanı ve rapor işlemleri ayrıldı

"""
Denetim Yöneticisi

Güvenlik sistemi işlemlerinin denetimi ve audit
kayıtlarının yönetimi için gerekli tüm işlemleri içerir.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from .veri_yapilari import IslemKaydi, IslemTuru, IslemDurumu, BackupBilgisi
from .audit_db import AuditDbYoneticisi
from .rapor_uretici import AuditRaporUreticisi


class DenetimYoneticisi:
    """
    Denetim Yöneticisi
    
    Tüm güvenlik işlemlerinin audit kayıtlarını tutar.
    İşlem logları ve raporlama sistemi sağlar.
    """
    
    def __init__(
        self,
        audit_klasoru: str,
        logger: logging.Logger
    ):
        """
        Args:
            audit_klasoru: Audit dosyalarının saklanacağı klasör
            logger: Logger instance
        """
        self.audit_klasoru = Path(audit_klasoru)
        self.logger = logger
        
        # Audit klasörünü oluştur
        self.audit_klasoru.mkdir(parents=True, exist_ok=True)
        
        # Alt sistemleri başlat
        audit_db_yolu = self.audit_klasoru / "audit.db"
        self.db_yoneticisi = AuditDbYoneticisi(str(audit_db_yolu))
        self.rapor_uretici = AuditRaporUreticisi(str(audit_db_yolu))
        
        # Aktif işlemler
        self.aktif_islemler: Dict[str, IslemKaydi] = {}
    
    def islem_baslat(
        self,
        islem_turu: IslemTuru,
        hedef_dosyalar: List[str]
    ) -> str:
        """
        Yeni işlem başlatır ve audit kaydı oluşturur.
        
        Args:
            islem_turu: İşlem türü
            hedef_dosyalar: Hedef dosya listesi
            
        Returns:
            İşlem ID'si
        """
        islem_id = f"{islem_turu.value}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        islem_kaydi = IslemKaydi(
            islem_id=islem_id,
            islem_turu=islem_turu,
            durum=IslemDurumu.BASLADI,
            baslangic_zamani=datetime.now(),
            hedef_dosyalar=hedef_dosyalar
        )
        
        self.aktif_islemler[islem_id] = islem_kaydi
        self.db_yoneticisi.islem_kaydi_ekle(islem_kaydi)
        
        self.logger.info(f"İşlem başlatıldı: {islem_id} - {islem_turu.value}")
        
        return islem_id
    
    def islem_tamamla(
        self,
        islem_id: str,
        degisiklikler: Dict[str, Any] = None,
        backup_yolu: str = None
    ):
        """
        İşlemi tamamlar ve audit kaydını günceller.
        
        Args:
            islem_id: İşlem ID'si
            degisiklikler: Yapılan değişiklikler
            backup_yolu: Backup yolu (varsa)
        """
        if islem_id in self.aktif_islemler:
            islem = self.aktif_islemler[islem_id]
            islem.durum = IslemDurumu.TAMAMLANDI
            islem.bitis_zamani = datetime.now()
            
            if degisiklikler:
                islem.degisiklikler = degisiklikler
            
            if backup_yolu:
                islem.backup_yolu = backup_yolu
            
            self.db_yoneticisi.islem_kaydi_guncelle(islem)
            del self.aktif_islemler[islem_id]
            
            self.logger.info(f"İşlem tamamlandı: {islem_id}")
    
    def islem_hata(self, islem_id: str, hata_mesaji: str):
        """
        İşlem hatasını kaydeder.
        
        Args:
            islem_id: İşlem ID'si
            hata_mesaji: Hata mesajı
        """
        if islem_id in self.aktif_islemler:
            islem = self.aktif_islemler[islem_id]
            islem.durum = IslemDurumu.HATA
            islem.bitis_zamani = datetime.now()
            islem.hata_mesaji = hata_mesaji
            
            self.db_yoneticisi.islem_kaydi_guncelle(islem)
            del self.aktif_islemler[islem_id]
            
            self.logger.error(f"İşlem hatası: {islem_id} - {hata_mesaji}")
    
    def backup_kaydet(self, backup_bilgi: BackupBilgisi):
        """
        Backup bilgisini veritabanına kaydeder.
        
        Args:
            backup_bilgi: Backup bilgisi
        """
        self.db_yoneticisi.backup_kaydet(backup_bilgi)
        self.logger.info(f"Backup kaydedildi: {backup_bilgi.backup_id}")
    
    def backup_al(self, backup_id: str) -> Optional[BackupBilgisi]:
        """
        Backup bilgisini veritabanından alır.
        
        Args:
            backup_id: Backup ID'si
            
        Returns:
            Backup bilgisi
        """
        return self.db_yoneticisi.backup_al(backup_id)
    
    def backup_listesi_al(self) -> List[BackupBilgisi]:
        """
        Tüm backup'ların listesini alır.
        
        Returns:
            Backup listesi
        """
        return self.db_yoneticisi.backup_listesi_al()
    
    def audit_raporu_olustur(
        self,
        baslangic_tarihi: datetime = None,
        bitis_tarihi: datetime = None
    ) -> Dict[str, Any]:
        """
        Audit raporu oluşturur.
        
        Args:
            baslangic_tarihi: Rapor başlangıç tarihi
            bitis_tarihi: Rapor bitiş tarihi
            
        Returns:
            Audit raporu
        """
        return self.rapor_uretici.audit_raporu_olustur(
            baslangic_tarihi,
            bitis_tarihi
        )