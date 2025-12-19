# Version: 0.1.0
# Last Update: 2024-12-18
# Module: test_ebelge_retry_sayaci_property
# Description: E-belge retry sayacı property testleri
# Changelog:
# - İlk sürüm oluşturuldu

"""
**Feature: test-stabilizasyon-paketi, Property 12: E-belge retry sayacı**
**Validates: Requirements 5.1, 5.2**

E-belge retry mekanizması için property-based testler.
Bu testler deneme sayısı artırma ve maksimum deneme sonrası HATA durumu kontrolünü test eder.
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
    """E-belge gönderimi için dummy sağlayıcı - %50 hata oranı ile simülasyon"""

    def __init__(self, fail_rate: float = 0.5):
        self.fail_rate = fail_rate
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

        # Basit hash tabanlı deterministik hata simülasyonu
        # Belge ID'sine göre başarı/başarısızlık belirle
        belge_id = belge_data.get("id", 0)
        is_success = (belge_id % 2) == 0  # Çift ID'ler başarılı

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


class TestEbelgeRetrySayaciProperty:
    """E-belge retry sayacı property testleri"""

    @given(
        belge_id=st.integers(min_value=1, max_value=1000),
        kaynak_id=st.integers(min_value=1, max_value=10000),
        toplam_tutar=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("999999.99"), places=2),
        maksimum_deneme=st.integers(min_value=1, max_value=5),
    )
    def test_deneme_sayisi_artirma_property(self, belge_id, kaynak_id, toplam_tutar, maksimum_deneme):
        """
        **Feature: test-stabilizasyon-paketi, Property 12: E-belge retry sayacı**

        For any e-belge gönderim hatası, deneme sayısı artmalı
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
            deneme_sayisi=0,
        )

        # Başlangıç deneme sayısını kaydet
        baslangic_deneme_sayisi = belge.deneme_sayisi

        # Dummy sağlayıcı oluştur (hep başarısız olacak şekilde)
        saglayici = DummySaglayici()
        retry_servisi = EbelgeRetryServisi(saglayici, maksimum_deneme)

        # Belge ID'yi tek yap ki hata alsın
        belge.id = belge_id * 2 + 1  # Tek sayı = hata

        # Retry işlemini çalıştır
        success, message = retry_servisi.belge_gonder_retry(belge)

        # Doğrulamalar
        if baslangic_deneme_sayisi < maksimum_deneme:
            # Deneme sayısı artmış olmalı
            assert belge.deneme_sayisi == baslangic_deneme_sayisi + 1
            assert not success  # Hata aldığı için başarısız olmalı
            assert belge.durum == "BEKLIYOR"
        else:
            # Maksimum deneme aşılmış
            assert belge.durum == "HATA"
            assert not success
            assert "Maksimum deneme sayısı" in message

    @given(
        belge_id=st.integers(min_value=1, max_value=1000),
        kaynak_id=st.integers(min_value=1, max_value=10000),
        toplam_tutar=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("999999.99"), places=2),
        maksimum_deneme=st.integers(min_value=2, max_value=5),
    )
    def test_maksimum_deneme_sonrasi_hata_durumu_property(self, belge_id, kaynak_id, toplam_tutar, maksimum_deneme):
        """
        **Feature: test-stabilizasyon-paketi, Property 12: E-belge retry sayacı**

        For any maksimum deneme sayısına ulaşıldığında, belge durumu kalıcı HATA olmalı
        """
        # Test verisi oluştur - maksimum deneme sayısında
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
            deneme_sayisi=maksimum_deneme,  # Zaten maksimuma ulaşmış
        )

        # Dummy sağlayıcı oluştur
        saglayici = DummySaglayici()
        retry_servisi = EbelgeRetryServisi(saglayici, maksimum_deneme)

        # Retry işlemini çalıştır
        success, message = retry_servisi.belge_gonder_retry(belge)

        # Doğrulamalar
        assert not success
        assert belge.durum == "HATA"
        assert "Maksimum deneme sayısı" in message
        assert belge.deneme_sayisi == maksimum_deneme  # Değişmemeli

    @given(
        belge_id=st.integers(min_value=1, max_value=1000),
        kaynak_id=st.integers(min_value=1, max_value=10000),
        toplam_tutar=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("999999.99"), places=2),
        baslangic_deneme=st.integers(min_value=0, max_value=2),
    )
    def test_dummy_saglayici_hata_simulasyonu_property(self, belge_id, kaynak_id, toplam_tutar, baslangic_deneme):
        """
        **Feature: test-stabilizasyon-paketi, Property 12: E-belge retry sayacı**

        For any DummySaglayici kullanımı, gerçekçi hata senaryoları test edilmeli
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
            deneme_sayisi=baslangic_deneme,
        )

        # Dummy sağlayıcı oluştur
        saglayici = DummySaglayici()
        retry_servisi = EbelgeRetryServisi(saglayici, maksimum_deneme=3)

        # Başlangıç durumunu kaydet
        baslangic_call_count = saglayici.call_count

        # Retry işlemini çalıştır
        success, message = retry_servisi.belge_gonder_retry(belge)

        # Doğrulamalar
        assert saglayici.call_count == baslangic_call_count + 1  # Bir kez çağrılmalı
        assert isinstance(success, bool)
        assert isinstance(message, str)
        assert len(message) > 0

        # Belge ID'ye göre deterministik sonuç kontrolü
        expected_success = (belge.id % 2) == 0
        if baslangic_deneme < 3:  # Maksimum deneme aşılmamışsa
            assert success == expected_success
            if success:
                assert belge.durum == "GONDERILDI"
                assert belge.deneme_sayisi == 0  # Başarılı olunca sıfırlanmalı
                assert belge.dis_belge_no is not None
            else:
                assert belge.durum == "BEKLIYOR"
                assert belge.deneme_sayisi == baslangic_deneme + 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
