# Version: 0.1.0
# Last Update: 2024-12-16
# Module: uygulama.arayuz.ekranlar.musteriler
# Description: Müşteri yönetimi ekranı
# Changelog:
# - İlk sürüm oluşturuldu

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QFrame,
    QGridLayout,
    QHeaderView,
    QComboBox,
    QGroupBox,
    QSplitter,
    QDateEdit,
    QSpinBox,
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from .temel_ekran import TemelEkran
from ..servis_fabrikasi import ServisFabrikasi
from ..yardimcilar import UIYardimcilari
from ..buton_eslestirme_kaydi import kayit_ekle


class Musteriler(TemelEkran):
    """Müşteri yönetimi ekranı"""

    def __init__(self, servis_fabrikasi: ServisFabrikasi, parent=None):
        self.arama_input = None
        self.musteri_tipi_combo = None
        self.musteri_tablo = None
        self.yeni_musteri_buton = None
        self.duzenle_buton = None
        self.detay_buton = None
        self.puan_islem_buton = None
        self.musteri_verileri = []
        super().__init__(servis_fabrikasi, parent)

    def ekrani_hazirla(self):
        """Müşteri ekranını hazırla"""
        # Ana başlık
        baslik = QLabel("Müşteri Yönetimi")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        baslik.setStyleSheet("color: #2c3e50; margin: 10px;")
        self.ana_layout.addWidget(baslik)

        # Ana splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Sol panel - Arama ve filtreler
        sol_panel = self.sol_panel_olustur()
        splitter.addWidget(sol_panel)

        # Sağ panel - Müşteri listesi ve işlemler
        sag_panel = self.sag_panel_olustur()
        splitter.addWidget(sag_panel)

        # Splitter oranları
        splitter.setSizes([300, 700])

        self.ana_layout.addWidget(splitter)
        self.ekran_hazir = True

    def sol_panel_olustur(self):
        """Sol panel - arama ve filtreler"""
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

        # Arama grubu
        arama_grup = self.arama_grubu_olustur()
        layout.addWidget(arama_grup)

        # Filtre grubu
        filtre_grup = self.filtre_grubu_olustur()
        layout.addWidget(filtre_grup)

        # Hızlı işlemler grubu
        islem_grup = self.hizli_islemler_grubu_olustur()
        layout.addWidget(islem_grup)

        layout.addStretch()

        return panel

    def arama_grubu_olustur(self):
        """Arama grubu"""
        grup = QGroupBox("Müşteri Arama")
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

        # Arama input
        self.arama_input = QLineEdit()
        self.arama_input.setPlaceholderText("Ad, soyad, telefon veya e-posta...")
        self.arama_input.setStyleSheet(
            """
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """
        )
        self.arama_input.textChanged.connect(self.arama_degisti)
        layout.addWidget(self.arama_input)

        # Arama butonu
        arama_buton = QPushButton("ARA")
        arama_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        )
        arama_buton.clicked.connect(self.arama_yap)
        layout.addWidget(arama_buton)

        return grup

    def filtre_grubu_olustur(self):
        """Filtre grubu"""
        grup = QGroupBox("Filtreler")
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

        # Müşteri tipi filtresi
        tip_label = QLabel("Müşteri Tipi:")
        layout.addWidget(tip_label)

        self.musteri_tipi_combo = QComboBox()
        self.musteri_tipi_combo.addItems(["Tümü", "Bireysel", "Kurumsal", "VIP", "Pasif"])
        self.musteri_tipi_combo.setStyleSheet(
            """
            QComboBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """
        )
        self.musteri_tipi_combo.currentTextChanged.connect(self.filtre_degisti)
        layout.addWidget(self.musteri_tipi_combo)

        # Sadakat durumu filtresi
        sadakat_label = QLabel("Sadakat Durumu:")
        layout.addWidget(sadakat_label)

        self.sadakat_combo = QComboBox()
        self.sadakat_combo.addItems(["Tümü", "Bronz", "Gümüş", "Altın", "Platin"])
        self.sadakat_combo.setStyleSheet(
            """
            QComboBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """
        )
        self.sadakat_combo.currentTextChanged.connect(self.filtre_degisti)
        layout.addWidget(self.sadakat_combo)

        # Kayıt tarihi filtresi
        tarih_label = QLabel("Kayıt Tarihi:")
        layout.addWidget(tarih_label)

        self.tarih_combo = QComboBox()
        self.tarih_combo.addItems(["Tümü", "Son 30 Gün", "Son 3 Ay", "Son 6 Ay", "Son 1 Yıl"])
        self.tarih_combo.setStyleSheet(
            """
            QComboBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """
        )
        self.tarih_combo.currentTextChanged.connect(self.filtre_degisti)
        layout.addWidget(self.tarih_combo)

        return grup

    def hizli_islemler_grubu_olustur(self):
        """Hızlı işlemler grubu"""
        grup = QGroupBox("Hızlı İşlemler")
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

        # VIP müşteriler
        vip_buton = QPushButton("VIP Müşteriler")
        vip_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """
        )
        vip_buton.clicked.connect(self.vip_musteriler)
        layout.addWidget(vip_buton)

        # Doğum günü yaklaşanlar
        dogum_gunu_buton = QPushButton("Doğum Günü Yaklaşanlar")
        dogum_gunu_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """
        )
        dogum_gunu_buton.clicked.connect(self.dogum_gunu_yaklasanlar)
        layout.addWidget(dogum_gunu_buton)

        # Sadakat raporu
        sadakat_buton = QPushButton("Sadakat Raporu")
        sadakat_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """
        )
        sadakat_buton.clicked.connect(self.sadakat_raporu)
        layout.addWidget(sadakat_buton)

        # Excel'e aktar
        excel_buton = QPushButton("Excel'e Aktar")
        excel_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #8e44ad;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7d3c98;
            }
        """
        )
        excel_buton.clicked.connect(self.excel_aktar)
        layout.addWidget(excel_buton)

        return grup

    def sag_panel_olustur(self):
        """Sağ panel - müşteri listesi ve işlemler"""
        panel = QFrame()
        layout = QVBoxLayout(panel)

        # Üst işlem butonları
        ust_butonlar = self.ust_butonlar_olustur()
        layout.addWidget(ust_butonlar)

        # Müşteri tablosu
        self.musteri_tablo = QTableWidget()
        self.musteri_tablo.setColumnCount(8)
        self.musteri_tablo.setHorizontalHeaderLabels(
            ["Müşteri No", "Ad Soyad", "Telefon", "E-posta", "Tip", "Sadakat", "Puan", "Son Alışveriş"]
        )

        # Tablo ayarları
        header = self.musteri_tablo.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)

        self.musteri_tablo.setAlternatingRowColors(True)
        self.musteri_tablo.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.musteri_tablo.setStyleSheet(
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

        # Çift tıklama ile detay
        self.musteri_tablo.itemDoubleClicked.connect(self.musteri_detay)

        layout.addWidget(self.musteri_tablo)

        # Alt durum çubuğu
        durum_cubugu = self.durum_cubugu_olustur()
        layout.addWidget(durum_cubugu)

        return panel

    def ust_butonlar_olustur(self):
        """Üst işlem butonları"""
        frame = QFrame()
        layout = QHBoxLayout(frame)

        # Yeni müşteri
        self.yeni_musteri_buton = QPushButton("YENİ MÜŞTERİ")
        self.yeni_musteri_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """
        )
        self.yeni_musteri_buton.clicked.connect(self.yeni_musteri_ekle)
        layout.addWidget(self.yeni_musteri_buton)

        # Düzenle
        self.duzenle_buton = QPushButton("DÜZENLE")
        self.duzenle_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        )
        self.duzenle_buton.clicked.connect(self.musteri_duzenle)
        layout.addWidget(self.duzenle_buton)

        # Detay
        self.detay_buton = QPushButton("DETAY")
        self.detay_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """
        )
        self.detay_buton.clicked.connect(self.musteri_detay)
        layout.addWidget(self.detay_buton)

        # Puan işlemi
        self.puan_islem_buton = QPushButton("PUAN İŞLEMİ")
        self.puan_islem_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """
        )
        self.puan_islem_buton.clicked.connect(self.puan_islemi)
        layout.addWidget(self.puan_islem_buton)

        layout.addStretch()

        # Yenile butonu
        yenile_buton = QPushButton("YENİLE")
        yenile_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """
        )
        yenile_buton.clicked.connect(self.verileri_yukle)
        layout.addWidget(yenile_buton)

        return frame

    def durum_cubugu_olustur(self):
        """Alt durum çubuğu"""
        frame = QFrame()
        frame.setStyleSheet(
            """
            QFrame {
                background-color: #ecf0f1;
                border-top: 1px solid #bdc3c7;
                padding: 5px;
            }
        """
        )
        layout = QHBoxLayout(frame)

        self.toplam_musteri_label = QLabel("Toplam Müşteri: 0")
        self.toplam_musteri_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.toplam_musteri_label)

        layout.addStretch()

        self.aktif_musteri_label = QLabel("Aktif Müşteri: 0")
        self.aktif_musteri_label.setStyleSheet("font-weight: bold; color: #27ae60;")
        layout.addWidget(self.aktif_musteri_label)

        layout.addStretch()

        self.toplam_puan_label = QLabel("Toplam Puan: 0")
        self.toplam_puan_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        layout.addWidget(self.toplam_puan_label)

        return frame

    def arama_degisti(self):
        """Arama metni değiştiğinde"""
        # Gerçek zamanlı arama (3 karakterden sonra)
        if len(self.arama_input.text()) >= 3:
            self.arama_yap()
        elif len(self.arama_input.text()) == 0:
            self.verileri_yukle()

    def arama_yap(self):
        """Müşteri arama işlemi"""
        kayit_ekle("Müşteriler", "ARA", "arama_yap", "crm_servisi.musteri_ara")
        try:
            arama_terimi = self.arama_input.text().strip()

            # CRM servisini çağır
            crm_servisi = self.servis_fabrikasi.crm_servisi()
            sonuc = self.servis_cagir_guvenli(crm_servisi.musteri_ara, arama_terimi)

            if sonuc:
                # Arama sonuçlarını göster (stub)
                self.arama_sonuclarini_goster(arama_terimi)

        except Exception as e:
            self.hata_goster("Arama Hatası", str(e))

    def arama_sonuclarini_goster(self, arama_terimi: str):
        """Arama sonuçlarını göster (stub)"""
        # Stub arama sonuçları
        self.musteri_verileri = [
            {
                "musteri_no": f"M{i:04d}",
                "ad_soyad": f"Arama {arama_terimi} {i}",
                "telefon": f"0532 123 45{i:02d}",
                "eposta": f"arama{i}@example.com",
                "tip": "Bireysel",
                "sadakat": "Gümüş",
                "puan": 150 + i * 10,
                "son_alisveris": "2024-12-10",
            }
            for i in range(1, 6)
        ]

        self.musteri_tablosunu_guncelle()

    def filtre_degisti(self):
        """Filtre değiştiğinde"""
        kayit_ekle("Müşteriler", "FİLTRE", "filtre_degisti", "crm_servisi.musteri_filtrele")
        try:
            musteri_tipi = self.musteri_tipi_combo.currentText()
            sadakat_durumu = self.sadakat_combo.currentText()
            tarih_filtresi = self.tarih_combo.currentText()

            # CRM servisini çağır
            crm_servisi = self.servis_fabrikasi.crm_servisi()
            sonuc = self.servis_cagir_guvenli(
                crm_servisi.musteri_filtrele, musteri_tipi, sadakat_durumu, tarih_filtresi
            )

            if sonuc:
                self.verileri_yukle()

        except Exception as e:
            self.hata_goster("Filtreleme Hatası", str(e))

    def musteri_tablosunu_guncelle(self):
        """Müşteri tablosunu güncelle"""
        try:
            self.musteri_tablo.setRowCount(len(self.musteri_verileri))

            for row, musteri in enumerate(self.musteri_verileri):
                self.musteri_tablo.setItem(row, 0, QTableWidgetItem(musteri["musteri_no"]))
                self.musteri_tablo.setItem(row, 1, QTableWidgetItem(musteri["ad_soyad"]))
                self.musteri_tablo.setItem(row, 2, QTableWidgetItem(musteri["telefon"]))
                self.musteri_tablo.setItem(row, 3, QTableWidgetItem(musteri["eposta"]))
                self.musteri_tablo.setItem(row, 4, QTableWidgetItem(musteri["tip"]))

                # Sadakat seviyesi - renk kodlaması
                sadakat_item = QTableWidgetItem(musteri["sadakat"])
                if musteri["sadakat"] == "Platin":
                    sadakat_item.setBackground(Qt.GlobalColor.darkBlue)
                    sadakat_item.setForeground(Qt.GlobalColor.white)
                elif musteri["sadakat"] == "Altın":
                    sadakat_item.setBackground(Qt.GlobalColor.yellow)
                elif musteri["sadakat"] == "Gümüş":
                    sadakat_item.setBackground(Qt.GlobalColor.lightGray)
                self.musteri_tablo.setItem(row, 5, sadakat_item)

                self.musteri_tablo.setItem(row, 6, QTableWidgetItem(str(musteri["puan"])))
                self.musteri_tablo.setItem(
                    row, 7, QTableWidgetItem(UIYardimcilari.tarih_formatla(musteri["son_alisveris"]))
                )

            # Durum çubuğunu güncelle
            self.durum_cubugunu_guncelle()

        except Exception as e:
            self.hata_goster("Tablo Güncelleme Hatası", str(e))

    def durum_cubugunu_guncelle(self):
        """Durum çubuğunu güncelle"""
        try:
            toplam_musteri = len(self.musteri_verileri)
            aktif_musteri = len([m for m in self.musteri_verileri if m["tip"] != "Pasif"])
            toplam_puan = sum(musteri["puan"] for musteri in self.musteri_verileri)

            self.toplam_musteri_label.setText(f"Toplam Müşteri: {toplam_musteri}")
            self.aktif_musteri_label.setText(f"Aktif Müşteri: {aktif_musteri}")
            self.toplam_puan_label.setText(f"Toplam Puan: {toplam_puan:,}")

        except Exception as e:
            self.hata_goster("Durum Güncelleme Hatası", str(e))

    def yeni_musteri_ekle(self):
        """Yeni müşteri ekleme dialog'u aç"""
        kayit_ekle("Müşteriler", "YENİ MÜŞTERİ", "yeni_musteri_ekle", "yeni_musteri_dialog")
        try:
            # Yeni müşteri dialog'u aç (stub)
            self.bilgi_goster_mesaj("Bilgi", "Yeni müşteri ekleme dialog'u açılacak")

        except Exception as e:
            self.hata_goster("Yeni Müşteri Hatası", str(e))

    def musteri_duzenle(self):
        """Seçili müşteriyi düzenle"""
        kayit_ekle("Müşteriler", "DÜZENLE", "musteri_duzenle", "musteri_duzenle_dialog")
        try:
            secili_satir = self.musteri_tablo.currentRow()
            if secili_satir < 0:
                self.hata_goster("Hata", "Lütfen düzenlemek için bir müşteri seçin")
                return

            # Müşteri düzenleme dialog'u aç (stub)
            musteri_no = self.musteri_tablo.item(secili_satir, 0).text()
            self.bilgi_goster_mesaj("Bilgi", f"Müşteri düzenleme dialog'u açılacak: {musteri_no}")

        except Exception as e:
            self.hata_goster("Müşteri Düzenleme Hatası", str(e))

    def musteri_detay(self):
        """Müşteri detay dialog'u aç"""
        kayit_ekle("Müşteriler", "DETAY", "musteri_detay", "musteri_detay_dialog")
        try:
            secili_satir = self.musteri_tablo.currentRow()
            if secili_satir < 0:
                self.hata_goster("Hata", "Lütfen detay için bir müşteri seçin")
                return

            # Müşteri detay dialog'u aç (stub)
            musteri_no = self.musteri_tablo.item(secili_satir, 0).text()
            self.bilgi_goster_mesaj("Bilgi", f"Müşteri detay dialog'u açılacak: {musteri_no}")

        except Exception as e:
            self.hata_goster("Müşteri Detay Hatası", str(e))

    def puan_islemi(self):
        """Puan işlem dialog'u aç"""
        kayit_ekle("Müşteriler", "PUAN İŞLEMİ", "puan_islemi", "puan_islemi_dialog")
        try:
            secili_satir = self.musteri_tablo.currentRow()
            if secili_satir < 0:
                self.hata_goster("Hata", "Lütfen puan işlemi için bir müşteri seçin")
                return

            # Puan işlem dialog'u aç (stub)
            musteri_no = self.musteri_tablo.item(secili_satir, 0).text()
            self.bilgi_goster_mesaj("Bilgi", f"Puan işlem dialog'u açılacak: {musteri_no}")

        except Exception as e:
            self.hata_goster("Puan İşlem Hatası", str(e))

    def vip_musteriler(self):
        """VIP müşteriler listesi"""
        kayit_ekle("Müşteriler", "VIP Müşteriler", "vip_musteriler", "vip_raporu")
        try:
            # VIP müşteriler listesi (stub)
            self.bilgi_goster_mesaj("Bilgi", "VIP müşteriler listesi açılacak")

        except Exception as e:
            self.hata_goster("VIP Müşteriler Hatası", str(e))

    def dogum_gunu_yaklasanlar(self):
        """Doğum günü yaklaşan müşteriler"""
        kayit_ekle("Müşteriler", "Doğum Günü Yaklaşanlar", "dogum_gunu_yaklasanlar", "dogum_gunu_raporu")
        try:
            # Doğum günü yaklaşanlar (stub)
            self.bilgi_goster_mesaj("Bilgi", "Doğum günü yaklaşan müşteriler listesi açılacak")

        except Exception as e:
            self.hata_goster("Doğum Günü Hatası", str(e))

    def sadakat_raporu(self):
        """Sadakat raporu göster"""
        kayit_ekle("Müşteriler", "Sadakat Raporu", "sadakat_raporu", "sadakat_raporu_goster")
        try:
            # Sadakat raporu (stub)
            self.bilgi_goster_mesaj("Bilgi", "Sadakat raporu açılacak")

        except Exception as e:
            self.hata_goster("Sadakat Raporu Hatası", str(e))

    def excel_aktar(self):
        """Excel'e aktar"""
        kayit_ekle("Müşteriler", "Excel'e Aktar", "excel_aktar", "excel_export")
        try:
            # Excel aktarım (stub)
            self.bilgi_goster_mesaj("Bilgi", "Excel aktarım işlemi başlatılacak")

        except Exception as e:
            self.hata_goster("Excel Aktarım Hatası", str(e))

    def verileri_yukle(self):
        """Müşteri verilerini yükle"""
        try:
            # CRM servisini çağır
            crm_servisi = self.servis_fabrikasi.crm_servisi()
            sonuc = self.servis_cagir_guvenli(crm_servisi.musteri_listesi_getir)

            if sonuc:
                # Stub müşteri verileri
                self.musteri_verileri = [
                    {
                        "musteri_no": f"M{i:04d}",
                        "ad_soyad": f"Müşteri {i}",
                        "telefon": f"0532 123 45{i:02d}",
                        "eposta": f"musteri{i}@example.com",
                        "tip": ["Bireysel", "Kurumsal", "VIP"][i % 3],
                        "sadakat": ["Bronz", "Gümüş", "Altın", "Platin"][i % 4],
                        "puan": 100 + i * 25,
                        "son_alisveris": "2024-12-10",
                    }
                    for i in range(1, 16)
                ]

                self.musteri_tablosunu_guncelle()

        except Exception as e:
            self.hata_goster("Veri Yükleme Hatası", str(e))

    def verileri_temizle(self):
        """Ekran kapandığında"""
        pass
