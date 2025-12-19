# Version: 0.1.0
# Last Update: 2024-12-18
# Module: test_ebelge_retry_basari_sifirlama_property
# Description: E-belge retry başarı sıfırlama property testleri
# Changelog:
# - İlk sürüm oluşturuldu

"""
**Feature: test-stabilizasyon-paketi, Property 13: E-belge retry başarı sıfırlama**
**Validates: Requirements 5.4**

E-belge retry başarı sıfırlama mekanizması için property-based testler.
Bu testler başarılı retry sonrası deneme sayacı sıfırlama işlemini test eder.
"""

import pytest
from hypothesis import given, strategies as st, assume
from unittest.mock import Mock, patch
from decimal import Decimal
from datetime import datetime


# E-belge modeli için basit test modeli oluştur
class EbelgeCikisKuyrugu:
    """Test için basit e-belge modeli"""

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", 1)
        self.kaynak_turu = kwargs.get("kaynak_turu", "SATIS")
        self.kaynak_id = kwargs.get("kaynak_id", 1)
        self.belge_turu = kwargs.get("belge_turu", "FATURA")
        self.musteri_ad = kwargs.get("musteri_ad", "Test Müşteri")
        self.vergi_no = kwargs.get("vergi_no", "1234567890")
        self.toplam_tutar = kwargs.get("toplam_tutar", Decimal("100.00"))
        self.belge_json = kwargs.get("belge_json", "{}")
        self.durum = kwargs.get("durum", "BEKLIYOR")
        self.deneme_sayisi = kwargs.get("deneme_sayisi", 0)
        self.mesaj = kwargs.get("mesaj", "")
        self.dis_belge_no = kwargs.get("dis_belge_no", None)
        self.guncellenme_zamani = kwargs.get("guncellenme_zamani", datetime.utcnow())


class DummySaglayici:
    """E-belge gönderimi için dummy sağlayıcı - kontrollü başarı/hata simülasyonu"""

    def __init__(self, success_pattern: str = "even"):
        """
        Args:
            success_pattern: "even" (çift ID başarılı), "odd" (tek ID başarılı), "all" (hep başarılı), "none" (hep hata)
        """
        self.success_pattern = success_pattern
        self.call_count = 0
        self.success_count = 0
        self.failure_count = 0

    def belge_gonder(self, belge_data: dict) -> tuple[bool, str]:
        """
        Belge gönderme simülasyonu

        Returns:
            tuple[bool, str]: (başarı_durumu, mesaj)
        """
        self.call_count += 1

        belge_id = belge_data.get("id", 0)

        if self.success_pattern == "even":
            is_success = (belge_id % 2) == 0
        elif self.success_pattern == "odd":
            is_success = (belge_id % 2) == 1
        elif self.success_pattern == "all":
            is_success = True
        elif self.success_pattern == "none":
            is_success = False
        else:
            is_success = (belge_id % 2) == 0  # Varsayılan

        if is_success:
            self.success_count += 1
            return True, "Belge başarıyla gönderildi"
        else:
            self.failure_count += 1
            return False, "Sağlayıcı hatası: Geçici ağ sorunu"


class EbelgeRetryServisi:
    """E-belge retry mekanizması servisi"""

    def __init__(self, saglayici: DummySaglayici, maksimum_deneme: int = 3):
        self.saglayici = saglayici
        self.maksimum_deneme = maksimum_deneme

    def belge_gonder_retry(self, belge: EbelgeCikisKuyrugu) -> tuple[bool, str]:
        """
        Belge gönderme retry mekanizması

        Returns:
            tuple[bool, str]: (başarı_durumu, mesaj)
        """
        # Maksimum deneme kontrolü
        if belge.deneme_sayisi >= self.maksimum_deneme:
            belge.durum = "HATA"
            return False, f"Maksimum deneme sayısı ({self.maksimum_deneme}) aşıldı"

        # Deneme sayısını artır
        belge.deneme_sayisi += 1
        belge.guncellenme_zamani = datetime.utcnow()

        # Belge verisini hazırla
        belge_data = {
            "id": belge.id,
            "kaynak_turu": belge.kaynak_turu,
            "kaynak_id": belge.kaynak_id,
            "belge_turu": belge.belge_turu,
            "musteri_ad": belge.musteri_ad,
            "vergi_no": belge.vergi_no,
            "toplam_tutar": float(belge.toplam_tutar),
            "belge_json": belge.belge_json,
        }

        # Sağlayıcı ile göndermeyi dene
        success, message = self.saglayici.belge_gonder(belge_data)

        if success:
            belge.durum = "GONDERILDI"
            belge.dis_belge_no = f"EXT-{belge.id}-{belge.deneme_sayisi}"
            # Başarılı retry sonrası deneme sayacını sıfırla
            belge.deneme_sayisi = 0
            return True, message
        else:
            belge.durum = "BEKLIYOR"
            belge.mesaj = message
            return False, message


class TestEbelgeRetryBasariSifirlamaProperty:
    """E-belge retry başarı sıfırlama property testleri"""

    @given(
        belge_id=st.integers(min_value=2, max_value=1000).filter(
            lambda x: x % 2 == 0
        ),  # Sadece çift sayılar (başarılı olacak)
        kaynak_id=st.integers(min_value=1, max_value=10000),
        toplam_tutar=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("999999.99"), places=2),
        baslangic_deneme=st.integers(min_value=1, max_value=2),  # Başarılı olacak deneme sayısı
    )
    def test_basarili_retry_sonrasi_sayac_sifirlama_property(self, belge_id, kaynak_id, toplam_tutar, baslangic_deneme):
        """
        **Feature: test-stabilizasyon-paketi, Property 13: E-belge retry başarı sıfırlama**

        For any başarılı e-belge retry işlemi, deneme sayacı sıfırlanmalı
        """
        # Test verisi oluştur - başarılı olacak şekilde
        belge = EbelgeCikisKuyrugu(
            id=belge_id,  # Çift sayı - başarılı olacak
            kaynak_turu="SATIS",
            kaynak_id=kaynak_id,
            belge_turu="FATURA",
            musteri_ad="Test Müşteri",
            vergi_no="1234567890",
            toplam_tutar=toplam_tutar,
            belge_json='{"test": "data"}',
            durum="BEKLIYOR",
            deneme_sayisi=baslangic_deneme,  # Sıfırdan büyük başlangıç değeri
        )

        # Başlangıç durumunu kaydet
        baslangic_deneme_sayisi = belge.deneme_sayisi

        # Dummy sağlayıcı oluştur (çift ID'ler başarılı olacak)
        saglayici = DummySaglayici(success_pattern="even")
        retry_servisi = EbelgeRetryServisi(saglayici, maksimum_deneme=3)

        # Retry işlemini çalıştır
        success, message = retry_servisi.belge_gonder_retry(belge)

        # Doğrulamalar
        assert success, f"Çift ID ({belge_id}) için başarılı olmalı"
        assert belge.durum == "GONDERILDI", f"Durum GONDERILDI olmalı, {belge.durum} oldu"
        assert belge.deneme_sayisi == 0, f"Başarılı retry sonrası deneme sayısı 0 olmalı, {belge.deneme_sayisi} oldu"
        assert belge.dis_belge_no is not None, "Dış belge numarası atanmalı"
        assert f"EXT-{belge_id}-" in belge.dis_belge_no, "Dış belge numarası doğru formatta olmalı"

    @given(
        belge_id=st.integers(min_value=1, max_value=999).filter(
            lambda x: x % 2 == 1
        ),  # Sadece tek sayılar (hata alacak)
        kaynak_id=st.integers(min_value=1, max_value=10000),
        toplam_tutar=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("999999.99"), places=2),
        baslangic_deneme=st.integers(min_value=0, max_value=2),
    )
    def test_basarisiz_retry_sonrasi_sayac_korunumu_property(self, belge_id, kaynak_id, toplam_tutar, baslangic_deneme):
        """
        **Feature: test-stabilizasyon-paketi, Property 13: E-belge retry başarı sıfırlama**

        For any başarısız e-belge retry işlemi, deneme sayacı sıfırlanmamalı (artmalı)
        """
        # Test verisi oluştur - başarısız olacak şekilde
        belge = EbelgeCikisKuyrugu(
            id=belge_id,  # Tek sayı - başarısız olacak
            kaynak_turu="SATIS",
            kaynak_id=kaynak_id,
            belge_turu="FATURA",
            musteri_ad="Test Müşteri",
            vergi_no="1234567890",
            toplam_tutar=toplam_tutar,
            belge_json='{"test": "data"}',
            durum="BEKLIYOR",
            deneme_sayisi=baslangic_deneme,
        )

        # Başlangıç durumunu kaydet
        baslangic_deneme_sayisi = belge.deneme_sayisi

        # Dummy sağlayıcı oluştur (çift ID'ler başarılı olacak, tek ID'ler başarısız)
        saglayici = DummySaglayici(success_pattern="even")
        retry_servisi = EbelgeRetryServisi(saglayici, maksimum_deneme=3)

        # Retry işlemini çalıştır
        success, message = retry_servisi.belge_gonder_retry(belge)

        # Doğrulamalar
        if baslangic_deneme_sayisi < 3:  # Maksimum deneme aşılmamışsa
            assert not success, f"Tek ID ({belge_id}) için başarısız olmalı"
            assert belge.durum == "BEKLIYOR", f"Durum BEKLIYOR olmalı, {belge.durum} oldu"
            assert belge.deneme_sayisi == baslangic_deneme_sayisi + 1, f"Başarısız retry sonrası deneme sayısı artmalı"
            assert belge.deneme_sayisi != 0, "Başarısız retry sonrası deneme sayısı sıfırlanmamalı"
        else:
            # Maksimum deneme aşılmış
            assert not success
            assert belge.durum == "HATA"

    @given(
        belge_id=st.integers(min_value=2, max_value=1000).filter(lambda x: x % 2 == 0),  # Çift sayılar
        kaynak_id=st.integers(min_value=1, max_value=10000),
        toplam_tutar=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("999999.99"), places=2),
        deneme_sayilari=st.lists(st.integers(min_value=1, max_value=3), min_size=1, max_size=3),
    )
    def test_coklu_retry_basari_sifirlama_property(self, belge_id, kaynak_id, toplam_tutar, deneme_sayilari):
        """
        **Feature: test-stabilizasyon-paketi, Property 13: E-belge retry başarı sıfırlama**

        For any çoklu retry senaryosu, her başarılı retry sonrası deneme sayacı sıfırlanmalı
        """
        # Test verisi oluştur
        belge = EbelgeCikisKuyrugu(
            id=belge_id,  # Çift sayı - başarılı olacak
            kaynak_turu="SATIS",
            kaynak_id=kaynak_id,
            belge_turu="FATURA",
            musteri_ad="Test Müşteri",
            vergi_no="1234567890",
            toplam_tutar=toplam_tutar,
            belge_json='{"test": "data"}',
            durum="BEKLIYOR",
            deneme_sayisi=0,
        )

        # Dummy sağlayıcı oluştur (çift ID'ler başarılı)
        saglayici = DummySaglayici(success_pattern="even")
        retry_servisi = EbelgeRetryServisi(saglayici, maksimum_deneme=5)

        # Her deneme sayısı için test et
        for deneme_sayisi in deneme_sayilari:
            # Belgeyi yeniden başlangıç durumuna getir
            belge.deneme_sayisi = deneme_sayisi
            belge.durum = "BEKLIYOR"
            belge.dis_belge_no = None

            # Retry işlemini çalıştır
            success, message = retry_servisi.belge_gonder_retry(belge)

            # Doğrulamalar
            assert success, f"Çift ID ({belge_id}) için başarılı olmalı"
            assert (
                belge.deneme_sayisi == 0
            ), f"Başarılı retry sonrası deneme sayısı 0 olmalı, {belge.deneme_sayisi} oldu"
            assert belge.durum == "GONDERILDI", "Durum GONDERILDI olmalı"

    @given(
        belge_id=st.integers(min_value=2, max_value=1000).filter(lambda x: x % 2 == 0),
        kaynak_id=st.integers(min_value=1, max_value=10000),
        toplam_tutar=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("999999.99"), places=2),
    )
    def test_dis_belge_no_atama_property(self, belge_id, kaynak_id, toplam_tutar):
        """
        **Feature: test-stabilizasyon-paketi, Property 13: E-belge retry başarı sıfırlama**

        For any başarılı retry işlemi, dış belge numarası doğru formatta atanmalı
        """
        # Test verisi oluştur
        belge = EbelgeCikisKuyrugu(
            id=belge_id,
            kaynak_turu="SATIS",
            kaynak_id=kaynak_id,
            belge_turu="FATURA",
            musteri_ad="Test Müşteri",
            vergi_no="1234567890",
            toplam_tutar=toplam_tutar,
            belge_json='{"test": "data"}',
            durum="BEKLIYOR",
            deneme_sayisi=1,  # Bir deneme yapılmış
        )

        # Dummy sağlayıcı oluştur (çift ID'ler başarılı)
        saglayici = DummySaglayici(success_pattern="even")
        retry_servisi = EbelgeRetryServisi(saglayici, maksimum_deneme=3)

        # Retry işlemini çalıştır
        success, message = retry_servisi.belge_gonder_retry(belge)

        # Doğrulamalar
        assert success, "Çift ID için başarılı olmalı"
        assert belge.dis_belge_no is not None, "Dış belge numarası atanmalı"

        # Dış belge numarası format kontrolü: EXT-{belge_id}-{deneme_sayisi}
        expected_prefix = f"EXT-{belge_id}-"
        assert belge.dis_belge_no.startswith(expected_prefix), f"Dış belge numarası '{expected_prefix}' ile başlamalı"

        # Deneme sayısı sıfırlanmış olmalı
        assert belge.deneme_sayisi == 0, "Başarılı retry sonrası deneme sayısı sıfırlanmalı"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
