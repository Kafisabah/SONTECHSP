# Version: 0.1.0
# Last Update: 2024-12-18
# Module: uygulama.arayuz.ekranlar.ebelge.ebelge_veri_yoneticisi
# Description: E-belge veri yönetimi
# Changelog:
# - İlk sürüm oluşturuldu

from PyQt6.QtWidgets import QTableWidgetItem, QPushButton
from PyQt6.QtCore import Qt
from ...yardimcilar import UIYardimcilari


class EbelgeVeriYoneticisi:
    """E-belge veri yönetimi"""
    
    def __init__(self, parent):
        self.parent = parent
    
    def bekleyen_listesi_yenile(self):
        """Bekleyen belgeler listesini yenile"""
        try:
            # Stub bekleyen belge verileri
            self.parent.bekleyen_verileri = [
                {
                    "belge_no": f"BKL{i:06d}",
                    "tur": ["e-Fatura", "e-Arşiv", "e-İrsaliye"][i % 3],
                    "musteri": f"Müşteri {i}",
                    "tutar": (i + 1) * 250.75,
                    "tarih": "2024-12-18",
                    "durum": "Bekliyor",
                    "deneme": i % 3 + 1
                }
                for i in range(1, 8)
            ]
            
            self.bekleyen_tablosunu_guncelle()
            
        except Exception as e:
            self.parent.hata_goster("Liste Yenileme Hatası", str(e))
    
    def gonderilen_listesi_yenile(self):
        """Gönderilen belgeler listesini yenile"""
        try:
            # Stub gönderilen belge verileri
            self.parent.gonderilen_verileri = [
                {
                    "belge_no": f"GND{i:06d}",
                    "tur": ["e-Fatura", "e-Arşiv", "e-İrsaliye"][i % 3],
                    "musteri": f"Müşteri {i}",
                    "tutar": (i + 1) * 180.25,
                    "gonderim_tarihi": "2024-12-18",
                    "uuid": f"uuid-{i:04d}-abcd-efgh",
                    "durum": "Kabul Edildi",
                    "yanit": "Başarılı"
                }
                for i in range(1, 15)
            ]
            
            self.gonderilen_tablosunu_guncelle()
            
        except Exception as e:
            self.parent.hata_goster("Liste Yenileme Hatası", str(e))
    
    def hatali_listesi_yenile(self):
        """Hatalı belgeler listesini yenile"""
        try:
            # Stub hatalı belge verileri
            self.parent.hatali_verileri = [
                {
                    "belge_no": f"HTL{i:06d}",
                    "tur": ["e-Fatura", "e-Arşiv"][i % 2],
                    "musteri": f"Müşteri {i}",
                    "tutar": (i + 1) * 95.50,
                    "hata_tarihi": "2024-12-18",
                    "hata_kodu": f"ERR{i:03d}",
                    "hata_aciklamasi": f"Hata açıklaması {i}"
                }
                for i in range(1, 4)
            ]
            
            self.hatali_tablosunu_guncelle()
            
        except Exception as e:
            self.parent.hata_goster("Liste Yenileme Hatası", str(e))
    
    def bekleyen_tablosunu_guncelle(self):
        """Bekleyen belgeler tablosunu güncelle"""
        try:
            self.parent.bekleyen_tablo.setRowCount(len(self.parent.bekleyen_verileri))
            
            for row, belge in enumerate(self.parent.bekleyen_verileri):
                self.parent.bekleyen_tablo.setItem(row, 0, QTableWidgetItem(belge["belge_no"]))
                self.parent.bekleyen_tablo.setItem(row, 1, QTableWidgetItem(belge["tur"]))
                self.parent.bekleyen_tablo.setItem(row, 2, QTableWidgetItem(belge["musteri"]))
                self.parent.bekleyen_tablo.setItem(row, 3, QTableWidgetItem(
                    UIYardimcilari.para_formatla(belge["tutar"])
                ))
                self.parent.bekleyen_tablo.setItem(row, 4, QTableWidgetItem(
                    UIYardimcilari.tarih_formatla(belge["tarih"])
                ))
                self.parent.bekleyen_tablo.setItem(row, 5, QTableWidgetItem(belge["durum"]))
                self.parent.bekleyen_tablo.setItem(row, 6, QTableWidgetItem(str(belge["deneme"])))
                
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
                self.parent.bekleyen_tablo.setCellWidget(row, 7, islem_buton)
            
            # Durum çubuğunu güncelle
            self.parent.bekleyen_durum_label.setText(f"Toplam Bekleyen: {len(self.parent.bekleyen_verileri)}")
            self.parent.durum.bekleyen_sayisi_label.setText(f"Bekleyen: {len(self.parent.bekleyen_verileri)}")
            
        except Exception as e:
            self.parent.hata_goster("Tablo Güncelleme Hatası", str(e))
    
    def gonderilen_tablosunu_guncelle(self):
        """Gönderilen belgeler tablosunu güncelle"""
        try:
            self.parent.gonderilen_tablo.setRowCount(len(self.parent.gonderilen_verileri))
            
            for row, belge in enumerate(self.parent.gonderilen_verileri):
                self.parent.gonderilen_tablo.setItem(row, 0, QTableWidgetItem(belge["belge_no"]))
                self.parent.gonderilen_tablo.setItem(row, 1, QTableWidgetItem(belge["tur"]))
                self.parent.gonderilen_tablo.setItem(row, 2, QTableWidgetItem(belge["musteri"]))
                self.parent.gonderilen_tablo.setItem(row, 3, QTableWidgetItem(
                    UIYardimcilari.para_formatla(belge["tutar"])
                ))
                self.parent.gonderilen_tablo.setItem(row, 4, QTableWidgetItem(
                    UIYardimcilari.tarih_formatla(belge["gonderim_tarihi"])
                ))
                self.parent.gonderilen_tablo.setItem(row, 5, QTableWidgetItem(belge["uuid"]))
                
                # Durum - renk kodlaması
                durum_item = QTableWidgetItem(belge["durum"])
                durum_item.setBackground(Qt.GlobalColor.green)
                durum_item.setForeground(Qt.GlobalColor.white)
                self.parent.gonderilen_tablo.setItem(row, 6, durum_item)
                
                self.parent.gonderilen_tablo.setItem(row, 7, QTableWidgetItem(belge["yanit"]))
                
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
                self.parent.gonderilen_tablo.setCellWidget(row, 8, islem_buton)
            
            # Durum çubuğunu güncelle
            self.parent.gonderilen_durum_label.setText(f"Toplam Gönderilen: {len(self.parent.gonderilen_verileri)}")
            self.parent.durum.gonderilen_sayisi_label.setText(f"Gönderilen: {len(self.parent.gonderilen_verileri)}")
            
        except Exception as e:
            self.parent.hata_goster("Tablo Güncelleme Hatası", str(e))
    
    def hatali_tablosunu_guncelle(self):
        """Hatalı belgeler tablosunu güncelle"""
        try:
            self.parent.hatali_tablo.setRowCount(len(self.parent.hatali_verileri))
            
            for row, belge in enumerate(self.parent.hatali_verileri):
                self.parent.hatali_tablo.setItem(row, 0, QTableWidgetItem(belge["belge_no"]))
                self.parent.hatali_tablo.setItem(row, 1, QTableWidgetItem(belge["tur"]))
                self.parent.hatali_tablo.setItem(row, 2, QTableWidgetItem(belge["musteri"]))
                self.parent.hatali_tablo.setItem(row, 3, QTableWidgetItem(
                    UIYardimcilari.para_formatla(belge["tutar"])
                ))
                self.parent.hatali_tablo.setItem(row, 4, QTableWidgetItem(
                    UIYardimcilari.tarih_formatla(belge["hata_tarihi"])
                ))
                self.parent.hatali_tablo.setItem(row, 5, QTableWidgetItem(belge["hata_kodu"]))
                self.parent.hatali_tablo.setItem(row, 6, QTableWidgetItem(belge["hata_aciklamasi"]))
                
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
                self.parent.hatali_tablo.setCellWidget(row, 7, islem_buton)
            
            # Durum çubuğunu güncelle
            self.parent.hatali_durum_label.setText(f"Toplam Hatalı: {len(self.parent.hatali_verileri)}")
            self.parent.durum.hatali_sayisi_label.setText(f"Hatalı: {len(self.parent.hatali_verileri)}")
            
        except Exception as e:
            self.parent.hata_goster("Tablo Güncelleme Hatası", str(e))