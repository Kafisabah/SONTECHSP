# Version: 0.1.0
# Last Update: 2024-12-16
# Module: uygulama.arayuz.ekranlar.ayarlar
# Description: Ayarlar ekranı
# Changelog:
# - İlk sürüm oluşturuldu

from PyQt6.QtWidgets import (QHBoxLayout, QVBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QFrame,
                             QGridLayout, QHeaderView, QComboBox, QGroupBox,
                             QSplitter, QTabWidget, QProgressBar, QTextEdit,
                             QLineEdit, QDateEdit, QCheckBox, QSpinBox,
                             QScrollArea, QWidget, QListWidget, QListWidgetItem,
                             QStackedWidget, QFormLayout, QSlider, QDoubleSpinBox)
from PyQt6.QtCore import Qt, QTimer, QDate
from PyQt6.QtGui import QFont, QPixmap, QIcon
from .temel_ekran import TemelEkran
from ..servis_fabrikasi import ServisFabrikasi
from ..yardimcilar import UIYardimcilari


class Ayarlar(TemelEkran):
    """Ayarlar ekranı"""
    
    def __init__(self, servis_fabrikasi: ServisFabrikasi, parent=None):
        self.kategori_listesi = None
        self.icerik_stack = None
        self.durum_label = None
        self.progress_bar = None
        self.degisiklikler = {}
        super().__init__(servis_fabrikasi, parent)
    
    def ekrani_hazirla(self):
        """Ayarlar ekranını hazırla"""
        # Ana başlık
        baslik = QLabel("Sistem Ayarları")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        baslik.setStyleSheet("color: #2c3e50; margin: 10px;")
        self.ana_layout.addWidget(baslik)
        
        # Ana splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sol panel - Kategori listesi
        sol_panel = self.sol_panel_olustur()
        splitter.addWidget(sol_panel)
        
        # Sağ panel - Ayar içerikleri
        sag_panel = self.sag_panel_olustur()
        splitter.addWidget(sag_panel)
        
        # Splitter oranları
        splitter.setSizes([250, 750])
        
        self.ana_layout.addWidget(splitter)
        
        # Alt butonlar
        alt_butonlar = self.alt_butonlar_olustur()
        self.ana_layout.addWidget(alt_butonlar)
        
        self.ekran_hazir = True
    
    def sol_panel_olustur(self):
        """Sol panel - kategori listesi"""
        panel = QFrame()
        panel.setFixedWidth(250)
        panel.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        layout = QVBoxLayout(panel)
        
        # Kategori başlığı
        kategori_baslik = QLabel("Ayar Kategorileri")
        kategori_baslik.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(kategori_baslik)
        
        # Kategori listesi
        self.kategori_listesi = QListWidget()
        self.kategori_listesi.setStyleSheet("""
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
            }
        """)
        
        # Kategorileri ekle
        kategoriler = [
            "Genel Ayarlar",
            "Veritabanı",
            "POS Ayarları", 
            "Stok Yönetimi",
            "E-ticaret",
            "E-belge",
            "Kargo",
            "Kullanıcılar",
            "Yetkilendirme",
            "Raporlar",
            "Sistem",
            "Yedekleme"
        ]
        
        for kategori in kategoriler:
            item = QListWidgetItem(kategori)
            self.kategori_listesi.addItem(item)
        
        self.kategori_listesi.currentRowChanged.connect(self.kategori_degisti)
        layout.addWidget(self.kategori_listesi)
        
        # Durum bilgisi
        durum_grup = self.durum_bilgisi_grubu_olustur()
        layout.addWidget(durum_grup)
        
        return panel
    
    def sag_panel_olustur(self):
        """Sağ panel - ayar içerikleri"""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        
        # İçerik başlığı
        self.icerik_baslik = QLabel("Ayar Seçin")
        self.icerik_baslik.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(self.icerik_baslik)
        
        # Stacked widget - farklı ayar sayfaları
        self.icerik_stack = QStackedWidget()
        
        # Ayar sayfalarını oluştur
        self.genel_ayarlar_sayfasi_olustur()
        self.veritabani_ayarlar_sayfasi_olustur()
        self.pos_ayarlar_sayfasi_olustur()
        self.stok_ayarlar_sayfasi_olustur()
        self.eticaret_ayarlar_sayfasi_olustur()
        self.ebelge_ayarlar_sayfasi_olustur()
        self.kargo_ayarlar_sayfasi_olustur()
        self.kullanici_ayarlar_sayfasi_olustur()
        self.yetki_ayarlar_sayfasi_olustur()
        self.rapor_ayarlar_sayfasi_olustur()
        self.sistem_ayarlar_sayfasi_olustur()
        self.yedekleme_ayarlar_sayfasi_olustur()
        
        layout.addWidget(self.icerik_stack)
        
        return panel
    
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
        
        # Değişiklik sayısı
        self.degisiklik_label = QLabel("Değişiklik: 0")
        self.degisiklik_label.setStyleSheet("font-size: 10px; color: #7f8c8d;")
        layout.addWidget(self.degisiklik_label)
        
        return grup
    
    def alt_butonlar_olustur(self):
        """Alt butonlar"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        layout = QHBoxLayout(frame)
        
        # Varsayılana dön
        varsayilan_buton = QPushButton("Varsayılana Dön")
        varsayilan_buton.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        varsayilan_buton.clicked.connect(self.varsayilana_don)
        layout.addWidget(varsayilan_buton)
        
        # İçe aktar
        ice_aktar_buton = QPushButton("İçe Aktar")
        ice_aktar_buton.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        ice_aktar_buton.clicked.connect(self.ice_aktar)
        layout.addWidget(ice_aktar_buton)
        
        # Dışa aktar
        disa_aktar_buton = QPushButton("Dışa Aktar")
        disa_aktar_buton.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        disa_aktar_buton.clicked.connect(self.disa_aktar)
        layout.addWidget(disa_aktar_buton)
        
        layout.addStretch()
        
        # İptal
        iptal_buton = QPushButton("İptal")
        iptal_buton.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        iptal_buton.clicked.connect(self.degisiklikleri_iptal)
        layout.addWidget(iptal_buton)
        
        # Kaydet
        kaydet_buton = QPushButton("Kaydet")
        kaydet_buton.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        kaydet_buton.clicked.connect(self.ayarlari_kaydet)
        layout.addWidget(kaydet_buton)
        
        return frame
    
    def genel_ayarlar_sayfasi_olustur(self):
        """Genel ayarlar sayfası"""
        sayfa = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(sayfa)
        
        layout = QVBoxLayout(sayfa)
        
        # Şirket bilgileri grubu
        sirket_grup = QGroupBox("Şirket Bilgileri")
        sirket_grup.setStyleSheet(self.grup_stili())
        sirket_layout = QFormLayout(sirket_grup)
        
        self.sirket_adi = QLineEdit("SONTECH SP")
        sirket_layout.addRow("Şirket Adı:", self.sirket_adi)
        
        self.vergi_no = QLineEdit("1234567890")
        sirket_layout.addRow("Vergi No:", self.vergi_no)
        
        self.adres = QTextEdit("İstanbul, Türkiye")
        self.adres.setMaximumHeight(80)
        sirket_layout.addRow("Adres:", self.adres)
        
        layout.addWidget(sirket_grup)
        
        # Uygulama ayarları grubu
        uygulama_grup = QGroupBox("Uygulama Ayarları")
        uygulama_grup.setStyleSheet(self.grup_stili())
        uygulama_layout = QFormLayout(uygulama_grup)
        
        self.dil_combo = QComboBox()
        self.dil_combo.addItems(["Türkçe", "English"])
        uygulama_layout.addRow("Dil:", self.dil_combo)
        
        self.tema_combo = QComboBox()
        self.tema_combo.addItems(["Açık Tema", "Koyu Tema", "Otomatik"])
        uygulama_layout.addRow("Tema:", self.tema_combo)
        
        self.otomatik_yedekleme = QCheckBox("Otomatik yedekleme aktif")
        self.otomatik_yedekleme.setChecked(True)
        uygulama_layout.addRow("", self.otomatik_yedekleme)
        
        layout.addWidget(uygulama_grup)
        layout.addStretch()
        
        self.icerik_stack.addWidget(scroll)
    
    def veritabani_ayarlar_sayfasi_olustur(self):
        """Veritabanı ayarlar sayfası"""
        sayfa = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(sayfa)
        
        layout = QVBoxLayout(sayfa)
        
        # PostgreSQL ayarları
        postgres_grup = QGroupBox("PostgreSQL Bağlantısı")
        postgres_grup.setStyleSheet(self.grup_stili())
        postgres_layout = QFormLayout(postgres_grup)
        
        self.db_host = QLineEdit("localhost")
        postgres_layout.addRow("Host:", self.db_host)
        
        self.db_port = QSpinBox()
        self.db_port.setRange(1, 65535)
        self.db_port.setValue(5432)
        postgres_layout.addRow("Port:", self.db_port)
        
        self.db_name = QLineEdit("sontechsp")
        postgres_layout.addRow("Veritabanı Adı:", self.db_name)
        
        self.db_user = QLineEdit("postgres")
        postgres_layout.addRow("Kullanıcı:", self.db_user)
        
        self.db_password = QLineEdit()
        self.db_password.setEchoMode(QLineEdit.EchoMode.Password)
        postgres_layout.addRow("Şifre:", self.db_password)
        
        baglanti_test_buton = QPushButton("Bağlantıyı Test Et")
        baglanti_test_buton.clicked.connect(self.baglanti_test)
        postgres_layout.addRow("", baglanti_test_buton)
        
        layout.addWidget(postgres_grup)
        
        # Performans ayarları
        performans_grup = QGroupBox("Performans Ayarları")
        performans_grup.setStyleSheet(self.grup_stili())
        performans_layout = QFormLayout(performans_grup)
        
        self.baglanti_havuzu = QSpinBox()
        self.baglanti_havuzu.setRange(5, 100)
        self.baglanti_havuzu.setValue(20)
        performans_layout.addRow("Bağlantı Havuzu:", self.baglanti_havuzu)
        
        self.sorgu_timeout = QSpinBox()
        self.sorgu_timeout.setRange(5, 300)
        self.sorgu_timeout.setValue(30)
        self.sorgu_timeout.setSuffix(" saniye")
        performans_layout.addRow("Sorgu Timeout:", self.sorgu_timeout)
        
        layout.addWidget(performans_grup)
        layout.addStretch()
        
        self.icerik_stack.addWidget(scroll)
    
    def pos_ayarlar_sayfasi_olustur(self):
        """POS ayarlar sayfası"""
        sayfa = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(sayfa)
        
        layout = QVBoxLayout(sayfa)
        
        # Genel POS ayarları
        pos_grup = QGroupBox("POS Ayarları")
        pos_grup.setStyleSheet(self.grup_stili())
        pos_layout = QFormLayout(pos_grup)
        
        self.otomatik_fiş = QCheckBox("Otomatik fiş yazdır")
        self.otomatik_fiş.setChecked(True)
        pos_layout.addRow("", self.otomatik_fiş)
        
        self.barkod_sesi = QCheckBox("Barkod okuma sesi")
        self.barkod_sesi.setChecked(True)
        pos_layout.addRow("", self.barkod_sesi)
        
        self.sepet_temizle = QCheckBox("Satış sonrası sepeti temizle")
        self.sepet_temizle.setChecked(True)
        pos_layout.addRow("", self.sepet_temizle)
        
        layout.addWidget(pos_grup)
        
        # Ödeme ayarları
        odeme_grup = QGroupBox("Ödeme Ayarları")
        odeme_grup.setStyleSheet(self.grup_stili())
        odeme_layout = QFormLayout(odeme_grup)
        
        self.nakit_odeme = QCheckBox("Nakit ödeme aktif")
        self.nakit_odeme.setChecked(True)
        odeme_layout.addRow("", self.nakit_odeme)
        
        self.kart_odeme = QCheckBox("Kart ödeme aktif")
        self.kart_odeme.setChecked(True)
        odeme_layout.addRow("", self.kart_odeme)
        
        self.veresiye_odeme = QCheckBox("Veresiye ödeme aktif")
        odeme_layout.addRow("", self.veresiye_odeme)
        
        layout.addWidget(odeme_grup)
        layout.addStretch()
        
        self.icerik_stack.addWidget(scroll)
    
    def stok_ayarlar_sayfasi_olustur(self):
        """Stok ayarlar sayfası"""
        sayfa = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(sayfa)
        
        layout = QVBoxLayout(sayfa)
        
        # Stok kontrol ayarları
        stok_grup = QGroupBox("Stok Kontrol")
        stok_grup.setStyleSheet(self.grup_stili())
        stok_layout = QFormLayout(stok_grup)
        
        self.negatif_stok = QCheckBox("Negatif stok satışına izin ver")
        stok_layout.addRow("", self.negatif_stok)
        
        self.kritik_stok_uyari = QCheckBox("Kritik stok uyarısı")
        self.kritik_stok_uyari.setChecked(True)
        stok_layout.addRow("", self.kritik_stok_uyari)
        
        self.kritik_stok_seviye = QSpinBox()
        self.kritik_stok_seviye.setRange(0, 1000)
        self.kritik_stok_seviye.setValue(10)
        stok_layout.addRow("Kritik Stok Seviyesi:", self.kritik_stok_seviye)
        
        layout.addWidget(stok_grup)
        
        # Otomatik işlemler
        otomasyon_grup = QGroupBox("Otomatik İşlemler")
        otomasyon_grup.setStyleSheet(self.grup_stili())
        otomasyon_layout = QFormLayout(otomasyon_grup)
        
        self.otomatik_barkod = QCheckBox("Otomatik barkod oluştur")
        self.otomatik_barkod.setChecked(True)
        otomasyon_layout.addRow("", self.otomatik_barkod)
        
        self.stok_senkron = QCheckBox("Otomatik stok senkronizasyonu")
        otomasyon_layout.addRow("", self.stok_senkron)
        
        layout.addWidget(otomasyon_grup)
        layout.addStretch()
        
        self.icerik_stack.addWidget(scroll)
    
    def eticaret_ayarlar_sayfasi_olustur(self):
        """E-ticaret ayarlar sayfası"""
        sayfa = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(sayfa)
        
        layout = QVBoxLayout(sayfa)
        
        # Genel e-ticaret ayarları
        eticaret_grup = QGroupBox("E-ticaret Ayarları")
        eticaret_grup.setStyleSheet(self.grup_stili())
        eticaret_layout = QFormLayout(eticaret_grup)
        
        self.otomatik_siparis_cek = QCheckBox("Otomatik sipariş çekme")
        eticaret_layout.addRow("", self.otomatik_siparis_cek)
        
        self.siparis_cekme_araligi = QSpinBox()
        self.siparis_cekme_araligi.setRange(5, 1440)
        self.siparis_cekme_araligi.setValue(30)
        self.siparis_cekme_araligi.setSuffix(" dakika")
        eticaret_layout.addRow("Sipariş Çekme Aralığı:", self.siparis_cekme_araligi)
        
        self.stok_senkron_eticaret = QCheckBox("Otomatik stok senkronizasyonu")
        eticaret_layout.addRow("", self.stok_senkron_eticaret)
        
        layout.addWidget(eticaret_grup)
        layout.addStretch()
        
        self.icerik_stack.addWidget(scroll)
    
    def ebelge_ayarlar_sayfasi_olustur(self):
        """E-belge ayarlar sayfası"""
        sayfa = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(sayfa)
        
        layout = QVBoxLayout(sayfa)
        
        # E-belge ayarları
        ebelge_grup = QGroupBox("E-belge Ayarları")
        ebelge_grup.setStyleSheet(self.grup_stili())
        ebelge_layout = QFormLayout(ebelge_grup)
        
        self.otomatik_gonderim = QCheckBox("Otomatik e-belge gönderimi")
        ebelge_layout.addRow("", self.otomatik_gonderim)
        
        self.gonderim_araligi = QSpinBox()
        self.gonderim_araligi.setRange(1, 60)
        self.gonderim_araligi.setValue(5)
        self.gonderim_araligi.setSuffix(" dakika")
        ebelge_layout.addRow("Gönderim Aralığı:", self.gonderim_araligi)
        
        self.hata_tekrar_deneme = QSpinBox()
        self.hata_tekrar_deneme.setRange(1, 10)
        self.hata_tekrar_deneme.setValue(3)
        ebelge_layout.addRow("Hata Tekrar Deneme:", self.hata_tekrar_deneme)
        
        layout.addWidget(ebelge_grup)
        layout.addStretch()
        
        self.icerik_stack.addWidget(scroll)
    
    def kargo_ayarlar_sayfasi_olustur(self):
        """Kargo ayarlar sayfası"""
        sayfa = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(sayfa)
        
        layout = QVBoxLayout(sayfa)
        
        # Kargo ayarları
        kargo_grup = QGroupBox("Kargo Ayarları")
        kargo_grup.setStyleSheet(self.grup_stili())
        kargo_layout = QFormLayout(kargo_grup)
        
        self.varsayilan_tasiyici = QComboBox()
        self.varsayilan_tasiyici.addItems(["Yurtiçi Kargo", "MNG Kargo", "Aras Kargo"])
        kargo_layout.addRow("Varsayılan Taşıyıcı:", self.varsayilan_tasiyici)
        
        self.otomatik_etiket = QCheckBox("Otomatik etiket oluştur")
        kargo_layout.addRow("", self.otomatik_etiket)
        
        self.durum_sorgula_araligi = QSpinBox()
        self.durum_sorgula_araligi.setRange(30, 1440)
        self.durum_sorgula_araligi.setValue(120)
        self.durum_sorgula_araligi.setSuffix(" dakika")
        kargo_layout.addRow("Durum Sorgulama Aralığı:", self.durum_sorgula_araligi)
        
        layout.addWidget(kargo_grup)
        layout.addStretch()
        
        self.icerik_stack.addWidget(scroll)
    
    def kullanici_ayarlar_sayfasi_olustur(self):
        """Kullanıcı ayarlar sayfası"""
        sayfa = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(sayfa)
        
        layout = QVBoxLayout(sayfa)
        
        # Kullanıcı güvenlik ayarları
        guvenlik_grup = QGroupBox("Güvenlik Ayarları")
        guvenlik_grup.setStyleSheet(self.grup_stili())
        guvenlik_layout = QFormLayout(guvenlik_grup)
        
        self.sifre_uzunlugu = QSpinBox()
        self.sifre_uzunlugu.setRange(4, 20)
        self.sifre_uzunlugu.setValue(8)
        guvenlik_layout.addRow("Min. Şifre Uzunluğu:", self.sifre_uzunlugu)
        
        self.oturum_suresi = QSpinBox()
        self.oturum_suresi.setRange(30, 1440)
        self.oturum_suresi.setValue(480)
        self.oturum_suresi.setSuffix(" dakika")
        guvenlik_layout.addRow("Oturum Süresi:", self.oturum_suresi)
        
        self.otomatik_kilit = QCheckBox("Otomatik ekran kilidi")
        guvenlik_layout.addRow("", self.otomatik_kilit)
        
        layout.addWidget(guvenlik_grup)
        layout.addStretch()
        
        self.icerik_stack.addWidget(scroll)
    
    def yetki_ayarlar_sayfasi_olustur(self):
        """Yetki ayarlar sayfası"""
        sayfa = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(sayfa)
        
        layout = QVBoxLayout(sayfa)
        
        # Yetki ayarları
        yetki_grup = QGroupBox("Yetki Ayarları")
        yetki_grup.setStyleSheet(self.grup_stili())
        yetki_layout = QFormLayout(yetki_grup)
        
        self.admin_onay = QCheckBox("Kritik işlemler için admin onayı")
        self.admin_onay.setChecked(True)
        yetki_layout.addRow("", self.admin_onay)
        
        self.log_tutma = QCheckBox("Kullanıcı işlem logları")
        self.log_tutma.setChecked(True)
        yetki_layout.addRow("", self.log_tutma)
        
        layout.addWidget(yetki_grup)
        layout.addStretch()
        
        self.icerik_stack.addWidget(scroll)
    
    def rapor_ayarlar_sayfasi_olustur(self):
        """Rapor ayarlar sayfası"""
        sayfa = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(sayfa)
        
        layout = QVBoxLayout(sayfa)
        
        # Rapor ayarları
        rapor_grup = QGroupBox("Rapor Ayarları")
        rapor_grup.setStyleSheet(self.grup_stili())
        rapor_layout = QFormLayout(rapor_grup)
        
        self.otomatik_rapor = QCheckBox("Otomatik günlük raporlar")
        rapor_layout.addRow("", self.otomatik_rapor)
        
        self.rapor_saati = QComboBox()
        self.rapor_saati.addItems([f"{i:02d}:00" for i in range(24)])
        self.rapor_saati.setCurrentText("18:00")
        rapor_layout.addRow("Rapor Saati:", self.rapor_saati)
        
        layout.addWidget(rapor_grup)
        layout.addStretch()
        
        self.icerik_stack.addWidget(scroll)
    
    def sistem_ayarlar_sayfasi_olustur(self):
        """Sistem ayarlar sayfası"""
        sayfa = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(sayfa)
        
        layout = QVBoxLayout(sayfa)
        
        # Sistem ayarları
        sistem_grup = QGroupBox("Sistem Ayarları")
        sistem_grup.setStyleSheet(self.grup_stili())
        sistem_layout = QFormLayout(sistem_grup)
        
        self.log_seviye = QComboBox()
        self.log_seviye.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_seviye.setCurrentText("INFO")
        sistem_layout.addRow("Log Seviyesi:", self.log_seviye)
        
        self.log_dosya_boyutu = QSpinBox()
        self.log_dosya_boyutu.setRange(1, 100)
        self.log_dosya_boyutu.setValue(10)
        self.log_dosya_boyutu.setSuffix(" MB")
        sistem_layout.addRow("Max Log Dosya Boyutu:", self.log_dosya_boyutu)
        
        layout.addWidget(sistem_grup)
        layout.addStretch()
        
        self.icerik_stack.addWidget(scroll)
    
    def yedekleme_ayarlar_sayfasi_olustur(self):
        """Yedekleme ayarlar sayfası"""
        sayfa = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(sayfa)
        
        layout = QVBoxLayout(sayfa)
        
        # Yedekleme ayarları
        yedekleme_grup = QGroupBox("Yedekleme Ayarları")
        yedekleme_grup.setStyleSheet(self.grup_stili())
        yedekleme_layout = QFormLayout(yedekleme_grup)
        
        self.otomatik_yedekleme_aktif = QCheckBox("Otomatik yedekleme aktif")
        self.otomatik_yedekleme_aktif.setChecked(True)
        yedekleme_layout.addRow("", self.otomatik_yedekleme_aktif)
        
        self.yedekleme_araligi = QComboBox()
        self.yedekleme_araligi.addItems(["Günlük", "Haftalık", "Aylık"])
        self.yedekleme_araligi.setCurrentText("Günlük")
        yedekleme_layout.addRow("Yedekleme Aralığı:", self.yedekleme_araligi)
        
        self.yedek_sayisi = QSpinBox()
        self.yedek_sayisi.setRange(1, 30)
        self.yedek_sayisi.setValue(7)
        yedekleme_layout.addRow("Saklanacak Yedek Sayısı:", self.yedek_sayisi)
        
        layout.addWidget(yedekleme_grup)
        layout.addStretch()
        
        self.icerik_stack.addWidget(scroll)
    
    def grup_stili(self):
        """Grup kutusu stili"""
        return """
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
        """
    
    def kategori_degisti(self, index):
        """Kategori seçimi değiştiğinde"""
        try:
            if index >= 0:
                kategori_adi = self.kategori_listesi.item(index).text()
                self.icerik_baslik.setText(kategori_adi)
                self.icerik_stack.setCurrentIndex(index)
            
        except Exception as e:
            self.hata_goster("Kategori Seçim Hatası", str(e))
    
    def baglanti_test(self):
        """Veritabanı bağlantı testi"""
        try:
            # Bağlantı test işlemi (stub)
            self.islem_baslat("Bağlantı test ediliyor...")
            
            # Simüle edilmiş test
            QTimer.singleShot(2000, lambda: (
                self.islem_bitir(),
                self.bilgi_goster_mesaj("Başarılı", "Veritabanı bağlantısı başarılı")
            ))
            
        except Exception as e:
            self.islem_bitir()
            self.hata_goster("Bağlantı Test Hatası", str(e))
    
    def varsayilana_don(self):
        """Varsayılan ayarlara dön"""
        try:
            if not self.onay_iste("Onay", "Tüm ayarlar varsayılan değerlere döndürülecek. Emin misiniz?"):
                return
            
            # Varsayılan değerleri yükle (stub)
            self.bilgi_goster_mesaj("Başarılı", "Ayarlar varsayılan değerlere döndürüldü")
            self.degisiklikler.clear()
            self.degisiklik_sayisini_guncelle()
            
        except Exception as e:
            self.hata_goster("Varsayılan Ayarlar Hatası", str(e))
    
    def ice_aktar(self):
        """Ayarları içe aktar"""
        try:
            # İçe aktarma dialog'u (stub)
            self.bilgi_goster_mesaj("Bilgi", "Ayar dosyası seçme dialog'u açılacak")
            
        except Exception as e:
            self.hata_goster("İçe Aktarma Hatası", str(e))
    
    def disa_aktar(self):
        """Ayarları dışa aktar"""
        try:
            # Dışa aktarma dialog'u (stub)
            self.bilgi_goster_mesaj("Bilgi", "Ayar dosyası kaydetme dialog'u açılacak")
            
        except Exception as e:
            self.hata_goster("Dışa Aktarma Hatası", str(e))
    
    def degisiklikleri_iptal(self):
        """Değişiklikleri iptal et"""
        try:
            if self.degisiklikler:
                if not self.onay_iste("Onay", "Yapılan değişiklikler iptal edilecek. Emin misiniz?"):
                    return
                
                self.degisiklikler.clear()
                self.degisiklik_sayisini_guncelle()
                self.bilgi_goster_mesaj("Bilgi", "Değişiklikler iptal edildi")
            
        except Exception as e:
            self.hata_goster("İptal Hatası", str(e))
    
    def ayarlari_kaydet(self):
        """Ayarları kaydet"""
        try:
            if not self.degisiklikler:
                self.bilgi_goster_mesaj("Bilgi", "Kaydedilecek değişiklik bulunmuyor")
                return
            
            # Ayar servisini çağır
            ayar_servisi = self.servis_fabrikasi.ayar_servisi()
            
            # İşlem başlat
            self.islem_baslat("Ayarlar kaydediliyor...")
            
            sonuc = self.servis_cagir_guvenli(ayar_servisi.kaydet, self.degisiklikler)
            
            if sonuc:
                self.degisiklikler.clear()
                self.degisiklik_sayisini_guncelle()
                self.bilgi_goster_mesaj("Başarılı", "Ayarlar başarıyla kaydedildi")
            
            self.islem_bitir()
            
        except Exception as e:
            self.islem_bitir()
            self.hata_goster("Kaydetme Hatası", str(e))
    
    def degisiklik_sayisini_guncelle(self):
        """Değişiklik sayısını güncelle"""
        self.degisiklik_label.setText(f"Değişiklik: {len(self.degisiklikler)}")
    
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
        # İlk kategoriyi seç
        if self.kategori_listesi.count() > 0:
            self.kategori_listesi.setCurrentRow(0)
    
    def verileri_temizle(self):
        """Ekran kapandığında"""
        pass