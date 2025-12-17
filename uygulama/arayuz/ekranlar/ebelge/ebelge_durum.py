# Version: 0.1.0
# Last Update: 2024-12-18
# Module: uygulama.arayuz.ekranlar.ebelge.ebelge_durum
# Description: E-belge durum UI bileşenleri
# Changelog:
# - İlk sürüm oluşturuldu

from PyQt6.QtWidgets import QVBoxLayout, QLabel, QGroupBox, QProgressBar, QFrame


class EbelgeDurum:
    """E-belge durum UI bileşenleri"""
    
    def __init__(self, parent):
        self.parent = parent
        self.durum_label = None
        self.progress_bar = None
        self.bekleyen_sayisi_label = None
        self.gonderilen_sayisi_label = None
        self.hatali_sayisi_label = None
        self.istatistik_frame = None
    
    def durum_bilgisi_grubu_olustur(self):
        """Durum bilgisi grubu"""
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
        
        # Progress bar
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
        
        # İstatistikler
        self.istatistik_frame = QFrame()
        istatistik_layout = QVBoxLayout(self.istatistik_frame)
        
        self.bekleyen_sayisi_label = QLabel("Bekleyen: 0")
        self.bekleyen_sayisi_label.setStyleSheet("font-size: 11px; color: #f39c12; font-weight: bold;")
        istatistik_layout.addWidget(self.bekleyen_sayisi_label)
        
        self.gonderilen_sayisi_label = QLabel("Gönderilen: 0")
        self.gonderilen_sayisi_label.setStyleSheet("font-size: 11px; color: #27ae60; font-weight: bold;")
        istatistik_layout.addWidget(self.gonderilen_sayisi_label)
        
        self.hatali_sayisi_label = QLabel("Hatalı: 0")
        self.hatali_sayisi_label.setStyleSheet("font-size: 11px; color: #e74c3c; font-weight: bold;")
        istatistik_layout.addWidget(self.hatali_sayisi_label)
        
        layout.addWidget(self.istatistik_frame)
        
        return grup
    
    def islem_baslat(self, mesaj: str):
        """İşlem başlatma"""
        self.durum_label.setText(mesaj)
        self.durum_label.setStyleSheet("""
            QLabel {
                padding: 5px;
                background-color: #f39c12;
                color: white;
                border-radius: 3px;
                font-weight: bold;
            }
        """)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Belirsiz progress
    
    def islem_bitir(self):
        """İşlem bitirme"""
        self.durum_label.setText("Hazır")
        self.durum_label.setStyleSheet("""
            QLabel {
                padding: 5px;
                background-color: #27ae60;
                color: white;
                border-radius: 3px;
                font-weight: bold;
            }
        """)
        self.progress_bar.setVisible(False)