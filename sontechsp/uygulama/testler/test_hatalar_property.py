# Version: 0.1.0
# Last Update: 2024-12-15
# Module: test_hatalar_property
# Description: Hata yönetimi property testleri
# Changelog:
# - 0.1.0: İlk sürüm, hata yönetimi property testleri oluşturuldu

"""
Hata Yönetimi Property Testleri

Bu modül hata yönetim sisteminin doğruluk özelliklerini test eder.
"""

import tempfile
import logging
from pathlib import Path
from typing import Dict, Any
from io import StringIO
import sys

import pytest
from hypothesis import given, strategies as st, settings, assume

from sontechsp.uygulama.cekirdek.hatalar import (
    SontechHatasi, AlanHatasi, DogrulamaHatasi, EntegrasyonHatasi,
    HataYoneticisi, HataSeviyesi, get_hata_yoneticisi
)
from sontechsp.uygulama.cekirdek.kayit import KayitSistemi


# Test stratejileri
hata_mesaji_strategy = st.text(min_size=1, max_size=200).filter(
    lambda x: x.strip() and '\n' not in x and '\r' not in x
)

alan_adi_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pc")),
    min_size=1,
    max_size=50
).filter(lambda x: x.replace('_', '').isalnum())

hata_tipi_strategy = st.sampled_from([AlanHatasi, DogrulamaHatasi, EntegrasyonHatasi])


class HataTestYardimcisi:
    """Hata testleri için yardımcı sınıf"""
    
    @staticmethod
    def gecici_log_sistemi_olustur() -> tuple:
        """Geçici log sistemi oluşturur"""
        log_klasoru = tempfile.mkdtemp(prefix='sontechsp_hata_test_')
        kayit = KayitSistemi(log_klasoru=log_klasoru, log_seviyesi='DEBUG')
        return kayit, log_klasoru
    
    @staticmethod
    def log_icerigini_oku(kayit: KayitSistemi) -> str:
        """Log dosyası içeriğini okur"""
        try:
            with open(kayit.log_dosyasi_yolu(), 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""
    
    @staticmethod
    def temizlik_yap(log_klasoru: str) -> None:
        """Geçici dosyaları temizler"""
        import shutil
        shutil.rmtree(log_klasoru, ignore_errors=True)


# **Feature: cekirdek-altyapi, Property 5: Hata loglama tutarlılığı**
@settings(max_examples=100)
@given(
    hata_tipi=hata_tipi_strategy,
    mesaj=hata_mesaji_strategy,
    alan_adi=alan_adi_strategy
)
def test_hata_loglama_tutarliligi(hata_tipi, mesaj, alan_adi):
    """
    Özellik 5: Hata loglama tutarlılığı
    Herhangi bir hata tipi için, uygun log seviyesinde kayıt yapılmalıdır
    Doğrular: Gereksinim 3.4
    """
    assume(mesaj.strip() and alan_adi.strip())
    
    # Geçici log sistemi oluştur
    kayit, log_klasoru = HataTestYardimcisi.gecici_log_sistemi_olustur()
    
    try:
        # Hata oluştur ve fırlat
        if hata_tipi == AlanHatasi:
            hata = AlanHatasi(alan_adi, mesaj)
        elif hata_tipi == DogrulamaHatasi:
            hata = DogrulamaHatasi(alan_adi, mesaj)
        else:  # EntegrasyonHatasi
            hata = EntegrasyonHatasi(alan_adi, mesaj)
        
        # Log içeriğini kontrol et
        log_icerigi = HataTestYardimcisi.log_icerigini_oku(kayit)
        
        # Hata mesajının loglandığını kontrol et
        assert mesaj in log_icerigi, f"Hata mesajı loglanmadı: {mesaj}"
        
        # Hata tipine göre log seviyesi kontrolü
        if hata_tipi == AlanHatasi:
            # Düşük seviye -> WARNING
            assert "UYARI" in log_icerigi, "AlanHatasi UYARI seviyesinde loglanmadı"
        elif hata_tipi == DogrulamaHatasi:
            # Orta seviye -> ERROR
            assert "HATA" in log_icerigi, "DogrulamaHatasi HATA seviyesinde loglanmadı"
        elif hata_tipi == EntegrasyonHatasi:
            # Yüksek seviye -> ERROR
            assert "HATA" in log_icerigi, "EntegrasyonHatasi HATA seviyesinde loglanmadı"
        
        # Hata kodunun loglandığını kontrol et
        assert hata.hata_kodu in log_icerigi, f"Hata kodu loglanmadı: {hata.hata_kodu}"
        
    finally:
        HataTestYardimcisi.temizlik_yap(log_klasoru)


# **Feature: cekirdek-altyapi, Property 6: Türkçe hata mesajı garantisi**
@settings(max_examples=100)
@given(
    hata_tipi=hata_tipi_strategy,
    mesaj=hata_mesaji_strategy,
    alan_adi=alan_adi_strategy
)
def test_turkce_hata_mesaji_garantisi(hata_tipi, mesaj, alan_adi):
    """
    Özellik 6: Türkçe hata mesajı garantisi
    Herhangi bir hata mesajı için, mesaj Türkçe olmalıdır
    Doğrular: Gereksinim 3.5
    """
    assume(mesaj.strip() and alan_adi.strip())
    
    # Hata oluştur
    if hata_tipi == AlanHatasi:
        hata = AlanHatasi(alan_adi, mesaj)
    elif hata_tipi == DogrulamaHatasi:
        hata = DogrulamaHatasi(alan_adi, mesaj)
    else:  # EntegrasyonHatasi
        hata = EntegrasyonHatasi(alan_adi, mesaj)
    
    hata_str = str(hata)
    
    # Türkçe anahtar kelimeler kontrolü
    turkce_kelimeler = {
        AlanHatasi: ["alanında", "hata"],
        DogrulamaHatasi: ["kuralı", "ihlal", "edildi"],
        EntegrasyonHatasi: ["sistemi", "entegrasyon", "hatası"]
    }
    
    beklenen_kelimeler = turkce_kelimeler[hata_tipi]
    for kelime in beklenen_kelimeler:
        assert kelime in hata_str.lower(), (
            f"Türkçe kelime '{kelime}' hata mesajında bulunamadı: {hata_str}"
        )
    
    # Hata kodu formatı kontrolü
    assert "[" in hata_str and "]" in hata_str, (
        f"Hata kodu formatı eksik: {hata_str}"
    )
    
    # Alan adının mesajda yer aldığını kontrol et
    assert alan_adi in hata_str, (
        f"Alan adı hata mesajında bulunamadı: {alan_adi} in {hata_str}"
    )
    
    # Orijinal mesajın yer aldığını kontrol et
    assert mesaj in hata_str, (
        f"Orijinal mesaj hata mesajında bulunamadı: {mesaj} in {hata_str}"
    )


def test_hata_yoneticisi_temel_islevsellik():
    """Hata yöneticisinin temel işlevselliğini test eder"""
    yonetici = HataYoneticisi()
    
    # Farklı hata tipleri oluştur
    alan_hatasi = AlanHatasi("test_alan", "Test alan hatası")
    dogrulama_hatasi = DogrulamaHatasi("test_kural", "Test doğrulama hatası")
    entegrasyon_hatasi = EntegrasyonHatasi("test_sistem", "Test entegrasyon hatası")
    
    # Hataları işle
    yonetici.hata_isle(alan_hatasi)
    yonetici.hata_isle(dogrulama_hatasi)
    yonetici.hata_isle(entegrasyon_hatasi)
    
    # İstatistikleri kontrol et
    istatistikler = yonetici.hata_istatistikleri()
    assert istatistikler['toplam_hata_sayisi'] == 3
    assert 'AlanHatasi' in istatistikler['hata_tipi_sayaclari']
    assert 'DogrulamaHatasi' in istatistikler['hata_tipi_sayaclari']
    assert 'EntegrasyonHatasi' in istatistikler['hata_tipi_sayaclari']
    
    # Son hataları kontrol et
    son_hatalar = yonetici.son_hatalari_getir(3)
    assert len(son_hatalar) == 3
    
    # Kritik hata kontrolü
    kritik_hata = SontechHatasi("Kritik test hatası", seviye=HataSeviyesi.KRITIK)
    yonetici.hata_isle(kritik_hata)
    assert yonetici.kritik_hata_kontrol() == True


def test_hata_sinif_hiyerarsisi():
    """Hata sınıf hiyerarşisinin doğruluğunu test eder"""
    # Temel sınıf kontrolü
    alan_hatasi = AlanHatasi("test", "test mesajı")
    assert isinstance(alan_hatasi, SontechHatasi)
    assert isinstance(alan_hatasi, Exception)
    
    dogrulama_hatasi = DogrulamaHatasi("test", "test mesajı")
    assert isinstance(dogrulama_hatasi, SontechHatasi)
    assert isinstance(dogrulama_hatasi, Exception)
    
    entegrasyon_hatasi = EntegrasyonHatasi("test", "test mesajı")
    assert isinstance(entegrasyon_hatasi, SontechHatasi)
    assert isinstance(entegrasyon_hatasi, Exception)


def test_hata_to_dict_fonksiyonu():
    """Hata sözlük dönüşüm fonksiyonunu test eder"""
    hata = AlanHatasi("test_alan", "Test mesajı", alan_degeri="test_değer")
    hata_dict = hata.to_dict()
    
    assert hata_dict['hata_tipi'] == 'AlanHatasi'
    assert hata_dict['mesaj'] == "'test_alan' alanında hata: Test mesajı"
    assert hata_dict['seviye'] == 'düşük'
    assert 'alan_adi' in hata_dict['ek_bilgi']
    assert hata_dict['ek_bilgi']['alan_adi'] == 'test_alan'


def test_global_hata_yoneticisi():
    """Global hata yöneticisi singleton'ını test eder"""
    yonetici1 = get_hata_yoneticisi()
    yonetici2 = get_hata_yoneticisi()
    
    assert yonetici1 is yonetici2, "Global hata yöneticisi singleton değil"
    assert isinstance(yonetici1, HataYoneticisi)


def test_hata_decorator():
    """Hata yakalama decorator'ını test eder"""
    from sontechsp.uygulama.cekirdek.hatalar import hata_yakala_ve_isle
    
    @hata_yakala_ve_isle
    def hata_firlatacak_fonksiyon():
        raise ValueError("Test hatası")
    
    yonetici = get_hata_yoneticisi()
    yonetici.hata_sayaclarini_sifirla()
    
    with pytest.raises(ValueError):
        hata_firlatacak_fonksiyon()
    
    # Hatanın yakalandığını kontrol et
    istatistikler = yonetici.hata_istatistikleri()
    assert istatistikler['toplam_hata_sayisi'] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])