# Version: 0.1.0
# Last Update: 2024-12-18
# Module: hizli_urun_paneli
# Description: POS hızlı ürün paneli bileşeni
# Changelog:
# - İlk oluşturma - Hızlı ürün paneli widget'ı

"""
POS Hızlı Ürün Paneli Bileşeni

Sık kullanılan ürünlerin hızlı erişim butonlarını sağlar.
Kategori bazlı dinamik buton sistemi ile çalışır.

Sorumluluklar:
- Hızlı ürün butonlarını gösterme
- Kategori seçimi
- Ürün butonlarını dinamik güncelleme
- Boş butonları yönetme
"""

from typing import Dict, Any, List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..handlers.pos_sinyalleri import POSSinyalleri
from .pos_bilesen_arayuzu import POSBilesenWidget


class HizliUrunPaneli(POSBilesenWidget):
    """
    Hızlı Ürün Paneli Widget'ı

    Sık kullanılan ürünlerin hızlı erişim butonlarını sağlar.
    """

    # Sinyaller
    hizli_urun_secildi = pyqtSignal(dict)  # ürün verisi
    kategori_degisti = pyqtSignal(str)  # kategori adı

    def __init__(self, sinyaller: POSSinyalleri, parent=None):
        super().__init__(parent)
        self.sinyaller = sinyaller
        self._kategoriler: List[Dict[str, Any]] = []
        self._hizli_urunler: List[Dict[str, Any]] = []
        self._aktif_kategori = ""
        self._buton_sayisi = 12  # Varsayılan 12 buton
        self._butonlar: List[QPushButton] = []
        self._ui_kuruldu = False
        self._ui_kur()
        self._sinyalleri_bagla()
        self._varsayilan_verileri_yukle()

    def _ui_kur(self):
        """UI bileşenlerini kurar"""
        if self._ui_kuruldu:
            return

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Başlık
        baslik = QLabel("HIZLI ÜRÜNLER")
        baslik.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(baslik)

        # Kategori seçici
        kategori_frame = QFrame()
        kategori_layout = QHBoxLayout(kategori_frame)
        kategori_layout.setContentsMargins(0, 0, 0, 0)

        kategori_label = QLabel("Kategori:")
        kategori_label.setFont(QFont("Arial", 9))
        kategori_layout.addWidget(kategori_label)

        self.kategori_combo = QComboBox()
        self.kategori_combo.setMinimumWidth(120)
        self.kategori_combo.currentTextChanged.connect(self._kategori_secildi)
        kategori_layout.addWidget(self.kategori_combo)

        kategori_layout.addStretch()

        # Buton sayısı ayarı
        buton_sayisi_label = QLabel("Buton:")
        buton_sayisi_label.setFont(QFont("Arial", 9))
        kategori_layout.addWidget(buton_sayisi_label)

        self.buton_sayisi_combo = QComboBox()
        self.buton_sayisi_combo.setEditable(True)  # Düzenlenebilir yap
        self.buton_sayisi_combo.addItems(["12", "16", "20", "24"])
        self.buton_sayisi_combo.setCurrentText("12")
        self.buton_sayisi_combo.currentTextChanged.connect(self._buton_sayisi_degisti)
        kategori_layout.addWidget(self.buton_sayisi_combo)

        layout.addWidget(kategori_frame)

        # Scroll area için hızlı ürün butonları
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Butonlar için widget
        self.butonlar_widget = QWidget()
        self.butonlar_layout = QGridLayout(self.butonlar_widget)
        self.butonlar_layout.setSpacing(5)

        scroll_area.setWidget(self.butonlar_widget)
        layout.addWidget(scroll_area)

        self._ui_kuruldu = True

    def _sinyalleri_bagla(self):
        """Sinyalleri bağlar"""
        self.sinyaller.hizli_urunler_guncellendi.connect(self._hizli_urunler_guncellendi)
        self.sinyaller.kategoriler_guncellendi.connect(self._kategoriler_guncellendi)

    def _varsayilan_verileri_yukle(self):
        """Varsayılan test verilerini yükler"""
        # Varsayılan kategoriler
        self._kategoriler = [
            {"id": "1", "ad": "İçecekler", "aktif": True},
            {"id": "2", "ad": "Atıştırmalık", "aktif": True},
            {"id": "3", "ad": "Temizlik", "aktif": True},
            {"id": "4", "ad": "Kırtasiye", "aktif": True},
        ]

        # Varsayılan hızlı ürünler
        self._hizli_urunler = [
            {
                "id": "1",
                "barkod": "8690504123456",
                "urun_adi": "Coca Cola 330ml",
                "birim_fiyat": 5.50,
                "kategori_id": "1",
                "pozisyon": 0,
            },
            {
                "id": "2",
                "barkod": "8690504123457",
                "urun_adi": "Fanta 330ml",
                "birim_fiyat": 5.50,
                "kategori_id": "1",
                "pozisyon": 1,
            },
        ]

        self._kategorileri_guncelle()
        self._butonlari_olustur()

    def _kategorileri_guncelle(self):
        """Kategori combo box'ını günceller"""
        self.kategori_combo.clear()
        self.kategori_combo.addItem("Tümü", "")

        for kategori in self._kategoriler:
            if kategori.get("aktif", True):
                self.kategori_combo.addItem(kategori["ad"], kategori["id"])

        # İlk kategoriyi seç
        if self._kategoriler:
            self.kategori_combo.setCurrentIndex(1)  # "Tümü" değil, ilk kategori

    def _kategori_secildi(self, kategori_adi: str):
        """Kategori seçildiğinde çağrılır"""
        kategori_id = self.kategori_combo.currentData()
        self._aktif_kategori = kategori_id or ""
        self._butonlari_guncelle()
        self.kategori_degisti.emit(kategori_adi)

    def _buton_sayisi_degisti(self, yeni_sayi: str):
        """Buton sayısı değiştiğinde çağrılır"""
        try:
            yeni_buton_sayisi = int(yeni_sayi)
            # 12-24 arası değer kontrolü
            if 12 <= yeni_buton_sayisi <= 24:
                self._buton_sayisi = yeni_buton_sayisi
                self._butonlari_olustur()
        except ValueError:
            pass

    def _butonlari_olustur(self):
        """Hızlı ürün butonlarını oluşturur"""
        # Mevcut butonları temizle
        for buton in self._butonlar:
            buton.deleteLater()
        self._butonlar.clear()

        # Grid düzeni hesapla (4 sütun)
        sutun_sayisi = 4
        satir_sayisi = (self._buton_sayisi + sutun_sayisi - 1) // sutun_sayisi

        # Yeni butonları oluştur
        for i in range(self._buton_sayisi):
            buton = QPushButton("Tanımsız")
            buton.setMinimumSize(80, 60)
            buton.setMaximumSize(120, 80)
            buton.setFont(QFont("Arial", 8))
            buton.setStyleSheet(
                """
                QPushButton {
                    background-color: #ecf0f1;
                    border: 1px solid #bdc3c7;
                    border-radius: 5px;
                    color: #7f8c8d;
                }
                QPushButton:hover {
                    background-color: #d5dbdb;
                }
                QPushButton:pressed {
                    background-color: #bdc3c7;
                }
                QPushButton[hasProduct="true"] {
                    background-color: #3498db;
                    color: white;
                    font-weight: bold;
                }
                QPushButton[hasProduct="true"]:hover {
                    background-color: #2980b9;
                }
            """
            )

            # Buton pozisyonunu hesapla
            satir = i // sutun_sayisi
            sutun = i % sutun_sayisi

            # Butonu grid'e ekle
            self.butonlar_layout.addWidget(buton, satir, sutun)

            # Buton click handler'ını bağla
            buton.clicked.connect(lambda checked, idx=i: self._hizli_urun_butonu_tiklandi(idx))

            self._butonlar.append(buton)

        self._butonlari_guncelle()

    def _butonlari_guncelle(self):
        """Butonları aktif kategoriye göre günceller"""
        # Önce tüm butonları sıfırla
        for i, buton in enumerate(self._butonlar):
            buton.setText("Tanımsız")
            buton.setProperty("hasProduct", False)
            buton.setProperty("productData", None)
            buton.style().unpolish(buton)
            buton.style().polish(buton)

        # Aktif kategoriye ait ürünleri bul
        kategori_urunleri = []
        for urun in self._hizli_urunler:
            if not self._aktif_kategori or urun.get("kategori_id") == self._aktif_kategori:
                kategori_urunleri.append(urun)

        # Ürünleri pozisyonlarına göre sırala
        kategori_urunleri.sort(key=lambda x: x.get("pozisyon", 999))

        # Ürünleri butonlara ata
        for urun in kategori_urunleri:
            pozisyon = urun.get("pozisyon", 0)
            if 0 <= pozisyon < len(self._butonlar):
                buton = self._butonlar[pozisyon]
                buton.setText(urun["urun_adi"])
                buton.setProperty("hasProduct", True)
                buton.setProperty("productData", urun)
                buton.style().unpolish(buton)
                buton.style().polish(buton)

    def _hizli_urun_butonu_tiklandi(self, pozisyon: int):
        """Hızlı ürün butonu tıklandığında çağrılır"""
        if pozisyon >= len(self._butonlar):
            return

        buton = self._butonlar[pozisyon]
        urun_verisi = buton.property("productData")

        if urun_verisi:
            self.hizli_urun_secildi.emit(urun_verisi)
            self.sinyaller.urun_eklendi.emit(urun_verisi)

    def _hizli_urunler_guncellendi(self, urunler: List[Dict[str, Any]]):
        """Hızlı ürünler güncellendiğinde çağrılır"""
        self._hizli_urunler = urunler
        self._butonlari_guncelle()

    def _kategoriler_guncellendi(self, kategoriler: List[Dict[str, Any]]):
        """Kategoriler güncellendiğinde çağrılır"""
        self._kategoriler = kategoriler
        self._kategorileri_guncelle()

    def baslat(self) -> None:
        """Bileşeni başlatır"""
        if not self._ui_kuruldu:
            self._ui_kur()
        self._varsayilan_verileri_yukle()

    def temizle(self) -> None:
        """Bileşeni temizler"""
        self._aktif_kategori = ""
        self._hizli_urunler.clear()
        self._butonlari_guncelle()

    def guncelle(self, veri: Dict[str, Any]) -> None:
        """Bileşeni günceller"""
        if "kategoriler" in veri:
            self._kategoriler_guncellendi(veri["kategoriler"])
        if "hizli_urunler" in veri:
            self._hizli_urunler_guncellendi(veri["hizli_urunler"])

    def klavye_kisayolu_isle(self, tus: str) -> bool:
        """Klavye kısayolunu işler"""
        # Sayısal tuşlar için hızlı ürün seçimi
        if tus.isdigit():
            pozisyon = int(tus) - 1
            if 0 <= pozisyon < len(self._butonlar):
                self._hizli_urun_butonu_tiklandi(pozisyon)
                return True
        return False

    def aktif_kategori_al(self) -> str:
        """Aktif kategori ID'sini döndürür"""
        return self._aktif_kategori

    def buton_sayisi_al(self) -> int:
        """Buton sayısını döndürür"""
        return self._buton_sayisi

    def hizli_urunler_al(self) -> List[Dict[str, Any]]:
        """Hızlı ürünler listesini döndürür"""
        return self._hizli_urunler.copy()
