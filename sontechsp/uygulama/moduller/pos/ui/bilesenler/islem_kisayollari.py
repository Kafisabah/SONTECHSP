# Version: 0.1.0
# Last Update: 2024-12-18
# Module: islem_kisayollari
# Description: POS işlem kısayolları paneli
# Changelog:
# - İlk oluşturma - İşlem kısayolları paneli bileşeni

"""
İşlem Kısayolları Paneli

POS ekranında işlem kısayolları için buton paneli.
BEKLET, BEKLEYENLER, İADE, İPTAL, FİŞ YAZDIR, FATURA butonları.

Sorumluluklar:
- İşlem butonlarını gösterme
- Buton tıklama olaylarını yönetme
- Sinyal gönderme
- Buton durumlarını yönetme
"""

from typing import Dict, Any, Optional
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from .pos_bilesen_arayuzu import POSBilesenWidget
from ..handlers.pos_sinyalleri import POSSinyalleri


class IslemKisayollari(POSBilesenWidget):
    """
    İşlem Kısayolları Paneli

    POS işlem kısayolları için buton paneli.
    """

    # Sinyaller
    beklet_tiklandi = pyqtSignal()
    bekleyenler_tiklandi = pyqtSignal()
    iade_tiklandi = pyqtSignal()
    iptal_tiklandi = pyqtSignal()
    fis_yazdir_tiklandi = pyqtSignal()
    fatura_tiklandi = pyqtSignal()

    def __init__(self, sinyaller: POSSinyalleri, parent=None):
        super().__init__(parent)
        self._sinyaller = sinyaller
        self._butonlar: Dict[str, QPushButton] = {}
        self._sepet_bos = True
        self._satis_tamamlandi = False
        self._ui_kur()

    def _ui_kur(self):
        """UI bileşenlerini kurar"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)

        # Başlık
        baslik = QLabel("İşlem Kısayolları")
        baslik.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(baslik)

        # Ayırıcı çizgi
        ayirici = QFrame()
        ayirici.setFrameShape(QFrame.Shape.HLine)
        ayirici.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(ayirici)

        # İlk satır butonları
        ilk_satir = QHBoxLayout()
        ilk_satir.setSpacing(5)

        self._butonlar["beklet"] = self._buton_olustur("BEKLET", "F6")
        self._butonlar["bekleyenler"] = self._buton_olustur("BEKLEYENLER", "F7")
        self._butonlar["iade"] = self._buton_olustur("İADE", "F8")

        ilk_satir.addWidget(self._butonlar["beklet"])
        ilk_satir.addWidget(self._butonlar["bekleyenler"])
        ilk_satir.addWidget(self._butonlar["iade"])

        layout.addLayout(ilk_satir)

        # İkinci satır butonları
        ikinci_satir = QHBoxLayout()
        ikinci_satir.setSpacing(5)

        self._butonlar["iptal"] = self._buton_olustur("İPTAL", "ESC")
        self._butonlar["fis_yazdir"] = self._buton_olustur("FİŞ YAZDIR", "F9")
        self._butonlar["fatura"] = self._buton_olustur("FATURA", "F10")

        ikinci_satir.addWidget(self._butonlar["iptal"])
        ikinci_satir.addWidget(self._butonlar["fis_yazdir"])
        ikinci_satir.addWidget(self._butonlar["fatura"])

        layout.addLayout(ikinci_satir)

        # Sinyalleri bağla
        self._sinyalleri_bagla()

        # Başlangıç durumu
        self._buton_durumlarini_guncelle()

    def _buton_olustur(self, metin: str, kisayol: str) -> QPushButton:
        """
        İşlem butonu oluşturur

        Args:
            metin: Buton metni
            kisayol: Klavye kısayolu

        Returns:
            QPushButton: Oluşturulan buton
        """
        buton = QPushButton(f"{metin}\n({kisayol})")
        buton.setMinimumHeight(50)
        buton.setFont(QFont("Arial", 9))
        buton.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        return buton

    def _sinyalleri_bagla(self):
        """Buton sinyallerini bağlar"""
        self._butonlar["beklet"].clicked.connect(self.beklet_tiklandi.emit)
        self._butonlar["bekleyenler"].clicked.connect(self.bekleyenler_tiklandi.emit)
        self._butonlar["iade"].clicked.connect(self.iade_tiklandi.emit)
        self._butonlar["iptal"].clicked.connect(self.iptal_tiklandi.emit)
        self._butonlar["fis_yazdir"].clicked.connect(self.fis_yazdir_tiklandi.emit)
        self._butonlar["fatura"].clicked.connect(self.fatura_tiklandi.emit)

    def _buton_durumlarini_guncelle(self):
        """Buton durumlarını günceller"""
        # BEKLET: Sepet boş değilse aktif
        self._butonlar["beklet"].setEnabled(not self._sepet_bos)

        # BEKLEYENLER: Her zaman aktif
        self._butonlar["bekleyenler"].setEnabled(True)

        # İADE: Her zaman aktif
        self._butonlar["iade"].setEnabled(True)

        # İPTAL: Sepet boş değilse aktif
        self._butonlar["iptal"].setEnabled(not self._sepet_bos)

        # FİŞ YAZDIR: Satış tamamlandıysa aktif
        self._butonlar["fis_yazdir"].setEnabled(self._satis_tamamlandi)

        # FATURA: Satış tamamlandıysa aktif
        self._butonlar["fatura"].setEnabled(self._satis_tamamlandi)

    def baslat(self) -> None:
        """Bileşeni başlatır"""
        super().baslat()
        self._sepet_bos = True
        self._satis_tamamlandi = False
        self._buton_durumlarini_guncelle()

    def temizle(self) -> None:
        """Bileşeni temizler"""
        super().temizle()
        self._sepet_bos = True
        self._satis_tamamlandi = False
        self._buton_durumlarini_guncelle()

    def guncelle(self, veri: Dict[str, Any]) -> None:
        """
        Bileşeni günceller

        Args:
            veri: Güncelleme verisi
                - sepet_bos: bool - Sepet boş mu
                - satis_tamamlandi: bool - Satış tamamlandı mı
        """
        if "sepet_bos" in veri:
            self._sepet_bos = veri["sepet_bos"]

        if "satis_tamamlandi" in veri:
            self._satis_tamamlandi = veri["satis_tamamlandi"]

        self._buton_durumlarini_guncelle()

    def klavye_kisayolu_isle(self, tus: str) -> bool:
        """
        Klavye kısayolunu işler

        Args:
            tus: Basılan tuş

        Returns:
            bool: Kısayol işlendiyse True
        """
        kisayol_map = {
            "F6": "beklet",
            "F7": "bekleyenler",
            "F8": "iade",
            "Escape": "iptal",
            "F9": "fis_yazdir",
            "F10": "fatura",
        }

        if tus in kisayol_map:
            buton_adi = kisayol_map[tus]
            buton = self._butonlar[buton_adi]

            if buton.isEnabled():
                buton.click()
                return True

        return False

    def sepet_durumu_ayarla(self, bos: bool):
        """
        Sepet durumunu ayarlar

        Args:
            bos: Sepet boş mu
        """
        self._sepet_bos = bos
        self._buton_durumlarini_guncelle()

    def satis_durumu_ayarla(self, tamamlandi: bool):
        """
        Satış durumunu ayarlar

        Args:
            tamamlandi: Satış tamamlandı mı
        """
        self._satis_tamamlandi = tamamlandi
        self._buton_durumlarini_guncelle()

    def buton_al(self, buton_adi: str) -> Optional[QPushButton]:
        """
        Belirtilen butonu döndürür

        Args:
            buton_adi: Buton adı

        Returns:
            QPushButton: Buton referansı
        """
        return self._butonlar.get(buton_adi)

    def buton_aktif_mi(self, buton_adi: str) -> bool:
        """
        Butonun aktif olup olmadığını kontrol eder

        Args:
            buton_adi: Buton adı

        Returns:
            bool: Buton aktifse True
        """
        buton = self._butonlar.get(buton_adi)
        return buton.isEnabled() if buton else False
