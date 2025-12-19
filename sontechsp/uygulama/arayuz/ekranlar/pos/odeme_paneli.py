# Version: 0.1.0
# Last Update: 2024-12-19
# Module: odeme_paneli
# Description: POS ödeme paneli bileşeni
# Changelog:
# - İlk oluşturma

"""
Ödeme Paneli - POS ödeme işlemleri ve toplam gösterimi
"""

from decimal import Decimal
from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTabWidget, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from .turkuaz_tema import TurkuazTema


class OdemePaneli(QWidget):
    """POS ödeme paneli widget'ı"""

    nakit_odeme_basildi = pyqtSignal()
    kart_odeme_basildi = pyqtSignal()
    parcali_odeme_basildi = pyqtSignal()
    acik_hesap_basildi = pyqtSignal()
    para_girisi_degisti = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.genel_toplam_tutari = Decimal("0.00")
        self.tema = TurkuazTema()
        self.setupUI()

    def setupUI(self):
        """UI bileşenlerini oluşturur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self._toplam_frame_olustur(layout)
        self._odeme_butonlari_olustur(layout)
        self._nakit_alani_olustur(layout)
        self._sekme_sistemi_olustur(layout)

    def _toplam_frame_olustur(self, layout: QVBoxLayout):
        """Toplam göstergesi frame'ini oluşturur"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame_layout = QVBoxLayout(frame)

        self.genel_toplam_label = QLabel("0.00 ₺")
        self.genel_toplam_label.setObjectName("genel-toplam")
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.genel_toplam_label.setFont(font)
        self.genel_toplam_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.ara_toplam_label = QLabel("Ara Toplam: 0.00 ₺")
        self.ara_toplam_label.setProperty("class", self.tema.label_stil_sinifi_al("ara_toplam"))
        self.indirim_label = QLabel("İndirim: 0.00 ₺")
        self.indirim_label.setProperty("class", self.tema.label_stil_sinifi_al("ara_toplam"))
        self.kdv_label = QLabel("KDV: 0.00 ₺")
        self.kdv_label.setProperty("class", self.tema.label_stil_sinifi_al("ara_toplam"))

        frame_layout.addWidget(QLabel("GENEL TOPLAM"))
        frame_layout.addWidget(self.genel_toplam_label)
        frame_layout.addWidget(self.ara_toplam_label)
        frame_layout.addWidget(self.indirim_label)
        frame_layout.addWidget(self.kdv_label)
        layout.addWidget(frame)

    def _odeme_butonlari_olustur(self, layout: QVBoxLayout):
        """Ödeme butonlarını oluşturur"""
        # İlk satır butonları
        ilk_satir = QHBoxLayout()
        self.nakit_btn = QPushButton("NAKİT\nF4")
        self.nakit_btn.setProperty("class", self.tema.buton_stil_sinifi_al("odeme"))
        self.nakit_btn.clicked.connect(self.nakit_odeme_basildi.emit)
        self.kart_btn = QPushButton("KART\nF5")
        self.kart_btn.setProperty("class", self.tema.buton_stil_sinifi_al("odeme"))
        self.kart_btn.clicked.connect(self.kart_odeme_basildi.emit)
        ilk_satir.addWidget(self.nakit_btn)
        ilk_satir.addWidget(self.kart_btn)

        # İkinci satır butonları
        ikinci_satir = QHBoxLayout()
        self.parcali_btn = QPushButton("PARÇALI\nF6")
        self.parcali_btn.setProperty("class", self.tema.buton_stil_sinifi_al("odeme"))
        self.parcali_btn.clicked.connect(self.parcali_odeme_basildi.emit)
        self.acik_hesap_btn = QPushButton("AÇIK HESAP\nF7")
        self.acik_hesap_btn.setProperty("class", self.tema.buton_stil_sinifi_al("odeme"))
        self.acik_hesap_btn.clicked.connect(self.acik_hesap_basildi.emit)
        ikinci_satir.addWidget(self.parcali_btn)
        ikinci_satir.addWidget(self.acik_hesap_btn)

        layout.addLayout(ilk_satir)
        layout.addLayout(ikinci_satir)

    def _nakit_alani_olustur(self, layout: QVBoxLayout):
        """Nakit ödeme alanını oluşturur"""
        self.nakit_frame = QFrame()
        self.nakit_frame.setFrameStyle(QFrame.Shape.Box)
        self.nakit_frame.setProperty("class", self.tema.widget_stil_sinifi_al("nakit_alan"))
        self.nakit_frame.setVisible(False)

        nakit_layout = QVBoxLayout(self.nakit_frame)
        nakit_layout.addWidget(QLabel("Alınan Para:"))

        self.alinan_para_edit = QLineEdit()
        self.alinan_para_edit.setPlaceholderText("0.00")
        self.alinan_para_edit.textChanged.connect(self.para_girisi_degisti.emit)
        self.alinan_para_edit.textChanged.connect(self.para_ustu_hesapla)

        self.para_ustu_label = QLabel("Para Üstü: 0.00 ₺")
        font = QFont()
        font.setBold(True)
        self.para_ustu_label.setFont(font)

        nakit_layout.addWidget(self.alinan_para_edit)
        nakit_layout.addWidget(self.para_ustu_label)
        layout.addWidget(self.nakit_frame)

    def _sekme_sistemi_olustur(self, layout: QVBoxLayout):
        """Sekme sistemini oluşturur"""
        self.tab_widget = QTabWidget()
        odeme_tab = QWidget()
        self.tab_widget.addTab(odeme_tab, "Ödeme")
        hizli_urunler_tab = QWidget()
        self.tab_widget.addTab(hizli_urunler_tab, "Hızlı Ürünler")
        layout.addWidget(self.tab_widget)

    def genel_toplami_guncelle(self, tutar: Decimal):
        """Genel toplamı günceller"""
        self.genel_toplam_tutari = tutar
        self.genel_toplam_label.setText(f"{tutar:.2f} ₺")
        ara_toplam = tutar / Decimal("1.18")
        kdv = tutar - ara_toplam
        self.ara_toplam_label.setText(f"Ara Toplam: {ara_toplam:.2f} ₺")
        self.kdv_label.setText(f"KDV: {kdv:.2f} ₺")
        self.para_ustu_hesapla()

    def nakit_alanini_goster(self, goster: bool = True):
        """Nakit ödeme alanını gösterir/gizler"""
        self.nakit_frame.setVisible(goster)
        if goster:
            self.alinan_para_edit.setFocus()

    def para_ustu_hesapla(self):
        """Para üstü hesaplar"""
        try:
            alinan = Decimal(self.alinan_para_edit.text() or "0")
            para_ustu = alinan - self.genel_toplam_tutari
            if para_ustu >= 0:
                self.para_ustu_label.setText(f"Para Üstü: {para_ustu:.2f} ₺")
            else:
                self.para_ustu_label.setText(f"Eksik: {abs(para_ustu):.2f} ₺")
        except:
            self.para_ustu_label.setText("Para Üstü: 0.00 ₺")

    def odeme_alanini_temizle(self):
        """Ödeme alanını temizler"""
        self.alinan_para_edit.clear()
        self.nakit_alanini_goster(False)
        self.para_ustu_label.setText("Para Üstü: 0.00 ₺")
