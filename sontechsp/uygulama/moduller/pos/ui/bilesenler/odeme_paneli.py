# Version: 0.1.0
# Last Update: 2024-12-18
# Module: odeme_paneli
# Description: POS ödeme paneli bileşeni
# Changelog:
# - İlk oluşturma - Ödeme paneli widget'ı

"""
POS Ödeme Paneli Bileşeni

Ödeme bilgilerini ve ödeme türü butonlarını gösteren widget.
AraToplam, İndirim, GenelToplam göstergeleri ve ödeme türü seçimi.

Sorumluluklar:
- Ödeme tutarlarını gösterme
- Ödeme türü butonlarını gösterme
- Ödeme türü seçimini yönetme
- Ödeme sinyallerini gönderme
"""

from typing import Dict, Any, Optional
from decimal import Decimal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox, QGridLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from .pos_bilesen_arayuzu import POSBilesenWidget
from ..handlers.pos_sinyalleri import POSSinyalleri


class OdemePaneli(POSBilesenWidget):
    """
    Ödeme Paneli Widget'ı

    Ödeme bilgilerini ve ödeme türü butonlarını gösterir.
    """

    # Sinyaller
    odeme_turu_secildi = pyqtSignal(str, object)  # Ödeme türü, tutar

    def __init__(self, sinyaller: POSSinyalleri, parent=None):
        super().__init__(parent)
        self.sinyaller = sinyaller
        self._ara_toplam = Decimal("0.00")
        self._indirim = Decimal("0.00")
        self._genel_toplam = Decimal("0.00")
        self._ui_kuruldu = False
        self._ui_kur()
        self._sinyalleri_bagla()

    def _ui_kur(self):
        """UI bileşenlerini kurar"""
        if self._ui_kuruldu:
            return

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Başlık
        baslik = QLabel("ÖDEME")
        baslik.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(baslik)

        # Tutar göstergeleri
        tutar_group = QGroupBox("Tutar Bilgileri")
        tutar_layout = QGridLayout()
        tutar_layout.setSpacing(10)

        # AraToplam
        ara_toplam_label = QLabel("Ara Toplam:")
        ara_toplam_label.setFont(QFont("Arial", 9))
        self.ara_toplam_deger = QLabel("0.00 ₺")
        self.ara_toplam_deger.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.ara_toplam_deger.setAlignment(Qt.AlignmentFlag.AlignRight)
        tutar_layout.addWidget(ara_toplam_label, 0, 0)
        tutar_layout.addWidget(self.ara_toplam_deger, 0, 1)

        # İndirim
        indirim_label = QLabel("İndirim:")
        indirim_label.setFont(QFont("Arial", 9))
        self.indirim_deger = QLabel("0.00 ₺")
        self.indirim_deger.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.indirim_deger.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.indirim_deger.setStyleSheet("color: #e74c3c;")
        tutar_layout.addWidget(indirim_label, 1, 0)
        tutar_layout.addWidget(self.indirim_deger, 1, 1)

        # GenelToplam
        genel_toplam_label = QLabel("Genel Toplam:")
        genel_toplam_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.genel_toplam_deger = QLabel("0.00 ₺")
        self.genel_toplam_deger.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.genel_toplam_deger.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.genel_toplam_deger.setStyleSheet("color: #27ae60;")
        tutar_layout.addWidget(genel_toplam_label, 2, 0)
        tutar_layout.addWidget(self.genel_toplam_deger, 2, 1)

        tutar_group.setLayout(tutar_layout)
        layout.addWidget(tutar_group)

        # Ödeme türü butonları
        odeme_group = QGroupBox("Ödeme Türü")
        odeme_layout = QGridLayout()
        odeme_layout.setSpacing(10)

        # NAKİT butonu
        self.nakit_btn = QPushButton("NAKİT\n(F4)")
        self.nakit_btn.setMinimumHeight(60)
        self.nakit_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """
        )
        self.nakit_btn.clicked.connect(lambda: self._odeme_turu_sec("nakit"))
        odeme_layout.addWidget(self.nakit_btn, 0, 0)

        # KART butonu
        self.kart_btn = QPushButton("KART\n(F5)")
        self.kart_btn.setMinimumHeight(60)
        self.kart_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        )
        self.kart_btn.clicked.connect(lambda: self._odeme_turu_sec("kart"))
        odeme_layout.addWidget(self.kart_btn, 0, 1)

        # PARÇALI butonu
        self.parcali_btn = QPushButton("PARÇALI")
        self.parcali_btn.setMinimumHeight(60)
        self.parcali_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #f39c12;
                color: white;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """
        )
        self.parcali_btn.clicked.connect(lambda: self._odeme_turu_sec("parcali"))
        odeme_layout.addWidget(self.parcali_btn, 1, 0)

        # AÇIK HESAP butonu
        self.acik_hesap_btn = QPushButton("AÇIK HESAP")
        self.acik_hesap_btn.setMinimumHeight(60)
        self.acik_hesap_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #9b59b6;
                color: white;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """
        )
        self.acik_hesap_btn.clicked.connect(lambda: self._odeme_turu_sec("acik_hesap"))
        odeme_layout.addWidget(self.acik_hesap_btn, 1, 1)

        odeme_group.setLayout(odeme_layout)
        layout.addWidget(odeme_group)

        layout.addStretch()
        self._ui_kuruldu = True

    def _sinyalleri_bagla(self):
        """Sinyalleri bağlar"""
        self.sinyaller.sepet_guncellendi.connect(self._sepet_guncellendi)

    def _odeme_turu_sec(self, odeme_turu: str):
        """Ödeme türü seçildiğinde çağrılır"""
        if self._genel_toplam <= 0:
            self.sinyaller.uyari_mesaji.emit("Sepet boş, ödeme yapılamaz")
            return

        # Ödeme sinyalini gönder
        self.odeme_turu_secildi.emit(odeme_turu, self._genel_toplam)
        self.sinyaller.odeme_baslatildi.emit(odeme_turu, self._genel_toplam)

    def _sepet_guncellendi(self, sepet_verileri: list):
        """Sepet güncellendiğinde tutarları hesaplar"""
        ara_toplam = Decimal("0.00")
        for veri in sepet_verileri:
            ara_toplam += Decimal(str(veri.get("toplam_fiyat", 0)))

        self._ara_toplam = ara_toplam
        self._genel_toplam = self._ara_toplam - self._indirim
        self._tutarlari_guncelle()

    def _tutarlari_guncelle(self):
        """Tutar göstergelerini günceller"""
        self.ara_toplam_deger.setText(f"{self._ara_toplam:.2f} ₺")
        self.indirim_deger.setText(f"{self._indirim:.2f} ₺")
        self.genel_toplam_deger.setText(f"{self._genel_toplam:.2f} ₺")

    # POSBilesenArayuzu implementasyonu
    def baslat(self) -> None:
        """Bileşeni başlatır"""
        super().baslat()
        self._ara_toplam = Decimal("0.00")
        self._indirim = Decimal("0.00")
        self._genel_toplam = Decimal("0.00")
        self._tutarlari_guncelle()

    def temizle(self) -> None:
        """Bileşeni temizler"""
        super().temizle()
        self._ara_toplam = Decimal("0.00")
        self._indirim = Decimal("0.00")
        self._genel_toplam = Decimal("0.00")
        self._tutarlari_guncelle()

    def guncelle(self, veri: Dict[str, Any]) -> None:
        """Bileşeni günceller"""
        if "ara_toplam" in veri:
            self._ara_toplam = Decimal(str(veri["ara_toplam"]))

        if "indirim" in veri:
            self._indirim = Decimal(str(veri["indirim"]))

        self._genel_toplam = self._ara_toplam - self._indirim
        self._tutarlari_guncelle()

    def klavye_kisayolu_isle(self, tus: str) -> bool:
        """Klavye kısayolunu işler"""
        if tus == "F4":
            self._odeme_turu_sec("nakit")
            return True
        elif tus == "F5":
            self._odeme_turu_sec("kart")
            return True
        return False

    def indirim_uygula(self, indirim_tutari: Decimal):
        """İndirim uygular"""
        if indirim_tutari < 0:
            return

        if indirim_tutari > self._ara_toplam:
            self.sinyaller.uyari_mesaji.emit("İndirim tutarı ara toplamdan büyük olamaz")
            return

        self._indirim = indirim_tutari
        self._genel_toplam = self._ara_toplam - self._indirim
        self._tutarlari_guncelle()

    def genel_toplam_getir(self) -> Decimal:
        """Genel toplamı döndürür"""
        return self._genel_toplam
