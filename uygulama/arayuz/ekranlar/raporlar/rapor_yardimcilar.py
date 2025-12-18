# Version: 0.1.0
# Last Update: 2024-12-18
# Module: uygulama.arayuz.ekranlar.raporlar.rapor_yardimcilar
# Description: Rapor yardımcı fonksiyonları ve UI bileşenleri
# Changelog:
# - İlk sürüm oluşturuldu

from PyQt6.QtWidgets import (QGroupBox, QVBoxLayout, QLabel, QProgressBar, 
                             QFrame, QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime
from ...yardimcilar import UIYardimcilari


class RaporYardimciUI:
    """Rapor yardımcı UI bileşenleri"""
    
    def __init__(self, parent):
        self.parent = parent
    
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
        self.parent.durum_label = QLabel("Hazır")
        self.parent.durum_label.setStyleSheet("""
            QLabel {
                padding: 5px;
                background-color: #27ae60;
                color: white;
                border-radius: 3px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.parent.durum_label)
        
        # Progress bar
        self.parent.progress_bar = QProgressBar()
        self.parent.progress_bar.setVisible(False)
        self.parent.progress_bar.setStyleSheet("""
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
        layout.addWidget(self.parent.progress_bar)
        
        # Son rapor bilgisi
        self.parent.son_rapor_label = QLabel("Son Rapor: Henüz oluşturulmadı")
        self.parent.son_rapor_label.setStyleSheet("font-size: 10px; color: #7f8c8d;")
        layout.addWidget(self.parent.son_rapor_label)
        
        return grup
    
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
        self.parent.rapor_baslik_label = QLabel("Rapor Sonuçları")
        self.parent.rapor_baslik_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50;")
        layout.addWidget(self.parent.rapor_baslik_label)
        
        layout.addStretch()
        
        # Kayıt sayısı
        self.parent.kayit_sayisi_label = QLabel("Toplam Kayıt: 0")
        self.parent.kayit_sayisi_label.setStyleSheet("font-weight: bold; color: #7f8c8d;")
        layout.addWidget(self.parent.kayit_sayisi_label)
        
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
        self.parent.toplam_tutar_label = QLabel("Toplam Tutar: ₺0,00")
        self.parent.toplam_tutar_label.setStyleSheet("""
            QLabel {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.parent.toplam_tutar_label)
        
        self.parent.ortalama_label = QLabel("Ortalama: ₺0,00")
        self.parent.ortalama_label.setStyleSheet("""
            QLabel {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.parent.ortalama_label)
        
        self.parent.en_yuksek_label = QLabel("En Yüksek: ₺0,00")
        self.parent.en_yuksek_label.setStyleSheet("""
            QLabel {
                background-color: #e67e22;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.parent.en_yuksek_label)
        
        layout.addStretch()
        
        return frame


class RaporYardimciIslemleri:
    """Rapor yardımcı işlemleri"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def rapor_tablosunu_guncelle(self):
        """Rapor tablosunu güncelle"""
        try:
            self.parent.rapor_tablo.setRowCount(len(self.parent.rapor_verileri))
            
            toplam_tutar = 0
            en_yuksek = 0
            
            for row, veri in enumerate(self.parent.rapor_verileri):
                self.parent.rapor_tablo.setItem(row, 0, QTableWidgetItem(
                    UIYardimcilari.tarih_formatla(veri["tarih"])
                ))
                self.parent.rapor_tablo.setItem(row, 1, QTableWidgetItem(veri["aciklama"]))
                self.parent.rapor_tablo.setItem(row, 2, QTableWidgetItem(str(veri["miktar"])))
                
                tutar_item = QTableWidgetItem(UIYardimcilari.para_formatla(veri["tutar"]))
                self.parent.rapor_tablo.setItem(row, 3, tutar_item)
                
                self.parent.rapor_tablo.setItem(row, 4, QTableWidgetItem(veri["kategori"]))
                
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
                self.parent.rapor_tablo.setItem(row, 5, durum_item)
                
                # Hesaplamalar
                toplam_tutar += veri["tutar"]
                if veri["tutar"] > en_yuksek:
                    en_yuksek = veri["tutar"]
            
            # Başlık ve sayaçları güncelle
            self.parent.rapor_baslik_label.setText(f"{self.parent.aktif_rapor_tipi} - {self.parent.alt_rapor_combo.currentText()}")
            self.parent.kayit_sayisi_label.setText(f"Toplam Kayıt: {len(self.parent.rapor_verileri)}")
            
            # Özet bilgileri güncelle
            self.parent.toplam_tutar_label.setText(f"Toplam Tutar: {UIYardimcilari.para_formatla(toplam_tutar)}")
            
            ortalama = toplam_tutar / len(self.parent.rapor_verileri) if self.parent.rapor_verileri else 0
            self.parent.ortalama_label.setText(f"Ortalama: {UIYardimcilari.para_formatla(ortalama)}")
            
            self.parent.en_yuksek_label.setText(f"En Yüksek: {UIYardimcilari.para_formatla(en_yuksek)}")
            
        except Exception as e:
            self.parent.hata_goster("Tablo Güncelleme Hatası", str(e))
    
    def islem_baslat(self, mesaj: str):
        """İşlem başlatma"""
        self.parent.durum_label.setText(mesaj)
        self.parent.durum_label.setStyleSheet("""
            QLabel {
                padding: 5px;
                background-color: #f39c12;
                color: white;
                border-radius: 3px;
                font-weight: bold;
            }
        """)
        self.parent.progress_bar.setVisible(True)
        self.parent.progress_bar.setRange(0, 0)  # Belirsiz progress
    
    def islem_bitir(self):
        """İşlem bitirme"""
        self.parent.durum_label.setText("Hazır")
        self.parent.durum_label.setStyleSheet("""
            QLabel {
                padding: 5px;
                background-color: #27ae60;
                color: white;
                border-radius: 3px;
                font-weight: bold;
            }
        """)
        self.parent.progress_bar.setVisible(False)
        
        # Son rapor zamanını güncelle
        simdi = datetime.now().strftime("%d.%m.%Y %H:%M")
        self.parent.son_rapor_label.setText(f"Son Rapor: {simdi}")