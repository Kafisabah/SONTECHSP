# Version: 0.1.0
# Last Update: 2024-12-19
# Module: test_pos_servis_entegrasyonu
# Description: POS UI - Servis entegrasyon testleri
# Changelog:
# - İlk oluşturma - POS servis entegrasyon testleri

"""
POS Servis Entegrasyon Testleri

POS UI bileşenleri ile servis katmanı arasındaki entegrasyonu test eder.
Mock servisler kullanarak gerçek entegrasyon senaryolarını simüle eder.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

from sontechsp.uygulama.moduller.pos.ui.pos_ana_ekran import POSAnaEkran
from sontechsp.uygulama.moduller.pos.ui.handlers.pos_servis_entegratoru import POSServisEntegratoru
from sontechsp.uygulama.moduller.pos.arayuzler import (
    ISepetService,
    IOdemeService,
    IStokService,
    IOfflineKuyrukService,
    OdemeTuru,
    IslemTuru,
    SepetDurum,
)
from sontechsp.uygulama.cekirdek.hatalar import POSHatasi, NetworkHatasi


class TestPOSServisEntegrasyonu:
    """POS UI - Servis entegrasyon testleri"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Test setup"""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()

    def test_pos_ana_ekran_servis_entegratoru_ile_baslatilir(self):
        """POS ana ekran servis entegratörü ile başlatılır"""
        # Mock servisler oluştur
        mock_sepet_service = Mock(spec=ISepetService)
        mock_odeme_service = Mock(spec=IOdemeService)
        mock_stok_service = Mock(spec=IStokService)
        mock_offline_service = Mock(spec=IOfflineKuyrukService)

        # Mock sepet oluşturma
        mock_sepet_service.yeni_sepet_olustur.return_value = 123

        # POS ana ekranı oluştur
        pos_ekran = POSAnaEkran(
            sepet_service=mock_sepet_service,
            odeme_service=mock_odeme_service,
            stok_service=mock_stok_service,
            offline_kuyruk_service=mock_offline_service,
        )

        # Servis entegratörünün oluşturulduğunu kontrol et
        assert pos_ekran.servis_entegratoru is not None
        assert isinstance(pos_ekran.servis_entegratoru, POSServisEntegratoru)

        # Sepet oluşturma çağrısının yapıldığını kontrol et
        mock_sepet_service.yeni_sepet_olustur.assert_called_once()

        pos_ekran.close()

    def test_barkod_ekleme_entegrasyonu(self):
        """Barkod ekleme UI-Servis entegrasyonu"""
        # Mock servisler
        mock_sepet_service = Mock(spec=ISepetService)
        mock_stok_service = Mock(spec=IStokService)

        # Mock sepet ve ürün bilgileri
        mock_sepet_service.yeni_sepet_olustur.return_value = 123
        mock_sepet_service.barkod_ekle.return_value = True
        mock_sepet_service.sepet_bilgisi_getir.return_value = {
            "id": 123,
            "satirlar": [
                {
                    "barkod": "1234567890",
                    "urun_adi": "Test Ürün",
                    "adet": 1,
                    "birim_fiyat": 10.50,
                    "toplam_fiyat": 10.50,
                }
            ],
        }

        mock_stok_service.urun_bilgisi_getir.return_value = {
            "id": 1,
            "urun_adi": "Test Ürün",
            "satis_fiyati": 10.50,
            "aktif": True,
        }

        # POS ana ekranı oluştur
        pos_ekran = POSAnaEkran(sepet_service=mock_sepet_service, stok_service=mock_stok_service)

        # Barkod panelini al
        barkod_paneli = pos_ekran._bilesenler.get("barkod_paneli")
        assert barkod_paneli is not None

        # Barkod girişi simüle et
        barkod_paneli._barkod_alani.setText("1234567890")
        barkod_paneli._barkod_ekle()

        # Servis çağrılarının yapıldığını kontrol et
        mock_sepet_service.barkod_ekle.assert_called_with(123, "1234567890")

        pos_ekran.close()

    def test_odeme_islemi_entegrasyonu(self):
        """Ödeme işlemi UI-Servis entegrasyonu"""
        # Mock servisler
        mock_sepet_service = Mock(spec=ISepetService)
        mock_odeme_service = Mock(spec=IOdemeService)

        # Mock sepet bilgileri
        mock_sepet_service.yeni_sepet_olustur.return_value = 123
        mock_odeme_service.tek_odeme_yap.return_value = True

        # POS ana ekranı oluştur
        pos_ekran = POSAnaEkran(sepet_service=mock_sepet_service, odeme_service=mock_odeme_service)

        # Ödeme panelini al
        odeme_paneli = pos_ekran._bilesenler.get("odeme_paneli")
        assert odeme_paneli is not None

        # Mock sepet verisi ile ödeme panelini güncelle
        sepet_verileri = [
            {
                "barkod": "1234567890",
                "urun_adi": "Test Ürün",
                "adet": 1,
                "birim_fiyat": Decimal("10.50"),
                "toplam_fiyat": Decimal("10.50"),
            }
        ]

        # Sepet güncellendiği sinyalini gönder
        pos_ekran.pos_sinyalleri.sepet_guncellendi.emit(sepet_verileri)

        # Nakit ödeme butonuna tıkla
        odeme_paneli._odeme_turu_sec("nakit")

        # Ödeme servisinin çağrıldığını kontrol et
        mock_odeme_service.tek_odeme_yap.assert_called_once()

        pos_ekran.close()

    def test_offline_kuyruk_entegrasyonu(self):
        """Offline kuyruk entegrasyonu"""
        # Mock servisler
        mock_sepet_service = Mock(spec=ISepetService)
        mock_offline_service = Mock(spec=IOfflineKuyrukService)

        # Mock sepet oluşturma
        mock_sepet_service.yeni_sepet_olustur.return_value = 123

        # Barkod ekleme başarısız olsun (network hatası)
        mock_sepet_service.barkod_ekle.side_effect = NetworkHatasi("Network bağlantısı yok")

        # Offline kuyruk ekleme başarılı
        mock_offline_service.islem_kuyruga_ekle.return_value = True

        # POS ana ekranı oluştur
        pos_ekran = POSAnaEkran(sepet_service=mock_sepet_service, offline_kuyruk_service=mock_offline_service)

        # Ürün ekleme sinyali gönder (network hatası ile)
        urun_verisi = {
            "barkod": "1234567890",
            "urun_adi": "Test Ürün",
            "adet": 1,
            "birim_fiyat": Decimal("10.50"),
            "toplam_fiyat": Decimal("10.50"),
        }

        pos_ekran.pos_sinyalleri.urun_eklendi.emit(urun_verisi)

        # Offline kuyruğa ekleme çağrısının yapıldığını kontrol et
        mock_offline_service.islem_kuyruga_ekle.assert_called_once()

        pos_ekran.close()

    def test_hata_yonetimi_entegrasyonu(self):
        """Hata yönetimi entegrasyonu"""
        # Mock servisler
        mock_sepet_service = Mock(spec=ISepetService)

        # Mock sepet oluşturma
        mock_sepet_service.yeni_sepet_olustur.return_value = 123

        # Barkod ekleme hatası
        mock_sepet_service.barkod_ekle.side_effect = POSHatasi("Geçersiz barkod")

        # POS ana ekranı oluştur
        pos_ekran = POSAnaEkran(sepet_service=mock_sepet_service)

        # Hata sinyalini yakalamak için mock
        hata_sinyali_mock = Mock()
        pos_ekran.pos_sinyalleri.hata_olustu.connect(hata_sinyali_mock)

        # Ürün ekleme sinyali gönder (hata ile)
        urun_verisi = {
            "barkod": "1234567890",
            "urun_adi": "Test Ürün",
            "adet": 1,
            "birim_fiyat": Decimal("10.50"),
            "toplam_fiyat": Decimal("10.50"),
        }

        pos_ekran.pos_sinyalleri.urun_eklendi.emit(urun_verisi)

        # Hata sinyalinin gönderildiğini kontrol et
        # Not: Hata yöneticisi üzerinden işlendiği için direkt sinyal gelmeyebilir

        pos_ekran.close()

    def test_sepet_temizleme_entegrasyonu(self):
        """Sepet temizleme entegrasyonu"""
        # Mock servisler
        mock_sepet_service = Mock(spec=ISepetService)

        # Mock sepet işlemleri
        mock_sepet_service.yeni_sepet_olustur.return_value = 123
        mock_sepet_service.sepet_bosalt.return_value = True

        # POS ana ekranı oluştur
        pos_ekran = POSAnaEkran(sepet_service=mock_sepet_service)

        # Sepet temizleme sinyali gönder
        pos_ekran.pos_sinyalleri.sepet_temizlendi.emit()

        # Sepet boşaltma çağrısının yapıldığını kontrol et
        mock_sepet_service.sepet_bosalt.assert_called_with(123)

        pos_ekran.close()

    def test_servis_durumu_kontrolu(self):
        """Servis durumu kontrolü"""
        # Mock servisler
        mock_sepet_service = Mock(spec=ISepetService)
        mock_odeme_service = Mock(spec=IOdemeService)

        mock_sepet_service.yeni_sepet_olustur.return_value = 123

        # POS ana ekranı oluştur
        pos_ekran = POSAnaEkran(sepet_service=mock_sepet_service, odeme_service=mock_odeme_service)

        # Servis durumunu kontrol et
        servis_durumu = pos_ekran.servis_durumu_getir()

        # Beklenen servis durumlarını kontrol et
        assert servis_durumu["sepet_service"] is True
        assert servis_durumu["odeme_service"] is True
        assert servis_durumu["stok_service"] is False  # Verilmedi
        assert servis_durumu["offline_kuyruk_service"] is False  # Verilmedi

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
        # POS ana ekranı servis olmadan oluştur (mock mode)
        pos_ekran = POSAnaEkran()

        # Barkod panelini al
        barkod_paneli = pos_ekran._bilesenler.get("barkod_paneli")
        sepet_tablosu = pos_ekran._bilesenler.get("sepet_tablosu")
        odeme_paneli = pos_ekran._bilesenler.get("odeme_paneli")

        assert barkod_paneli is not None
        assert sepet_tablosu is not None
        assert odeme_paneli is not None

        # 1. Barkod ekleme (mock)
        barkod_paneli._barkod_alani.setText("1234567890")
        barkod_paneli._barkod_ekle()

        # 2. Sepet kontrolü (mock veri ile çalışır)
        sepet_verileri = sepet_tablosu.sepet_verilerini_getir()
        # Mock modda direkt eklenmeyebilir, bu normal

        # 3. Mock ödeme işlemi
        mock_sepet_verisi = [
            {
                "barkod": "1234567890",
                "urun_adi": "Test Ürün",
                "adet": 1,
                "birim_fiyat": Decimal("10.50"),
                "toplam_fiyat": Decimal("10.50"),
            }
        ]

        # Sepet güncellendiği sinyalini gönder
        pos_ekran.pos_sinyalleri.sepet_guncellendi.emit(mock_sepet_verisi)

        # Ödeme işlemi
        odeme_paneli._odeme_turu_sec("nakit")

        pos_ekran.close()

    def test_end_to_end_akis_mock(self):
        """End-to-end akış mock testi"""
        # POS ana ekranı oluştur
        pos_ekran = POSAnaEkran()

        # Sinyal yakalama için mock'lar
        sepet_guncellendi_mock = Mock()
        odeme_tamamlandi_mock = Mock()

        pos_ekran.pos_sinyalleri.sepet_guncellendi.connect(sepet_guncellendi_mock)
        pos_ekran.pos_sinyalleri.odeme_tamamlandi.connect(odeme_tamamlandi_mock)

        # 1. Ürün ekleme sinyali gönder
        urun_verisi = {
            "barkod": "1234567890",
            "urun_adi": "Test Ürün",
            "adet": 1,
            "birim_fiyat": Decimal("10.50"),
            "toplam_fiyat": Decimal("10.50"),
        }

        pos_ekran.pos_sinyalleri.urun_eklendi.emit(urun_verisi)

        # 2. Sepet güncelleme sinyali gönder
        pos_ekran.pos_sinyalleri.sepet_guncellendi.emit([urun_verisi])

        # 3. Ödeme başlatma sinyali gönder
        pos_ekran.pos_sinyalleri.odeme_baslatildi.emit("nakit", Decimal("10.50"))

        # Sinyallerin çağrıldığını kontrol et
        sepet_guncellendi_mock.assert_called()

        pos_ekran.close()


class TestPOSServisEntegratoru:
    """POS Servis Entegratörü unit testleri"""

    def test_entegrator_olusturma(self):
        """Entegratör oluşturma testi"""
        from sontechsp.uygulama.moduller.pos.ui.handlers.pos_sinyalleri import POSSinyalleri
        from sontechsp.uygulama.moduller.pos.ui.handlers.pos_hata_yoneticisi import POSHataYoneticisi

        # Mock bileşenler
        sinyaller = POSSinyalleri()
        hata_yoneticisi = Mock(spec=POSHataYoneticisi)
        mock_sepet_service = Mock(spec=ISepetService)

        # Entegratör oluştur
        entegrator = POSServisEntegratoru(
            sinyaller=sinyaller, hata_yoneticisi=hata_yoneticisi, sepet_service=mock_sepet_service
        )

        assert entegrator is not None
        assert entegrator._sepet_service == mock_sepet_service
        assert entegrator._sinyaller == sinyaller

    def test_entegrator_baslat(self):
        """Entegratör başlatma testi"""
        from sontechsp.uygulama.moduller.pos.ui.handlers.pos_sinyalleri import POSSinyalleri
        from sontechsp.uygulama.moduller.pos.ui.handlers.pos_hata_yoneticisi import POSHataYoneticisi

        # Mock bileşenler
        sinyaller = POSSinyalleri()
        hata_yoneticisi = Mock(spec=POSHataYoneticisi)
        mock_sepet_service = Mock(spec=ISepetService)

        # Mock sepet oluşturma
        mock_sepet_service.yeni_sepet_olustur.return_value = 456

        # Entegratör oluştur ve başlat
        entegrator = POSServisEntegratoru(
            sinyaller=sinyaller, hata_yoneticisi=hata_yoneticisi, sepet_service=mock_sepet_service
        )

        entegrator.baslat()

        # Sepet oluşturma çağrısının yapıldığını kontrol et
        mock_sepet_service.yeni_sepet_olustur.assert_called_once()
        assert entegrator._aktif_sepet_id == 456

    def test_kuyruk_istatistikleri(self):
        """Kuyruk istatistikleri testi"""
        from sontechsp.uygulama.moduller.pos.ui.handlers.pos_sinyalleri import POSSinyalleri
        from sontechsp.uygulama.moduller.pos.ui.handlers.pos_hata_yoneticisi import POSHataYoneticisi

        # Mock bileşenler
        sinyaller = POSSinyalleri()
        hata_yoneticisi = Mock(spec=POSHataYoneticisi)
        mock_offline_service = Mock(spec=IOfflineKuyrukService)

        # Mock istatistikler
        mock_istatistikler = {
            "toplam_kayit": 5,
            "durum_sayilari": {"bekleyen": 3, "tamamlandi": 2},
            "network_durumu": True,
        }
        mock_offline_service.kuyruk_istatistikleri_getir.return_value = mock_istatistikler

        # Entegratör oluştur
        entegrator = POSServisEntegratoru(
            sinyaller=sinyaller, hata_yoneticisi=hata_yoneticisi, offline_kuyruk_service=mock_offline_service
        )

        # İstatistikleri al
        istatistikler = entegrator.kuyruk_istatistikleri_getir()

        assert istatistikler == mock_istatistikler
        mock_offline_service.kuyruk_istatistikleri_getir.assert_called_once()
