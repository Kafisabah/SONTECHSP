# Version: 0.1.0
# Last Update: 2024-12-19
# Module: indirim_dialog
# Description: İndirim ve kupon dialog'u
# Changelog:
# - İlk oluşturma

"""
İndirim Dialog'u - İndirim yüzdesi ve kupon kodu işlemleri
"""

from decimal import Decimal
from typing import Optional, Tuple
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QFrame,
    QTabWidget,
    QWidget,
)
from PyQt6.QtCore import Qt
from ..turkuaz_tema import TurkuazTema


class IndirimDialog(QDialog):
    """İndirim ve kupon dialog'u"""

    def __init__(self, mevcut_tutar: Decimal, parent: Optional = None):
        super().__init__(parent)
        self.mevcut_tutar = mevcut_tutar
        self.indirim_tutari = Decimal("0.00")
        self.indirim_yuzde = 0.0
        self.kupon_kodu = ""
        self.tema = TurkuazTema()
        self.setupUI()
        self.tema_uygula()

    def setupUI(self):
        """UI bileşenlerini oluşturur"""
        self.setWindowTitle("İndirim ve Kupon")
        self.setModal(True)
        self.setFixedSize(400, 350)

        layout = QVBoxLayout(self)

        # Mevcut tutar göstergesi
        self.tutar_frame_olustur(layout)

        # Sekme sistemi
        self.sekme_sistemi_olustur(layout)

        # Butonlar
        self.butonlari_olustur(layout)

    def tutar_frame_olustur(self, layout: QVBoxLayout):
        """Mevcut tutar frame'ini oluşturur"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame_layout = QVBoxLayout(frame)

        frame_layout.addWidget(QLabel("Mevcut Tutar:"))
        self.mevcut_tutar_label = QLabel(f"{self.mevcut_tutar:.2f} ₺")
        self.mevcut_tutar_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        frame_layout.addWidget(self.mevcut_tutar_label)
        layout.addWidget(frame)

    def sekme_sistemi_olustur(self, layout: QVBoxLayout):
        """Sekme sistemini oluşturur"""
        self.tab_widget = QTabWidget()

        # İndirim sekmesi
        indirim_tab = self.indirim_sekmesi_olustur()
        self.tab_widget.addTab(indirim_tab, "İndirim")

        # Kupon sekmesi
        kupon_tab = self.kupon_sekmesi_olustur()
        self.tab_widget.addTab(kupon_tab, "Kupon")

        layout.addWidget(self.tab_widget)

    def indirim_sekmesi_olustur(self) -> QWidget:
        """İndirim sekmesini oluşturur"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # İndirim türü seçimi
        self.indirim_grubu = QButtonGroup()

        self.yuzde_radio = QRadioButton("Yüzde İndirim")
        self.yuzde_radio.setChecked(True)
        self.yuzde_radio.toggled.connect(self.indirim_hesapla)

        self.tutar_radio = QRadioButton("Tutar İndirim")
        self.tutar_radio.toggled.connect(self.indirim_hesapla)

        self.indirim_grubu.addButton(self.yuzde_radio)
        self.indirim_grubu.addButton(self.tutar_radio)

        layout.addWidget(self.yuzde_radio)
        layout.addWidget(self.tutar_radio)

        # İndirim değeri girişi
        deger_layout = QHBoxLayout()
        deger_layout.addWidget(QLabel("Değer:"))

        self.indirim_edit = QLineEdit()
        self.indirim_edit.setPlaceholderText("0")
        self.indirim_edit.textChanged.connect(self.indirim_hesapla)

        deger_layout.addWidget(self.indirim_edit)

        self.birim_label = QLabel("%")
        deger_layout.addWidget(self.birim_label)

        layout.addLayout(deger_layout)

        # İndirim sonucu
        self.indirim_sonuc_label = QLabel("İndirim Tutarı: 0.00 ₺")
        self.yeni_tutar_label = QLabel("Yeni Tutar: 0.00 ₺")

        layout.addWidget(self.indirim_sonuc_label)
        layout.addWidget(self.yeni_tutar_label)

        return widget

    def kupon_sekmesi_olustur(self) -> QWidget:
        """Kupon sekmesini oluşturur"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel("Kupon Kodu:"))

        self.kupon_edit = QLineEdit()
        self.kupon_edit.setPlaceholderText("Kupon kodunu girin...")

        kupon_dogrula_btn = QPushButton("Kupon Doğrula")
        kupon_dogrula_btn.clicked.connect(self.kupon_dogrula)

        self.kupon_sonuc_label = QLabel("")

        layout.addWidget(self.kupon_edit)
        layout.addWidget(kupon_dogrula_btn)
        layout.addWidget(self.kupon_sonuc_label)

        return widget

    def butonlari_olustur(self, layout: QVBoxLayout):
        """Dialog butonlarını oluşturur"""
        buton_layout = QHBoxLayout()

        tamam_btn = QPushButton("Uygula")
        tamam_btn.clicked.connect(self.accept)

        iptal_btn = QPushButton("İptal")
        iptal_btn.clicked.connect(self.reject)

        buton_layout.addWidget(tamam_btn)
        buton_layout.addWidget(iptal_btn)

        layout.addLayout(buton_layout)

    def indirim_hesapla(self):
        """İndirim tutarını hesaplar"""
        try:
            deger = float(self.indirim_edit.text() or "0")
        except:
            deger = 0.0

        if self.yuzde_radio.isChecked():
            # Yüzde indirim
            self.birim_label.setText("%")
            self.indirim_yuzde = deger
            self.indirim_tutari = self.mevcut_tutar * Decimal(deger / 100)
        else:
            # Tutar indirim
            self.birim_label.setText("₺")
            self.indirim_tutari = Decimal(deger)
            if self.mevcut_tutar > 0:
                self.indirim_yuzde = float(self.indirim_tutari / self.mevcut_tutar * 100)

        # Sonuçları güncelle
        yeni_tutar = self.mevcut_tutar - self.indirim_tutari
        self.indirim_sonuc_label.setText(f"İndirim Tutarı: {self.indirim_tutari:.2f} ₺")
        self.yeni_tutar_label.setText(f"Yeni Tutar: {yeni_tutar:.2f} ₺")

    def kupon_dogrula(self):
        """Kupon kodunu doğrular"""
        self.kupon_kodu = self.kupon_edit.text().strip()

        if not self.kupon_kodu:
            self.kupon_sonuc_label.setText("Kupon kodu giriniz!")
            self.kupon_sonuc_label.setStyleSheet("color: red;")
            return

        # Burada kupon doğrulama servisi çağrılacak
        # Şimdilik basit kontrol
        if self.kupon_kodu.upper() == "INDIRIM10":
            self.kupon_sonuc_label.setText("Geçerli kupon! %10 indirim")
            self.kupon_sonuc_label.setStyleSheet("color: green;")
            self.indirim_yuzde = 10.0
            self.indirim_tutari = self.mevcut_tutar * Decimal("0.10")
        else:
            self.kupon_sonuc_label.setText("Geçersiz kupon kodu!")
            self.kupon_sonuc_label.setStyleSheet("color: red;")

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
            
            QLineEdit {{
                border: 2px solid {self.tema.ikincil_renk};
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }}
            
            QLineEdit:focus {{
                border-color: {self.tema.ana_renk};
            }}
            
            QRadioButton {{
                font-size: 12px;
                spacing: 5px;
            }}
            
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
            }}
            
            QRadioButton::indicator:checked {{
                background-color: {self.tema.ana_renk};
                border: 2px solid {self.tema.ana_renk};
                border-radius: 8px;
            }}
            
            QRadioButton::indicator:unchecked {{
                background-color: white;
                border: 2px solid {self.tema.ikincil_renk};
                border-radius: 8px;
            }}
            
            QTabWidget::pane {{
                border: 2px solid {self.tema.ikincil_renk};
                border-radius: 4px;
            }}
            
            QTabBar::tab {{
                background-color: {self.tema.ikincil_renk};
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {self.tema.ana_renk};
            }}
            
            QLabel {{
                color: #333333;
                font-size: 12px;
            }}
        """
        )

    def indirim_bilgilerini_al(self) -> Tuple[Decimal, float, str]:
        """İndirim bilgilerini döndürür"""
        return self.indirim_tutari, self.indirim_yuzde, self.kupon_kodu
