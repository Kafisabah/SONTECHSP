# Version: 0.1.0
# Last Update: 2025-12-18
# Module: tests.test_pos_transaction_atomikligi_property
# Description: POS transaction atomikliği property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP POS Transaction Atomikliği Property Testleri

Bu modül POS ödeme işlemlerinin atomik olduğunu test eder.
Stok düşümü + satış kaydı birlikte başarılı/başarısız olmalıdır.
"""

from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, strategies as st, settings, assume
import pytest

from sontechsp.uygulama.moduller.pos.servisler.odeme_service import OdemeService
from sontechsp.uygulama.moduller.pos.arayuzler import OdemeTuru, SepetDurum, SatisDurum
from sontechsp.uygulama.cekirdek.hatalar import DogrulamaHatasi, SontechHatasi


class TestPOSTransactionAtomikligi:
    """POS transaction atomikliği property testleri"""

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
        urun_sayisi=st.integers(min_value=1, max_value=5),
    )
    @settings(max_examples=50, deadline=10000)
    def test_property_pos_transaction_atomikligi_basarili_durum(self, sepet_id, toplam_tutar, urun_sayisi):
        """
        **Feature: test-stabilizasyon-paketi, Property 9: POS transaction atomikliği**

        For any POS ödeme işlemi, stok düşümü ve satış kaydı tek transaction içinde yapılmalı.
        Başarılı durumda hem stok düşümü hem satış kaydı tamamlanmalı.
        **Validates: Requirements 4.1**
        """
        # Mock'ları sıfırla
        self._reset_mocks()

        # Arrange - Başarılı senaryo için mock'ları ayarla
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

        # Mock repository yanıtları - başarılı durum
        self.mock_sepet_repository.sepet_getir.return_value = sepet_bilgisi
        self.mock_satis_repository.satis_olustur.return_value = 123  # satis_id
        self.mock_satis_repository.satis_odeme_ekle.return_value = 456  # odeme_id
        self.mock_satis_repository.satis_tamamla.return_value = True
        self.mock_sepet_repository.sepet_durum_guncelle.return_value = True
        self.mock_stok_service.stok_dusur.return_value = True

        # Act - Tek ödeme işlemi yap
        sonuc = self.odeme_service.tek_odeme_yap(sepet_id=sepet_id, odeme_turu=OdemeTuru.NAKIT, tutar=toplam_tutar)

        # Assert - Transaction atomikliği kontrolleri
        assert sonuc is True, "Ödeme işlemi başarılı olmalı"

        # 1. Satış kaydı oluşturulmuş olmalı
        self.mock_satis_repository.satis_olustur.assert_called_once()
        satis_args = self.mock_satis_repository.satis_olustur.call_args[1]
        assert satis_args["sepet_id"] == sepet_id
        assert satis_args["toplam_tutar"] == toplam_tutar

        # 2. Ödeme kaydı eklenmiş olmalı
        self.mock_satis_repository.satis_odeme_ekle.assert_called_once()
        odeme_args = self.mock_satis_repository.satis_odeme_ekle.call_args[1]
        assert odeme_args["satis_id"] == 123
        assert odeme_args["odeme_turu"] == OdemeTuru.NAKIT
        assert odeme_args["tutar"] == toplam_tutar

        # 3. Stok düşümü yapılmış olmalı (her ürün için)
        assert self.mock_stok_service.stok_dusur.call_count == urun_sayisi

        # 4. Satış tamamlanmış olmalı
        self.mock_satis_repository.satis_tamamla.assert_called_once()
        tamamla_args = self.mock_satis_repository.satis_tamamla.call_args[0]
        assert tamamla_args[0] == 123  # satis_id
        assert tamamla_args[1] is not None  # fis_no

        # 5. Sepet durumu güncellenmiş olmalı
        self.mock_sepet_repository.sepet_durum_guncelle.assert_called_once_with(sepet_id, SepetDurum.TAMAMLANDI)

    @given(
        sepet_id=st.integers(min_value=1, max_value=1000),
        toplam_tutar=st.decimals(min_value=Decimal("1.00"), max_value=Decimal("1000.00"), places=2),
        hata_noktasi=st.sampled_from(["satis_olustur", "odeme_ekle", "stok_dusur", "satis_tamamla"]),
    )
    @settings(max_examples=50, deadline=10000)
    def test_property_pos_transaction_atomikligi_hata_durumu(self, sepet_id, toplam_tutar, hata_noktasi):
        """
        **Feature: test-stabilizasyon-paketi, Property 9: POS transaction atomikliği**

        For any POS ödeme işlemi, herhangi bir adımda hata oluştuğunda tüm işlem başarısız olmalı.
        Kısmi başarı durumu olmamalı (atomiklik).
        **Validates: Requirements 4.1**
        """
        # Mock'ları sıfırla
        self._reset_mocks()

        # Arrange - Hata senaryosu için mock'ları ayarla
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

        # Transaction atomikliği kontrolleri
        if hata_noktasi == "satis_olustur":
            # Satış oluşturulamadıysa hiçbir işlem yapılmamalı
            self.mock_satis_repository.satis_odeme_ekle.assert_not_called()
            self.mock_stok_service.stok_dusur.assert_not_called()
            self.mock_satis_repository.satis_tamamla.assert_not_called()
            self.mock_sepet_repository.sepet_durum_guncelle.assert_not_called()

        elif hata_noktasi == "odeme_ekle":
            # Satış oluştu ama ödeme eklenemedi
            self.mock_satis_repository.satis_olustur.assert_called_once()
            # Sonraki işlemler yapılmamalı
            self.mock_stok_service.stok_dusur.assert_not_called()
            self.mock_satis_repository.satis_tamamla.assert_not_called()
            self.mock_sepet_repository.sepet_durum_guncelle.assert_not_called()

        elif hata_noktasi == "stok_dusur":
            # Satış ve ödeme oluştu ama stok düşürülemedi
            self.mock_satis_repository.satis_olustur.assert_called_once()
            self.mock_satis_repository.satis_odeme_ekle.assert_called_once()
            # Sonraki işlemler yapılmamalı
            self.mock_satis_repository.satis_tamamla.assert_not_called()
            self.mock_sepet_repository.sepet_durum_guncelle.assert_not_called()

        elif hata_noktasi == "satis_tamamla":
            # Tüm işlemler yapıldı ama tamamlanamadı
            self.mock_satis_repository.satis_olustur.assert_called_once()
            self.mock_satis_repository.satis_odeme_ekle.assert_called_once()
            self.mock_stok_service.stok_dusur.assert_called()
            # Sepet durumu güncellenmemeli
            self.mock_sepet_repository.sepet_durum_guncelle.assert_not_called()

    @given(
        sepet_id=st.integers(min_value=1, max_value=1000),
        odemeler_sayisi=st.integers(min_value=2, max_value=4),
        toplam_tutar=st.decimals(min_value=Decimal("10.00"), max_value=Decimal("500.00"), places=2),
    )
    @settings(max_examples=30, deadline=10000)
    def test_property_pos_parcali_odeme_atomikligi(self, sepet_id, odemeler_sayisi, toplam_tutar):
        """
        **Feature: test-stabilizasyon-paketi, Property 9: POS transaction atomikliği**

        For any parçalı ödeme işlemi, tüm ödemeler ve stok düşümü birlikte başarılı/başarısız olmalı.
        **Validates: Requirements 4.1**
        """
        # Mock'ları sıfırla
        self._reset_mocks()

        # Arrange - Parçalı ödeme için mock'ları ayarla
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

        # Ödemeleri oluştur (toplam tutarı böl)
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

        # Mock repository yanıtları - başarılı durum
        self.mock_sepet_repository.sepet_getir.return_value = sepet_bilgisi
        self.mock_satis_repository.satis_olustur.return_value = 789  # satis_id
        self.mock_satis_repository.satis_odeme_ekle.return_value = 101  # odeme_id
        self.mock_satis_repository.satis_tamamla.return_value = True
        self.mock_sepet_repository.sepet_durum_guncelle.return_value = True
        self.mock_stok_service.stok_dusur.return_value = True

        # Act - Parçalı ödeme işlemi yap
        sonuc = self.odeme_service.parcali_odeme_yap(sepet_id=sepet_id, odemeler=odemeler)

        # Assert - Parçalı ödeme atomikliği kontrolleri
        assert sonuc is True, "Parçalı ödeme işlemi başarılı olmalı"

        # 1. Satış kaydı oluşturulmuş olmalı
        self.mock_satis_repository.satis_olustur.assert_called_once()

        # 2. Tüm ödemeler eklenmiş olmalı
        assert self.mock_satis_repository.satis_odeme_ekle.call_count == odemeler_sayisi

        # 3. Stok düşümü yapılmış olmalı
        self.mock_stok_service.stok_dusur.assert_called()

        # 4. Satış tamamlanmış olmalı
        self.mock_satis_repository.satis_tamamla.assert_called_once()

        # 5. Sepet durumu güncellenmiş olmalı
        self.mock_sepet_repository.sepet_durum_guncelle.assert_called_once_with(sepet_id, SepetDurum.TAMAMLANDI)

        # 6. Ödeme tutarları toplamı sepet toplamına eşit olmalı
        toplam_odeme = sum(Decimal(str(odeme["tutar"])) for odeme in odemeler)
        assert abs(toplam_odeme - toplam_tutar) < Decimal(
            "0.01"
        ), f"Toplam ödeme tutarı uyumsuz: {toplam_odeme} != {toplam_tutar}"
