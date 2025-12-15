# Version: 0.1.0
# Last Update: 2024-12-15
# Module: test_otomatik_kurulum_sureci
# Description: SONTECHSP otomatik kurulum süreci property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Otomatik Kurulum Süreci Property Testleri

**Feature: sontechsp-proje-iskeleti, Property 14: Otomatik kurulum süreci**

Otomatik kurulum sürecinin doğruluğunu test eder:
- Klasör oluşturma işlemleri
- Yapılandırma dosyası oluşturma
- Veritabanı bağlantı testi
- Admin kullanıcı oluşturma
- Kurulum tamamlanma işaretlemesi
"""

import os
import json
import tempfile
import sqlite3
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock

import pytest
from hypothesis import given, strategies as st, assume, settings

# Test edilecek modül
from sontechsp.uygulama.kurulum.baslat import KurulumYoneticisi


class TestOtomatikKurulumSureci:
    """SONTECHSP otomatik kurulum süreci testleri"""
    
    @pytest.fixture
    def gecici_proje_koku(self):
        """Geçici proje kökü oluşturur"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def kurulum_yoneticisi(self, gecici_proje_koku):
        """Test için kurulum yöneticisi oluşturur"""
        with patch.object(KurulumYoneticisi, '__init__', lambda self: None):
            yonetici = KurulumYoneticisi()
            yonetici.proje_koku = gecici_proje_koku
            yonetici.logger = MagicMock()
            yonetici.kurulum_tamamlandi = False
            return yonetici
    
    def test_klasor_olusturma_islemi(self, kurulum_yoneticisi):
        """
        **Feature: sontechsp-proje-iskeleti, Property 14: Otomatik kurulum süreci**
        
        Gerekli klasörler otomatik olarak oluşturulmalıdır.
        """
        # Kurulum öncesi klasörler mevcut olmamalı
        gerekli_klasorler = ["logs", "data", "config", "temp", "backup", "uploads"]
        
        for klasor_adi in gerekli_klasorler:
            klasor_yolu = kurulum_yoneticisi.proje_koku / klasor_adi
            assert not klasor_yolu.exists(), f"Klasör zaten mevcut: {klasor_adi}"
        
        # Klasör oluşturma işlemini çalıştır
        kurulum_yoneticisi._klasorleri_olustur()
        
        # Kurulum sonrası tüm klasörler mevcut olmalı
        for klasor_adi in gerekli_klasorler:
            klasor_yolu = kurulum_yoneticisi.proje_koku / klasor_adi
            assert klasor_yolu.exists(), f"Klasör oluşturulmadı: {klasor_adi}"
            assert klasor_yolu.is_dir(), f"Klasör değil: {klasor_adi}"
    
    def test_yapilandirma_dosyasi_olusturma(self, kurulum_yoneticisi):
        """
        **Feature: sontechsp-proje-iskeleti, Property 14: Otomatik kurulum süreci**
        
        Yapılandırma dosyası şablonu oluşturulmalıdır.
        """
        config_dosyasi = kurulum_yoneticisi.proje_koku / "config" / "config.json"
        env_dosyasi = kurulum_yoneticisi.proje_koku / ".env"
        
        # Kurulum öncesi dosyalar mevcut olmamalı
        assert not config_dosyasi.exists(), "Config dosyası zaten mevcut"
        assert not env_dosyasi.exists(), ".env dosyası zaten mevcut"
        
        # Yapılandırma dosyası oluşturma işlemini çalıştır
        kurulum_yoneticisi._yapilandirma_dosyasi_olustur()
        
        # Kurulum sonrası dosyalar mevcut olmalı
        assert config_dosyasi.exists(), "Config dosyası oluşturulmadı"
        assert env_dosyasi.exists(), ".env dosyası oluşturulmadı"
        
        # Config dosyası geçerli JSON olmalı
        with open(config_dosyasi, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Gerekli config bölümleri mevcut olmalı
        gerekli_bolumler = ["database", "sqlite", "logging", "security", "ui", "business"]
        for bolum in gerekli_bolumler:
            assert bolum in config_data, f"Config bölümü eksik: {bolum}"
        
        # .env dosyası gerekli değişkenleri içermeli
        env_icerik = env_dosyasi.read_text(encoding='utf-8')
        gerekli_env_degiskenleri = ["DATABASE_URL", "SECRET_KEY", "DEBUG", "LOG_LEVEL"]
        for degisken in gerekli_env_degiskenleri:
            assert degisken in env_icerik, f"Env değişkeni eksik: {degisken}"
    
    def test_sqlite_cache_olusturma(self, kurulum_yoneticisi):
        """
        **Feature: sontechsp-proje-iskeleti, Property 14: Otomatik kurulum süreci**
        
        SQLite cache veritabanı oluşturulmalıdır.
        """
        sqlite_yolu = kurulum_yoneticisi.proje_koku / "data" / "sontechsp_cache.db"
        
        # Kurulum öncesi SQLite dosyası mevcut olmamalı
        assert not sqlite_yolu.exists(), "SQLite dosyası zaten mevcut"
        
        # SQLite cache oluşturma işlemini çalıştır
        kurulum_yoneticisi._sqlite_cache_olustur()
        
        # Kurulum sonrası SQLite dosyası mevcut olmalı
        assert sqlite_yolu.exists(), "SQLite dosyası oluşturulmadı"
        
        # SQLite dosyası geçerli veritabanı olmalı
        with sqlite3.connect(sqlite_yolu) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()[0]
            assert version is not None, "SQLite sürümü alınamadı"
    
    def test_kurulum_tamamlandi_isaretlemesi(self, kurulum_yoneticisi):
        """
        **Feature: sontechsp-proje-iskeleti, Property 14: Otomatik kurulum süreci**
        
        Kurulum tamamlandı işaretlemesi yapılmalıdır.
        """
        kurulum_dosyasi = kurulum_yoneticisi.proje_koku / "config" / ".kurulum_tamamlandi"
        
        # Kurulum öncesi işaretleme dosyası mevcut olmamalı
        assert not kurulum_dosyasi.exists(), "Kurulum dosyası zaten mevcut"
        
        # Kurulum tamamlandı işaretlemesi yap
        kurulum_yoneticisi._kurulum_tamamlandi_isaretle()
        
        # Kurulum sonrası işaretleme dosyası mevcut olmalı
        assert kurulum_dosyasi.exists(), "Kurulum dosyası oluşturulmadı"
        
        # Dosya geçerli JSON olmalı
        with open(kurulum_dosyasi, 'r', encoding='utf-8') as f:
            kurulum_bilgileri = json.load(f)
        
        # Gerekli bilgiler mevcut olmalı
        gerekli_alanlar = ["kurulum_tarihi", "versiyon", "kurulum_turu"]
        for alan in gerekli_alanlar:
            assert alan in kurulum_bilgileri, f"Kurulum bilgisi eksik: {alan}"
    
    def test_kurulum_durumu_kontrolu(self, kurulum_yoneticisi):
        """
        **Feature: sontechsp-proje-iskeleti, Property 14: Otomatik kurulum süreci**
        
        Kurulum durumu doğru şekilde kontrol edilmelidir.
        """
        # İlk durumda kurulum tamamlanmamış olmalı
        durum = kurulum_yoneticisi.kurulum_durumu_kontrol_et()
        assert not durum["kurulum_tamamlandi"], "Kurulum zaten tamamlanmış görünüyor"
        assert durum["kurulum_bilgileri"] is None, "Kurulum bilgileri olmamalı"
        
        # Kurulum tamamlandı işaretlemesi yap
        kurulum_yoneticisi._kurulum_tamamlandi_isaretle()
        
        # Kurulum sonrası durum tamamlanmış olmalı
        durum = kurulum_yoneticisi.kurulum_durumu_kontrol_et()
        assert durum["kurulum_tamamlandi"], "Kurulum tamamlanmış görünmüyor"
        assert durum["kurulum_bilgileri"] is not None, "Kurulum bilgileri eksik"
    
    def test_hizli_kurulum_sureci(self, kurulum_yoneticisi):
        """
        **Feature: sontechsp-proje-iskeleti, Property 14: Otomatik kurulum süreci**
        
        Hızlı kurulum süreci başarılı olmalıdır.
        """
        # Hızlı kurulum çalıştır
        basarili = kurulum_yoneticisi.hizli_kurulum_yap()
        
        # Kurulum başarılı olmalı
        assert basarili, "Hızlı kurulum başarısız"
        
        # Temel klasörler oluşturulmuş olmalı
        temel_klasorler = ["logs", "data", "config"]
        for klasor_adi in temel_klasorler:
            klasor_yolu = kurulum_yoneticisi.proje_koku / klasor_adi
            assert klasor_yolu.exists(), f"Temel klasör oluşturulmadı: {klasor_adi}"
        
        # Config dosyası oluşturulmuş olmalı
        config_dosyasi = kurulum_yoneticisi.proje_koku / "config" / "config.json"
        assert config_dosyasi.exists(), "Config dosyası oluşturulmadı"
    
    @patch('sontechsp.uygulama.kurulum.baslat.KurulumYoneticisi._postgresql_baglanti_testi')
    @patch('sontechsp.uygulama.kurulum.baslat.KurulumYoneticisi._migration_calistir')
    @patch('sontechsp.uygulama.kurulum.baslat.KurulumYoneticisi._admin_kullanici_olustur')
    def test_tam_kurulum_sureci(self, mock_admin, mock_migration, mock_pg_test, kurulum_yoneticisi):
        """
        **Feature: sontechsp-proje-iskeleti, Property 14: Otomatik kurulum süreci**
        
        Tam kurulum süreci başarılı olmalıdır.
        """
        # Mock'ları başarılı olarak ayarla
        mock_pg_test.return_value = True
        mock_migration.return_value = None
        mock_admin.return_value = None
        
        # Tam kurulum çalıştır
        basarili = kurulum_yoneticisi.tam_kurulum_yap()
        
        # Kurulum başarılı olmalı
        assert basarili, "Tam kurulum başarısız"
        assert kurulum_yoneticisi.kurulum_tamamlandi, "Kurulum tamamlandı işaretlenmemiş"
        
        # Tüm klasörler oluşturulmuş olmalı
        gerekli_klasorler = ["logs", "data", "config", "temp", "backup", "uploads"]
        for klasor_adi in gerekli_klasorler:
            klasor_yolu = kurulum_yoneticisi.proje_koku / klasor_adi
            assert klasor_yolu.exists(), f"Klasör oluşturulmadı: {klasor_adi}"
        
        # Kurulum tamamlandı dosyası oluşturulmuş olmalı
        kurulum_dosyasi = kurulum_yoneticisi.proje_koku / "config" / ".kurulum_tamamlandi"
        assert kurulum_dosyasi.exists(), "Kurulum tamamlandı dosyası oluşturulmadı"


@given(st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=10))
@settings(max_examples=20)
def test_klasor_olusturma_property(klasor_isimleri: List[str]):
    """
    **Feature: sontechsp-proje-iskeleti, Property 14: Otomatik kurulum süreci**
    
    Herhangi bir klasör ismi listesi için klasör oluşturma işlemi çalışmalıdır.
    """
    assume(all(isim.strip() for isim in klasor_isimleri))
    
    # Geçerli klasör isimleri filtrele
    gecerli_isimler = []
    for isim in klasor_isimleri:
        # Windows için geçersiz karakterleri temizle
        temiz_isim = ''.join(c for c in isim if c.isalnum() or c in '_-')
        if temiz_isim and len(temiz_isim) <= 50:
            gecerli_isimler.append(temiz_isim)
    
    assume(len(gecerli_isimler) > 0)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Klasörleri oluştur
        for klasor_ismi in gecerli_isimler:
            klasor_yolu = temp_path / klasor_ismi
            klasor_yolu.mkdir(parents=True, exist_ok=True)
            
            # Klasör oluşturulmuş olmalı
            assert klasor_yolu.exists()
            assert klasor_yolu.is_dir()


@given(st.dictionaries(
    st.text(min_size=1, max_size=20), 
    st.one_of(st.text(), st.integers(), st.booleans()),
    min_size=1, max_size=10
))
@settings(max_examples=15)
def test_config_dosyasi_olusturma_property(config_verisi: Dict[str, Any]):
    """
    **Feature: sontechsp-proje-iskeleti, Property 14: Otomatik kurulum süreci**
    
    Herhangi bir config verisi için JSON dosyası oluşturulabilmelidir.
    """
    assume(len(config_verisi) > 0)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dosyasi = Path(temp_dir) / "config.json"
        
        # JSON dosyası oluştur
        with open(config_dosyasi, 'w', encoding='utf-8') as f:
            json.dump(config_verisi, f, indent=2, ensure_ascii=False)
        
        # Dosya oluşturulmuş olmalı
        assert config_dosyasi.exists()
        
        # Dosya geçerli JSON olmalı
        with open(config_dosyasi, 'r', encoding='utf-8') as f:
            okunan_veri = json.load(f)
        
        # Veri korunmuş olmalı
        assert len(okunan_veri) == len(config_verisi)


@given(st.text(min_size=1, max_size=100))
@settings(max_examples=20)
def test_sqlite_veritabani_olusturma_property(veritabani_adi: str):
    """
    **Feature: sontechsp-proje-iskeleti, Property 14: Otomatik kurulum süreci**
    
    Herhangi bir veritabanı adı için SQLite dosyası oluşturulabilmelidir.
    """
    # Geçerli dosya adı oluştur
    temiz_ad = ''.join(c for c in veritabani_adi if c.isalnum() or c in '_-')
    assume(len(temiz_ad) > 0)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        sqlite_yolu = Path(temp_dir) / f"{temiz_ad}.db"
        
        # SQLite veritabanı oluştur
        conn = sqlite3.connect(sqlite_yolu)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()[0]
        finally:
            conn.close()
        
        # Dosya oluşturulmuş olmalı
        assert sqlite_yolu.exists()
        assert version is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])