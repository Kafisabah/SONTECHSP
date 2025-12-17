# Version: 0.1.0
# Last Update: 2024-12-18
# Module: uygulama.arayuz.ekranlar.ebelge_filtreleri
# Description: E-belge filtre bileşenleri
# Changelog:
# - İlk sürüm oluşturuldu

from PyQt6.QtWidgets import (QVBoxLayout, QLabel, QComboBox, QFrame,
                             QDateEdit, QLineEdit, QPushButton, QGroupBox)
from PyQt6.QtCore import Qt, QDate


class EbelgeFiltreleri:
    """E-belge filtre bileşenleri sınıfı"""
    
    def __init__(self, parent):
        self.parent = parent
        self.belge_turu_combo = None
        self.baslangic_tarih = None
        self.bitis_tarih = None
        self.musteri_filtre = None
    
    def filtre_grubu_olustur(self):
        """Filtre grubu oluştur"""
        grup = QGroupBox("Filtreler")
        grup.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        layout = QVBoxLayout(grup)
        
        # Belge türü filtresi
        self._belge_turu_filtresi_olustur(layout)
        
        # Tarih aralığı filtresi
        self._tarih_araligi_filtresi_olustur(layout)
        
        # Müşteri filtresi
        self._musteri_filtresi_olustur(layout)
        
        # Filtre uygula butonu
        self._filtre_uygula_butonu_olustur(layout)
        
        return grup
    
    def _belge_turu_filtresi_olustur(self, layout):
        """Belge türü filtresi oluştur"""
        belge_turu_label = QLabel("Belge Türü:")
        layout.addWidget(belge_turu_label)
        
        self.belge_turu_combo = QComboBox()
        self.belge_turu_combo.addItems([
            "Tümü", "e-Fatura", "e-Arşiv", "e-İrsaliye", "e-Müstahsil"
        ])
        self.belge_turu_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.belge_turu_combo)
    
    def _tarih_araligi_filtresi_olustur(self, layout):
        """Tarih aralığı filtresi oluştur"""
        tarih_label = QLabel("Tarih Aralığı:")
        layout.addWidget(tarih_label)
        
        tarih_frame = QFrame()
        tarih_layout = QVBoxLayout(tarih_frame)
        
        # Başlangıç tarihi
        self.baslangic_tarih = QDateEdit()
        self.baslangic_tarih.setDate(QDate.currentDate().addDays(-30))
        self.baslangic_tarih.setCalendarPopup(True)
        self.baslangic_tarih.setStyleSheet("""
            QDateEdit {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        tarih_layout.addWidget(QLabel("Başlangıç:"))
        tarih_layout.addWidget(self.baslangic_tarih)
        
        # Bitiş tarihi
        self.bitis_tarih = QDateEdit()
        self.bitis_tarih.setDate(QDate.currentDate())
        self.bitis_tarih.setCalendarPopup(True)
        self.bitis_tarih.setStyleSheet("""
            QDateEdit {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        tarih_layout.addWidget(QLabel("Bitiş:"))
        tarih_layout.addWidget(self.bitis_tarih)
        
        layout.addWidget(tarih_frame)
    
    def _musteri_filtresi_olustur(self, layout):
        """Müşteri filtresi oluştur"""
        musteri_label = QLabel("Müşteri:")
        layout.addWidget(musteri_label)
        
        self.musteri_filtre = QLineEdit()
        self.musteri_filtre.setPlaceholderText("Müşteri adı veya VKN...")
        self.musteri_filtre.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.musteri_filtre)
    
    def _filtre_uygula_butonu_olustur(self, layout):
        """Filtre uygula butonu oluştur"""
        filtre_uygula_buton = QPushButton("Filtre Uygula")
        filtre_uygula_buton.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        filtre_uygula_buton.clicked.connect(self.parent.filtre_uygula)
        layout.addWidget(filtre_uygula_buton)
    
    def filtre_verilerini_al(self):
        """Filtre verilerini al"""
        return {
            'belge_turu': self.belge_turu_combo.currentText(),
            'baslangic_tarih': self.baslangic_tarih.date().toPython(),
            'bitis_tarih': self.bitis_tarih.date().toPython(),
            'musteri_filtre': self.musteri_filtre.text().strip()
        }