# Version: 0.1.0
# Last Update: 2024-12-18
# Module: sepet_tablosu
# Description: POS sepet tablosu bileşeni
# Changelog:
# - İlk oluşturma - Sepet tablosu widget'ı
# - setVisible() metoduna geçiş (hide/show yerine)

"""POS Sepet Tablosu Bileşeni"""

from decimal import Decimal
from typing import Any, Dict, List

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from ..handlers.pos_sinyalleri import POSSinyalleri
from .pos_bilesen_arayuzu import POSBilesenWidget


class SepetTablosu(POSBilesenWidget):
    """Sepet Tablosu Widget'ı"""

    # Sinyaller
    satir_secildi = pyqtSignal(int)
    satir_silindi = pyqtSignal(int)

    def __init__(self, sinyaller: POSSinyalleri, parent=None):
        super().__init__(parent)
        self.sinyaller = sinyaller
        self._sepet_verileri: List[Dict[str, Any]] = []
        self._secili_satir = -1
        self._ui_kuruldu = False
        self._ui_kur()
        self._sinyalleri_bagla()

    def _ui_kur(self):
        """UI bileşenlerini kurar"""
        if self._ui_kuruldu:
            return

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Başlık
        baslik = QLabel("SEPET")
        baslik.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(baslik)

        # Tablo
        self.tablo = QTableWidget()
        self.tablo.setColumnCount(6)
        self.tablo.setHorizontalHeaderLabels(["Barkod", "Ürün", "Adet", "Fiyat", "Tutar", "Sil"])

        # Tablo ayarları
        header = self.tablo.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        self.tablo.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tablo.setAlternatingRowColors(True)
        self.tablo.itemSelectionChanged.connect(self._satir_secim_degisti)

        layout.addWidget(self.tablo)

        # Boş sepet mesajı
        self.bos_sepet_label = QLabel("Sepet boş")
        self.bos_sepet_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bos_sepet_label.setStyleSheet(
            """
            QLabel {
                color: #7f8c8d;
                font-size: 14px;
                font-style: italic;
                padding: 20px;
            }
        """
        )
        self.bos_sepet_label.hide()
        layout.addWidget(self.bos_sepet_label)

        self._ui_kuruldu = True

    def _sinyalleri_bagla(self):
        """Sinyalleri bağlar"""
        self.sinyaller.sepet_guncellendi.connect(self._sepet_guncellendi)
        self.sinyaller.sepet_temizlendi.connect(self._sepet_temizlendi)
        self.sinyaller.urun_eklendi.connect(self._urun_eklendi)

    def _satir_secim_degisti(self):
        """Satır seçimi değiştiğinde çağrılır"""
        secili_satirlar = self.tablo.selectionModel().selectedRows()
        if secili_satirlar:
            self._secili_satir = secili_satirlar[0].row()
            self.satir_secildi.emit(self._secili_satir)
        else:
            self._secili_satir = -1

    def _sil_butonu_tiklandi(self, satir_index: int):
        """Sil butonu tıklandığında çağrılır"""
        if 0 <= satir_index < len(self._sepet_verileri):
            self.satir_silindi.emit(satir_index)
            self.sinyaller.urun_cikarildi.emit(satir_index)

    def _sepet_guncellendi(self, sepet_verileri: List[Dict[str, Any]]):
        """Sepet güncellendiğinde çağrılır"""
        self._sepet_verileri = sepet_verileri
        self._tabloyu_guncelle()

    def _sepet_temizlendi(self):
        """Sepet temizlendiğinde çağrılır"""
        self._sepet_verileri = []
        self._tabloyu_guncelle()

    def _urun_eklendi(self, urun_verisi: Dict[str, Any]):
        """Ürün eklendiğinde çağrılır"""
        # Mevcut ürün var mı kontrol et
        for i, veri in enumerate(self._sepet_verileri):
            if veri.get("barkod") == urun_verisi.get("barkod"):
                # Mevcut ürünün adedini artır
                self._sepet_verileri[i]["adet"] += urun_verisi.get("adet", 1)
                self._sepet_verileri[i]["toplam_fiyat"] = (
                    Decimal(str(self._sepet_verileri[i]["birim_fiyat"])) * self._sepet_verileri[i]["adet"]
                )
                self._tabloyu_guncelle()
                return

        # Yeni ürün için toplam fiyat hesapla
        birim_fiyat = Decimal(str(urun_verisi.get("birim_fiyat", 0)))
        adet = urun_verisi.get("adet", 1)
        urun_verisi["toplam_fiyat"] = birim_fiyat * adet

        # Yeni ürün ekle
        self._sepet_verileri.append(urun_verisi)
        self._tabloyu_guncelle()

    def _tabloyu_guncelle(self):
        """Tabloyu günceller"""
        if not self._sepet_verileri:
            self.tablo.setVisible(False)
            self.bos_sepet_label.setVisible(True)
            return

        self.bos_sepet_label.setVisible(False)
        self.tablo.setVisible(True)

        self.tablo.setRowCount(len(self._sepet_verileri))

        for satir, veri in enumerate(self._sepet_verileri):
            # Barkod
            barkod_item = QTableWidgetItem(str(veri.get("barkod", "")))
            barkod_item.setFlags(barkod_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tablo.setItem(satir, 0, barkod_item)

            # Ürün adı
            urun_item = QTableWidgetItem(str(veri.get("urun_adi", "")))
            urun_item.setFlags(urun_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tablo.setItem(satir, 1, urun_item)

            # Adet
            adet_item = QTableWidgetItem(str(veri.get("adet", 0)))
            self.tablo.setItem(satir, 2, adet_item)

            # Birim fiyat
            birim_fiyat = veri.get("birim_fiyat", 0)
            fiyat_item = QTableWidgetItem(f"{birim_fiyat:.2f} ₺")
            fiyat_item.setFlags(fiyat_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tablo.setItem(satir, 3, fiyat_item)

            # Toplam tutar
            toplam_fiyat = veri.get("toplam_fiyat", 0)
            tutar_item = QTableWidgetItem(f"{toplam_fiyat:.2f} ₺")
            tutar_item.setFlags(tutar_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.tablo.setItem(satir, 4, tutar_item)

            # Sil butonu
            sil_btn = QPushButton("Sil")
            sil_btn.setMaximumWidth(50)
            sil_btn.clicked.connect(lambda checked, idx=satir: self._sil_butonu_tiklandi(idx))
            self.tablo.setCellWidget(satir, 5, sil_btn)

    def baslat(self) -> None:
        """Bileşeni başlatır"""
        super().baslat()
        self._sepet_verileri = []
        self._secili_satir = -1
        self._tabloyu_guncelle()

    def temizle(self) -> None:
        """Bileşeni temizler"""
        super().temizle()
        self._sepet_verileri = []
        self._secili_satir = -1
        self._tabloyu_guncelle()

    def guncelle(self, veri: Dict[str, Any]) -> None:
        """Bileşeni günceller"""
        if "sepet_verileri" in veri:
            self._sepet_verileri = veri["sepet_verileri"]
            self._tabloyu_guncelle()

    def klavye_kisayolu_isle(self, tus: str) -> bool:
        """Klavye kısayolunu işler"""
        if tus == "Delete" and self._secili_satir >= 0:
            self._sil_butonu_tiklandi(self._secili_satir)
            return True
        return False

    def secili_satir_getir(self) -> int:
        """Seçili satır index'ini döndürür"""
        return self._secili_satir

    def sepet_verilerini_getir(self) -> List[Dict[str, Any]]:
        """Sepet verilerini döndürür"""
        return self._sepet_verileri.copy()

    def toplam_tutar_hesapla(self) -> Decimal:
        """Sepet toplam tutarını hesaplar"""
        toplam = Decimal("0.00")
        for veri in self._sepet_verileri:
            toplam += Decimal(str(veri.get("toplam_fiyat", 0)))
        return toplam
