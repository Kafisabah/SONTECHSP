# Version: 0.1.0
# Last Update: 2024-12-18
# Module: eslestirme_dialog
# Description: POS buton eşleştirme tablosu dialog widget'ı
# Changelog:
# - İlk oluşturma - Eşleştirme tablosu dialog bileşeni

"""
Eşleştirme Dialog Bileşeni

POS buton eşleştirmelerini gösteren dialog penceresi.
Buton-handler-servis ilişkilerini tablo formatında görüntüler.

Özellikler:
- Otomatik güncelleme
- CSV dışa aktarım
- Filtreleme ve arama
- Gerçek zamanlı veri gösterimi
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional

from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox,
    QFileDialog,
    QHeaderView,
)

from sontechsp.uygulama.arayuz.buton_eslestirme_kaydi import kayitlari_listele, csv_dosyasina_kaydet, kayit_sayisi


class EslestirmeDialog(QDialog):
    """
    Eşleştirme Tablosu Dialog

    POS buton eşleştirmelerini görüntüleyen ve yöneten dialog penceresi.
    """

    # Sinyaller
    dialog_kapandi = pyqtSignal()
    csv_disari_aktarildi = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._guncelleme_timer = None
        self._arama_metni = ""
        self._setup_ui()
        self._setup_timer()
        self._baglantilari_kur()

    def _setup_ui(self):
        """UI bileşenlerini kurar"""
        self.setWindowTitle("POS Buton Eşleştirme Tablosu")
        self.setModal(False)
        self.resize(800, 600)

        # Ana layout
        layout = QVBoxLayout(self)

        # Üst panel - bilgi ve kontroller
        ust_panel = self._ust_panel_olustur()
        layout.addLayout(ust_panel)

        # Tablo
        self.tablo = self._tablo_olustur()
        layout.addWidget(self.tablo)

        # Alt panel - butonlar
        alt_panel = self._alt_panel_olustur()
        layout.addLayout(alt_panel)

    def _ust_panel_olustur(self) -> QHBoxLayout:
        """Üst kontrol panelini oluşturur"""
        layout = QHBoxLayout()

        # Kayıt sayısı etiketi
        self.kayit_sayisi_etiketi = QLabel("Kayıt: 0")
        layout.addWidget(self.kayit_sayisi_etiketi)

        # Arama alanı
        layout.addWidget(QLabel("Ara:"))
        self.arama_alani = QLineEdit()
        self.arama_alani.setPlaceholderText("Ekran, buton veya handler adı...")
        layout.addWidget(self.arama_alani)

        # Yenile butonu
        self.yenile_butonu = QPushButton("Yenile")
        layout.addWidget(self.yenile_butonu)

        return layout

    def _tablo_olustur(self) -> QTableWidget:
        """Ana tabloyu oluşturur"""
        tablo = QTableWidget()

        # Kolonlar
        kolonlar = ["Ekran", "Buton", "Handler", "Servis Metodu", "Zaman", "Çağrılma"]
        tablo.setColumnCount(len(kolonlar))
        tablo.setHorizontalHeaderLabels(kolonlar)

        # Tablo ayarları
        header = tablo.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tablo.setAlternatingRowColors(True)
        tablo.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tablo.setSortingEnabled(True)

        return tablo

    def _alt_panel_olustur(self) -> QHBoxLayout:
        """Alt buton panelini oluşturur"""
        layout = QHBoxLayout()

        # CSV dışa aktarım butonu
        self.csv_buton = QPushButton("CSV Dışa Aktar")
        layout.addWidget(self.csv_buton)

        layout.addStretch()

        # Kapat butonu
        self.kapat_butonu = QPushButton("Kapat")
        layout.addWidget(self.kapat_butonu)

        return layout

    def _setup_timer(self):
        """Otomatik güncelleme timer'ını kurar"""
        self._guncelleme_timer = QTimer()
        self._guncelleme_timer.timeout.connect(self._tabloyu_guncelle)
        self._guncelleme_timer.start(2000)  # 2 saniyede bir güncelle

    def _baglantilari_kur(self):
        """Sinyal-slot bağlantılarını kurar"""
        self.yenile_butonu.clicked.connect(self._tabloyu_guncelle)
        self.csv_buton.clicked.connect(self._csv_disari_aktar)
        self.kapat_butonu.clicked.connect(self.close)
        self.arama_alani.textChanged.connect(self._arama_degisti)

    def _tabloyu_guncelle(self):
        """Tabloyu güncel verilerle doldurur"""
        kayitlar = kayitlari_listele()

        # Kayıt sayısını güncelle
        self.kayit_sayisi_etiketi.setText(f"Kayıt: {len(kayitlar)}")

        # Arama filtresi uygula
        if self._arama_metni:
            kayitlar = self._kayitlari_filtrele(kayitlar)

        # Tabloyu temizle ve doldur
        self.tablo.setRowCount(len(kayitlar))

        for satir, kayit in enumerate(kayitlar):
            self._satir_doldur(satir, kayit)

    def _kayitlari_filtrele(self, kayitlar: list) -> list:
        """Kayıtları arama metnine göre filtreler"""
        if not self._arama_metni:
            return kayitlar

        arama = self._arama_metni.lower()
        filtrelenmis = []

        for kayit in kayitlar:
            if (
                arama in kayit.get("ekran_adi", "").lower()
                or arama in kayit.get("buton_adi", "").lower()
                or arama in kayit.get("handler_adi", "").lower()
                or arama in kayit.get("servis_metodu", "").lower()
            ):
                filtrelenmis.append(kayit)

        return filtrelenmis

    def _satir_doldur(self, satir: int, kayit: Dict[str, Any]):
        """Tablo satırını kayıt verisiyle doldurur"""
        # Ekran adı
        self.tablo.setItem(satir, 0, QTableWidgetItem(kayit.get("ekran_adi", "")))

        # Buton adı
        self.tablo.setItem(satir, 1, QTableWidgetItem(kayit.get("buton_adi", "")))

        # Handler adı
        self.tablo.setItem(satir, 2, QTableWidgetItem(kayit.get("handler_adi", "")))

        # Servis metodu
        servis = kayit.get("servis_metodu") or "Servis hazır değil"
        self.tablo.setItem(satir, 3, QTableWidgetItem(servis))

        # Zaman
        zaman_str = kayit.get("kayit_zamani", "")
        if zaman_str:
            try:
                zaman = datetime.fromisoformat(zaman_str.replace("Z", "+00:00"))
                zaman_gorunum = zaman.strftime("%H:%M:%S")
            except:
                zaman_gorunum = zaman_str
        else:
            zaman_gorunum = ""
        self.tablo.setItem(satir, 4, QTableWidgetItem(zaman_gorunum))

        # Çağrılma sayısı
        cagrilma = str(kayit.get("cagrilma_sayisi", 0))
        self.tablo.setItem(satir, 5, QTableWidgetItem(cagrilma))

    def _arama_degisti(self, metin: str):
        """Arama metni değiştiğinde çağrılır"""
        self._arama_metni = metin.strip()
        self._tabloyu_guncelle()

    def _csv_disari_aktar(self):
        """CSV dışa aktarım işlemini gerçekleştirir"""
        try:
            # Dosya seçim dialogu
            varsayilan_ad = f"pos_eslestirme_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            dosya_yolu, _ = QFileDialog.getSaveFileName(
                self, "CSV Dosyası Kaydet", varsayilan_ad, "CSV Dosyaları (*.csv);;Tüm Dosyalar (*)"
            )

            if not dosya_yolu:
                return

            # CSV'ye kaydet
            basarili = csv_dosyasina_kaydet(dosya_yolu)

            if basarili:
                QMessageBox.information(self, "Başarılı", f"Eşleştirme tablosu başarıyla kaydedildi:\n{dosya_yolu}")
                self.csv_disari_aktarildi.emit(dosya_yolu)
            else:
                QMessageBox.warning(self, "Hata", "CSV dosyası kaydedilemedi. Dosya yolunu kontrol edin.")

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"CSV dışa aktarım hatası:\n{str(e)}")

    def showEvent(self, event):
        """Dialog gösterildiğinde çağrılır"""
        super().showEvent(event)
        self._tabloyu_guncelle()

    def closeEvent(self, event):
        """Dialog kapatıldığında çağrılır"""
        if self._guncelleme_timer:
            self._guncelleme_timer.stop()
        self.dialog_kapandi.emit()
        super().closeEvent(event)

    def guncelleme_durdur(self):
        """Otomatik güncellemeyi durdurur"""
        if self._guncelleme_timer:
            self._guncelleme_timer.stop()

    def guncelleme_baslat(self):
        """Otomatik güncellemeyi başlatır"""
        if self._guncelleme_timer:
            self._guncelleme_timer.start(2000)
