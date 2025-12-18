# Version: 0.1.0
# Last Update: 2024-12-18
# Module: uygulama.arayuz.ekranlar.raporlar.rapor_filtreleri
# Description: Rapor filtreleri ve tarih aralığı UI bileşenleri
# Changelog:
# - İlk sürüm oluşturuldu

from PyQt6.QtWidgets import (QGroupBox, QVBoxLayout, QLabel, QComboBox, 
                             QDateEdit, QGridLayout, QPushButton, QFrame)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont


class RaporFiltreleriUI:
    """Rapor filtreleri UI bileşenleri"""
    
    def __init__(self, parent):
        self.parent = parent
    
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
        
        self.parent.rapor_turu_combo = QComboBox()
        self.parent.rapor_turu_combo.addItems([
            "Satış Raporu",
            "Stok Raporu", 
            "Müşteri Raporu",
            "Finansal Raporu",
            "E-ticaret Raporu",
            "Kargo Raporu",
            "E-belge Raporu",
            "Performans Raporu"
        ])
        self.parent.rapor_turu_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 12px;
            }
        """)
        self.parent.rapor_turu_combo.currentTextChanged.connect(self.parent.rapor_turu_degisti)
        layout.addWidget(self.parent.rapor_turu_combo)
        
        # Alt rapor türü
        self.parent.alt_rapor_label = QLabel("Alt Kategori:")
        layout.addWidget(self.parent.alt_rapor_label)
        
        self.parent.alt_rapor_combo = QComboBox()
        self.parent.alt_rapor_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.parent.alt_rapor_combo)
        
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
        bugun_buton.setStyleSheet(self._kucuk_buton_stili())
        bugun_buton.clicked.connect(lambda: self.parent.hizli_tarih_sec("bugun"))
        hizli_layout.addWidget(bugun_buton, 0, 0)
        
        dun_buton = QPushButton("Dün")
        dun_buton.setStyleSheet(self._kucuk_buton_stili())
        dun_buton.clicked.connect(lambda: self.parent.hizli_tarih_sec("dun"))
        hizli_layout.addWidget(dun_buton, 0, 1)
        
        bu_hafta_buton = QPushButton("Bu Hafta")
        bu_hafta_buton.setStyleSheet(self._kucuk_buton_stili())
        bu_hafta_buton.clicked.connect(lambda: self.parent.hizli_tarih_sec("bu_hafta"))
        hizli_layout.addWidget(bu_hafta_buton, 1, 0)
        
        bu_ay_buton = QPushButton("Bu Ay")
        bu_ay_buton.setStyleSheet(self._kucuk_buton_stili())
        bu_ay_buton.clicked.connect(lambda: self.parent.hizli_tarih_sec("bu_ay"))
        hizli_layout.addWidget(bu_ay_buton, 1, 1)
        
        layout.addWidget(hizli_secim_frame)
        
        # Manuel tarih seçimi
        tarih_frame = QFrame()
        tarih_layout = QVBoxLayout(tarih_frame)
        
        self.parent.baslangic_tarih = QDateEdit()
        self.parent.baslangic_tarih.setDate(QDate.currentDate().addDays(-30))
        self.parent.baslangic_tarih.setCalendarPopup(True)
        self.parent.baslangic_tarih.setStyleSheet("""
            QDateEdit {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        tarih_layout.addWidget(QLabel("Başlangıç:"))
        tarih_layout.addWidget(self.parent.baslangic_tarih)
        
        self.parent.bitis_tarih = QDateEdit()
        self.parent.bitis_tarih.setDate(QDate.currentDate())
        self.parent.bitis_tarih.setCalendarPopup(True)
        self.parent.bitis_tarih.setStyleSheet("""
            QDateEdit {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        tarih_layout.addWidget(QLabel("Bitiş:"))
        tarih_layout.addWidget(self.parent.bitis_tarih)
        
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
        
        self.parent.magaza_combo = QComboBox()
        self.parent.magaza_combo.addItems([
            "Tüm Mağazalar", "Ana Mağaza", "Şube 1", "Şube 2", "Online Mağaza"
        ])
        self.parent.magaza_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.parent.magaza_combo)
        
        # Kullanıcı filtresi
        kullanici_label = QLabel("Kullanıcı:")
        layout.addWidget(kullanici_label)
        
        self.parent.kullanici_combo = QComboBox()
        self.parent.kullanici_combo.addItems([
            "Tüm Kullanıcılar", "Admin", "Kasiyer 1", "Kasiyer 2", "Müdür"
        ])
        self.parent.kullanici_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.parent.kullanici_combo)
        
        # Kategori filtresi
        kategori_label = QLabel("Kategori:")
        layout.addWidget(kategori_label)
        
        self.parent.kategori_combo = QComboBox()
        self.parent.kategori_combo.addItems([
            "Tüm Kategoriler", "Elektronik", "Giyim", "Ev & Yaşam", "Spor"
        ])
        self.parent.kategori_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.parent.kategori_combo)
        
        # Detay seviyesi
        detay_label = QLabel("Detay Seviyesi:")
        layout.addWidget(detay_label)
        
        self.parent.detay_combo = QComboBox()
        self.parent.detay_combo.addItems([
            "Özet", "Detaylı", "Çok Detaylı"
        ])
        self.parent.detay_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.parent.detay_combo)
        
        return grup
    
    def _kucuk_buton_stili(self):
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


class RaporFiltreleriIslemleri:
    """Rapor filtreleri iş mantığı"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def rapor_turu_degisti(self):
        """Rapor türü değiştiğinde"""
        try:
            secili_rapor = self.parent.rapor_turu_combo.currentText()
            self.parent.aktif_rapor_tipi = secili_rapor
            
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
            
            self.parent.alt_rapor_combo.clear()
            if secili_rapor in alt_turler:
                self.parent.alt_rapor_combo.addItems(alt_turler[secili_rapor])
            
        except Exception as e:
            self.parent.hata_goster("Rapor Türü Seçim Hatası", str(e))
    
    def hizli_tarih_sec(self, tur: str):
        """Hızlı tarih seçimi"""
        try:
            bugun = QDate.currentDate()
            
            if tur == "bugun":
                self.parent.baslangic_tarih.setDate(bugun)
                self.parent.bitis_tarih.setDate(bugun)
            elif tur == "dun":
                dun = bugun.addDays(-1)
                self.parent.baslangic_tarih.setDate(dun)
                self.parent.bitis_tarih.setDate(dun)
            elif tur == "bu_hafta":
                hafta_basi = bugun.addDays(-bugun.dayOfWeek() + 1)
                self.parent.baslangic_tarih.setDate(hafta_basi)
                self.parent.bitis_tarih.setDate(bugun)
            elif tur == "bu_ay":
                ay_basi = QDate(bugun.year(), bugun.month(), 1)
                self.parent.baslangic_tarih.setDate(ay_basi)
                self.parent.bitis_tarih.setDate(bugun)
            
        except Exception as e:
            self.parent.hata_goster("Tarih Seçim Hatası", str(e))