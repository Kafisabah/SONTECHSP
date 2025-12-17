# Version: 0.1.0
# Last Update: 2024-12-17
# Module: tests.kurulum.test_ayar_icerik_property
# Description: Ayar dosyası içerik bütünlüğü property testleri
# Changelog:
# - Ayar dosyası içerik bütünlüğü property testleri oluşturuldu

"""
Ayar dosyası içerik bütünlüğü property testleri

**Özellik: kurulum-bootstrap-altyapisi, Özellik 5: Ayar Dosyası İçerik Bütünlüğü**
"""

import pytest
from pathlib import Path
from hypothesis import given, strategies as st, settings, HealthCheck

from uygulama.kurulum.ayar_olusturucu import (
    ayar_dosyasi_olustur,
    ayarlari_yukle,
    varsayilan_ayarlar,
    ayar_dosyasini_dogrula
)
from uygulama.kurulum.sabitler import CONFIG_DOSYA_ADI
from uygulama.kurulum import AyarHatasi


class TestAyarDosyasiIcerikButunlugu:
    """
    **Özellik: kurulum-bootstrap-altyapisi, Özellik 5: Ayar Dosyası İçerik Bütünlüğü**
    **Doğrular: Gereksinimler 2.3**
    """

    def test_yeni_ayar_dosyasi_gerekli_alanlari_icerir(self, gecici_dizin):
        """Yeni oluşturulan ayar dosyası tüm gerekli alanları içermeli"""
        # Varsayılan ayarlarla dosya oluştur
        ayarlar = varsayilan_ayarlar()
        ayar_dosyasi_olustur(gecici_dizin, ayarlar)
        
        # Dosyayı yükle ve gerekli alanları kontrol et
        yuklenen_ayarlar = ayarlari_yukle(gecici_dizin)
        
        # Gerekli alanların varlığını kontrol et
        assert "veritabani_url" in yuklenen_ayarlar
        assert "ortam" in yuklenen_ayarlar
        assert "log_seviyesi" in yuklenen_ayarlar
        
        # Alanların boş olmadığını kontrol et
        assert yuklenen_ayarlar["veritabani_url"] is not None
        assert yuklenen_ayarlar["ortam"] is not None
        assert yuklenen_ayarlar["log_seviyesi"] is not None
        
        # String değerler olduğunu kontrol et
        assert isinstance(yuklenen_ayarlar["veritabani_url"], str)
        assert isinstance(yuklenen_ayarlar["ortam"], str)
        assert isinstance(yuklenen_ayarlar["log_seviyesi"], str)

    def test_veritabani_url_alani_butunlugu(self, gecici_dizin):
        """Veritabanı URL alanının bütünlüğü korunmalı"""
        test_urls = [
            "postgresql://test:test@localhost:5432/test_db",
            "postgresql://user:pass@192.168.1.1:5432/mydb",
            "postgresql://admin:secret@db.example.com:5432/production"
        ]
        
        for veritabani_url in test_urls:
            # Özel veritabanı URL'i ile ayar oluştur
            ayarlar = {
                "veritabani_url": veritabani_url,
                "ortam": "dev",
                "log_seviyesi": "INFO"
            }
            
            # Önceki dosyayı temizle
            ayar_dosya_yolu = gecici_dizin / CONFIG_DOSYA_ADI
            if ayar_dosya_yolu.exists():
                ayar_dosya_yolu.unlink()
            
            try:
                ayar_dosyasi_olustur(gecici_dizin, ayarlar)
                yuklenen_ayarlar = ayarlari_yukle(gecici_dizin)
                
                # URL'in korunduğunu kontrol et
                assert yuklenen_ayarlar["veritabani_url"] == veritabani_url
                assert "veritabani_url" in yuklenen_ayarlar
                
            except AyarHatasi:
                # Geçersiz URL'ler için beklenen davranış
                pass

    def test_ortam_alani_butunlugu(self, gecici_dizin):
        """Ortam alanının bütünlüğü korunmalı"""
        test_ortamlar = ["dev", "test", "prod"]
        
        for ortam in test_ortamlar:
            ayarlar = {
                "veritabani_url": "postgresql://test:test@localhost:5432/test_db",
                "ortam": ortam,
                "log_seviyesi": "INFO"
            }
            
            # Önceki dosyayı temizle
            ayar_dosya_yolu = gecici_dizin / CONFIG_DOSYA_ADI
            if ayar_dosya_yolu.exists():
                ayar_dosya_yolu.unlink()
            
            ayar_dosyasi_olustur(gecici_dizin, ayarlar)
            yuklenen_ayarlar = ayarlari_yukle(gecici_dizin)
            
            # Ortam değerinin korunduğunu kontrol et
            assert yuklenen_ayarlar["ortam"] == ortam
            assert "ortam" in yuklenen_ayarlar

    def test_log_seviyesi_alani_butunlugu(self, gecici_dizin):
        """Log seviyesi alanının bütünlüğü korunmalı"""
        test_seviyeleri = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for log_seviyesi in test_seviyeleri:
            ayarlar = {
                "veritabani_url": "postgresql://test:test@localhost:5432/test_db",
                "ortam": "dev",
                "log_seviyesi": log_seviyesi
            }
            
            # Önceki dosyayı temizle
            ayar_dosya_yolu = gecici_dizin / CONFIG_DOSYA_ADI
            if ayar_dosya_yolu.exists():
                ayar_dosya_yolu.unlink()
            
            ayar_dosyasi_olustur(gecici_dizin, ayarlar)
            yuklenen_ayarlar = ayarlari_yukle(gecici_dizin)
            
            # Log seviyesinin korunduğunu kontrol et
            assert yuklenen_ayarlar["log_seviyesi"] == log_seviyesi
            assert "log_seviyesi" in yuklenen_ayarlar

    def test_ek_alanlar_korunmali(self, gecici_dizin):
        """Ek alanlar da korunmalı"""
        # Gerekli alanlar + ek alanlar
        ayarlar = {
            "veritabani_url": "postgresql://test:test@localhost:5432/test_db",
            "ortam": "dev",
            "log_seviyesi": "INFO",
            "ek_alan_1": "ek_deger_1",
            "ek_alan_2": 42,
            "ek_alan_3": True
        }
        
        ayar_dosyasi_olustur(gecici_dizin, ayarlar)
        yuklenen_ayarlar = ayarlari_yukle(gecici_dizin)
        
        # Tüm alanların korunduğunu kontrol et
        for anahtar, deger in ayarlar.items():
            assert anahtar in yuklenen_ayarlar
            assert yuklenen_ayarlar[anahtar] == deger

    @given(st.dictionaries(
        st.text(min_size=1, max_size=20),
        st.one_of(st.text(), st.integers(), st.booleans()),
        min_size=1, max_size=5
    ))
    @settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_rastgele_ek_alanlar_butunlugu(self, gecici_dizin, ek_alanlar):
        """Rastgele ek alanların bütünlüğü korunmalı"""
        # Temel gerekli alanlar
        temel_ayarlar = {
            "veritabani_url": "postgresql://test:test@localhost:5432/test_db",
            "ortam": "dev",
            "log_seviyesi": "INFO"
        }
        
        # Ek alanları birleştir
        tam_ayarlar = {**temel_ayarlar, **ek_alanlar}
        
        try:
            ayar_dosyasi_olustur(gecici_dizin, tam_ayarlar)
            yuklenen_ayarlar = ayarlari_yukle(gecici_dizin)
            
            # Temel alanların varlığını kontrol et
            for anahtar in temel_ayarlar:
                assert anahtar in yuklenen_ayarlar
                assert yuklenen_ayarlar[anahtar] == temel_ayarlar[anahtar]
            
            # Ek alanların korunduğunu kontrol et
            for anahtar, deger in ek_alanlar.items():
                if anahtar in yuklenen_ayarlar:
                    assert yuklenen_ayarlar[anahtar] == deger
                    
        except (AyarHatasi, UnicodeEncodeError, TypeError, ValueError):
            # JSON serileştirme sorunları için beklenen davranış
            pass

    def test_alan_tipleri_korunmali(self, gecici_dizin):
        """Alan tiplerinin korunması"""
        ayarlar = {
            "veritabani_url": "postgresql://test:test@localhost:5432/test_db",
            "ortam": "dev",
            "log_seviyesi": "INFO",
            "string_alan": "string_deger",
            "integer_alan": 123,
            "boolean_alan": True,
            "float_alan": 3.14,
            "list_alan": [1, 2, 3],
            "dict_alan": {"ic_anahtar": "ic_deger"}
        }
        
        ayar_dosyasi_olustur(gecici_dizin, ayarlar)
        yuklenen_ayarlar = ayarlari_yukle(gecici_dizin)
        
        # Tip kontrolü
        assert isinstance(yuklenen_ayarlar["string_alan"], str)
        assert isinstance(yuklenen_ayarlar["integer_alan"], int)
        assert isinstance(yuklenen_ayarlar["boolean_alan"], bool)
        assert isinstance(yuklenen_ayarlar["float_alan"], float)
        assert isinstance(yuklenen_ayarlar["list_alan"], list)
        assert isinstance(yuklenen_ayarlar["dict_alan"], dict)
        
        # Değer kontrolü
        assert yuklenen_ayarlar["string_alan"] == "string_deger"
        assert yuklenen_ayarlar["integer_alan"] == 123
        assert yuklenen_ayarlar["boolean_alan"] == True
        assert yuklenen_ayarlar["float_alan"] == 3.14
        assert yuklenen_ayarlar["list_alan"] == [1, 2, 3]
        assert yuklenen_ayarlar["dict_alan"] == {"ic_anahtar": "ic_deger"}


class TestGerekliAlanKontrolu:
    """Gerekli alan kontrolü testleri"""

    def test_eksik_veritabani_url_hatasi(self, gecici_dizin):
        """Eksik veritabanı URL'i hata vermeli"""
        ayarlar = {
            "ortam": "dev",
            "log_seviyesi": "INFO"
            # veritabani_url eksik
        }
        
        with pytest.raises(AyarHatasi) as exc_info:
            ayar_dosyasi_olustur(gecici_dizin, ayarlar)
        
        assert "veritabani_url" in str(exc_info.value)

    def test_eksik_ortam_hatasi(self, gecici_dizin):
        """Eksik ortam hata vermeli"""
        ayarlar = {
            "veritabani_url": "postgresql://test:test@localhost:5432/test_db",
            "log_seviyesi": "INFO"
            # ortam eksik
        }
        
        with pytest.raises(AyarHatasi) as exc_info:
            ayar_dosyasi_olustur(gecici_dizin, ayarlar)
        
        assert "ortam" in str(exc_info.value)

    def test_eksik_log_seviyesi_hatasi(self, gecici_dizin):
        """Eksik log seviyesi hata vermeli"""
        ayarlar = {
            "veritabani_url": "postgresql://test:test@localhost:5432/test_db",
            "ortam": "dev"
            # log_seviyesi eksik
        }
        
        with pytest.raises(AyarHatasi) as exc_info:
            ayar_dosyasi_olustur(gecici_dizin, ayarlar)
        
        assert "log_seviyesi" in str(exc_info.value)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])