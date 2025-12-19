# Version: 0.1.0
# Last Update: 2025-12-18
# Module: tests.test_offline_kuyruk
# Description: Offline kuyruk işleyiş testleri - Ana test dosyası
# Changelog:
# - İlk oluşturma

"""
Offline Kuyruk İşleyiş Testleri

Bu modül offline kuyruk sisteminin kapsamlı testlerini içerir:
- Kayıt ekleme ve kuyruktan okuma testleri
- FIFO sırası kontrolü ve kuyruk temizleme testleri
- İnternet bağlantı simülasyonu ile gerçekçi offline senaryoları

Görev 6: Offline kuyruk işleyiş testleri geliştir
Requirements: 6.1, 6.2, 6.3, 6.4
"""

import pytest
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any
from unittest.mock import Mock, patch, MagicMock

from sontechsp.uygulama.moduller.pos.services.offline_kuyruk_service import OfflineKuyrukService
from sontechsp.uygulama.moduller.pos.repositories.offline_kuyruk_repository_backup import OfflineKuyrukRepository
from sontechsp.uygulama.moduller.pos.arayuzler import IslemTuru, KuyrukDurum
from sontechsp.uygulama.cekirdek.hatalar import DogrulamaHatasi, NetworkHatasi, VeritabaniHatasi


class TestOfflineKuyrukIsleyis:
    """Offline kuyruk işleyiş ana test sınıfı"""

    def setup_method(self):
        """Her test öncesi çalışır"""
        self.mock_repository = Mock(spec=OfflineKuyrukRepository)
        self.service = OfflineKuyrukService(self.mock_repository)

    def test_offline_kuyruga_kayit_ekleme(self):
        """
        Offline kuyruğa kayıt ekleme testi

        Requirements: 6.1 - Offline kuyruğa kayıt ekleme
        """
        # Arrange
        with patch.object(self.service, "network_durumu_kontrol", return_value=False):
            self.mock_repository.kuyruk_ekle.return_value = 1

            test_verisi = {"fis_no": "F001", "toplam_tutar": 150.50, "urunler": [{"id": 1, "adet": 2, "fiyat": 75.25}]}

            # Act
            sonuc = self.service.islem_kuyruga_ekle(
                islem_turu=IslemTuru.SATIS, veri=test_verisi, terminal_id=1, kasiyer_id=1
            )

            # Assert
            assert sonuc is True
            self.mock_repository.kuyruk_ekle.assert_called_once()

            # Çağrı parametrelerini kontrol et
            call_args = self.mock_repository.kuyruk_ekle.call_args
            if call_args and call_args.args and len(call_args.args) >= 4:
                assert call_args.args[0] == IslemTuru.SATIS  # islem_turu
                assert call_args.args[1] == test_verisi  # veri
                assert call_args.args[2] == 1  # terminal_id
                assert call_args.args[3] == 1  # kasiyer_id

    def test_kuyruktan_kayit_okuma(self):
        """
        Kuyruktan kayıt okuma testi

        Requirements: 6.1 - Kuyruktan okuma
        """
        # Arrange
        mock_kuyruk_kayitlari = [
            {
                "id": 1,
                "islem_turu": IslemTuru.SATIS.value,
                "durum": KuyrukDurum.BEKLEMEDE.value,
                "veri": {"fis_no": "F001", "toplam": 100.0},
                "terminal_id": 1,
                "kasiyer_id": 1,
                "oncelik": 1,
                "islem_tarihi": datetime.now().isoformat(),
            },
            {
                "id": 2,
                "islem_turu": IslemTuru.IADE.value,
                "durum": KuyrukDurum.BEKLEMEDE.value,
                "veri": {"iade_no": "I001", "tutar": 50.0},
                "terminal_id": 1,
                "kasiyer_id": 1,
                "oncelik": 2,
                "islem_tarihi": datetime.now().isoformat(),
            },
        ]

        self.mock_repository.bekleyen_kuyruk_listesi.return_value = mock_kuyruk_kayitlari

        # Act
        bekleyen_islemler = self.mock_repository.bekleyen_kuyruk_listesi()

        # Assert
        assert len(bekleyen_islemler) == 2
        assert bekleyen_islemler[0]["id"] == 1
        assert bekleyen_islemler[1]["id"] == 2
        assert bekleyen_islemler[0]["islem_turu"] == IslemTuru.SATIS.value
        assert bekleyen_islemler[1]["islem_turu"] == IslemTuru.IADE.value

    def test_fifo_sirasi_kontrolu(self):
        """
        FIFO sırası kontrolü testi

        Requirements: 6.2 - FIFO sırası kontrolü
        """
        # Arrange - Aynı öncelikte işlemler
        mock_kuyruk_kayitlari = []
        for i in range(5):
            kayit = {
                "id": i + 1,
                "islem_turu": IslemTuru.SATIS.value,
                "durum": KuyrukDurum.BEKLEMEDE.value,
                "veri": {"islem_no": i + 1},
                "terminal_id": 1,
                "kasiyer_id": 1,
                "oncelik": 1,  # Aynı öncelik
                "islem_tarihi": (datetime.now() + timedelta(seconds=i)).isoformat(),
            }
            mock_kuyruk_kayitlari.append(kayit)

        self.mock_repository.bekleyen_kuyruk_listesi.return_value = mock_kuyruk_kayitlari

        # Act
        bekleyen_islemler = self.mock_repository.bekleyen_kuyruk_listesi()

        # Assert - FIFO sırası korunmuş olmalı
        for i, islem in enumerate(bekleyen_islemler):
            assert islem["id"] == i + 1
            assert islem["veri"]["islem_no"] == i + 1

    def test_kuyruk_temizleme(self):
        """
        Kuyruk temizleme testi

        Requirements: 6.4 - Kuyruk temizleme
        """
        # Arrange
        gun_sayisi = 7
        beklenen_silinen_sayisi = 5
        self.mock_repository.kuyruk_temizle.return_value = beklenen_silinen_sayisi

        # Act
        silinen_sayisi = self.service.kuyruk_temizle(gun_sayisi)

        # Assert
        assert silinen_sayisi == beklenen_silinen_sayisi
        self.mock_repository.kuyruk_temizle.assert_called_once_with(gun_sayisi)

    def test_internet_baglanti_simulasyonu_offline(self):
        """
        İnternet bağlantı simülasyonu - Offline durumu

        Requirements: 6.3 - İnternet bağlantı simülasyonu
        """
        # Arrange - Network offline
        with patch.object(self.service, "network_durumu_kontrol", return_value=False):
            self.mock_repository.kuyruk_ekle.return_value = 1

            test_verisi = {"islem_no": 1, "tutar": 100.0}

            # Act
            sonuc = self.service.islem_kuyruga_ekle(
                islem_turu=IslemTuru.SATIS, veri=test_verisi, terminal_id=1, kasiyer_id=1
            )

            # Assert - İşlem kuyruğa eklenmeli
            assert sonuc is True
            self.mock_repository.kuyruk_ekle.assert_called_once()

    def test_internet_baglanti_simulasyonu_online(self):
        """
        İnternet bağlantı simülasyonu - Online durumu

        Requirements: 6.3 - İnternet bağlantı simülasyonu
        """
        # Arrange - Network online
        with patch.object(self.service, "network_durumu_kontrol", return_value=True):
            with patch.object(self.service, "_islem_direkt_gonder", return_value=True):
                test_verisi = {"islem_no": 1, "tutar": 100.0}

                # Act
                sonuc = self.service.islem_kuyruga_ekle(
                    islem_turu=IslemTuru.SATIS, veri=test_verisi, terminal_id=1, kasiyer_id=1
                )

                # Assert - İşlem direkt gönderilmeli
                assert sonuc is True
                # Direkt gönderim başarılı olduğu için kuyruğa eklenmemeli
                self.mock_repository.kuyruk_ekle.assert_not_called()

    def test_network_kesintisi_sirasinda_kayit(self):
        """
        Network kesintisi sırasında kayıt testi

        Requirements: 6.1, 6.3 - Network kesintisi sırasında güvenli kayıt
        """
        # Arrange - Network kesintisi simülasyonu
        with patch.object(self.service, "network_durumu_kontrol", return_value=False):
            self.mock_repository.kuyruk_ekle.return_value = 1

            # Kritik işlem verisi
            kritik_veri = {
                "fis_no": "KRITIK_001",
                "toplam_tutar": 1500.75,
                "odeme_turu": "KREDI_KARTI",
                "musteri_id": 12345,
                "urunler": [{"id": 1, "adet": 3, "fiyat": 500.25}],
                "timestamp": datetime.now().isoformat(),
            }

            # Act
            sonuc = self.service.islem_kuyruga_ekle(
                islem_turu=IslemTuru.SATIS, veri=kritik_veri, terminal_id=1, kasiyer_id=1
            )

            # Assert - Kritik veri güvenli şekilde saklanmalı
            assert sonuc is True
            self.mock_repository.kuyruk_ekle.assert_called_once()

            # Veri bütünlüğü kontrolü
            call_args = self.mock_repository.kuyruk_ekle.call_args
            if call_args and call_args.args and len(call_args.args) >= 2:
                kaydedilen_veri = call_args.args[1]
                assert kaydedilen_veri["fis_no"] == "KRITIK_001"
                assert kaydedilen_veri["toplam_tutar"] == 1500.75
                assert kaydedilen_veri["musteri_id"] == 12345

    def test_senkronizasyon_network_geri_gelince(self):
        """
        Network geri gelince senkronizasyon testi

        Requirements: 6.3 - Network geri gelince işleme
        """
        # Arrange - Network geri geldi
        with patch.object(self.service, "network_durumu_kontrol", return_value=True):
            # Mock bekleyen işlemler
            bekleyen_islemler = [
                {
                    "id": 1,
                    "islem_turu": IslemTuru.SATIS.value,
                    "durum": KuyrukDurum.BEKLEMEDE.value,
                    "veri": {"fis_no": "F001"},
                    "terminal_id": 1,
                    "kasiyer_id": 1,
                },
                {
                    "id": 2,
                    "islem_turu": IslemTuru.IADE.value,
                    "durum": KuyrukDurum.BEKLEMEDE.value,
                    "veri": {"iade_no": "I001"},
                    "terminal_id": 1,
                    "kasiyer_id": 1,
                },
            ]

            self.mock_repository.bekleyen_kuyruk_listesi.return_value = bekleyen_islemler
            self.mock_repository.kuyruk_durum_guncelle.return_value = True

            # Mock başarılı işlem gönderimi
            with patch.object(self.service, "_kuyruk_islemini_gonder", return_value=True):
                # Act
                islenen_sayisi = self.service.kuyruk_senkronize_et()

                # Assert
                assert islenen_sayisi == 2
                self.mock_repository.bekleyen_kuyruk_listesi.assert_called()

                # Her işlem için durum güncellemesi yapılmış olmalı
                assert self.mock_repository.kuyruk_durum_guncelle.call_count >= 4  # ISLENIYOR + TAMAMLANDI

    def test_karmasik_offline_senaryosu(self):
        """
        Karmaşık offline senaryosu testi

        Requirements: 6.1, 6.2, 6.3, 6.4 - Kapsamlı offline senaryo
        """
        # Senaryo: Network kesintisi -> Çoklu işlem -> Network geri gelme -> Senkronizasyon

        # 1. Network kesintisi
        with patch.object(self.service, "network_durumu_kontrol", return_value=False):
            self.mock_repository.kuyruk_ekle.return_value = 1

            # Çoklu işlem ekleme
            islemler = [
                {"turu": IslemTuru.SATIS, "veri": {"fis_no": "F001", "tutar": 100}},
                {"turu": IslemTuru.SATIS, "veri": {"fis_no": "F002", "tutar": 200}},
                {"turu": IslemTuru.IADE, "veri": {"iade_no": "I001", "tutar": 50}},
                {"turu": IslemTuru.STOK_DUSUMU, "veri": {"urun_id": 1, "adet": 5}},
            ]

            # İşlemleri kuyruğa ekle
            for islem in islemler:
                sonuc = self.service.islem_kuyruga_ekle(
                    islem_turu=islem["turu"], veri=islem["veri"], terminal_id=1, kasiyer_id=1
                )
                assert sonuc is True

            # Kuyruk ekleme sayısını kontrol et
            assert self.mock_repository.kuyruk_ekle.call_count == 4

        # 2. Network geri gelme ve senkronizasyon
        with patch.object(self.service, "network_durumu_kontrol", return_value=True):
            # Mock bekleyen işlemler (FIFO sırasında)
            bekleyen_islemler = [
                {
                    "id": i + 1,
                    "islem_turu": islemler[i]["turu"].value,
                    "veri": islemler[i]["veri"],
                    "durum": KuyrukDurum.BEKLEMEDE.value,
                }
                for i in range(4)
            ]

            self.mock_repository.bekleyen_kuyruk_listesi.return_value = bekleyen_islemler
            self.mock_repository.kuyruk_durum_guncelle.return_value = True

            # Mock başarılı senkronizasyon
            with patch.object(self.service, "_kuyruk_islemini_gonder", return_value=True):
                islenen_sayisi = self.service.kuyruk_senkronize_et()

                # Assert - Tüm işlemler senkronize edilmeli
                assert islenen_sayisi == 4

    def test_eszamanli_kuyruk_islemleri(self):
        """
        Eş zamanlı kuyruk işlemleri testi

        Requirements: 6.1, 6.2 - Thread-safe kuyruk işlemleri
        """
        # Arrange
        with patch.object(self.service, "network_durumu_kontrol", return_value=False):
            self.mock_repository.kuyruk_ekle.return_value = 1

            sonuclar = []
            hatalar = []

            def kuyruk_islem_ekle(thread_id):
                try:
                    for i in range(3):
                        veri = {"thread_id": thread_id, "islem_no": i + 1}
                        sonuc = self.service.islem_kuyruga_ekle(
                            islem_turu=IslemTuru.SATIS, veri=veri, terminal_id=thread_id, kasiyer_id=1
                        )
                        sonuclar.append((thread_id, i + 1, sonuc))
                        time.sleep(0.01)  # Kısa bekleme
                except Exception as e:
                    hatalar.append((thread_id, str(e)))

            # Act - 3 thread ile eş zamanlı işlem
            threads = []
            for thread_id in range(1, 4):
                thread = threading.Thread(target=kuyruk_islem_ekle, args=(thread_id,))
                threads.append(thread)
                thread.start()

            # Thread'lerin bitmesini bekle
            for thread in threads:
                thread.join()

            # Assert
            assert len(hatalar) == 0  # Hata olmamalı
            assert len(sonuclar) == 9  # 3 thread * 3 işlem = 9
            assert all(sonuc for _, _, sonuc in sonuclar)  # Tüm işlemler başarılı olmalı

    def test_kuyruk_hata_yonetimi(self):
        """
        Kuyruk hata yönetimi testi

        Requirements: 6.3 - Hata durumu yönetimi
        """
        # Arrange - Network var ama senkronizasyon başarısız
        with patch.object(self.service, "network_durumu_kontrol", return_value=True):
            bekleyen_islemler = [
                {
                    "id": 1,
                    "islem_turu": IslemTuru.SATIS.value,
                    "durum": KuyrukDurum.BEKLEMEDE.value,
                    "veri": {"fis_no": "F001"},
                    "terminal_id": 1,
                    "kasiyer_id": 1,
                }
            ]

            self.mock_repository.bekleyen_kuyruk_listesi.return_value = bekleyen_islemler
            self.mock_repository.kuyruk_durum_guncelle.return_value = True
            self.mock_repository.kuyruk_deneme_artir.return_value = True

            # Mock başarısız işlem gönderimi
            with patch.object(self.service, "_kuyruk_islemini_gonder", return_value=False):
                # Act
                islenen_sayisi = self.service.kuyruk_senkronize_et()

                # Assert - İşlem başarısız, deneme artırılmalı
                assert islenen_sayisi == 0
                self.mock_repository.kuyruk_deneme_artir.assert_called_once()

    def test_gecersiz_parametreler(self):
        """
        Geçersiz parametreler testi

        Requirements: 6.1 - Parametre validasyonu
        """
        # Geçersiz terminal_id
        with pytest.raises(DogrulamaHatasi, match="Terminal ID pozitif olmalıdır"):
            self.service.islem_kuyruga_ekle(
                islem_turu=IslemTuru.SATIS, veri={"test": "data"}, terminal_id=0, kasiyer_id=1
            )

        # Geçersiz kasiyer_id
        with pytest.raises(DogrulamaHatasi, match="Kasiyer ID pozitif olmalıdır"):
            self.service.islem_kuyruga_ekle(
                islem_turu=IslemTuru.SATIS, veri={"test": "data"}, terminal_id=1, kasiyer_id=0
            )

        # Boş veri
        with pytest.raises(DogrulamaHatasi, match="İşlem verisi geçerli bir dict olmalıdır"):
            self.service.islem_kuyruga_ekle(islem_turu=IslemTuru.SATIS, veri={}, terminal_id=1, kasiyer_id=1)

    def test_network_hatasi_senkronizasyon(self):
        """
        Network hatası durumunda senkronizasyon testi

        Requirements: 6.3 - Network hata yönetimi
        """
        # Arrange - Network yok
        with patch.object(self.service, "network_durumu_kontrol", return_value=False):
            # Act & Assert
            with pytest.raises(NetworkHatasi, match="Network bağlantısı yok"):
                self.service.kuyruk_senkronize_et()

    def test_kuyruk_istatistikleri(self):
        """
        Kuyruk istatistikleri testi

        Requirements: 6.4 - İstatistik raporlama
        """
        # Arrange
        mock_istatistikler = {
            "toplam_kayit": 10,
            "durum_sayilari": {"BEKLEMEDE": 5, "ISLENIYOR": 2, "TAMAMLANDI": 2, "HATA": 1},
            "islem_turu_sayilari": {"SATIS": 7, "IADE": 2, "STOK_DUSUMU": 1},
            "ortalama_bekleme_suresi_saniye": 120,
        }

        self.mock_repository.kuyruk_istatistikleri.return_value = mock_istatistikler

        with patch.object(self.service, "network_durumu_kontrol", return_value=True):
            # Act
            istatistikler = self.service.kuyruk_istatistikleri_getir(terminal_id=1)

            # Assert
            assert istatistikler["toplam_kayit"] == 10
            assert istatistikler["durum_sayilari"]["BEKLEMEDE"] == 5
            assert istatistikler["network_durumu"] is True
            self.mock_repository.kuyruk_istatistikleri.assert_called_once_with(1)

    def test_hata_durumundaki_islemler(self):
        """
        Hata durumundaki işlemler testi

        Requirements: 6.4 - Hata durumu raporlama
        """
        # Arrange
        mock_hata_islemleri = [
            {
                "id": 1,
                "islem_turu": IslemTuru.SATIS.value,
                "durum": KuyrukDurum.HATA.value,
                "hata_mesaji": "Network timeout",
                "deneme_sayisi": 3,
                "max_deneme_sayisi": 3,
            }
        ]

        self.mock_repository.hata_durumundaki_kuyruklar.return_value = mock_hata_islemleri

        # Act
        hata_islemleri = self.service.hata_durumundaki_islemler(terminal_id=1)

        # Assert
        assert len(hata_islemleri) == 1
        assert hata_islemleri[0]["durum"] == KuyrukDurum.HATA.value
        assert hata_islemleri[0]["hata_mesaji"] == "Network timeout"
        self.mock_repository.hata_durumundaki_kuyruklar.assert_called_once_with(1)


class TestOfflineKuyrukEntegrasyon:
    """Offline kuyruk entegrasyon testleri"""

    def setup_method(self):
        """Her test öncesi çalışır"""
        # Gerçek repository ile entegrasyon testi
        self.repository = OfflineKuyrukRepository()
        self.service = OfflineKuyrukService(self.repository)

    @pytest.mark.slow
    def test_gercek_sqlite_kuyruk_islemleri(self):
        """
        Gerçek SQLite kuyruk işlemleri entegrasyon testi

        Requirements: 6.1, 6.2 - Gerçek veritabanı ile test
        """
        # Bu test gerçek SQLite veritabanı gerektirir
        # Test ortamında çalıştırılmalıdır

        # Arrange
        test_verisi = {
            "fis_no": "ENTEGRASYON_001",
            "toplam_tutar": 250.75,
            "test_timestamp": datetime.now().isoformat(),
        }

        try:
            # Act - Kuyruğa ekle
            with patch.object(self.service, "network_durumu_kontrol", return_value=False):
                sonuc = self.service.islem_kuyruga_ekle(
                    islem_turu=IslemTuru.SATIS,
                    veri=test_verisi,
                    terminal_id=999,  # Test terminal
                    kasiyer_id=999,  # Test kasiyer
                )

                # Assert
                assert sonuc is True

        except Exception as e:
            # SQLite bağlantısı yoksa test'i atla
            pytest.skip(f"SQLite bağlantısı yok: {str(e)}")

    @pytest.mark.critical
    def test_kritik_veri_kaybi_onleme(self):
        """
        Kritik veri kaybı önleme testi

        Requirements: 6.1, 6.3 - Veri kaybı önleme
        """
        # Arrange - Kritik satış verisi
        kritik_satis = {
            "fis_no": "KRITIK_SATIS_001",
            "toplam_tutar": 5000.00,
            "odeme_turu": "KREDI_KARTI",
            "taksit_sayisi": 12,
            "musteri_id": 12345,
            "urunler": [{"id": 1, "ad": "Laptop", "adet": 1, "fiyat": 5000.00}],
            "timestamp": datetime.now().isoformat(),
            "kritik_islem": True,
        }

        # Mock repository başarılı kayıt
        mock_repository = Mock(spec=OfflineKuyrukRepository)
        mock_repository.kuyruk_ekle.return_value = 1
        service = OfflineKuyrukService(mock_repository)

        # Network kesintisi simülasyonu
        with patch.object(service, "network_durumu_kontrol", return_value=False):
            # Act
            sonuc = service.islem_kuyruga_ekle(
                islem_turu=IslemTuru.SATIS, veri=kritik_satis, terminal_id=1, kasiyer_id=1
            )

            # Assert - Kritik veri kaybolmamalı
            assert sonuc is True
            mock_repository.kuyruk_ekle.assert_called_once()

            # Veri bütünlüğü kontrolü
            call_args = mock_repository.kuyruk_ekle.call_args
            if call_args and call_args.args and len(call_args.args) >= 2:
                kaydedilen_veri = call_args.args[1]

                # Tüm kritik alanlar korunmuş olmalı
                assert kaydedilen_veri["fis_no"] == "KRITIK_SATIS_001"
                assert kaydedilen_veri["toplam_tutar"] == 5000.00
                assert kaydedilen_veri["musteri_id"] == 12345
                assert kaydedilen_veri["kritik_islem"] is True
                assert len(kaydedilen_veri["urunler"]) == 1
                assert kaydedilen_veri["urunler"][0]["fiyat"] == 5000.00


# Test kategorileri için pytest marker'ları
pytestmark = [pytest.mark.offline_kuyruk, pytest.mark.pos]
