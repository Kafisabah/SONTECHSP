# Version: 0.1.0
# Last Update: 2024-12-16
# Module: uygulama.arayuz.ekranlar.gosterge_paneli
# Description: Gösterge paneli ekranı
# Changelog:
# - İlk sürüm oluşturuldu

from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame, QGridLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from .temel_ekran import TemelEkran
from ..servis_fabrikasi import ServisFabrikasi
from ..yardimcilar import UIYardimcilari
from ..buton_eslestirme_kaydi import kayit_ekle
from ..log_sistemi import stub_servis_loglama


class GostergePaneli(TemelEkran):
    """Gösterge paneli ekranı"""

    # Ekran değişim sinyali
    ekran_degistir_istegi = pyqtSignal(str)

    def __init__(self, servis_fabrikasi: ServisFabrikasi, parent=None):
        self.ciro_label = None
        self.kritik_stok_label = None
        self.bekleyen_siparis_label = None
        super().__init__(servis_fabrikasi, parent)

    def ekrani_hazirla(self):
        """Gösterge paneli ekranını hazırla"""
        # Ana başlık
        baslik = QLabel("Gösterge Paneli")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        baslik.setStyleSheet("color: #2c3e50; margin: 20px;")

        self.ana_layout.addWidget(baslik)

        # Kartlar alanı
        kartlar_widget = self.kartlar_olustur()
        self.ana_layout.addWidget(kartlar_widget)

        # Hızlı erişim butonları
        butonlar_widget = self.hizli_erisim_butonlari_olustur()
        self.ana_layout.addWidget(butonlar_widget)

        # Boşluk ekle
        self.ana_layout.addStretch()

        self.ekran_hazir = True

    def kartlar_olustur(self):
        """Bilgi kartlarını oluştur"""
        kartlar_frame = QFrame()
        kartlar_layout = QGridLayout(kartlar_frame)
        kartlar_layout.setSpacing(20)

        # Günlük ciro kartı
        ciro_kart = self.kart_olustur("Bugün Ciro", "0,00 TL", "#3498db")
        self.ciro_label = ciro_kart.findChild(QLabel, "deger_label")
        kartlar_layout.addWidget(ciro_kart, 0, 0)

        # Kritik stok kartı
        kritik_stok_kart = self.kart_olustur("Kritik Stok", "0 Ürün", "#e74c3c")
        self.kritik_stok_label = kritik_stok_kart.findChild(QLabel, "deger_label")
        kartlar_layout.addWidget(kritik_stok_kart, 0, 1)

        # Bekleyen sipariş kartı
        bekleyen_siparis_kart = self.kart_olustur("Bekleyen Sipariş", "0 Sipariş", "#f39c12")
        self.bekleyen_siparis_label = bekleyen_siparis_kart.findChild(QLabel, "deger_label")
        kartlar_layout.addWidget(bekleyen_siparis_kart, 0, 2)

        return kartlar_frame

    def kart_olustur(self, baslik: str, deger: str, renk: str):
        """Tek bir bilgi kartı oluştur"""
        kart = QFrame()
        kart.setFixedSize(200, 120)
        kart.setStyleSheet(
            f"""
            QFrame {{
                background-color: {renk};
                border-radius: 10px;
                border: none;
            }}
            QLabel {{
                color: white;
                border: none;
            }}
        """
        )

        layout = QVBoxLayout(kart)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Başlık
        baslik_label = QLabel(baslik)
        baslik_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(baslik_label)

        # Değer
        deger_label = QLabel(deger)
        deger_label.setObjectName("deger_label")
        deger_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        deger_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(deger_label)

        return kart

    def hizli_erisim_butonlari_olustur(self):
        """Hızlı erişim butonlarını oluştur"""
        butonlar_frame = QFrame()
        butonlar_layout = QHBoxLayout(butonlar_frame)
        butonlar_layout.setSpacing(15)

        # POS'a Git butonu
        pos_buton = QPushButton("POS Satış")
        pos_buton.setFixedSize(150, 50)
        pos_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """
        )
        # Wrapper fonksiyonu ile buton bağla
        self.buton_bagla_ve_kaydet(
            pos_buton, "POS Satış", lambda: self.hizli_erisim_tiklandi("pos_satis"), "ekran_degistir_istegi"
        )
        butonlar_layout.addWidget(pos_buton)

        # Kritik Stok'a Git butonu
        stok_buton = QPushButton("Kritik Stok")
        stok_buton.setFixedSize(150, 50)
        stok_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """
        )
        # Wrapper fonksiyonu ile buton bağla
        self.buton_bagla_ve_kaydet(
            stok_buton, "Kritik Stok", lambda: self.hizli_erisim_tiklandi("urunler_stok"), "ekran_degistir_istegi"
        )
        butonlar_layout.addWidget(stok_buton)

        # Ortalama için boşluk
        butonlar_layout.addStretch()

        return butonlar_frame

    def hizli_erisim_tiklandi(self, ekran_adi: str):
        """Hızlı erişim butonu tıklandığında"""
        try:
            # Ana pencereye sinyal gönder
            self.ekran_degistir_istegi.emit(ekran_adi)
        except Exception as e:
            self.hata_goster("Navigasyon Hatası", f"Ekran değiştirme hatası: {e}")

    def verileri_yukle(self):
        """Gösterge paneli verilerini yükle"""
        try:
            # Günlük ciro bilgisi (stub)
            ciro = self.servis_cagir_guvenli(self.gunluk_ciro_getir)
            if ciro is not None and self.ciro_label:
                self.ciro_label.setText(UIYardimcilari.para_formatla(ciro))

            # Kritik stok sayısı (stub)
            kritik_stok = self.servis_cagir_guvenli(self.kritik_stok_sayisi_getir)
            if kritik_stok is not None and self.kritik_stok_label:
                self.kritik_stok_label.setText(f"{kritik_stok} Ürün")

            # Bekleyen sipariş sayısı (stub)
            bekleyen_siparis = self.servis_cagir_guvenli(self.bekleyen_siparis_sayisi_getir)
            if bekleyen_siparis is not None and self.bekleyen_siparis_label:
                self.bekleyen_siparis_label.setText(f"{bekleyen_siparis} Sipariş")

        except Exception as e:
            self.hata_goster("Veri Yükleme Hatası", f"Veriler yüklenirken hata: {e}")

    def gunluk_ciro_getir(self):
        """Günlük ciro bilgisini getir (stub)"""
        # Stub servis loglama
        stub_servis_loglama(
            ekran_adi="GostergePaneli",
            buton_adi="Veri Yükleme",
            handler_adi="gunluk_ciro_getir",
            servis_metodu="rapor_servisi.gunluk_ciro_getir_stub",
            detay="Günlük ciro stub verisi döndürüldü",
        )

        # Gerçek implementasyonda rapor servisi kullanılacak
        rapor_servisi = self.servis_fabrikasi.rapor_servisi()
        # Stub veri
        return 1250.75

    def kritik_stok_sayisi_getir(self):
        """Kritik stok sayısını getir (stub)"""
        # Stub servis loglama
        stub_servis_loglama(
            ekran_adi="GostergePaneli",
            buton_adi="Veri Yükleme",
            handler_adi="kritik_stok_sayisi_getir",
            servis_metodu="stok_servisi.kritik_stok_sayisi_getir_stub",
            detay="Kritik stok sayısı stub verisi döndürüldü",
        )

        # Gerçek implementasyonda stok servisi kullanılacak
        stok_servisi = self.servis_fabrikasi.stok_servisi()
        # Stub veri
        return 5

    def bekleyen_siparis_sayisi_getir(self):
        """Bekleyen sipariş sayısını getir (stub)"""
        # Stub servis loglama
        stub_servis_loglama(
            ekran_adi="GostergePaneli",
            buton_adi="Veri Yükleme",
            handler_adi="bekleyen_siparis_sayisi_getir",
            servis_metodu="eticaret_servisi.bekleyen_siparis_sayisi_getir_stub",
            detay="Bekleyen sipariş sayısı stub verisi döndürüldü",
        )

        # Gerçek implementasyonda e-ticaret servisi kullanılacak
        eticaret_servisi = self.servis_fabrikasi.eticaret_servisi()
        # Stub veri
        return 12
