# Version: 0.1.0
# Last Update: 2024-12-16
# Module: uygulama.arayuz.uygulama
# Description: PyQt6 uygulama başlatıcısı
# Changelog:
# - İlk sürüm oluşturuldu

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from .ana_pencere import AnaPencere
from .servis_fabrikasi import ServisFabrikasi


class UygulamaBaslatici:
    """SONTECHSP PyQt6 uygulama başlatıcısı"""
    
    def __init__(self):
        self.app = None
        self.ana_pencere = None
        self.servis_fabrikasi = None
    
    def arayuzu_baslat(self):
        """Ana arayüz başlatma fonksiyonu"""
        try:
            # QApplication oluştur
            self.app = QApplication(sys.argv)
            
            # Tema yükle
            self.tema_yukle()
            
            # Servis fabrikasını oluştur
            self.servis_fabrikasi = ServisFabrikasi()
            
            # Ana pencereyi oluştur ve göster
            self.ana_pencere = AnaPencere(self.servis_fabrikasi)
            self.ana_pencere.show()
            
            # Uygulama döngüsünü başlat
            return self.app.exec()
            
        except Exception as e:
            print(f"Uygulama başlatma hatası: {e}")
            return -1
    
    def tema_yukle(self):
        """Tema ve stylesheet yer tutucu"""
        # Temel tema ayarları (yer tutucu)
        stylesheet = """
        QMainWindow {
            background-color: #f0f0f0;
        }
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #106ebe;
        }
        """
        if self.app:
            self.app.setStyleSheet(stylesheet)
    
    def kaynaklari_temizle(self):
        """Uygulama kapatılırken kaynakları temizle"""
        try:
            if self.ana_pencere:
                self.ana_pencere.close()
                self.ana_pencere = None
            
            if self.app:
                self.app.quit()
                self.app = None
                
            self.servis_fabrikasi = None
            
        except Exception as e:
            print(f"Kaynak temizleme hatası: {e}")


def main():
    """Ana giriş noktası"""
    baslatici = UygulamaBaslatici()
    
    try:
        return baslatici.arayuzu_baslat()
    finally:
        baslatici.kaynaklari_temizle()


if __name__ == "__main__":
    sys.exit(main())