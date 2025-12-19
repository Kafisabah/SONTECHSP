# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.kurulum.test_sabitler_property
# Description: Sabitler modülü property testleri
# Changelog:
# - Property testler oluşturuldu

"""
Sabitler modülü property testleri

**Özellik: kurulum-bootstrap-altyapisi, Özellik 2: Gerekli Klasörlerin Varlığı**
"""

import pytest
from hypothesis import given, strategies as st
from pathlib import Path

from sontechsp.uygulama.kurulum.sabitler import (
    VERI_KLASORU,
    LOG_KLASORU,
    YEDEK_KLASORU,
    RAPOR_KLASORU,
    GEREKLI_KLASORLER,
    CONFIG_DOSYA_ADI,
    VARSAYILAN_ORTAM,
    VARSAYILAN_LOG_SEVIYESI,
    VARSAYILAN_ADMIN_KULLANICI,
    VARSAYILAN_ADMIN_SIFRE,
)


class TestSabitlerProperty:
    """
    **Özellik: kurulum-bootstrap-altyapisi, Özellik 2: Gerekli Klasörlerin Varlığı**
    **Doğrular: Gereksinimler 1.1**
    """

    def test_gerekli_klasorler_listesi_tutarliligi(self):
        """Gerekli klasörler listesinin tüm klasör sabitlerini içerdiğini test et"""
        beklenen_klasorler = {VERI_KLASORU, LOG_KLASORU, YEDEK_KLASORU, RAPOR_KLASORU}
        gercek_klasorler = set(GEREKLI_KLASORLER)

        assert (
            beklenen_klasorler == gercek_klasorler
        ), f"Gerekli klasörler listesi eksik: {beklenen_klasorler - gercek_klasorler}"

    @given(st.text(min_size=1, max_size=50))
    def test_klasor_adlari_gecerli_string(self, test_string):
        """Tüm klasör adlarının geçerli string olduğunu test et"""
        for klasor in GEREKLI_KLASORLER:
            assert isinstance(klasor, str), f"Klasör adı string değil: {klasor}"
            assert len(klasor) > 0, f"Klasör adı boş: {klasor}"
            assert not klasor.isspace(), f"Klasör adı sadece boşluk: {klasor}"

    def test_config_dosya_adi_gecerliligi(self):
        """Config dosya adının geçerli olduğunu test et"""
        assert isinstance(CONFIG_DOSYA_ADI, str)
        assert len(CONFIG_DOSYA_ADI) > 0
        assert CONFIG_DOSYA_ADI.endswith(".json")

    @given(st.text(min_size=1, max_size=100))
    def test_varsayilan_degerler_gecerliligi(self, test_string):
        """Varsayılan değerlerin geçerli olduğunu test et"""
        # Ortam değeri
        assert isinstance(VARSAYILAN_ORTAM, str)
        assert len(VARSAYILAN_ORTAM) > 0
        assert VARSAYILAN_ORTAM in ["dev", "test", "prod"]

        # Log seviyesi
        assert isinstance(VARSAYILAN_LOG_SEVIYESI, str)
        assert len(VARSAYILAN_LOG_SEVIYESI) > 0
        assert VARSAYILAN_LOG_SEVIYESI in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        # Admin kullanıcı bilgileri
        assert isinstance(VARSAYILAN_ADMIN_KULLANICI, str)
        assert len(VARSAYILAN_ADMIN_KULLANICI) > 0
        assert isinstance(VARSAYILAN_ADMIN_SIFRE, str)
        assert len(VARSAYILAN_ADMIN_SIFRE) > 0

    def test_klasor_adlari_benzersizligi(self):
        """Klasör adlarının benzersiz olduğunu test et"""
        klasor_seti = set(GEREKLI_KLASORLER)
        assert len(klasor_seti) == len(GEREKLI_KLASORLER), "Klasör adlarında tekrar var"

    @given(st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=10))
    def test_klasor_listesi_immutable(self, test_list):
        """Gerekli klasörler listesinin değişmez olduğunu test et"""
        original_length = len(GEREKLI_KLASORLER)
        original_content = list(GEREKLI_KLASORLER)

        # Liste içeriğinin değişmediğini kontrol et
        assert len(GEREKLI_KLASORLER) == original_length
        assert list(GEREKLI_KLASORLER) == original_content

    def test_path_uyumlulugu(self):
        """Klasör adlarının Path ile uyumlu olduğunu test et"""
        for klasor in GEREKLI_KLASORLER:
            # Windows ve Unix uyumluluğu için geçersiz karakterleri kontrol et
            gecersiz_karakterler = ["<", ">", ":", '"', "|", "?", "*"]
            for karakter in gecersiz_karakterler:
                assert karakter not in klasor, f"Klasör adında geçersiz karakter: {klasor}"

            # Path oluşturulabilirliğini test et
            try:
                test_path = Path(klasor)
                assert test_path.name == klasor
            except Exception as e:
                pytest.fail(f"Klasör adı Path ile uyumlu değil: {klasor}, Hata: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
