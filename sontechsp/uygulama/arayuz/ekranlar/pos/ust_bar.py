# Version: 0.1.0
# Last Update: 2024-12-19
# Module: ust_bar
# Description: POS üst bar bileşeni - barkod girişi ve müşteri işlemleri
# Changelog:
# - İlk oluşturma

"""
Üst Bar - POS ekranının üst çubuğu bileşeni
"""

from typing import Optional
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QComboBox, QLabel, QPushButton, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QDateTime
from PyQt6.QtGui import QFont


class UstBar(QWidget):
    """POS üst bar widget'ı"""

    barkod_girildi = pyqtSignal(str)
    urun_secildi = pyqtSignal(str)
    musteri_sec_tiklandi = pyqtSignal()
    musteri_temizle_tiklandi = pyqtSignal()
    acik_hesap_tiklandi = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setupUI()
        self.saat_timer_baslat()

    def setupUI(self):
        """UI bileşenlerini oluşturur"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Sol taraf - Barkod ve ürün arama
        self.barkod_edit = QLineEdit()
        self.barkod_edit.setPlaceholderText("Barkod okutun veya yazın...")
        self.barkod_edit.setMinimumWidth(200)
        self.barkod_edit.returnPressed.connect(self.barkod_enter_basildi)

        self.urun_arama_combo = QComboBox()
        self.urun_arama_combo.setEditable(True)
        self.urun_arama_combo.setPlaceholderText("Ürün ara...")
        self.urun_arama_combo.setMinimumWidth(250)
        self.urun_arama_combo.currentTextChanged.connect(self.urun_arama_degisti)

        layout.addWidget(QLabel("Barkod:"))
        layout.addWidget(self.barkod_edit)
        layout.addWidget(QLabel("Ürün:"))
        layout.addWidget(self.urun_arama_combo)

        # Orta boşluk
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout.addItem(spacer)

        # Sağ taraf - Kasiyer bilgisi ve müşteri butonları
        self.kasiyer_label = QLabel("Kasiyer: Admin | Mağaza: Ana | Terminal: 001")
        font = QFont()
        font.setBold(True)
        self.kasiyer_label.setFont(font)

        self.musteri_sec_btn = QPushButton("Müşteri Seç")
        self.musteri_sec_btn.clicked.connect(self.musteri_sec_tiklandi.emit)

        self.musteri_temizle_btn = QPushButton("Müşteri Temizle")
        self.musteri_temizle_btn.clicked.connect(self.musteri_temizle_tiklandi.emit)

        self.acik_hesap_btn = QPushButton("Açık Hesap")
        self.acik_hesap_btn.clicked.connect(self.acik_hesap_tiklandi.emit)

        self.saat_label = QLabel()
        self.saat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.saat_label.setFont(font)

        layout.addWidget(self.kasiyer_label)
        layout.addWidget(self.musteri_sec_btn)
        layout.addWidget(self.musteri_temizle_btn)
        layout.addWidget(self.acik_hesap_btn)
        layout.addWidget(self.saat_label)

        # Stil uygula
        self.setObjectName("UstBar")

    def barkod_enter_basildi(self):
        """Barkod alanında Enter tuşuna basıldığında çalışır"""
        barkod = self.barkod_edit.text().strip()
        if barkod:
            self.barkod_girildi.emit(barkod)
            self.barkod_edit.clear()

    def urun_arama_degisti(self, metin: str):
        """Ürün arama metni değiştiğinde çalışır"""
        if len(metin) >= 3:  # En az 3 karakter
            # Burada servis çağrısı yapılacak
            pass

    def barkod_odagini_ver(self):
        """Barkod alanına odak verir"""
        self.barkod_edit.setFocus()
        self.barkod_edit.selectAll()

    def saat_timer_baslat(self):
        """Saat güncellemesi için timer başlatır"""
        self.saat_timer = QTimer()
        self.saat_timer.timeout.connect(self.saati_guncelle)
        self.saat_timer.start(1000)  # Her saniye
        self.saati_guncelle()

    def saati_guncelle(self):
        """Saat etiketini günceller"""
        simdi = QDateTime.currentDateTime()
        saat_metni = simdi.toString("dd.MM.yyyy hh:mm:ss")
        self.saat_label.setText(saat_metni)

    def kasiyer_bilgisini_guncelle(self, kasiyer: str, magaza: str, terminal: str):
        """Kasiyer bilgisini günceller"""
        self.kasiyer_label.setText(f"Kasiyer: {kasiyer} | Mağaza: {magaza} | Terminal: {terminal}")
