# Version: 0.1.0
# Last Update: 2024-12-18
# Module: uygulama.arayuz.ekranlar.ebelge.ebelge_tablolar
# Description: E-belge tablo UI bileşenleri
# Changelog:
# - İlk sürüm oluşturuldu

from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QFrame, QPushButton, 
                             QTableWidget, QHeaderView, QLabel)
from .ebelge_veri_yoneticisi import EbelgeVeriYoneticisi


class EbelgeTablolar:
    """E-belge tablo UI bileşenleri"""
    
    def __init__(self, parent):
        self.parent = parent
        self.veri_yoneticisi = EbelgeVeriYoneticisi(parent)
    
    def bekleyen_belgeler_sekmesi_olustur(self):
        """Bekleyen belgeler sekmesi"""
        widget = QFrame()
        layout = QVBoxLayout(widget)
        
        # Üst butonlar
        ust_butonlar = self.bekleyen_ust_butonlar_olustur()
        layout.addWidget(ust_butonlar)
        
        # Bekleyen belgeler tablosu
        self.parent.bekleyen_tablo = QTableWidget()
        self.parent.bekleyen_tablo.setColumnCount(8)
        self.parent.bekleyen_tablo.setHorizontalHeaderLabels([
            "Belge No", "Tür", "Müşteri", "Tutar", "Tarih", "Durum", "Deneme", "İşlemler"
        ])
        
        # Tablo ayarları
        self.tablo_ayarlarini_uygula(self.parent.bekleyen_tablo)
        layout.addWidget(self.parent.bekleyen_tablo)
        
        return widget
    
    def gonderilen_belgeler_sekmesi_olustur(self):
        """Gönderilen belgeler sekmesi"""
        widget = QFrame()
        layout = QVBoxLayout(widget)
        
        # Üst butonlar
        ust_butonlar = self.gonderilen_ust_butonlar_olustur()
        layout.addWidget(ust_butonlar)
        
        # Gönderilen belgeler tablosu
        self.parent.gonderilen_tablo = QTableWidget()
        self.parent.gonderilen_tablo.setColumnCount(9)
        self.parent.gonderilen_tablo.setHorizontalHeaderLabels([
            "Belge No", "Tür", "Müşteri", "Tutar", "Gönderim Tarihi", "UUID", "Durum", "Yanıt", "İşlemler"
        ])
        
        # Tablo ayarları
        self.tablo_ayarlarini_uygula(self.parent.gonderilen_tablo)
        layout.addWidget(self.parent.gonderilen_tablo)
        
        return widget
    
    def hatali_belgeler_sekmesi_olustur(self):
        """Hatalı belgeler sekmesi"""
        widget = QFrame()
        layout = QVBoxLayout(widget)
        
        # Üst butonlar
        ust_butonlar = self.hatali_ust_butonlar_olustur()
        layout.addWidget(ust_butonlar)
        
        # Hatalı belgeler tablosu
        self.parent.hatali_tablo = QTableWidget()
        self.parent.hatali_tablo.setColumnCount(8)
        self.parent.hatali_tablo.setHorizontalHeaderLabels([
            "Belge No", "Tür", "Müşteri", "Tutar", "Hata Tarihi", "Hata Kodu", "Hata Açıklaması", "İşlemler"
        ])
        
        # Tablo ayarları
        self.tablo_ayarlarini_uygula(self.parent.hatali_tablo)
        layout.addWidget(self.parent.hatali_tablo)
        
        return widget
    
    def tablo_ayarlarini_uygula(self, tablo):
        """Tablo ayarlarını uygula"""
        header = tablo.horizontalHeader()
        for i in range(tablo.columnCount()):
            if i == 2:  # Müşteri sütunu
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            elif i == tablo.columnCount() - 1:  # İşlemler sütunu
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        tablo.setAlternatingRowColors(True)
        tablo.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tablo.setStyleSheet("""
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
    
    def bekleyen_ust_butonlar_olustur(self):
        """Bekleyen belgeler üst butonları"""
        frame = QFrame()
        layout = QHBoxLayout(frame)
        
        # Yenile
        yenile_buton = QPushButton("YENİLE")
        yenile_buton.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        yenile_buton.clicked.connect(self.parent.bekleyen_listesi_yenile)
        layout.addWidget(yenile_buton)
        
        # Seçilenleri gönder
        secilenleri_gonder_buton = QPushButton("Seçilenleri Gönder")
        secilenleri_gonder_buton.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        secilenleri_gonder_buton.clicked.connect(self.parent.secilenleri_gonder)
        layout.addWidget(secilenleri_gonder_buton)
        
        layout.addStretch()
        
        # Durum çubuğu
        self.parent.bekleyen_durum_label = QLabel("Toplam Bekleyen: 0")
        self.parent.bekleyen_durum_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.parent.bekleyen_durum_label)
        
        return frame
    
    def gonderilen_ust_butonlar_olustur(self):
        """Gönderilen belgeler üst butonları"""
        frame = QFrame()
        layout = QHBoxLayout(frame)
        
        # Yenile
        yenile_buton = QPushButton("YENİLE")
        yenile_buton.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        yenile_buton.clicked.connect(self.parent.gonderilen_listesi_yenile)
        layout.addWidget(yenile_buton)
        
        # PDF indir
        pdf_indir_buton = QPushButton("PDF İndir")
        pdf_indir_buton.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        pdf_indir_buton.clicked.connect(self.parent.pdf_indir)
        layout.addWidget(pdf_indir_buton)
        
        layout.addStretch()
        
        # Durum çubuğu
        self.parent.gonderilen_durum_label = QLabel("Toplam Gönderilen: 0")
        self.parent.gonderilen_durum_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.parent.gonderilen_durum_label)
        
        return frame
    
    def hatali_ust_butonlar_olustur(self):
        """Hatalı belgeler üst butonları"""
        frame = QFrame()
        layout = QHBoxLayout(frame)
        
        # Yenile
        yenile_buton = QPushButton("YENİLE")
        yenile_buton.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        yenile_buton.clicked.connect(self.parent.hatali_listesi_yenile)
        layout.addWidget(yenile_buton)
        
        # Hataları düzelt
        hatalari_duzelt_buton = QPushButton("Hataları Düzelt")
        hatalari_duzelt_buton.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        hatalari_duzelt_buton.clicked.connect(self.parent.hatalari_duzelt)
        layout.addWidget(hatalari_duzelt_buton)
        
        layout.addStretch()
        
        # Durum çubuğu
        self.parent.hatali_durum_label = QLabel("Toplam Hatalı: 0")
        self.parent.hatali_durum_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.parent.hatali_durum_label)
        
        return frame
    
    # Delegasyon fonksiyonları - veri yöneticisine yönlendir
    def bekleyen_listesi_yenile(self):
        """Bekleyen belgeler listesini yenile"""
        self.veri_yoneticisi.bekleyen_listesi_yenile()
    
    def gonderilen_listesi_yenile(self):
        """Gönderilen belgeler listesini yenile"""
        self.veri_yoneticisi.gonderilen_listesi_yenile()
    
    def hatali_listesi_yenile(self):
        """Hatalı belgeler listesini yenile"""
        self.veri_yoneticisi.hatali_listesi_yenile()
    
    def bekleyen_tablosunu_guncelle(self):
        """Bekleyen belgeler tablosunu güncelle"""
        self.veri_yoneticisi.bekleyen_tablosunu_guncelle()
    
    def gonderilen_tablosunu_guncelle(self):
        """Gönderilen belgeler tablosunu güncelle"""
        self.veri_yoneticisi.gonderilen_tablosunu_guncelle()
    
    def hatali_tablosunu_guncelle(self):
        """Hatalı belgeler tablosunu güncelle"""
        self.veri_yoneticisi.hatali_tablosunu_guncelle()