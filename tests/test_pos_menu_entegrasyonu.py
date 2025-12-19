# Version: 0.1.0
# Last Update: 2024-12-19
# Module: test_pos_menu_entegrasyonu
# Description: POS menü entegrasyonu ve durum yönetimi özellik testleri
# Changelog:
# - İlk oluşturma

"""
POS Menü Entegrasyonu Testleri

Feature: pos-yeni-ekran-tasarimi, Property 10: Menü Entegrasyonu ve Durum Yönetimi
Validates: Gereksinim 12.3, 12.5
"""

import pytest
import sys
import os
import json
from decimal import Decimal

# Proje kök dizinini path'e ekle
proje_kok = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, proje_kok)

from PyQt6.QtWidgets import QApplication
from sontechsp.uygulama.arayuz.ana_pencere import AnaPencere
from sontechsp.uygulama.arayuz.ekranlar.pos.sepet_modeli import SepetOgesi


@pytest.fixture(scope="module")
def qapp():
    """QApplication fixture"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def ana_pencere(qapp):
    """Ana pencere fixture"""
    pencere = AnaPencere()
    yield pencere
    pencere.close()


class TestMenuEntegrasyonu:
    """Menü entegrasyonu testleri"""

    def test_pos_menu_secimi(self, ana_pencere):
        """
        Test: POS menü seçimi başarılı olmalı
        Feature: pos-yeni-ekran-tasarimi, Property 10
        """
        # POS menüsünü seç
        basarili = ana_pencere.pos_menusunu_sec()

        # Doğrulama
        assert basarili, "POS menü seçimi başarısız"
        assert ana_pencere.aktif_modul_kodunu_al() == "pos", "Aktif modül POS değil"

    def test_menu_gecisleri_durum_koruma(self, ana_pencere):
        """
        Test: Menü geçişlerinde ekran durumu korunmalı
        Feature: pos-yeni-ekran-tasarimi, Property 10
        Validates: Gereksinim 12.3
        """
        # POS menüsünü seç
        ana_pencere.pos_menusunu_sec()
        pos_ekrani_1 = ana_pencere.icerik_alani.currentWidget()

        # Başka bir modüle geç (stok)
        for i in range(ana_pencere.modul_menusu.count()):
            item = ana_pencere.modul_menusu.item(i)
            if item.data(0x0100) == "stok":  # Qt.ItemDataRole.UserRole
                ana_pencere.modul_menusu.setCurrentRow(i)
                break

        # Tekrar POS'a dön
        ana_pencere.pos_menusunu_sec()
        pos_ekrani_2 = ana_pencere.icerik_alani.currentWidget()

        # Doğrulama: Aynı ekran instance'ı olmalı (durum korundu)
        assert pos_ekrani_1 is pos_ekrani_2, "POS ekran durumu korunmadı"

    def test_pos_yeni_ekran_yukleme(self, ana_pencere):
        """
        Test: POS yeni ekran manuel yükleme başarılı olmalı
        Feature: pos-yeni-ekran-tasarimi, Property 10
        """
        # Yeni ekranı yükle
        basarili = ana_pencere.pos_yeni_ekran_yukle()

        # Doğrulama
        assert basarili, "POS yeni ekran yükleme başarısız"
        assert "pos" in ana_pencere._modul_ekranlari, "POS ekranı cache'de yok"

    def test_sepet_verilerini_kaydetme(self, ana_pencere, tmp_path):
        """
        Test: POS ekranı kapatıldığında sepet verileri güvenli şekilde saklanmalı
        Feature: pos-yeni-ekran-tasarimi, Property 10
        Validates: Gereksinim 12.5
        """
        # POS menüsünü seç ve yeni ekranı yükle
        ana_pencere.pos_menusunu_sec()
        ana_pencere.pos_yeni_ekran_yukle()

        # POS ekranını al
        pos_wrapper = ana_pencere._modul_ekranlari.get("pos")
        if pos_wrapper and hasattr(pos_wrapper, "pos_ekrani"):
            pos_ekrani = pos_wrapper.pos_ekrani

            # Sepete test ürünleri ekle
            if hasattr(pos_ekrani, "sepet_modeli"):
                test_ogeler = [
                    SepetOgesi("123456", "Test Ürün 1", 2, Decimal("15.50"), Decimal("31.00")),
                    SepetOgesi("789012", "Test Ürün 2", 1, Decimal("25.75"), Decimal("25.75")),
                ]

                for oge in test_ogeler:
                    pos_ekrani.sepet_modeli.oge_ekle(oge)

                # Sepet verilerini kaydet
                ana_pencere._pos_sepet_verilerini_kaydet()

                # Doğrulama: Backup dosyası oluşturuldu mu?
                backup_dosyasi = os.path.join(os.getcwd(), "temp", "pos_sepet_backup.json")
                assert os.path.exists(backup_dosyasi), "Sepet backup dosyası oluşturulmadı"

                # Backup içeriğini kontrol et
                with open(backup_dosyasi, "r", encoding="utf-8") as f:
                    backup_verisi = json.load(f)

                assert "sepet_verileri" in backup_verisi, "Backup'ta sepet verileri yok"
                assert len(backup_verisi["sepet_verileri"]) == 2, "Sepet ürün sayısı yanlış"
                assert backup_verisi["sepet_verileri"][0]["barkod"] == "123456", "İlk ürün barkodu yanlış"

                # Temizlik
                if os.path.exists(backup_dosyasi):
                    os.remove(backup_dosyasi)
        else:
            pytest.skip("POS yeni ekran yüklenemedi, test atlandı")

    def test_modul_ekranlarini_temizleme(self, ana_pencere):
        """
        Test: Tüm modül ekranları temizlenebilmeli
        Feature: pos-yeni-ekran-tasarimi, Property 10
        """
        # POS menüsünü seç
        ana_pencere.pos_menusunu_sec()

        # Başlangıç durumu
        baslangic_sayisi = len(ana_pencere._modul_ekranlari)
        assert baslangic_sayisi > 0, "Hiç modül ekranı yüklenmemiş"

        # Temizle
        ana_pencere._modul_ekranlarini_temizle()

        # Doğrulama
        assert len(ana_pencere._modul_ekranlari) == 0, "Modül ekranları temizlenmedi"


class TestMenuEntegrasyonuOzellikTabanli:
    """Özellik tabanlı menü entegrasyonu testleri"""

    def test_property_menu_gecisleri_durum_koruma(self, ana_pencere):
        """
        Property Test: Herhangi bir menü geçişinde sistem ekran durumunu korumalı
        Feature: pos-yeni-ekran-tasarimi, Property 10
        Validates: Gereksinim 12.3

        For any menu transition, the system should preserve screen state
        """
        # POS menüsünü seç
        ana_pencere.pos_menusunu_sec()
        ilk_pos_ekrani = ana_pencere.icerik_alani.currentWidget()

        # Tüm modülleri dolaş
        modul_sayisi = ana_pencere.modul_menusu.count()
        for i in range(modul_sayisi):
            # Başka bir modüle geç
            ana_pencere.modul_menusu.setCurrentRow(i)

            # POS'a geri dön
            ana_pencere.pos_menusunu_sec()
            son_pos_ekrani = ana_pencere.icerik_alani.currentWidget()

            # Doğrulama: Her zaman aynı instance olmalı
            assert ilk_pos_ekrani is son_pos_ekrani, f"Modül {i} geçişinden sonra POS ekran durumu korunmadı"

    def test_property_sepet_verilerini_kaydetme_guvenli(self, ana_pencere):
        """
        Property Test: Herhangi bir sepet durumunda kapatma güvenli olmalı
        Feature: pos-yeni-ekran-tasarimi, Property 10
        Validates: Gereksinim 12.5

        For any cart state, closing should safely save data
        """
        # POS menüsünü seç ve yeni ekranı yükle
        ana_pencere.pos_menusunu_sec()
        ana_pencere.pos_yeni_ekran_yukle()

        # Farklı sepet durumlarını test et
        sepet_durumlari = [
            [],  # Boş sepet
            [SepetOgesi("111", "Ürün 1", 1, Decimal("10"), Decimal("10"))],  # Tek ürün
            [
                SepetOgesi("222", "Ürün 2", 5, Decimal("20"), Decimal("100")),
                SepetOgesi("333", "Ürün 3", 2, Decimal("15"), Decimal("30")),
            ],  # Çoklu ürün
        ]

        for sepet_durumu in sepet_durumlari:
            # POS ekranını al
            pos_wrapper = ana_pencere._modul_ekranlari.get("pos")
            if pos_wrapper and hasattr(pos_wrapper, "pos_ekrani"):
                pos_ekrani = pos_wrapper.pos_ekrani

                if hasattr(pos_ekrani, "sepet_modeli"):
                    # Sepeti temizle
                    pos_ekrani.sepet_modeli.sepeti_temizle()

                    # Test durumunu ekle
                    for oge in sepet_durumu:
                        pos_ekrani.sepet_modeli.oge_ekle(oge)

                    # Kaydetme işlemi hata vermemeli
                    try:
                        ana_pencere._pos_sepet_verilerini_kaydet()
                        kayit_basarili = True
                    except Exception:
                        kayit_basarili = False

                    assert kayit_basarili, f"Sepet durumu {len(sepet_durumu)} ürün için kaydetme başarısız"

                    # Temizlik
                    backup_dosyasi = os.path.join(os.getcwd(), "temp", "pos_sepet_backup.json")
                    if os.path.exists(backup_dosyasi):
                        os.remove(backup_dosyasi)
            else:
                pytest.skip("POS yeni ekran yüklenemedi, test atlandı")
                break


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
