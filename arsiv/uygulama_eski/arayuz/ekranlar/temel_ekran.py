# Version: 0.2.0
# Last Update: 2024-12-18
# Module: uygulama.arayuz.ekranlar.temel_ekran
# Description: Tüm ekranlar için temel sınıf
# Changelog:
# - İlk sürüm oluşturuldu
# - Buton kayıt desteği ve wrapper fonksiyonu eklendi

from typing import Callable, Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from ..servis_fabrikasi import ServisFabrikasi
from ..yardimcilar import UIYardimcilari
from ..buton_eslestirme_kaydi import kayit_ekle
from ..log_sistemi import handler_loglama, stub_servis_loglama, LogDurumu


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
            self.hata_goster("Servis Hatası", f"İşlem sırasında hata oluştu: {str(e)}")
            return None

    def buton_bagla_ve_kaydet(
        self, buton: QPushButton, buton_adi: str, handler_fonksiyonu: Callable, servis_metodu: Optional[str] = None
    ) -> None:
        """
        Buton bağlama wrapper fonksiyonu - otomatik kayıt ve loglama ile

        Args:
            buton: QPushButton nesnesi
            buton_adi: Butonun adı (kayıt için)
            handler_fonksiyonu: Buton tıklandığında çağrılacak fonksiyon
            servis_metodu: Çağrılan servis metodunun adı (opsiyonel)
        """
        # Ekran adını al (sınıf adından)
        ekran_adi = self.__class__.__name__
        handler_adi = handler_fonksiyonu.__name__

        # Buton eşleştirmesini kaydet
        kayit_ekle(ekran_adi, buton_adi, handler_adi, servis_metodu)

        # Wrapper handler oluştur
        def wrapper_handler():
            try:
                # Handler loglama
                handler_loglama(
                    ekran_adi=ekran_adi,
                    buton_adi=buton_adi,
                    handler_adi=handler_adi,
                    servis_metodu=servis_metodu,
                    durum=LogDurumu.BASARILI,
                    detay="Buton handler çalıştırıldı",
                )

                # Gerçek handler'ı çağır
                result = handler_fonksiyonu()

                # Eğer stub servis çağrısı varsa logla
                if servis_metodu and "stub" in servis_metodu.lower():
                    stub_servis_loglama(
                        ekran_adi=ekran_adi,
                        buton_adi=buton_adi,
                        handler_adi=handler_adi,
                        servis_metodu=servis_metodu,
                        detay="Stub servis çağrıldı",
                    )

                return result

            except Exception as e:
                # Hata durumunda log
                handler_loglama(
                    ekran_adi=ekran_adi,
                    buton_adi=buton_adi,
                    handler_adi=handler_adi,
                    servis_metodu=servis_metodu,
                    durum=LogDurumu.HATA,
                    detay=f"Handler hatası: {str(e)}",
                )

                # Hata mesajı göster
                self.hata_goster("Handler Hatası", f"Buton işlemi sırasında hata: {str(e)}")

        # Buton sinyalini bağla
        buton.clicked.connect(wrapper_handler)

    def showEvent(self, event):
        """Ekran gösterildiğinde çağrılır"""
        super().showEvent(event)
        if self.ekran_hazir:
            self.verileri_yukle()

    def hideEvent(self, event):
        """Ekran gizlendiğinde çağrılır"""
        super().hideEvent(event)
        self.verileri_temizle()
