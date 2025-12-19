# Version: 0.1.0
# Last Update: 2024-12-19
# Module: hizli_islem_seridi
# Description: POS alt şerit hızlı işlem butonları
# Changelog:
# - İlk oluşturma

"""
Hızlı İşlem Şeridi - POS alt şerit butonları
"""

from typing import Optional
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal
from .turkuaz_tema import TurkuazTema


class HizliIslemSeridi(QWidget):
    """POS hızlı işlem şeridi widget'ı"""

    beklet_basildi = pyqtSignal()
    bekleyenler_basildi = pyqtSignal()
    iade_basildi = pyqtSignal()
    iptal_basildi = pyqtSignal()
    fis_yazdir_basildi = pyqtSignal()
    fatura_basildi = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.tema = TurkuazTema()
        self.setupUI()

    def setupUI(self):
        """UI bileşenlerini oluşturur"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        # Hızlı işlem butonları
        self.beklet_btn = self.buton_olustur("BEKLET\nF8", self.beklet_basildi)
        self.bekleyenler_btn = self.buton_olustur("BEKLEYENLER\nF9", self.bekleyenler_basildi)
        self.iade_btn = self.buton_olustur("İADE\nF10", self.iade_basildi)
        self.iptal_btn = self.buton_olustur("İPTAL\nESC", self.iptal_basildi)
        self.fis_yazdir_btn = self.buton_olustur("FİŞ YAZDIR", self.fis_yazdir_basildi)
        self.fatura_btn = self.buton_olustur("FATURA", self.fatura_basildi)

        # Butonları layout'a ekle
        layout.addWidget(self.beklet_btn)
        layout.addWidget(self.bekleyenler_btn)
        layout.addWidget(self.iade_btn)
        layout.addWidget(self.iptal_btn)
        layout.addWidget(self.fis_yazdir_btn)
        layout.addWidget(self.fatura_btn)

        # Stil uygula
        self.setObjectName("HizliIslemSeridi")

    def buton_olustur(self, metin: str, sinyal: pyqtSignal) -> QPushButton:
        """Hızlı işlem butonu oluşturur"""
        buton = QPushButton(metin)
        buton.setProperty("class", self.tema.buton_stil_sinifi_al("hizli_islem"))
        buton.clicked.connect(sinyal.emit)
        return buton

    def beklet_islemi(self):
        """Beklet işlemini gerçekleştirir"""
        # Mevcut sepeti bekletir ve yeni sepet başlatır
        self.beklet_basildi.emit()

    def bekleyenler_listesi_goster(self):
        """Bekleyen sepetler listesini gösterir"""
        # Bekletilen sepetler dialog'unu açar
        self.bekleyenler_basildi.emit()

    def iade_islemi_baslat(self):
        """İade işlemini başlatır"""
        # İade işlemi dialog'unu açar
        self.iade_basildi.emit()

    def islem_iptal_et(self):
        """Mevcut işlemi iptal eder"""
        # Onay dialog'u ile mevcut işlemi iptal eder
        self.iptal_basildi.emit()

    def fis_yazdir(self):
        """Fiş yazdırır"""
        # Yazdırma servisini çağırır
        self.fis_yazdir_basildi.emit()

    def fatura_olustur(self):
        """Fatura oluşturur"""
        # Fatura oluşturma servisini çağırır
        self.fatura_basildi.emit()
