# Version: 0.1.0
# Last Update: 2024-12-18
# Module: uygulama.arayuz.ekranlar.ebelge_durum
# Description: E-belge durum bileşenleri
# Changelog:
# - İlk sürüm oluşturuldu

from PyQt6.QtWidgets import (QVBoxLayout, QLabel, QProgressBar, 
                             QFrame, QGroupBox)
from PyQt6.QtCore import Qt


class EbelgeDurum:
    """E-belge durum bileşenleri sınıfı"""
    
    def __init__(self, parent):
        self.parent = parent
        self.durum_label = None
        self.progress_bar = None
        self.bekleyen_sayisi_label = None
        self.gonderilen_sayisi_label = None
        self.hatali_sayisi_label = None
        self.istatistik_frame = None
    
    def durum_bilgisi_grubu_olustur(self):
        """Durum bilgisi grubu oluştur"""
        grup = QGroupBox("Durum Bilgisi")
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
        
        # Durum etiketi
        self._durum_etiketi_olustur(layout)
        
        # Progress bar
        self._progress_bar_olustur(layout)
        
        # İstatistikler
        self._istatistikler_olustur(layout)
        
        return grup
    
    def _durum_etiketi_olustur(self, layout):
        """Durum etiketi oluştur"""
        self.durum_label = QLabel("Hazır")
        self.durum_label.setStyleSheet("""
            QLabel {
                padding: 5px;
                background-color: #27ae60;
                color: white;
                border-radius: 3px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.durum_label)
    
    def _progress_bar_olustur(self, layout):
        """Progress bar oluştur"""
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress_bar)
    
    def _istatistikler_olustur(self, layout):
        """İstatistikler oluştur"""
        self.istatistik_frame = QFrame()
        istatistik_layout = QVBoxLayout(self.istatistik_frame)
        
        self.bekleyen_sayisi_label = QLabel("Bekleyen: 0")
        self.bekleyen_sayisi_label.setStyleSheet(
            "font-size: 11px; color: #f39c12; font-weight: bold;"
        )
        istatistik_layout.addWidget(self.bekleyen_sayisi_label)
        
        self.gonderilen_sayisi_label = QLabel("Gönderilen: 0")
        self.gonderilen_sayisi_label.setStyleSheet(
            "font-size: 11px; color: #27ae60; font-weight: bold;"
        )
        istatistik_layout.addWidget(self.gonderilen_sayisi_label)
        
        self.hatali_sayisi_label = QLabel("Hatalı: 0")
        self.hatali_sayisi_label.setStyleSheet(
            "font-size: 11px; color: #e74c3c; font-weight: bold;"
        )
        istatistik_layout.addWidget(self.hatali_sayisi_label)
        
        layout.addWidget(self.istatistik_frame)
    
    def durum_guncelle(self, durum_metni, renk="#27ae60"):
        """Durum güncelle"""
        if self.durum_label:
            self.durum_label.setText(durum_metni)
            self.durum_label.setStyleSheet(f"""
                QLabel {{
                    padding: 5px;
                    background-color: {renk};
                    color: white;
                    border-radius: 3px;
                    font-weight: bold;
                }}
            """)
    
    def progress_goster(self, goster=True):
        """Progress bar göster/gizle"""
        if self.progress_bar:
            self.progress_bar.setVisible(goster)
    
    def progress_guncelle(self, deger):
        """Progress bar güncelle"""
        if self.progress_bar:
            self.progress_bar.setValue(deger)
    
    def istatistikleri_guncelle(self, bekleyen=0, gonderilen=0, hatali=0):
        """İstatistikleri güncelle"""
        if self.bekleyen_sayisi_label:
            self.bekleyen_sayisi_label.setText(f"Bekleyen: {bekleyen}")
        
        if self.gonderilen_sayisi_label:
            self.gonderilen_sayisi_label.setText(f"Gönderilen: {gonderilen}")
        
        if self.hatali_sayisi_label:
            self.hatali_sayisi_label.setText(f"Hatalı: {hatali}")