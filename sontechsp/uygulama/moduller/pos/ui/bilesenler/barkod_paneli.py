# Version: 0.1.0
# Last Update: 2024-12-19
# Module: barkod_paneli
# Description: POS barkod giriş paneli bileşeni
# Changelog:
# - İlk oluşturma - Barkod giriş alanı ve EKLE butonu
# - Decimal import düzenlemesi

"""
POS Barkod Paneli Bileşeni

Barkod okuma ve ürün ekleme işlemlerini yöneten UI bileşeni.
Barkod doğrulama ve ürün ekleme handler'larını içerir.

Sorumluluklar:
- Barkod giriş alanı yönetimi
- EKLE butonu işlemleri
- Enter tuşu desteği
- Barkod doğrulama
- Ürün ekleme sinyali gönderimi
"""

from decimal import Decimal
from typing import Any, Dict, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

from .pos_bilesen_arayuzu import POSBilesenWidget
from ..handlers.pos_sinyalleri import POSSinyalleri


class BarkodPaneli(POSBilesenWidget):
    """
    Barkod Paneli Bileşeni

    Barkod giriş alanı ve EKLE butonunu içeren panel.
    Barkod doğrulama ve ürün ekleme işlemlerini yönetir.
    """

    def __init__(self, sinyaller: POSSinyalleri, stok_service=None, parent=None):
        """
        Barkod paneli constructor

        Args:
            sinyaller: POS sinyal sistemi
            stok_service: Stok servisi (opsiyonel, test için)
            parent: Parent widget
        """
        super().__init__(parent)
        self._sinyaller = sinyaller
        self._stok_service = stok_service

        # UI bileşenleri
        self._barkod_alani: Optional[QLineEdit] = None
        self._ekle_butonu: Optional[QPushButton] = None

        self._ui_olustur()
        self._sinyalleri_bagla()

    def _ui_olustur(self):
        """UI bileşenlerini oluşturur"""
        # Ana layout
        ana_layout = QVBoxLayout(self)
        ana_layout.setContentsMargins(5, 5, 5, 5)
        ana_layout.setSpacing(5)

        # Başlık
        baslik = QLabel("Barkod Okuma")
        baslik.setStyleSheet(
            """
            QLabel {
                font-weight: bold;
                font-size: 12px;
                color: #2c3e50;
                padding: 2px;
            }
        """
        )
        ana_layout.addWidget(baslik)

        # Barkod giriş alanı
        self._barkod_alani = QLineEdit()
        self._barkod_alani.setPlaceholderText("Barkod okutun veya yazın...")
        self._barkod_alani.setStyleSheet(
            """
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """
        )
        ana_layout.addWidget(self._barkod_alani)

        # EKLE butonu
        self._ekle_butonu = QPushButton("EKLE")
        self._ekle_butonu.setStyleSheet(
            """
            QPushButton {
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """
        )
        ana_layout.addWidget(self._ekle_butonu)

        # Stretch ekle
        ana_layout.addStretch()

    def _sinyalleri_bagla(self):
        """Sinyal/slot bağlantılarını kurar"""
        # Enter tuşu ile ekleme
        self._barkod_alani.returnPressed.connect(self._barkod_ekle)

        # EKLE butonu ile ekleme
        self._ekle_butonu.clicked.connect(self._barkod_ekle)

    def _barkod_ekle(self):
        """Barkod ekleme işlemini gerçekleştirir"""
        barkod = self._barkod_alani.text().strip()

        # Boş barkod kontrolü
        if not barkod:
            self._sinyaller.hata_olustu.emit("Barkod boş olamaz")
            return

        # Barkod doğrulama
        if not self._barkod_dogrula(barkod):
            self._sinyaller.hata_olustu.emit(f"Geçersiz barkod: {barkod}")
            return

        # Ürün bilgisi al
        urun_bilgisi = self._urun_bilgisi_getir(barkod)
        if not urun_bilgisi:
            self._sinyaller.hata_olustu.emit(f"Ürün bulunamadı: {barkod}")
            return

        # Ürün verisi oluştur
        urun_verisi = {
            "barkod": barkod,
            "urun_adi": urun_bilgisi["urun_adi"],
            "adet": 1,
            "birim_fiyat": Decimal(str(urun_bilgisi["satis_fiyati"])),
            "urun_id": urun_bilgisi.get("id", 0),
        }

        # Ürün eklendi sinyali gönder
        self._sinyaller.urun_eklendi.emit(urun_verisi)

        # Barkod alanını temizle ve odakla
        self._barkod_alani.clear()
        self._barkod_alani.setFocus()

    def _barkod_dogrula(self, barkod: str) -> bool:
        """
        Barkod doğrulama yapar

        Args:
            barkod: Doğrulanacak barkod

        Returns:
            bool: Barkod geçerli mi
        """
        # Temel barkod doğrulama kuralları
        if len(barkod) < 4:
            return False

        # Sadece özel karakterler içeriyorsa geçersiz
        if not any(c.isalnum() for c in barkod):
            return False

        return True

    def _urun_bilgisi_getir(self, barkod: str) -> Optional[Dict[str, Any]]:
        """
        Ürün bilgisini getirir

        Args:
            barkod: Ürün barkodu

        Returns:
            Optional[Dict]: Ürün bilgileri veya None
        """
        if self._stok_service:
            try:
                return self._stok_service.urun_bilgisi_getir(barkod)
            except Exception as e:
                self._sinyaller.hata_olustu.emit(f"Stok servis hatası: {str(e)}")
                return None
        else:
            # Mock veri (test için)
            return {
                "id": hash(barkod) % 1000 + 1,
                "urun_adi": f"Test Ürün {barkod[:5]}",
                "satis_fiyati": 10.50,
                "aktif": True,
            }

    # POSBilesenArayuzu metodları
    def baslat(self) -> None:
        """Bileşeni başlatır"""
        super().baslat()
        self._barkod_alani.setFocus()
        self._barkod_alani.clear()

    def temizle(self) -> None:
        """Bileşeni temizler"""
        super().temizle()
        self._barkod_alani.clear()
        self._barkod_alani.setFocus()

    def guncelle(self, veri: Dict[str, Any]) -> None:
        """Bileşeni günceller"""
        super().guncelle(veri)
        # Şimdilik güncelleme işlemi yok

    def klavye_kisayolu_isle(self, tus: str) -> bool:
        """
        Klavye kısayolunu işler

        Args:
            tus: Basılan tuş kombinasyonu

        Returns:
            bool: Kısayol işlendiyse True
        """
        if tus == "F2":
            self.odak_al()
            return True

        return False

    def odak_al(self) -> None:
        """Bileşene odak verir"""
        super().odak_al()
        self._barkod_alani.setFocus()

    def veri_dogrula(self, veri: Dict[str, Any]) -> bool:
        """
        Veri doğrulaması yapar

        Args:
            veri: Doğrulanacak veri

        Returns:
            bool: Veri geçerli mi
        """
        if "barkod" in veri:
            return self._barkod_dogrula(veri["barkod"])

        return True
