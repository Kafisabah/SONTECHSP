# Version: 0.1.0
# Last Update: 2024-12-18
# Module: uygulama.arayuz.ekranlar.ayarlar.ayar_butonlari
# Description: Ayarlar ekranı alt butonları ve event handler'ları
# Changelog:
# - İlk sürüm oluşturuldu

from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QFrame
from PyQt6.QtCore import QTimer


class AyarButonlari:
    """Ayarlar ekranı butonları ve event handler'ları"""
    
    def __init__(self, parent_ekran):
        self.parent = parent_ekran
    
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
    
    def varsayilana_don(self):
        """Varsayılan ayarlara dön"""
        try:
            if not self.parent.onay_iste("Onay", "Tüm ayarlar varsayılan değerlere döndürülecek. Emin misiniz?"):
                return
            
            # Varsayılan değerleri yükle (stub)
            self.parent.bilgi_goster_mesaj("Başarılı", "Ayarlar varsayılan değerlere döndürüldü")
            self.parent.degisiklikler.clear()
            self.parent.degisiklik_sayisini_guncelle()
            
        except Exception as e:
            self.parent.hata_goster("Varsayılan Ayarlar Hatası", str(e))
    
    def ice_aktar(self):
        """Ayarları içe aktar"""
        try:
            # İçe aktarma dialog'u (stub)
            self.parent.bilgi_goster_mesaj("Bilgi", "Ayar dosyası seçme dialog'u açılacak")
            
        except Exception as e:
            self.parent.hata_goster("İçe Aktarma Hatası", str(e))
    
    def disa_aktar(self):
        """Ayarları dışa aktar"""
        try:
            # Dışa aktarma dialog'u (stub)
            self.parent.bilgi_goster_mesaj("Bilgi", "Ayar dosyası kaydetme dialog'u açılacak")
            
        except Exception as e:
            self.parent.hata_goster("Dışa Aktarma Hatası", str(e))
    
    def degisiklikleri_iptal(self):
        """Değişiklikleri iptal et"""
        try:
            if self.parent.degisiklikler:
                if not self.parent.onay_iste("Onay", "Yapılan değişiklikler iptal edilecek. Emin misiniz?"):
                    return
                
                self.parent.degisiklikler.clear()
                self.parent.degisiklik_sayisini_guncelle()
                self.parent.bilgi_goster_mesaj("Bilgi", "Değişiklikler iptal edildi")
            
        except Exception as e:
            self.parent.hata_goster("İptal Hatası", str(e))
    
    def ayarlari_kaydet(self):
        """Ayarları kaydet"""
        try:
            if not self.parent.degisiklikler:
                self.parent.bilgi_goster_mesaj("Bilgi", "Kaydedilecek değişiklik bulunmuyor")
                return
            
            # Ayar servisini çağır
            ayar_servisi = self.parent.servis_fabrikasi.ayar_servisi()
            
            # İşlem başlat
            self.parent.islem_baslat("Ayarlar kaydediliyor...")
            
            sonuc = self.parent.servis_cagir_guvenli(ayar_servisi.kaydet, self.parent.degisiklikler)
            
            if sonuc:
                self.parent.degisiklikler.clear()
                self.parent.degisiklik_sayisini_guncelle()
                self.parent.bilgi_goster_mesaj("Başarılı", "Ayarlar başarıyla kaydedildi")
            
            self.parent.islem_bitir()
            
        except Exception as e:
            self.parent.islem_bitir()
            self.parent.hata_goster("Kaydetme Hatası", str(e))