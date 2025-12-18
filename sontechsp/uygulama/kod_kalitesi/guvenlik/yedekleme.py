# Version: 0.1.0
# Last Update: 2025-12-18
# Module: kod_kalitesi.guvenlik.yedekleme
# Description: Backup ve yedekleme işlemleri
# Changelog:
# - Refactoring: Dosya işlemleri ayrıldı

"""
Yedekleme Yöneticisi

Proje dosyalarının güvenli yedeklenmesi için gerekli
tüm işlemleri yönetir.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List

from .veri_yapilari import BackupBilgisi
from .dosya_islemleri import DosyaIslemleri


class YedeklemeYoneticisi:
    """
    Yedekleme Yöneticisi
    
    Proje dosyalarının backup'ını alır ve yönetir.
    Hash kontrolü ile dosya bütünlüğünü sağlar.
    """
    
    def __init__(
        self,
        proje_yolu: str,
        backup_klasoru: str,
        logger: logging.Logger
    ):
        """
        Args:
            proje_yolu: Yedeklenecek proje yolu
            backup_klasoru: Backup'ların saklanacağı klasör
            logger: Logger instance
        """
        self.proje_yolu = Path(proje_yolu)
        self.backup_klasoru = Path(backup_klasoru)
        self.logger = logger
        
        # Backup klasörünü oluştur
        self.backup_klasoru.mkdir(parents=True, exist_ok=True)
    
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
        backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.logger.info(f"Backup oluşturuluyor: {backup_id}")
        
        # Backup klasörü oluştur
        backup_yolu = self.backup_klasoru / backup_id
        backup_yolu.mkdir(exist_ok=True)
        
        # Varsayılan hariç tutulacaklar
        if hariç_tutulacaklar is None:
            hariç_tutulacaklar = [
                '__pycache__', '*.pyc', '.git', '.pytest_cache',
                'venv', 'env', '.hypothesis', '.guvenlik'
            ]
        
        # Proje dosyalarını kopyala
        dosya_sayisi, toplam_boyut = DosyaIslemleri.proje_kopyala(
            self.proje_yolu,
            backup_yolu / "proje",
            hariç_tutulacaklar
        )
        
        # Hash hesapla
        hash_degeri = DosyaIslemleri.hash_hesapla(backup_yolu / "proje")
        
        # Backup bilgilerini oluştur
        backup_bilgi = BackupBilgisi(
            backup_id=backup_id,
            olusturma_zamani=datetime.now(),
            proje_yolu=str(self.proje_yolu),
            backup_yolu=str(backup_yolu),
            dosya_sayisi=dosya_sayisi,
            toplam_boyut=toplam_boyut,
            hash_degeri=hash_degeri,
            aciklama=aciklama
        )
        
        # Metadata dosyası oluştur
        self._metadata_olustur(backup_yolu, backup_bilgi)
        
        self.logger.info(f"Backup oluşturuldu: {backup_yolu}")
        
        return backup_bilgi
    
    def _metadata_olustur(self, backup_yolu: Path, backup_bilgi: BackupBilgisi):
        """Backup metadata dosyası oluşturur"""
        metadata = {
            'backup_id': backup_bilgi.backup_id,
            'olusturma_zamani': backup_bilgi.olusturma_zamani.isoformat(),
            'proje_yolu': backup_bilgi.proje_yolu,
            'dosya_sayisi': backup_bilgi.dosya_sayisi,
            'toplam_boyut': backup_bilgi.toplam_boyut,
            'hash_degeri': backup_bilgi.hash_degeri,
            'aciklama': backup_bilgi.aciklama
        }
        
        with open(backup_yolu / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def hash_kontrol_et(self, backup_yolu: Path, beklenen_hash: str) -> bool:
        """
        Backup hash kontrolü yapar.
        
        Args:
            backup_yolu: Backup klasör yolu
            beklenen_hash: Beklenen hash değeri
            
        Returns:
            Hash kontrolü sonucu
        """
        try:
            mevcut_hash = DosyaIslemleri.hash_hesapla(backup_yolu)
            return mevcut_hash == beklenen_hash
        except Exception as e:
            self.logger.error(f"Hash kontrol hatası: {e}")
            return False