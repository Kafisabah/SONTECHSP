# Version: 0.1.0
# Last Update: 2025-12-18
# Module: kod_kalitesi.guvenlik.geri_yukleme
# Description: Geri yükleme ve restore işlemleri
# Changelog:
# - Refactoring: Hash kontrolü dosya işlemlerine taşındı

"""
Geri Yükleme Yöneticisi

Backup'lardan proje dosyalarının geri yüklenmesi
için gerekli tüm işlemleri yönetir.
"""

import logging
import shutil
from pathlib import Path

from .veri_yapilari import BackupBilgisi
from .dosya_islemleri import DosyaIslemleri


class GeriYuklemeYoneticisi:
    """
    Geri Yükleme Yöneticisi
    
    Backup'lardan proje dosyalarını geri yükler.
    Hash kontrolü ile dosya bütünlüğünü doğrular.
    """
    
    def __init__(
        self,
        proje_yolu: str,
        logger: logging.Logger
    ):
        """
        Args:
            proje_yolu: Geri yüklenecek proje yolu
            logger: Logger instance
        """
        self.proje_yolu = Path(proje_yolu)
        self.logger = logger
    
    def geri_yukle(
        self,
        backup_bilgi: BackupBilgisi,
        hash_kontrol_yap: bool = True
    ) -> bool:
        """
        Backup'tan geri yükleme yapar.
        
        Args:
            backup_bilgi: Geri yüklenecek backup bilgisi
            hash_kontrol_yap: Hash kontrolü yapılsın mı
            
        Returns:
            Başarı durumu
        """
        try:
            self.logger.info(f"Geri yükleme başlatılıyor: {backup_bilgi.backup_id}")
            
            backup_yolu = Path(backup_bilgi.backup_yolu)
            proje_backup_yolu = backup_yolu / "proje"
            
            if not proje_backup_yolu.exists():
                raise FileNotFoundError(f"Backup dosyaları bulunamadı: {proje_backup_yolu}")
            
            # Hash kontrolü
            if hash_kontrol_yap:
                if not self._hash_kontrol_et(proje_backup_yolu, backup_bilgi.hash_degeri):
                    self.logger.warning(f"Backup hash uyumsuzluğu: {backup_bilgi.backup_id}")
                    return False
            
            # Mevcut projeyi sil
            if self.proje_yolu.exists():
                self._proje_sil()
            
            # Backup'tan geri yükle
            shutil.copytree(proje_backup_yolu, self.proje_yolu)
            
            self.logger.info(f"Geri yükleme tamamlandı: {backup_bilgi.backup_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Geri yükleme hatası: {e}")
            return False
    
    def dosya_butunlugu_kontrol_et(self, dosya_yolu: str) -> bool:
        """
        Dosya bütünlüğünü kontrol eder.
        
        Args:
            dosya_yolu: Kontrol edilecek dosya yolu
            
        Returns:
            Bütünlük durumu
        """
        try:
            dosya = Path(dosya_yolu)
            if not dosya.exists():
                return False
            
            # Dosya okunabilir mi?
            with open(dosya, 'r', encoding='utf-8') as f:
                f.read()
            
            # Python dosyası ise syntax kontrolü
            if dosya.suffix == '.py':
                with open(dosya, 'r', encoding='utf-8') as f:
                    compile(f.read(), str(dosya), 'exec')
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Dosya bütünlük hatası {dosya_yolu}: {e}")
            return False
    
    def _hash_kontrol_et(self, backup_yolu: Path, beklenen_hash: str) -> bool:
        """Hash kontrolü yapar"""
        try:
            mevcut_hash = DosyaIslemleri.hash_hesapla(backup_yolu)
            return mevcut_hash == beklenen_hash
        except Exception as e:
            self.logger.error(f"Hash kontrol hatası: {e}")
            return False
    
    def _proje_sil(self):
        """Mevcut projeyi güvenli şekilde siler"""
        try:
            shutil.rmtree(self.proje_yolu)
            self.logger.info(f"Mevcut proje silindi: {self.proje_yolu}")
        except Exception as e:
            self.logger.error(f"Proje silme hatası: {e}")
            raise