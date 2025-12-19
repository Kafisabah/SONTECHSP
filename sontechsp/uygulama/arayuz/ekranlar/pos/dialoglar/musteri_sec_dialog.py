# Version: 0.1.0
# Last Update: 2024-12-19
# Module: musteri_sec_dialog
# Description: Müşteri seçim dialog'u (CRM stub)
# Changelog:
# - İlk oluşturma

"""
Müşteri Seç Dialog'u - CRM müşteri seçimi (stub implementasyon)
"""

from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PyQt6.QtCore import Qt
from ..turkuaz_tema import TurkuazTema


class MusteriSecDialog(QDialog):
    """Müşteri seçim dialog'u"""

    def __init__(self, parent: Optional = None):
        super().__init__(parent)
        self.secili_musteri: Optional[Dict[str, Any]] = None
        self.tema = TurkuazTema()
        self.setupUI()
        self.demo_verileri_yukle()
        self.tema_uygula()

    def setupUI(self):
        """UI bileşenlerini oluşturur"""
        self.setWindowTitle("Müşteri Seç")
        self.setModal(True)
        self.setFixedSize(600, 400)

        layout = QVBoxLayout(self)

        # Arama alanı
        self.arama_alani_olustur(layout)

        # Müşteri listesi
        self.musteri_tablosu_olustur(layout)

        # Butonlar
        self.butonlari_olustur(layout)

    def arama_alani_olustur(self, layout: QVBoxLayout):
        """Arama alanını oluşturur"""
        arama_layout = QHBoxLayout()

        arama_layout.addWidget(QLabel("Müşteri Ara:"))

        self.arama_edit = QLineEdit()
        self.arama_edit.setPlaceholderText("Ad, telefon veya e-posta ile ara...")
        self.arama_edit.textChanged.connect(self.musteri_ara)

        arama_btn = QPushButton("Ara")
        arama_btn.clicked.connect(self.musteri_ara)

        arama_layout.addWidget(self.arama_edit)
        arama_layout.addWidget(arama_btn)

        layout.addLayout(arama_layout)

    def musteri_tablosu_olustur(self, layout: QVBoxLayout):
        """Müşteri tablosunu oluşturur"""
        self.musteri_tablo = QTableWidget()
        self.musteri_tablo.setColumnCount(4)
        self.musteri_tablo.setHorizontalHeaderLabels(["ID", "Ad Soyad", "Telefon", "E-posta"])

        # Kolon genişlikleri
        header = self.musteri_tablo.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        # Tek satır seçimi
        self.musteri_tablo.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.musteri_tablo.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        # Çift tıklama ile seçim
        self.musteri_tablo.itemDoubleClicked.connect(self.musteri_cift_tiklandi)

        layout.addWidget(self.musteri_tablo)

    def butonlari_olustur(self, layout: QVBoxLayout):
        """Dialog butonlarını oluşturur"""
        buton_layout = QHBoxLayout()

        yeni_musteri_btn = QPushButton("Yeni Müşteri")
        yeni_musteri_btn.clicked.connect(self.yeni_musteri_olustur)

        sec_btn = QPushButton("Seç")
        sec_btn.clicked.connect(self.musteri_sec)

        iptal_btn = QPushButton("İptal")
        iptal_btn.clicked.connect(self.reject)

        buton_layout.addWidget(yeni_musteri_btn)
        buton_layout.addWidget(sec_btn)
        buton_layout.addWidget(iptal_btn)

        layout.addLayout(buton_layout)

    def demo_verileri_yukle(self):
        """Demo müşteri verilerini yükler (CRM olmadığı için)"""
        demo_musteriler = [
            {"id": 1, "ad_soyad": "Ahmet Yılmaz", "telefon": "0532 123 4567", "eposta": "ahmet@email.com"},
            {"id": 2, "ad_soyad": "Ayşe Demir", "telefon": "0533 234 5678", "eposta": "ayse@email.com"},
            {"id": 3, "ad_soyad": "Mehmet Kaya", "telefon": "0534 345 6789", "eposta": "mehmet@email.com"},
            {"id": 4, "ad_soyad": "Fatma Özkan", "telefon": "0535 456 7890", "eposta": "fatma@email.com"},
            {"id": 5, "ad_soyad": "Ali Çelik", "telefon": "0536 567 8901", "eposta": "ali@email.com"},
        ]

        self.musteri_tablo.setRowCount(len(demo_musteriler))

        for satir, musteri in enumerate(demo_musteriler):
            self.musteri_tablo.setItem(satir, 0, QTableWidgetItem(str(musteri["id"])))
            self.musteri_tablo.setItem(satir, 1, QTableWidgetItem(musteri["ad_soyad"]))
            self.musteri_tablo.setItem(satir, 2, QTableWidgetItem(musteri["telefon"]))
            self.musteri_tablo.setItem(satir, 3, QTableWidgetItem(musteri["eposta"]))

    def musteri_ara(self):
        """Müşteri arama işlemi"""
        arama_metni = self.arama_edit.text().lower()

        for satir in range(self.musteri_tablo.rowCount()):
            gizle = True

            if not arama_metni:  # Boşsa tümünü göster
                gizle = False
            else:
                # Her kolonda ara
                for sutun in range(1, self.musteri_tablo.columnCount()):  # ID hariç
                    item = self.musteri_tablo.item(satir, sutun)
                    if item and arama_metni in item.text().lower():
                        gizle = False
                        break

            self.musteri_tablo.setRowHidden(satir, gizle)

    def musteri_cift_tiklandi(self, item):
        """Müşteri satırına çift tıklandığında çalışır"""
        self.musteri_sec()

    def musteri_sec(self):
        """Seçili müşteriyi onaylar"""
        secili_satir = self.musteri_tablo.currentRow()

        if secili_satir >= 0:
            self.secili_musteri = {
                "id": int(self.musteri_tablo.item(secili_satir, 0).text()),
                "ad_soyad": self.musteri_tablo.item(secili_satir, 1).text(),
                "telefon": self.musteri_tablo.item(secili_satir, 2).text(),
                "eposta": self.musteri_tablo.item(secili_satir, 3).text(),
            }
            self.accept()

    def yeni_musteri_olustur(self):
        """Yeni müşteri oluşturma dialog'unu açar"""
        # Burada yeni müşteri dialog'u açılacak
        # Şimdilik basit bilgi mesajı
        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.information(self, "Bilgi", "Yeni müşteri oluşturma özelliği CRM modülü ile gelecek.")

    def tema_uygula(self):
        """Turkuaz temayı uygular"""
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {self.tema.arka_plan};
                font-family: 'Segoe UI', Arial, sans-serif;
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
            
            QTableWidget {{
                background-color: white;
                border: 2px solid {self.tema.ikincil_renk};
                border-radius: 4px;
                gridline-color: #E0E0E0;
            }}
            
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #E0E0E0;
            }}
            
            QTableWidget::item:selected {{
                background-color: {self.tema.vurgu_renk};
                color: white;
            }}
            
            QHeaderView::section {{
                background-color: {self.tema.ana_renk};
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }}
            
            QLabel {{
                color: #333333;
                font-size: 12px;
            }}
        """
        )

    def secili_musteriyi_al(self) -> Optional[Dict[str, Any]]:
        """Seçili müşteri bilgilerini döndürür"""
        return self.secili_musteri
