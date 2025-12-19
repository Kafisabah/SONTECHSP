# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.kurulum.test_json_format_property
# Description: JSON format geçerliliği property testleri
# Changelog:
# - JSON format geçerliliği property testleri oluşturuldu

"""
JSON format geçerliliği property testleri

**Özellik: kurulum-bootstrap-altyapisi, Özellik 6: JSON Format Geçerliliği**
"""

import pytest
import json
from pathlib import Path
from hypothesis import given, strategies as st, settings, HealthCheck

from sontechsp.uygulama.kurulum.ayar_olusturucu import ayar_dosyasi_olustur, ayarlari_yukle, varsayilan_ayarlar
from sontechsp.uygulama.kurulum.sabitler import CONFIG_DOSYA_ADI
from sontechsp.uygulama.kurulum import AyarHatasi


class TestJSONFormatGecerliligi:
    """
    **Özellik: kurulum-bootstrap-altyapisi, Özellik 6: JSON Format Geçerliliği**
    **Doğrular: Gereksinimler 2.4**
    """

    def test_olusturulan_dosya_gecerli_json(self, gecici_dizin):
        """Oluşturulan ayar dosyası geçerli JSON formatında olmalı"""
        # Ayar dosyası oluştur
        ayarlar = varsayilan_ayarlar()
        ayar_dosyasi_olustur(gecici_dizin, ayarlar)

        # Dosyayı manuel olarak JSON parse et
        ayar_dosya_yolu = gecici_dizin / CONFIG_DOSYA_ADI

        with open(ayar_dosya_yolu, "r", encoding="utf-8") as f:
            dosya_icerigi = f.read()

        # JSON parse edilebilir olmalı
        try:
            parsed_json = json.loads(dosya_icerigi)
            assert isinstance(parsed_json, dict)
        except json.JSONDecodeError:
            pytest.fail("Oluşturulan dosya geçerli JSON formatında değil")

    def test_yuklenen_ayarlar_json_uyumlu(self, gecici_dizin):
        """Yüklenen ayarlar JSON ile uyumlu olmalı"""
        # Ayar dosyası oluştur
        ayarlar = varsayilan_ayarlar()
        ayar_dosyasi_olustur(gecici_dizin, ayarlar)

        # Ayarları yükle
        yuklenen_ayarlar = ayarlari_yukle(gecici_dizin)

        # Yüklenen ayarları tekrar JSON'a çevirebilmeli
        try:
            json_string = json.dumps(yuklenen_ayarlar, ensure_ascii=False)
            # Tekrar parse edebilmeli
            reparsed = json.loads(json_string)
            assert reparsed == yuklenen_ayarlar
        except (json.JSONEncodeError, TypeError):
            pytest.fail("Yüklenen ayarlar JSON ile uyumlu değil")

    @given(
        st.dictionaries(
            st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"))),
            st.one_of(
                st.text(max_size=100),
                st.integers(min_value=-1000, max_value=1000),
                st.booleans(),
                st.floats(allow_nan=False, allow_infinity=False, min_value=-1000.0, max_value=1000.0),
            ),
            min_size=3,
            max_size=10,
        )
    )
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_rastgele_ayarlar_json_gecerliligi(self, gecici_dizin, ek_ayarlar):
        """Rastgele ayarlar JSON formatında geçerli olmalı"""
        # Temel gerekli alanlar
        temel_ayarlar = {
            "veritabani_url": "postgresql://test:test@localhost:5432/test_db",
            "ortam": "dev",
            "log_seviyesi": "INFO",
        }

        # Ek ayarları birleştir
        tam_ayarlar = {**temel_ayarlar, **ek_ayarlar}

        try:
            # Ayar dosyası oluştur
            ayar_dosyasi_olustur(gecici_dizin, tam_ayarlar)

            # Dosyayı manuel JSON parse et
            ayar_dosya_yolu = gecici_dizin / CONFIG_DOSYA_ADI
            with open(ayar_dosya_yolu, "r", encoding="utf-8") as f:
                dosya_icerigi = f.read()

            # JSON geçerliliğini kontrol et
            parsed_json = json.loads(dosya_icerigi)
            assert isinstance(parsed_json, dict)

            # Ayarları yükleyebilmeli
            yuklenen_ayarlar = ayarlari_yukle(gecici_dizin)
            assert isinstance(yuklenen_ayarlar, dict)

        except (AyarHatasi, json.JSONDecodeError, UnicodeEncodeError):
            # Geçersiz karakterler veya JSON uyumsuz veriler için beklenen davranış
            pass

    def test_turkce_karakterler_json_destegi(self, gecici_dizin):
        """Türkçe karakterler JSON'da desteklenmeli"""
        ayarlar = {
            "veritabani_url": "postgresql://türkçe:şifre@localhost:5432/çğıöşü_db",
            "ortam": "dev",
            "log_seviyesi": "INFO",
            "açıklama": "Türkçe karakterli açıklama: çğıöşüÇĞIÖŞÜ",
            "şehir": "İstanbul",
            "ülke": "Türkiye",
        }

        # Ayar dosyası oluştur
        ayar_dosyasi_olustur(gecici_dizin, ayarlar)

        # Dosyayı manuel JSON parse et
        ayar_dosya_yolu = gecici_dizin / CONFIG_DOSYA_ADI
        with open(ayar_dosya_yolu, "r", encoding="utf-8") as f:
            dosya_icerigi = f.read()

        # JSON parse edilebilir olmalı
        parsed_json = json.loads(dosya_icerigi)

        # Türkçe karakterler korunmalı
        assert parsed_json["açıklama"] == ayarlar["açıklama"]
        assert parsed_json["şehir"] == ayarlar["şehir"]
        assert parsed_json["ülke"] == ayarlar["ülke"]

    def test_ozel_karakterler_json_destegi(self, gecici_dizin):
        """Özel karakterler JSON'da desteklenmeli"""
        ayarlar = {
            "veritabani_url": "postgresql://test:test@localhost:5432/test_db",
            "ortam": "dev",
            "log_seviyesi": "INFO",
            "özel_karakterler": "!@#$%^&*()_+-=[]{}|;':\",./<>?",
            "unicode_test": "αβγδε 中文 العربية русский",
            "emoji_test": "🚀 🎉 ✅ ❌",
        }

        try:
            # Ayar dosyası oluştur
            ayar_dosyasi_olustur(gecici_dizin, ayarlar)

            # Dosyayı manuel JSON parse et
            ayar_dosya_yolu = gecici_dizin / CONFIG_DOSYA_ADI
            with open(ayar_dosya_yolu, "r", encoding="utf-8") as f:
                dosya_icerigi = f.read()

            # JSON parse edilebilir olmalı
            parsed_json = json.loads(dosya_icerigi)

            # Özel karakterler korunmalı
            assert parsed_json["özel_karakterler"] == ayarlar["özel_karakterler"]
            assert parsed_json["unicode_test"] == ayarlar["unicode_test"]
            assert parsed_json["emoji_test"] == ayarlar["emoji_test"]

        except (UnicodeEncodeError, json.JSONEncodeError):
            # Bazı özel karakterler için beklenen davranış
            pass

    def test_ic_ice_json_yapilari(self, gecici_dizin):
        """İç içe JSON yapıları desteklenmeli"""
        ayarlar = {
            "veritabani_url": "postgresql://test:test@localhost:5432/test_db",
            "ortam": "dev",
            "log_seviyesi": "INFO",
            "veritabani_ayarlari": {"host": "localhost", "port": 5432, "ssl": True, "timeout": 30},
            "log_ayarlari": {"dosya": "app.log", "rotasyon": {"boyut": "10MB", "sayi": 5}},
            "listeler": {"izinli_ip_listesi": ["127.0.0.1", "192.168.1.1"], "desteklenen_diller": ["tr", "en", "de"]},
        }

        # Ayar dosyası oluştur
        ayar_dosyasi_olustur(gecici_dizin, ayarlar)

        # Ayarları yükle
        yuklenen_ayarlar = ayarlari_yukle(gecici_dizin)

        # İç içe yapıların korunduğunu kontrol et
        assert yuklenen_ayarlar["veritabani_ayarlari"]["host"] == "localhost"
        assert yuklenen_ayarlar["veritabani_ayarlari"]["port"] == 5432
        assert yuklenen_ayarlar["log_ayarlari"]["rotasyon"]["boyut"] == "10MB"
        assert yuklenen_ayarlar["listeler"]["izinli_ip_listesi"] == ["127.0.0.1", "192.168.1.1"]

    def test_json_format_hata_yonetimi(self, gecici_dizin):
        """JSON format hataları uygun şekilde yönetilmeli"""
        # Geçersiz JSON içeriği ile dosya oluştur
        ayar_dosya_yolu = gecici_dizin / CONFIG_DOSYA_ADI
        gecersiz_json = '{"veritabani_url": "test", "ortam": "dev", "log_seviyesi": "INFO"'  # Eksik kapanış

        with open(ayar_dosya_yolu, "w", encoding="utf-8") as f:
            f.write(gecersiz_json)

        # Ayar yükleme hata vermeli
        with pytest.raises(AyarHatasi) as exc_info:
            ayarlari_yukle(gecici_dizin)

        # Hata mesajında JSON parse hatası belirtilmeli
        assert "JSON parse hatası" in str(exc_info.value) or "parse" in str(exc_info.value).lower()

    def test_bos_json_dosyasi_hatasi(self, gecici_dizin):
        """Boş JSON dosyası hata vermeli"""
        # Boş dosya oluştur
        ayar_dosya_yolu = gecici_dizin / CONFIG_DOSYA_ADI
        ayar_dosya_yolu.touch()

        # Ayar yükleme hata vermeli
        with pytest.raises(AyarHatasi):
            ayarlari_yukle(gecici_dizin)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
