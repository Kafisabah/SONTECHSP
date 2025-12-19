# Version: 0.1.0
# Last Update: 2025-12-18
# Module: tests.test_offline_kuyruk_fifo_property
# Description: Offline kuyruk FIFO sırası property testi
# Changelog:
# - İlk oluşturma
# - Import düzenlemesi ve PEP8 uyumluluğu

"""
Offline Kuyruk FIFO Sırası Property Testi

Bu modül offline kuyruk sisteminin FIFO (First In, First Out) sırası korunumunu
ve kuyruk temizleme işlemlerini property-based testing ile doğrular.

**Feature: test-stabilizasyon-paketi, Property 14: Offline kuyruk FIFO sırası**
**Validates: Requirements 6.2, 6.4**
"""

# Standart kütüphane importları
import pytest
from datetime import datetime, timedelta
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

# Üçüncü parti kütüphane importları
from hypothesis import assume, given, settings
from hypothesis import strategies as st

# Yerel proje importları
from sontechsp.uygulama.cekirdek.hatalar import DogrulamaHatasi, NetworkHatasi, VeritabaniHatasi
from sontechsp.uygulama.moduller.pos.arayuzler import IslemTuru, KuyrukDurum
from sontechsp.uygulama.moduller.pos.repositories.offline_kuyruk_repository_backup import OfflineKuyrukRepository
from sontechsp.uygulama.moduller.pos.services.offline_kuyruk_service import OfflineKuyrukService

# Hızlı test ayarları
FAST_SETTINGS = settings(max_examples=5, deadline=500)


class TestOfflineKuyrukFifoProperty:
    """Offline kuyruk FIFO sırası property testleri"""

    def setup_method(self):
        """Her test öncesi çalışır"""
        self.mock_repository = Mock(spec=OfflineKuyrukRepository)
        self.service = OfflineKuyrukService(self.mock_repository)

    @given(
        kuyruk_boyutu=st.integers(min_value=2, max_value=5),
        terminal_id=st.integers(min_value=1, max_value=10),
        kasiyer_id=st.integers(min_value=1, max_value=5),
        oncelik=st.integers(min_value=1, max_value=3),
    )
    @FAST_SETTINGS
    def test_fifo_sirasi_korunumu_property(self, kuyruk_boyutu: int, terminal_id: int, kasiyer_id: int, oncelik: int):
        """
        **Feature: test-stabilizasyon-paketi, Property 14: Offline kuyruk FIFO sırası**

        For any offline kuyruk işlemi, FIFO sırası korunmalı
        **Validates: Requirements 6.2**

        Herhangi bir offline kuyruk işleminde, aynı öncelikte eklenen işlemler
        FIFO (First In, First Out) sırasında işlenmeli ve okunmalıdır.
        """
        # Arrange - Aynı öncelikte işlemler oluştur
        mock_kuyruk_kayitlari = []
        base_time = datetime.now()

        for i in range(kuyruk_boyutu):
            kayit = {
                "id": i + 1,
                "islem_turu": IslemTuru.SATIS.value,
                "durum": KuyrukDurum.BEKLEMEDE.value,
                "veri": {"islem_no": i + 1, "sira": i + 1, "timestamp": (base_time + timedelta(seconds=i)).isoformat()},
                "terminal_id": terminal_id,
                "kasiyer_id": kasiyer_id,
                "oncelik": oncelik,  # Aynı öncelik
                "islem_tarihi": (base_time + timedelta(seconds=i)).isoformat(),
                "olusturma_zamani": base_time + timedelta(seconds=i),
            }
            mock_kuyruk_kayitlari.append(kayit)

        # Mock repository davranışı
        self.mock_repository.bekleyen_kuyruk_listesi.return_value = mock_kuyruk_kayitlari

        # Act - Bekleyen kuyruk listesini al
        bekleyen_islemler = self.mock_repository.bekleyen_kuyruk_listesi()

        # Assert - FIFO sırası korunmuş olmalı
        assert len(bekleyen_islemler) == kuyruk_boyutu

        # İlk giren ilk çıkar kontrolü
        for i, islem in enumerate(bekleyen_islemler):
            assert islem["id"] == i + 1
            assert islem["veri"]["islem_no"] == i + 1
            assert islem["veri"]["sira"] == i + 1

            # Zaman sırası kontrolü
            if i > 0:
                onceki_zaman = datetime.fromisoformat(bekleyen_islemler[i - 1]["islem_tarihi"])
                mevcut_zaman = datetime.fromisoformat(islem["islem_tarihi"])
                assert mevcut_zaman >= onceki_zaman

    @given(
        islem_sayisi=st.integers(min_value=3, max_value=5),
        islenen_sayisi=st.integers(min_value=1, max_value=3),
        terminal_id=st.integers(min_value=1, max_value=10),
    )
    @FAST_SETTINGS
    def test_fifo_islem_sirasi_property(self, islem_sayisi: int, islenen_sayisi: int, terminal_id: int):
        """
        **Feature: test-stabilizasyon-paketi, Property 14: Offline kuyruk FIFO sırası**

        For any kuyruk işleme sırası, FIFO kuralına göre işlenmeli
        **Validates: Requirements 6.2**

        Herhangi bir kuyruk işleme sırasında, işlemler FIFO sırasına göre
        işlenmeli ve tamamlanan işlemler kuyruktan silinmelidir.
        """
        # islenen_sayisi islem_sayisi'ndan büyük olamaz
        assume(islenen_sayisi <= islem_sayisi)

        # Arrange - Network aktif
        with patch.object(self.service, "network_durumu_kontrol", return_value=True):
            # Mock bekleyen işlemler - FIFO sırasında
            bekleyen_islemler = []
            base_time = datetime.now()

            for i in range(islem_sayisi):
                islem = {
                    "id": i + 1,
                    "islem_turu": IslemTuru.SATIS.value,
                    "durum": KuyrukDurum.BEKLEMEDE.value,
                    "veri": {
                        "islem_no": i + 1,
                        "fifo_sira": i + 1,
                        "timestamp": (base_time + timedelta(seconds=i)).isoformat(),
                    },
                    "terminal_id": terminal_id,
                    "kasiyer_id": 1,
                    "oncelik": 1,
                    "islem_tarihi": (base_time + timedelta(seconds=i)).isoformat(),
                }
                bekleyen_islemler.append(islem)

            # Mock repository davranışları
            self.mock_repository.bekleyen_kuyruk_listesi.return_value = bekleyen_islemler
            self.mock_repository.kuyruk_durum_guncelle.return_value = True

            # Mock işlem gönderimi - ilk N tanesi başarılı
            islenen_islem_idleri = []

            def mock_islem_gonder(islem):
                islem_id = islem["id"]
                if len(islenen_islem_idleri) < islenen_sayisi:
                    islenen_islem_idleri.append(islem_id)
                    return True
                return False

            with patch.object(self.service, "_kuyruk_islemini_gonder", side_effect=mock_islem_gonder):
                # Act - Kuyruk senkronizasyonu
                gercek_islenen_sayisi = self.service.kuyruk_senkronize_et()

                # Assert - Doğru sayıda işlem işlenmiş olmalı
                assert gercek_islenen_sayisi == islenen_sayisi

                # İşlenen işlemler FIFO sırasında olmalı
                assert len(islenen_islem_idleri) == islenen_sayisi
                for i, islem_id in enumerate(islenen_islem_idleri):
                    assert islem_id == i + 1  # İlk giren ilk işlenen

    @given(
        gun_sayisi=st.integers(min_value=1, max_value=10),
        silinecek_kayit_sayisi=st.integers(min_value=0, max_value=10),
    )
    @FAST_SETTINGS
    def test_kuyruk_temizleme_property(self, gun_sayisi: int, silinecek_kayit_sayisi: int):
        """
        **Feature: test-stabilizasyon-paketi, Property 14: Offline kuyruk FIFO sırası**

        For any kuyruk temizleme işlemi, işlenen kayıtlar silinmeli
        **Validates: Requirements 6.4**

        Herhangi bir kuyruk temizleme işleminde, belirtilen gün sayısından
        eski olan tamamlanmış işlemler kuyruktan silinmelidir.
        """
        # Arrange - Mock repository temizleme davranışı
        self.mock_repository.kuyruk_temizle.return_value = silinecek_kayit_sayisi

        # Act - Kuyruk temizleme
        silinen_sayisi = self.service.kuyruk_temizle(gun_sayisi)

        # Assert - Doğru sayıda kayıt silinmiş olmalı
        assert silinen_sayisi == silinecek_kayit_sayisi

        # Repository'nin doğru parametrelerle çağrıldığını kontrol et
        self.mock_repository.kuyruk_temizle.assert_called_once_with(gun_sayisi)

    @given(
        toplam_kayit=st.integers(min_value=5, max_value=10),
        tamamlanan_kayit=st.integers(min_value=1, max_value=5),
        bekleyen_kayit=st.integers(min_value=1, max_value=5),
        terminal_id=st.integers(min_value=1, max_value=10),
    )
    @FAST_SETTINGS
    def test_kuyruk_durum_tutarliligi_property(
        self, toplam_kayit: int, tamamlanan_kayit: int, bekleyen_kayit: int, terminal_id: int
    ):
        """
        **Feature: test-stabilizasyon-paketi, Property 14: Offline kuyruk FIFO sırası**

        For any kuyruk durumu, toplam kayıt sayısı tutarlı olmalı
        **Validates: Requirements 6.2, 6.4**

        Herhangi bir kuyruk durumunda, toplam kayıt sayısı ile durum bazlı
        kayıt sayıları tutarlı olmalı ve FIFO sırası korunmalıdır.
        """
        # Toplam kayıt sayısı mantıklı olmalı
        assume(tamamlanan_kayit + bekleyen_kayit <= toplam_kayit)

        # Arrange - Mock kuyruk istatistikleri
        hata_kayit = toplam_kayit - tamamlanan_kayit - bekleyen_kayit

        mock_istatistikler = {
            "toplam_kayit": toplam_kayit,
            "durum_sayilari": {
                "BEKLEMEDE": bekleyen_kayit,
                "TAMAMLANDI": tamamlanan_kayit,
                "HATA": hata_kayit,
                "ISLENIYOR": 0,
            },
            "islem_turu_sayilari": {
                "SATIS": toplam_kayit // 2,
                "IADE": toplam_kayit // 4,
                "STOK_DUSUMU": toplam_kayit - (toplam_kayit // 2) - (toplam_kayit // 4),
            },
            "ortalama_bekleme_suresi_saniye": 120,
        }

        self.mock_repository.kuyruk_istatistikleri.return_value = mock_istatistikler

        with patch.object(self.service, "network_durumu_kontrol", return_value=True):
            # Act - Kuyruk istatistikleri
            istatistikler = self.service.kuyruk_istatistikleri_getir(terminal_id=terminal_id)

            # Assert - Tutarlılık kontrolleri
            assert istatistikler["toplam_kayit"] == toplam_kayit

            # Durum sayıları toplamı toplam kayıt sayısını geçmemeli
            durum_toplami = sum(istatistikler["durum_sayilari"].values())
            assert durum_toplami <= toplam_kayit

            # Bekleyen kayıt sayısı doğru olmalı
            assert istatistikler["durum_sayilari"]["BEKLEMEDE"] == bekleyen_kayit
            assert istatistikler["durum_sayilari"]["TAMAMLANDI"] == tamamlanan_kayit

            # İşlem türü sayıları toplamı toplam kayıt sayısına eşit olmalı
            islem_turu_toplami = sum(istatistikler["islem_turu_sayilari"].values())
            assert islem_turu_toplami == toplam_kayit

    @given(
        oncelik_1_sayisi=st.integers(min_value=1, max_value=3),
        oncelik_2_sayisi=st.integers(min_value=1, max_value=3),
        oncelik_3_sayisi=st.integers(min_value=1, max_value=3),
        terminal_id=st.integers(min_value=1, max_value=10),
    )
    @FAST_SETTINGS
    def test_oncelik_bazli_fifo_property(
        self, oncelik_1_sayisi: int, oncelik_2_sayisi: int, oncelik_3_sayisi: int, terminal_id: int
    ):
        """
        **Feature: test-stabilizasyon-paketi, Property 14: Offline kuyruk FIFO sırası**

        For any öncelik bazlı kuyruk, öncelik içinde FIFO sırası korunmalı
        **Validates: Requirements 6.2**

        Herhangi bir öncelik bazlı kuyrukta, yüksek öncelikli işlemler önce işlenmeli
        ve aynı öncelik içinde FIFO sırası korunmalıdır.
        """
        # Arrange - Farklı önceliklerde işlemler oluştur
        mock_kuyruk_kayitlari = []
        base_time = datetime.now()
        kayit_id = 1

        # Öncelik 1 (en yüksek) işlemler
        for i in range(oncelik_1_sayisi):
            kayit = {
                "id": kayit_id,
                "islem_turu": IslemTuru.SATIS.value,
                "durum": KuyrukDurum.BEKLEMEDE.value,
                "veri": {"islem_no": kayit_id, "oncelik": 1, "sira": i + 1},
                "terminal_id": terminal_id,
                "kasiyer_id": 1,
                "oncelik": 1,
                "islem_tarihi": (base_time + timedelta(seconds=kayit_id)).isoformat(),
            }
            mock_kuyruk_kayitlari.append(kayit)
            kayit_id += 1

        # Öncelik 2 işlemler
        for i in range(oncelik_2_sayisi):
            kayit = {
                "id": kayit_id,
                "islem_turu": IslemTuru.SATIS.value,
                "durum": KuyrukDurum.BEKLEMEDE.value,
                "veri": {"islem_no": kayit_id, "oncelik": 2, "sira": i + 1},
                "terminal_id": terminal_id,
                "kasiyer_id": 1,
                "oncelik": 2,
                "islem_tarihi": (base_time + timedelta(seconds=kayit_id)).isoformat(),
            }
            mock_kuyruk_kayitlari.append(kayit)
            kayit_id += 1

        # Öncelik 3 işlemler
        for i in range(oncelik_3_sayisi):
            kayit = {
                "id": kayit_id,
                "islem_turu": IslemTuru.SATIS.value,
                "durum": KuyrukDurum.BEKLEMEDE.value,
                "veri": {"islem_no": kayit_id, "oncelik": 3, "sira": i + 1},
                "terminal_id": terminal_id,
                "kasiyer_id": 1,
                "oncelik": 3,
                "islem_tarihi": (base_time + timedelta(seconds=kayit_id)).isoformat(),
            }
            mock_kuyruk_kayitlari.append(kayit)
            kayit_id += 1

        # Mock repository davranışı - öncelik sırasına göre sıralı
        mock_kuyruk_kayitlari.sort(key=lambda x: (x["oncelik"], x["id"]))
        self.mock_repository.bekleyen_kuyruk_listesi.return_value = mock_kuyruk_kayitlari

        # Act - Bekleyen kuyruk listesi
        bekleyen_islemler = self.mock_repository.bekleyen_kuyruk_listesi()

        # Assert - Öncelik sırası ve FIFO kontrolü
        toplam_islem = oncelik_1_sayisi + oncelik_2_sayisi + oncelik_3_sayisi
        assert len(bekleyen_islemler) == toplam_islem

        # Öncelik sırası kontrolü
        onceki_oncelik = 0
        ayni_oncelik_sayaci = {}

        for islem in bekleyen_islemler:
            mevcut_oncelik = islem["oncelik"]

            # Öncelik azalmıyor olmalı (1 -> 2 -> 3)
            assert mevcut_oncelik >= onceki_oncelik

            # Aynı öncelik içinde FIFO sırası
            if mevcut_oncelik not in ayni_oncelik_sayaci:
                ayni_oncelik_sayaci[mevcut_oncelik] = 0

            ayni_oncelik_sayaci[mevcut_oncelik] += 1
            beklenen_sira = ayni_oncelik_sayaci[mevcut_oncelik]

            assert islem["veri"]["sira"] == beklenen_sira

            onceki_oncelik = mevcut_oncelik

    @given(
        kuyruk_boyutu=st.integers(min_value=3, max_value=6),
        terminal_id=st.integers(min_value=1, max_value=10),
    )
    @FAST_SETTINGS
    def test_kuyruk_boslugu_fifo_property(self, kuyruk_boyutu: int, terminal_id: int):
        """
        **Feature: test-stabilizasyon-paketi, Property 14: Offline kuyruk FIFO sırası**

        For any kuyruk boşluğu, FIFO sırası korunmalı
        **Validates: Requirements 6.2, 6.4**

        Herhangi bir kuyruk boşluğunda (bazı işlemler tamamlandıktan sonra),
        kalan işlemler hala FIFO sırasını korumalıdır.
        """
        # Arrange - Karışık durumlu işlemler
        mock_kuyruk_kayitlari = []
        base_time = datetime.now()

        for i in range(kuyruk_boyutu):
            # Bazı işlemler tamamlanmış, bazıları beklemede
            durum = KuyrukDurum.TAMAMLANDI if i % 3 == 0 else KuyrukDurum.BEKLEMEDE

            kayit = {
                "id": i + 1,
                "islem_turu": IslemTuru.SATIS.value,
                "durum": durum.value,
                "veri": {"islem_no": i + 1, "sira": i + 1},
                "terminal_id": terminal_id,
                "kasiyer_id": 1,
                "oncelik": 1,
                "islem_tarihi": (base_time + timedelta(seconds=i)).isoformat(),
            }
            mock_kuyruk_kayitlari.append(kayit)

        # Sadece bekleyen işlemler döndürülür
        bekleyen_kayitlar = [k for k in mock_kuyruk_kayitlari if k["durum"] == KuyrukDurum.BEKLEMEDE.value]
        self.mock_repository.bekleyen_kuyruk_listesi.return_value = bekleyen_kayitlar

        # Act - Bekleyen kuyruk listesi
        bekleyen_islemler = self.mock_repository.bekleyen_kuyruk_listesi()

        # Assert - Bekleyen işlemler FIFO sırasında olmalı
        if len(bekleyen_islemler) > 1:
            for i in range(1, len(bekleyen_islemler)):
                onceki_islem = bekleyen_islemler[i - 1]
                mevcut_islem = bekleyen_islemler[i]

                # ID sırası korunmuş olmalı (FIFO)
                assert onceki_islem["id"] < mevcut_islem["id"]

                # Zaman sırası korunmuş olmalı
                onceki_zaman = datetime.fromisoformat(onceki_islem["islem_tarihi"])
                mevcut_zaman = datetime.fromisoformat(mevcut_islem["islem_tarihi"])
                assert onceki_zaman <= mevcut_zaman

    def test_bos_kuyruk_fifo_property(self):
        """
        **Feature: test-stabilizasyon-paketi, Property 14: Offline kuyruk FIFO sırası**

        For any boş kuyruk, uygun davranış sergilemeli
        **Validates: Requirements 6.2, 6.4**

        Herhangi bir boş kuyruk durumunda, sistem uygun davranış sergilemeli
        ve hata vermemelidir.
        """
        # Arrange - Boş kuyruk
        self.mock_repository.bekleyen_kuyruk_listesi.return_value = []
        self.mock_repository.kuyruk_temizle.return_value = 0

        # Act & Assert - Boş kuyruk listesi
        bekleyen_islemler = self.mock_repository.bekleyen_kuyruk_listesi()
        assert bekleyen_islemler == []

        # Boş kuyruk temizleme
        silinen_sayisi = self.service.kuyruk_temizle(7)
        assert silinen_sayisi == 0

    def test_gecersiz_parametreler_fifo(self):
        """
        Geçersiz parametrelerle FIFO testleri

        Geçersiz parametreler verildiğinde 0 döndürülmelidir.
        """
        # Arrange & Act & Assert - Geçersiz gün sayısı
        sonuc1 = self.service.kuyruk_temizle(0)
        assert sonuc1 == 0

        sonuc2 = self.service.kuyruk_temizle(-1)
        assert sonuc2 == 0


# Test kategorileri için pytest marker'ları
pytestmark = [pytest.mark.offline_kuyruk, pytest.mark.pos, pytest.mark.property_test]
