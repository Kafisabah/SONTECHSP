# Version: 0.1.0
# Last Update: 2024-12-15
# Module: test_ayarlar_property
# Description: Ayarlar yönetimi property testleri
# Changelog:
# - 0.1.0: İlk sürüm, ayarlar modülü property testleri oluşturuldu

"""
Ayarlar Yönetimi Property Testleri

Bu modül ayarlar yöneticisinin doğruluk özelliklerini test eder.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest
from hypothesis import given, strategies as st, settings, assume

from sontechsp.uygulama.cekirdek.ayarlar import AyarlarYoneticisi


# Test stratejileri
ayar_anahtari_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")), 
    min_size=1, 
    max_size=20
).filter(lambda x: x.isalnum())

ayar_degeri_strategy = st.one_of(
    st.text(min_size=0, max_size=100),
    st.integers(min_value=0, max_value=1000000),
    st.booleans(),
    st.floats(min_value=0.0, max_value=1000.0, allow_nan=False, allow_infinity=False)
)


class AyarlarTestYardimcisi:
    """Ayarlar testleri için yardımcı sınıf"""
    
    @staticmethod
    def gecici_env_dosyasi_olustur(ayarlar: Dict[str, Any]) -> str:
        """Geçici .env dosyası oluşturur"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            for anahtar, deger in ayarlar.items():
                f.write(f"{anahtar}={deger}\n")
            return f.name
    
    @staticmethod
    def gecici_dosyayi_sil(dosya_yolu: str) -> None:
        """Geçici dosyayı siler"""
        try:
            Path(dosya_yolu).unlink()
        except FileNotFoundError:
            pass


# **Feature: cekirdek-altyapi, Property 1: Ayar okuma tutarlılığı**
@settings(max_examples=100)
@given(
    anahtar=ayar_anahtari_strategy,
    deger=ayar_degeri_strategy
)
def test_ayar_okuma_tutarliligi(anahtar, deger):
    """
    Özellik 1: Ayar okuma tutarlılığı
    Herhangi bir geçerli ayar anahtarı için, ayar okuma işlemi tutarlı sonuç döndürmelidir
    Doğrular: Gereksinim 1.1, 1.3
    """
    assume(anahtar and isinstance(anahtar, str))
    
    # Geçici .env dosyası oluştur
    ayarlar = {anahtar: str(deger)}
    env_dosya = AyarlarTestYardimcisi.gecici_env_dosyasi_olustur(ayarlar)
    
    try:
        yonetici = AyarlarYoneticisi(env_dosya)
        
        # Aynı anahtarı birden fazla kez oku
        sonuc1 = yonetici.ayar_oku(anahtar)
        sonuc2 = yonetici.ayar_oku(anahtar)
        sonuc3 = yonetici.ayar_oku(anahtar)
        
        # Tutarlılık kontrolü
        assert sonuc1 == sonuc2 == sonuc3, (
            f"Ayar okuma tutarsız: {sonuc1} != {sonuc2} != {sonuc3}"
        )
        
        # Tip güvenliği kontrolü
        assert type(sonuc1) == type(sonuc2) == type(sonuc3), (
            f"Tip tutarsızlığı: {type(sonuc1)} != {type(sonuc2)} != {type(sonuc3)}"
        )
        
    finally:
        AyarlarTestYardimcisi.gecici_dosyayi_sil(env_dosya)


# **Feature: cekirdek-altyapi, Property 18: Güvenli yapılandırma yükleme**
@settings(max_examples=100)
@given(
    hassas_anahtar=st.sampled_from(["SIFRE", "PASSWORD", "SECRET_KEY", "TOKEN"]),
    hassas_deger=st.text(min_size=8, max_size=50)
)
def test_guvenli_yapilandirma_yukleme(hassas_anahtar, hassas_deger):
    """
    Özellik 18: Güvenli yapılandırma yükleme
    Herhangi bir .env dosyası için, hassas bilgiler güvenli şekilde yüklenmelidir
    Doğrular: Gereksinim 7.1
    """
    # Geçici .env dosyası oluştur
    ayarlar = {hassas_anahtar: hassas_deger}
    env_dosya = AyarlarTestYardimcisi.gecici_env_dosyasi_olustur(ayarlar)
    
    try:
        yonetici = AyarlarYoneticisi(env_dosya)
        
        # Hassas bilgi yüklenmiş olmalı
        yuklenen_deger = yonetici.ayar_oku(hassas_anahtar)
        assert yuklenen_deger == hassas_deger, (
            f"Hassas bilgi doğru yüklenmedi: {yuklenen_deger} != {hassas_deger}"
        )
        
        # Listeleme sırasında maskelenmiş olmalı
        tum_ayarlar = yonetici.tum_ayarlari_listele()
        assert tum_ayarlar[hassas_anahtar] == "***", (
            f"Hassas bilgi maskelenmedi: {tum_ayarlar[hassas_anahtar]}"
        )
        
    finally:
        AyarlarTestYardimcisi.gecici_dosyayi_sil(env_dosya)


# **Feature: cekirdek-altyapi, Property 19: Yapılandırma doğrulama**
@settings(max_examples=100)
@given(
    zorunlu_ayarlar=st.dictionaries(
        keys=st.sampled_from(["VERITABANI_URL", "LOG_KLASORU", "ORTAM"]),
        values=st.text(min_size=1, max_size=100),
        min_size=1,
        max_size=3
    )
)
def test_yapilandirma_dogrulama(zorunlu_ayarlar):
    """
    Özellik 19: Yapılandırma doğrulama
    Herhangi bir yapılandırma için, zorunlu alanlar kontrol edilmelidir
    Doğrular: Gereksinim 7.2
    """
    # Geçici .env dosyası oluştur
    env_dosya = AyarlarTestYardimcisi.gecici_env_dosyasi_olustur(zorunlu_ayarlar)
    
    try:
        yonetici = AyarlarYoneticisi(env_dosya)
        
        # Tüm zorunlu ayarlar mevcutsa doğrulama başarılı olmalı
        tum_zorunlu_mevcut = all(
            anahtar in zorunlu_ayarlar 
            for anahtar in ["VERITABANI_URL", "LOG_KLASORU", "ORTAM"]
        )
        
        if tum_zorunlu_mevcut:
            assert yonetici.ayar_dogrula() == True
        else:
            # Eksik zorunlu ayar varsa hata fırlatmalı
            with pytest.raises(ValueError, match="Eksik zorunlu ayarlar"):
                yonetici.ayar_dogrula()
                
    finally:
        AyarlarTestYardimcisi.gecici_dosyayi_sil(env_dosya)


# **Feature: cekirdek-altyapi, Property 20: Ortam değişkeni önceliği**
@settings(max_examples=100)
@given(
    anahtar=ayar_anahtari_strategy,
    env_degeri=st.text(min_size=1, max_size=50),
    dosya_degeri=st.text(min_size=1, max_size=50)
)
def test_ortam_degiskeni_onceligi(anahtar, env_degeri, dosya_degeri):
    """
    Özellik 20: Ortam değişkeni önceliği
    Herhangi bir ayar çakışması için, ortam değişkeni öncelikli kullanılmalıdır
    Doğrular: Gereksinim 7.3
    """
    assume(anahtar and env_degeri != dosya_degeri)
    
    # Geçici .env dosyası oluştur
    ayarlar = {anahtar: dosya_degeri}
    env_dosya = AyarlarTestYardimcisi.gecici_env_dosyasi_olustur(ayarlar)
    
    # Ortam değişkenini ayarla
    eski_deger = os.environ.get(anahtar)
    os.environ[anahtar] = env_degeri
    
    try:
        yonetici = AyarlarYoneticisi(env_dosya)
        
        # Ortam değişkeni öncelikli olmalı
        okunan_deger = yonetici.ayar_oku(anahtar)
        assert str(okunan_deger) == env_degeri, (
            f"Ortam değişkeni öncelikli değil: {okunan_deger} != {env_degeri}"
        )
        
    finally:
        # Ortam değişkenini temizle
        if eski_deger is None:
            os.environ.pop(anahtar, None)
        else:
            os.environ[anahtar] = eski_deger
        AyarlarTestYardimcisi.gecici_dosyayi_sil(env_dosya)


# **Feature: cekirdek-altyapi, Property 21: Dinamik ayar algılama**
@settings(max_examples=100)
@given(
    anahtar=ayar_anahtari_strategy,
    ilk_deger=st.text(min_size=1, max_size=50),
    yeni_deger=st.text(min_size=1, max_size=50)
)
def test_dinamik_ayar_algilama(anahtar, ilk_deger, yeni_deger):
    """
    Özellik 21: Dinamik ayar algılama
    Herhangi bir ayar değişikliği için, sistem değişikliği algılamalıdır
    Doğrular: Gereksinim 7.5
    """
    assume(anahtar and ilk_deger != yeni_deger)
    
    # İlk .env dosyası oluştur
    ayarlar = {anahtar: ilk_deger}
    env_dosya = AyarlarTestYardimcisi.gecici_env_dosyasi_olustur(ayarlar)
    
    try:
        yonetici = AyarlarYoneticisi(env_dosya)
        
        # İlk değeri kontrol et
        assert yonetici.ayar_oku(anahtar) == ilk_deger
        
        # Dosyayı güncelle
        with open(env_dosya, 'w', encoding='utf-8') as f:
            f.write(f"{anahtar}={yeni_deger}\n")
        
        # Değişiklik algılanmalı
        degisiklik_var = yonetici.ayar_degisikligini_algi()
        assert degisiklik_var == True, "Ayar değişikliği algılanmadı"
        
        # Yeni değer okunmalı
        assert yonetici.ayar_oku(anahtar) == yeni_deger, (
            f"Yeni değer okunamadı: {yonetici.ayar_oku(anahtar)} != {yeni_deger}"
        )
        
    finally:
        AyarlarTestYardimcisi.gecici_dosyayi_sil(env_dosya)


def test_ayarlar_yoneticisi_temel_islevsellik():
    """Ayarlar yöneticisinin temel işlevselliğini test eder"""
    # Geçici .env dosyası oluştur
    ayarlar = {
        "VERITABANI_URL": "postgresql://test:test@localhost:5432/test",
        "LOG_KLASORU": "test_logs",
        "ORTAM": "test"
    }
    env_dosya = AyarlarTestYardimcisi.gecici_env_dosyasi_olustur(ayarlar)
    
    try:
        yonetici = AyarlarYoneticisi(env_dosya)
        
        # Temel okuma
        assert yonetici.ayar_oku("ORTAM") == "test"
        
        # Zorunlu ayar okuma
        assert yonetici.zorunlu_ayar_oku("VERITABANI_URL") == ayarlar["VERITABANI_URL"]
        
        # Doğrulama
        assert yonetici.ayar_dogrula() == True
        
        # Yapılandırma modeli
        model = yonetici.yapilandirma_modeli_olustur()
        assert model.ortam == "test"
        
    finally:
        AyarlarTestYardimcisi.gecici_dosyayi_sil(env_dosya)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])