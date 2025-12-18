# Version: 0.1.0
# Last Update: 2024-12-18
# Module: uygulama.arayuz.ekranlar.raporlar.rapor_olusturma
# Description: Rapor oluşturma UI bileşenleri
# Changelog:
# - İlk sürüm oluşturuldu

from PyQt6.QtWidgets import (QGroupBox, QVBoxLayout, QPushButton, QGridLayout, 
                             QFrame, QProgressBar, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class RaporOlusturmaUI:
    """Rapor oluşturma UI bileşenleri"""
    
    def __init__(self, parent):
        self.parent = parent
    
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
        rapor_olustur_buton.clicked.connect(self.parent.rapor_olustur)
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
        excel_buton.clicked.connect(lambda: self.parent.disa_aktar("excel"))
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
        pdf_buton.clicked.connect(lambda: self.parent.disa_aktar("pdf"))
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
        csv_buton.clicked.connect(lambda: self.parent.disa_aktar("csv"))
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
        yazdir_buton.clicked.connect(self.parent.yazdir)
        disa_aktar_layout.addWidget(yazdir_buton, 1, 1)
        
        layout.addWidget(disa_aktar_frame)
        
        return grup


class RaporOlusturmaIslemleri:
    """Rapor oluşturma iş mantığı"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def rapor_olustur(self):
        """Rapor oluşturma işlemi"""
        try:
            if not self.parent.aktif_rapor_tipi:
                self.parent.hata_goster("Hata", "Lütfen bir rapor türü seçin")
                return
            
            # Rapor servisini çağır
            rapor_servisi = self.parent.servis_fabrikasi.rapor_servisi()
            
            # İşlem başlat
            self.parent.islem_baslat("Rapor oluşturuluyor...")
            
            # Parametreleri hazırla
            parametreler = {
                "rapor_turu": self.parent.aktif_rapor_tipi,
                "alt_tur": self.parent.alt_rapor_combo.currentText(),
                "baslangic_tarih": self.parent.baslangic_tarih.date().toString("yyyy-MM-dd"),
                "bitis_tarih": self.parent.bitis_tarih.date().toString("yyyy-MM-dd"),
                "magaza": self.parent.magaza_combo.currentText(),
                "kullanici": self.parent.kullanici_combo.currentText(),
                "kategori": self.parent.kategori_combo.currentText(),
                "detay_seviye": self.parent.detay_combo.currentText()
            }
            
            sonuc = self.parent.servis_cagir_guvenli(
                rapor_servisi.rapor_olustur, 
                parametreler
            )
            
            if sonuc:
                self.parent.rapor_verilerini_yukle()
                self.parent.bilgi_goster_mesaj("Başarılı", "Rapor başarıyla oluşturuldu")
            
            self.parent.islem_bitir()
            
        except Exception as e:
            self.parent.islem_bitir()
            self.parent.hata_goster("Rapor Oluşturma Hatası", str(e))
    
    def rapor_verilerini_yukle(self):
        """Rapor verilerini yükle"""
        try:
            # Stub rapor verileri
            self.parent.rapor_verileri = [
                {
                    "tarih": "2024-12-18",
                    "aciklama": f"İşlem {i}",
                    "miktar": i + 5,
                    "tutar": (i + 1) * 125.75,
                    "kategori": ["Elektronik", "Giyim", "Ev & Yaşam"][i % 3],
                    "durum": ["Tamamlandı", "Beklemede", "İptal"][i % 3]
                }
                for i in range(1, 21)
            ]
            
            self.parent.rapor_tablosunu_guncelle()
            
        except Exception as e:
            self.parent.hata_goster("Veri Yükleme Hatası", str(e))