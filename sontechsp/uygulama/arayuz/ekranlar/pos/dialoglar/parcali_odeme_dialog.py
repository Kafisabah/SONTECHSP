# Version: 0.1.0
# Last Update: 2024-12-19
# Module: parcali_odeme_dialog
# Description: Parçalı ödeme dialog'u (nakit + kart)
# Changelog:
# - İlk oluşturma

"""
Parçalı Ödeme Dialog'u - Nakit ve kart karışık ödeme
"""

from decimal import Decimal
from typing import Optional, Tuple
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ..turkuaz_tema import TurkuazTema


class ParcaliOdemeDialog(QDialog):
    """Parçalı ödeme dialog'u"""

    def __init__(self, toplam_tutar: Decimal, parent: Optional = None):
        super().__init__(parent)
        self.toplam_tutar = toplam_tutar
        self.nakit_tutar = Decimal("0.00")
        self.kart_tutar = Decimal("0.00")
        self.tema = TurkuazTema()
        self.setupUI()
        self.tema_uygula()

    def setupUI(self):
        """UI bileşenlerini oluşturur"""
        self.setWindowTitle("Parçalı Ödeme")
        self.setModal(True)
        self.setFixedSize(400, 300)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Toplam tutar göstergesi
        self.toplam_frame_olustur(layout)

        # Nakit tutar girişi
        self.nakit_alani_olustur(layout)

        # Kart tutar girişi
        self.kart_alani_olustur(layout)

        # Kalan tutar göstergesi
        self.kalan_alani_olustur(layout)

        # Butonlar
        self.butonlari_olustur(layout)

    def toplam_frame_olustur(self, layout: QVBoxLayout):
        """Toplam tutar frame'ini oluşturur"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame_layout = QVBoxLayout(frame)

        label = QLabel("TOPLAM TUTAR")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.toplam_label = QLabel(f"{self.toplam_tutar:.2f} ₺")
        self.toplam_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.toplam_label.setFont(font)

        frame_layout.addWidget(label)
        frame_layout.addWidget(self.toplam_label)

        layout.addWidget(frame)

    def nakit_alani_olustur(self, layout: QVBoxLayout):
        """Nakit tutar alanını oluşturur"""
        nakit_layout = QHBoxLayout()

        nakit_layout.addWidget(QLabel("Nakit:"))

        self.nakit_edit = QLineEdit()
        self.nakit_edit.setPlaceholderText("0.00")
        self.nakit_edit.textChanged.connect(self.tutarlari_hesapla)

        nakit_layout.addWidget(self.nakit_edit)
        nakit_layout.addWidget(QLabel("₺"))

        layout.addLayout(nakit_layout)

    def kart_alani_olustur(self, layout: QVBoxLayout):
        """Kart tutar alanını oluşturur"""
        kart_layout = QHBoxLayout()

        kart_layout.addWidget(QLabel("Kart:"))

        self.kart_edit = QLineEdit()
        self.kart_edit.setPlaceholderText("0.00")
        self.kart_edit.textChanged.connect(self.tutarlari_hesapla)

        kart_layout.addWidget(self.kart_edit)
        kart_layout.addWidget(QLabel("₺"))

        layout.addLayout(kart_layout)

    def kalan_alani_olustur(self, layout: QVBoxLayout):
        """Kalan tutar alanını oluşturur"""
        self.kalan_label = QLabel("Kalan: 0.00 ₺")
        self.kalan_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        self.kalan_label.setFont(font)

        layout.addWidget(self.kalan_label)

    def butonlari_olustur(self, layout: QVBoxLayout):
        """Dialog butonlarını oluşturur"""
        buton_layout = QHBoxLayout()

        self.tamam_btn = QPushButton("Tamam")
        self.tamam_btn.clicked.connect(self.accept)
        self.tamam_btn.setEnabled(False)

        iptal_btn = QPushButton("İptal")
        iptal_btn.clicked.connect(self.reject)

        buton_layout.addWidget(self.tamam_btn)
        buton_layout.addWidget(iptal_btn)

        layout.addLayout(buton_layout)

    def tutarlari_hesapla(self):
        """Nakit ve kart tutarlarını hesaplar"""
        try:
            self.nakit_tutar = Decimal(self.nakit_edit.text() or "0")
        except:
            self.nakit_tutar = Decimal("0")

        try:
            self.kart_tutar = Decimal(self.kart_edit.text() or "0")
        except:
            self.kart_tutar = Decimal("0")

        toplam_girilen = self.nakit_tutar + self.kart_tutar
        kalan = self.toplam_tutar - toplam_girilen

        if kalan == 0:
            self.kalan_label.setText("Kalan: 0.00 ₺")
            self.kalan_label.setStyleSheet("color: green;")
            self.tamam_btn.setEnabled(True)
        elif kalan > 0:
            self.kalan_label.setText(f"Kalan: {kalan:.2f} ₺")
            self.kalan_label.setStyleSheet("color: red;")
            self.tamam_btn.setEnabled(False)
        else:
            self.kalan_label.setText(f"Fazla: {abs(kalan):.2f} ₺")
            self.kalan_label.setStyleSheet("color: orange;")
            self.tamam_btn.setEnabled(False)

    def tema_uygula(self):
        """Turkuaz temayı uygular"""
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {self.tema.arka_plan};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            
            QFrame {{
                background-color: white;
                border: 2px solid {self.tema.ana_renk};
                border-radius: 8px;
                padding: 10px;
            }}
            
            QPushButton {{
                background-color: {self.tema.ana_renk};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
                min-width: 80px;
            }}
            
            QPushButton:hover {{
                background-color: {self.tema.vurgu_renk};
            }}
            
            QPushButton:disabled {{
                background-color: {self.tema.ikincil_renk};
            }}
            
            QLineEdit {{
                border: 2px solid {self.tema.ikincil_renk};
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }}
            
            QLineEdit:focus {{
                border-color: {self.tema.ana_renk};
            }}
            
            QLabel {{
                color: #333333;
                font-size: 12px;
            }}
        """
        )

    def odeme_bilgilerini_al(self) -> Tuple[Decimal, Decimal]:
        """Ödeme bilgilerini döndürür"""
        return self.nakit_tutar, self.kart_tutar
