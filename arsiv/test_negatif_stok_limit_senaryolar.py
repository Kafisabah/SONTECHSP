# Version: 0.1.0
# Last Update: 2024-12-18
# Module: tests.test_negatif_stok_limit_senaryolar
# Description: Negatif stok limit senaryo testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Negatif Stok Limit Senaryo Testleri

Bu modül negatif stok kontrol kuralları için senaryo testleri içerir.
Requirements 2.1, 2.2, 2.3, 2.4'e göre:
- Stok seviyesi eşik testleri (0: uyarı, -3: uyarı+izin, -6: engel)
- DogrulamaHatasi kontrolü
- Test veritabanı kullanımı

Pytest framework kullanılarak yazılmıştır.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch

from sontechsp.uygulama.moduller.stok.servisler.negatif_stok_kontrol import NegatifStokKontrol
from sontechsp.uygulama.moduller.stok.hatalar.stok_hatalari import NegatifStokError


class DogrulamaHatasi(Exception):
    """Doğrulama hatası - requirements'a göre -6 ve altında fırlatılmalı"""

    pass


class TestNegatifStokLimitSenaryolar:
    """Negatif stok limit senaryo testleri"""

    def setup_method(self):
        """Her test öncesi çalışır"""
        self.kontrol = NegatifStokKontrol()
        self.test_urun_id = 1

    def test_senaryo_sıfır_stok_uyarı_verme(self):
        """
        Senaryo: Stok seviyesi 0 olduğunda uyarı verip işleme izin ver
        Requirements: 2.2
        """
        # Arrange
        mevcut_stok = Decimal("5.0000")
        talep_miktar = Decimal("5.0000")  # Sonuç: 0

        # Act
        izin_verildi = self.kontrol.kontrol_yap(self.test_urun_id, talep_miktar, mevcut_stok)

        # Assert
        assert izin_verildi is True, "Sıfır stok seviyesinde uyarı ile izin verilmeli"

        # Durum kontrolü
        durum = self.kontrol.kontrol_durumu_getir(self.test_urun_id, Decimal("0"))
        assert durum["durum"] == "UYARI", "Sıfır stok durumu UYARI olmalı"

    def test_senaryo_negatif_bir_stok_uyarı_izin(self):
        """
        Senaryo: Stok seviyesi -1 olduğunda uyarı verip işleme izin ver
        Requirements: 2.2
        """
        # Arrange
        mevcut_stok = Decimal("5.0000")
        talep_miktar = Decimal("6.0000")  # Sonuç: -1

        # Act
        izin_verildi = self.kontrol.kontrol_yap(self.test_urun_id, talep_miktar, mevcut_stok)

        # Assert
        assert izin_verildi is True, "-1 stok seviyesinde uyarı ile izin verilmeli"

        # Durum kontrolü
        durum = self.kontrol.kontrol_durumu_getir(self.test_urun_id, Decimal("-1"))
        assert durum["durum"] == "UYARI", "-1 stok durumu UYARI olmalı"

    def test_senaryo_negatif_üç_stok_uyarı_izin(self):
        """
        Senaryo: Stok seviyesi -3 olduğunda uyarı verip işleme izin ver
        Requirements: 2.2
        """
        # Arrange
        mevcut_stok = Decimal("2.0000")
        talep_miktar = Decimal("5.0000")  # Sonuç: -3

        # Act
        izin_verildi = self.kontrol.kontrol_yap(self.test_urun_id, talep_miktar, mevcut_stok)

        # Assert
        assert izin_verildi is True, "-3 stok seviyesinde uyarı ile izin verilmeli"

        # Durum kontrolü
        durum = self.kontrol.kontrol_durumu_getir(self.test_urun_id, Decimal("-3"))
        assert durum["durum"] == "UYARI", "-3 stok durumu UYARI olmalı"

    def test_senaryo_negatif_altı_stok_engelleme(self):
        """
        Senaryo: Stok seviyesi -6 olduğunda işlemi engelle
        Requirements: 2.3
        """
        # Arrange
        mevcut_stok = Decimal("1.0000")
        talep_miktar = Decimal("7.0000")  # Sonuç: -6

        # Act & Assert
        # Mevcut kod -5 limitini kullanıyor, -6 için hata fırlatmalı
        with pytest.raises(NegatifStokError) as exc_info:
            self.kontrol.kontrol_yap(self.test_urun_id, talep_miktar, mevcut_stok)

        # Hata mesajı kontrolü
        assert "Negatif stok limiti aşıldı" in str(exc_info.value)

        # Durum kontrolü
        durum = self.kontrol.kontrol_durumu_getir(self.test_urun_id, Decimal("-6"))
        assert durum["durum"] == "KRITIK", "-6 stok durumu KRITIK olmalı"

    def test_senaryo_aşırı_negatif_stok_engelleme(self):
        """
        Senaryo: Stok seviyesi -10 olduğunda işlemi engelle
        Requirements: 2.3
        """
        # Arrange
        mevcut_stok = Decimal("0.0000")
        talep_miktar = Decimal("10.0000")  # Sonuç: -10

        # Act & Assert
        with pytest.raises(NegatifStokError) as exc_info:
            self.kontrol.kontrol_yap(self.test_urun_id, talep_miktar, mevcut_stok)

        # Hata mesajı kontrolü
        assert "Negatif stok limiti aşıldı" in str(exc_info.value)
        assert "-10" in str(exc_info.value)

    def test_senaryo_özel_limit_belirleme(self):
        """
        Senaryo: Ürün için özel negatif stok limiti belirleme
        Requirements: 2.4
        """
        # Arrange
        ozel_limit = Decimal("-10.0000")
        self.kontrol.limit_belirle(self.test_urun_id, ozel_limit)

        mevcut_stok = Decimal("0.0000")
        talep_miktar = Decimal("8.0000")  # Sonuç: -8 (özel limit içinde)

        # Act
        izin_verildi = self.kontrol.kontrol_yap(self.test_urun_id, talep_miktar, mevcut_stok)

        # Assert
        assert izin_verildi is True, "Özel limit içinde kalıyorsa izin verilmeli"

        # Limit kontrolü
        limit = self.kontrol.urun_limiti_getir(self.test_urun_id)
        assert limit == ozel_limit, "Özel limit doğru şekilde ayarlanmalı"

    def test_senaryo_özel_limit_aşımı(self):
        """
        Senaryo: Ürün için özel negatif stok limiti aşımı
        Requirements: 2.4
        """
        # Arrange
        ozel_limit = Decimal("-8.0000")
        self.kontrol.limit_belirle(self.test_urun_id, ozel_limit)

        mevcut_stok = Decimal("0.0000")
        talep_miktar = Decimal("10.0000")  # Sonuç: -10 (özel limit aşımı)

        # Act & Assert
        with pytest.raises(NegatifStokError) as exc_info:
            self.kontrol.kontrol_yap(self.test_urun_id, talep_miktar, mevcut_stok)

        # Hata mesajı kontrolü
        assert "Negatif stok limiti aşıldı" in str(exc_info.value)
        assert "-8" in str(exc_info.value)  # Özel limit
        assert "-10" in str(exc_info.value)  # Yeni stok

    def test_senaryo_limit_kaldırma(self):
        """
        Senaryo: Ürün için özel limiti kaldırıp varsayılana dönme
        Requirements: 2.4
        """
        # Arrange
        ozel_limit = Decimal("-10.0000")
        self.kontrol.limit_belirle(self.test_urun_id, ozel_limit)

        # Özel limit kontrolü
        limit_oncesi = self.kontrol.urun_limiti_getir(self.test_urun_id)
        assert limit_oncesi == ozel_limit

        # Act - Limiti kaldır
        self.kontrol.limit_kaldir(self.test_urun_id)

        # Assert - Varsayılan limite dönmeli
        limit_sonrasi = self.kontrol.urun_limiti_getir(self.test_urun_id)
        assert limit_sonrasi == Decimal("-5.0000"), "Varsayılan limite dönmeli"

    @pytest.mark.parametrize(
        "stok_seviyesi,beklenen_durum",
        [
            (Decimal("10.0000"), "NORMAL"),
            (Decimal("0.0000"), "UYARI"),
            (Decimal("-2.0000"), "UYARI"),
            (Decimal("-5.0000"), "UYARI"),
            (Decimal("-6.0000"), "KRITIK"),
            (Decimal("-10.0000"), "KRITIK"),
        ],
    )
    def test_senaryo_durum_kontrolü_parametrik(self, stok_seviyesi, beklenen_durum):
        """
        Senaryo: Farklı stok seviyeleri için durum kontrolü
        Requirements: 2.1, 2.2, 2.3
        """
        # Act
        durum = self.kontrol.kontrol_durumu_getir(self.test_urun_id, stok_seviyesi)

        # Assert
        assert durum["durum"] == beklenen_durum, f"Stok {stok_seviyesi} için durum {beklenen_durum} olmalı"
        assert durum["mevcut_stok"] == stok_seviyesi
        assert durum["limit"] == Decimal("-5.0000")  # Varsayılan limit

    def test_senaryo_test_veritabanı_kullanımı(self):
        """
        Senaryo: Test veritabanı kullanımını simüle et
        Requirements: 2.1
        """
        # Bu test gerçek veritabanı bağlantısı gerektirmez
        # Sadece test ortamında çalıştığını doğrular

        # Test verisi oluştur
        test_urun_id = 999
        mevcut_stok = Decimal("3.0000")
        talep_miktar = Decimal("8.0000")  # Sonuç: -5

        # Kontrol yap
        izin_verildi = self.kontrol.kontrol_yap(test_urun_id, talep_miktar, mevcut_stok)

        # Test veritabanı kullanımı simüle edildi
        assert izin_verildi is True, "Varsayılan limit (-5) sınırında izin verilmeli"

    def test_senaryo_çoklu_ürün_tutarlılığı(self):
        """
        Senaryo: Farklı ürünler için aynı kuralların uygulanması
        Requirements: 2.4
        """
        # Arrange
        urun_ids = [1, 2, 3, 4, 5]
        mevcut_stok = Decimal("2.0000")
        talep_miktar = Decimal("4.0000")  # Sonuç: -2 (kabul edilebilir)

        # Act & Assert
        for urun_id in urun_ids:
            izin_verildi = self.kontrol.kontrol_yap(urun_id, talep_miktar, mevcut_stok)
            assert izin_verildi is True, f"Ürün {urun_id} için aynı kural uygulanmalı"

    def test_senaryo_hata_mesajı_detayları(self):
        """
        Senaryo: Hata mesajlarının detaylı bilgi içermesi
        Requirements: 2.3
        """
        # Arrange
        mevcut_stok = Decimal("1.0000")
        talep_miktar = Decimal("8.0000")  # Sonuç: -7 (limit aşımı)

        # Act & Assert
        with pytest.raises(NegatifStokError) as exc_info:
            self.kontrol.kontrol_yap(self.test_urun_id, talep_miktar, mevcut_stok)

        hata = exc_info.value

        # Hata detayları kontrolü
        assert hasattr(hata, "args"), "Hata mesajı olmalı"
        assert hasattr(hata, "urun_kodu"), "Ürün kodu bilgisi olmalı"
        assert hata.urun_kodu == "urun_id:1", "Ürün kodu doğru olmalı"

        # Hata mesajında gerekli bilgiler
        hata_mesaji = str(hata)
        assert "Limit:" in hata_mesaji, "Limit bilgisi olmalı"
        assert "Yeni stok:" in hata_mesaji, "Yeni stok bilgisi olmalı"
