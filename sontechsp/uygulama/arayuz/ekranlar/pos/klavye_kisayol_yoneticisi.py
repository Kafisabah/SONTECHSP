# Version: 0.1.0
# Last Update: 2024-12-19
# Module: klavye_kisayol_yoneticisi
# Description: POS klavye kısayol yönetimi
# Changelog:
# - İlk oluşturma - POS klavye kısayol sistemi

"""
Klavye Kısayol Yöneticisi

POS ekranı için klavye kısayollarını yönetir.
Global ve bileşen bazlı kısayolları destekler.
"""

from typing import Dict, Callable, Optional
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QWidget


class KlavyeKisayolYoneticisi(QObject):
    """
    Klavye Kısayol Yöneticisi

    POS ekranı için klavye kısayollarını yönetir.
    """

    # Sinyal: Kısayol tetiklendiğinde
    kisayol_tetiklendi = pyqtSignal(str)  # Kısayol adı

    def __init__(self, parent_widget: QWidget):
        super().__init__()
        self.parent_widget = parent_widget

        # Kısayol tanımları: {tus_kodu: (kisayol_adi, handler_fonksiyonu)}
        self._kisayollar: Dict[int, tuple] = {}

        # Varsayılan kısayolları tanımla
        self._varsayilan_kisayollari_tanimla()

    def _varsayilan_kisayollari_tanimla(self):
        """Varsayılan POS kısayollarını tanımlar"""
        # F2: Barkod alanına odaklan
        self.kisayol_ekle(Qt.Key.Key_F2, "barkod_odakla", None)

        # F4-F7: Ödeme türleri
        self.kisayol_ekle(Qt.Key.Key_F4, "nakit_odeme", None)
        self.kisayol_ekle(Qt.Key.Key_F5, "kart_odeme", None)
        self.kisayol_ekle(Qt.Key.Key_F6, "parcali_odeme", None)
        self.kisayol_ekle(Qt.Key.Key_F7, "acik_hesap_odeme", None)

        # F8-F10: İşlem kısayolları
        self.kisayol_ekle(Qt.Key.Key_F8, "sepet_beklet", None)
        self.kisayol_ekle(Qt.Key.Key_F9, "bekleyenler_goster", None)
        self.kisayol_ekle(Qt.Key.Key_F10, "iade_islemi", None)

        # ESC: İptal
        self.kisayol_ekle(Qt.Key.Key_Escape, "islem_iptal", None)

        # DEL: Satır sil
        self.kisayol_ekle(Qt.Key.Key_Delete, "satir_sil", None)

        # +/-: Adet değiştir
        self.kisayol_ekle(Qt.Key.Key_Plus, "adet_artir", None)
        self.kisayol_ekle(Qt.Key.Key_Minus, "adet_azalt", None)

    def kisayol_ekle(self, tus: Qt.Key, kisayol_adi: str, handler: Optional[Callable] = None):
        """
        Yeni kısayol ekler

        Args:
            tus: Tuş kodu
            kisayol_adi: Kısayol adı
            handler: Handler fonksiyonu (opsiyonel)
        """
        self._kisayollar[tus] = (kisayol_adi, handler)

    def handler_bagla(self, kisayol_adi: str, handler: Callable):
        """
        Kısayola handler bağlar

        Args:
            kisayol_adi: Kısayol adı
            handler: Handler fonksiyonu
        """
        for tus, (adi, _) in self._kisayollar.items():
            if adi == kisayol_adi:
                self._kisayollar[tus] = (adi, handler)
                break

    def olay_isle(self, event: QKeyEvent) -> bool:
        """
        Klavye olayını işler

        Args:
            event: Klavye olayı

        Returns:
            bool: Olay işlendiyse True, aksi halde False
        """
        key = event.key()

        # Modifier tuşları varsa işleme
        if event.modifiers() != Qt.KeyboardModifier.NoModifier:
            return False

        # Kısayol tanımlı mı kontrol et
        if key in self._kisayollar:
            kisayol_adi, handler = self._kisayollar[key]

            # Handler varsa çağır
            if handler:
                try:
                    handler()
                except Exception as e:
                    print(f"Kısayol handler hatası ({kisayol_adi}): {e}")

            # Sinyal gönder
            self.kisayol_tetiklendi.emit(kisayol_adi)
            return True

        return False

    def kisayol_var_mi(self, tus: Qt.Key) -> bool:
        """
        Kısayol tanımlı mı kontrol eder

        Args:
            tus: Tuş kodu

        Returns:
            bool: Tanımlı ise True
        """
        return tus in self._kisayollar

    def kisayollari_listele(self) -> Dict[int, tuple]:
        """
        Tanımlı kısayolları listeler

        Returns:
            Dict: {tus_kodu: (kisayol_adi, handler)}
        """
        return self._kisayollar.copy()
