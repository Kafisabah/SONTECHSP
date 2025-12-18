# Version: 0.1.0
# Last Update: 2024-12-18
# Module: uygulama.arayuz.ekranlar.ayarlar.ayar_formlari
# Description: Ayarlar ekranı form sayfaları
# Changelog:
# - İlk sürüm oluşturuldu

from PyQt6.QtWidgets import (QVBoxLayout, QGroupBox, QFormLayout, QLineEdit, 
                             QTextEdit, QComboBox, QCheckBox, QSpinBox, 
                             QPushButton, QScrollArea, QWidget, QDoubleSpinBox)
from PyQt6.QtCore import Qt


class AyarFormlari:
    """Ayarlar ekranı form sayfaları"""
    
    def __init__(self, parent_ekran):
        self.parent = parent_ekran
    
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
        
        self.parent.sirket_adi = QLineEdit("SONTECH SP")
        sirket_layout.addRow("Şirket Adı:", self.parent.sirket_adi)
        
        self.parent.vergi_no = QLineEdit("1234567890")
        sirket_layout.addRow("Vergi No:", self.parent.vergi_no)
        
        self.parent.adres = QTextEdit("İstanbul, Türkiye")
        self.parent.adres.setMaximumHeight(80)
        sirket_layout.addRow("Adres:", self.parent.adres)
        
        layout.addWidget(sirket_grup)
        
        # Uygulama ayarları grubu
        uygulama_grup = QGroupBox("Uygulama Ayarları")
        uygulama_grup.setStyleSheet(self.grup_stili())
        uygulama_layout = QFormLayout(uygulama_grup)
        
        self.parent.dil_combo = QComboBox()
        self.parent.dil_combo.addItems(["Türkçe", "English"])
        uygulama_layout.addRow("Dil:", self.parent.dil_combo)
        
        self.parent.tema_combo = QComboBox()
        self.parent.tema_combo.addItems(["Açık Tema", "Koyu Tema", "Otomatik"])
        uygulama_layout.addRow("Tema:", self.parent.tema_combo)
        
        self.parent.otomatik_yedekleme = QCheckBox("Otomatik yedekleme aktif")
        self.parent.otomatik_yedekleme.setChecked(True)
        uygulama_layout.addRow("", self.parent.otomatik_yedekleme)
        
        layout.addWidget(uygulama_grup)
        layout.addStretch()
        
        return scroll
    
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
        
        self.parent.db_host = QLineEdit("localhost")
        postgres_layout.addRow("Host:", self.parent.db_host)
        
        self.parent.db_port = QSpinBox()
        self.parent.db_port.setRange(1, 65535)
        self.parent.db_port.setValue(5432)
        postgres_layout.addRow("Port:", self.parent.db_port)
        
        self.parent.db_name = QLineEdit("sontechsp")
        postgres_layout.addRow("Veritabanı Adı:", self.parent.db_name)
        
        self.parent.db_user = QLineEdit("postgres")
        postgres_layout.addRow("Kullanıcı:", self.parent.db_user)
        
        self.parent.db_password = QLineEdit()
        self.parent.db_password.setEchoMode(QLineEdit.EchoMode.Password)
        postgres_layout.addRow("Şifre:", self.parent.db_password)
        
        baglanti_test_buton = QPushButton("Bağlantıyı Test Et")
        baglanti_test_buton.clicked.connect(self.parent.baglanti_test)
        postgres_layout.addRow("", baglanti_test_buton)
        
        layout.addWidget(postgres_grup)
        
        # Performans ayarları
        performans_grup = QGroupBox("Performans Ayarları")
        performans_grup.setStyleSheet(self.grup_stili())
        performans_layout = QFormLayout(performans_grup)
        
        self.parent.baglanti_havuzu = QSpinBox()
        self.parent.baglanti_havuzu.setRange(5, 100)
        self.parent.baglanti_havuzu.setValue(20)
        performans_layout.addRow("Bağlantı Havuzu:", self.parent.baglanti_havuzu)
        
        self.parent.sorgu_timeout = QSpinBox()
        self.parent.sorgu_timeout.setRange(5, 300)
        self.parent.sorgu_timeout.setValue(30)
        self.parent.sorgu_timeout.setSuffix(" saniye")
        performans_layout.addRow("Sorgu Timeout:", self.parent.sorgu_timeout)
        
        layout.addWidget(performans_grup)
        layout.addStretch()
        
        return scroll
    
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
        
        self.parent.otomatik_fiş = QCheckBox("Otomatik fiş yazdır")
        self.parent.otomatik_fiş.setChecked(True)
        pos_layout.addRow("", self.parent.otomatik_fiş)
        
        self.parent.barkod_sesi = QCheckBox("Barkod okuma sesi")
        self.parent.barkod_sesi.setChecked(True)
        pos_layout.addRow("", self.parent.barkod_sesi)
        
        self.parent.sepet_temizle = QCheckBox("Satış sonrası sepeti temizle")
        self.parent.sepet_temizle.setChecked(True)
        pos_layout.addRow("", self.parent.sepet_temizle)
        
        layout.addWidget(pos_grup)
        
        # Ödeme ayarları
        odeme_grup = QGroupBox("Ödeme Ayarları")
        odeme_grup.setStyleSheet(self.grup_stili())
        odeme_layout = QFormLayout(odeme_grup)
        
        self.parent.nakit_odeme = QCheckBox("Nakit ödeme aktif")
        self.parent.nakit_odeme.setChecked(True)
        odeme_layout.addRow("", self.parent.nakit_odeme)
        
        self.parent.kart_odeme = QCheckBox("Kart ödeme aktif")
        self.parent.kart_odeme.setChecked(True)
        odeme_layout.addRow("", self.parent.kart_odeme)
        
        self.parent.veresiye_odeme = QCheckBox("Veresiye ödeme aktif")
        odeme_layout.addRow("", self.parent.veresiye_odeme)
        
        layout.addWidget(odeme_grup)
        layout.addStretch()
        
        return scroll
    
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
        
        self.parent.negatif_stok = QCheckBox("Negatif stok satışına izin ver")
        stok_layout.addRow("", self.parent.negatif_stok)
        
        self.parent.kritik_stok_uyari = QCheckBox("Kritik stok uyarısı")
        self.parent.kritik_stok_uyari.setChecked(True)
        stok_layout.addRow("", self.parent.kritik_stok_uyari)
        
        self.parent.kritik_stok_seviye = QSpinBox()
        self.parent.kritik_stok_seviye.setRange(0, 1000)
        self.parent.kritik_stok_seviye.setValue(10)
        stok_layout.addRow("Kritik Stok Seviyesi:", self.parent.kritik_stok_seviye)
        
        layout.addWidget(stok_grup)
        
        # Otomatik işlemler
        otomasyon_grup = QGroupBox("Otomatik İşlemler")
        otomasyon_grup.setStyleSheet(self.grup_stili())
        otomasyon_layout = QFormLayout(otomasyon_grup)
        
        self.parent.otomatik_barkod = QCheckBox("Otomatik barkod oluştur")
        self.parent.otomatik_barkod.setChecked(True)
        otomasyon_layout.addRow("", self.parent.otomatik_barkod)
        
        self.parent.stok_senkron = QCheckBox("Otomatik stok senkronizasyonu")
        otomasyon_layout.addRow("", self.parent.stok_senkron)
        
        layout.addWidget(otomasyon_grup)
        layout.addStretch()
        
        return scroll
    
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
        
        self.parent.otomatik_siparis_cek = QCheckBox("Otomatik sipariş çekme")
        eticaret_layout.addRow("", self.parent.otomatik_siparis_cek)
        
        self.parent.siparis_cekme_araligi = QSpinBox()
        self.parent.siparis_cekme_araligi.setRange(5, 1440)
        self.parent.siparis_cekme_araligi.setValue(30)
        self.parent.siparis_cekme_araligi.setSuffix(" dakika")
        eticaret_layout.addRow("Sipariş Çekme Aralığı:", self.parent.siparis_cekme_araligi)
        
        self.parent.stok_senkron_eticaret = QCheckBox("Otomatik stok senkronizasyonu")
        eticaret_layout.addRow("", self.parent.stok_senkron_eticaret)
        
        layout.addWidget(eticaret_grup)
        layout.addStretch()
        
        return scroll
    
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
        
        self.parent.otomatik_gonderim = QCheckBox("Otomatik e-belge gönderimi")
        ebelge_layout.addRow("", self.parent.otomatik_gonderim)
        
        self.parent.gonderim_araligi = QSpinBox()
        self.parent.gonderim_araligi.setRange(1, 60)
        self.parent.gonderim_araligi.setValue(5)
        self.parent.gonderim_araligi.setSuffix(" dakika")
        ebelge_layout.addRow("Gönderim Aralığı:", self.parent.gonderim_araligi)
        
        self.parent.hata_tekrar_deneme = QSpinBox()
        self.parent.hata_tekrar_deneme.setRange(1, 10)
        self.parent.hata_tekrar_deneme.setValue(3)
        ebelge_layout.addRow("Hata Tekrar Deneme:", self.parent.hata_tekrar_deneme)
        
        layout.addWidget(ebelge_grup)
        layout.addStretch()
        
        return scroll
    
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
        
        self.parent.varsayilan_tasiyici = QComboBox()
        self.parent.varsayilan_tasiyici.addItems(["Yurtiçi Kargo", "MNG Kargo", "Aras Kargo"])
        kargo_layout.addRow("Varsayılan Taşıyıcı:", self.parent.varsayilan_tasiyici)
        
        self.parent.otomatik_etiket = QCheckBox("Otomatik etiket oluştur")
        kargo_layout.addRow("", self.parent.otomatik_etiket)
        
        self.parent.durum_sorgula_araligi = QSpinBox()
        self.parent.durum_sorgula_araligi.setRange(30, 1440)
        self.parent.durum_sorgula_araligi.setValue(120)
        self.parent.durum_sorgula_araligi.setSuffix(" dakika")
        kargo_layout.addRow("Durum Sorgulama Aralığı:", self.parent.durum_sorgula_araligi)
        
        layout.addWidget(kargo_grup)
        layout.addStretch()
        
        return scroll
    
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
        
        self.parent.sifre_uzunlugu = QSpinBox()
        self.parent.sifre_uzunlugu.setRange(4, 20)
        self.parent.sifre_uzunlugu.setValue(8)
        guvenlik_layout.addRow("Min. Şifre Uzunluğu:", self.parent.sifre_uzunlugu)
        
        self.parent.oturum_suresi = QSpinBox()
        self.parent.oturum_suresi.setRange(30, 1440)
        self.parent.oturum_suresi.setValue(480)
        self.parent.oturum_suresi.setSuffix(" dakika")
        guvenlik_layout.addRow("Oturum Süresi:", self.parent.oturum_suresi)
        
        self.parent.otomatik_kilit = QCheckBox("Otomatik ekran kilidi")
        guvenlik_layout.addRow("", self.parent.otomatik_kilit)
        
        layout.addWidget(guvenlik_grup)
        layout.addStretch()
        
        return scroll
    
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
        
        self.parent.admin_onay = QCheckBox("Kritik işlemler için admin onayı")
        self.parent.admin_onay.setChecked(True)
        yetki_layout.addRow("", self.parent.admin_onay)
        
        self.parent.log_tutma = QCheckBox("Kullanıcı işlem logları")
        self.parent.log_tutma.setChecked(True)
        yetki_layout.addRow("", self.parent.log_tutma)
        
        layout.addWidget(yetki_grup)
        layout.addStretch()
        
        return scroll
    
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
        
        self.parent.otomatik_rapor = QCheckBox("Otomatik günlük raporlar")
        rapor_layout.addRow("", self.parent.otomatik_rapor)
        
        self.parent.rapor_saati = QComboBox()
        self.parent.rapor_saati.addItems([f"{i:02d}:00" for i in range(24)])
        self.parent.rapor_saati.setCurrentText("18:00")
        rapor_layout.addRow("Rapor Saati:", self.parent.rapor_saati)
        
        layout.addWidget(rapor_grup)
        layout.addStretch()
        
        return scroll
    
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
        
        self.parent.log_seviye = QComboBox()
        self.parent.log_seviye.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.parent.log_seviye.setCurrentText("INFO")
        sistem_layout.addRow("Log Seviyesi:", self.parent.log_seviye)
        
        self.parent.log_dosya_boyutu = QSpinBox()
        self.parent.log_dosya_boyutu.setRange(1, 100)
        self.parent.log_dosya_boyutu.setValue(10)
        self.parent.log_dosya_boyutu.setSuffix(" MB")
        sistem_layout.addRow("Max Log Dosya Boyutu:", self.parent.log_dosya_boyutu)
        
        layout.addWidget(sistem_grup)
        layout.addStretch()
        
        return scroll
    
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
        
        self.parent.otomatik_yedekleme_aktif = QCheckBox("Otomatik yedekleme aktif")
        self.parent.otomatik_yedekleme_aktif.setChecked(True)
        yedekleme_layout.addRow("", self.parent.otomatik_yedekleme_aktif)
        
        self.parent.yedekleme_araligi = QComboBox()
        self.parent.yedekleme_araligi.addItems(["Günlük", "Haftalık", "Aylık"])
        self.parent.yedekleme_araligi.setCurrentText("Günlük")
        yedekleme_layout.addRow("Yedekleme Aralığı:", self.parent.yedekleme_araligi)
        
        self.parent.yedek_sayisi = QSpinBox()
        self.parent.yedek_sayisi.setRange(1, 30)
        self.parent.yedek_sayisi.setValue(7)
        yedekleme_layout.addRow("Saklanacak Yedek Sayısı:", self.parent.yedek_sayisi)
        
        layout.addWidget(yedekleme_grup)
        layout.addStretch()
        
        return scroll