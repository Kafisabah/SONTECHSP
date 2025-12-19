# Version: 0.1.0
# Last Update: 2024-12-19
# Module: test_pos_ui_servis_entegrasyonu
# Description: POS UI - Servis entegrasyon testleri (Görev 16.1)
# Changelog:
# - İlk oluşturma - Kapsamlı POS UI-Servis entegrasyon testleri

"""
POS UI - Servis Entegrasyon Testleri

Bu modül POS yeni ekran tasarımındaki UI bileşenleri ile servis katmanı
arasındaki entegrasyonu test eder. Mock servisler ve gerçek UI bileşenleri
kullanarak end-to-end akışları doğrular.der. Mock servisler ve gerçek UI bileşenleri
kullanarak end-to-end akışları doğrular.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from decimal import Decimal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt, QTimer
import sys
import os

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


class TestPOSUIServisEntegrasyonu:
    """POS UI - Servis entegrasyon testleri ana sınıfı"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Test setup - QApplication oluştur"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()

    @pytest.fixture
    def mock_sepet_service(self):
        """Mock sepet servisi"""
        mock = Mock(spec=ISepetService)
        mock.yeni_sepet_olustur.return_value = 123
        mock.barkod_ekle.return_value = True
        mock.sepet_bilgisi_getir.return_value = {
            "id": 123,
            "durum": SepetDurum.AKTIF.value,
            "toplam_tutar": Decimal("10.50"),
            "net_tutar": Decimal("10.50"),
            "terminal_id": 1,
            "kasiyer_id": 1,
            "satirlar": [],
        }
        return mock

    @pytest.fixture
    def mock_odeme_service(self):
        """Mock ödeme servisi"""
        mock = Mock(spec=IOdemeService)
        mock.tek_odeme_yap.return_value = True
        mock.parcali_odeme_yap.return_value = True
        mock.odeme_tutari_kontrol.return_value = {
            "gecerli": True,
            "mesaj": "Ödeme tutarı doğru",
            "eksik_tutar": Decimal("0.00"),
        }
        return mock

    @pytest.fixture
    def mock_stok_service(self):
        """Mock stok servisi"""
        mock = Mock(spec=IStokService)
        mock.urun_bilgisi_getir.return_value = {
            "urun_id": 1,
            "barkod": "1234567890",
            "urun_adi": "Test Ürün",
            "satis_fiyati": Decimal("10.50"),
            "aktif": True,
        }
        mock.stok_kontrol.return_value = True
        return mock

    @pytest.fixture
    def mock_offline_service(self):
        """Mock offline kuyruk servisi"""
        mock = Mock(spec=IOfflineKuyrukService)
        mock.islem_kuyruga_ekle.return_value = True
        mock.kuyruk_istatistikleri_getir.return_value = {"toplam_kayit": 0, "bekleyen": 0, "tamamlandi": 0}
        return mock

    def test_pos_ekrani_servislerle_baslatilir(self, mock_sepet_service, mock_odeme_service):
        """POS ekranı servislerle başarıyla başlatılır"""
        # POS ekranını oluştur
        pos_ekran = POSSatisEkrani()

        # Servisleri mock'la
        pos_ekran._sepet_service = mock_sepet_service
        pos_ekran._odeme_service = mock_odeme_service

        # UI bileşenlerinin oluşturulduğunu kontrol et
        assert pos_ekran.ust_bar is not None
        assert pos_ekran.sepet_modeli is not None
        assert pos_ekran.odeme_paneli is not None
        assert pos_ekran.alt_serit is not None

        pos_ekran.close()

    def test_barkod_ekleme_ui_servis_entegrasyonu(self, mock_sepet_service, mock_stok_service):
        """Barkod ekleme UI-Servis entegrasyonu"""
        # POS ekranını oluştur
        pos_ekran = POSSatisEkrani()
        pos_ekran._sepet_service = mock_sepet_service
        pos_ekran._stok_service = mock_stok_service

        # Barkod girişi simüle et
        test_barkod = "1234567890"
        pos_ekran.barkod_isle(test_barkod)

        # Sepet modeline ürün eklendiğini kontrol et
        assert pos_ekran.sepet_modeli.rowCount() > 0

        # İlk satırdaki ürün bilgilerini kontrol et
        ilk_satir = pos_ekran.sepet_modeli.sepet_ogeleri[0]
        assert ilk_satir.barkod == test_barkod
        assert ilk_satir.urun_adi == f"Demo Ürün {test_barkod}"

        pos_ekran.close()

    def test_sepet_toplam_guncelleme_entegrasyonu(self, mock_sepet_service):
        """Sepet toplam güncelleme entegrasyonu"""
        # POS ekranını oluştur
        pos_ekran = POSSatisEkrani()
        pos_ekran._sepet_service = mock_sepet_service

        # Test ürünü ekle
        test_urun = SepetOgesi(
            barkod="1234567890",
            urun_adi="Test Ürün",
            adet=2,
            birim_fiyat=Decimal("15.75"),
            toplam_fiyat=Decimal("31.50"),
        )
        pos_ekran.sepet_modeli.oge_ekle(test_urun)

        # Toplam hesaplamasını kontrol et
        beklenen_toplam = Decimal("31.50")
        hesaplanan_toplam = pos_ekran.sepet_modeli.genel_toplam()
        assert hesaplanan_toplam == beklenen_toplam

        pos_ekran.close()

    def test_nakit_odeme_ui_servis_entegrasyonu(self, mock_sepet_service, mock_odeme_service):
        """Nakit ödeme UI-Servis entegrasyonu"""
        # POS ekranını oluştur
        pos_ekran = POSSatisEkrani()
        pos_ekran._sepet_service = mock_sepet_service
        pos_ekran._odeme_service = mock_odeme_service

        # Sepete ürün ekle
        test_urun = SepetOgesi(
            barkod="1234567890",
            urun_adi="Test Ürün",
            adet=1,
            birim_fiyat=Decimal("10.50"),
            toplam_fiyat=Decimal("10.50"),
        )
        pos_ekran.sepet_modeli.oge_ekle(test_urun)

        # Nakit ödeme işlemini başlat
        pos_ekran.nakit_odeme()

        # Ödeme panelinin nakit alanını gösterdiğini kontrol et
        assert pos_ekran.odeme_paneli.nakit_alani_gorunur_mu()

        pos_ekran.close()

    def test_parcali_odeme_dialog_entegrasyonu(self, mock_sepet_service, mock_odeme_service):
        """Parçalı ödeme dialog entegrasyonu"""
        # POS ekranını oluştur
        pos_ekran = POSSatisEkrani()
        pos_ekran._sepet_service = mock_sepet_service
        pos_ekran._odeme_service = mock_odeme_service

        # Sepete ürün ekle
        test_urun = SepetOgesi(
            barkod="1234567890",
            urun_adi="Test Ürün",
            adet=1,
            birim_fiyat=Decimal("50.00"),
            toplam_fiyat=Decimal("50.00"),
        )
        pos_ekran.sepet_modeli.oge_ekle(test_urun)

        # Parçalı ödeme dialog'unu mock'la
        with patch("sontechsp.uygulama.arayuz.ekranlar.pos.dialoglar.ParcaliOdemeDialog") as mock_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.exec.return_value = True
            mock_dialog_instance.odeme_bilgilerini_al.return_value = (Decimal("30.00"), Decimal("20.00"))
            mock_dialog.return_value = mock_dialog_instance

            # Parçalı ödeme işlemini başlat
            pos_ekran.parcali_odeme()

            # Dialog'un oluşturulduğunu kontrol et
            mock_dialog.assert_called_once()
            mock_dialog_instance.exec.assert_called_once()

        pos_ekran.close()

    def test_klavye_kisayollari_servis_entegrasyonu(self, mock_sepet_service, mock_odeme_service):
        """Klavye kısayolları servis entegrasyonu"""
        # POS ekranını oluştur
        pos_ekran = POSSatisEkrani()
        pos_ekran._sepet_service = mock_sepet_service
        pos_ekran._odeme_service = mock_odeme_service

        # F4 (nakit ödeme) kısayolunu test et
        pos_ekran.klavye_kisayolu_isle("nakit_odeme")
        assert pos_ekran.odeme_paneli.nakit_alani_gorunur_mu()

        # F8 (sepet beklet) kısayolunu test et
        test_urun = SepetOgesi(
            barkod="1234567890",
            urun_adi="Test Ürün",
            adet=1,
            birim_fiyat=Decimal("10.50"),
            toplam_fiyat=Decimal("10.50"),
        )
        pos_ekran.sepet_modeli.oge_ekle(test_urun)

        pos_ekran.klavye_kisayolu_isle("sepet_beklet")

        # Sepet bekletme sinyalinin gönderildiğini kontrol et
        # (Sepet temizlenmiş olmalı)
        assert pos_ekran.sepet_modeli.rowCount() == 0

        pos_ekran.close()

    def test_hata_yonetimi_ui_servis_entegrasyonu(self, mock_sepet_service):
        """Hata yönetimi UI-Servis entegrasyonu"""
        # POS ekranını oluştur
        pos_ekran = POSSatisEkrani()

        # Sepet servisinde hata oluşturacak mock
        mock_sepet_service.barkod_ekle.side_effect = DogrulamaHatasi("test_hata", "Geçersiz barkod")
        pos_ekran._sepet_service = mock_sepet_service

        # Hata yöneticisini mock'la
        pos_ekran.hata_yoneticisi.hata_goster = Mock()

        # Barkod ekleme işlemini dene (hata oluşacak)
        pos_ekran.barkod_isle("gecersiz_barkod")

        # Hata gösteriminin çağrıldığını kontrol et
        pos_ekran.hata_yoneticisi.hata_goster.assert_called()

        pos_ekran.close()

    def test_offline_kuyruk_entegrasyonu(self, mock_sepet_service, mock_offline_service):
        """Offline kuyruk entegrasyonu"""
        # POS ekranını oluştur
        pos_ekran = POSSatisEkrani()
        pos_ekran._sepet_service = mock_sepet_service
        pos_ekran._offline_service = mock_offline_service

        # Network hatası simüle et
        mock_sepet_service.barkod_ekle.side_effect = NetworkHatasi("Bağlantı hatası")

        # Barkod ekleme işlemini dene
        pos_ekran.barkod_isle("1234567890")

        # Offline kuyruğa ekleme çağrısının yapıldığını kontrol et
        mock_offline_service.islem_kuyruga_ekle.assert_called_once()

        pos_ekran.close()

    def test_musteri_secim_entegrasyonu(self, mock_sepet_service):
        """Müşteri seçim entegrasyonu"""
        # POS ekranını oluştur
        pos_ekran = POSSatisEkrani()
        pos_ekran._sepet_service = mock_sepet_service

        # Müşteri seçim dialog'unu mock'la
        with patch("sontechsp.uygulama.arayuz.ekranlar.pos.dialoglar.MusteriSecDialog") as mock_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.exec.return_value = True
            mock_dialog_instance.secili_musteriyi_al.return_value = {
                "id": 1,
                "ad_soyad": "Test Müşteri",
                "telefon": "555-1234",
            }
            mock_dialog.return_value = mock_dialog_instance

            # Müşteri seçim işlemini başlat
            pos_ekran.musteri_sec()

            # Müşteri bilgisinin atandığını kontrol et
            assert pos_ekran.mevcut_musteri is not None
            assert pos_ekran.mevcut_musteri["ad_soyad"] == "Test Müşteri"

        pos_ekran.close()

    def test_sepet_satir_islemleri_entegrasyonu(self, mock_sepet_service):
        """Sepet satır işlemleri entegrasyonu"""
        # POS ekranını oluştur
        pos_ekran = POSSatisEkrani()
        pos_ekran._sepet_service = mock_sepet_service

        # Test ürünü ekle
        test_urun = SepetOgesi(
            barkod="1234567890",
            urun_adi="Test Ürün",
            adet=1,
            birim_fiyat=Decimal("10.50"),
            toplam_fiyat=Decimal("10.50"),
        )
        pos_ekran.sepet_modeli.oge_ekle(test_urun)

        # İlk satırı seç
        pos_ekran.sepet_tablo.selectRow(0)

        # Adet artırma işlemi
        pos_ekran.secili_urun_adet_artir()

        # Adet değişikliğini kontrol et
        guncellenen_urun = pos_ekran.sepet_modeli.sepet_ogeleri[0]
        assert guncellenen_urun.adet == 2
        assert guncellenen_urun.toplam_fiyat == Decimal("21.00")

        pos_ekran.close()


class TestMockServisEntegrasyonu:
    """Mock servis entegrasyon testleri"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Test setup"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()

    def test_mock_servis_ile_tam_akis(self):
        """Mock servisler ile tam akış testi"""
        # POS ekranını servis olmadan oluştur (mock mode)
        pos_ekran = POSSatisEkrani()

        # UI bileşenlerinin oluşturulduğunu kontrol et
        assert pos_ekran.ust_bar is not None
        assert pos_ekran.sepet_modeli is not None
        assert pos_ekran.odeme_paneli is not None
        assert pos_ekran.alt_serit is not None
        assert pos_ekran.hizli_urunler is not None

        # 1. Barkod ekleme (mock)
        pos_ekran.barkod_isle("1234567890")

        # Sepete ürün eklendiğini kontrol et
        assert pos_ekran.sepet_modeli.rowCount() == 1

        # 2. Toplam hesaplama
        toplam = pos_ekran.sepet_modeli.genel_toplam()
        assert toplam > Decimal("0")

        # 3. Mock ödeme işlemi
        pos_ekran.nakit_odeme()

        pos_ekran.close()

    def test_end_to_end_akis_mock(self):
        """End-to-end akış mock testi"""
        # POS ekranını oluştur
        pos_ekran = POSSatisEkrani()

        # 1. Birden fazla ürün ekleme
        urunler = ["1111111111", "2222222222", "3333333333"]
        for barkod in urunler:
            pos_ekran.barkod_isle(barkod)

        # Sepette 3 ürün olduğunu kontrol et
        assert pos_ekran.sepet_modeli.rowCount() == 3

        # 2. Toplam hesaplama
        toplam = pos_ekran.sepet_modeli.genel_toplam()
        beklenen_toplam = Decimal("31.50")  # 3 * 10.50
        assert toplam == beklenen_toplam

        # 3. İndirim uygulama
        with patch("sontechsp.uygulama.arayuz.ekranlar.pos.dialoglar.IndirimDialog") as mock_dialog:
            mock_dialog_instance = Mock()
            mock_dialog_instance.exec.return_value = True
            mock_dialog_instance.indirim_bilgilerini_al.return_value = (Decimal("5.00"), 15.87, None)
            mock_dialog.return_value = mock_dialog_instance

            pos_ekran.indirim_uygula()
            mock_dialog.assert_called_once()

        # 4. Ödeme işlemi
        pos_ekran.nakit_odeme()

        pos_ekran.close()

    def test_hizli_urun_butonlari_entegrasyonu(self):
        """Hızlı ürün butonları entegrasyonu"""
        # POS ekranını oluştur
        pos_ekran = POSSatisEkrani()

        # Hızlı ürün sekmesini kontrol et
        assert pos_ekran.hizli_urunler is not None

        # Hızlı ürün seçimi simüle et
        test_barkod = "9999999999"
        pos_ekran.barkod_isle(test_barkod)

        # Sepete ürün eklendiğini kontrol et
        assert pos_ekran.sepet_modeli.rowCount() == 1
        eklenen_urun = pos_ekran.sepet_modeli.sepet_ogeleri[0]
        assert eklenen_urun.barkod == test_barkod

        pos_ekran.close()

    def test_tema_uygulama_entegrasyonu(self):
        """Tema uygulama entegrasyonu"""
        # POS ekranını oluştur
        pos_ekran = POSSatisEkrani()

        # Tema uygulamasını kontrol et
        assert pos_ekran.tema is not None

        # Widget'ların tema özelliklerini kontrol et
        assert pos_ekran.property("class") == "pos-ana-ekran"

        # Alt widget'ların tema ayarlarını kontrol et
        assert pos_ekran.ust_bar.objectName() == "UstBar"
        assert pos_ekran.odeme_paneli.objectName() == "OdemePaneli"
        assert pos_ekran.alt_serit.objectName() == "HizliIslemSeridi"

        pos_ekran.close()


class TestServisHataYonetimi:
    """Servis hata yönetimi testleri"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Test setup"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()

    def test_sepet_servisi_hata_yonetimi(self):
        """Sepet servisi hata yönetimi"""
        # POS ekranını oluştur
        pos_ekran = POSSatisEkrani()

        # Hata yöneticisini mock'la
        pos_ekran.hata_yoneticisi.hata_goster = Mock()

        # Sepet servisinde hata oluşturacak mock
        mock_sepet_service = Mock(spec=ISepetService)
        mock_sepet_service.barkod_ekle.side_effect = DogrulamaHatasi("test_hata", "Geçersiz barkod")
        pos_ekran._sepet_service = mock_sepet_service

        # Barkod ekleme işlemini dene
        pos_ekran.barkod_isle("gecersiz_barkod")

        # Hata gösteriminin çağrıldığını kontrol et
        pos_ekran.hata_yoneticisi.hata_goster.assert_called()

        pos_ekran.close()

    def test_odeme_servisi_hata_yonetimi(self):
        """Ödeme servisi hata yönetimi"""
        # POS ekranını oluştur
        pos_ekran = POSSatisEkrani()

        # Hata yöneticisini mock'la
        pos_ekran.hata_yoneticisi.hata_goster = Mock()

        # Ödeme servisinde hata oluşturacak mock
        mock_odeme_service = Mock(spec=IOdemeService)
        mock_odeme_service.tek_odeme_yap.side_effect = SontechHatasi("Ödeme işlemi başarısız")
        pos_ekran._odeme_service = mock_odeme_service

        # Sepete ürün ekle
        test_urun = SepetOgesi(
            barkod="1234567890",
            urun_adi="Test Ürün",
            adet=1,
            birim_fiyat=Decimal("10.50"),
            toplam_fiyat=Decimal("10.50"),
        )
        pos_ekran.sepet_modeli.oge_ekle(test_urun)

        # Nakit ödeme işlemini dene (hata oluşacak)
        pos_ekran.nakit_odeme()

        pos_ekran.close()

    def test_network_hatasi_yonetimi(self):
        """Network hatası yönetimi"""
        # POS ekranını oluştur
        pos_ekran = POSSatisEkrani()

        # Offline servisini mock'la
        mock_offline_service = Mock(spec=IOfflineKuyrukService)
        mock_offline_service.islem_kuyruga_ekle.return_value = True
        pos_ekran._offline_service = mock_offline_service

        # Sepet servisinde network hatası oluşturacak mock
        mock_sepet_service = Mock(spec=ISepetService)
        mock_sepet_service.barkod_ekle.side_effect = NetworkHatasi("Bağlantı hatası")
        pos_ekran._sepet_service = mock_sepet_service

        # Barkod ekleme işlemini dene
        pos_ekran.barkod_isle("1234567890")

        # Offline kuyruğa ekleme çağrısının yapıldığını kontrol et
        mock_offline_service.islem_kuyruga_ekle.assert_called_once()

        pos_ekran.close()


class TestPerformansEntegrasyonu:
    """Performans entegrasyon testleri"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Test setup"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()

    def test_coklu_urun_ekleme_performansi(self):
        """Çoklu ürün ekleme performansı"""
        # POS ekranını oluştur
        pos_ekran = POSSatisEkrani()

        # 50 ürün ekleme performansını test et
        import time

        baslangic = time.time()

        for i in range(50):
            barkod = f"123456789{i:02d}"
            pos_ekran.barkod_isle(barkod)

        bitis = time.time()
        gecen_sure = bitis - baslangic

        # 50 ürün 2 saniyede eklenmeli
        assert gecen_sure < 2.0
        assert pos_ekran.sepet_modeli.rowCount() == 50

        pos_ekran.close()

    def test_sepet_toplam_hesaplama_performansi(self):
        """Sepet toplam hesaplama performansı"""
        # POS ekranını oluştur
        pos_ekran = POSSatisEkrani()

        # 100 ürün ekle
        for i in range(100):
            test_urun = SepetOgesi(
                barkod=f"123456789{i:03d}",
                urun_adi=f"Test Ürün {i}",
                adet=1,
                birim_fiyat=Decimal("10.50"),
                toplam_fiyat=Decimal("10.50"),
            )
            pos_ekran.sepet_modeli.oge_ekle(test_urun)

        # Toplam hesaplama performansını test et
        import time

        baslangic = time.time()

        for _ in range(10):
            toplam = pos_ekran.sepet_modeli.genel_toplam()

        bitis = time.time()
        gecen_sure = bitis - baslangic

        # 10 toplam hesaplama 0.1 saniyede tamamlanmalı
        assert gecen_sure < 0.1
        assert toplam == Decimal("1050.00")  # 100 * 10.50

        pos_ekran.close()


if __name__ == "__main__":
    # Test çalıştırma
    pytest.main([__file__, "-v"])
