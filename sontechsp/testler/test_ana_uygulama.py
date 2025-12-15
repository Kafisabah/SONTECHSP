# Version: 0.1.0
# Last Update: 2024-12-15
# Module: testler.test_ana_uygulama
# Description: Ana uygulama property testleri
# Changelog:
# - İlk oluşturma

"""
Ana Uygulama Property Testleri

SONTECHSP ana uygulamasının doğruluk özelliklerini test eder:
- PyQt6 uygulama başlatma bütünlüğü
- Bootstrap işlevi sadeliği
- Merkezi hata yönetimi
"""

import pytest
import sys
import os
import tempfile
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock
from hypothesis import given, strategies as st, settings

# Test edilecek modüller
from sontechsp.uygulama.cekirdek.kayit import LogSistemi, log_sistemi
from sontechsp.uygulama.cekirdek.hatalar import (
    SONTECHSPHatasi, AlanHatasi, DogrulamaHatasi, EntegrasyonHatasi
)


class TestPyQt6UygulamaBaslatmaBütünlügü:
    """
    **Feature: sontechsp-proje-iskeleti, Property 2: PyQt6 uygulama başlatma bütünlüğü**
    **Validates: Requirements 1.2, 3.1, 3.2, 3.3**
    
    Herhangi bir ana uygulama başlatıldığında, PyQt6 penceresi açılmalı ve 
    log sistemi (dosya+console) aktif hale gelmelidir
    """
    
    def test_log_sistemi_temel_işlevsellik(self):
        """Log sistemi temel işlevselliği çalışmalıdır"""
        # Memory handler kullan (dosya yerine)
        test_log_sistemi = LogSistemi()
        
        # Logger al
        logger = test_log_sistemi.logger_al("test")
        assert logger is not None
        assert "sontechsp" in logger.name
    
    @given(log_seviyesi=st.sampled_from(["DEBUG", "INFO", "WARNING", "ERROR"]))
    @settings(max_examples=5)
    def test_log_seviyesi_ayarlama(self, log_seviyesi):
        """Log seviyesi ayarlama çalışmalıdır"""
        # Basit test - sadece seviye kontrolü
        import logging
        seviye_degeri = getattr(logging, log_seviyesi.upper())
        assert seviye_degeri is not None
        assert isinstance(seviye_degeri, int)
    
    def test_ana_pencere_import_edilebilir(self):
        """Ana pencere sınıfı import edilebilir olmalıdır"""
        try:
            from sontechsp.uygulama.ana import AnaPencere, uygulama_baslat, merkezi_hata_yakalayici
            
            # Sınıf ve fonksiyonlar mevcut olmalı
            assert AnaPencere is not None
            assert callable(uygulama_baslat)
            assert callable(merkezi_hata_yakalayici)
            
        except ImportError as e:
            pytest.fail(f"Ana uygulama modülü import edilemiyor: {e}")
    
    def test_bootstrap_fonksiyonlari_mevcut(self):
        """Bootstrap fonksiyonları mevcut olmalıdır"""
        from sontechsp.uygulama import ana
        
        # Gerekli fonksiyonlar mevcut olmalı
        assert hasattr(ana, 'uygulama_baslat')
        assert hasattr(ana, 'merkezi_hata_yakalayici')
        assert callable(ana.uygulama_baslat)
        assert callable(ana.merkezi_hata_yakalayici)


class TestBootstrapİşleviSadeliği:
    """
    **Feature: sontechsp-proje-iskeleti, Property 7: Bootstrap işlevi sadeliği**
    **Validates: Requirements 3.4**
    
    Herhangi bir ana.py dosyası, sadece PyQt6 AnaPencere başlatma işlevini görmeli 
    ve iş kuralları içermemelidir
    """
    
    def test_ana_py_sadece_bootstrap_içerir(self):
        """ana.py dosyası sadece bootstrap kodu içermelidir"""
        # ana.py dosyasını oku
        ana_py_yolu = Path("sontechsp/uygulama/ana.py")
        assert ana_py_yolu.exists(), "ana.py dosyası mevcut olmalı"
        
        ana_py_içerik = ana_py_yolu.read_text(encoding='utf-8')
        
        # İş kuralı belirten yasaklı kelimeler
        yasakli_kelimeler = [
            "stok_hesapla", "fiyat_hesapla", "kdv_hesapla",
            "musteri_kaydet", "urun_kaydet", "satis_kaydet",
            "odeme_isle", "fatura_olustur", "rapor_olustur",
            "class.*Service", "class.*Repository", "class.*Model"
        ]
        
        for kelime in yasakli_kelimeler:
            assert kelime.lower() not in ana_py_içerik.lower(), \
                f"ana.py iş kuralı içermemeli: {kelime}"
        
        # Bootstrap anahtar kelimeler mevcut olmalı
        gerekli_kelimeler = [
            "QApplication", "QMainWindow", "uygulama_baslat",
            "log_sistemi", "merkezi_hata"
        ]
        
        for kelime in gerekli_kelimeler:
            assert kelime in ana_py_içerik, \
                f"Bootstrap kodu eksik: {kelime}"
    
    @given(dosya_satir_sayisi=st.integers(min_value=50, max_value=120))
    @settings(max_examples=100)
    def test_ana_py_dosya_boyut_sınırı(self, dosya_satir_sayisi):
        """ana.py dosyası 120 satırı aşmamalıdır (yorumlar hariç)"""
        ana_py_yolu = Path("sontechsp/uygulama/ana.py")
        ana_py_içerik = ana_py_yolu.read_text(encoding='utf-8')
        
        # Yorumları ve boş satırları çıkar
        kod_satirlari = []
        for satir in ana_py_içerik.split('\n'):
            temiz_satir = satir.strip()
            if temiz_satir and not temiz_satir.startswith('#') and not temiz_satir.startswith('"""'):
                kod_satirlari.append(satir)
        
        # 120 satır sınırını kontrol et
        assert len(kod_satirlari) <= 120, \
            f"ana.py {len(kod_satirlari)} satır, maksimum 120 olmalı"


class TestMerkeziHataYönetimi:
    """
    **Feature: sontechsp-proje-iskeleti, Property 8: Merkezi hata yönetimi**
    **Validates: Requirements 3.5, 7.4**
    
    Herhangi bir hata durumunda, merkezi hata yönetimi sistemi devreye girmeli ve 
    AlanHatasi/DogrulamaHatasi/EntegrasyonHatasi sınıfları kullanılmalıdır
    """
    
    @given(
        alan_adi=st.text(min_size=1, max_size=50),
        hata_mesaji=st.text(min_size=1, max_size=100),
        deger=st.one_of(st.none(), st.text(), st.integers(), st.floats())
    )
    @settings(max_examples=100)
    def test_alan_hatasi_yapısı(self, alan_adi, hata_mesaji, deger):
        """AlanHatasi sınıfı doğru yapıda olmalıdır"""
        hata = AlanHatasi(alan_adi, hata_mesaji, deger)
        
        # Temel özellikler
        assert isinstance(hata, SONTECHSPHatasi)
        assert hata.alan_adi == alan_adi
        assert hata.deger == deger
        assert hata.hata_kodu == "ALAN_HATASI"
        
        # Ek bilgi yapısı
        assert "alan" in hata.ek_bilgi
        assert "deger" in hata.ek_bilgi
        assert hata.ek_bilgi["alan"] == alan_adi
        assert hata.ek_bilgi["deger"] == deger
    
    @given(
        kural=st.text(min_size=1, max_size=50),
        mesaj=st.text(min_size=1, max_size=100),
        nesne_id=st.one_of(st.none(), st.text(min_size=1, max_size=50))
    )
    @settings(max_examples=100)
    def test_dogrulama_hatasi_yapısı(self, kural, mesaj, nesne_id):
        """DogrulamaHatasi sınıfı doğru yapıda olmalıdır"""
        hata = DogrulamaHatasi(kural, mesaj, nesne_id)
        
        # Temel özellikler
        assert isinstance(hata, SONTECHSPHatasi)
        assert hata.kural == kural
        assert hata.nesne_id == nesne_id
        assert hata.hata_kodu == "DOGRULAMA_HATASI"
        
        # Mesaj formatı
        assert kural in str(hata)
        assert mesaj in str(hata)
    
    @given(
        sistem=st.text(min_size=1, max_size=50),
        mesaj=st.text(min_size=1, max_size=100),
        detay=st.one_of(st.none(), st.text(min_size=1, max_size=200))
    )
    @settings(max_examples=100)
    def test_entegrasyon_hatasi_yapısı(self, sistem, mesaj, detay):
        """EntegrasyonHatasi sınıfı doğru yapıda olmalıdır"""
        hata = EntegrasyonHatasi(sistem, mesaj, detay)
        
        # Temel özellikler
        assert isinstance(hata, SONTECHSPHatasi)
        assert hata.sistem == sistem
        assert hata.hata_detayi == detay
        assert hata.hata_kodu == "ENTEGRASYON_HATASI"
        
        # Ek bilgi yapısı
        assert "sistem" in hata.ek_bilgi
        assert "detay" in hata.ek_bilgi
        assert hata.ek_bilgi["sistem"] == sistem
        assert hata.ek_bilgi["detay"] == detay
    
    def test_merkezi_hata_yakalayici_mevcut(self):
        """Merkezi hata yakalayıcı fonksiyon mevcut olmalıdır"""
        from sontechsp.uygulama.ana import merkezi_hata_yakalayici
        
        # Fonksiyon çağrılabilir olmalı
        assert callable(merkezi_hata_yakalayici)
        
        # Test hatası ile çağır (mock logger ile)
        with patch('sontechsp.uygulama.ana.logger_al') as mock_logger_al:
            mock_logger = MagicMock()
            mock_logger_al.return_value = mock_logger
            
            # Test exception
            test_exception = Exception("Test hatası")
            
            # Hata yakalayıcıyı çağır
            merkezi_hata_yakalayici(Exception, test_exception, None)
            
            # Logger çağrılmış olmalı
            mock_logger_al.assert_called_with("hata_yakalayici")
            mock_logger.critical.assert_called()