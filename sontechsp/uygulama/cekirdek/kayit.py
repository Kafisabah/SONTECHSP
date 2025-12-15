# Version: 0.1.0
# Last Update: 2024-12-15
# Module: kayit
# Description: SONTECHSP kayıt (logging) sistemi modülü
# Changelog:
# - 0.1.0: İlk sürüm, çift çıktı log sistemi ve Türkçe mesaj desteği

"""
SONTECHSP Kayıt (Logging) Sistemi Modülü

Bu modül uygulama olaylarını kayıt altına alır:
- Çift çıktı: dosya + konsol
- Seviye filtreleme (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Otomatik dosya döndürme
- Türkçe mesaj desteği
- Yapılandırılabilir log formatı
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class TurkceFormatter(logging.Formatter):
    """Türkçe log mesajları için özel formatter"""
    
    SEVIYE_ISIMLERI = {
        'DEBUG': 'HATA_AYIKLAMA',
        'INFO': 'BİLGİ',
        'WARNING': 'UYARI',
        'ERROR': 'HATA',
        'CRITICAL': 'KRİTİK'
    }
    
    def format(self, record):
        # Seviye ismini Türkçe'ye çevir
        if record.levelname in self.SEVIYE_ISIMLERI:
            record.levelname = self.SEVIYE_ISIMLERI[record.levelname]
        
        return super().format(record)


class KayitSistemi:
    """
    SONTECHSP kayıt sistemi
    
    Özellikler:
    - Çift çıktı (dosya + konsol)
    - Seviye filtreleme
    - Otomatik dosya döndürme
    - Türkçe mesaj desteği
    """
    
    def __init__(self, 
                 log_klasoru: str = "logs",
                 log_seviyesi: str = "INFO",
                 log_dosya_boyutu: int = 10485760,  # 10MB
                 log_dosya_sayisi: int = 5,
                 dosya_adi: str = "sontechsp"):
        
        self.log_klasoru = Path(log_klasoru)
        self.log_seviyesi = log_seviyesi.upper()
        self.log_dosya_boyutu = log_dosya_boyutu
        self.log_dosya_sayisi = log_dosya_sayisi
        self.dosya_adi = dosya_adi
        
        self._logger: Optional[logging.Logger] = None
        self._dosya_handler: Optional[logging.handlers.RotatingFileHandler] = None
        self._konsol_handler: Optional[logging.StreamHandler] = None
        
        self._log_sistemi_kur()

    def _log_sistemi_kur(self) -> None:
        """Log sistemini kurar"""
        # Log klasörünü oluştur
        self._log_klasoru_olustur()
        
        # Logger'ı oluştur
        self._logger = logging.getLogger('sontechsp')
        self._logger.setLevel(getattr(logging, self.log_seviyesi))
        
        # Mevcut handler'ları temizle
        self._logger.handlers.clear()
        
        # Dosya handler'ını kur
        self._dosya_handler_kur()
        
        # Konsol handler'ını kur
        self._konsol_handler_kur()

    def _log_klasoru_olustur(self) -> None:
        """Log klasörünü oluşturur"""
        try:
            self.log_klasoru.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Log klasörü oluşturulamadı: {e}", file=sys.stderr)
            # Varsayılan olarak mevcut dizini kullan
            self.log_klasoru = Path(".")

    def _dosya_handler_kur(self) -> None:
        """Dosya handler'ını kurar"""
        log_dosya_yolu = self.log_klasoru / f"{self.dosya_adi}.log"
        
        self._dosya_handler = logging.handlers.RotatingFileHandler(
            log_dosya_yolu,
            maxBytes=self.log_dosya_boyutu,
            backupCount=self.log_dosya_sayisi,
            encoding='utf-8'
        )
        
        # Dosya formatı (detaylı)
        dosya_format = TurkceFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self._dosya_handler.setFormatter(dosya_format)
        self._dosya_handler.setLevel(getattr(logging, self.log_seviyesi))
        
        self._logger.addHandler(self._dosya_handler)

    def _konsol_handler_kur(self) -> None:
        """Konsol handler'ını kurar"""
        self._konsol_handler = logging.StreamHandler(sys.stdout)
        
        # Konsol formatı (sade)
        konsol_format = TurkceFormatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        self._konsol_handler.setFormatter(konsol_format)
        self._konsol_handler.setLevel(getattr(logging, self.log_seviyesi))
        
        self._logger.addHandler(self._konsol_handler)

    def debug(self, mesaj: str, **kwargs) -> None:
        """
        Debug seviyesinde log kaydı
        
        Args:
            mesaj: Log mesajı
            **kwargs: Ek parametreler
        """
        if self._logger:
            self._logger.debug(mesaj, **kwargs)

    def info(self, mesaj: str, **kwargs) -> None:
        """
        Info seviyesinde log kaydı
        
        Args:
            mesaj: Log mesajı
            **kwargs: Ek parametreler
        """
        if self._logger:
            self._logger.info(mesaj, **kwargs)

    def warning(self, mesaj: str, **kwargs) -> None:
        """
        Warning seviyesinde log kaydı
        
        Args:
            mesaj: Log mesajı
            **kwargs: Ek parametreler
        """
        if self._logger:
            self._logger.warning(mesaj, **kwargs)

    def error(self, mesaj: str, **kwargs) -> None:
        """
        Error seviyesinde log kaydı
        
        Args:
            mesaj: Log mesajı
            **kwargs: Ek parametreler
        """
        if self._logger:
            self._logger.error(mesaj, **kwargs)

    def critical(self, mesaj: str, **kwargs) -> None:
        """
        Critical seviyesinde log kaydı
        
        Args:
            mesaj: Log mesajı
            **kwargs: Ek parametreler
        """
        if self._logger:
            self._logger.critical(mesaj, **kwargs)

    def exception(self, mesaj: str, **kwargs) -> None:
        """
        Exception bilgisi ile birlikte error seviyesinde log kaydı
        
        Args:
            mesaj: Log mesajı
            **kwargs: Ek parametreler
        """
        if self._logger:
            self._logger.exception(mesaj, **kwargs)

    def log_seviyesi_degistir(self, yeni_seviye: str) -> None:
        """
        Log seviyesini değiştirir
        
        Args:
            yeni_seviye: Yeni log seviyesi (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        yeni_seviye = yeni_seviye.upper()
        if yeni_seviye in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            self.log_seviyesi = yeni_seviye
            
            if self._logger:
                self._logger.setLevel(getattr(logging, yeni_seviye))
            
            if self._dosya_handler:
                self._dosya_handler.setLevel(getattr(logging, yeni_seviye))
            
            if self._konsol_handler:
                self._konsol_handler.setLevel(getattr(logging, yeni_seviye))
            
            self.info(f"Log seviyesi {yeni_seviye} olarak değiştirildi")

    def log_dosyasi_yolu(self) -> Path:
        """
        Aktif log dosyasının yolunu döndürür
        
        Returns:
            Log dosyası yolu
        """
        return self.log_klasoru / f"{self.dosya_adi}.log"

    def log_dosyasi_boyutu(self) -> int:
        """
        Aktif log dosyasının boyutunu döndürür
        
        Returns:
            Dosya boyutu (byte)
        """
        try:
            return self.log_dosyasi_yolu().stat().st_size
        except FileNotFoundError:
            return 0

    def log_dosyalarini_listele(self) -> list:
        """
        Tüm log dosyalarını listeler
        
        Returns:
            Log dosyaları listesi
        """
        log_dosyalari = []
        
        # Ana log dosyası
        ana_dosya = self.log_dosyasi_yolu()
        if ana_dosya.exists():
            log_dosyalari.append({
                'dosya': ana_dosya.name,
                'yol': str(ana_dosya),
                'boyut': ana_dosya.stat().st_size,
                'degistirilme_tarihi': datetime.fromtimestamp(ana_dosya.stat().st_mtime)
            })
        
        # Döndürülmüş log dosyaları
        for i in range(1, self.log_dosya_sayisi + 1):
            dosya_yolu = self.log_klasoru / f"{self.dosya_adi}.log.{i}"
            if dosya_yolu.exists():
                log_dosyalari.append({
                    'dosya': dosya_yolu.name,
                    'yol': str(dosya_yolu),
                    'boyut': dosya_yolu.stat().st_size,
                    'degistirilme_tarihi': datetime.fromtimestamp(dosya_yolu.stat().st_mtime)
                })
        
        return sorted(log_dosyalari, key=lambda x: x['degistirilme_tarihi'], reverse=True)

    def log_istatistikleri(self) -> Dict[str, Any]:
        """
        Log sistemi istatistiklerini döndürür
        
        Returns:
            İstatistik bilgileri
        """
        dosyalar = self.log_dosyalarini_listele()
        toplam_boyut = sum(d['boyut'] for d in dosyalar)
        
        return {
            'log_seviyesi': self.log_seviyesi,
            'log_klasoru': str(self.log_klasoru),
            'dosya_sayisi': len(dosyalar),
            'toplam_boyut': toplam_boyut,
            'maksimum_dosya_boyutu': self.log_dosya_boyutu,
            'maksimum_dosya_sayisi': self.log_dosya_sayisi,
            'aktif_dosya_boyutu': self.log_dosyasi_boyutu()
        }

    def log_temizle(self, gun_sayisi: int = 30) -> int:
        """
        Belirtilen günden eski log dosyalarını temizler
        
        Args:
            gun_sayisi: Kaç günden eski dosyalar silinecek
            
        Returns:
            Silinen dosya sayısı
        """
        silinen_sayisi = 0
        simdi = datetime.now()
        
        for dosya_info in self.log_dosyalarini_listele():
            dosya_yolu = Path(dosya_info['yol'])
            dosya_tarihi = dosya_info['degistirilme_tarihi']
            
            if (simdi - dosya_tarihi).days > gun_sayisi:
                try:
                    dosya_yolu.unlink()
                    silinen_sayisi += 1
                    self.info(f"Eski log dosyası silindi: {dosya_yolu.name}")
                except Exception as e:
                    self.error(f"Log dosyası silinemedi {dosya_yolu.name}: {e}")
        
        return silinen_sayisi

    def sistem_bilgisi_logla(self) -> None:
        """Sistem bilgilerini loglar"""
        self.info("=== SONTECHSP Sistem Bilgileri ===")
        self.info(f"Python sürümü: {sys.version}")
        self.info(f"Platform: {sys.platform}")
        self.info(f"Çalışma dizini: {os.getcwd()}")
        self.info(f"Log klasörü: {self.log_klasoru}")
        self.info(f"Log seviyesi: {self.log_seviyesi}")
        self.info("=== Sistem Bilgileri Sonu ===")

    def __del__(self):
        """Kaynak temizliği"""
        if self._logger:
            # Handler'ları temizle
            for handler in self._logger.handlers[:]:
                handler.close()
                self._logger.removeHandler(handler)


# Global kayıt sistemi instance
_kayit_sistemi: Optional[KayitSistemi] = None


def kayit_sistemi_al() -> KayitSistemi:
    """Global kayıt sistemi instance'ını döndürür"""
    global _kayit_sistemi
    if _kayit_sistemi is None:
        _kayit_sistemi = KayitSistemi()
    return _kayit_sistemi