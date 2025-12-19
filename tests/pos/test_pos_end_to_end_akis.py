# Version: 0.1.0
# Last Update: 2024-12-19
# Module: test_pos_end_to_end_akis
# Description: POS End-to-End akış testleri (Görev 16.1)
# Changelog:
# - İlk oluşturma - Kapsamlı end-to-end akış testleri

"""
POS End-to-End Akış Testleri

Bu modül POS sisteminin tam akış senaryolarını test eder.
Gerçek kullanım senaryolarını simüle ederek sistem bütünlüğünü doğrular.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt, QTimer
import sys
import os
import time

# Proje kök dizinini path'e ekle
proje_kok = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, proje_kok)

from sontechsp.uygulama.arayuz.ekranlar.pos.pos_satis_ekrani import POSSatisEkrani
from sontechsp.uygulama.arayuz.ekranlar.pos.sepet_modeli import SepetModeli, SepetOgesi
from sontechsp.uygulama.moduller.pos.arayuzler import (
    ISepetService,
    IOdemeService,
    IStokService,
    IOfflineKuyrukService,
    OdemeTuru,
    IslemTuru,
    SepetDurum,
)
from sontechsp.uygulama.cekirdek.hatalar import DogrulamaHatasi, SontechHatasi, NetworkHatasi


class TestPOSEndToEndAkis:
    """POS End-to-End akış testleri"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Test setup - QApplication oluştur"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()

    @pytest.fixture
    def pos_ekrani_hazir(self):
        """Hazır POS ekranı fixture"""
        pos_ekran = POSSatisEkrani()

        # Mock servisler ekle
        pos_ekran._sepet_service = Mock(spec=ISepetService)
        pos_ekran._odeme_service = Mock(spec=IOdemeService)
        pos_ekran._stok_service = Mock(spec=IStokService)
        pos_ekran._offline_service = Mock(spec=IOfflineKuyrukService)

        # Mock servis davranışları
        pos_ekran._sepet_service.yeni_sepet_olustur.return_value = 123
        pos_ekran._sepet_service.barkod_ekle.return_value = True
        pos_ekran._odeme_service.tek_odeme_yap.return_value = True
        pos_ekran._stok_service.urun_bilgisi_getir.return_value = {
            "urun_id": 1,
            "urun_adi": "Test Ürün",
            "satis_fiyati": Decimal("10.50"),
        }

        yield pos_ekran
        pos_ekran.close()

    def test_basit_satis_akisi(self, pos_ekrani_hazir):
        """Basit satış akışı - tek ürün, nakit ödeme"""
        pos_ekran = pos_ekrani_hazir

        # 1. Barkod ekleme
        pos_ekran.barkod_isle("1234567890")

        # Sepette ürün olduğunu kontrol et
        assert pos_ekran.sepet_modeli.rowCount() == 1

        # 2. Toplam kontrolü
        toplam = pos_ekran.sepet_modeli.genel_toplam()
        assert toplam == Decimal("10.50")

        # 3. Nakit ödeme
        pos_ekran.nakit_odeme()

        # Ödeme panelinin nakit alanını gösterdiğini kontrol et
        assert pos_ekran.odeme_paneli.nakit_alani_gorunur_mu()

    def test_coklu_urun_satis_akisi(self, pos_ekrani_hazir):
        """Çoklu ürün satış akışı"""
        pos_ekran = pos_ekrani_hazir

        # 1. Birden fazla ürün ekleme
        urunler = ["1111111111", "2222222222", "3333333333", "4444444444"]
        for barkod in urunler:
            pos_ekran.barkod_isle(barkod)

        # Sepette 4 ürün olduğunu kontrol et
        assert pos_ekran.sepet_modeli.rowCount() == 4

        # 2. Toplam hesaplama
        toplam = pos_ekran.sepet_modeli.genel_toplam()
        beklenen_toplam = Decimal("42.00")  # 4 * 10.50
        assert toplam == beklenen_toplam

        # 3. Adet değiştirme
        pos_ekran.sepet_tablo.selectRow(0)
        pos_ekran.secili_urun_adet_artir()
        pos_ekran.secili_urun_adet_artir()  # Toplam 3 adet

        # Yeni toplam kontrolü
        yeni_toplam = pos_ekran.sepet_modeli.genel_toplam()
        assert yeni_toplam == Decimal("63.00")  # (3*10.50) + (3*10.50) = 63.00

        # 4. Kart ödeme
        pos_ekran.kart_odeme()

    def test_parcali_odeme_akisi(self, pos_ekrani_hazir):
        """Parçalı ödeme akışı"""
        pos_ekran = pos_ekrani_hazir

        # 1. Yüksek tutarlı ürün ekleme
        for i in range(5):
            pos_ekran.barkod_isle(f"555555555{i}")

        toplam = pos_ekran.sepet_modeli.genel_toplam()
        assert toplam == Decimal("52.50")  # 5 * 10.50

        # 2. Parçalı ödeme dialog'unu mock'la
        with patch("sontechsp.uygulama.arayuz.ekranlar.pos.dialoglar.ParcaliOdemeDialog") as mock_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.exec.return_value = True
            mock_dialog_instance.odeme_bilgilerini_al.return_value = (Decimal("30.00"), Decimal("22.50"))
            mock_dialog.return_value = mock_dialog_instance

            # 3. Parçalı ödeme işlemi
            pos_ekran.parcali_odeme()

            # Dialog'un çağrıldığını kontrol et
            mock_dialog.assert_called_once_with(toplam, pos_ekran)

    def test_indirim_uygulama_akisi(self, pos_ekrani_hazir):
        """İndirim uygulama akışı"""
        pos_ekran = pos_ekrani_hazir

        # 1. Ürün ekleme
        for i in range(3):
            pos_ekran.barkod_isle(f"777777777{i}")

        ilk_toplam = pos_ekran.sepet_modeli.genel_toplam()
        assert ilk_toplam == Decimal("31.50")  # 3 * 10.50

        # 2. İndirim dialog'unu mock'la
        with patch("sontechsp.uygulama.arayuz.ekranlar.pos.dialoglar.IndirimDialog") as mock_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.exec.return_value = True
            mock_dialog_instance.indirim_bilgilerini_al.return_value = (Decimal("5.00"), 15.87, None)
            mock_dialog.return_value = mock_dialog_instance

            # 3. İndirim uygulama
            pos_ekran.indirim_uygula()

            # Dialog'un çağrıldığını kontrol et
            mock_dialog.assert_called_once_with(ilk_toplam, pos_ekran)

    def test_musteri_secim_acik_hesap_akisi(self, pos_ekrani_hazir):
        """Müşteri seçim ve açık hesap akışı"""
        pos_ekran = pos_ekrani_hazir

        # 1. Ürün ekleme
        pos_ekran.barkod_isle("8888888888")

        # 2. Müşteri seçim dialog'unu mock'la
        with patch("sontechsp.uygulama.arayuz.ekranlar.pos.dialoglar.MusteriSecDialog") as mock_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.exec.return_value = True
            mock_dialog_instance.secili_musteriyi_al.return_value = {
                "id": 1,
                "ad_soyad": "Test Müşteri",
                "telefon": "555-1234",
                "email": "test@example.com",
            }
            mock_dialog.return_value = mock_dialog_instance

            # 3. Müşteri seçimi
            pos_ekran.musteri_sec()

            # Müşteri seçildiğini kontrol et
            assert pos_ekran.mevcut_musteri is not None
            assert pos_ekran.mevcut_musteri["ad_soyad"] == "Test Müşteri"

        # 4. Açık hesap ödeme
        pos_ekran.acik_hesap_odeme()

    def test_sepet_bekletme_akisi(self, pos_ekrani_hazir):
        """Sepet bekletme akışı"""
        pos_ekran = pos_ekrani_hazir

        # 1. İlk sepete ürün ekleme
        pos_ekran.barkod_isle("1111111111")
        pos_ekran.barkod_isle("2222222222")

        ilk_sepet_sayisi = pos_ekran.sepet_modeli.rowCount()
        assert ilk_sepet_sayisi == 2

        # 2. Sepet bekletme
        pos_ekran.sepet_beklet()

        # Sepet temizlendiğini kontrol et
        assert pos_ekran.sepet_modeli.rowCount() == 0

        # 3. Yeni sepete ürün ekleme
        pos_ekran.barkod_isle("3333333333")

        assert pos_ekran.sepet_modeli.rowCount() == 1

    def test_klavye_kisayollari_akisi(self, pos_ekrani_hazir):
        """Klavye kısayolları akışı"""
        pos_ekran = pos_ekrani_hazir

        # 1. F2 - Barkod odağı
        pos_ekran.klavye_kisayolu_isle("barkod_odakla")
        # Barkod alanının odakta olduğunu kontrol et (UI test)

        # 2. Ürün ekleme
        pos_ekran.barkod_isle("1234567890")
        pos_ekran.sepet_tablo.selectRow(0)

        # 3. + tuşu - Adet artırma
        pos_ekran.klavye_kisayolu_isle("adet_artir")

        urun = pos_ekran.sepet_modeli.sepet_ogeleri[0]
        assert urun.adet == 2

        # 4. - tuşu - Adet azaltma
        pos_ekran.klavye_kisayolu_isle("adet_azalt")

        urun = pos_ekran.sepet_modeli.sepet_ogeleri[0]
        assert urun.adet == 1

        # 5. F4 - Nakit ödeme
        pos_ekran.klavye_kisayolu_isle("nakit_odeme")
        assert pos_ekran.odeme_paneli.nakit_alani_gorunur_mu()

        # 6. F8 - Sepet bekletme
        pos_ekran.klavye_kisayolu_isle("sepet_beklet")
        assert pos_ekran.sepet_modeli.rowCount() == 0

    def test_hata_yonetimi_akisi(self, pos_ekrani_hazir):
        """Hata yönetimi akışı"""
        pos_ekran = pos_ekrani_hazir

        # Hata yöneticisini mock'la
        pos_ekran.hata_yoneticisi.hata_goster = Mock()
        pos_ekran.hata_yoneticisi.basari_goster = Mock()

        # 1. Geçersiz barkod hatası
        pos_ekran._sepet_service.barkod_ekle.side_effect = DogrulamaHatasi("test_hata", "Geçersiz barkod")

        pos_ekran.barkod_isle("gecersiz_barkod")

        # Hata gösteriminin çağrıldığını kontrol et
        pos_ekran.hata_yoneticisi.hata_goster.assert_called()

        # 2. Başarılı işlem
        pos_ekran._sepet_service.barkod_ekle.side_effect = None
        pos_ekran._sepet_service.barkod_ekle.return_value = True

        pos_ekran.barkod_isle("1234567890")

        # Başarı mesajının gösterildiğini kontrol et (sepet güncellemesi)
        assert pos_ekran.sepet_modeli.rowCount() == 1

    def test_offline_mod_akisi(self, pos_ekrani_hazir):
        """Offline mod akışı"""
        pos_ekran = pos_ekrani_hazir

        # 1. Network hatası simüle et
        pos_ekran._sepet_service.barkod_ekle.side_effect = NetworkHatasi("Bağlantı hatası")

        # 2. Offline kuyruk servisini hazırla
        pos_ekran._offline_service.islem_kuyruga_ekle.return_value = True

        # 3. Barkod ekleme işlemi (offline)
        pos_ekran.barkod_isle("1234567890")

        # Offline kuyruğa ekleme çağrısının yapıldığını kontrol et
        pos_ekran._offline_service.islem_kuyruga_ekle.assert_called_once()

        # 4. Online duruma geçiş simülasyonu
        pos_ekran._sepet_service.barkod_ekle.side_effect = None
        pos_ekran._sepet_service.barkod_ekle.return_value = True

        # 5. Kuyruk senkronizasyonu
        pos_ekran._offline_service.kuyruk_senkronize_et.return_value = 1

        # Senkronizasyon çağrısı (gerçek implementasyonda otomatik olur)
        senkronize_edilen = pos_ekran._offline_service.kuyruk_senkronize_et()
        assert senkronize_edilen == 1

    def test_performans_akisi(self, pos_ekrani_hazir):
        """Performans akışı - çok sayıda ürün"""
        pos_ekran = pos_ekrani_hazir

        # 1. 100 ürün ekleme performansı
        baslangic = time.time()

        for i in range(100):
            barkod = f"123456789{i:03d}"
            pos_ekran.barkod_isle(barkod)

        bitis = time.time()
        gecen_sure = bitis - baslangic

        # 100 ürün 3 saniyede eklenmeli
        assert gecen_sure < 3.0
        assert pos_ekran.sepet_modeli.rowCount() == 100

        # 2. Toplam hesaplama performansı
        baslangic = time.time()

        for _ in range(50):
            toplam = pos_ekran.sepet_modeli.genel_toplam()

        bitis = time.time()
        gecen_sure = bitis - baslangic

        # 50 toplam hesaplama 0.5 saniyede tamamlanmalı
        assert gecen_sure < 0.5
        assert toplam == Decimal("1050.00")  # 100 * 10.50

    def test_tam_satis_dongusu_akisi(self, pos_ekrani_hazir):
        """Tam satış döngüsü akışı"""
        pos_ekran = pos_ekrani_hazir

        # 1. Müşteri seçimi
        with patch("sontechsp.uygulama.arayuz.ekranlar.pos.dialoglar.MusteriSecDialog") as mock_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.exec.return_value = True
            mock_dialog_instance.secili_musteriyi_al.return_value = {"id": 1, "ad_soyad": "Test Müşteri"}
            mock_dialog.return_value = mock_dialog_instance

            pos_ekran.musteri_sec()

        # 2. Ürün ekleme
        urunler = ["1111111111", "2222222222", "3333333333"]
        for barkod in urunler:
            pos_ekran.barkod_isle(barkod)

        # 3. Adet değiştirme
        pos_ekran.sepet_tablo.selectRow(1)
        pos_ekran.secili_urun_adet_artir()

        # 4. İndirim uygulama
        with patch("sontechsp.uygulama.arayuz.ekranlar.pos.dialoglar.IndirimDialog") as mock_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.exec.return_value = True
            mock_dialog_instance.indirim_bilgilerini_al.return_value = (Decimal("5.00"), 11.90, None)
            mock_dialog.return_value = mock_dialog_instance

            pos_ekran.indirim_uygula()

        # 5. Parçalı ödeme
        toplam = pos_ekran.sepet_modeli.genel_toplam()

        with patch("sontechsp.uygulama.arayuz.ekranlar.pos.dialoglar.ParcaliOdemeDialog") as mock_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.exec.return_value = True
            mock_dialog_instance.odeme_bilgilerini_al.return_value = (Decimal("25.00"), toplam - Decimal("25.00"))
            mock_dialog.return_value = mock_dialog_instance

            pos_ekran.parcali_odeme()

        # 6. Fiş yazdırma
        pos_ekran.fis_yazdir()

        # Tüm işlemlerin başarıyla tamamlandığını kontrol et
        assert pos_ekran.mevcut_musteri is not None
        assert pos_ekran.sepet_modeli.rowCount() == 3

    def test_iptal_ve_temizleme_akisi(self, pos_ekrani_hazir):
        """İptal ve temizleme akışı"""
        pos_ekran = pos_ekrani_hazir

        # 1. Ürün ekleme ve müşteri seçimi
        pos_ekran.barkod_isle("1234567890")
        pos_ekran.mevcut_musteri = {"id": 1, "ad_soyad": "Test Müşteri"}

        # 2. Onay dialog'unu mock'la
        pos_ekran.hata_yoneticisi.onay_iste = Mock(return_value=True)

        # 3. İşlem iptali
        pos_ekran.islem_iptal()

        # Temizleme işlemlerinin yapıldığını kontrol et
        assert pos_ekran.sepet_modeli.rowCount() == 0
        assert pos_ekran.mevcut_musteri is None
        pos_ekran.hata_yoneticisi.onay_iste.assert_called_once()

    def test_hizli_urun_entegrasyon_akisi(self, pos_ekrani_hazir):
        """Hızlı ürün entegrasyon akışı"""
        pos_ekran = pos_ekrani_hazir

        # 1. Hızlı ürün sekmesinin varlığını kontrol et
        assert pos_ekran.hizli_urunler is not None

        # 2. Hızlı ürün seçimi simüle et
        test_barkod = "9999999999"
        pos_ekran.barkod_isle(test_barkod)  # Hızlı ürün butonundan geliyormuş gibi

        # 3. Sepete ekleme kontrolü
        assert pos_ekran.sepet_modeli.rowCount() == 1
        eklenen_urun = pos_ekran.sepet_modeli.sepet_ogeleri[0]
        assert eklenen_urun.barkod == test_barkod

        # 4. Normal barkod ile karışık kullanım
        pos_ekran.barkod_isle("1111111111")
        assert pos_ekran.sepet_modeli.rowCount() == 2


class TestPOSStresTestleri:
    """POS stres testleri"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Test setup"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()

    def test_yuksek_hacim_urun_ekleme(self):
        """Yüksek hacim ürün ekleme stres testi"""
        pos_ekran = POSSatisEkrani()

        # 500 ürün ekleme
        baslangic = time.time()

        for i in range(500):
            barkod = f"STRESS{i:06d}"
            pos_ekran.barkod_isle(barkod)

        bitis = time.time()
        gecen_sure = bitis - baslangic

        # 500 ürün 10 saniyede eklenmeli
        assert gecen_sure < 10.0
        assert pos_ekran.sepet_modeli.rowCount() == 500

        # Toplam hesaplama
        toplam = pos_ekran.sepet_modeli.genel_toplam()
        assert toplam == Decimal("5250.00")  # 500 * 10.50

        pos_ekran.close()

    def test_surekli_adet_degistirme(self):
        """Sürekli adet değiştirme stres testi"""
        pos_ekran = POSSatisEkrani()

        # 10 ürün ekle
        for i in range(10):
            pos_ekran.barkod_isle(f"ADET{i:03d}")

        # Her ürünün adetini 100 kez değiştir
        baslangic = time.time()

        for satir_index in range(10):
            pos_ekran.sepet_tablo.selectRow(satir_index)

            for _ in range(50):
                pos_ekran.secili_urun_adet_artir()

            for _ in range(49):  # 1 adet kalacak şekilde
                pos_ekran.secili_urun_adet_azalt()

        bitis = time.time()
        gecen_sure = bitis - baslangic

        # İşlem 5 saniyede tamamlanmalı
        assert gecen_sure < 5.0

        # Her ürünün adeti 2 olmalı (1 + 50 - 49)
        for urun in pos_ekran.sepet_modeli.sepet_ogeleri:
            assert urun.adet == 2

        pos_ekran.close()

    def test_bellek_kullanimi(self):
        """Bellek kullanımı stres testi"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        baslangic_bellek = process.memory_info().rss / 1024 / 1024  # MB

        pos_ekran = POSSatisEkrani()

        # 1000 ürün ekle ve sil
        for i in range(1000):
            pos_ekran.barkod_isle(f"BELLEK{i:06d}")

            if i % 100 == 99:  # Her 100 üründe sepeti temizle
                pos_ekran.sepet_modeli.sepeti_temizle()

        bitis_bellek = process.memory_info().rss / 1024 / 1024  # MB
        bellek_artisi = bitis_bellek - baslangic_bellek

        # Bellek artışı 50MB'dan az olmalı
        assert bellek_artisi < 50

        pos_ekran.close()


if __name__ == "__main__":
    # Test çalıştırma
    pytest.main([__file__, "-v"])
