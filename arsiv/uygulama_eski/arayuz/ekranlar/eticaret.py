# Version: 0.1.0
# Last Update: 2024-12-16
# Module: uygulama.arayuz.ekranlar.eticaret
# Description: E-ticaret yönetimi ekranı
# Changelog:
# - İlk sürüm oluşturuldu

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QFrame,
    QGridLayout,
    QHeaderView,
    QComboBox,
    QGroupBox,
    QSplitter,
    QTabWidget,
    QProgressBar,
    QTextEdit,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from .temel_ekran import TemelEkran
from ..servis_fabrikasi import ServisFabrikasi
from ..yardimcilar import UIYardimcilari
from ..buton_eslestirme_kaydi import kayit_ekle


class Eticaret(TemelEkran):
    """E-ticaret yönetimi ekranı"""

    def __init__(self, servis_fabrikasi: ServisFabrikasi, parent=None):
        self.magaza_combo = None
        self.siparis_tablo = None
        self.durum_label = None
        self.progress_bar = None
        self.log_text = None
        self.siparis_verileri = []
        self.aktif_magaza_id = None
        super().__init__(servis_fabrikasi, parent)

    def ekrani_hazirla(self):
        """E-ticaret ekranını hazırla"""
        # Ana başlık
        baslik = QLabel("E-ticaret Yönetimi")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        baslik.setStyleSheet("color: #2c3e50; margin: 10px;")
        self.ana_layout.addWidget(baslik)

        # Ana splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Sol panel - Mağaza seçimi ve işlemler
        sol_panel = self.sol_panel_olustur()
        splitter.addWidget(sol_panel)

        # Sağ panel - Sipariş listesi ve detaylar
        sag_panel = self.sag_panel_olustur()
        splitter.addWidget(sag_panel)

        # Splitter oranları
        splitter.setSizes([300, 700])

        self.ana_layout.addWidget(splitter)
        self.ekran_hazir = True

    def sol_panel_olustur(self):
        """Sol panel - mağaza seçimi ve işlemler"""
        panel = QFrame()
        panel.setFixedWidth(300)
        panel.setStyleSheet(
            """
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 10px;
            }
        """
        )
        layout = QVBoxLayout(panel)

        # Mağaza seçimi grubu
        magaza_grup = self.magaza_secimi_grubu_olustur()
        layout.addWidget(magaza_grup)

        # Senkronizasyon işlemleri grubu
        senkron_grup = self.senkronizasyon_grubu_olustur()
        layout.addWidget(senkron_grup)

        # Durum bilgisi grubu
        durum_grup = self.durum_bilgisi_grubu_olustur()
        layout.addWidget(durum_grup)

        layout.addStretch()

        return panel

    def magaza_secimi_grubu_olustur(self):
        """Mağaza seçimi grubu"""
        grup = QGroupBox("Mağaza Seçimi")
        grup.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """
        )
        layout = QVBoxLayout(grup)

        # Mağaza combo
        magaza_label = QLabel("Aktif Mağaza:")
        layout.addWidget(magaza_label)

        self.magaza_combo = QComboBox()
        self.magaza_combo.addItems(
            ["Trendyol", "Hepsiburada", "N11", "GittiGidiyor", "Amazon", "Çiçeksepeti", "Pazarama"]
        )
        self.magaza_combo.setStyleSheet(
            """
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 12px;
            }
        """
        )
        self.magaza_combo.currentTextChanged.connect(self.magaza_degisti)
        layout.addWidget(self.magaza_combo)

        # Mağaza durumu
        self.magaza_durum_label = QLabel("Durum: Bağlantı Bekleniyor")
        self.magaza_durum_label.setStyleSheet(
            """
            QLabel {
                padding: 5px;
                background-color: #f39c12;
                color: white;
                border-radius: 3px;
                font-weight: bold;
            }
        """
        )
        layout.addWidget(self.magaza_durum_label)

        return grup

    def senkronizasyon_grubu_olustur(self):
        """Senkronizasyon işlemleri grubu"""
        grup = QGroupBox("Senkronizasyon İşlemleri")
        grup.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """
        )
        layout = QVBoxLayout(grup)

        # Sipariş çekme
        siparis_cek_buton = QPushButton("Sipariş Çek")
        siparis_cek_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        )
        siparis_cek_buton.clicked.connect(self.siparis_cek)
        layout.addWidget(siparis_cek_buton)

        # Stok gönderme
        stok_gonder_buton = QPushButton("Stok Gönder")
        stok_gonder_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """
        )
        stok_gonder_buton.clicked.connect(self.stok_gonder)
        layout.addWidget(stok_gonder_buton)

        # Fiyat gönderme
        fiyat_gonder_buton = QPushButton("Fiyat Gönder")
        fiyat_gonder_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """
        )
        fiyat_gonder_buton.clicked.connect(self.fiyat_gonder)
        layout.addWidget(fiyat_gonder_buton)

        # Otomatik senkron
        otomatik_buton = QPushButton("Otomatik Senkron")
        otomatik_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """
        )
        otomatik_buton.clicked.connect(self.otomatik_senkron)
        layout.addWidget(otomatik_buton)

        return grup

    def durum_bilgisi_grubu_olustur(self):
        """Durum bilgisi grubu"""
        grup = QGroupBox("Durum Bilgisi")
        grup.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """
        )
        layout = QVBoxLayout(grup)

        # Durum etiketi
        self.durum_label = QLabel("Hazır")
        self.durum_label.setStyleSheet(
            """
            QLabel {
                padding: 5px;
                background-color: #27ae60;
                color: white;
                border-radius: 3px;
                font-weight: bold;
            }
        """
        )
        layout.addWidget(self.durum_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 2px;
            }
        """
        )
        layout.addWidget(self.progress_bar)

        # Son senkron bilgisi
        self.son_senkron_label = QLabel("Son Senkron: Henüz yapılmadı")
        self.son_senkron_label.setStyleSheet("font-size: 10px; color: #7f8c8d;")
        layout.addWidget(self.son_senkron_label)

        return grup

    def sag_panel_olustur(self):
        """Sağ panel - sipariş listesi ve detaylar"""
        panel = QFrame()
        layout = QVBoxLayout(panel)

        # Tab widget
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(
            """
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
        """
        )

        # Sipariş listesi sekmesi
        siparis_tab = self.siparis_listesi_sekmesi_olustur()
        tab_widget.addTab(siparis_tab, "Siparişler")

        # İşlem geçmişi sekmesi
        gecmis_tab = self.islem_gecmisi_sekmesi_olustur()
        tab_widget.addTab(gecmis_tab, "İşlem Geçmişi")

        layout.addWidget(tab_widget)

        return panel

    def siparis_listesi_sekmesi_olustur(self):
        """Sipariş listesi sekmesi"""
        widget = QFrame()
        layout = QVBoxLayout(widget)

        # Üst butonlar
        ust_butonlar = self.siparis_ust_butonlar_olustur()
        layout.addWidget(ust_butonlar)

        # Sipariş tablosu
        self.siparis_tablo = QTableWidget()
        self.siparis_tablo.setColumnCount(7)
        self.siparis_tablo.setHorizontalHeaderLabels(
            ["Sipariş No", "Mağaza", "Müşteri", "Ürün Sayısı", "Tutar", "Durum", "Tarih"]
        )

        # Tablo ayarları
        header = self.siparis_tablo.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        self.siparis_tablo.setAlternatingRowColors(True)
        self.siparis_tablo.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.siparis_tablo.setStyleSheet(
            """
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """
        )

        layout.addWidget(self.siparis_tablo)

        return widget

    def islem_gecmisi_sekmesi_olustur(self):
        """İşlem geçmişi sekmesi"""
        widget = QFrame()
        layout = QVBoxLayout(widget)

        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(
            """
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Courier New', monospace;
                font-size: 10px;
                border: 1px solid #34495e;
            }
        """
        )
        self.log_text.setPlainText("E-ticaret işlem geçmişi burada görüntülenecek...")
        layout.addWidget(self.log_text)

        # Alt butonlar
        alt_butonlar = QFrame()
        alt_layout = QHBoxLayout(alt_butonlar)

        temizle_buton = QPushButton("Geçmişi Temizle")
        temizle_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """
        )
        temizle_buton.clicked.connect(self.gecmisi_temizle)
        alt_layout.addWidget(temizle_buton)

        alt_layout.addStretch()

        disa_aktar_buton = QPushButton("Dışa Aktar")
        disa_aktar_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """
        )
        disa_aktar_buton.clicked.connect(self.gecmisi_disa_aktar)
        alt_layout.addWidget(disa_aktar_buton)

        layout.addWidget(alt_butonlar)

        return widget

    def siparis_ust_butonlar_olustur(self):
        """Sipariş üst butonları"""
        frame = QFrame()
        layout = QHBoxLayout(frame)

        # Yenile
        yenile_buton = QPushButton("YENİLE")
        yenile_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        )
        yenile_buton.clicked.connect(self.siparis_listesi_yenile)
        layout.addWidget(yenile_buton)

        # Filtrele
        filtre_combo = QComboBox()
        filtre_combo.addItems(["Tüm Siparişler", "Bekleyen", "Hazırlanıyor", "Kargoda", "Teslim Edildi"])
        filtre_combo.setStyleSheet(
            """
            QComboBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """
        )
        layout.addWidget(filtre_combo)

        layout.addStretch()

        # Durum çubuğu
        self.siparis_durum_label = QLabel("Toplam Sipariş: 0")
        self.siparis_durum_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.siparis_durum_label)

        return frame

    def magaza_degisti(self):
        """Mağaza seçimi değiştiğinde"""
        kayit_ekle("E-ticaret", "MAGAZA SEÇİMİ", "magaza_degisti", "eticaret_servisi.magaza_sec")
        try:
            secili_magaza = self.magaza_combo.currentText()
            self.aktif_magaza_id = self.magaza_combo.currentIndex() + 1

            # Mağaza durumunu güncelle
            self.magaza_durum_label.setText(f"Durum: {secili_magaza} - Bağlı")
            self.magaza_durum_label.setStyleSheet(
                """
                QLabel {
                    padding: 5px;
                    background-color: #27ae60;
                    color: white;
                    border-radius: 3px;
                    font-weight: bold;
                }
            """
            )

            # Sipariş listesini yenile
            self.siparis_listesi_yenile()

            # Log ekle
            self.log_ekle(f"Mağaza değiştirildi: {secili_magaza}")

        except Exception as e:
            self.hata_goster("Mağaza Seçim Hatası", str(e))

    def siparis_cek(self):
        """Sipariş çekme işlemi"""
        kayit_ekle("E-ticaret", "Sipariş Çek", "siparis_cek", "eticaret_servisi.siparis_cek")
        try:
            if not self.aktif_magaza_id:
                self.hata_goster("Hata", "Lütfen önce bir mağaza seçin")
                return

            # E-ticaret servisini çağır
            eticaret_servisi = self.servis_fabrikasi.eticaret_servisi()

            # İşlem başlat
            self.islem_baslat("Siparişler çekiliyor...")

            sonuc = self.servis_cagir_guvenli(eticaret_servisi.siparis_cek, self.aktif_magaza_id)

            if sonuc:
                self.log_ekle(f"Sipariş çekme işlemi tamamlandı - Mağaza ID: {self.aktif_magaza_id}")
                self.siparis_listesi_yenile()
                self.bilgi_goster_mesaj("Başarılı", "Siparişler başarıyla çekildi")

            self.islem_bitir()

        except Exception as e:
            self.islem_bitir()
            self.hata_goster("Sipariş Çekme Hatası", str(e))

    def stok_gonder(self):
        """Stok gönderme işlemi"""
        kayit_ekle("E-ticaret", "Stok Gönder", "stok_gonder", "eticaret_servisi.stok_gonder")
        try:
            if not self.aktif_magaza_id:
                self.hata_goster("Hata", "Lütfen önce bir mağaza seçin")
                return

            # E-ticaret servisini çağır
            eticaret_servisi = self.servis_fabrikasi.eticaret_servisi()

            # İşlem başlat
            self.islem_baslat("Stok bilgileri gönderiliyor...")

            sonuc = self.servis_cagir_guvenli(eticaret_servisi.stok_gonder, self.aktif_magaza_id)

            if sonuc:
                self.log_ekle(f"Stok gönderme işlemi tamamlandı - Mağaza ID: {self.aktif_magaza_id}")
                self.bilgi_goster_mesaj("Başarılı", "Stok bilgileri başarıyla gönderildi")

            self.islem_bitir()

        except Exception as e:
            self.islem_bitir()
            self.hata_goster("Stok Gönderme Hatası", str(e))

    def fiyat_gonder(self):
        """Fiyat gönderme işlemi"""
        kayit_ekle("E-ticaret", "Fiyat Gönder", "fiyat_gonder", "eticaret_servisi.fiyat_gonder")
        try:
            if not self.aktif_magaza_id:
                self.hata_goster("Hata", "Lütfen önce bir mağaza seçin")
                return

            # E-ticaret servisini çağır
            eticaret_servisi = self.servis_fabrikasi.eticaret_servisi()

            # İşlem başlat
            self.islem_baslat("Fiyat bilgileri gönderiliyor...")

            sonuc = self.servis_cagir_guvenli(eticaret_servisi.fiyat_gonder, self.aktif_magaza_id)

            if sonuc:
                self.log_ekle(f"Fiyat gönderme işlemi tamamlandı - Mağaza ID: {self.aktif_magaza_id}")
                self.bilgi_goster_mesaj("Başarılı", "Fiyat bilgileri başarıyla gönderildi")

            self.islem_bitir()

        except Exception as e:
            self.islem_bitir()
            self.hata_goster("Fiyat Gönderme Hatası", str(e))

    def otomatik_senkron(self):
        """Otomatik senkronizasyon"""
        kayit_ekle("E-ticaret", "Otomatik Senkron", "otomatik_senkron", "otomatik_senkron_dialog")
        try:
            if not self.aktif_magaza_id:
                self.hata_goster("Hata", "Lütfen önce bir mağaza seçin")
                return

            # Otomatik senkron dialog'u (stub)
            self.bilgi_goster_mesaj("Bilgi", "Otomatik senkronizasyon ayarları açılacak")

        except Exception as e:
            self.hata_goster("Otomatik Senkron Hatası", str(e))

    def siparis_listesi_yenile(self):
        """Sipariş listesini yenile"""
        kayit_ekle("E-ticaret", "YENİLE", "siparis_listesi_yenile", "eticaret_servisi.siparis_listesi")
        try:
            if not self.aktif_magaza_id:
                return

            # Stub sipariş verileri
            magaza_adi = self.magaza_combo.currentText()
            self.siparis_verileri = [
                {
                    "siparis_no": f"SP{i:06d}",
                    "magaza": magaza_adi,
                    "musteri": f"Müşteri {i}",
                    "urun_sayisi": i + 2,
                    "tutar": (i + 1) * 125.50,
                    "durum": ["Bekleyen", "Hazırlanıyor", "Kargoda"][i % 3],
                    "tarih": "2024-12-16",
                }
                for i in range(1, 11)
            ]

            self.siparis_tablosunu_guncelle()

        except Exception as e:
            self.hata_goster("Liste Yenileme Hatası", str(e))

    def siparis_tablosunu_guncelle(self):
        """Sipariş tablosunu güncelle"""
        try:
            self.siparis_tablo.setRowCount(len(self.siparis_verileri))

            for row, siparis in enumerate(self.siparis_verileri):
                self.siparis_tablo.setItem(row, 0, QTableWidgetItem(siparis["siparis_no"]))
                self.siparis_tablo.setItem(row, 1, QTableWidgetItem(siparis["magaza"]))
                self.siparis_tablo.setItem(row, 2, QTableWidgetItem(siparis["musteri"]))
                self.siparis_tablo.setItem(row, 3, QTableWidgetItem(str(siparis["urun_sayisi"])))
                self.siparis_tablo.setItem(row, 4, QTableWidgetItem(UIYardimcilari.para_formatla(siparis["tutar"])))

                # Durum - renk kodlaması
                durum_item = QTableWidgetItem(siparis["durum"])
                if siparis["durum"] == "Bekleyen":
                    durum_item.setBackground(Qt.GlobalColor.yellow)
                elif siparis["durum"] == "Hazırlanıyor":
                    durum_item.setBackground(Qt.GlobalColor.cyan)
                elif siparis["durum"] == "Kargoda":
                    durum_item.setBackground(Qt.GlobalColor.green)
                    durum_item.setForeground(Qt.GlobalColor.white)
                self.siparis_tablo.setItem(row, 5, durum_item)

                self.siparis_tablo.setItem(row, 6, QTableWidgetItem(UIYardimcilari.tarih_formatla(siparis["tarih"])))

            # Durum çubuğunu güncelle
            self.siparis_durum_label.setText(f"Toplam Sipariş: {len(self.siparis_verileri)}")

        except Exception as e:
            self.hata_goster("Tablo Güncelleme Hatası", str(e))

    def islem_baslat(self, mesaj: str):
        """İşlem başlatma"""
        self.durum_label.setText(mesaj)
        self.durum_label.setStyleSheet(
            """
            QLabel {
                padding: 5px;
                background-color: #f39c12;
                color: white;
                border-radius: 3px;
                font-weight: bold;
            }
        """
        )
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Belirsiz progress

    def islem_bitir(self):
        """İşlem bitirme"""
        self.durum_label.setText("Hazır")
        self.durum_label.setStyleSheet(
            """
            QLabel {
                padding: 5px;
                background-color: #27ae60;
                color: white;
                border-radius: 3px;
                font-weight: bold;
            }
        """
        )
        self.progress_bar.setVisible(False)

        # Son senkron zamanını güncelle
        from datetime import datetime

        simdi = datetime.now().strftime("%d.%m.%Y %H:%M")
        self.son_senkron_label.setText(f"Son Senkron: {simdi}")

    def log_ekle(self, mesaj: str):
        """Log mesajı ekle"""
        from datetime import datetime

        zaman = datetime.now().strftime("%H:%M:%S")
        log_mesaj = f"[{zaman}] {mesaj}"

        if self.log_text:
            self.log_text.append(log_mesaj)

    def gecmisi_temizle(self):
        """İşlem geçmişini temizle"""
        kayit_ekle("E-ticaret", "Geçmişi Temizle", "gecmisi_temizle", "log_temizle")
        try:
            if self.onay_iste("Onay", "İşlem geçmişi temizlenecek. Emin misiniz?"):
                self.log_text.clear()
                self.log_ekle("İşlem geçmişi temizlendi")

        except Exception as e:
            self.hata_goster("Temizleme Hatası", str(e))

    def gecmisi_disa_aktar(self):
        """İşlem geçmişini dışa aktar"""
        kayit_ekle("E-ticaret", "Dışa Aktar", "gecmisi_disa_aktar", "log_export")
        try:
            # Dışa aktarım dialog'u (stub)
            self.bilgi_goster_mesaj("Bilgi", "İşlem geçmişi dışa aktarım dialog'u açılacak")

        except Exception as e:
            self.hata_goster("Dışa Aktarım Hatası", str(e))

    def verileri_yukle(self):
        """Ekran açıldığında"""
        # İlk mağazayı seç
        if self.magaza_combo.count() > 0:
            self.magaza_combo.setCurrentIndex(0)
            self.magaza_degisti()

        self.log_ekle("E-ticaret ekranı yüklendi")

    def verileri_temizle(self):
        """Ekran kapandığında"""
        pass
