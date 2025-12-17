# Version: 0.1.0
# Last Update: 2024-12-18
# Module: uygulama.arayuz.ekranlar.ebelge_islemleri
# Description: E-belge işlem bileşenleri
# Changelog:
# - İlk sürüm oluşturuldu

from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QGroupBox


class EbelgeIslemleri:
    """E-belge işlem bileşenleri sınıfı"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def islemler_grubu_olustur(self):
        """İşlemler grubu oluştur"""
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
        
        # Belge gönder butonu
        self._belge_gonder_butonu_olustur(layout)
        
        # Durum sorgula butonu
        self._durum_sorgula_butonu_olustur(layout)
        
        # Tekrar dene butonu
        self._tekrar_dene_butonu_olustur(layout)
        
        # Toplu işlemler butonu
        self._toplu_gonder_butonu_olustur(layout)
        
        # XML görüntüle butonu
        self._xml_goruntule_butonu_olustur(layout)
        
        return grup
    
    def _belge_gonder_butonu_olustur(self, layout):
        """Belge gönder butonu oluştur"""
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
    
    def _durum_sorgula_butonu_olustur(self, layout):
        """Durum sorgula butonu oluştur"""
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
    
    def _tekrar_dene_butonu_olustur(self, layout):
        """Tekrar dene butonu oluştur"""
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
    
    def _toplu_gonder_butonu_olustur(self, layout):
        """Toplu gönder butonu oluştur"""
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
    
    def _xml_goruntule_butonu_olustur(self, layout):
        """XML görüntüle butonu oluştur"""
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