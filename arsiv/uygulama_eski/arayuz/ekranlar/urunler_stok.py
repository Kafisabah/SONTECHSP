# Version: 0.1.0
# Last Update: 2024-12-16
# Module: uygulama.arayuz.ekranlar.urunler_stok
# Description: Ürünler ve stok yönetimi ekranı
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
    QSpinBox,
    QGroupBox,
    QSplitter,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from .temel_ekran import TemelEkran
from ..servis_fabrikasi import ServisFabrikasi
from ..yardimcilar import UIYardimcilari
from ..buton_eslestirme_kaydi import kayit_ekle
from ..log_sistemi import stub_servis_loglama


class UrunlerStok(TemelEkran):
    """Ürünler ve stok yönetimi ekranı"""

    def __init__(self, servis_fabrikasi: ServisFabrikasi, parent=None):
        self.arama_input = None
        self.kategori_combo = None
        self.urun_tablo = None
        self.yeni_urun_buton = None
        self.duzenle_buton = None
        self.sayim_buton = None
        self.transfer_buton = None
        self.urun_verileri = []
        super().__init__(servis_fabrikasi, parent)

    def ekrani_hazirla(self):
        """Ürünler ve stok ekranını hazırla"""
        # Ana başlık
        baslik = QLabel("Ürünler ve Stok Yönetimi")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        baslik.setStyleSheet("color: #2c3e50; margin: 10px;")
        self.ana_layout.addWidget(baslik)

        # Ana splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Sol panel - Arama ve filtreler
        sol_panel = self.sol_panel_olustur()
        splitter.addWidget(sol_panel)

        # Sağ panel - Ürün listesi ve işlemler
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
        grup = QGroupBox("Arama")
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
        self.arama_input.setPlaceholderText("Ürün adı, kodu veya barkod...")
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
        # Wrapper fonksiyonu ile buton bağla
        self.buton_bagla_ve_kaydet(arama_buton, "ARA", self.arama_yap, "stok_servisi.urun_ara")
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

        # Kategori filtresi
        kategori_label = QLabel("Kategori:")
        layout.addWidget(kategori_label)

        self.kategori_combo = QComboBox()
        self.kategori_combo.addItems(["Tümü", "Elektronik", "Giyim", "Gıda", "Ev & Yaşam", "Spor", "Diğer"])
        self.kategori_combo.setStyleSheet(
            """
            QComboBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """
        )
        self.kategori_combo.currentTextChanged.connect(self.filtre_degisti)
        layout.addWidget(self.kategori_combo)

        # Stok durumu filtresi
        stok_label = QLabel("Stok Durumu:")
        layout.addWidget(stok_label)

        self.stok_combo = QComboBox()
        self.stok_combo.addItems(["Tümü", "Stokta Var", "Kritik Seviye", "Stokta Yok"])
        self.stok_combo.setStyleSheet(
            """
            QComboBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """
        )
        self.stok_combo.currentTextChanged.connect(self.filtre_degisti)
        layout.addWidget(self.stok_combo)

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

        # Kritik stok raporu
        kritik_stok_buton = QPushButton("Kritik Stok Raporu")
        kritik_stok_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """
        )
        # Wrapper fonksiyonu ile buton bağla
        self.buton_bagla_ve_kaydet(
            kritik_stok_buton, "Kritik Stok Raporu", self.kritik_stok_raporu, "rapor_goster_stub"
        )
        layout.addWidget(kritik_stok_buton)

        # Stok değer raporu
        deger_raporu_buton = QPushButton("Stok Değer Raporu")
        deger_raporu_buton.setStyleSheet(
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
        # Wrapper fonksiyonu ile buton bağla
        self.buton_bagla_ve_kaydet(deger_raporu_buton, "Stok Değer Raporu", self.stok_deger_raporu, "rapor_goster_stub")
        layout.addWidget(deger_raporu_buton)

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
        # Wrapper fonksiyonu ile buton bağla
        self.buton_bagla_ve_kaydet(excel_buton, "Excel'e Aktar", self.excel_aktar, "excel_export_servisi_stub")
        layout.addWidget(excel_buton)

        return grup

    def sag_panel_olustur(self):
        """Sağ panel - ürün listesi ve işlemler"""
        panel = QFrame()
        layout = QVBoxLayout(panel)

        # Üst işlem butonları
        ust_butonlar = self.ust_butonlar_olustur()
        layout.addWidget(ust_butonlar)

        # Ürün tablosu
        self.urun_tablo = QTableWidget()
        self.urun_tablo.setColumnCount(7)
        self.urun_tablo.setHorizontalHeaderLabels(
            ["Ürün Kodu", "Ürün Adı", "Kategori", "Birim", "Stok", "Birim Fiyat", "Toplam Değer"]
        )

        # Tablo ayarları
        header = self.urun_tablo.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        self.urun_tablo.setAlternatingRowColors(True)
        self.urun_tablo.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.urun_tablo.setStyleSheet(
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

        # Çift tıklama ile düzenleme
        self.urun_tablo.itemDoubleClicked.connect(self.urun_duzenle)

        layout.addWidget(self.urun_tablo)

        # Alt durum çubuğu
        durum_cubugu = self.durum_cubugu_olustur()
        layout.addWidget(durum_cubugu)

        return panel

    def ust_butonlar_olustur(self):
        """Üst işlem butonları"""
        frame = QFrame()
        layout = QHBoxLayout(frame)

        # Yeni ürün
        self.yeni_urun_buton = QPushButton("YENİ ÜRÜN")
        self.yeni_urun_buton.setStyleSheet(
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
        # Wrapper fonksiyonu ile buton bağla
        self.buton_bagla_ve_kaydet(self.yeni_urun_buton, "YENİ ÜRÜN", self.yeni_urun_ekle, "yeni_urun_dialog_stub")
        layout.addWidget(self.yeni_urun_buton)

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
        # Wrapper fonksiyonu ile buton bağla
        self.buton_bagla_ve_kaydet(self.duzenle_buton, "DÜZENLE", self.urun_duzenle, "urun_duzenle_dialog_stub")
        layout.addWidget(self.duzenle_buton)

        # Stok sayım
        self.sayim_buton = QPushButton("STOK SAYIM")
        self.sayim_buton.setStyleSheet(
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
        # Wrapper fonksiyonu ile buton bağla
        self.buton_bagla_ve_kaydet(self.sayim_buton, "STOK SAYIM", self.stok_sayim, "stok_sayim_dialog_stub")
        layout.addWidget(self.sayim_buton)

        # Transfer
        self.transfer_buton = QPushButton("TRANSFER")
        self.transfer_buton.setStyleSheet(
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
        # Wrapper fonksiyonu ile buton bağla
        self.buton_bagla_ve_kaydet(self.transfer_buton, "TRANSFER", self.stok_transfer, "stok_transfer_dialog_stub")
        layout.addWidget(self.transfer_buton)

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
        # Wrapper fonksiyonu ile buton bağla
        self.buton_bagla_ve_kaydet(yenile_buton, "YENİLE", self.verileri_yukle, "stok_servisi.urun_listesi_getir")
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

        self.toplam_urun_label = QLabel("Toplam Ürün: 0")
        self.toplam_urun_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.toplam_urun_label)

        layout.addStretch()

        self.toplam_deger_label = QLabel("Toplam Stok Değeri: 0,00 TL")
        self.toplam_deger_label.setStyleSheet("font-weight: bold; color: #27ae60;")
        layout.addWidget(self.toplam_deger_label)

        return frame

    def arama_degisti(self):
        """Arama metni değiştiğinde"""
        # Gerçek zamanlı arama (3 karakterden sonra)
        if len(self.arama_input.text()) >= 3:
            self.arama_yap()
        elif len(self.arama_input.text()) == 0:
            self.verileri_yukle()

    def arama_yap(self):
        """Ürün arama işlemi"""
        try:
            arama_terimi = self.arama_input.text().strip()

            # Stok servisini çağır
            stok_servisi = self.servis_fabrikasi.stok_servisi()
            sonuc = self.servis_cagir_guvenli(stok_servisi.urun_ara, arama_terimi)

            if sonuc:
                # Arama sonuçlarını göster (stub)
                self.arama_sonuclarini_goster(arama_terimi)

        except Exception as e:
            self.hata_goster("Arama Hatası", str(e))

    def arama_sonuclarini_goster(self, arama_terimi: str):
        """Arama sonuçlarını göster (stub)"""
        # Stub arama sonuçları
        self.urun_verileri = [
            {
                "urun_kodu": f"ARN{i:03d}",
                "urun_adi": f"Arama Sonucu {arama_terimi} {i}",
                "kategori": "Elektronik",
                "birim": "adet",
                "stok": 50 - i * 5,
                "birim_fiyat": 25.50 + i,
                "toplam_deger": (50 - i * 5) * (25.50 + i),
            }
            for i in range(1, 6)
        ]

        self.urun_tablosunu_guncelle()

    def filtre_degisti(self):
        """Filtre değiştiğinde"""
        try:
            kategori = self.kategori_combo.currentText()
            stok_durumu = self.stok_combo.currentText()

            # Stok servisini çağır
            stok_servisi = self.servis_fabrikasi.stok_servisi()
            sonuc = self.servis_cagir_guvenli(stok_servisi.urun_filtrele, kategori, stok_durumu)

            if sonuc:
                self.verileri_yukle()

        except Exception as e:
            self.hata_goster("Filtreleme Hatası", str(e))

    def urun_tablosunu_guncelle(self):
        """Ürün tablosunu güncelle"""
        try:
            self.urun_tablo.setRowCount(len(self.urun_verileri))

            for row, urun in enumerate(self.urun_verileri):
                self.urun_tablo.setItem(row, 0, QTableWidgetItem(urun["urun_kodu"]))
                self.urun_tablo.setItem(row, 1, QTableWidgetItem(urun["urun_adi"]))
                self.urun_tablo.setItem(row, 2, QTableWidgetItem(urun["kategori"]))
                self.urun_tablo.setItem(row, 3, QTableWidgetItem(urun["birim"]))

                # Stok miktarı - renk kodlaması
                stok_item = QTableWidgetItem(str(urun["stok"]))
                if urun["stok"] <= 10:
                    stok_item.setBackground(Qt.GlobalColor.red)
                    stok_item.setForeground(Qt.GlobalColor.white)
                elif urun["stok"] <= 25:
                    stok_item.setBackground(Qt.GlobalColor.yellow)
                self.urun_tablo.setItem(row, 4, stok_item)

                self.urun_tablo.setItem(row, 5, QTableWidgetItem(UIYardimcilari.para_formatla(urun["birim_fiyat"])))
                self.urun_tablo.setItem(row, 6, QTableWidgetItem(UIYardimcilari.para_formatla(urun["toplam_deger"])))

            # Durum çubuğunu güncelle
            self.durum_cubugunu_guncelle()

        except Exception as e:
            self.hata_goster("Tablo Güncelleme Hatası", str(e))

    def durum_cubugunu_guncelle(self):
        """Durum çubuğunu güncelle"""
        try:
            toplam_urun = len(self.urun_verileri)
            toplam_deger = sum(urun["toplam_deger"] for urun in self.urun_verileri)

            self.toplam_urun_label.setText(f"Toplam Ürün: {toplam_urun}")
            self.toplam_deger_label.setText(f"Toplam Stok Değeri: {UIYardimcilari.para_formatla(toplam_deger)}")

        except Exception as e:
            self.hata_goster("Durum Güncelleme Hatası", str(e))

    def yeni_urun_ekle(self):
        """Yeni ürün ekleme dialog'u aç"""
        try:
            # Stub servis loglama
            stub_servis_loglama(
                ekran_adi="UrunlerStok",
                buton_adi="YENİ ÜRÜN",
                handler_adi="yeni_urun_ekle",
                servis_metodu="yeni_urun_dialog_stub",
                detay="Yeni ürün dialog'u stub açıldı",
            )

            # Yeni ürün dialog'u aç (stub)
            self.bilgi_goster_mesaj("Bilgi", "Yeni ürün ekleme dialog'u açılacak")

        except Exception as e:
            self.hata_goster("Yeni Ürün Hatası", str(e))

    def urun_duzenle(self):
        """Seçili ürünü düzenle"""
        try:
            secili_satir = self.urun_tablo.currentRow()
            if secili_satir < 0:
                self.hata_goster("Hata", "Lütfen düzenlemek için bir ürün seçin")
                return

            urun_kodu = self.urun_tablo.item(secili_satir, 0).text()

            # Stub servis loglama
            stub_servis_loglama(
                ekran_adi="UrunlerStok",
                buton_adi="DÜZENLE",
                handler_adi="urun_duzenle",
                servis_metodu="urun_duzenle_dialog_stub",
                detay=f"Ürün düzenleme dialog'u stub açıldı: {urun_kodu}",
            )

            # Ürün düzenleme dialog'u aç (stub)
            self.bilgi_goster_mesaj("Bilgi", f"Ürün düzenleme dialog'u açılacak: {urun_kodu}")

        except Exception as e:
            self.hata_goster("Ürün Düzenleme Hatası", str(e))

    def stok_sayim(self):
        """Stok sayım dialog'u aç"""
        kayit_ekle("Ürünler Stok", "STOK SAYIM", "stok_sayim", "stok_sayim_dialog")
        try:
            secili_satir = self.urun_tablo.currentRow()
            if secili_satir < 0:
                self.hata_goster("Hata", "Lütfen sayım için bir ürün seçin")
                return

            # Stok sayım dialog'u aç (stub)
            urun_kodu = self.urun_tablo.item(secili_satir, 0).text()
            self.bilgi_goster_mesaj("Bilgi", f"Stok sayım dialog'u açılacak: {urun_kodu}")

        except Exception as e:
            self.hata_goster("Stok Sayım Hatası", str(e))

    def stok_transfer(self):
        """Stok transfer dialog'u aç"""
        kayit_ekle("Ürünler Stok", "TRANSFER", "stok_transfer", "stok_transfer_dialog")
        try:
            secili_satir = self.urun_tablo.currentRow()
            if secili_satir < 0:
                self.hata_goster("Hata", "Lütfen transfer için bir ürün seçin")
                return

            # Stok transfer dialog'u aç (stub)
            urun_kodu = self.urun_tablo.item(secili_satir, 0).text()
            self.bilgi_goster_mesaj("Bilgi", f"Stok transfer dialog'u açılacak: {urun_kodu}")

        except Exception as e:
            self.hata_goster("Stok Transfer Hatası", str(e))

    def kritik_stok_raporu(self):
        """Kritik stok raporu göster"""
        try:
            # Stub servis loglama
            stub_servis_loglama(
                ekran_adi="UrunlerStok",
                buton_adi="Kritik Stok Raporu",
                handler_adi="kritik_stok_raporu",
                servis_metodu="rapor_goster_stub",
                detay="Kritik stok raporu stub açıldı",
            )

            # Kritik stok raporu (stub)
            self.bilgi_goster_mesaj("Bilgi", "Kritik stok raporu açılacak")

        except Exception as e:
            self.hata_goster("Kritik Stok Raporu Hatası", str(e))

    def stok_deger_raporu(self):
        """Stok değer raporu göster"""
        kayit_ekle("Ürünler Stok", "Stok Değer Raporu", "stok_deger_raporu", "rapor_goster")
        try:
            # Stok değer raporu (stub)
            self.bilgi_goster_mesaj("Bilgi", "Stok değer raporu açılacak")

        except Exception as e:
            self.hata_goster("Stok Değer Raporu Hatası", str(e))

    def excel_aktar(self):
        """Excel'e aktar"""
        kayit_ekle("Ürünler Stok", "Excel'e Aktar", "excel_aktar", "excel_export_servisi")
        try:
            # Excel aktarım (stub)
            self.bilgi_goster_mesaj("Bilgi", "Excel aktarım işlemi başlatılacak")

        except Exception as e:
            self.hata_goster("Excel Aktarım Hatası", str(e))

    def verileri_yukle(self):
        """Ürün verilerini yükle"""
        try:
            # Stok servisini çağır
            stok_servisi = self.servis_fabrikasi.stok_servisi()
            sonuc = self.servis_cagir_guvenli(stok_servisi.urun_listesi_getir)

            if sonuc:
                # Stub ürün verileri
                self.urun_verileri = [
                    {
                        "urun_kodu": f"URN{i:03d}",
                        "urun_adi": f"Ürün {i}",
                        "kategori": ["Elektronik", "Giyim", "Gıda", "Ev & Yaşam"][i % 4],
                        "birim": "adet",
                        "stok": 100 - i * 3,
                        "birim_fiyat": 15.50 + i * 2,
                        "toplam_deger": (100 - i * 3) * (15.50 + i * 2),
                    }
                    for i in range(1, 21)
                ]

                self.urun_tablosunu_guncelle()

        except Exception as e:
            self.hata_goster("Veri Yükleme Hatası", str(e))

    def verileri_temizle(self):
        """Ekran kapandığında"""
        pass
