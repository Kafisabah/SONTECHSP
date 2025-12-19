# Version: 0.1.0
# Last Update: 2025-12-18
# Module: tests.test_offline_kuyruk_kayit_isleme_property
# Description: Offline kuyruk kayıt-işleme property testi
# Changelog:
# - İlk oluşturma

"""
Offline Kuyruk Kayıt-İşleme Property Testi

Bu modül offline kuyruk sisteminin kayıt ekleme ve işleme süreçlerini
property-based testing ile doğrular.

**Feature: test-stabilizasyon-paketi, Property 15: Offline kuyruk kayıt-işleme**
**Validates: Requirements 6.1, 6.3**
"""

import pytest
from datetime import datetime, timedelta
from typing import List, Dict, Any
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, assume, settings, strategies as st

from sontechsp.uygulama.moduller.pos.repositories.offline_kuyruk_repository_backup import OfflineKuyrukRepository
from sontechsp.uygulama.moduller.pos.services.offline_kuyruk_service import OfflineKuyrukService
from sontechsp.uygulama.moduller.pos.arayuzler import IslemTuru, KuyrukDurum
from sontechsp.uygulama.cekirdek.hatalar import DogrulamaHatasi, VeritabaniHatasi, NetworkHatasi


class TestOfflineKuyrukKayitIslemeProperty:
    """Offline kuyruk kayıt-işleme property testleri"""

    def setup_method(self):
        """Her test öncesi çalışır"""
        self.mock_repository = Mock(spec=OfflineKuyrukRepository)
        self.service = OfflineKuyrukService(self.mock_repository)

    @given(
        islem_turu=st.sampled_from(list(IslemTuru)),
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=50),
        islem_sayisi=st.integers(min_value=1, max_value=10),
    )
    @settings(max_examples=100, deadline=5000)
    def test_offline_kuyruk_kayit_isleme_property(
        self, islem_turu: IslemTuru, terminal_id: int, kasiyer_id: int, islem_sayisi: int
    ):
        """
        **Feature: test-stabilizasyon-paketi, Property 15: Offline kuyruk kayıt-işleme**

        For any internet kesintisi, işlemler SQLite kuyruğuna kaydedilmeli ve bağlantı gelince işlenmeli
        **Validates: Requirements 6.1, 6.3**

        Herhangi bir internet kesintisi durumunda, işlemler SQLite kuyruğuna kaydedilmeli
        ve internet bağlantısı geri geldiğinde sırayla işlenmelidir.
        """
        # Arrange - Network kesintisi simülasyonu
        # Mock'u sıfırla (Hypothesis çoklu çalıştırma için)
        self.mock_repository.reset_mock()

        with patch.object(self.service, "network_durumu_kontrol", return_value=False):
            # Mock repository davranışları
            self.mock_repository.kuyruk_ekle.return_value = 1

            # Test verisi oluştur
            test_verileri = []
            for i in range(islem_sayisi):
                veri = {
                    "islem_no": i + 1,
                    "islem_turu": islem_turu.value,
                    "terminal_id": terminal_id,
                    "kasiyer_id": kasiyer_id,
                    "timestamp": datetime.now().isoformat(),
                }
                test_verileri.append(veri)

            # Act - İşlemleri offline kuyruğa ekle
            eklenen_islemler = []
            for veri in test_verileri:
                sonuc = self.service.islem_kuyruga_ekle(
                    islem_turu=islem_turu, veri=veri, terminal_id=terminal_id, kasiyer_id=kasiyer_id
                )
                eklenen_islemler.append(sonuc)

            # Assert - Tüm işlemler kuyruğa eklenmiş olmalı
            assert len(eklenen_islemler) == islem_sayisi
            assert all(sonuc is True for sonuc in eklenen_islemler)

            # Repository'nin doğru çağrıldığını kontrol et
            assert self.mock_repository.kuyruk_ekle.call_count == islem_sayisi

            # Her çağrının doğru parametrelerle yapıldığını kontrol et
            for i, call_args in enumerate(self.mock_repository.kuyruk_ekle.call_args_list):
                args, kwargs = call_args
                assert args[0] == islem_turu  # islem_turu
                assert args[1] == test_verileri[i]  # veri
                assert args[2] == terminal_id  # terminal_id
                assert args[3] == kasiyer_id  # kasiyer_id

    @given(
        bekleyen_islem_sayisi=st.integers(min_value=1, max_value=8),
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=50),
    )
    @settings(max_examples=100, deadline=5000)
    def test_network_geri_gelince_senkronizasyon_property(
        self, bekleyen_islem_sayisi: int, terminal_id: int, kasiyer_id: int
    ):
        """
        **Feature: test-stabilizasyon-paketi, Property 15: Offline kuyruk kayıt-işleme**

        For any network geri gelme durumu, bekleyen işlemler sırayla işlenmeli
        **Validates: Requirements 6.3**

        Herhangi bir network geri gelme durumunda, bekleyen işlemler
        sırayla işlenmeli ve başarılı olanlar kuyruktan silinmelidir.
        """
        # Arrange - Network geri geldi simülasyonu
        with patch.object(self.service, "network_durumu_kontrol", return_value=True):
            # Mock bekleyen işlemler
            bekleyen_islemler = []
            for i in range(bekleyen_islem_sayisi):
                islem = {
                    "id": i + 1,
                    "islem_turu": IslemTuru.SATIS.value,
                    "durum": KuyrukDurum.BEKLEMEDE.value,
                    "veri": {"islem_no": i + 1},
                    "terminal_id": terminal_id,
                    "kasiyer_id": kasiyer_id,
                    "oncelik": 1,
                    "islem_tarihi": datetime.now().isoformat(),
                }
                bekleyen_islemler.append(islem)

            # Mock repository davranışları
            self.mock_repository.bekleyen_kuyruk_listesi.return_value = bekleyen_islemler
            self.mock_repository.kuyruk_durum_guncelle.return_value = True

            # Mock başarılı işlem gönderimi
            with patch.object(self.service, "_kuyruk_islemini_gonder", return_value=True):
                # Act - Kuyruk senkronizasyonu
                islenen_sayisi = self.service.kuyruk_senkronize_et()

                # Assert - Tüm işlemler işlenmiş olmalı
                assert islenen_sayisi == bekleyen_islem_sayisi

                # Repository metodlarının doğru çağrıldığını kontrol et
                self.mock_repository.bekleyen_kuyruk_listesi.assert_called()

                # Her işlem için durum güncellemesi yapılmış olmalı
                durum_guncelleme_cagrisi = self.mock_repository.kuyruk_durum_guncelle.call_count
                assert durum_guncelleme_cagrisi >= bekleyen_islem_sayisi * 2  # ISLENIYOR + TAMAMLANDI

    @given(
        basarili_islem_sayisi=st.integers(min_value=1, max_value=5),
        basarisiz_islem_sayisi=st.integers(min_value=1, max_value=5),
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=50),
    )
    @settings(max_examples=100, deadline=5000)
    def test_karmasik_senkronizasyon_property(
        self, basarili_islem_sayisi: int, basarisiz_islem_sayisi: int, terminal_id: int, kasiyer_id: int
    ):
        """
        **Feature: test-stabilizasyon-paketi, Property 15: Offline kuyruk kayıt-işleme**

        For any karmaşık senkronizasyon senaryosu, başarılı ve başarısız işlemler doğru yönetilmeli
        **Validates: Requirements 6.3**

        Herhangi bir karmaşık senkronizasyon senaryosunda, başarılı işlemler tamamlanmalı,
        başarısız işlemler tekrar deneme için beklemede kalmalıdır.
        """
        # Arrange - Network aktif
        with patch.object(self.service, "network_durumu_kontrol", return_value=True):
            toplam_islem_sayisi = basarili_islem_sayisi + basarisiz_islem_sayisi

            # Mock bekleyen işlemler
            bekleyen_islemler = []
            for i in range(toplam_islem_sayisi):
                islem = {
                    "id": i + 1,
                    "islem_turu": IslemTuru.SATIS.value,
                    "durum": KuyrukDurum.BEKLEMEDE.value,
                    "veri": {"islem_no": i + 1},
                    "terminal_id": terminal_id,
                    "kasiyer_id": kasiyer_id,
                    "oncelik": 1,
                    "islem_tarihi": datetime.now().isoformat(),
                }
                bekleyen_islemler.append(islem)

            # Mock repository davranışları
            self.mock_repository.bekleyen_kuyruk_listesi.return_value = bekleyen_islemler
            self.mock_repository.kuyruk_durum_guncelle.return_value = True
            self.mock_repository.kuyruk_deneme_artir.return_value = True

            # Mock işlem gönderimi - ilk N tanesi başarılı, geri kalanı başarısız
            def mock_islem_gonder(islem):
                islem_no = islem["veri"]["islem_no"]
                return islem_no <= basarili_islem_sayisi

            with patch.object(self.service, "_kuyruk_islemini_gonder", side_effect=mock_islem_gonder):
                # Act - Kuyruk senkronizasyonu
                islenen_sayisi = self.service.kuyruk_senkronize_et()

                # Assert - Sadece başarılı işlemler işlenmiş olmalı
                assert islenen_sayisi == basarili_islem_sayisi

                # Repository metodlarının doğru çağrıldığını kontrol et
                self.mock_repository.bekleyen_kuyruk_listesi.assert_called()

                # Başarılı işlemler için TAMAMLANDI durumu
                tamamlandi_cagrisi = [
                    call
                    for call in self.mock_repository.kuyruk_durum_guncelle.call_args_list
                    if len(call[0]) > 1 and call[0][1] == KuyrukDurum.TAMAMLANDI
                ]
                assert len(tamamlandi_cagrisi) == basarili_islem_sayisi

                # Başarısız işlemler için deneme artırma
                assert self.mock_repository.kuyruk_deneme_artir.call_count == basarisiz_islem_sayisi

    @given(
        islem_turu=st.sampled_from(list(IslemTuru)),
        terminal_id=st.integers(min_value=1, max_value=100),
        kasiyer_id=st.integers(min_value=1, max_value=50),
    )
    @settings(max_examples=100, deadline=5000)
    def test_network_durumu_degisimi_property(self, islem_turu: IslemTuru, terminal_id: int, kasiyer_id: int):
        """
        **Feature: test-stabilizasyon-paketi, Property 15: Offline kuyruk kayıt-işleme**

        For any network durumu değişimi, sistem uygun davranış sergilemeli
        **Validates: Requirements 6.1, 6.3**

        Herhangi bir network durumu değişiminde, sistem offline/online durumuna
        göre uygun davranış sergilemelidir.
        """
        # Test verisi
        veri = {"islem_no": 1, "islem_turu": islem_turu.value, "timestamp": datetime.now().isoformat()}

        # Senaryo 1: Network yok - kuyruğa ekle
        with patch.object(self.service, "network_durumu_kontrol", return_value=False):
            self.mock_repository.kuyruk_ekle.return_value = 1

            # Act
            sonuc1 = self.service.islem_kuyruga_ekle(
                islem_turu=islem_turu, veri=veri, terminal_id=terminal_id, kasiyer_id=kasiyer_id
            )

            # Assert - Kuyruğa eklendi
            assert sonuc1 is True
            self.mock_repository.kuyruk_ekle.assert_called()

        # Senaryo 2: Network var - direkt gönder veya kuyruğa ekle
        with patch.object(self.service, "network_durumu_kontrol", return_value=True):
            with patch.object(self.service, "_islem_direkt_gonder", return_value=True):
                self.mock_repository.reset_mock()

                # Act
                sonuc2 = self.service.islem_kuyruga_ekle(
                    islem_turu=islem_turu, veri=veri, terminal_id=terminal_id, kasiyer_id=kasiyer_id
                )

                # Assert - İşlem başarılı
                assert sonuc2 is True

    @given(terminal_id=st.integers(min_value=1, max_value=100), kasiyer_id=st.integers(min_value=1, max_value=50))
    @settings(max_examples=100, deadline=5000)
    def test_network_kesintisi_sirasinda_kayit_property(self, terminal_id: int, kasiyer_id: int):
        """
        **Feature: test-stabilizasyon-paketi, Property 15: Offline kuyruk kayıt-işleme**

        For any network kesintisi sırasında kayıt, işlem güvenli şekilde saklanmalı
        **Validates: Requirements 6.1**

        Herhangi bir network kesintisi sırasında, işlemler güvenli şekilde
        SQLite kuyruğuna saklanmalı ve veri kaybı olmamalıdır.
        """
        # Arrange - Network kesintisi
        with patch.object(self.service, "network_durumu_kontrol", return_value=False):
            # Mock repository başarılı kayıt
            self.mock_repository.kuyruk_ekle.return_value = 1

            # Test verisi
            veri = {
                "islem_no": 1,
                "islem_turu": IslemTuru.SATIS.value,
                "terminal_id": terminal_id,
                "kasiyer_id": kasiyer_id,
                "timestamp": datetime.now().isoformat(),
                "kritik_veri": "Bu veri kaybolmamalı",
            }

            # Act - İşlemi kuyruğa ekle
            sonuc = self.service.islem_kuyruga_ekle(
                islem_turu=IslemTuru.SATIS, veri=veri, terminal_id=terminal_id, kasiyer_id=kasiyer_id
            )

            # Assert - İşlem başarılı ve veri korunmuş
            assert sonuc is True

            # Repository'nin doğru parametrelerle çağrıldığını kontrol et
            call_args = self.mock_repository.kuyruk_ekle.call_args
            args, kwargs = call_args

            assert args[0] == IslemTuru.SATIS  # islem_turu
            assert args[1] == veri  # veri - tam olarak aynı
            assert args[2] == terminal_id  # terminal_id
            assert args[3] == kasiyer_id  # kasiyer_id

            # Kritik verinin korunduğunu kontrol et
            assert args[1]["kritik_veri"] == "Bu veri kaybolmamalı"

    def test_gecersiz_parametreler_kayit_isleme(self):
        """
        Geçersiz parametrelerle kayıt-işleme testleri

        Geçersiz parametreler verildiğinde uygun hatalar fırlatılmalıdır.
        """
        # Arrange & Act & Assert - Geçersiz terminal_id
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
        Network hatası durumunda senkronizasyon testleri

        Network hatası oluştuğunda uygun hata yönetimi yapılmalıdır.
        """
        # Arrange - Network yok
        with patch.object(self.service, "network_durumu_kontrol", return_value=False):
            # Act & Assert - Network hatası
            with pytest.raises(NetworkHatasi, match="Network bağlantısı yok"):
                self.service.kuyruk_senkronize_et()
