# Version: 0.1.0
# Last Update: 2024-12-19
# Module: hizli_urunler_sekmesi
# Description: POS hızlı ürünler sekmesi bileşeni
# Changelog:
# - İlk oluşturma

"""
Hızlı Ürünler Sekmesi - POS hızlı ürün butonları grid sistemi
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, List
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QComboBox, QLabel, QScrollArea
from PyQt6.QtCore import pyqtSignal
from .turkuaz_tema import TurkuazTema


@dataclass
class HizliUrunButonu:
    """Hızlı ürün butonu veri sınıfı"""

    pozisyon: int
    urun_id: Optional[int]
    urun_adi: str
    barkod: str
    fiyat: Decimal
    kategori_id: int
    aktif: bool = True


class HizliUrunlerSekmesi(QWidget):
    """Hızlı ürünler sekmesi widget'ı"""

    hizli_urun_secildi = pyqtSignal(str)  # barkod
    kategori_degisti = pyqtSignal(int)  # kategori_id

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.hizli_urunler: List[HizliUrunButonu] = []
        self.mevcut_kategori = 0
        self.tema = TurkuazTema()
        self.setupUI()

    def setupUI(self):
        """UI bileşenlerini oluşturur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Kategori seçimi
        self.kategori_combo = QComboBox()
        self.kategori_combo.addItem("Tüm Kategoriler", 0)
        self.kategori_combo.currentIndexChanged.connect(self.kategori_secimi_degisti)

        layout.addWidget(QLabel("Kategori:"))
        layout.addWidget(self.kategori_combo)

        # Scroll area için hızlı ürün butonları
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        self.buton_widget = QWidget()
        self.buton_layout = QGridLayout(self.buton_widget)
        self.buton_layout.setSpacing(5)

        scroll_area.setWidget(self.buton_widget)
        layout.addWidget(scroll_area)

        # Başlangıç butonlarını oluştur
        self.butonlari_olustur()

    def butonlari_olustur(self):
        """Hızlı ürün butonlarını oluşturur"""
        # Mevcut butonları temizle
        for i in reversed(range(self.buton_layout.count())):
            self.buton_layout.itemAt(i).widget().setParent(None)

        # 4x6 = 24 buton grid'i
        satir_sayisi = 6
        sutun_sayisi = 4

        for i in range(24):
            satir = i // sutun_sayisi
            sutun = i % sutun_sayisi

            # Hızlı ürün varsa bilgilerini al
            hizli_urun = None
            if i < len(self.hizli_urunler):
                hizli_urun = self.hizli_urunler[i]
                if hizli_urun.kategori_id != self.mevcut_kategori and self.mevcut_kategori != 0:
                    hizli_urun = None

            # Buton oluştur
            if hizli_urun and hizli_urun.aktif:
                buton_metni = f"{hizli_urun.urun_adi}\n{hizli_urun.fiyat:.2f} ₺"
                buton = QPushButton(buton_metni)
                buton.setProperty("class", self.tema.buton_stil_sinifi_al("hizli_urun"))
                buton.clicked.connect(lambda checked, barkod=hizli_urun.barkod: self.hizli_urun_tiklandi(barkod))
            else:
                buton = QPushButton(f"Boş\n{i+1}")
                buton.setProperty("class", self.tema.buton_stil_sinifi_al("hizli_urun"))
                buton.setEnabled(False)

            buton.setMinimumHeight(60)
            buton.setMaximumHeight(80)
            self.buton_layout.addWidget(buton, satir, sutun)

    def hizli_urun_tiklandi(self, barkod: str):
        """Hızlı ürün butonuna tıklandığında çalışır"""
        self.hizli_urun_secildi.emit(barkod)

    def kategori_secimi_degisti(self, index: int):
        """Kategori seçimi değiştiğinde çalışır"""
        kategori_id = self.kategori_combo.itemData(index)
        self.mevcut_kategori = kategori_id
        self.butonlari_olustur()
        self.kategori_degisti.emit(kategori_id)

    def hizli_urunleri_yukle(self, urunler: List[HizliUrunButonu]):
        """Hızlı ürünleri yükler"""
        self.hizli_urunler = urunler
        self.butonlari_olustur()

    def kategori_ekle(self, kategori_id: int, kategori_adi: str):
        """Kategori dropdown'ına yeni kategori ekler"""
        self.kategori_combo.addItem(kategori_adi, kategori_id)

    def kategorileri_temizle(self):
        """Kategori dropdown'ını temizler"""
        self.kategori_combo.clear()
        self.kategori_combo.addItem("Tüm Kategoriler", 0)

    def hizli_urun_guncelle(self, pozisyon: int, urun: HizliUrunButonu):
        """Belirli pozisyondaki hızlı ürünü günceller"""
        if 0 <= pozisyon < 24:
            # Mevcut listede pozisyon varsa güncelle, yoksa ekle
            while len(self.hizli_urunler) <= pozisyon:
                self.hizli_urunler.append(None)

            self.hizli_urunler[pozisyon] = urun
            self.butonlari_olustur()
