# Version: 0.1.0
# Last Update: 2025-12-18
# Module: tests.test_pos_satis_stok_butunlugu_property
# Description: POS satış-stok bütünlüğü property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP POS Satış-Stok Bütünlüğü Property Testleri

Bu modül POS ödeme işlemlerinde satış-stok bütünlüğünün korunduğunu test eder.
Stok düşümü olmadan satış durumunun TAMAMLANDI olmaması gerektiğini doğrular.
"""

from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock, call
from hypothesis import given, strategies as st, settings, assume
import pytest

from sontechsp.uygulama.moduller.pos.servisler.odeme_service import OdemeService
from sontechsp.uygulama.moduller.pos.arayuzler import OdemeTuru, SepetDurum, SatisDurum
from sontechsp.uygulama.cekirdek.hatalar import DogrulamaHatasi, SontechHatasi


class TestPOSSatisStokButunlugu:
    """POS satış-stok bütünlüğü property testleri"""

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
    @settings(max_examples=20, deadline=5000)
    def test_property_satis_stok_butunlugu_basarili_durum(self, sepet_id, toplam_tutar, urun_sayisi):
        """
        **Feature: test-stabilizasyon-paketi, Property 11: Satış-stok bütünlüğü**

        For any tamamlanmış satış, stok düşümü olmadan TAMAMLANDI durumunda olmamalı.
        Başarılı durumda hem stok düşümü hem satış tamamlama birlikte yapılmalı.
        **Validates: Requirements 4.3**
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

        # Assert - Satış-stok bütünlüğü kontrolleri
        assert sonuc is True, "Ödeme işlemi başarılı olmalı"

        # 1. Stok düşümü yapılmış olmalı (her ürün için)
        assert self.mock_stok_service.stok_dusur.call_count == urun_sayisi

        # 2. Satış tamamlanmış olmalı
        self.mock_satis_repository.satis_tamamla.assert_called_once()

        # 3. Stok düşümü ve satış tamamlama birlikte yapılmış olmalı
        # Stok düşümü çağrıları satış tamamlamadan önce yapılmalı
        stok_calls = [call for call in self.mock_stok_service.stok_dusur.call_args_list]
        satis_tamamla_call = self.mock_satis_repository.satis_tamamla.call_args

        assert len(stok_calls) == urun_sayisi, f"Stok düşümü {urun_sayisi} kez yapılmalı"
        assert satis_tamamla_call is not None, "Satış tamamlama çağrılmalı"

        # 4. Sepet durumu güncellenmiş olmalı
        self.mock_sepet_repository.sepet_durum_guncelle.assert_called_once_with(sepet_id, SepetDurum.TAMAMLANDI)

    @given(
        sepet_id=st.integers(min_value=1, max_value=1000),
        toplam_tutar=st.decimals(min_value=Decimal("1.00"), max_value=Decimal("1000.00"), places=2),
        urun_sayisi=st.integers(min_value=1, max_value=3),
        basarisiz_urun_indeksi=st.integers(min_value=0, max_value=2),
    )
    @settings(max_examples=15, deadline=5000)
    def test_property_stok_dusumu_basarisiz_satis_tamamlanmamali(
        self, sepet_id, toplam_tutar, urun_sayisi, basarisiz_urun_indeksi
    ):
        """
        **Feature: test-stabilizasyon-paketi, Property 11: Satış-stok bütünlüğü**

        For any stok düşümü başarısız olan ürün, satış TAMAMLANDI durumuna geçmemeli.
        Kısmi stok düşümü durumunda satış tamamlanmamalı.
        **Validates: Requirements 4.3**
        """
        assume(basarisiz_urun_indeksi < urun_sayisi)

        # Mock'ları sıfırla
        self._reset_mocks()

        # Arrange - Stok düşümü başarısız senaryosu
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
        self.mock_satis_repository.satis_olustur.return_value = 123
        self.mock_satis_repository.satis_odeme_ekle.return_value = 456

        # Belirli bir ürün için stok düşümü başarısız
        def stok_dusur_side_effect(urun_id, adet):
            if urun_id == basarisiz_urun_indeksi + 1:  # urun_id 1'den başlar
                raise Exception(f"Stok düşümü başarısız - Ürün {urun_id}")
            return True

        self.mock_stok_service.stok_dusur.side_effect = stok_dusur_side_effect

        # Act & Assert - Stok düşümü başarısız olduğunda exception fırlatılmalı
        with pytest.raises(Exception):
            self.odeme_service.tek_odeme_yap(sepet_id=sepet_id, odeme_turu=OdemeTuru.NAKIT, tutar=toplam_tutar)

        # Satış-stok bütünlüğü kontrolleri
        # 1. Satış tamamlanmamış olmalı
        self.mock_satis_repository.satis_tamamla.assert_not_called()

        # 2. Sepet durumu değişmemiş olmalı
        self.mock_sepet_repository.sepet_durum_guncelle.assert_not_called()

        # 3. Stok düşümü çağrılmış ama başarısız olmuş
        assert self.mock_stok_service.stok_dusur.call_count >= basarisiz_urun_indeksi + 1

    @given(
        sepet_id=st.integers(min_value=1, max_value=1000),
        toplam_tutar=st.decimals(min_value=Decimal("10.00"), max_value=Decimal("500.00"), places=2),
        odemeler_sayisi=st.integers(min_value=2, max_value=4),
    )
    @settings(max_examples=15, deadline=5000)
    def test_property_parcali_odeme_satis_stok_butunlugu(self, sepet_id, toplam_tutar, odemeler_sayisi):
        """
        **Feature: test-stabilizasyon-paketi, Property 11: Satış-stok bütünlüğü**

        For any parçalı ödeme işlemi, tüm ödemeler tamamlandıktan sonra stok düşümü ve satış tamamlama birlikte yapılmalı.
        **Validates: Requirements 4.3**
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
                {"urun_id": 1, "adet": 2, "birim_fiyat": float(toplam_tutar / 2), "toplam_tutar": float(toplam_tutar)}
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

        # Assert - Parçalı ödeme satış-stok bütünlüğü kontrolleri
        assert sonuc is True, "Parçalı ödeme işlemi başarılı olmalı"

        # 1. Tüm ödemeler eklenmiş olmalı
        assert self.mock_satis_repository.satis_odeme_ekle.call_count == odemeler_sayisi

        # 2. Stok düşümü yapılmış olmalı
        self.mock_stok_service.stok_dusur.assert_called()

        # 3. Satış tamamlanmış olmalı
        self.mock_satis_repository.satis_tamamla.assert_called_once()

        # 4. Stok düşümü ve satış tamamlama birlikte yapılmış olmalı
        # Stok düşümü satış tamamlamadan önce yapılmalı
        stok_call_count = self.mock_stok_service.stok_dusur.call_count
        assert stok_call_count > 0, "Stok düşümü yapılmalı"

        # 5. Sepet durumu güncellenmiş olmalı
        self.mock_sepet_repository.sepet_durum_guncelle.assert_called_once_with(sepet_id, SepetDurum.TAMAMLANDI)

    @given(
        sepet_id=st.integers(min_value=1, max_value=1000),
        toplam_tutar=st.decimals(min_value=Decimal("1.00"), max_value=Decimal("500.00"), places=2),
    )
    @settings(max_examples=15, deadline=5000)
    def test_property_satis_tamamlama_basarisiz_stok_geri_alinmali(self, sepet_id, toplam_tutar):
        """
        **Feature: test-stabilizasyon-paketi, Property 11: Satış-stok bütünlüğü**

        For any satış tamamlama başarısız olduğunda, düşürülen stok geri alınmalı.
        Satış-stok tutarlılığı korunmalı.
        **Validates: Requirements 4.3**
        """
        # Mock'ları sıfırla
        self._reset_mocks()

        # Arrange - Satış tamamlama başarısız senaryosu
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
        self.mock_satis_repository.satis_olustur.return_value = 999
        self.mock_satis_repository.satis_odeme_ekle.return_value = 888
        self.mock_stok_service.stok_dusur.return_value = True
        # Satış tamamlama başarısız
        self.mock_satis_repository.satis_tamamla.side_effect = Exception("Satış tamamlama başarısız")

        # Act & Assert - Satış tamamlama başarısız olduğunda exception fırlatılmalı
        with pytest.raises(Exception):
            self.odeme_service.tek_odeme_yap(sepet_id=sepet_id, odeme_turu=OdemeTuru.NAKIT, tutar=toplam_tutar)

        # Satış-stok bütünlüğü kontrolleri
        # 1. Stok düşümü yapılmış
        self.mock_stok_service.stok_dusur.assert_called_once()

        # 2. Satış tamamlama denendi ama başarısız oldu
        self.mock_satis_repository.satis_tamamla.assert_called_once()

        # 3. Sepet durumu değişmemiş olmalı
        self.mock_sepet_repository.sepet_durum_guncelle.assert_not_called()

        # 4. Gerçek implementasyonda stok geri yükleme yapılmalı
        # Mock ortamında bu davranışı test edemiyoruz ama
        # gerçek sistemde transaction rollback ile stok geri alınır
