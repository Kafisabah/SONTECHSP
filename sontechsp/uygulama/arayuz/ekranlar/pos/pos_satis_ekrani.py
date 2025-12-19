# Version: 0.1.0
# Last Update: 2024-12-19
# Module: pos_satis_ekrani
# Description: Ana POS satış ekranı - tüm bileşenleri birleştiren ana widget
# Changelog:
# - İlk oluşturma

"""
POS Satış Ekranı - Ana POS arayüzü birleştirici widget
"""

from typing import Optional
from decimal import Decimal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableView, QSplitter, QApplication
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent

from .sepet_modeli import SepetModeli, SepetOgesi
from .ust_bar import UstBar
from .odeme_paneli import OdemePaneli
from .hizli_islem_seridi import HizliIslemSeridi
from .hizli_urunler_sekmesi import HizliUrunlerSekmesi
from .turkuaz_tema import TurkuazTema
from .pos_hata_yoneticisi import POSHataYoneticisi
from .klavye_kisayol_yoneticisi import KlavyeKisayolYoneticisi
from .dialoglar import ParcaliOdemeDialog, IndirimDialog, MusteriSecDialog


class POSSatisEkrani(QWidget):
    """Ana POS satış ekranı widget'ı"""

    # Sinyaller
    satis_tamamlandi = pyqtSignal(dict)
    sepet_bekletildi = pyqtSignal(list)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.tema = TurkuazTema()
        self.hata_yoneticisi = POSHataYoneticisi(self)
        self.mevcut_musteri = None

        # Klavye kısayol yöneticisini oluştur
        self.klavye_yoneticisi = KlavyeKisayolYoneticisi(self)

        self.setupUI()
        self.sinyalleri_bagla()
        self.tema_uygula()

    def setupUI(self):
        """UI bileşenlerini oluşturur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Üst Bar
        self.ust_bar = UstBar()
        layout.addWidget(self.ust_bar)

        # Orta Alan (Sepet + Ödeme Paneli)
        self.orta_alan_olustur(layout)

        # Alt Şerit
        self.alt_serit = HizliIslemSeridi()
        layout.addWidget(self.alt_serit)

        # Ana widget stil
        self.setObjectName("POSSatisEkrani")

    def orta_alan_olustur(self, layout: QVBoxLayout):
        """Orta alanı oluşturur (sepet + ödeme paneli)"""
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Sol taraf - Sepet (%70)
        self.sepet_alani_olustur(self.splitter)

        # Sağ taraf - Ödeme Paneli (%30)
        self.odeme_paneli = OdemePaneli()
        self.odeme_paneli.setProperty("class", self.tema.widget_stil_sinifi_al("kart"))

        # Hızlı ürünler sekmesini ödeme paneline ekle
        self.hizli_urunler = HizliUrunlerSekmesi()
        self.odeme_paneli.tab_widget.removeTab(1)  # Boş sekmeyi kaldır
        self.odeme_paneli.tab_widget.addTab(self.hizli_urunler, "Hızlı Ürünler")

        self.splitter.addWidget(self.sepet_widget)
        self.splitter.addWidget(self.odeme_paneli)

        # Oranları ayarla (%70 - %30)
        self.splitter.setSizes([700, 300])

        layout.addWidget(self.splitter)

    def sepet_alani_olustur(self, parent):
        """Sepet alanını oluşturur"""
        from PyQt6.QtWidgets import QFrame

        self.sepet_widget = QFrame()
        self.sepet_widget.setProperty("class", self.tema.widget_stil_sinifi_al("kart"))
        sepet_layout = QVBoxLayout(self.sepet_widget)

        # Sepet tablosu
        self.sepet_modeli = SepetModeli()
        self.sepet_tablo = QTableView()
        self.sepet_tablo.setModel(self.sepet_modeli)

        # Tablo ayarları
        self.sepet_tablo.setAlternatingRowColors(True)
        self.sepet_tablo.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.sepet_tablo.verticalHeader().setVisible(False)

        sepet_layout.addWidget(self.sepet_tablo)

        # Sepet alt butonları (Not, İndirim, Kupon)
        self.sepet_alt_butonlari_olustur(sepet_layout)

    def sepet_alt_butonlari_olustur(self, layout: QVBoxLayout):
        """Sepet altındaki butonları oluşturur"""
        buton_layout = QHBoxLayout()

        from PyQt6.QtWidgets import QPushButton

        not_btn = QPushButton("Not Ekle")
        not_btn.setProperty("class", "sepet-alt-buton")
        not_btn.clicked.connect(self.not_ekle)

        indirim_btn = QPushButton("İndirim")
        indirim_btn.setProperty("class", "sepet-alt-buton")
        indirim_btn.clicked.connect(self.indirim_uygula)

        kupon_btn = QPushButton("Kupon")
        kupon_btn.setProperty("class", "sepet-alt-buton")
        kupon_btn.clicked.connect(self.kupon_uygula)

        buton_layout.addWidget(not_btn)
        buton_layout.addWidget(indirim_btn)
        buton_layout.addWidget(kupon_btn)

        layout.addLayout(buton_layout)

    def sinyalleri_bagla(self):
        """Widget sinyallerini bağlar"""
        # Üst bar sinyalleri
        self.ust_bar.barkod_girildi.connect(self.barkod_isle)
        self.ust_bar.musteri_sec_tiklandi.connect(self.musteri_sec)
        self.ust_bar.musteri_temizle_tiklandi.connect(self.musteri_temizle)

        # Ödeme paneli sinyalleri
        self.odeme_paneli.nakit_odeme_basildi.connect(self.nakit_odeme)
        self.odeme_paneli.kart_odeme_basildi.connect(self.kart_odeme)
        self.odeme_paneli.parcali_odeme_basildi.connect(self.parcali_odeme)
        self.odeme_paneli.acik_hesap_basildi.connect(self.acik_hesap_odeme)

        # Alt şerit sinyalleri
        self.alt_serit.beklet_basildi.connect(self.sepet_beklet)
        self.alt_serit.bekleyenler_basildi.connect(self.bekleyenler_goster)
        self.alt_serit.iade_basildi.connect(self.iade_islemi)
        self.alt_serit.iptal_basildi.connect(self.islem_iptal)
        self.alt_serit.fis_yazdir_basildi.connect(self.fis_yazdir)
        self.alt_serit.fatura_basildi.connect(self.fatura_olustur)

        # Sepet modeli sinyalleri
        self.sepet_modeli.sepet_degisti.connect(self.sepet_toplami_guncelle)

        # Hızlı ürünler sinyalleri
        self.hizli_urunler.hizli_urun_secildi.connect(self.barkod_isle)

        # Klavye kısayol sinyalleri
        self.klavye_yoneticisi.kisayol_tetiklendi.connect(self.klavye_kisayolu_isle)

    def tema_uygula(self):
        """Turkuaz temayı uygular"""
        if QApplication.instance():
            self.tema.temayı_uygula(QApplication.instance())

        # Widget'lara stil sınıfları uygula
        self.setProperty("class", "pos-ana-ekran")

        # Sepet tablosuna stil uygula
        if hasattr(self, "sepet_tablo"):
            self.sepet_tablo.setProperty("class", "sepet-tablo")

        # Splitter'a stil uygula
        if hasattr(self, "splitter"):
            self.splitter.setProperty("class", "ana-splitter")

        # Tüm alt widget'lara tema uygula
        self.alt_widget_temalarini_uygula()

    def alt_widget_temalarini_uygula(self):
        """Alt widget'lara tema uygular"""
        # Üst bar tema
        if hasattr(self, "ust_bar"):
            self.ust_bar.setObjectName("UstBar")

        # Ödeme paneli tema
        if hasattr(self, "odeme_paneli"):
            self.odeme_paneli.setObjectName("OdemePaneli")

        # Alt şerit tema
        if hasattr(self, "alt_serit"):
            self.alt_serit.setObjectName("HizliIslemSeridi")

        # Hızlı ürünler tema
        if hasattr(self, "hizli_urunler"):
            self.hizli_urunler.setObjectName("HizliUrunlerSekmesi")

        # Sepet widget tema
        if hasattr(self, "sepet_widget"):
            self.sepet_widget.setProperty("class", self.tema.widget_stil_sinifi_al("kart"))

        # Stil güncellemesi için repaint
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def keyPressEvent(self, event: QKeyEvent):
        """Klavye olaylarını işler"""
        # Önce klavye kısayol yöneticisine gönder
        if self.klavye_yoneticisi.olay_isle(event):
            # Kısayol işlendi, başka bir şey yapmaya gerek yok
            return

        # Kısayol değilse parent'a ilet (QLineEdit'ler için)
        super().keyPressEvent(event)

    def klavye_kisayolu_isle(self, kisayol_adi: str):
        """Klavye kısayolu işler"""
        if kisayol_adi == "barkod_odakla":
            self.ust_bar.barkod_odagini_ver()
        elif kisayol_adi == "nakit_odeme":
            self.nakit_odeme()
        elif kisayol_adi == "kart_odeme":
            self.kart_odeme()
        elif kisayol_adi == "parcali_odeme":
            self.parcali_odeme()
        elif kisayol_adi == "acik_hesap_odeme":
            self.acik_hesap_odeme()
        elif kisayol_adi == "sepet_beklet":
            self.sepet_beklet()
        elif kisayol_adi == "bekleyenler_goster":
            self.bekleyenler_goster()
        elif kisayol_adi == "iade_islemi":
            self.iade_islemi()
        elif kisayol_adi == "islem_iptal":
            self.islem_iptal()
        elif kisayol_adi == "satir_sil":
            self.secili_urunu_sil()
        elif kisayol_adi == "adet_artir":
            self.secili_urun_adet_artir()
        elif kisayol_adi == "adet_azalt":
            self.secili_urun_adet_azalt()

    def barkod_isle(self, barkod: str):
        """Barkod işleme"""
        # Burada ürün servisi çağrılacak
        # Şimdilik demo ürün ekle
        demo_urun = SepetOgesi(
            barkod=barkod,
            urun_adi=f"Demo Ürün {barkod}",
            adet=1,
            birim_fiyat=Decimal("10.50"),
            toplam_fiyat=Decimal("10.50"),
        )
        self.sepet_modeli.oge_ekle(demo_urun)

    def sepet_toplami_guncelle(self):
        """Sepet toplamını günceller"""
        toplam = self.sepet_modeli.genel_toplam()
        self.odeme_paneli.genel_toplami_guncelle(toplam)

    def nakit_odeme(self):
        """Nakit ödeme işlemi"""
        self.odeme_paneli.nakit_alanini_goster(True)

    def kart_odeme(self):
        """Kart ödeme işlemi"""
        # Kart ödeme servisi çağrılacak
        self.hata_yoneticisi.basari_goster("Kart ödeme işlemi başlatıldı")

    def parcali_odeme(self):
        """Parçalı ödeme işlemi"""
        toplam = self.sepet_modeli.genel_toplam()
        dialog = ParcaliOdemeDialog(toplam, self)
        if dialog.exec():
            nakit, kart = dialog.odeme_bilgilerini_al()
            self.hata_yoneticisi.basari_goster(f"Parçalı ödeme: {nakit:.2f}₺ nakit, {kart:.2f}₺ kart")

    def acik_hesap_odeme(self):
        """Açık hesap ödeme işlemi"""
        if not self.mevcut_musteri:
            self.hata_yoneticisi.hata_goster("dogrulama", "Açık hesap için müşteri seçmelisiniz!")
            return

        self.hata_yoneticisi.basari_goster("Açık hesap ödeme işlemi başlatıldı")

    def musteri_sec(self):
        """Müşteri seçim dialog'unu açar"""
        dialog = MusteriSecDialog(self)
        if dialog.exec():
            self.mevcut_musteri = dialog.secili_musteriyi_al()
            if self.mevcut_musteri:
                self.hata_yoneticisi.basari_goster(f"Müşteri seçildi: {self.mevcut_musteri['ad_soyad']}")

    def musteri_temizle(self):
        """Mevcut müşteriyi temizler"""
        self.mevcut_musteri = None
        self.hata_yoneticisi.basari_goster("Müşteri temizlendi")

    def sepet_beklet(self):
        """Sepeti bekletir"""
        if self.sepet_modeli.rowCount() > 0:
            # Sepet verilerini kaydet ve temizle
            bekletilen_sepet = self.sepet_modeli.sepet_ogeleri.copy()
            self.sepet_modeli.sepeti_temizle()
            self.sepet_bekletildi.emit(bekletilen_sepet)
            self.hata_yoneticisi.basari_goster("Sepet bekletildi")

    def islem_iptal(self):
        """İşlemi iptal eder"""
        if self.hata_yoneticisi.onay_iste("Mevcut işlemi iptal etmek istediğinizden emin misiniz?"):
            self.sepet_modeli.sepeti_temizle()
            self.odeme_paneli.odeme_alanini_temizle()
            self.mevcut_musteri = None

    def secili_urunu_sil(self):
        """Seçili ürünü sepetten siler"""
        secili_satir = self.sepet_tablo.currentIndex().row()
        if secili_satir >= 0:
            self.sepet_modeli.oge_sil(secili_satir)

    def secili_urun_adet_artir(self):
        """Seçili ürünün adetini artırır"""
        secili_satir = self.sepet_tablo.currentIndex().row()
        if secili_satir >= 0:
            self.sepet_modeli.adet_degistir(secili_satir, 1)

    def secili_urun_adet_azalt(self):
        """Seçili ürünün adetini azaltır"""
        secili_satir = self.sepet_tablo.currentIndex().row()
        if secili_satir >= 0:
            self.sepet_modeli.adet_degistir(secili_satir, -1)

    def not_ekle(self):
        """Sepete not ekler"""
        # Not ekleme dialog'u açılacak
        self.hata_yoneticisi.basari_goster("Not ekleme özelliği yakında gelecek")

    def indirim_uygula(self):
        """İndirim uygular"""
        toplam = self.sepet_modeli.genel_toplam()
        dialog = IndirimDialog(toplam, self)
        if dialog.exec():
            indirim_tutari, indirim_yuzde, kupon = dialog.indirim_bilgilerini_al()
            self.hata_yoneticisi.basari_goster(f"İndirim uygulandı: {indirim_tutari:.2f}₺")

    def kupon_uygula(self):
        """Kupon uygular"""
        self.indirim_uygula()  # Aynı dialog kullanılıyor

    def iade_islemi(self):
        """İade işlemi"""
        self.hata_yoneticisi.basari_goster("İade işlemi özelliği yakında gelecek")

    def bekleyenler_goster(self):
        """Bekletilen sepetler listesini gösterir"""
        self.hata_yoneticisi.basari_goster("Bekletilen sepetler listesi yakında gelecek")

    def fis_yazdir(self):
        """Fiş yazdırır"""
        if self.sepet_modeli.rowCount() == 0:
            self.hata_yoneticisi.hata_goster("dogrulama", "Yazdırılacak fiş bulunamadı!")
            return
        self.hata_yoneticisi.basari_goster("Fiş yazdırma işlemi başlatıldı")

    def fatura_olustur(self):
        """Fatura oluşturur"""
        if self.sepet_modeli.rowCount() == 0:
            self.hata_yoneticisi.hata_goster("dogrulama", "Fatura oluşturulacak ürün bulunamadı!")
            return
        self.hata_yoneticisi.basari_goster("Fatura oluşturma işlemi başlatıldı")
