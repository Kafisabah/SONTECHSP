# Version: 0.1.0
# Last Update: 2024-12-19
# Module: test_ozeti
# Description: POS yeni ekran tasarımı test özeti
# Changelog:
# - İlk oluşturma

"""
POS Yeni Ekran Tasarımı Test Özeti
"""

import sys
import os

# Proje kök dizinini path'e ekle
proje_kok = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.."))
sys.path.insert(0, proje_kok)

from PyQt6.QtWidgets import QApplication
from sontechsp.uygulama.arayuz.ekranlar.pos.turkuaz_tema import TurkuazTema
from sontechsp.uygulama.arayuz.ana_pencere import AnaPencere


def test_ozeti_calistir():
    """Test özetini çalıştırır"""
    print("POS Yeni Ekran Tasarımı Test Özeti")
    print("=" * 50)

    testler = []

    # 1. Tema Testi
    try:
        tema_gecerli = TurkuazTema.tema_dogrulama()
        testler.append(("Tema Doğrulama", tema_gecerli, None))
    except Exception as e:
        testler.append(("Tema Doğrulama", False, str(e)))

    # 2. QSS Stilleri Testi
    try:
        qss_uzunluk = len(TurkuazTema.qss_stilleri())
        qss_gecerli = qss_uzunluk > 5000  # En az 5000 karakter olmalı
        testler.append(("QSS Stilleri", qss_gecerli, f"{qss_uzunluk} karakter"))
    except Exception as e:
        testler.append(("QSS Stilleri", False, str(e)))

    # 3. Ana Pencere Entegrasyonu
    try:
        app = QApplication([])
        ana_pencere = AnaPencere()
        pos_secildi = ana_pencere.pos_menusunu_sec()
        testler.append(("Ana Pencere Entegrasyonu", pos_secildi, None))
    except Exception as e:
        testler.append(("Ana Pencere Entegrasyonu", False, str(e)))

    # 4. POS Yeni Ekran Yükleme
    try:
        yeni_ekran_yuklendi = ana_pencere.pos_yeni_ekran_yukle()
        testler.append(("POS Yeni Ekran Yükleme", yeni_ekran_yuklendi, None))
    except Exception as e:
        testler.append(("POS Yeni Ekran Yükleme", False, str(e)))

    # Sonuçları yazdır
    basarili_sayisi = 0
    for test_adi, basarili, detay in testler:
        durum = "✓ BAŞARILI" if basarili else "✗ BAŞARISIZ"
        detay_str = f" ({detay})" if detay else ""
        print(f"{test_adi:.<30} {durum}{detay_str}")
        if basarili:
            basarili_sayisi += 1

    print(f"\nToplam: {len(testler)} test, {basarili_sayisi} başarılı")
    print(f"Başarı oranı: {basarili_sayisi/len(testler)*100:.1f}%")

    return basarili_sayisi == len(testler)


if __name__ == "__main__":
    test_ozeti_calistir()
