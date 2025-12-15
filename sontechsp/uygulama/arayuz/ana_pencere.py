# Version: 0.1.0
# Last Update: 2024-12-15
# Module: ana_pencere
# Description: SONTECHSP PyQt6 ana pencere sınıfı (sadece mantık)
# Changelog:
# - İlk oluşturma
# - Kod kalitesi: UI bileşenleri ayrı dosyaya taşındı

"""
SONTECHSP Ana Pencere Sınıfı

PyQt6 tabanlı ana pencere mantığı.
UI bileşenleri ayrı dosyada tutulur.

Sorumluluklar:
- Ana pencere mantığı
- Modül navigasyonu
- Oturum yönetimi
- Ekran geçişleri
"""

from typing import Dict, Optional, Any
from PyQt6.QtWidgets import QMainWindow, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

from sontechsp.uygulama.cekirdek.kayit import logger_al
from sontechsp.uygulama.cekirdek.oturum import oturum_baglamini_al
from sontechsp.uygulama.arayuz.taban_ekran import TabanEkran
from sontechsp.uygulama.arayuz.ana_pencere_ui import (
    ana_ui_kur, menu_kur, toolbar_kur, statusbar_kur,
    placeholder_ekran_olustur
)


class AnaPencere(QMainWindow):
    """
    SONTECHSP ana pencere sınıfı
    
    Sol menü + içerik alanı yapısını sağlar.
    Modül ekranları arasında navigasyon yapar.
    """
    
    # Sinyaller
    modul_secildi = pyqtSignal(str)  # Modül seçildiğinde
    oturum_degisti = pyqtSignal(dict)  # Oturum değiştiğinde
    
    def __init__(self):
        super().__init__()
        self.logger = logger_al("ana_pencere")
        self.oturum_baglami = oturum_baglamini_al()
        
        # Modül ekranları saklayıcı
        self._modul_ekranlari: Dict[str, TabanEkran] = {}
        
        # UI kurulumu (UI dosyasından)
        ana_ui_kur(self)
        menu_kur(self)
        toolbar_kur(self)
        statusbar_kur(self)
        self._sinyalleri_bagla()
        
        # Oturum durumu timer'ı
        self._oturum_timer = QTimer()
        self._oturum_timer.timeout.connect(self._oturum_durumunu_kontrol_et)
        self._oturum_timer.start(5000)  # 5 saniyede bir kontrol
        
        self.logger.info("Ana pencere oluşturuldu")
    
    def _sinyalleri_bagla(self):
        """Sinyal-slot bağlantılarını kurar"""
        self.modul_menusu.currentRowChanged.connect(self._modul_secildi)
        self.oturum_degisti.connect(self._oturum_bilgisini_guncelle)
    
    def _modul_secildi(self, index: int):
        """Modül seçildiğinde çağrılır"""
        if index >= 0:
            item = self.modul_menusu.item(index)
            modul_kodu = item.data(Qt.ItemDataRole.UserRole)
            modul_adi = item.text()
            
            self.logger.info(f"Modül seçildi: {modul_adi} ({modul_kodu})")
            
            # Modül ekranını yükle
            self._modul_ekranini_yukle(modul_kodu, modul_adi)
            
            # Sinyal gönder
            self.modul_secildi.emit(modul_kodu)
    
    def _modul_ekranini_yukle(self, modul_kodu: str, modul_adi: str):
        """Modül ekranını yükler"""
        # Önce cache'de var mı kontrol et
        if modul_kodu in self._modul_ekranlari:
            ekran = self._modul_ekranlari[modul_kodu]
            self.icerik_alani.setCurrentWidget(ekran)
            self.statusbar.showMessage(f"{modul_adi} modülü")
            return
        
        # Yeni ekran oluştur (şimdilik placeholder)
        placeholder_ekran = placeholder_ekran_olustur(modul_adi)
        
        # Cache'e ekle
        self._modul_ekranlari[modul_kodu] = placeholder_ekran
        
        # İçerik alanına ekle
        self.icerik_alani.addWidget(placeholder_ekran)
        self.icerik_alani.setCurrentWidget(placeholder_ekran)
        
        self.statusbar.showMessage(f"{modul_adi} modülü")
        self.logger.debug(f"Modül ekranı yüklendi: {modul_kodu}")
    
    def _oturum_durumunu_kontrol_et(self):
        """Oturum durumunu kontrol eder"""
        if self.oturum_baglami.aktif_mi():
            oturum_bilgisi = {
                'kullanici_id': self.oturum_baglami.kullanici_id,
                'magaza_id': self.oturum_baglami.magaza_id,
                'terminal_id': self.oturum_baglami.terminal_id
            }
            self.oturum_degisti.emit(oturum_bilgisi)
    
    def _oturum_bilgisini_guncelle(self, oturum_bilgisi: Dict[str, Any]):
        """Oturum bilgisini günceller"""
        if oturum_bilgisi.get('kullanici_id'):
            kullanici_text = f"Kullanıcı: {oturum_bilgisi['kullanici_id']}"
            if oturum_bilgisi.get('magaza_id'):
                kullanici_text += f" | Mağaza: {oturum_bilgisi['magaza_id']}"
            if oturum_bilgisi.get('terminal_id'):
                kullanici_text += f" | Terminal: {oturum_bilgisi['terminal_id']}"
            
            self.oturum_label.setText(kullanici_text)
        else:
            self.oturum_label.setText("Oturum: Yok")
    
    def modul_ekrani_ekle(self, modul_kodu: str, ekran: TabanEkran):
        """
        Modül ekranı ekler
        
        Args:
            modul_kodu: Modül kodu
            ekran: Ekran widget'ı
        """
        self._modul_ekranlari[modul_kodu] = ekran
        self.icerik_alani.addWidget(ekran)
        self.logger.debug(f"Modül ekranı eklendi: {modul_kodu}")
    
    def aktif_modul_kodunu_al(self) -> Optional[str]:
        """
        Aktif modül kodunu döndürür
        
        Returns:
            Optional[str]: Aktif modül kodu
        """
        secili_index = self.modul_menusu.currentRow()
        if secili_index >= 0:
            item = self.modul_menusu.item(secili_index)
            return item.data(Qt.ItemDataRole.UserRole)
        return None
    
    def closeEvent(self, event):
        """Pencere kapatılırken çağrılır"""
        self.logger.info("Ana pencere kapatılıyor")
        self._oturum_timer.stop()
        event.accept()