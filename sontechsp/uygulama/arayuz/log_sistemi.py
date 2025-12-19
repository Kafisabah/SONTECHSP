# Version: 0.1.0
# Last Update: 2024-12-18
# Module: log_sistemi
# Description: UI smoke test log sistemi - handler ve stub servis loglama
# Changelog:
# - İlk versiyon: LogKaydi dataclass ve log yapılandırması

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional


class LogSeviyesi(Enum):
    """Log seviyesi enum"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LogDurumu(Enum):
    """Log durum enum"""

    BASARILI = "basarili"
    HATA = "hata"
    STUB = "stub"


@dataclass
class LogKaydi:
    """Log kaydı veri modeli"""

    zaman: datetime
    ekran_adi: str
    buton_adi: str
    handler_adi: str
    durum: LogDurumu
    servis_metodu: Optional[str] = None
    detay: Optional[str] = None
    log_seviyesi: LogSeviyesi = LogSeviyesi.INFO

    def to_dict(self) -> Dict[str, Any]:
        """Log kaydını sözlük formatında döndür"""
        return {
            "zaman": self.zaman.isoformat(),
            "ekran_adi": self.ekran_adi,
            "buton_adi": self.buton_adi,
            "handler_adi": self.handler_adi,
            "servis_metodu": self.servis_metodu,
            "durum": self.durum.value,
            "detay": self.detay,
            "log_seviyesi": self.log_seviyesi.value,
        }

    def format_mesaj(self) -> str:
        """Log kaydını formatlanmış mesaj olarak döndür"""
        zaman_str = self.zaman.strftime("%H:%M:%S.%f")[:-3]  # milisaniye hassasiyeti

        temel_mesaj = (
            f"[{zaman_str}] {self.log_seviyesi.value} - "
            f"Ekran: {self.ekran_adi} | "
            f"Buton: {self.buton_adi} | "
            f"Handler: {self.handler_adi}"
        )

        if self.servis_metodu:
            temel_mesaj += f" | Servis: {self.servis_metodu}"

        temel_mesaj += f" | Durum: {self.durum.value}"

        if self.detay:
            temel_mesaj += f" | Detay: {self.detay}"

        return temel_mesaj


class LogYapilandirmasi:
    """Log sistemi yapılandırması"""

    def __init__(self):
        self.log_seviyesi = LogSeviyesi.INFO
        self.dosya_loglama_aktif = True
        self.konsol_loglama_aktif = True
        self.log_dosya_yolu = self._varsayilan_log_yolu()
        self.maksimum_dosya_boyutu = 10 * 1024 * 1024  # 10MB
        self.yedek_dosya_sayisi = 5

    def _varsayilan_log_yolu(self) -> Path:
        """Varsayılan log dosya yolunu belirle"""
        # logs klasörü yoksa oluştur
        log_klasoru = Path("logs")
        log_klasoru.mkdir(exist_ok=True)

        return log_klasoru / "ui_smoke_test.log"

    def log_dosya_yolunu_ayarla(self, yol: str) -> None:
        """Log dosya yolunu ayarla"""
        self.log_dosya_yolu = Path(yol)
        # Klasör yoksa oluştur
        self.log_dosya_yolu.parent.mkdir(parents=True, exist_ok=True)


class UISmokeTestLogger:
    """UI Smoke Test için özelleştirilmiş logger"""

    def __init__(self, yapilandirma: Optional[LogYapilandirmasi] = None):
        self.yapilandirma = yapilandirma or LogYapilandirmasi()
        self._log_kayitlari: List[LogKaydi] = []
        self._lock = Lock()
        self._logger = self._logger_olustur()

    def _logger_olustur(self) -> logging.Logger:
        """Python logging modülü ile logger oluştur"""
        logger = logging.getLogger("ui_smoke_test")
        logger.setLevel(getattr(logging, self.yapilandirma.log_seviyesi.value))

        # Mevcut handler'ları temizle
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Dosya handler ekle
        if self.yapilandirma.dosya_loglama_aktif:
            from logging.handlers import RotatingFileHandler

            dosya_handler = RotatingFileHandler(
                self.yapilandirma.log_dosya_yolu,
                maxBytes=self.yapilandirma.maksimum_dosya_boyutu,
                backupCount=self.yapilandirma.yedek_dosya_sayisi,
                encoding="utf-8",
            )

            dosya_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
            dosya_handler.setFormatter(dosya_formatter)
            logger.addHandler(dosya_handler)

        # Konsol handler ekle
        if self.yapilandirma.konsol_loglama_aktif:
            konsol_handler = logging.StreamHandler()
            konsol_formatter = logging.Formatter("%(levelname)s - %(message)s")
            konsol_handler.setFormatter(konsol_formatter)
            logger.addHandler(konsol_handler)

        return logger

    def log_kaydi_ekle(self, log_kaydi: LogKaydi) -> None:
        """Yeni log kaydı ekle"""
        with self._lock:
            self._log_kayitlari.append(log_kaydi)

            # Python logging modülü ile de logla
            mesaj = log_kaydi.format_mesaj()
            log_level = getattr(logging, log_kaydi.log_seviyesi.value)
            self._logger.log(log_level, mesaj)

    def handler_loglama(
        self,
        ekran_adi: str,
        buton_adi: str,
        handler_adi: str,
        servis_metodu: Optional[str] = None,
        durum: LogDurumu = LogDurumu.BASARILI,
        detay: Optional[str] = None,
    ) -> None:
        """Handler çalıştığında log yaz"""
        log_kaydi = LogKaydi(
            zaman=datetime.now(),
            ekran_adi=ekran_adi,
            buton_adi=buton_adi,
            handler_adi=handler_adi,
            servis_metodu=servis_metodu,
            durum=durum,
            detay=detay,
            log_seviyesi=LogSeviyesi.INFO,
        )
        self.log_kaydi_ekle(log_kaydi)

    def stub_servis_loglama(
        self, ekran_adi: str, buton_adi: str, handler_adi: str, servis_metodu: str, detay: Optional[str] = None
    ) -> None:
        """Stub servis çağrıldığında log yaz"""
        log_kaydi = LogKaydi(
            zaman=datetime.now(),
            ekran_adi=ekran_adi,
            buton_adi=buton_adi,
            handler_adi=handler_adi,
            servis_metodu=servis_metodu,
            durum=LogDurumu.STUB,
            detay=detay if detay is not None else "stub çağrıldı",
            log_seviyesi=LogSeviyesi.INFO,
        )
        self.log_kaydi_ekle(log_kaydi)

    def log_kayitlarini_listele(self) -> List[Dict[str, Any]]:
        """Tüm log kayıtlarını listele"""
        with self._lock:
            return [kayit.to_dict() for kayit in self._log_kayitlari]

    def log_kayitlarini_temizle(self) -> None:
        """Tüm log kayıtlarını temizle"""
        with self._lock:
            self._log_kayitlari.clear()

    def log_sayisi(self) -> int:
        """Toplam log sayısını döndür"""
        with self._lock:
            return len(self._log_kayitlari)


# Global singleton instance
_varsayilan_yapilandirma = LogYapilandirmasi()
_logger_instance = UISmokeTestLogger(_varsayilan_yapilandirma)


def handler_loglama(
    ekran_adi: str,
    buton_adi: str,
    handler_adi: str,
    servis_metodu: Optional[str] = None,
    durum: LogDurumu = LogDurumu.BASARILI,
    detay: Optional[str] = None,
) -> None:
    """Global handler loglama fonksiyonu"""
    _logger_instance.handler_loglama(ekran_adi, buton_adi, handler_adi, servis_metodu, durum, detay)


def stub_servis_loglama(
    ekran_adi: str, buton_adi: str, handler_adi: str, servis_metodu: str, detay: Optional[str] = None
) -> None:
    """Global stub servis loglama fonksiyonu"""
    _logger_instance.stub_servis_loglama(ekran_adi, buton_adi, handler_adi, servis_metodu, detay)


def log_kayitlarini_listele() -> List[Dict[str, Any]]:
    """Global log kayıtları listeleme fonksiyonu"""
    return _logger_instance.log_kayitlarini_listele()


def log_kayitlarini_temizle() -> None:
    """Global log kayıtları temizleme fonksiyonu"""
    _logger_instance.log_kayitlarini_temizle()


def log_sayisi() -> int:
    """Global log sayısı fonksiyonu"""
    return _logger_instance.log_sayisi()


def log_yapilandirmasini_ayarla(yapilandirma: LogYapilandirmasi) -> None:
    """Global log yapılandırmasını ayarla"""
    global _logger_instance
    _logger_instance = UISmokeTestLogger(yapilandirma)
