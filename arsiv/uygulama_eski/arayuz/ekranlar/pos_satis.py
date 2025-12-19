# Version: 0.1.0
# Last Update: 2024-12-16
# Module: uygulama.arayuz.ekranlar.pos_satis
# Description: POS satış ekranı
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
    QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from .temel_ekran import TemelEkran
from ..servis_fabrikasi import ServisFabrikasi
from ..yardimcilar import UIYardimcilari
from ..buton_eslestirme_kaydi import kayit_ekle
from ..log_sistemi import stub_servis_loglama


class PosSatis(TemelEkran):
    """POS satış ekranı"""

    def __init__(self, servis_fabrikasi: ServisFabrikasi, parent=None):
        self.barkod_input = None
        self.sepet_tablo = None
        self.ara_toplam_label = None
        self.indirim_label = None
        self.genel_toplam_label = None
        self.sepet_verileri = []
        super().__init__(servis_fabrikasi, parent)

    def ekrani_hazirla(self):
        """POS satış ekranını hazırla"""
        # Ana başlık
        baslik = QLabel("POS Satış")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        baslik.setStyleSheet("color: #2c3e50; margin: 10px;")
        self.ana_layout.addWidget(baslik)

        # Ana içerik alanı
        icerik_layout = QHBoxLayout()

        # Sol panel - Barkod girişi ve sepet
        sol_panel = self.sol_panel_olustur()
        icerik_layout.addWidget(sol_panel, 2)

        # Sağ panel - Toplam ve ödeme butonları
        sag_panel = self.sag_panel_olustur()
        icerik_layout.addWidget(sag_panel, 1)

        self.ana_layout.addLayout(icerik_layout)
        self.ekran_hazir = True

    def sol_panel_olustur(self):
        """Sol panel - barkod girişi ve sepet tablosu"""
        panel = QFrame()
        layout = QVBoxLayout(panel)

        # Barkod giriş alanı
        barkod_frame = QFrame()
        barkod_layout = QHBoxLayout(barkod_frame)

        barkod_label = QLabel("Barkod/Arama:")
        barkod_label.setFixedWidth(100)
        barkod_layout.addWidget(barkod_label)

        self.barkod_input = QLineEdit()
        self.barkod_input.setPlaceholderText("Barkod okutun veya ürün adı yazın...")
        self.barkod_input.returnPressed.connect(self.ekle_tiklandi)
        barkod_layout.addWidget(self.barkod_input)

        ekle_buton = QPushButton("EKLE")
        ekle_buton.setFixedSize(80, 30)
        ekle_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """
        )
        # Wrapper fonksiyonu ile buton bağla
        self.buton_bagla_ve_kaydet(ekle_buton, "EKLE", self.ekle_tiklandi, "pos_servisi.barkod_ekle")
        barkod_layout.addWidget(ekle_buton)

        layout.addWidget(barkod_frame)

        # Sepet tablosu
        self.sepet_tablo = QTableWidget()
        self.sepet_tablo.setColumnCount(5)
        self.sepet_tablo.setHorizontalHeaderLabels(["Ürün Adı", "Birim Fiyat", "Miktar", "İndirim", "Toplam"])

        # Tablo ayarları
        header = self.sepet_tablo.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        self.sepet_tablo.setAlternatingRowColors(True)
        self.sepet_tablo.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        layout.addWidget(self.sepet_tablo)

        return panel

    def sag_panel_olustur(self):
        """Sağ panel - toplam ve ödeme butonları"""
        panel = QFrame()
        panel.setFixedWidth(300)
        panel.setStyleSheet(
            """
            QFrame {
                background-color: #ecf0f1;
                border-radius: 10px;
                padding: 10px;
            }
        """
        )
        layout = QVBoxLayout(panel)

        # Toplam bilgileri
        toplam_frame = self.toplam_bilgileri_olustur()
        layout.addWidget(toplam_frame)

        # Ödeme butonları
        odeme_frame = self.odeme_butonlari_olustur()
        layout.addWidget(odeme_frame)

        # İşlem butonları
        islem_frame = self.islem_butonlari_olustur()
        layout.addWidget(islem_frame)

        layout.addStretch()

        return panel

    def toplam_bilgileri_olustur(self):
        """Toplam bilgileri alanı"""
        frame = QFrame()
        layout = QVBoxLayout(frame)

        # Ara toplam
        ara_toplam_layout = QHBoxLayout()
        ara_toplam_layout.addWidget(QLabel("Ara Toplam:"))
        self.ara_toplam_label = QLabel("0,00 TL")
        self.ara_toplam_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        ara_toplam_layout.addWidget(self.ara_toplam_label)
        layout.addLayout(ara_toplam_layout)

        # İndirim
        indirim_layout = QHBoxLayout()
        indirim_layout.addWidget(QLabel("İndirim:"))
        self.indirim_label = QLabel("0,00 TL")
        self.indirim_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        indirim_layout.addWidget(self.indirim_label)
        layout.addLayout(indirim_layout)

        # Çizgi
        cizgi = QFrame()
        cizgi.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(cizgi)

        # Genel toplam
        genel_toplam_layout = QHBoxLayout()
        genel_label = QLabel("GENEL TOPLAM:")
        genel_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        genel_toplam_layout.addWidget(genel_label)

        self.genel_toplam_label = QLabel("0,00 TL")
        self.genel_toplam_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.genel_toplam_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.genel_toplam_label.setStyleSheet("color: #e74c3c;")
        genel_toplam_layout.addWidget(self.genel_toplam_label)
        layout.addLayout(genel_toplam_layout)

        return frame

    def odeme_butonlari_olustur(self):
        """Ödeme butonları"""
        frame = QFrame()
        layout = QVBoxLayout(frame)

        # Nakit ödeme
        nakit_buton = QPushButton("NAKİT ÖDEME")
        nakit_buton.setFixedHeight(50)
        nakit_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """
        )
        # Wrapper fonksiyonu ile buton bağla
        self.buton_bagla_ve_kaydet(
            nakit_buton, "NAKİT ÖDEME", lambda: self.odeme_tiklandi("nakit"), "pos_servisi.odeme_tamamla"
        )
        layout.addWidget(nakit_buton)

        # Kart ödeme
        kart_buton = QPushButton("KART ÖDEME")
        kart_buton.setFixedHeight(50)
        kart_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        )
        # Wrapper fonksiyonu ile buton bağla
        self.buton_bagla_ve_kaydet(
            kart_buton, "KART ÖDEME", lambda: self.odeme_tiklandi("kart"), "pos_servisi.odeme_tamamla"
        )
        layout.addWidget(kart_buton)

        # Parçalı ödeme
        parcali_buton = QPushButton("PARÇALI ÖDEME")
        parcali_buton.setFixedHeight(40)
        parcali_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """
        )
        # Wrapper fonksiyonu ile buton bağla
        self.buton_bagla_ve_kaydet(
            parcali_buton, "PARÇALI ÖDEME", lambda: self.odeme_tiklandi("parcali"), "pos_servisi.odeme_tamamla"
        )
        layout.addWidget(parcali_buton)

        return frame

    def islem_butonlari_olustur(self):
        """İşlem butonları"""
        frame = QFrame()
        layout = QGridLayout(frame)

        # Beklet
        beklet_buton = QPushButton("BEKLET")
        beklet_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """
        )
        # Wrapper fonksiyonu ile buton bağla
        self.buton_bagla_ve_kaydet(beklet_buton, "BEKLET", self.beklet_tiklandi, "pos_servisi.satis_beklet")
        layout.addWidget(beklet_buton, 0, 0)

        # İade
        iade_buton = QPushButton("İADE")
        iade_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """
        )
        # Wrapper fonksiyonu ile buton bağla
        self.buton_bagla_ve_kaydet(iade_buton, "İADE", self.iade_tiklandi, "iade_dialogu_stub")
        layout.addWidget(iade_buton, 0, 1)

        # İptal
        iptal_buton = QPushButton("İPTAL")
        iptal_buton.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """
        )
        # Wrapper fonksiyonu ile buton bağla
        self.buton_bagla_ve_kaydet(iptal_buton, "İPTAL", self.iptal_tiklandi, "pos_servisi.satis_iptal")
        layout.addWidget(iptal_buton, 1, 0, 1, 2)

        return frame

    def ekle_tiklandi(self):
        """Ürün ekleme butonu tıklandığında"""
        try:
            barkod = self.barkod_input.text().strip()
            if not barkod:
                self.hata_goster("Hata", "Lütfen barkod veya ürün adı girin")
                return

            # POS servisini çağır
            pos_servisi = self.servis_fabrikasi.pos_servisi()
            sonuc = self.servis_cagir_guvenli(pos_servisi.barkod_ekle, barkod)

            if sonuc:
                # Sepete ürün ekle (stub veri)
                self.sepete_urun_ekle(barkod)
                self.barkod_input.clear()
                self.barkod_input.setFocus()

        except Exception as e:
            self.hata_goster("Ürün Ekleme Hatası", str(e))

    def sepete_urun_ekle(self, barkod: str):
        """Sepete ürün ekle (stub)"""
        # Stub ürün verisi
        urun_adi = f"Ürün {barkod}"
        birim_fiyat = 10.50
        miktar = 1
        indirim = 0.0
        toplam = birim_fiyat * miktar - indirim

        # Sepet verilerine ekle
        self.sepet_verileri.append(
            {"urun_adi": urun_adi, "birim_fiyat": birim_fiyat, "miktar": miktar, "indirim": indirim, "toplam": toplam}
        )

        # Tabloyu güncelle
        self.sepet_tablosunu_guncelle()

    def sepet_tablosunu_guncelle(self):
        """Sepet tablosunu güncelle"""
        try:
            self.sepet_tablo.setRowCount(len(self.sepet_verileri))

            for row, urun in enumerate(self.sepet_verileri):
                self.sepet_tablo.setItem(row, 0, QTableWidgetItem(urun["urun_adi"]))
                self.sepet_tablo.setItem(row, 1, QTableWidgetItem(UIYardimcilari.para_formatla(urun["birim_fiyat"])))
                self.sepet_tablo.setItem(row, 2, QTableWidgetItem(str(urun["miktar"])))
                self.sepet_tablo.setItem(row, 3, QTableWidgetItem(UIYardimcilari.para_formatla(urun["indirim"])))
                self.sepet_tablo.setItem(row, 4, QTableWidgetItem(UIYardimcilari.para_formatla(urun["toplam"])))

            # Toplamları güncelle
            self.toplamlari_guncelle()

        except Exception as e:
            self.hata_goster("Tablo Güncelleme Hatası", str(e))

    def toplamlari_guncelle(self):
        """Toplam bilgilerini güncelle"""
        try:
            ara_toplam = sum(urun["toplam"] for urun in self.sepet_verileri)
            toplam_indirim = sum(urun["indirim"] for urun in self.sepet_verileri)
            genel_toplam = ara_toplam

            self.ara_toplam_label.setText(UIYardimcilari.para_formatla(ara_toplam))
            self.indirim_label.setText(UIYardimcilari.para_formatla(toplam_indirim))
            self.genel_toplam_label.setText(UIYardimcilari.para_formatla(genel_toplam))

        except Exception as e:
            self.hata_goster("Toplam Hesaplama Hatası", str(e))

    def odeme_tiklandi(self, odeme_turu: str):
        """Ödeme butonu tıklandığında"""
        try:
            if not self.sepet_verileri:
                self.hata_goster("Hata", "Sepette ürün bulunmuyor")
                return

            # Genel toplam al
            genel_toplam = sum(urun["toplam"] for urun in self.sepet_verileri)

            # POS servisini çağır
            pos_servisi = self.servis_fabrikasi.pos_servisi()

            if odeme_turu == "parcali":
                # Stub servis loglama
                stub_servis_loglama(
                    ekran_adi="PosSatis",
                    buton_adi="PARÇALI ÖDEME",
                    handler_adi="odeme_tiklandi",
                    servis_metodu="parcali_odeme_dialogu_stub",
                    detay="Parçalı ödeme dialog'u stub açıldı",
                )

                # Parçalı ödeme dialog'u aç (stub)
                self.bilgi_goster_mesaj("Bilgi", "Parçalı ödeme dialog'u açılacak")
            else:
                # Tek ödeme
                sonuc = self.servis_cagir_guvenli(pos_servisi.odeme_tamamla, odeme_turu, genel_toplam)

                if sonuc:
                    self.bilgi_goster_mesaj("Başarılı", f"{odeme_turu.title()} ödeme tamamlandı")
                    self.sepeti_temizle()

        except Exception as e:
            self.hata_goster("Ödeme Hatası", str(e))

    def beklet_tiklandi(self):
        """Beklet butonu tıklandığında"""
        try:
            if not self.sepet_verileri:
                self.hata_goster("Hata", "Sepette ürün bulunmuyor")
                return

            pos_servisi = self.servis_fabrikasi.pos_servisi()
            sonuc = self.servis_cagir_guvenli(pos_servisi.satis_beklet)

            if sonuc:
                self.bilgi_goster_mesaj("Bilgi", "Satış bekletildi")
                self.sepeti_temizle()

        except Exception as e:
            self.hata_goster("Bekletme Hatası", str(e))

    def iade_tiklandi(self):
        """İade butonu tıklandığında"""
        try:
            # Stub servis loglama
            stub_servis_loglama(
                ekran_adi="PosSatis",
                buton_adi="İADE",
                handler_adi="iade_tiklandi",
                servis_metodu="iade_dialogu_stub",
                detay="İade dialog'u stub açıldı",
            )

            # İade dialog'u aç (stub)
            self.bilgi_goster_mesaj("Bilgi", "İade dialog'u açılacak")

        except Exception as e:
            self.hata_goster("İade Hatası", str(e))

    def iptal_tiklandi(self):
        """İptal butonu tıklandığında"""
        try:
            if not self.sepet_verileri:
                return

            if self.onay_iste("Onay", "Sepetteki tüm ürünler silinecek. Emin misiniz?"):
                pos_servisi = self.servis_fabrikasi.pos_servisi()
                sonuc = self.servis_cagir_guvenli(pos_servisi.satis_iptal)

                if sonuc:
                    self.sepeti_temizle()
                    self.bilgi_goster_mesaj("Bilgi", "Satış iptal edildi")

        except Exception as e:
            self.hata_goster("İptal Hatası", str(e))

    def sepeti_temizle(self):
        """Sepeti temizle"""
        self.sepet_verileri.clear()
        self.sepet_tablosunu_guncelle()
        self.barkod_input.setFocus()

    def verileri_yukle(self):
        """Ekran açıldığında"""
        self.barkod_input.setFocus()

    def verileri_temizle(self):
        """Ekran kapandığında"""
        pass
