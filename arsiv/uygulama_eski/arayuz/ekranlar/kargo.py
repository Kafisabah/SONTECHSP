# Version: 0.1.0
# Last Update: 2024-12-16
# Module: uygulama.arayuz.ekranlar.kargo
# Description: Kargo yönetimi ekranı
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
    QLineEdit,
    QDateEdit,
    QCheckBox,
    QSpinBox,
)
from PyQt6.QtCore import Qt, QTimer, QDate
from PyQt6.QtGui import QFont, QPixmap, QIcon
from .temel_ekran import TemelEkran
from ..servis_fabrikasi import ServisFabrikasi
from ..yardimcilar import UIYardimcilari
from ..buton_eslestirme_kaydi import kayit_ekle


class Kargo(TemelEkran):
    """Kargo yönetimi ekranı"""

    def __init__(self, servis_fabrikasi: ServisFabrikasi, parent=None):
        self.kargo_tablo = None
        self.durum_label = None
        self.progress_bar = None
        self.log_text = None
        self.kargo_verileri = []
        self.aktif_tasiyici = None
        super().__init__(servis_fabrikasi, parent)

    def ekrani_hazirla(self):
        """Kargo ekranını hazırla"""
        # Ana başlık
        baslik = QLabel("Kargo Yönetimi")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        baslik.setStyleSheet("color: #2c3e50; margin: 10px;")
        self.ana_layout.addWidget(baslik)

        # Ana splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Sol panel - Taşıyıcı seçimi ve işlemler
        sol_panel = self.sol_panel_olustur()
        splitter.addWidget(sol_panel)

        # Sağ panel - Kargo listesi ve detaylar
        sag_panel = self.sag_panel_olustur()
        splitter.addWidget(sag_panel)

        # Splitter oranları
        splitter.setSizes([300, 700])

        self.ana_layout.addWidget(splitter)
        self.ekran_hazir = True

    def sol_panel_olustur(self):
        """Sol panel - taşıyıcı seçimi ve işlemler"""
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

        # Taşıyıcı seçimi grubu
        tasiyici_grup = self.tasiyici_secimi_grubu_olustur()
        layout.addWidget(tasiyici_grup)

        # Kargo işlemleri grubu
        islemler_grup = self.kargo_islemleri_grubu_olustur()
        layout.addWidget(islemler_grup)

        # Durum bilgisi grubu
        durum_grup = self.durum_bilgisi_grubu_olustur()
        layout.addWidget(durum_grup)

        layout.addStretch()

        return panel

    def tasiyici_secimi_grubu_olustur(self):
        """Taşıyıcı seçimi grubu"""
        grup = QGroupBox("Taşıyıcı Seçimi")
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

        # Taşıyıcı combo
        tasiyici_label = QLabel("Aktif Taşıyıcı:")
        layout.addWidget(tasiyici_label)

        self.tasiyici_combo = QComboBox()
        self.tasiyici_combo.addItems(
            ["Yurtiçi Kargo", "MNG Kargo", "Aras Kargo", "PTT Kargo", "UPS", "DHL", "FedEx", "Sürat Kargo"]
        )
        self.tasiyici_combo.setStyleSheet(
            """
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 12px;
            }
        """
        )
        self.tasiyici_combo.currentTextChanged.connect(self.tasiyici_degisti)
        layout.addWidget(self.tasiyici_combo)

        # Taşıyıcı durumu
        self.tasiyici_durum_label = QLabel("Durum: Bağlantı Bekleniyor")
        self.tasiyici_durum_label.setStyleSheet(
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
        layout.addWidget(self.tasiyici_durum_label)

        # API bilgileri
        api_bilgi_frame = QFrame()
        api_layout = QVBoxLayout(api_bilgi_frame)

        self.api_durum_label = QLabel("API: Bağlı")
        self.api_durum_label.setStyleSheet("font-size: 10px; color: #27ae60; font-weight: bold;")
        api_layout.addWidget(self.api_durum_label)

        self.son_senkron_label = QLabel("Son Senkron: Henüz yapılmadı")
        self.son_senkron_label.setStyleSheet("font-size: 10px; color: #7f8c8d;")
        api_layout.addWidget(self.son_senkron_label)

        layout.addWidget(api_bilgi_frame)

        return grup

    def kargo_islemleri_grubu_olustur(self):
        """Kargo işlemleri grubu"""
        grup = QGroupBox("Kargo İşlemleri")
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

        # Etiket oluştur
        etiket_olustur_buton = QPushButton("Etiket Oluştur")
        etiket_olustur_buton.setStyleSheet(
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
        etiket_olustur_buton.clicked.connect(self.etiket_olustur)
        layout.addWidget(etiket_olustur_buton)

        # Durum sorgula
        durum_sorgula_buton = QPushButton("Durum Sorgula")
        durum_sorgula_buton.setStyleSheet(
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
        durum_sorgula_buton.clicked.connect(self.durum_sorgula)
        layout.addWidget(durum_sorgula_buton)

        # Toplu etiket
        toplu_etiket_buton = QPushButton("Toplu Etiket")
        toplu_etiket_buton.setStyleSheet(
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
        toplu_etiket_buton.clicked.connect(self.toplu_etiket)
        layout.addWidget(toplu_etiket_buton)

        # Kargo iptal
        iptal_buton = QPushButton("Kargo İptal")
        iptal_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """
        )
        iptal_buton.clicked.connect(self.kargo_iptal)
        layout.addWidget(iptal_buton)

        # Manifest oluştur
        manifest_buton = QPushButton("Manifest Oluştur")
        manifest_buton.setStyleSheet(
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
        manifest_buton.clicked.connect(self.manifest_olustur)
        layout.addWidget(manifest_buton)

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

        # İstatistikler
        self.istatistik_frame = QFrame()
        istatistik_layout = QVBoxLayout(self.istatistik_frame)

        self.bekleyen_kargo_label = QLabel("Bekleyen: 0")
        self.bekleyen_kargo_label.setStyleSheet("font-size: 11px; color: #f39c12; font-weight: bold;")
        istatistik_layout.addWidget(self.bekleyen_kargo_label)

        self.kargoda_label = QLabel("Kargoda: 0")
        self.kargoda_label.setStyleSheet("font-size: 11px; color: #3498db; font-weight: bold;")
        istatistik_layout.addWidget(self.kargoda_label)

        self.teslim_edildi_label = QLabel("Teslim Edildi: 0")
        self.teslim_edildi_label.setStyleSheet("font-size: 11px; color: #27ae60; font-weight: bold;")
        istatistik_layout.addWidget(self.teslim_edildi_label)

        layout.addWidget(self.istatistik_frame)

        return grup

    def sag_panel_olustur(self):
        """Sağ panel - kargo listesi ve detaylar"""
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

        # Kargo listesi sekmesi
        kargo_tab = self.kargo_listesi_sekmesi_olustur()
        tab_widget.addTab(kargo_tab, "Kargo Listesi")

        # Takip geçmişi sekmesi
        takip_tab = self.takip_gecmisi_sekmesi_olustur()
        tab_widget.addTab(takip_tab, "Takip Geçmişi")

        layout.addWidget(tab_widget)

        return panel

    def kargo_listesi_sekmesi_olustur(self):
        """Kargo listesi sekmesi"""
        widget = QFrame()
        layout = QVBoxLayout(widget)

        # Üst butonlar
        ust_butonlar = self.kargo_ust_butonlar_olustur()
        layout.addWidget(ust_butonlar)

        # Kargo tablosu
        self.kargo_tablo = QTableWidget()
        self.kargo_tablo.setColumnCount(9)
        self.kargo_tablo.setHorizontalHeaderLabels(
            ["Kargo No", "Takip No", "Alıcı", "Şehir", "Durum", "Tarih", "Taşıyıcı", "Tutar", "İşlemler"]
        )

        # Tablo ayarları
        header = self.kargo_tablo.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)

        self.kargo_tablo.setAlternatingRowColors(True)
        self.kargo_tablo.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.kargo_tablo.setStyleSheet(
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

        layout.addWidget(self.kargo_tablo)

        return widget

    def takip_gecmisi_sekmesi_olustur(self):
        """Takip geçmişi sekmesi"""
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
        self.log_text.setPlainText("Kargo takip geçmişi burada görüntülenecek...")
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

    def kargo_ust_butonlar_olustur(self):
        """Kargo üst butonları"""
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
        yenile_buton.clicked.connect(self.kargo_listesi_yenile)
        layout.addWidget(yenile_buton)

        # Filtrele
        filtre_combo = QComboBox()
        filtre_combo.addItems(["Tüm Kargolar", "Bekleyen", "Kargoda", "Teslim Edildi", "İptal Edildi"])
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

        # Takip no arama
        takip_arama = QLineEdit()
        takip_arama.setPlaceholderText("Takip no ile ara...")
        takip_arama.setStyleSheet(
            """
            QLineEdit {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """
        )
        layout.addWidget(takip_arama)

        layout.addStretch()

        # Durum çubuğu
        self.kargo_durum_label = QLabel("Toplam Kargo: 0")
        self.kargo_durum_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.kargo_durum_label)

        return frame

    def tasiyici_degisti(self):
        """Taşıyıcı seçimi değiştiğinde"""
        kayit_ekle("Kargo", "TAŞIYICI SEÇİMİ", "tasiyici_degisti", "kargo_servisi.tasiyici_sec")
        try:
            secili_tasiyici = self.tasiyici_combo.currentText()
            self.aktif_tasiyici = secili_tasiyici

            # Taşıyıcı durumunu güncelle
            self.tasiyici_durum_label.setText(f"Durum: {secili_tasiyici} - Bağlı")
            self.tasiyici_durum_label.setStyleSheet(
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

            # Kargo listesini yenile
            self.kargo_listesi_yenile()

            # Log ekle
            self.log_ekle(f"Taşıyıcı değiştirildi: {secili_tasiyici}")

        except Exception as e:
            self.hata_goster("Taşıyıcı Seçim Hatası", str(e))

    def etiket_olustur(self):
        """Etiket oluşturma işlemi"""
        kayit_ekle("Kargo", "Etiket Oluştur", "etiket_olustur", "kargo_servisi.etiket_olustur")
        try:
            if not self.aktif_tasiyici:
                self.hata_goster("Hata", "Lütfen önce bir taşıyıcı seçin")
                return

            # Kargo servisini çağır
            kargo_servisi = self.servis_fabrikasi.kargo_servisi()

            # İşlem başlat
            self.islem_baslat("Etiket oluşturuluyor...")

            sonuc = self.servis_cagir_guvenli(kargo_servisi.etiket_olustur)

            if sonuc:
                self.log_ekle(f"Etiket oluşturma işlemi tamamlandı - Taşıyıcı: {self.aktif_tasiyici}")
                self.kargo_listesi_yenile()
                self.bilgi_goster_mesaj("Başarılı", "Etiket başarıyla oluşturuldu")

            self.islem_bitir()

        except Exception as e:
            self.islem_bitir()
            self.hata_goster("Etiket Oluşturma Hatası", str(e))

    def durum_sorgula(self):
        """Durum sorgulama işlemi"""
        kayit_ekle("Kargo", "Durum Sorgula", "durum_sorgula", "kargo_servisi.durum_sorgula")
        try:
            if not self.aktif_tasiyici:
                self.hata_goster("Hata", "Lütfen önce bir taşıyıcı seçin")
                return

            # Kargo servisini çağır
            kargo_servisi = self.servis_fabrikasi.kargo_servisi()

            # İşlem başlat
            self.islem_baslat("Durum sorgulanıyor...")

            sonuc = self.servis_cagir_guvenli(kargo_servisi.durum_sorgula)

            if sonuc:
                self.log_ekle(f"Durum sorgulama işlemi tamamlandı - Taşıyıcı: {self.aktif_tasiyici}")
                self.kargo_listesi_yenile()
                self.bilgi_goster_mesaj("Başarılı", "Durum sorgulaması tamamlandı")

            self.islem_bitir()

        except Exception as e:
            self.islem_bitir()
            self.hata_goster("Durum Sorgulama Hatası", str(e))

    def toplu_etiket(self):
        """Toplu etiket oluşturma"""
        kayit_ekle("Kargo", "Toplu Etiket", "toplu_etiket", "kargo_servisi.etiket_olustur")
        try:
            if not self.onay_iste("Onay", "Bekleyen tüm kargolar için etiket oluşturulacak. Emin misiniz?"):
                return

            # Kargo servisini çağır
            kargo_servisi = self.servis_fabrikasi.kargo_servisi()

            # İşlem başlat
            self.islem_baslat("Toplu etiket oluşturuluyor...")

            sonuc = self.servis_cagir_guvenli(kargo_servisi.etiket_olustur)

            if sonuc:
                self.log_ekle("Toplu etiket oluşturma işlemi tamamlandı")
                self.kargo_listesi_yenile()
                self.bilgi_goster_mesaj("Başarılı", "Toplu etiket oluşturma tamamlandı")

            self.islem_bitir()

        except Exception as e:
            self.islem_bitir()
            self.hata_goster("Toplu Etiket Hatası", str(e))

    def kargo_iptal(self):
        """Kargo iptal işlemi"""
        kayit_ekle("Kargo", "Kargo İptal", "kargo_iptal", "kargo_servisi.iptal_et")
        try:
            secili_satirlar = self.kargo_tablo.selectionModel().selectedRows()
            if not secili_satirlar:
                self.hata_goster("Hata", "Lütfen iptal edilecek kargoları seçin")
                return

            if not self.onay_iste("Onay", f"{len(secili_satirlar)} kargo iptal edilecek. Emin misiniz?"):
                return

            # Kargo iptal işlemi (stub)
            self.bilgi_goster_mesaj("Başarılı", f"{len(secili_satirlar)} kargo iptal edildi")
            self.kargo_listesi_yenile()

        except Exception as e:
            self.hata_goster("Kargo İptal Hatası", str(e))

    def manifest_olustur(self):
        """Manifest oluşturma"""
        kayit_ekle("Kargo", "Manifest Oluştur", "manifest_olustur", "kargo_servisi.manifest_olustur")
        try:
            # Manifest oluşturma dialog'u (stub)
            self.bilgi_goster_mesaj("Bilgi", "Manifest oluşturma dialog'u açılacak")

        except Exception as e:
            self.hata_goster("Manifest Oluşturma Hatası", str(e))

    def kargo_listesi_yenile(self):
        """Kargo listesini yenile"""
        kayit_ekle("Kargo", "YENİLE", "kargo_listesi_yenile", "kargo_servisi.liste_getir")
        try:
            if not self.aktif_tasiyici:
                return

            # Stub kargo verileri
            self.kargo_verileri = [
                {
                    "kargo_no": f"KRG{i:06d}",
                    "takip_no": f"TK{i:010d}",
                    "alici": f"Alıcı {i}",
                    "sehir": ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya"][i % 5],
                    "durum": ["Bekleyen", "Kargoda", "Teslim Edildi"][i % 3],
                    "tarih": "2024-12-16",
                    "tasiyici": self.aktif_tasiyici,
                    "tutar": (i + 1) * 15.50,
                }
                for i in range(1, 13)
            ]

            self.kargo_tablosunu_guncelle()

        except Exception as e:
            self.hata_goster("Liste Yenileme Hatası", str(e))

    def kargo_tablosunu_guncelle(self):
        """Kargo tablosunu güncelle"""
        try:
            self.kargo_tablo.setRowCount(len(self.kargo_verileri))

            bekleyen_sayisi = 0
            kargoda_sayisi = 0
            teslim_sayisi = 0

            for row, kargo in enumerate(self.kargo_verileri):
                self.kargo_tablo.setItem(row, 0, QTableWidgetItem(kargo["kargo_no"]))
                self.kargo_tablo.setItem(row, 1, QTableWidgetItem(kargo["takip_no"]))
                self.kargo_tablo.setItem(row, 2, QTableWidgetItem(kargo["alici"]))
                self.kargo_tablo.setItem(row, 3, QTableWidgetItem(kargo["sehir"]))

                # Durum - renk kodlaması
                durum_item = QTableWidgetItem(kargo["durum"])
                if kargo["durum"] == "Bekleyen":
                    durum_item.setBackground(Qt.GlobalColor.yellow)
                    bekleyen_sayisi += 1
                elif kargo["durum"] == "Kargoda":
                    durum_item.setBackground(Qt.GlobalColor.cyan)
                    kargoda_sayisi += 1
                elif kargo["durum"] == "Teslim Edildi":
                    durum_item.setBackground(Qt.GlobalColor.green)
                    durum_item.setForeground(Qt.GlobalColor.white)
                    teslim_sayisi += 1
                self.kargo_tablo.setItem(row, 4, durum_item)

                self.kargo_tablo.setItem(row, 5, QTableWidgetItem(UIYardimcilari.tarih_formatla(kargo["tarih"])))
                self.kargo_tablo.setItem(row, 6, QTableWidgetItem(kargo["tasiyici"]))
                self.kargo_tablo.setItem(row, 7, QTableWidgetItem(UIYardimcilari.para_formatla(kargo["tutar"])))

                # İşlemler butonu
                islem_buton = QPushButton("Takip")
                islem_buton.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        border-radius: 3px;
                        padding: 4px 8px;
                        font-size: 10px;
                    }
                """
                )
                self.kargo_tablo.setCellWidget(row, 8, islem_buton)

            # Durum çubuğunu güncelle
            self.kargo_durum_label.setText(f"Toplam Kargo: {len(self.kargo_verileri)}")

            # İstatistikleri güncelle
            self.bekleyen_kargo_label.setText(f"Bekleyen: {bekleyen_sayisi}")
            self.kargoda_label.setText(f"Kargoda: {kargoda_sayisi}")
            self.teslim_edildi_label.setText(f"Teslim Edildi: {teslim_sayisi}")

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
        """Takip geçmişini temizle"""
        kayit_ekle("Kargo", "Geçmişi Temizle", "gecmisi_temizle", "log_temizle")
        try:
            if self.onay_iste("Onay", "Takip geçmişi temizlenecek. Emin misiniz?"):
                self.log_text.clear()
                self.log_ekle("Takip geçmişi temizlendi")

        except Exception as e:
            self.hata_goster("Temizleme Hatası", str(e))

    def gecmisi_disa_aktar(self):
        """Takip geçmişini dışa aktar"""
        try:
            # Dışa aktarım dialog'u (stub)
            self.bilgi_goster_mesaj("Bilgi", "Takip geçmişi dışa aktarım dialog'u açılacak")

        except Exception as e:
            self.hata_goster("Dışa Aktarım Hatası", str(e))

    def verileri_yukle(self):
        """Ekran açıldığında"""
        # İlk taşıyıcıyı seç
        if self.tasiyici_combo.count() > 0:
            self.tasiyici_combo.setCurrentIndex(0)
            self.tasiyici_degisti()

        self.log_ekle("Kargo ekranı yüklendi")

    def verileri_temizle(self):
        """Ekran kapandığında"""
        pass
