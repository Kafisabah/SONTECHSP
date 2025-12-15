# Version: 0.1.0
# Last Update: 2024-12-15
# Module: test_kayit_property
# Description: Kayıt sistemi property testleri
# Changelog:
# - 0.1.0: İlk sürüm, kayıt sistemi property testleri oluşturuldu

"""
Kayıt Sistemi Property Testleri

Bu modül kayıt sisteminin doğruluk özelliklerini test eder.
"""

import tempfile
import logging
from pathlib import Path
from typing import List
from io import StringIO
import sys

import pytest
from hypothesis import given, strategies as st, settings, assume

from sontechsp.uygulama.cekirdek.kayit import KayitSistemi


# Test stratejileri
log_mesaji_strategy = st.text(min_size=1, max_size=200).filter(
    lambda x: x.strip() and '\n' not in x and '\r' not in x
)

log_seviyesi_strategy = st.sampled_from(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])


class KayitTestYardimcisi:
    """Kayıt testleri için yardımcı sınıf"""
    
    @staticmethod
    def gecici_log_klasoru_olustur() -> str:
        """Geçici log klasörü oluşturur"""
        return tempfile.mkdtemp(prefix='sontechsp_test_logs_')
    
    @staticmethod
    def dosya_icerigini_oku(dosya_yolu: Path) -> str:
        """Dosya içeriğini okur"""
        try:
            with open(dosya_yolu, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""
    
    @staticmethod
    def konsol_ciktisini_yakala(func, *args, **kwargs):
        """Konsol çıktısını yakalar"""
        eski_stdout = sys.stdout
        sys.stdout = yakalanan = StringIO()
        try:
            func(*args, **kwargs)
            return yakalanan.getvalue()
        finally:
            sys.stdout = eski_stdout


# **Feature: cekirdek-altyapi, Property 2: Log çift yazım garantisi**
@settings(max_examples=100)
@given(
    mesaj=log_mesaji_strategy,
    seviye=log_seviyesi_strategy
)
def test_log_cift_yazim_garantisi(mesaj, seviye):
    """
    Özellik 2: Log çift yazım garantisi
    Herhangi bir log mesajı için, mesaj hem dosyaya hem konsola yazılmalıdır
    Doğrular: Gereksinim 2.1
    """
    assume(mesaj.strip())
    
    # Geçici log klasörü oluştur
    log_klasoru = KayitTestYardimcisi.gecici_log_klasoru_olustur()
    
    try:
        # Kayıt sistemini oluştur
        kayit = KayitSistemi(
            log_klasoru=log_klasoru,
            log_seviyesi='DEBUG'  # Tüm seviyeleri yakala
        )
        
        # Log fonksiyonunu seç
        log_func = getattr(kayit, seviye.lower())
        
        # Konsol çıktısını yakala
        konsol_ciktisi = KayitTestYardimcisi.konsol_ciktisini_yakala(log_func, mesaj)
        
        # Dosya içeriğini oku
        log_dosyasi = kayit.log_dosyasi_yolu()
        dosya_icerigi = KayitTestYardimcisi.dosya_icerigini_oku(log_dosyasi)
        
        # Çift yazım kontrolü
        assert mesaj in konsol_ciktisi, f"Mesaj konsola yazılmadı: {mesaj}"
        assert mesaj in dosya_icerigi, f"Mesaj dosyaya yazılmadı: {mesaj}"
        
        # Seviye kontrolü
        turkce_seviye_map = {
            'DEBUG': 'HATA_AYIKLAMA',
            'INFO': 'BİLGİ', 
            'WARNING': 'UYARI',
            'ERROR': 'HATA',
            'CRITICAL': 'KRİTİK'
        }
        
        beklenen_seviye = turkce_seviye_map.get(seviye, seviye)
        assert beklenen_seviye in konsol_ciktisi, f"Seviye konsola yazılmadı: {beklenen_seviye}"
        assert beklenen_seviye in dosya_icerigi, f"Seviye dosyaya yazılmadı: {beklenen_seviye}"
        
    finally:
        # Temizlik
        import shutil
        shutil.rmtree(log_klasoru, ignore_errors=True)


# **Feature: cekirdek-altyapi, Property 3: Log seviye filtreleme**
@settings(max_examples=100)
@given(
    ayarlanan_seviye=log_seviyesi_strategy,
    mesaj_seviyesi=log_seviyesi_strategy,
    mesaj=log_mesaji_strategy
)
def test_log_seviye_filtreleme(ayarlanan_seviye, mesaj_seviyesi, mesaj):
    """
    Özellik 3: Log seviye filtreleme
    Herhangi bir log seviyesi ayarı için, sadece belirtilen seviye ve üstü mesajlar kaydedilmelidir
    Doğrular: Gereksinim 2.2
    """
    assume(mesaj.strip())
    
    # Seviye öncelik sırası
    seviye_oncelik = {
        'DEBUG': 10,
        'INFO': 20,
        'WARNING': 30,
        'ERROR': 40,
        'CRITICAL': 50
    }
    
    # Geçici log klasörü oluştur
    log_klasoru = KayitTestYardimcisi.gecici_log_klasoru_olustur()
    
    try:
        # Kayıt sistemini oluştur
        kayit = KayitSistemi(
            log_klasoru=log_klasoru,
            log_seviyesi=ayarlanan_seviye
        )
        
        # Log fonksiyonunu seç
        log_func = getattr(kayit, mesaj_seviyesi.lower())
        
        # Konsol çıktısını yakala
        konsol_ciktisi = KayitTestYardimcisi.konsol_ciktisini_yakala(log_func, mesaj)
        
        # Dosya içeriğini oku
        log_dosyasi = kayit.log_dosyasi_yolu()
        dosya_icerigi = KayitTestYardimcisi.dosya_icerigini_oku(log_dosyasi)
        
        # Filtreleme kontrolü
        mesaj_seviye_degeri = seviye_oncelik[mesaj_seviyesi]
        ayarlanan_seviye_degeri = seviye_oncelik[ayarlanan_seviye]
        
        if mesaj_seviye_degeri >= ayarlanan_seviye_degeri:
            # Mesaj kaydedilmeli
            assert mesaj in konsol_ciktisi, f"Yeterli seviyedeki mesaj konsola yazılmadı: {mesaj}"
            assert mesaj in dosya_icerigi, f"Yeterli seviyedeki mesaj dosyaya yazılmadı: {mesaj}"
        else:
            # Mesaj kaydedilmemeli
            assert mesaj not in konsol_ciktisi, f"Yetersiz seviyedeki mesaj konsola yazıldı: {mesaj}"
            assert mesaj not in dosya_icerigi, f"Yetersiz seviyedeki mesaj dosyaya yazıldı: {mesaj}"
        
    finally:
        # Temizlik
        import shutil
        shutil.rmtree(log_klasoru, ignore_errors=True)


# **Feature: cekirdek-altyapi, Property 4: Log ayar uyumluluğu**
@settings(max_examples=100)
@given(
    log_seviyesi=log_seviyesi_strategy,
    dosya_boyutu=st.integers(min_value=1024, max_value=1048576),  # 1KB - 1MB
    dosya_sayisi=st.integers(min_value=1, max_value=10),
    mesaj=log_mesaji_strategy
)
def test_log_ayar_uyumlulugu(log_seviyesi, dosya_boyutu, dosya_sayisi, mesaj):
    """
    Özellik 4: Log ayar uyumluluğu
    Herhangi bir log ayar kombinasyonu için, sistem ayarlara uygun davranış sergilemelidir
    Doğrular: Gereksinim 2.5
    """
    assume(mesaj.strip())
    
    # Geçici log klasörü oluştur
    log_klasoru = KayitTestYardimcisi.gecici_log_klasoru_olustur()
    
    try:
        # Kayıt sistemini oluştur
        kayit = KayitSistemi(
            log_klasoru=log_klasoru,
            log_seviyesi=log_seviyesi,
            log_dosya_boyutu=dosya_boyutu,
            log_dosya_sayisi=dosya_sayisi
        )
        
        # İstatistikleri kontrol et
        istatistikler = kayit.log_istatistikleri()
        
        # Ayar uyumluluğu kontrolü
        assert istatistikler['log_seviyesi'] == log_seviyesi, (
            f"Log seviyesi ayarı uyumsuz: {istatistikler['log_seviyesi']} != {log_seviyesi}"
        )
        
        assert istatistikler['maksimum_dosya_boyutu'] == dosya_boyutu, (
            f"Dosya boyutu ayarı uyumsuz: {istatistikler['maksimum_dosya_boyutu']} != {dosya_boyutu}"
        )
        
        assert istatistikler['maksimum_dosya_sayisi'] == dosya_sayisi, (
            f"Dosya sayısı ayarı uyumsuz: {istatistikler['maksimum_dosya_sayisi']} != {dosya_sayisi}"
        )
        
        assert Path(istatistikler['log_klasoru']) == Path(log_klasoru), (
            f"Log klasörü ayarı uyumsuz: {istatistikler['log_klasoru']} != {log_klasoru}"
        )
        
        # Mesaj yazma testi
        kayit.info(mesaj)
        
        # Log dosyasının oluştuğunu kontrol et
        log_dosyasi = kayit.log_dosyasi_yolu()
        assert log_dosyasi.exists(), "Log dosyası oluşturulmadı"
        
        # Seviye değiştirme testi
        yeni_seviye = 'ERROR' if log_seviyesi != 'ERROR' else 'INFO'
        kayit.log_seviyesi_degistir(yeni_seviye)
        
        guncel_istatistikler = kayit.log_istatistikleri()
        assert guncel_istatistikler['log_seviyesi'] == yeni_seviye, (
            f"Seviye değişikliği uygulanmadı: {guncel_istatistikler['log_seviyesi']} != {yeni_seviye}"
        )
        
    finally:
        # Temizlik
        import shutil
        shutil.rmtree(log_klasoru, ignore_errors=True)


def test_kayit_sistemi_temel_islevsellik():
    """Kayıt sisteminin temel işlevselliğini test eder"""
    log_klasoru = KayitTestYardimcisi.gecici_log_klasoru_olustur()
    
    try:
        kayit = KayitSistemi(log_klasoru=log_klasoru, log_seviyesi='DEBUG')
        
        # Tüm seviyeler için test
        kayit.debug("Test debug mesajı")
        kayit.info("Test info mesajı")
        kayit.warning("Test warning mesajı")
        kayit.error("Test error mesajı")
        kayit.critical("Test critical mesajı")
        
        # Log dosyasının oluştuğunu kontrol et
        log_dosyasi = kayit.log_dosyasi_yolu()
        assert log_dosyasi.exists()
        
        # İçerik kontrolü
        dosya_icerigi = KayitTestYardimcisi.dosya_icerigini_oku(log_dosyasi)
        assert "Test debug mesajı" in dosya_icerigi
        assert "Test info mesajı" in dosya_icerigi
        assert "Test warning mesajı" in dosya_icerigi
        assert "Test error mesajı" in dosya_icerigi
        assert "Test critical mesajı" in dosya_icerigi
        
        # Türkçe seviye isimleri kontrolü
        assert "HATA_AYIKLAMA" in dosya_icerigi
        assert "BİLGİ" in dosya_icerigi
        assert "UYARI" in dosya_icerigi
        assert "HATA" in dosya_icerigi
        assert "KRİTİK" in dosya_icerigi
        
        # İstatistikler
        istatistikler = kayit.log_istatistikleri()
        assert istatistikler['dosya_sayisi'] >= 1
        assert istatistikler['aktif_dosya_boyutu'] > 0
        
    finally:
        import shutil
        shutil.rmtree(log_klasoru, ignore_errors=True)


def test_log_dosya_dondurme():
    """Log dosya döndürme işlevselliğini test eder"""
    log_klasoru = KayitTestYardimcisi.gecici_log_klasoru_olustur()
    
    try:
        # Küçük dosya boyutu ile test
        kayit = KayitSistemi(
            log_klasoru=log_klasoru,
            log_seviyesi='INFO',
            log_dosya_boyutu=1024,  # 1KB
            log_dosya_sayisi=3
        )
        
        # Büyük mesajlar yazarak dosya döndürmeyi tetikle
        for i in range(50):
            kayit.info(f"Bu çok uzun bir test mesajıdır - {i} " + "x" * 100)
        
        # Birden fazla log dosyası oluşmuş olmalı
        log_dosyalari = kayit.log_dosyalarini_listele()
        assert len(log_dosyalari) > 1, "Log dosya döndürme çalışmadı"
        
    finally:
        import shutil
        shutil.rmtree(log_klasoru, ignore_errors=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])