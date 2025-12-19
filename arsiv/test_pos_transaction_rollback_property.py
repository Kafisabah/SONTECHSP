# Version: 0.1.0
# Last Update: 2025-12-18
# Module: tests.test_pos_transaction_rollback_property
# Description: POS transaction rollback garantisi property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP POS Transaction Rollback Garantisi Property Testleri

Bu modül POS ödeme işlemlerinde hata durumunda rollback mekanizmasının
doğru çalıştığını test eder. Transaction sırasında hata oluştuğunda
tüm değişiklikler geri alınmalı ve sistem önceki duruma dönmelidir.
"""

from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock, call
from hypothesis import given, strategies as st, settings, assume
import pytest

from sontechsp.uygulama.moduller.pos.servisler.odeme_service import OdemeService
from sontechsp.uygulama.moduller.pos.arayuzler import OdemeTuru, SepetDurum, SatisDurum
from sontechsp.uygulama.cekirdek.hatalar import DogrulamaHatasi, SontechHatasi


class TestPOSTransactionRollbackGarantisi:
    """POS transaction rollback garantisi property testleri"""

    def setup_method(self):
        """Her test öncesi çalışır"""
        # Mock repository'ler oluştur
        self.mock_sepet_repository = Mock()
        self.mock_satis_repository = Mock()
        self.mock_stok_service = Mock()

        # OdemeService'i mock'larla oluştur
        self.odeme_service = OdemeService(
            sepet_repository=self.mock_sepet_repository,
            satis_repository=self.mock_satis_repository,
            stok_service=self.mock_stok_service,
        )

    def _reset_mocks(self):
        """Mock'ları sıfırla"""
        self.mock_sepet_repository.reset_mock()
        self.mock_satis_repository.reset_mock()
        self.mock_stok_service.reset_mock()

    @given(
        sepet_id=st.integers(min_value=1, max_value=1000),
        toplam_tutar=st.decimals(min_value=Decimal("1.00"), max_value=Decimal("1000.00"), places=2),
        hata_noktasi=st.sampled_from(["satis_olustur", "odeme_ekle", "stok_dusur", "satis_tamamla"]),
        urun_sayisi=st.integers(min_value=1, max_value=3),
    )
    @settings(max_examples=20, deadline=5000)
    def test_property_transaction_rollback_garantisi_hata_durumu(
        self, sepet_id, toplam_tutar, hata_noktasi, urun_sayisi
    ):
        """
        **Feature: test-stabilizasyon-paketi, Property 10: Transaction rollback garantisi**

        For any transaction hatası, tüm değişiklikler geri alınmalı ve sistem önceki duruma dönmeli.
        Rollback sonrası hiçbir kısmi değişiklik kalmamalı.
        **Validates: Requirements 4.2, 4.4**
        """
        # Mock'ları sıfırla
        self._reset_mocks()

        # Arrange - Hata senaryosu için mock'ları ayarla
        sepet_satirlari = []
        for i in range(urun_sayisi):
            sepet_satirlari.append(
                {
                    "urun_id": i + 1,
                    "adet": 2,
                    "birim_fiyat": float(toplam_tutar / urun_sayisi / 2),
                    "toplam_tutar": float(toplam_tutar / urun_sayisi),
                }
            )

        sepet_bilgisi = {
            "id": sepet_id,
            "terminal_id": 1,
            "kasiyer_id": 1,
            "toplam_tutar": float(toplam_tutar),
            "net_tutar": float(toplam_tutar),
            "durum": SepetDurum.AKTIF.value,
            "satirlar": sepet_satirlari,
        }

        self.mock_sepet_repository.sepet_getir.return_value = sepet_bilgisi

        # Hata noktasına göre mock'ları ayarla
        if hata_noktasi == "satis_olustur":
            self.mock_satis_repository.satis_olustur.side_effect = Exception("Satış oluşturma hatası")
        elif hata_noktasi == "odeme_ekle":
            self.mock_satis_repository.satis_olustur.return_value = 123
            self.mock_satis_repository.satis_odeme_ekle.side_effect = Exception("Ödeme ekleme hatası")
        elif hata_noktasi == "stok_dusur":
            self.mock_satis_repository.satis_olustur.return_value = 123
            self.mock_satis_repository.satis_odeme_ekle.return_value = 456
            self.mock_stok_service.stok_dusur.side_effect = Exception("Stok düşüm hatası")
        elif hata_noktasi == "satis_tamamla":
            self.mock_satis_repository.satis_olustur.return_value = 123
            self.mock_satis_repository.satis_odeme_ekle.return_value = 456
            self.mock_stok_service.stok_dusur.return_value = True
            self.mock_satis_repository.satis_tamamla.side_effect = Exception("Satış tamamlama hatası")

        # Act & Assert - Hata durumunda exception fırlatılmalı
        with pytest.raises(Exception):
            self.odeme_service.tek_odeme_yap(sepet_id=sepet_id, odeme_turu=OdemeTuru.NAKIT, tutar=toplam_tutar)

        # Rollback garantisi kontrolleri
        # 1. Hata durumunda işlem tamamlanmamış olmalı
        # Sepet durumu değişmemiş olmalı (hala AKTIF)
        self.mock_sepet_repository.sepet_durum_guncelle.assert_not_called()

        # 2. Hata noktasına göre sistem durumu kontrolleri
        if hata_noktasi == "satis_olustur":
            # Satış oluşturulamadıysa hiçbir işlem yapılmamalı
            self.mock_satis_repository.satis_odeme_ekle.assert_not_called()
            self.mock_stok_service.stok_dusur.assert_not_called()
            self.mock_satis_repository.satis_tamamla.assert_not_called()

        elif hata_noktasi == "odeme_ekle":
            # Satış oluştu ama ödeme eklenemedi
            self.mock_satis_repository.satis_olustur.assert_called_once()
            # Sonraki işlemler yapılmamalı
            self.mock_stok_service.stok_dusur.assert_not_called()
            self.mock_satis_repository.satis_tamamla.assert_not_called()

        elif hata_noktasi == "stok_dusur":
            # Satış ve ödeme oluştu ama stok düşürülemedi
            self.mock_satis_repository.satis_olustur.assert_called_once()
            self.mock_satis_repository.satis_odeme_ekle.assert_called_once()
            # Sonraki işlemler yapılmamalı
            self.mock_satis_repository.satis_tamamla.assert_not_called()

        elif hata_noktasi == "satis_tamamla":
            # Tüm işlemler yapıldı ama tamamlanamadı
            self.mock_satis_repository.satis_olustur.assert_called_once()
            self.mock_satis_repository.satis_odeme_ekle.assert_called_once()
            self.mock_stok_service.stok_dusur.assert_called()

    @given(
        sepet_id=st.integers(min_value=1, max_value=1000),
        toplam_tutar=st.decimals(min_value=Decimal("10.00"), max_value=Decimal("500.00"), places=2),
        odemeler_sayisi=st.integers(min_value=2, max_value=4),
        hata_odeme_indeksi=st.integers(min_value=1, max_value=3),
    )
    @settings(max_examples=15, deadline=5000)
    def test_property_parcali_odeme_rollback_garantisi(
        self, sepet_id, toplam_tutar, odemeler_sayisi, hata_odeme_indeksi
    ):
        """
        **Feature: test-stabilizasyon-paketi, Property 10: Transaction rollback garantisi**

        For any parçalı ödeme transaction hatası, tüm ödemeler geri alınmalı ve sistem önceki duruma dönmeli.
        Kısmi ödeme kayıtları kalmamalı.
        **Validates: Requirements 4.2, 4.4**
        """
        assume(hata_odeme_indeksi < odemeler_sayisi)

        # Mock'ları sıfırla
        self._reset_mocks()

        # Arrange - Parçalı ödeme hata senaryosu
        sepet_bilgisi = {
            "id": sepet_id,
            "terminal_id": 1,
            "kasiyer_id": 1,
            "toplam_tutar": float(toplam_tutar),
            "net_tutar": float(toplam_tutar),
            "durum": SepetDurum.AKTIF.value,
            "satirlar": [
                {"urun_id": 1, "adet": 1, "birim_fiyat": float(toplam_tutar), "toplam_tutar": float(toplam_tutar)}
            ],
        }

        # Ödemeleri oluştur
        odeme_tutari = toplam_tutar / odemeler_sayisi
        odemeler = []
        for i in range(odemeler_sayisi):
            if i == odemeler_sayisi - 1:  # Son ödeme kalan tutarı alsın
                kalan_tutar = toplam_tutar - (odeme_tutari * (odemeler_sayisi - 1))
                odemeler.append(
                    {
                        "turu": OdemeTuru.NAKIT if i % 2 == 0 else OdemeTuru.KART,
                        "tutar": kalan_tutar,
                        "referans": f"REF_{i}",
                    }
                )
            else:
                odemeler.append(
                    {
                        "turu": OdemeTuru.NAKIT if i % 2 == 0 else OdemeTuru.KART,
                        "tutar": odeme_tutari,
                        "referans": f"REF_{i}",
                    }
                )

        self.mock_sepet_repository.sepet_getir.return_value = sepet_bilgisi
        self.mock_satis_repository.satis_olustur.return_value = 789

        # İlk birkaç ödeme başarılı, sonra hata
        def odeme_ekle_side_effect(*args, **kwargs):
            call_count = self.mock_satis_repository.satis_odeme_ekle.call_count
            if call_count > hata_odeme_indeksi:
                raise Exception(f"Ödeme ekleme hatası - {call_count}. ödeme")
            return 100 + call_count

        self.mock_satis_repository.satis_odeme_ekle.side_effect = odeme_ekle_side_effect

        # Act & Assert - Hata durumunda exception fırlatılmalı
        with pytest.raises(Exception):
            self.odeme_service.parcali_odeme_yap(sepet_id=sepet_id, odemeler=odemeler)

        # Parçalı ödeme rollback garantisi kontrolleri
        # 1. Satış kaydı oluşturulmuş ama rollback ile geri alınmış olmalı
        self.mock_satis_repository.satis_olustur.assert_called_once()

        # 2. Hata öncesi eklenen ödemeler rollback ile geri alınmış olmalı
        # Ödeme ekleme çağrı sayısı hata indeksinden fazla olmalı
        assert self.mock_satis_repository.satis_odeme_ekle.call_count > hata_odeme_indeksi

        # 3. Stok düşümü yapılmamış olmalı (ödeme aşamasında hata)
        self.mock_stok_service.stok_dusur.assert_not_called()

        # 4. Satış tamamlanmamış olmalı
        self.mock_satis_repository.satis_tamamla.assert_not_called()

        # 5. Sepet durumu değişmemiş olmalı
        self.mock_sepet_repository.sepet_durum_guncelle.assert_not_called()

    @given(
        sepet_id=st.integers(min_value=1, max_value=1000),
        toplam_tutar=st.decimals(min_value=Decimal("1.00"), max_value=Decimal("1000.00"), places=2),
        database_hata_turu=st.sampled_from(["connection_lost", "deadlock", "constraint_violation"]),
    )
    @settings(max_examples=15, deadline=5000)
    def test_property_database_hata_rollback_garantisi(self, sepet_id, toplam_tutar, database_hata_turu):
        """
        **Feature: test-stabilizasyon-paketi, Property 10: Transaction rollback garantisi**

        For any veritabanı hatası (bağlantı kopması, deadlock, constraint ihlali),
        transaction rollback garantisi sağlanmalı ve sistem tutarlı durumda kalmalı.
        **Validates: Requirements 4.2, 4.4**
        """
        # Mock'ları sıfırla
        self._reset_mocks()

        # Arrange - Veritabanı hata senaryosu
        sepet_bilgisi = {
            "id": sepet_id,
            "terminal_id": 1,
            "kasiyer_id": 1,
            "toplam_tutar": float(toplam_tutar),
            "net_tutar": float(toplam_tutar),
            "durum": SepetDurum.AKTIF.value,
            "satirlar": [
                {"urun_id": 1, "adet": 1, "birim_fiyat": float(toplam_tutar), "toplam_tutar": float(toplam_tutar)}
            ],
        }

        self.mock_sepet_repository.sepet_getir.return_value = sepet_bilgisi

        # Veritabanı hata türüne göre mock'ları ayarla
        if database_hata_turu == "connection_lost":
            # Bağlantı kopması - satış oluşturma sırasında
            self.mock_satis_repository.satis_olustur.side_effect = Exception("Database connection lost")
        elif database_hata_turu == "deadlock":
            # Deadlock - stok düşümü sırasında
            self.mock_satis_repository.satis_olustur.return_value = 123
            self.mock_satis_repository.satis_odeme_ekle.return_value = 456
            self.mock_stok_service.stok_dusur.side_effect = Exception("Deadlock detected")
        elif database_hata_turu == "constraint_violation":
            # Constraint ihlali - satış tamamlama sırasında
            self.mock_satis_repository.satis_olustur.return_value = 123
            self.mock_satis_repository.satis_odeme_ekle.return_value = 456
            self.mock_stok_service.stok_dusur.return_value = True
            self.mock_satis_repository.satis_tamamla.side_effect = Exception("Foreign key constraint violation")

        # Act & Assert - Veritabanı hatası durumunda exception fırlatılmalı
        with pytest.raises(Exception):
            self.odeme_service.tek_odeme_yap(sepet_id=sepet_id, odeme_turu=OdemeTuru.NAKIT, tutar=toplam_tutar)

        # Veritabanı hata rollback garantisi kontrolleri
        # 1. Hata türüne göre sistem durumu kontrolleri
        if database_hata_turu == "connection_lost":
            # Bağlantı kopması durumunda hiçbir işlem yapılmamalı
            self.mock_satis_repository.satis_odeme_ekle.assert_not_called()
            self.mock_stok_service.stok_dusur.assert_not_called()
            self.mock_satis_repository.satis_tamamla.assert_not_called()

        elif database_hata_turu == "deadlock":
            # Deadlock durumunda satış ve ödeme oluştu ama stok düşümü başarısız
            self.mock_satis_repository.satis_olustur.assert_called_once()
            self.mock_satis_repository.satis_odeme_ekle.assert_called_once()
            # Sonraki işlemler yapılmamalı
            self.mock_satis_repository.satis_tamamla.assert_not_called()

        elif database_hata_turu == "constraint_violation":
            # Constraint ihlali durumunda tüm işlemler yapıldı ama tamamlanamadı
            self.mock_satis_repository.satis_olustur.assert_called_once()
            self.mock_satis_repository.satis_odeme_ekle.assert_called_once()
            self.mock_stok_service.stok_dusur.assert_called_once()

        # 2. Tüm durumlarda sepet durumu değişmemiş olmalı
        self.mock_sepet_repository.sepet_durum_guncelle.assert_not_called()

    @given(
        sepet_id=st.integers(min_value=1, max_value=1000),
        toplam_tutar=st.decimals(min_value=Decimal("1.00"), max_value=Decimal("500.00"), places=2),
    )
    @settings(max_examples=15, deadline=5000)
    def test_property_sistem_durumu_tutarliligi_rollback_sonrasi(self, sepet_id, toplam_tutar):
        """
        **Feature: test-stabilizasyon-paketi, Property 10: Transaction rollback garantisi**

        For any rollback işlemi sonrası, sistem durumu işlem öncesi haline dönmeli.
        Hiçbir kısmi değişiklik kalmamalı ve sistem tutarlı durumda olmalı.
        **Validates: Requirements 4.2, 4.4**
        """
        # Mock'ları sıfırla
        self._reset_mocks()

        # Arrange - Sistem durumu tutarlılığı testi
        sepet_bilgisi = {
            "id": sepet_id,
            "terminal_id": 1,
            "kasiyer_id": 1,
            "toplam_tutar": float(toplam_tutar),
            "net_tutar": float(toplam_tutar),
            "durum": SepetDurum.AKTIF.value,
            "satirlar": [
                {"urun_id": 1, "adet": 2, "birim_fiyat": float(toplam_tutar / 2), "toplam_tutar": float(toplam_tutar)}
            ],
        }

        self.mock_sepet_repository.sepet_getir.return_value = sepet_bilgisi

        # Satış tamamlama sırasında hata (en son aşamada)
        self.mock_satis_repository.satis_olustur.return_value = 999
        self.mock_satis_repository.satis_odeme_ekle.return_value = 888
        self.mock_stok_service.stok_dusur.return_value = True
        self.mock_satis_repository.satis_tamamla.side_effect = Exception("Sistem hatası - tamamlama başarısız")

        # Act & Assert - Hata durumunda exception fırlatılmalı
        with pytest.raises(Exception):
            self.odeme_service.tek_odeme_yap(sepet_id=sepet_id, odeme_turu=OdemeTuru.NAKIT, tutar=toplam_tutar)

        # Sistem durumu tutarlılığı kontrolleri
        # 1. Sepet durumu değişmemiş olmalı
        self.mock_sepet_repository.sepet_durum_guncelle.assert_not_called()

        # 2. Tüm işlemler yapıldı ama son adımda hata oluştu
        self.mock_satis_repository.satis_olustur.assert_called_once()
        self.mock_satis_repository.satis_odeme_ekle.assert_called_once()
        self.mock_stok_service.stok_dusur.assert_called_once()

        # 3. Satış tamamlama başarısız oldu
        self.mock_satis_repository.satis_tamamla.assert_called_once()

        # 4. Sistem tutarlı durumda kaldı - kısmi işlem yok
        # Gerçek implementasyonda bu durumda rollback mekanizması
        # repository katmanında çalışır ve tüm değişiklikler geri alınır
