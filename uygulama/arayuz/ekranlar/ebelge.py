# Version: 0.1.1
# Last Update: 2024-12-16
# Module: uygulama.arayuz.ekranlar.ebelge
# Description: E-belge yönetimi ekranı
# Changelog:
# - İlk sürüm oluşturuldu
# - CSS stil hatası düzeltildi

from PyQt6.QtWidgets import (QHBoxLayout, QVBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QFrame,
                             QGridLayout, QHeaderView, QComboBox, QGroupBox,
                             QSplitter, QTabWidget, QProgressBar, QTextEdit,
                             QLineEdit, QDateEdit, QCheckBox, QSpinBox)
from PyQt6.QtCore import Qt, QTimer, QDate
from PyQt6.QtGui import QFont, QPixmap, QIcon
from .temel_ekran import TemelEkran
from ..servis_fabrikasi import ServisFabrikasi
from ..yardimcilar import UIYardimcilari


class Ebelge(TemelEkran):
    """E-belge yönetimi ekranı"""
    
    def __init__(self, servis_fabrikasi: ServisFabrikasi, parent=None):
        self.bekleyen_tablo = None
        self.gonderilen_tablo = None
        self.hatali_tablo = None
        self.durum_label = None
        self.progress_bar = None
        self.log_text = None
        self.bekleyen_verileri = []
        self.gonderilen_verileri = []
        self.hatali_verileri = []
        super().__init__(servis_fabrikasi, parent)
    
    def ekrani_hazirla(self):
        """E-belge ekranını hazırla"""
        # Ana başlık
        baslik = QLabel("E-belge Yönetimi")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        baslik.setStyleSheet("color: #2c3e50; margin: 10px;")
        self.ana_layout.addWidget(baslik)
        
        # Ana splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sol panel - Filtreler ve işlemler
        sol_panel = self.sol_panel_olustur()
        splitter.addWidget(sol_panel)
        
        # Sağ panel - Sekmeli belge listeleri
        sag_panel = self.sag_panel_olustur()
        splitter.addWidget(sag_panel)
        
        # Splitter oranları
        splitter.setSizes([300, 700])
        
        self.ana_layout.addWidget(splitter)
        self.ekran_hazir = True
    
    def sol_panel_olustur(self):
        """Sol panel - filtreler ve işlemler"""
        panel = QFrame()
        panel.setFixedWidth(300)
        panel.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        layout = QVBoxLayout(panel)
        
        # Filtre grubu
        filtre_grup = self.filtre_grubu_olustur()
        layout.addWidget(filtre_grup)
        
        # İşlemler grubu
        islemler_grup = self.islemler_grubu_olustur()
        layout.addWidget(islemler_grup)
        
        # Durum bilgisi grubu
        durum_grup = self.durum_bilgisi_grubu_olustur()
        layout.addWidget(durum_grup)
        
        layout.addStretch()
        
        return panel
    
    def filtre_grubu_olustur(self):
        """Filtre grubu"""
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
        
        # Belge türü
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
        
        # Tarih aralığı
        tarih_label = QLabel("Tarih Aralığı:")
        layout.addWidget(tarih_label)
        
        tarih_frame = QFrame()
        tarih_layout = QVBoxLayout(tarih_frame)
        
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
        
        # Müşteri filtresi
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
        
        # Filtre uygula butonu
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
        filtre_uygula_buton.clicked.connect(self.filtre_uygula)
        layout.addWidget(filtre_uygula_buton)
        
        return grup
    
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
        gonder_buton.clicked.connect(self.belge_gonder)
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
        durum_sorgula_buton.clicked.connect(self.durum_sorgula)
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
        tekrar_dene_buton.clicked.connect(self.tekrar_dene)
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
        toplu_gonder_buton.clicked.connect(self.toplu_gonder)
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
        xml_goruntule_buton.clicked.connect(self.xml_goruntule)
        layout.addWidget(xml_goruntule_buton)
        
        return grup
    
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
    
    def sag_panel_olustur(self):
        """Sağ panel - sekmeli belge listeleri"""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        # Bekleyen belgeler sekmesi
        bekleyen_tab = self.bekleyen_belgeler_sekmesi_olustur()
        self.tab_widget.addTab(bekleyen_tab, "Bekleyen Belgeler")
        
        # Gönderilen belgeler sekmesi
        gonderilen_tab = self.gonderilen_belgeler_sekmesi_olustur()
        self.tab_widget.addTab(gonderilen_tab, "Gönderilen Belgeler")
        
        # Hatalı belgeler sekmesi
        hatali_tab = self.hatali_belgeler_sekmesi_olustur()
        self.tab_widget.addTab(hatali_tab, "Hatalı Belgeler")
        
        layout.addWidget(self.tab_widget)
        
        return panel
    
    def bekleyen_belgeler_sekmesi_olustur(self):
        """Bekleyen belgeler sekmesi"""
        widget = QFrame()
        layout = QVBoxLayout(widget)
        
        # Üst butonlar
        ust_butonlar = self.bekleyen_ust_butonlar_olustur()
        layout.addWidget(ust_butonlar)
        
        # Bekleyen belgeler tablosu
        self.bekleyen_tablo = QTableWidget()
        self.bekleyen_tablo.setColumnCount(8)
        self.bekleyen_tablo.setHorizontalHeaderLabels([
            "Belge No", "Tür", "Müşteri", "Tutar", "Tarih", "Durum", "Deneme", "İşlemler"
        ])
        
        # Tablo ayarları
        self.tablo_ayarlarini_uygula(self.bekleyen_tablo)
        layout.addWidget(self.bekleyen_tablo)
        
        return widget
    
    def gonderilen_belgeler_sekmesi_olustur(self):
        """Gönderilen belgeler sekmesi"""
        widget = QFrame()
        layout = QVBoxLayout(widget)
        
        # Üst butonlar
        ust_butonlar = self.gonderilen_ust_butonlar_olustur()
        layout.addWidget(ust_butonlar)
        
        # Gönderilen belgeler tablosu
        self.gonderilen_tablo = QTableWidget()
        self.gonderilen_tablo.setColumnCount(9)
        self.gonderilen_tablo.setHorizontalHeaderLabels([
            "Belge No", "Tür", "Müşteri", "Tutar", "Gönderim Tarihi", "UUID", "Durum", "Yanıt", "İşlemler"
        ])
        
        # Tablo ayarları
        self.tablo_ayarlarini_uygula(self.gonderilen_tablo)
        layout.addWidget(self.gonderilen_tablo)
        
        return widget
    
    def hatali_belgeler_sekmesi_olustur(self):
        """Hatalı belgeler sekmesi"""
        widget = QFrame()
        layout = QVBoxLayout(widget)
        
        # Üst butonlar
        ust_butonlar = self.hatali_ust_butonlar_olustur()
        layout.addWidget(ust_butonlar)
        
        # Hatalı belgeler tablosu
        self.hatali_tablo = QTableWidget()
        self.hatali_tablo.setColumnCount(8)
        self.hatali_tablo.setHorizontalHeaderLabels([
            "Belge No", "Tür", "Müşteri", "Tutar", "Hata Tarihi", "Hata Kodu", "Hata Açıklaması", "İşlemler"
        ])
        
        # Tablo ayarları
        self.tablo_ayarlarini_uygula(self.hatali_tablo)
        layout.addWidget(self.hatali_tablo)
        
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
        yenile_buton.clicked.connect(self.bekleyen_listesi_yenile)
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
        secilenleri_gonder_buton.clicked.connect(self.secilenleri_gonder)
        layout.addWidget(secilenleri_gonder_buton)
        
        layout.addStretch()
        
        # Durum çubuğu
        self.bekleyen_durum_label = QLabel("Toplam Bekleyen: 0")
        self.bekleyen_durum_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.bekleyen_durum_label)
        
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
        yenile_buton.clicked.connect(self.gonderilen_listesi_yenile)
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
        pdf_indir_buton.clicked.connect(self.pdf_indir)
        layout.addWidget(pdf_indir_buton)
        
        layout.addStretch()
        
        # Durum çubuğu
        self.gonderilen_durum_label = QLabel("Toplam Gönderilen: 0")
        self.gonderilen_durum_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.gonderilen_durum_label)
        
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
        yenile_buton.clicked.connect(self.hatali_listesi_yenile)
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
        hatalari_duzelt_buton.clicked.connect(self.hatalari_duzelt)
        layout.addWidget(hatalari_duzelt_buton)
        
        layout.addStretch()
        
        # Durum çubuğu
        self.hatali_durum_label = QLabel("Toplam Hatalı: 0")
        self.hatali_durum_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.hatali_durum_label)
        
        return frame
    
    def filtre_uygula(self):
        """Filtre uygula"""
        try:
            # Tüm listeleri yenile
            self.bekleyen_listesi_yenile()
            self.gonderilen_listesi_yenile()
            self.hatali_listesi_yenile()
            
        except Exception as e:
            self.hata_goster("Filtre Hatası", str(e))
    
    def belge_gonder(self):
        """Belge gönderme işlemi"""
        try:
            # E-belge servisini çağır
            ebelge_servisi = self.servis_fabrikasi.ebelge_servisi()
            
            # İşlem başlat
            self.islem_baslat("Belgeler gönderiliyor...")
            
            sonuc = self.servis_cagir_guvenli(ebelge_servisi.gonder)
            
            if sonuc:
                self.bilgi_goster_mesaj("Başarılı", "Belgeler başarıyla gönderildi")
                self.bekleyen_listesi_yenile()
                self.gonderilen_listesi_yenile()
            
            self.islem_bitir()
            
        except Exception as e:
            self.islem_bitir()
            self.hata_goster("Belge Gönderme Hatası", str(e))
    
    def durum_sorgula(self):
        """Durum sorgulama işlemi"""
        try:
            # E-belge servisini çağır
            ebelge_servisi = self.servis_fabrikasi.ebelge_servisi()
            
            # İşlem başlat
            self.islem_baslat("Durum sorgulanıyor...")
            
            sonuc = self.servis_cagir_guvenli(ebelge_servisi.durum_sorgula)
            
            if sonuc:
                self.bilgi_goster_mesaj("Başarılı", "Durum sorgulaması tamamlandı")
                self.gonderilen_listesi_yenile()
            
            self.islem_bitir()
            
        except Exception as e:
            self.islem_bitir()
            self.hata_goster("Durum Sorgulama Hatası", str(e))
    
    def tekrar_dene(self):
        """Tekrar deneme işlemi"""
        try:
            # E-belge servisini çağır
            ebelge_servisi = self.servis_fabrikasi.ebelge_servisi()
            
            # İşlem başlat
            self.islem_baslat("Hatalı belgeler tekrar gönderiliyor...")
            
            sonuc = self.servis_cagir_guvenli(ebelge_servisi.tekrar_dene)
            
            if sonuc:
                self.bilgi_goster_mesaj("Başarılı", "Hatalı belgeler tekrar gönderildi")
                self.hatali_listesi_yenile()
                self.bekleyen_listesi_yenile()
            
            self.islem_bitir()
            
        except Exception as e:
            self.islem_bitir()
            self.hata_goster("Tekrar Deneme Hatası", str(e))
    
    def toplu_gonder(self):
        """Toplu gönderme işlemi"""
        try:
            if not self.onay_iste("Onay", "Tüm bekleyen belgeler gönderilecek. Emin misiniz?"):
                return
            
            # E-belge servisini çağır
            ebelge_servisi = self.servis_fabrikasi.ebelge_servisi()
            
            # İşlem başlat
            self.islem_baslat("Toplu gönderim yapılıyor...")
            
            sonuc = self.servis_cagir_guvenli(ebelge_servisi.gonder)
            
            if sonuc:
                self.bilgi_goster_mesaj("Başarılı", "Toplu gönderim tamamlandı")
                self.bekleyen_listesi_yenile()
                self.gonderilen_listesi_yenile()
            
            self.islem_bitir()
            
        except Exception as e:
            self.islem_bitir()
            self.hata_goster("Toplu Gönderim Hatası", str(e))
    
    def xml_goruntule(self):
        """XML görüntüleme"""
        try:
            # XML görüntüleme dialog'u (stub)
            self.bilgi_goster_mesaj("Bilgi", "XML görüntüleme dialog'u açılacak")
            
        except Exception as e:
            self.hata_goster("XML Görüntüleme Hatası", str(e))
    
    def secilenleri_gonder(self):
        """Seçilen belgeleri gönder"""
        try:
            secili_satirlar = self.bekleyen_tablo.selectionModel().selectedRows()
            if not secili_satirlar:
                self.hata_goster("Hata", "Lütfen gönderilecek belgeleri seçin")
                return
            
            if not self.onay_iste("Onay", f"{len(secili_satirlar)} belge gönderilecek. Emin misiniz?"):
                return
            
            # Seçili belgeleri gönder (stub)
            self.bilgi_goster_mesaj("Başarılı", f"{len(secili_satirlar)} belge gönderildi")
            self.bekleyen_listesi_yenile()
            
        except Exception as e:
            self.hata_goster("Seçili Gönderim Hatası", str(e))
    
    def pdf_indir(self):
        """PDF indirme"""
        try:
            # PDF indirme dialog'u (stub)
            self.bilgi_goster_mesaj("Bilgi", "PDF indirme dialog'u açılacak")
            
        except Exception as e:
            self.hata_goster("PDF İndirme Hatası", str(e))
    
    def hatalari_duzelt(self):
        """Hataları düzeltme"""
        try:
            # Hata düzeltme dialog'u (stub)
            self.bilgi_goster_mesaj("Bilgi", "Hata düzeltme dialog'u açılacak")
            
        except Exception as e:
            self.hata_goster("Hata Düzeltme Hatası", str(e))
    
    def bekleyen_listesi_yenile(self):
        """Bekleyen belgeler listesini yenile"""
        try:
            # Stub bekleyen belge verileri
            self.bekleyen_verileri = [
                {
                    "belge_no": f"BKL{i:06d}",
                    "tur": ["e-Fatura", "e-Arşiv", "e-İrsaliye"][i % 3],
                    "musteri": f"Müşteri {i}",
                    "tutar": (i + 1) * 250.75,
                    "tarih": "2024-12-16",
                    "durum": "Bekliyor",
                    "deneme": i % 3 + 1
                }
                for i in range(1, 8)
            ]
            
            self.bekleyen_tablosunu_guncelle()
            
        except Exception as e:
            self.hata_goster("Liste Yenileme Hatası", str(e))
    
    def gonderilen_listesi_yenile(self):
        """Gönderilen belgeler listesini yenile"""
        try:
            # Stub gönderilen belge verileri
            self.gonderilen_verileri = [
                {
                    "belge_no": f"GND{i:06d}",
                    "tur": ["e-Fatura", "e-Arşiv", "e-İrsaliye"][i % 3],
                    "musteri": f"Müşteri {i}",
                    "tutar": (i + 1) * 180.25,
                    "gonderim_tarihi": "2024-12-16",
                    "uuid": f"uuid-{i:04d}-abcd-efgh",
                    "durum": "Kabul Edildi",
                    "yanit": "Başarılı"
                }
                for i in range(1, 15)
            ]
            
            self.gonderilen_tablosunu_guncelle()
            
        except Exception as e:
            self.hata_goster("Liste Yenileme Hatası", str(e))
    
    def hatali_listesi_yenile(self):
        """Hatalı belgeler listesini yenile"""
        try:
            # Stub hatalı belge verileri
            self.hatali_verileri = [
                {
                    "belge_no": f"HTL{i:06d}",
                    "tur": ["e-Fatura", "e-Arşiv"][i % 2],
                    "musteri": f"Müşteri {i}",
                    "tutar": (i + 1) * 95.50,
                    "hata_tarihi": "2024-12-16",
                    "hata_kodu": f"ERR{i:03d}",
                    "hata_aciklamasi": f"Hata açıklaması {i}"
                }
                for i in range(1, 4)
            ]
            
            self.hatali_tablosunu_guncelle()
            
        except Exception as e:
            self.hata_goster("Liste Yenileme Hatası", str(e))
    
    def bekleyen_tablosunu_guncelle(self):
        """Bekleyen belgeler tablosunu güncelle"""
        try:
            self.bekleyen_tablo.setRowCount(len(self.bekleyen_verileri))
            
            for row, belge in enumerate(self.bekleyen_verileri):
                self.bekleyen_tablo.setItem(row, 0, QTableWidgetItem(belge["belge_no"]))
                self.bekleyen_tablo.setItem(row, 1, QTableWidgetItem(belge["tur"]))
                self.bekleyen_tablo.setItem(row, 2, QTableWidgetItem(belge["musteri"]))
                self.bekleyen_tablo.setItem(row, 3, QTableWidgetItem(
                    UIYardimcilari.para_formatla(belge["tutar"])
                ))
                self.bekleyen_tablo.setItem(row, 4, QTableWidgetItem(
                    UIYardimcilari.tarih_formatla(belge["tarih"])
                ))
                self.bekleyen_tablo.setItem(row, 5, QTableWidgetItem(belge["durum"]))
                self.bekleyen_tablo.setItem(row, 6, QTableWidgetItem(str(belge["deneme"])))
                
                # İşlemler butonu
                islem_buton = QPushButton("Gönder")
                islem_buton.setStyleSheet("""
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 4px 8px;
                        font-size: 10px;
                    }
                """)
                self.bekleyen_tablo.setCellWidget(row, 7, islem_buton)
            
            # Durum çubuğunu güncelle
            self.bekleyen_durum_label.setText(f"Toplam Bekleyen: {len(self.bekleyen_verileri)}")
            self.bekleyen_sayisi_label.setText(f"Bekleyen: {len(self.bekleyen_verileri)}")
            
        except Exception as e:
            self.hata_goster("Tablo Güncelleme Hatası", str(e))
    
    def gonderilen_tablosunu_guncelle(self):
        """Gönderilen belgeler tablosunu güncelle"""
        try:
            self.gonderilen_tablo.setRowCount(len(self.gonderilen_verileri))
            
            for row, belge in enumerate(self.gonderilen_verileri):
                self.gonderilen_tablo.setItem(row, 0, QTableWidgetItem(belge["belge_no"]))
                self.gonderilen_tablo.setItem(row, 1, QTableWidgetItem(belge["tur"]))
                self.gonderilen_tablo.setItem(row, 2, QTableWidgetItem(belge["musteri"]))
                self.gonderilen_tablo.setItem(row, 3, QTableWidgetItem(
                    UIYardimcilari.para_formatla(belge["tutar"])
                ))
                self.gonderilen_tablo.setItem(row, 4, QTableWidgetItem(
                    UIYardimcilari.tarih_formatla(belge["gonderim_tarihi"])
                ))
                self.gonderilen_tablo.setItem(row, 5, QTableWidgetItem(belge["uuid"]))
                
                # Durum - renk kodlaması
                durum_item = QTableWidgetItem(belge["durum"])
                durum_item.setBackground(Qt.GlobalColor.green)
                durum_item.setForeground(Qt.GlobalColor.white)
                self.gonderilen_tablo.setItem(row, 6, durum_item)
                
                self.gonderilen_tablo.setItem(row, 7, QTableWidgetItem(belge["yanit"]))
                
                # İşlemler butonu
                islem_buton = QPushButton("PDF")
                islem_buton.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 4px 8px;
                        font-size: 10px;
                    }
                """)
                self.gonderilen_tablo.setCellWidget(row, 8, islem_buton)
            
            # Durum çubuğunu güncelle
            self.gonderilen_durum_label.setText(f"Toplam Gönderilen: {len(self.gonderilen_verileri)}")
            self.gonderilen_sayisi_label.setText(f"Gönderilen: {len(self.gonderilen_verileri)}")
            
        except Exception as e:
            self.hata_goster("Tablo Güncelleme Hatası", str(e))
    
    def hatali_tablosunu_guncelle(self):
        """Hatalı belgeler tablosunu güncelle"""
        try:
            self.hatali_tablo.setRowCount(len(self.hatali_verileri))
            
            for row, belge in enumerate(self.hatali_verileri):
                self.hatali_tablo.setItem(row, 0, QTableWidgetItem(belge["belge_no"]))
                self.hatali_tablo.setItem(row, 1, QTableWidgetItem(belge["tur"]))
                self.hatali_tablo.setItem(row, 2, QTableWidgetItem(belge["musteri"]))
                self.hatali_tablo.setItem(row, 3, QTableWidgetItem(
                    UIYardimcilari.para_formatla(belge["tutar"])
                ))
                self.hatali_tablo.setItem(row, 4, QTableWidgetItem(
                    UIYardimcilari.tarih_formatla(belge["hata_tarihi"])
                ))
                self.hatali_tablo.setItem(row, 5, QTableWidgetItem(belge["hata_kodu"]))
                self.hatali_tablo.setItem(row, 6, QTableWidgetItem(belge["hata_aciklamasi"]))
                
                # İşlemler butonu
                islem_buton = QPushButton("Düzelt")
                islem_buton.setStyleSheet("""
                    QPushButton {
                        background-color: #f39c12;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 4px 8px;
                        font-size: 10px;
                    }
                """)
                self.hatali_tablo.setCellWidget(row, 7, islem_buton)
            
            # Durum çubuğunu güncelle
            self.hatali_durum_label.setText(f"Toplam Hatalı: {len(self.hatali_verileri)}")
            self.hatali_sayisi_label.setText(f"Hatalı: {len(self.hatali_verileri)}")
            
        except Exception as e:
            self.hata_goster("Tablo Güncelleme Hatası", str(e))
    
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
    
    def verileri_yukle(self):
        """Ekran açıldığında"""
        # Tüm listeleri yükle
        self.bekleyen_listesi_yenile()
        self.gonderilen_listesi_yenile()
        self.hatali_listesi_yenile()
    
    def verileri_temizle(self):
        """Ekran kapandığında"""
        pass