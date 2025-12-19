# Version: 0.1.0
# Last Update: 2024-12-18
# Module: klavye_kisayol_yoneticisi
# Description: POS klavye kısayol yönetimi
# Changelog:
# - İlk oluşturma - Klavye kısayol sistemi

"""
Klavye Kısayol Yöneticisi

POS ekranı için klavye kısayollarını yönetir.
Global ve bileşen bazlı kısayolları destekler.

Sorumluluklar:
- Klavye olaylarını yakalama
- Kısayol tanımlama ve yönetimi
- Kısayol çakışma kontrolü
- Bileşenlere kısayol yönlendirme
"""

from typing import Dict, Callable, Optional
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtGui import QKeyEvent

from sontechsp.uygulama.cekirdek.kayit import kayit_al


class KlavyeKisayolYoneticisi(QObject):
    """
    Klavye Kısayol Yöneticisi

    POS ekranı için klavye kısayollarını yönetir.
    """

    # Sinyal: Kısayol tetiklendiğinde
    kisayol_tetiklendi = pyqtSignal(str)  # Kısayol adı

    def __init__(self):
        super().__init__()
        self.logger = kayit_al("klavye_kisayol_yoneticisi")

        # Kısayol tanımları: {tus_kombinasyonu: (kisayol_adi, aciklama)}
        self._kisayollar: Dict[str, tuple] = {}

        # Kısayol handler'ları: {kisayol_adi: handler_fonksiyonu}
        self._handler_lar: Dict[str, Callable] = {}

        # Varsayılan kısayolları tanımla
        self._varsayilan_kisayollari_tanimla()

        self.logger.info("Klavye kısayol yöneticisi oluşturuldu")

    def _varsayilan_kisayollari_tanimla(self):
        """Varsayılan POS kısayollarını tanımlar"""
        # F2: Barkod alanına odaklan
        self.kisayol_ekle(Qt.Key.Key_F2, "barkod_odakla", "Barkod alanına odaklan")

        # F4: Nakit ödeme
        self.kisayol_ekle(Qt.Key.Key_F4, "nakit_odeme", "Nakit ödeme başlat")

        # F5: Kart ödeme
        self.kisayol_ekle(Qt.Key.Key_F5, "kart_odeme", "Kart ödeme başlat")

        # ESC: İşlem iptal
        self.kisayol_ekle(Qt.Key.Key_Escape, "islem_iptal", "İşlemi iptal et")

        # Delete: Satır sil
        self.kisayol_ekle(Qt.Key.Key_Delete, "satir_sil", "Seçili satırı sil")

        # F6: Beklet
        self.kisayol_ekle(Qt.Key.Key_F6, "sepet_beklet", "Sepeti beklet")

        # F7: Bekleyenler
        self.kisayol_ekle(Qt.Key.Key_F7, "bekleyenler_goster", "Bekletilen sepetleri göster")

        # F8: İade
        self.kisayol_ekle(Qt.Key.Key_F8, "iade_baslat", "İade işlemi başlat")

        # F9: Fiş yazdır
        self.kisayol_ekle(Qt.Key.Key_F9, "fis_yazdir", "Fiş yazdır")

        # F10: Fatura
        self.kisayol_ekle(Qt.Key.Key_F10, "fatura_olustur", "Fatura oluştur")

    def kisayol_ekle(self, tus: Qt.Key, kisayol_adi: str, aciklama: str = "") -> bool:
        """
        Yeni kısayol ekler

        Args:
            tus: Tuş kodu
            kisayol_adi: Kısayol adı
            aciklama: Kısayol açıklaması

        Returns:
            bool: Başarılı ise True
        """
        tus_str = self._tus_string_olustur(tus)

        # Çakışma kontrolü
        if tus_str in self._kisayollar:
            self.logger.warning(f"Kısayol çakışması: {tus_str} zaten tanımlı")
            return False

        self._kisayollar[tus_str] = (kisayol_adi, aciklama)
        self.logger.debug(f"Kısayol eklendi: {tus_str} -> {kisayol_adi}")

        return True

    def kisayol_cikar(self, tus: Qt.Key) -> bool:
        """
        Kısayol çıkarır

        Args:
            tus: Tuş kodu

        Returns:
            bool: Başarılı ise True
        """
        tus_str = self._tus_string_olustur(tus)

        if tus_str in self._kisayollar:
            kisayol_adi = self._kisayollar[tus_str][0]
            del self._kisayollar[tus_str]

            # Handler'ı da çıkar
            if kisayol_adi in self._handler_lar:
                del self._handler_lar[kisayol_adi]

            self.logger.debug(f"Kısayol çıkarıldı: {tus_str}")
            return True

        return False

    def handler_bagla(self, kisayol_adi: str, handler: Callable):
        """
        Kısayola handler bağlar

        Args:
            kisayol_adi: Kısayol adı
            handler: Handler fonksiyonu
        """
        self._handler_lar[kisayol_adi] = handler
        self.logger.debug(f"Handler bağlandı: {kisayol_adi}")

    def handler_ayir(self, kisayol_adi: str):
        """
        Kısayoldan handler ayırır

        Args:
            kisayol_adi: Kısayol adı
        """
        if kisayol_adi in self._handler_lar:
            del self._handler_lar[kisayol_adi]
            self.logger.debug(f"Handler ayrıldı: {kisayol_adi}")

    def olay_isle(self, event: QKeyEvent) -> bool:
        """
        Klavye olayını işler

        Args:
            event: Klavye olayı

        Returns:
            bool: Olay işlendiyse True
        """
        tus_str = self._tus_string_olustur(event.key(), event.modifiers())

        if tus_str in self._kisayollar:
            kisayol_adi, _ = self._kisayollar[tus_str]

            # Handler varsa çağır
            if kisayol_adi in self._handler_lar:
                try:
                    self._handler_lar[kisayol_adi]()
                except Exception as e:
                    self.logger.error(f"Kısayol handler hatası ({kisayol_adi}): {e}")

            # Sinyal gönder
            self.kisayol_tetiklendi.emit(kisayol_adi)

            self.logger.debug(f"Kısayol tetiklendi: {kisayol_adi}")
            return True

        return False

    def _tus_string_olustur(self, tus: Qt.Key, modifier: Qt.KeyboardModifier = None) -> str:
        """
        Tuş kombinasyonundan string oluşturur

        Args:
            tus: Tuş kodu
            modifier: Modifier tuşları

        Returns:
            str: Tuş string'i
        """
        parts = []

        if modifier:
            if modifier & Qt.KeyboardModifier.ControlModifier:
                parts.append("Ctrl")
            if modifier & Qt.KeyboardModifier.AltModifier:
                parts.append("Alt")
            if modifier & Qt.KeyboardModifier.ShiftModifier:
                parts.append("Shift")

        # Tuş adını ekle
        if isinstance(tus, Qt.Key):
            tus_adi = tus.name.replace("Key_", "")
        else:
            tus_adi = str(tus)

        parts.append(tus_adi)

        return "+".join(parts)

    def kisayollari_listele(self) -> Dict[str, tuple]:
        """
        Tanımlı kısayolları listeler

        Returns:
            Dict: {tus_kombinasyonu: (kisayol_adi, aciklama)}
        """
        return self._kisayollar.copy()

    def kisayol_var_mi(self, tus: Qt.Key) -> bool:
        """
        Kısayol tanımlı mı kontrol eder

        Args:
            tus: Tuş kodu

        Returns:
            bool: Tanımlı ise True
        """
        tus_str = self._tus_string_olustur(tus)
        return tus_str in self._kisayollar

    def kisayol_bilgisi_al(self, tus: Qt.Key) -> Optional[tuple]:
        """
        Kısayol bilgisini döndürür

        Args:
            tus: Tuş kodu

        Returns:
            Optional[tuple]: (kisayol_adi, aciklama) veya None
        """
        tus_str = self._tus_string_olustur(tus)
        return self._kisayollar.get(tus_str)
