# Version: 0.3.1
# Last Update: 2025-12-18
# Module: buton_eslestirme_kaydi
# Description: UI buton eşleştirme kayıt sistemi - thread-safe veri modeli ve kayıt yönetimi
# Changelog:
# - İlk versiyon: ButonEslestirme dataclass ve thread-safe kayıt listesi
# - CSV export desteği eklendi
# - CSV dosyasına kaydetme fonksiyonu eklendi
# - Kod analizi ve iyileştirme yapıldı

import csv
import io
from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from typing import Any, Dict, List, Optional


@dataclass
class ButonEslestirme:
    """Buton eşleştirme veri modeli"""

    ekran_adi: str
    buton_adi: str
    handler_adi: str
    servis_metodu: Optional[str] = None
    kayit_zamani: datetime = field(default_factory=datetime.now)
    cagrilma_sayisi: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Kayıt verilerini sözlük formatında döndür"""
        return {
            "ekran_adi": self.ekran_adi,
            "buton_adi": self.buton_adi,
            "handler_adi": self.handler_adi,
            "servis_metodu": self.servis_metodu,
            "kayit_zamani": self.kayit_zamani.isoformat(),
            "cagrilma_sayisi": self.cagrilma_sayisi,
        }


class ButonEslestirmeKayitSistemi:
    """Thread-safe buton eşleştirme kayıt sistemi"""

    def __init__(self):
        self._kayitlar: List[ButonEslestirme] = []
        self._lock = Lock()

    def kayit_ekle(self, ekran_adi: str, buton_adi: str, handler_adi: str, servis_metodu: Optional[str] = None) -> None:
        """
        Yeni buton eşleştirmesi kaydet

        Args:
            ekran_adi: Ekranın adı
            buton_adi: Butonun adı
            handler_adi: Handler fonksiyonunun adı
            servis_metodu: Çağrılan servis metodunun adı (opsiyonel)
        """
        with self._lock:
            yeni_kayit = ButonEslestirme(
                ekran_adi=ekran_adi, buton_adi=buton_adi, handler_adi=handler_adi, servis_metodu=servis_metodu
            )
            self._kayitlar.append(yeni_kayit)

    def kayitlari_listele(self) -> List[Dict[str, Any]]:
        """
        Tüm kayıtları yapılandırılmış formatta döndür

        Returns:
            Kayıtların sözlük listesi
        """
        with self._lock:
            return [kayit.to_dict() for kayit in self._kayitlar]

    def kayitlari_temizle(self) -> None:
        """Tüm kayıtları temizle"""
        with self._lock:
            self._kayitlar.clear()

    def kayit_sayisi(self) -> int:
        """Toplam kayıt sayısını döndür"""
        with self._lock:
            return len(self._kayitlar)

    def tablo_formatinda_cikti(self) -> str:
        """Kayıtları tablo formatında string olarak döndür"""
        with self._lock:
            if not self._kayitlar:
                return "Henüz kayıt bulunmuyor."

            # Başlık satırı
            baslik = f"{'Ekran':<20} {'Buton':<20} {'Handler':<25} {'Servis':<25} {'Zaman':<20}"
            ayirici = "-" * 110

            satirlar = [baslik, ayirici]

            for kayit in self._kayitlar:
                satir = (
                    f"{kayit.ekran_adi:<20} "
                    f"{kayit.buton_adi:<20} "
                    f"{kayit.handler_adi:<25} "
                    f"{kayit.servis_metodu or 'N/A':<25} "
                    f"{kayit.kayit_zamani.strftime('%H:%M:%S'):<20}"
                )
                satirlar.append(satir)

            return "\n".join(satirlar)

    def csv_formatinda_cikti(self) -> str:
        """Kayıtları CSV formatında string olarak döndür"""
        with self._lock:
            if not self._kayitlar:
                return "Ekran,Buton,Handler,Servis,Zaman,Cagrilma_Sayisi\n"

            output = io.StringIO()
            writer = csv.writer(output)

            # Başlık satırı
            writer.writerow(["Ekran", "Buton", "Handler", "Servis", "Zaman", "Cagrilma_Sayisi"])

            # Veri satırları
            for kayit in self._kayitlar:
                writer.writerow(
                    [
                        kayit.ekran_adi,
                        kayit.buton_adi,
                        kayit.handler_adi,
                        kayit.servis_metodu or "",
                        kayit.kayit_zamani.isoformat(),
                        kayit.cagrilma_sayisi,
                    ]
                )

            return output.getvalue()

    def csv_dosyasina_kaydet(self, dosya_yolu: str) -> bool:
        """Kayıtları CSV dosyasına kaydet"""
        try:
            with open(dosya_yolu, "w", newline="", encoding="utf-8") as dosya:
                dosya.write(self.csv_formatinda_cikti())
            return True
        except Exception:
            return False


# Global singleton instance
_kayit_sistemi = ButonEslestirmeKayitSistemi()


def kayit_ekle(ekran_adi: str, buton_adi: str, handler_adi: str, servis_metodu: Optional[str] = None) -> None:
    """Global kayıt ekleme fonksiyonu"""
    _kayit_sistemi.kayit_ekle(ekran_adi, buton_adi, handler_adi, servis_metodu)


def kayitlari_listele() -> List[Dict[str, Any]]:
    """Global kayıt listeleme fonksiyonu"""
    return _kayit_sistemi.kayitlari_listele()


def kayitlari_temizle() -> None:
    """Global kayıt temizleme fonksiyonu"""
    _kayit_sistemi.kayitlari_temizle()


def tablo_formatinda_cikti() -> str:
    """Global tablo formatı çıktı fonksiyonu"""
    return _kayit_sistemi.tablo_formatinda_cikti()


def kayit_sayisi() -> int:
    """Global kayıt sayısı fonksiyonu"""
    return _kayit_sistemi.kayit_sayisi()


def csv_formatinda_cikti() -> str:
    """Global CSV formatı çıktı fonksiyonu"""
    return _kayit_sistemi.csv_formatinda_cikti()


def csv_dosyasina_kaydet(dosya_yolu: str) -> bool:
    """Global CSV dosyasına kaydetme fonksiyonu"""
    return _kayit_sistemi.csv_dosyasina_kaydet(dosya_yolu)
