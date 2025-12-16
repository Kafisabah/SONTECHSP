# Version: 0.1.0
# Last Update: 2024-12-15
# Module: taban_ekran
# Description: SONTECHSP arayüz katmanı temel ekran sınıfı
# Changelog:
# - İlk oluşturma
# - Metaclass sorunu çözüldü
# - 120 satır limitine uygun hale getirildi

"""
SONTECHSP Arayüz Katmanı Temel Ekran Sınıfı

Tüm modül ekranlarının türeyeceği temel sınıf.
Katmanlar arası bağımlılık kurallarını uygular.
"""

from abc import abstractmethod
from typing import Optional

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from sontechsp.uygulama.arayuz.taban_ui_bilesenleri import (
    AltAracCubuguYoneticisi,
    BaslikAlaniYoneticisi,
    IcerikAlaniYoneticisi,
    MesajYoneticisi
)
from sontechsp.uygulama.cekirdek.kayit import kayit_al
from sontechsp.uygulama.cekirdek.oturum import oturum_baglamini_al


class TabanEkran(QWidget):
    """
    Tüm modül ekranlarının türeyeceği temel sınıf
    
    Katman kuralları:
    - Sadece servis katmanını çağırır
    - Veritabanına doğrudan erişemez
    - Repository katmanını çağıramaz
    """
    
    # Sinyaller
    veri_degisti = pyqtSignal(dict)
    hata_olustu = pyqtSignal(str)
    yukleme_basladi = pyqtSignal()
    yukleme_bitti = pyqtSignal()
    
    def __init__(self, ekran_adi: str, parent: Optional[QWidget] = None):
        """
        Ekran başlatıcı
        
        Args:
            ekran_adi: Ekran adı
            parent: Üst widget
        """
        super().__init__(parent)
        
        self.ekran_adi = ekran_adi
        self.setWindowTitle(ekran_adi)  # Window title ayarla
        self.logger = kayit_al(f"ekran.{ekran_adi}")
        self.oturum_baglami = oturum_baglamini_al()
        
        # Durum değişkenleri
        self._yukleme_durumu = False
        self._veri_degisti_mi = False
        
        # UI yöneticileri
        self._ui_yoneticilerini_kur()
        self._sinyalleri_bagla()
        
        self.logger.debug(f"{ekran_adi} ekranı oluşturuldu")
    
    def _ui_yoneticilerini_kur(self):
        """UI yöneticilerini kurar"""
        # Ana layout
        self.ana_layout = QVBoxLayout(self)
        self.ana_layout.setContentsMargins(10, 10, 10, 10)
        self.ana_layout.setSpacing(10)
        
        # UI bileşen yöneticileri
        self.baslik_yoneticisi = BaslikAlaniYoneticisi(self.ekran_adi)
        self.icerik_yoneticisi = IcerikAlaniYoneticisi()
        self.alt_arac_yoneticisi = AltAracCubuguYoneticisi()
        self.mesaj_yoneticisi = MesajYoneticisi(self)
        
        # Layout'a ekle
        self.ana_layout.addWidget(self.baslik_yoneticisi.widget)
        self.ana_layout.addWidget(self.icerik_yoneticisi.widget)
        self.ana_layout.addWidget(self.alt_arac_yoneticisi.widget)
        self.ana_layout.addWidget(self.mesaj_yoneticisi.progress_bar)
        
        # Alt sınıfların içerik eklemesi için
        self._icerik_olustur()
    
    @property
    def icerik_layout(self):
        """İçerik layout'una erişim sağlar"""
        return self.icerik_yoneticisi.layout
    
    def _sinyalleri_bagla(self):
        """Sinyal-slot bağlantılarını kurar"""
        self.hata_olustu.connect(self.mesaj_yoneticisi.hata_goster)
        self.yukleme_basladi.connect(self._yukleme_basladi_slot)
        self.yukleme_bitti.connect(self._yukleme_bitti_slot)
        
        # Yenile butonunu bağla
        self.alt_arac_yoneticisi.yenile_buton.clicked.connect(self.yenile)
    
    @abstractmethod
    def _icerik_olustur(self):
        """Alt sınıfların içerik oluşturması için soyut metod"""
        pass
    
    @abstractmethod
    def yenile(self):
        """Alt sınıflar bu metodu implement etmelidir"""
        pass
    
    @pyqtSlot()
    def _yukleme_basladi_slot(self):
        """Yükleme başladığında çağrılır"""
        self.setEnabled(False)
        self.alt_arac_yoneticisi.durum_guncelle("Yükleniyor...")
    
    @pyqtSlot()
    def _yukleme_bitti_slot(self):
        """Yükleme bittiğinde çağrılır"""
        self.setEnabled(True)
        self.alt_arac_yoneticisi.durum_guncelle("Hazır")
    
    def veri_degisti_isaretle(self):
        """Veri değiştiğini işaretler"""
        self._veri_degisti_mi = True
        self.veri_degisti.emit({'ekran': self.ekran_adi})