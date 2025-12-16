# Version: 0.1.0
# Last Update: 2024-12-16
# Module: uygulama.arayuz.ekranlar.temel_ekran
# Description: Tüm ekranlar için temel sınıf
# Changelog:
# - İlk sürüm oluşturuldu

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from ..servis_fabrikasi import ServisFabrikasi
from ..yardimcilar import UIYardimcilari


class TemelEkran(QWidget):
    """Tüm ekranlar için temel sınıf"""
    
    # Sinyaller
    hata_olustu = pyqtSignal(str, str)  # başlık, mesaj
    bilgi_goster = pyqtSignal(str, str)  # başlık, mesaj
    
    def __init__(self, servis_fabrikasi: ServisFabrikasi, parent=None):
        super().__init__(parent)
        self.servis_fabrikasi = servis_fabrikasi
        self.ekran_hazir = False
        
        # Temel layout oluştur
        self.ana_layout = QVBoxLayout(self)
        self.ana_layout.setContentsMargins(20, 20, 20, 20)
        self.ana_layout.setSpacing(15)
        
        # Ekranı hazırla
        self.ekrani_hazirla()
        
        # Sinyalleri bağla
        self.sinyalleri_bagla()
    
    def ekrani_hazirla(self):
        """Alt sınıflar bu metodu override etmeli"""
        # Varsayılan başlık
        baslik = QLabel("Temel Ekran")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        baslik.setStyleSheet("color: #2c3e50; margin: 20px;")
        
        self.ana_layout.addWidget(baslik)
        self.ekran_hazir = True
    
    def sinyalleri_bagla(self):
        """Sinyal bağlantılarını kur"""
        self.hata_olustu.connect(self.hata_goster_slot)
        self.bilgi_goster.connect(self.bilgi_goster_slot)
    
    def verileri_yukle(self):
        """Ekran verileri yükleme - alt sınıflar override etmeli"""
        pass
    
    def verileri_temizle(self):
        """Ekran verilerini temizle - alt sınıflar override etmeli"""
        pass
    
    def hata_goster(self, baslik: str, mesaj: str):
        """Hata mesajı göster"""
        try:
            UIYardimcilari.hata_goster(self, baslik, mesaj)
        except Exception as e:
            print(f"Hata gösterim hatası: {e}")
    
    def bilgi_goster_mesaj(self, baslik: str, mesaj: str):
        """Bilgi mesajı göster"""
        try:
            UIYardimcilari.bilgi_goster(self, baslik, mesaj)
        except Exception as e:
            print(f"Bilgi gösterim hatası: {e}")
    
    def onay_iste(self, baslik: str, mesaj: str) -> bool:
        """Kullanıcıdan onay iste"""
        try:
            return UIYardimcilari.onay_iste(self, baslik, mesaj)
        except Exception as e:
            print(f"Onay dialog hatası: {e}")
            return False
    
    def hata_goster_slot(self, baslik: str, mesaj: str):
        """Hata gösterme slot'u"""
        self.hata_goster(baslik, mesaj)
    
    def bilgi_goster_slot(self, baslik: str, mesaj: str):
        """Bilgi gösterme slot'u"""
        self.bilgi_goster_mesaj(baslik, mesaj)
    
    def servis_cagir_guvenli(self, servis_fonksiyonu, *args, **kwargs):
        """Güvenli servis çağrısı"""
        try:
            return servis_fonksiyonu(*args, **kwargs)
        except Exception as e:
            self.hata_goster(
                "Servis Hatası", 
                f"İşlem sırasında hata oluştu: {str(e)}"
            )
            return None
    
    def showEvent(self, event):
        """Ekran gösterildiğinde çağrılır"""
        super().showEvent(event)
        if self.ekran_hazir:
            self.verileri_yukle()
    
    def hideEvent(self, event):
        """Ekran gizlendiğinde çağrılır"""
        super().hideEvent(event)
        self.verileri_temizle()