# Version: 0.1.0
# Last Update: 2024-12-16
# Module: uygulama.arayuz.ekranlar.raporlar
# Description: Raporlar ekranı
# Changelog:
# - İlk sürüm oluşturuldu

from PyQt6.QtWidgets import (QHBoxLayout, QVBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QFrame,
                             QGridLayout, QHeaderView, QComboBox, QGroupBox,
                             QSplitter, QTabWidget, QProgressBar, QTextEdit,
                             QLineEdit, QDateEdit, QCheckBox, QSpinBox,
                             QScrollArea, QWidget)
from PyQt6.QtCore import Qt, QTimer, QDate
from PyQt6.QtGui import QFont, QPixmap, QIcon
from .temel_ekran import TemelEkran
from ..servis_fabrikasi import ServisFabrikasi
from ..yardimcilar import UIYardimcilari


class Raporlar(TemelEkran):
    """Raporlar ekranı"""
    
    def __init__(self, servis_fabrikasi: ServisFabrikasi, parent=None):
        self.rapor_tablo = None
        self.durum_label = None
        self.progress_bar = None
        self.rapor_verileri = []
        self.aktif_rapor_tipi = None
        super().__init__(servis_fabrikasi, parent)
    
    def ekrani_hazirla(self):
        """Raporlar ekranını hazırla"""
        # Ana başlık
        baslik = QLabel("Raporlar")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        baslik.setStyleSheet("color: #2c3e50; margin: 10px;")
        self.ana_layout.addWidget(baslik)
        
        # Ana splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sol panel - Rapor parametreleri
        sol_panel = self.sol_panel_olustur()
        splitter.addWidget(sol_panel)
        
        # Sağ panel - Rapor sonuçları
        sag_panel = self.sag_panel_olustur()
        splitter.addWidget(sag_panel)
        
        # Splitter oranları
        splitter.setSizes([350, 650])
        
        self.ana_layout.addWidget(splitter)
        self.ekran_hazir = True
    
    def sol_panel_olustur(self):
        """Sol panel - rapor parametreleri"""
        panel = QFrame()
        panel.setFixedWidth(350)
        panel.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        # Scroll area oluştur
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        
        # Rapor türü seçimi grubu
        rapor_turu_grup = self.rapor_turu_grubu_olustur()
        layout.addWidget(rapor_turu_grup)
        
        # Tarih aralığı grubu
        tarih_grup = self.tarih_araligi_grubu_olustur()
        layout.addWidget(tarih_grup)
        
        # Filtreler grubu
        filtreler_grup = self.filtreler_grubu_olustur()
        layout.addWidget(filtreler_grup)
        
        # Rapor oluşturma grubu
        olusturma_grup = self.rapor_olusturma_grubu_olustur()
        layout.addWidget(olusturma_grup)
        
        # Durum bilgisi grubu
        durum_grup = self.durum_bilgisi_grubu_olustur()
        layout.addWidget(durum_grup)
        
        layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        
        panel_layout = QVBoxLayout(panel)
        panel_layout.addWidget(scroll)
        
        return panel
    
    def rapor_turu_grubu_olustur(self):
        """Rapor türü seçimi grubu"""
        grup = QGroupBox("Rapor Türü")
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
        
        # Rapor türü combo
        rapor_turu_label = QLabel("Rapor Seçin:")
        layout.addWidget(rapor_turu_label)
        
        self.rapor_turu_combo = QComboBox()
        self.rapor_turu_combo.addItems([
            "Satış Raporu",
            "Stok Raporu", 
            "Müşteri Raporu",
            "Finansal Rapor",
            "E-ticaret Raporu",
            "Kargo Raporu",
            "E-belge Raporu",
            "Performans Raporu"
        ])
        self.rapor_turu_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 12px;
            }
        """)
        self.rapor_turu_combo.currentTextChanged.connect(self.rapor_turu_degisti)
        layout.addWidget(self.rapor_turu_combo)
        
        # Alt rapor türü
        self.alt_rapor_label = QLabel("Alt Kategori:")
        layout.addWidget(self.alt_rapor_label)
        
        self.alt_rapor_combo = QComboBox()
        self.alt_rapor_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.alt_rapor_combo)
        
        return grup
    
    def tarih_araligi_grubu_olustur(self):
        """Tarih aralığı grubu"""
        grup = QGroupBox("Tarih Aralığı")
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
        
        # Hızlı seçim butonları
        hizli_secim_frame = QFrame()
        hizli_layout = QGridLayout(hizli_secim_frame)
        
        bugun_buton = QPushButton("Bugün")
        bugun_buton.setStyleSheet(self.kucuk_buton_stili())
        bugun_buton.clicked.connect(lambda: self.hizli_tarih_sec("bugun"))
        hizli_layout.addWidget(bugun_buton, 0, 0)
        
        dun_buton = QPushButton("Dün")
        dun_buton.setStyleSheet(self.kucuk_buton_stili())
        dun_buton.clicked.connect(lambda: self.hizli_tarih_sec("dun"))
        hizli_layout.addWidget(dun_buton, 0, 1)
        
        bu_hafta_buton = QPushButton("Bu Hafta")
        bu_hafta_buton.setStyleSheet(self.kucuk_buton_stili())
        bu_hafta_buton.clicked.connect(lambda: self.hizli_tarih_sec("bu_hafta"))
        hizli_layout.addWidget(bu_hafta_buton, 1, 0)
        
        bu_ay_buton = QPushButton("Bu Ay")
        bu_ay_buton.setStyleSheet(self.kucuk_buton_stili())
        bu_ay_buton.clicked.connect(lambda: self.hizli_tarih_sec("bu_ay"))
        hizli_layout.addWidget(bu_ay_buton, 1, 1)
        
        layout.addWidget(hizli_secim_frame)
        
        # Manuel tarih seçimi
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
        
        return grup
    
    def filtreler_grubu_olustur(self):
        """Filtreler grubu"""
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
        
        # Mağaza seçimi
        magaza_label = QLabel("Mağaza:")
        layout.addWidget(magaza_label)
        
        self.magaza_combo = QComboBox()
        self.magaza_combo.addItems([
            "Tüm Mağazalar", "Ana Mağaza", "Şube 1", "Şube 2", "Online Mağaza"
        ])
        self.magaza_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.magaza_combo)
        
        # Kullanıcı filtresi
        kullanici_label = QLabel("Kullanıcı:")
        layout.addWidget(kullanici_label)
        
        self.kullanici_combo = QComboBox()
        self.kullanici_combo.addItems([
            "Tüm Kullanıcılar", "Admin", "Kasiyer 1", "Kasiyer 2", "Müdür"
        ])
        self.kullanici_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.kullanici_combo)
        
        # Kategori filtresi
        kategori_label = QLabel("Kategori:")
        layout.addWidget(kategori_label)
        
        self.kategori_combo = QComboBox()
        self.kategori_combo.addItems([
            "Tüm Kategoriler", "Elektronik", "Giyim", "Ev & Yaşam", "Spor"
        ])
        self.kategori_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.kategori_combo)
        
        # Detay seviyesi
        detay_label = QLabel("Detay Seviyesi:")
        layout.addWidget(detay_label)
        
        self.detay_combo = QComboBox()
        self.detay_combo.addItems([
            "Özet", "Detaylı", "Çok Detaylı"
        ])
        self.detay_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.detay_combo)
        
        return grup
    
    def rapor_olusturma_grubu_olustur(self):
        """Rapor oluşturma grubu"""
        grup = QGroupBox("Rapor Oluştur")
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
        
        # Rapor oluştur butonu
        rapor_olustur_buton = QPushButton("Rapor Oluştur")
        rapor_olustur_buton.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        rapor_olustur_buton.clicked.connect(self.rapor_olustur)
        layout.addWidget(rapor_olustur_buton)
        
        # Dışa aktarma seçenekleri
        disa_aktar_frame = QFrame()
        disa_aktar_layout = QGridLayout(disa_aktar_frame)
        
        excel_buton = QPushButton("Excel")
        excel_buton.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        excel_buton.clicked.connect(lambda: self.disa_aktar("excel"))
        disa_aktar_layout.addWidget(excel_buton, 0, 0)
        
        pdf_buton = QPushButton("PDF")
        pdf_buton.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        pdf_buton.clicked.connect(lambda: self.disa_aktar("pdf"))
        disa_aktar_layout.addWidget(pdf_buton, 0, 1)
        
        csv_buton = QPushButton("CSV")
        csv_buton.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        csv_buton.clicked.connect(lambda: self.disa_aktar("csv"))
        disa_aktar_layout.addWidget(csv_buton, 1, 0)
        
        yazdir_buton = QPushButton("Yazdır")
        yazdir_buton.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        yazdir_buton.clicked.connect(self.yazdir)
        disa_aktar_layout.addWidget(yazdir_buton, 1, 1)
        
        layout.addWidget(disa_aktar_frame)
        
        return grup
    
    def durum_bilgisi_grubu_olustur(self):
        """Durum bilgisi grubu"""
        grup = QGroupBox("Durum")
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
        
        # Son rapor bilgisi
        self.son_rapor_label = QLabel("Son Rapor: Henüz oluşturulmadı")
        self.son_rapor_label.setStyleSheet("font-size: 10px; color: #7f8c8d;")
        layout.addWidget(self.son_rapor_label)
        
        return grup
    
    def sag_panel_olustur(self):
        """Sağ panel - rapor sonuçları"""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        
        # Üst bilgi çubuğu
        ust_bilgi = self.ust_bilgi_cubugun_olustur()
        layout.addWidget(ust_bilgi)
        
        # Rapor tablosu
        self.rapor_tablo = QTableWidget()
        self.rapor_tablo.setColumnCount(6)
        self.rapor_tablo.setHorizontalHeaderLabels([
            "Tarih", "Açıklama", "Miktar", "Tutar", "Kategori", "Durum"
        ])
        
        # Tablo ayarları
        header = self.rapor_tablo.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        self.rapor_tablo.setAlternatingRowColors(True)
        self.rapor_tablo.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.rapor_tablo.setStyleSheet("""
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        layout.addWidget(self.rapor_tablo)
        
        # Alt özet bilgileri
        alt_ozet = self.alt_ozet_olustur()
        layout.addWidget(alt_ozet)
        
        return panel
    
    def ust_bilgi_cubugun_olustur(self):
        """Üst bilgi çubuğu"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        layout = QHBoxLayout(frame)
        
        # Rapor başlığı
        self.rapor_baslik_label = QLabel("Rapor Sonuçları")
        self.rapor_baslik_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50;")
        layout.addWidget(self.rapor_baslik_label)
        
        layout.addStretch()
        
        # Kayıt sayısı
        self.kayit_sayisi_label = QLabel("Toplam Kayıt: 0")
        self.kayit_sayisi_label.setStyleSheet("font-weight: bold; color: #7f8c8d;")
        layout.addWidget(self.kayit_sayisi_label)
        
        return frame
    
    def alt_ozet_olustur(self):
        """Alt özet bilgileri"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        layout = QHBoxLayout(frame)
        
        # Özet kartları
        self.toplam_tutar_label = QLabel("Toplam Tutar: ₺0,00")
        self.toplam_tutar_label.setStyleSheet("""
            QLabel {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.toplam_tutar_label)
        
        self.ortalama_label = QLabel("Ortalama: ₺0,00")
        self.ortalama_label.setStyleSheet("""
            QLabel {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.ortalama_label)
        
        self.en_yuksek_label = QLabel("En Yüksek: ₺0,00")
        self.en_yuksek_label.setStyleSheet("""
            QLabel {
                background-color: #e67e22;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.en_yuksek_label)
        
        layout.addStretch()
        
        return frame
    
    def kucuk_buton_stili(self):
        """Küçük buton stili"""
        return """
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """
    
    def rapor_turu_degisti(self):
        """Rapor türü değiştiğinde"""
        try:
            secili_rapor = self.rapor_turu_combo.currentText()
            self.aktif_rapor_tipi = secili_rapor
            
            # Alt rapor türlerini güncelle
            alt_turler = {
                "Satış Raporu": ["Günlük Satış", "Ürün Bazlı", "Müşteri Bazlı", "Kasiyer Bazlı"],
                "Stok Raporu": ["Stok Durumu", "Kritik Stok", "Stok Hareketleri", "Sayım Raporu"],
                "Müşteri Raporu": ["Müşteri Listesi", "Sadakat Puanları", "Alışveriş Geçmişi"],
                "Finansal Raporu": ["Gelir-Gider", "Kâr-Zarar", "Nakit Akışı", "Vergi Raporu"],
                "E-ticaret Raporu": ["Sipariş Raporu", "Mağaza Performansı", "İade Raporu"],
                "Kargo Raporu": ["Kargo Durumu", "Taşıyıcı Performansı", "Teslimat Süreleri"],
                "E-belge Raporu": ["Gönderim Durumu", "Hata Raporu", "Belge Türü Bazlı"],
                "Performans Raporu": ["Sistem Performansı", "Kullanıcı Aktivitesi", "Hata Logları"]
            }
            
            self.alt_rapor_combo.clear()
            if secili_rapor in alt_turler:
                self.alt_rapor_combo.addItems(alt_turler[secili_rapor])
            
        except Exception as e:
            self.hata_goster("Rapor Türü Seçim Hatası", str(e))
    
    def hizli_tarih_sec(self, tur: str):
        """Hızlı tarih seçimi"""
        try:
            bugun = QDate.currentDate()
            
            if tur == "bugun":
                self.baslangic_tarih.setDate(bugun)
                self.bitis_tarih.setDate(bugun)
            elif tur == "dun":
                dun = bugun.addDays(-1)
                self.baslangic_tarih.setDate(dun)
                self.bitis_tarih.setDate(dun)
            elif tur == "bu_hafta":
                hafta_basi = bugun.addDays(-bugun.dayOfWeek() + 1)
                self.baslangic_tarih.setDate(hafta_basi)
                self.bitis_tarih.setDate(bugun)
            elif tur == "bu_ay":
                ay_basi = QDate(bugun.year(), bugun.month(), 1)
                self.baslangic_tarih.setDate(ay_basi)
                self.bitis_tarih.setDate(bugun)
            
        except Exception as e:
            self.hata_goster("Tarih Seçim Hatası", str(e))
    
    def rapor_olustur(self):
        """Rapor oluşturma işlemi"""
        try:
            if not self.aktif_rapor_tipi:
                self.hata_goster("Hata", "Lütfen bir rapor türü seçin")
                return
            
            # Rapor servisini çağır
            rapor_servisi = self.servis_fabrikasi.rapor_servisi()
            
            # İşlem başlat
            self.islem_baslat("Rapor oluşturuluyor...")
            
            # Parametreleri hazırla
            parametreler = {
                "rapor_turu": self.aktif_rapor_tipi,
                "alt_tur": self.alt_rapor_combo.currentText(),
                "baslangic_tarih": self.baslangic_tarih.date().toString("yyyy-MM-dd"),
                "bitis_tarih": self.bitis_tarih.date().toString("yyyy-MM-dd"),
                "magaza": self.magaza_combo.currentText(),
                "kullanici": self.kullanici_combo.currentText(),
                "kategori": self.kategori_combo.currentText(),
                "detay_seviye": self.detay_combo.currentText()
            }
            
            sonuc = self.servis_cagir_guvenli(
                rapor_servisi.rapor_olustur, 
                parametreler
            )
            
            if sonuc:
                self.rapor_verilerini_yukle()
                self.bilgi_goster_mesaj("Başarılı", "Rapor başarıyla oluşturuldu")
            
            self.islem_bitir()
            
        except Exception as e:
            self.islem_bitir()
            self.hata_goster("Rapor Oluşturma Hatası", str(e))
    
    def disa_aktar(self, format_turu: str):
        """Dışa aktarma işlemi"""
        try:
            if not self.rapor_verileri:
                self.hata_goster("Hata", "Önce bir rapor oluşturun")
                return
            
            # Dışa aktarma dialog'u (stub)
            self.bilgi_goster_mesaj("Bilgi", f"Rapor {format_turu.upper()} formatında dışa aktarılacak")
            
        except Exception as e:
            self.hata_goster("Dışa Aktarma Hatası", str(e))
    
    def yazdir(self):
        """Yazdırma işlemi"""
        try:
            if not self.rapor_verileri:
                self.hata_goster("Hata", "Önce bir rapor oluşturun")
                return
            
            # Yazdırma dialog'u (stub)
            self.bilgi_goster_mesaj("Bilgi", "Yazdırma dialog'u açılacak")
            
        except Exception as e:
            self.hata_goster("Yazdırma Hatası", str(e))
    
    def rapor_verilerini_yukle(self):
        """Rapor verilerini yükle"""
        try:
            # Stub rapor verileri
            self.rapor_verileri = [
                {
                    "tarih": "2024-12-16",
                    "aciklama": f"İşlem {i}",
                    "miktar": i + 5,
                    "tutar": (i + 1) * 125.75,
                    "kategori": ["Elektronik", "Giyim", "Ev & Yaşam"][i % 3],
                    "durum": ["Tamamlandı", "Beklemede", "İptal"][i % 3]
                }
                for i in range(1, 21)
            ]
            
            self.rapor_tablosunu_guncelle()
            
        except Exception as e:
            self.hata_goster("Veri Yükleme Hatası", str(e))
    
    def rapor_tablosunu_guncelle(self):
        """Rapor tablosunu güncelle"""
        try:
            self.rapor_tablo.setRowCount(len(self.rapor_verileri))
            
            toplam_tutar = 0
            en_yuksek = 0
            
            for row, veri in enumerate(self.rapor_verileri):
                self.rapor_tablo.setItem(row, 0, QTableWidgetItem(
                    UIYardimcilari.tarih_formatla(veri["tarih"])
                ))
                self.rapor_tablo.setItem(row, 1, QTableWidgetItem(veri["aciklama"]))
                self.rapor_tablo.setItem(row, 2, QTableWidgetItem(str(veri["miktar"])))
                
                tutar_item = QTableWidgetItem(UIYardimcilari.para_formatla(veri["tutar"]))
                self.rapor_tablo.setItem(row, 3, tutar_item)
                
                self.rapor_tablo.setItem(row, 4, QTableWidgetItem(veri["kategori"]))
                
                # Durum - renk kodlaması
                durum_item = QTableWidgetItem(veri["durum"])
                if veri["durum"] == "Tamamlandı":
                    durum_item.setBackground(Qt.GlobalColor.green)
                    durum_item.setForeground(Qt.GlobalColor.white)
                elif veri["durum"] == "Beklemede":
                    durum_item.setBackground(Qt.GlobalColor.yellow)
                elif veri["durum"] == "İptal":
                    durum_item.setBackground(Qt.GlobalColor.red)
                    durum_item.setForeground(Qt.GlobalColor.white)
                self.rapor_tablo.setItem(row, 5, durum_item)
                
                # Hesaplamalar
                toplam_tutar += veri["tutar"]
                if veri["tutar"] > en_yuksek:
                    en_yuksek = veri["tutar"]
            
            # Başlık ve sayaçları güncelle
            self.rapor_baslik_label.setText(f"{self.aktif_rapor_tipi} - {self.alt_rapor_combo.currentText()}")
            self.kayit_sayisi_label.setText(f"Toplam Kayıt: {len(self.rapor_verileri)}")
            
            # Özet bilgileri güncelle
            self.toplam_tutar_label.setText(f"Toplam Tutar: {UIYardimcilari.para_formatla(toplam_tutar)}")
            
            ortalama = toplam_tutar / len(self.rapor_verileri) if self.rapor_verileri else 0
            self.ortalama_label.setText(f"Ortalama: {UIYardimcilari.para_formatla(ortalama)}")
            
            self.en_yuksek_label.setText(f"En Yüksek: {UIYardimcilari.para_formatla(en_yuksek)}")
            
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
        
        # Son rapor zamanını güncelle
        from datetime import datetime
        simdi = datetime.now().strftime("%d.%m.%Y %H:%M")
        self.son_rapor_label.setText(f"Son Rapor: {simdi}")
    
    def verileri_yukle(self):
        """Ekran açıldığında"""
        # İlk rapor türünü seç
        if self.rapor_turu_combo.count() > 0:
            self.rapor_turu_combo.setCurrentIndex(0)
            self.rapor_turu_degisti()
    
    def verileri_temizle(self):
        """Ekran kapandığında"""
        pass