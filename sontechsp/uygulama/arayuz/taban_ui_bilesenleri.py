# Version: 0.1.0
# Last Update: 2024-12-15
# Module: taban_ui_bilesenleri
# Description: SONTECHSP arayüz katmanı UI bileşen yöneticileri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Arayüz Katmanı UI Bileşen Yöneticileri

TabanEkran sınıfının kullandığı UI bileşenlerini yöneten sınıflar.
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QMessageBox, QProgressBar,
    QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class BaslikAlaniYoneticisi:
    """Başlık alanını yöneten sınıf"""
    
    def __init__(self, ekran_adi: str):
        self.ekran_adi = ekran_adi
        self._widget_olustur()
    
    def _widget_olustur(self):
        """Başlık widget'ını oluşturur"""
        self.widget = QFrame()
        self.widget.setFrameStyle(QFrame.Shape.StyledPanel)
        self.widget.setMaximumHeight(60)
        
        layout = QHBoxLayout(self.widget)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Başlık metni
        self.baslik_label = QLabel(self.ekran_adi)
        baslik_font = QFont()
        baslik_font.setPointSize(16)
        baslik_font.setBold(True)
        self.baslik_label.setFont(baslik_font)
        self.baslik_label.setStyleSheet("color: #2c3e50;")
        
        layout.addWidget(self.baslik_label)
        layout.addStretch()
        
        # Buton alanı
        self.buton_layout = QHBoxLayout()
        layout.addLayout(self.buton_layout)
    
    def buton_ekle(self, buton: QPushButton):
        """Başlık alanına buton ekler"""
        self.buton_layout.addWidget(buton)


class IcerikAlaniYoneticisi:
    """İçerik alanını yöneten sınıf"""
    
    def __init__(self):
        self._widget_olustur()
    
    def _widget_olustur(self):
        """İçerik widget'ını oluşturur"""
        # Scroll area ile sarmalama
        self.widget = QScrollArea()
        self.widget.setWidgetResizable(True)
        self.widget.setFrameStyle(QFrame.Shape.NoFrame)
        
        # İçerik widget'ı
        self.icerik_widget = QWidget()
        self.layout = QVBoxLayout(self.icerik_widget)
        self.layout.setContentsMargins(5, 5, 5, 5)
        
        self.widget.setWidget(self.icerik_widget)


class AltAracCubuguYoneticisi:
    """Alt araç çubuğunu yöneten sınıf"""
    
    def __init__(self):
        self._widget_olustur()
    
    def _widget_olustur(self):
        """Alt araç çubuğu widget'ını oluşturur"""
        self.widget = QFrame()
        self.widget.setFrameStyle(QFrame.Shape.StyledPanel)
        self.widget.setMaximumHeight(50)
        
        layout = QHBoxLayout(self.widget)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Sol taraf - durum bilgisi
        self.durum_label = QLabel("Hazır")
        self.durum_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addWidget(self.durum_label)
        
        layout.addStretch()
        
        # Sağ taraf - yenile butonu
        self.yenile_buton = QPushButton("Yenile")
        layout.addWidget(self.yenile_buton)
        
        # Ek butonlar için alan
        self.buton_layout = QHBoxLayout()
        layout.addLayout(self.buton_layout)
    
    def durum_guncelle(self, mesaj: str, sure: int = 0):
        """Durum mesajını günceller"""
        self.durum_label.setText(mesaj)
        
        if sure > 0:
            QTimer.singleShot(sure * 1000, lambda: self.durum_label.setText("Hazır"))
    
    def buton_ekle(self, buton: QPushButton):
        """Alt araç çubuğuna buton ekler"""
        self.buton_layout.addWidget(buton)


class MesajYoneticisi:
    """Mesaj ve progress bar yöneticisi"""
    
    def __init__(self, parent: QWidget):
        self.parent = parent
        self._widget_olustur()
    
    def _widget_olustur(self):
        """Progress bar oluşturur"""
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
    
    def hata_goster(self, hata_mesaji: str):
        """Hata mesajı gösterir"""
        QMessageBox.critical(self.parent, "Hata", hata_mesaji)
    
    def bilgi_goster(self, mesaj: str, baslik: str = "Bilgi"):
        """Bilgi mesajı gösterir"""
        QMessageBox.information(self.parent, baslik, mesaj)
    
    def uyari_goster(self, mesaj: str, baslik: str = "Uyarı"):
        """Uyarı mesajı gösterir"""
        QMessageBox.warning(self.parent, baslik, mesaj)
    
    def onay_iste(self, mesaj: str, baslik: str = "Onay") -> bool:
        """Kullanıcıdan onay ister"""
        cevap = QMessageBox.question(
            self.parent, baslik, mesaj,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return cevap == QMessageBox.StandardButton.Yes