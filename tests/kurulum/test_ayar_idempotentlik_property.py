# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.kurulum.test_ayar_idempotentlik_property
# Description: Ayar dosyası idempotentlik property testleri
# Changelog:
# - Ayar dosyası idempotentlik property testleri oluşturuldu

"""
Ayar dosyası idempotentlik property testleri

**Özellik: kurulum-bootstrap-altyapisi, Özellik 4: Ayar Dosyası İdempotentliği**
"""

import pytest
import json
from pathlib import Path
from hypothesis import given, strategies as st, settings, HealthCheck

from sontechsp.uygulama.kurulum.ayar_olusturucu import (
    ayar_dosyasi_olustur,
    ayar_dosyasi_var_mi,
    ayarlari_yukle,
    varsayilan_ayarlar,
    ayar_dosyasini_dogrula,
)
from sontechsp.uygulama.kurulum.sabitler import CONFIG_DOSYA_ADI
from sontechsp.uygulama.kurulum import AyarHatasi


class TestAyarDosyasiIdempotentligi:
    """
    **Özellik: kurulum-bootstrap-altyapisi, Özellik 4: Ayar Dosyası İdempotentliği**
    **Doğrular: Gereksinimler 2.2**
    """

    def test_ayar_dosyasi_olusturma_idempotentligi(self, gecici_dizin):
        """Ayar dosyası oluşturma işlemini iki kez çalıştırmak mevcut ayarları korumalı"""
        # İlk ayarları oluştur
        ilk_ayarlar = varsayilan_ayarlar()
        ayar_dosyasi_olustur(gecici_dizin, ilk_ayarlar)

        # Dosyanın oluştuğunu kontrol et
        assert ayar_dosyasi_var_mi(gecici_dizin) == True

        # İlk ayarları yükle
        yuklenen_ayarlar = ayarlari_yukle(gecici_dizin)

        # Farklı ayarlarla ikinci kez oluşturmaya çalış
        ikinci_ayarlar = {
            "veritabani_url": "postgresql://farkli:url@localhost:5432/farkli_db",
            "ortam": "prod",
            "log_seviyesi": "ERROR",
        }

        # İkinci çalıştırma mevcut dosyayı korumalı
        ayar_dosyasi_olustur(gecici_dizin, ikinci_ayarlar)

        # Ayarların değişmediğini kontrol et
        son_ayarlar = ayarlari_yukle(gecici_dizin)
        assert son_ayarlar == yuklenen_ayarlar
        assert son_ayarlar == ilk_ayarlar

    @given(st.integers(min_value=2, max_value=5))
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_coklu_olusturma_idempotentligi(self, gecici_dizin, calistirma_sayisi):
        """Ayar dosyası oluşturmayı n kez çalıştırmak 1 kez çalıştırmakla aynı sonucu vermeli"""
        # İlk ayarları oluştur
        ilk_ayarlar = varsayilan_ayarlar()
        ayar_dosyasi_olustur(gecici_dizin, ilk_ayarlar)

        # İlk durumu kaydet
        ilk_durum = ayarlari_yukle(gecici_dizin)

        # n kez daha çalıştır
        for i in range(calistirma_sayisi - 1):
            farkli_ayarlar = {
                "veritabani_url": f"postgresql://test{i}:pass@localhost:5432/db{i}",
                "ortam": "test",
                "log_seviyesi": "DEBUG",
            }
            ayar_dosyasi_olustur(gecici_dizin, farkli_ayarlar)

        # Son durumu kontrol et
        son_durum = ayarlari_yukle(gecici_dizin)
        assert son_durum == ilk_durum

    def test_mevcut_ayar_dosyasi_korunmali(self, gecici_dizin):
        """Mevcut ayar dosyası korunmalı ve üzerine yazılmamalı"""
        # Manuel olarak özel ayar dosyası oluştur
        ozel_ayarlar = {
            "veritabani_url": "postgresql://ozel:kullanici@localhost:5432/ozel_db",
            "ortam": "prod",
            "log_seviyesi": "WARNING",
            "ozel_alan": "ozel_deger",
        }

        ayar_dosya_yolu = gecici_dizin / CONFIG_DOSYA_ADI
        with open(ayar_dosya_yolu, "w", encoding="utf-8") as f:
            json.dump(ozel_ayarlar, f, indent=2, ensure_ascii=False)

        # Varsayılan ayarlarla oluşturmaya çalış
        varsayilan = varsayilan_ayarlar()
        ayar_dosyasi_olustur(gecici_dizin, varsayilan)

        # Özel ayarların korunduğunu kontrol et
        korunan_ayarlar = ayarlari_yukle(gecici_dizin)
        assert korunan_ayarlar["veritabani_url"] == ozel_ayarlar["veritabani_url"]
        assert korunan_ayarlar["ortam"] == ozel_ayarlar["ortam"]
        assert korunan_ayarlar["log_seviyesi"] == ozel_ayarlar["log_seviyesi"]

    @given(
        st.dictionaries(
            st.sampled_from(["veritabani_url", "ortam", "log_seviyesi"]),
            st.text(min_size=1, max_size=50),
            min_size=3,
            max_size=3,
        )
    )
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_farkli_ayarlarla_idempotentlik(self, gecici_dizin, ayarlar):
        """Farklı ayarlarla idempotentlik korunmalı"""
        # Geçerli ayarlar oluştur
        gecerli_ayarlar = {
            "veritabani_url": "postgresql://test:test@localhost:5432/test_db",
            "ortam": "dev",
            "log_seviyesi": "INFO",
        }

        # İlk oluşturma
        ayar_dosyasi_olustur(gecici_dizin, gecerli_ayarlar)
        ilk_durum = ayarlari_yukle(gecici_dizin)

        # Farklı ayarlarla ikinci oluşturma
        try:
            ayar_dosyasi_olustur(gecici_dizin, ayarlar)
        except AyarHatasi:
            # Geçersiz ayarlar için beklenen davranış
            pass

        # İlk durumun korunduğunu kontrol et
        son_durum = ayarlari_yukle(gecici_dizin)
        assert son_durum == ilk_durum


class TestAyarDosyasiVarligi:
    """Ayar dosyası varlık kontrolü testleri"""

    def test_bos_dizinde_ayar_dosyasi_yok(self, gecici_dizin):
        """Boş dizinde ayar dosyası mevcut değil"""
        assert ayar_dosyasi_var_mi(gecici_dizin) == False

    def test_ayar_dosyasi_oluşturulduktan_sonra_mevcut(self, gecici_dizin):
        """Ayar dosyası oluşturulduktan sonra mevcut"""
        ayarlar = varsayilan_ayarlar()
        ayar_dosyasi_olustur(gecici_dizin, ayarlar)
        assert ayar_dosyasi_var_mi(gecici_dizin) == True

    def test_olmayan_dizinde_ayar_dosyasi_yok(self):
        """Olmayan dizinde ayar dosyası mevcut değil"""
        olmayan_dizin = Path("/olmayan/dizin/yolu")
        assert ayar_dosyasi_var_mi(olmayan_dizin) == False


class TestAyarDogrulama:
    """Ayar doğrulama testleri"""

    def test_varsayilan_ayarlar_gecerli(self):
        """Varsayılan ayarlar geçerli olmalı"""
        ayarlar = varsayilan_ayarlar()
        assert ayar_dosyasini_dogrula(ayarlar) == True

    def test_eksik_alan_gecersiz(self):
        """Eksik alan içeren ayarlar geçersiz"""
        ayarlar = {
            "veritabani_url": "postgresql://test:test@localhost:5432/test_db",
            "ortam": "dev",
            # log_seviyesi eksik
        }
        assert ayar_dosyasini_dogrula(ayarlar) == False

    def test_gecersiz_ortam_gecersiz(self):
        """Geçersiz ortam değeri geçersiz"""
        ayarlar = {
            "veritabani_url": "postgresql://test:test@localhost:5432/test_db",
            "ortam": "gecersiz_ortam",
            "log_seviyesi": "INFO",
        }
        assert ayar_dosyasini_dogrula(ayarlar) == False

    def test_gecersiz_log_seviyesi_gecersiz(self):
        """Geçersiz log seviyesi geçersiz"""
        ayarlar = {
            "veritabani_url": "postgresql://test:test@localhost:5432/test_db",
            "ortam": "dev",
            "log_seviyesi": "GECERSIZ",
        }
        assert ayar_dosyasini_dogrula(ayarlar) == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
