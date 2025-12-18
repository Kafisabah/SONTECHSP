# Version: 0.1.0
# Last Update: 2025-12-18
# Module: kod_kalitesi.guvenlik.koordinator
# Description: Güvenlik sistemi koordinatörü
# Changelog:
# - İlk versiyon: Ana koordinasyon sınıfı

"""
Güvenlik Sistemi Koordinatörü

Alt sistemleri koordine eder ve ana API'yi sağlar.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .veri_yapilari import IslemTuru, BackupBilgisi
from .yedekleme import YedeklemeYoneticisi
from .geri_yukleme import GeriYuklemeYoneticisi
from .denetim import DenetimYoneticisi


class GuvenlikKoordinatoru:
    """
    Güvenlik Sistemi Koordinatörü
    
    Yedekleme, geri yükleme ve denetim alt sistemlerini
    koordine eder.
    """
    
    def __init__(
        self,
        proje_yolu: str,
        guvenlik_klasoru: str,
        logger: logging.Logger
    ):
        """
        Args:
            proje_yolu: Korunacak proje yolu
            guvenlik_klasoru: Güvenlik dosyalarının saklanacağı klasör
            logger: Logger instance
        """
        self.proje_yolu = Path(proje_yolu)
        self.guvenlik_klasoru = Path(guvenlik_klasoru)
        self.logger = logger
        
        # Alt klasörleri oluştur
        self.backup_klasoru = self.guvenlik_klasoru / "backups"
        self.audit_klasoru = self.guvenlik_klasoru / "audit"
        
        for klasor in [self.backup_klasoru, self.audit_klasoru]:
            klasor.mkdir(exist_ok=True)
        
        # Alt sistemleri başlat
        self.yedekleme_yoneticisi = YedeklemeYoneticisi(
            str(self.proje_yolu),
            str(self.backup_klasoru),
            self.logger
        )
        
        self.geri_yukleme_yoneticisi = GeriYuklemeYoneticisi(
            str(self.proje_yolu),
            self.logger
        )
        
        self.denetim_yoneticisi = DenetimYoneticisi(
            str(self.audit_klasoru),
            self.logger
        )
    
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
        islem_id = self.denetim_yoneticisi.islem_baslat(
            IslemTuru.BACKUP_OLUSTUR,
            [str(self.proje_yolu)]
        )
        
        try:
            backup_bilgi = self.yedekleme_yoneticisi.backup_olustur(
                aciklama,
                hariç_tutulacaklar
            )
            
            # Backup bilgisini denetim sistemine kaydet
            self.denetim_yoneticisi.backup_kaydet(backup_bilgi)
            
            self.denetim_yoneticisi.islem_tamamla(
                islem_id,
                backup_yolu=backup_bilgi.backup_yolu
            )
            
            return backup_bilgi
            
        except Exception as e:
            self.denetim_yoneticisi.islem_hata(islem_id, str(e))
            raise
    
    def geri_al(self, backup_id: str) -> bool:
        """
        Backup'tan geri alma yapar.
        
        Args:
            backup_id: Geri alınacak backup ID'si
            
        Returns:
            Başarı durumu
        """
        islem_id = self.denetim_yoneticisi.islem_baslat(
            IslemTuru.GERI_AL,
            [backup_id]
        )
        
        try:
            # Backup bilgisini al
            backup_bilgi = self.denetim_yoneticisi.backup_al(backup_id)
            if not backup_bilgi:
                raise ValueError(f"Backup bulunamadı: {backup_id}")
            
            # Mevcut projeyi yedekle (güvenlik için)
            acil_backup = self.backup_olustur(
                f"Acil backup - geri alma öncesi: {backup_id}"
            )
            
            # Geri yükleme yap
            basarili = self.geri_yukleme_yoneticisi.geri_yukle(backup_bilgi)
            
            if basarili:
                self.denetim_yoneticisi.islem_tamamla(islem_id)
            else:
                self.denetim_yoneticisi.islem_hata(islem_id, "Geri yükleme başarısız")
            
            return basarili
            
        except Exception as e:
            self.denetim_yoneticisi.islem_hata(islem_id, str(e))
            return False
    
    def dosya_butunlugu_kontrol_et(self, dosya_yolu: str) -> bool:
        """
        Dosya bütünlüğünü kontrol eder.
        
        Args:
            dosya_yolu: Kontrol edilecek dosya yolu
            
        Returns:
            Bütünlük durumu
        """
        return self.geri_yukleme_yoneticisi.dosya_butunlugu_kontrol_et(dosya_yolu)
    
    def backup_listesi_al(self) -> List[BackupBilgisi]:
        """
        Tüm backup'ların listesini alır.
        
        Returns:
            Backup listesi
        """
        return self.denetim_yoneticisi.backup_listesi_al()
    
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
        return self.denetim_yoneticisi.audit_raporu_olustur(
            baslangic_tarihi,
            bitis_tarihi
        )