# Version: 0.1.0
# Last Update: 2024-12-18
# Module: uygulama.arayuz.ekranlar.ebelge.ebelge_islemleri
# Description: E-belge işlem UI bileşenleri
# Changelog:
# - İlk sürüm oluşturuldu

from PyQt6.QtWidgets import QVBoxLayout, QGroupBox, QPushButton


class EbelgeIslemleri:
    """E-belge işlem UI bileşenleri"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def islemler_grubu_olustur(self):
        """İşlemler grubu"""
        grup = QGroupBox("E-belge İşlemleri")
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
        
        # Belge gönder
        gonder_buton = QPushButton("Belge Gönder")
        gonder_buton.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        gonder_buton.clicked.connect(self.parent.belge_gonder)
        layout.addWidget(gonder_buton)
        
        # Durum sorgula
        durum_sorgula_buton = QPushButton("Durum Sorgula")
        durum_sorgula_buton.setStyleSheet("""
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
        durum_sorgula_buton.clicked.connect(self.parent.durum_sorgula)
        layout.addWidget(durum_sorgula_buton)
        
        # Tekrar dene
        tekrar_dene_buton = QPushButton("Tekrar Dene")
        tekrar_dene_buton.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        tekrar_dene_buton.clicked.connect(self.parent.tekrar_dene)
        layout.addWidget(tekrar_dene_buton)
        
        # Toplu işlemler
        toplu_gonder_buton = QPushButton("Toplu Gönder")
        toplu_gonder_buton.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        toplu_gonder_buton.clicked.connect(self.parent.toplu_gonder)
        layout.addWidget(toplu_gonder_buton)
        
        # XML görüntüle
        xml_goruntule_buton = QPushButton("XML Görüntüle")
        xml_goruntule_buton.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        xml_goruntule_buton.clicked.connect(self.parent.xml_goruntule)
        layout.addWidget(xml_goruntule_buton)
        
        return grup