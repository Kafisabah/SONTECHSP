# Version: 0.1.0
# Last Update: 2024-12-19
# Module: tema_test
# Description: Turkuaz tema test ve doğrulama fonksiyonları
# Changelog:
# - İlk oluşturma

"""
Tema Test - Turkuaz tema doğrulama ve test fonksiyonları
"""

import sys
import os

# Proje kök dizinini path'e ekle
proje_kok = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))
sys.path.insert(0, proje_kok)

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt
from sontechsp.uygulama.arayuz.ekranlar.pos.turkuaz_tema import TurkuazTema


def tema_dogrulama_testi():
    """Tema doğrulama testini çalıştırır"""
    print("Turkuaz Tema Doğrulama Testi")
    print("=" * 40)

    # Tema renk doğrulaması
    tema_gecerli = TurkuazTema.tema_dogrulama()
    print(f"Tema renk doğrulaması: {'✓ BAŞARILI' if tema_gecerli else '✗ BAŞARISIZ'}")

    # Renk listesi
    renkler = TurkuazTema.tema_renklerini_al()
    print(f"Toplam renk sayısı: {len(renkler)}")

    for renk_adi, renk_kodu in renkler.items():
        print(f"  {renk_adi}: {renk_kodu}")

    # Stil sınıfları testi
    print("\nStil Sınıfları Testi:")
    buton_turleri = ["odeme", "hizli_islem", "hizli_urun", "iptal"]
    for tur in buton_turleri:
        stil = TurkuazTema.buton_stil_sinifi_al(tur)
        print(f"  {tur}: {stil if stil else 'Bulunamadı'}")

    widget_turleri = ["kart", "nakit_alan"]
    for tur in widget_turleri:
        stil = TurkuazTema.widget_stil_sinifi_al(tur)
        print(f"  {tur}: {stil if stil else 'Bulunamadı'}")

    # QSS stilleri testi
    print(f"\nQSS Stilleri Uzunluğu: {len(TurkuazTema.qss_stilleri())} karakter")

    print("\nTema doğrulama testi tamamlandı!")
    return tema_gecerli


class TemaTestWidget(QWidget):
    """Tema test widget'ı - basit bileşen testleri"""

    def __init__(self):
        super().__init__()
        self.tema = TurkuazTema()
        self.setupUI()
        self.tema_uygula()

    def setupUI(self):
        """Test UI'sını oluşturur"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Başlık
        baslik = QLabel("Turkuaz Tema Test Ekranı")
        baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baslik.setObjectName("genel-toplam")
        layout.addWidget(baslik)

        # Buton testleri
        self.buton_testleri_olustur(layout)

        # Frame testleri
        self.frame_testleri_olustur(layout)

    def buton_testleri_olustur(self, layout: QVBoxLayout):
        """Buton testlerini oluşturur"""
        buton_frame = QFrame()
        buton_frame.setProperty("class", self.tema.widget_stil_sinifi_al("kart"))
        buton_layout = QVBoxLayout(buton_frame)

        buton_layout.addWidget(QLabel("Buton Testleri:"))

        # Farklı buton türleri
        buton_satir1 = QHBoxLayout()

        odeme_btn = QPushButton("Ödeme Butonu")
        odeme_btn.setProperty("class", self.tema.buton_stil_sinifi_al("odeme"))

        hizli_islem_btn = QPushButton("Hızlı İşlem")
        hizli_islem_btn.setProperty("class", self.tema.buton_stil_sinifi_al("hizli_islem"))

        hizli_urun_btn = QPushButton("Hızlı Ürün")
        hizli_urun_btn.setProperty("class", self.tema.buton_stil_sinifi_al("hizli_urun"))

        buton_satir1.addWidget(odeme_btn)
        buton_satir1.addWidget(hizli_islem_btn)
        buton_satir1.addWidget(hizli_urun_btn)

        # İkinci satır
        buton_satir2 = QHBoxLayout()

        normal_btn = QPushButton("Normal Buton")

        iptal_btn = QPushButton("İptal Butonu")
        iptal_btn.setProperty("class", self.tema.buton_stil_sinifi_al("iptal"))

        disabled_btn = QPushButton("Devre Dışı")
        disabled_btn.setEnabled(False)

        buton_satir2.addWidget(normal_btn)
        buton_satir2.addWidget(iptal_btn)
        buton_satir2.addWidget(disabled_btn)

        buton_layout.addLayout(buton_satir1)
        buton_layout.addLayout(buton_satir2)
        layout.addWidget(buton_frame)

    def frame_testleri_olustur(self, layout: QVBoxLayout):
        """Frame testlerini oluşturur"""
        frame_satir = QHBoxLayout()

        # Kart frame
        kart_frame = QFrame()
        kart_frame.setProperty("class", self.tema.widget_stil_sinifi_al("kart"))
        kart_layout = QVBoxLayout(kart_frame)
        kart_layout.addWidget(QLabel("Kart Frame"))
        kart_layout.addWidget(QLabel("Bu bir kart frame örneğidir"))

        # Nakit alan frame
        nakit_frame = QFrame()
        nakit_frame.setProperty("class", self.tema.widget_stil_sinifi_al("nakit_alan"))
        nakit_layout = QVBoxLayout(nakit_frame)
        nakit_layout.addWidget(QLabel("Nakit Alan Frame"))
        nakit_layout.addWidget(QLabel("Bu nakit ödeme alanıdır"))

        frame_satir.addWidget(kart_frame)
        frame_satir.addWidget(nakit_frame)
        layout.addLayout(frame_satir)

        # Toplam göstergesi testi
        toplam_label = QLabel("1,234.56 ₺")
        toplam_label.setObjectName("genel-toplam")
        toplam_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(toplam_label)

    def tema_uygula(self):
        """Temayı uygular"""
        if QApplication.instance():
            self.tema.temayı_uygula(QApplication.instance())

        # Widget'ı güncelle
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


def tema_test_uygulamasi_calistir():
    """Tema test uygulamasını çalıştırır"""
    app = QApplication(sys.argv)

    # Doğrulama testini çalıştır
    tema_dogrulama_testi()

    # Test widget'ını göster
    test_widget = TemaTestWidget()
    test_widget.setWindowTitle("Turkuaz Tema Test")
    test_widget.resize(800, 600)
    test_widget.show()

    return app.exec()


if __name__ == "__main__":
    # Sadece doğrulama testini çalıştır (GUI olmadan)
    tema_dogrulama_testi()
