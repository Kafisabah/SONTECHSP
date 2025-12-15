# Version: 0.1.0
# Last Update: 2024-12-15
# Module: testler.test_cekirdek_modul_bagimsizligi
# Description: Çekirdek modül bağımsızlığı property testleri
# Changelog:
# - İlk oluşturma

"""
Çekirdek Modül Bağımsızlığı Property Testleri

SONTECHSP çekirdek modülünün diğer katmanlardan bağımsızlığını test eder:
- Çekirdek modül bileşenlerinin ayrı dosyalarda olması
- UI ve veritabanı katmanlarından bağımsızlık
- Oturum bağlamı yönetimi
"""

import pytest
import os
import ast
import importlib.util
from pathlib import Path
from hypothesis import given, strategies as st, settings


class TestCekirdekModulBagimsizligi:
    """
    **Feature: sontechsp-proje-iskeleti, Property 13: Çekirdek modül bağımsızlığı**
    **Validates: Requirements 7.1, 7.2, 7.3, 7.5**
    
    Herhangi bir çekirdek modülü, ayarlar/kayit/hatalar/yetki/oturum bileşenlerini 
    ayrı dosyalarda içermeli ve UI/veritabanı katmanlarından bağımsız olmalıdır
    """
    
    def test_cekirdek_bilesenler_ayri_dosyalarda(self):
        """Çekirdek bileşenler ayrı dosyalarda olmalıdır"""
        cekirdek_klasoru = Path("sontechsp/uygulama/cekirdek")
        assert cekirdek_klasoru.exists(), "Çekirdek klasörü mevcut olmalı"
        
        beklenen_dosyalar = [
            "ayarlar.py",
            "kayit.py", 
            "hatalar.py",
            "yetki.py",
            "oturum.py"
        ]
        
        for dosya_adi in beklenen_dosyalar:
            dosya_yolu = cekirdek_klasoru / dosya_adi
            assert dosya_yolu.exists(), f"Çekirdek bileşen dosyası mevcut değil: {dosya_adi}"
            assert dosya_yolu.is_file(), f"Çekirdek bileşen yolu bir dosya değil: {dosya_adi}"
            
            # Dosya boş olmamalı
            dosya_içerik = dosya_yolu.read_text(encoding='utf-8')
            assert len(dosya_içerik.strip()) > 0, f"Çekirdek bileşen dosyası boş: {dosya_adi}"
    
    @given(st.sampled_from([
        "ayarlar.py", "kayit.py", "hatalar.py", "yetki.py", "oturum.py"
    ]))
    @settings(max_examples=100)
    def test_cekirdek_dosya_bagimsizligi_property(self, dosya_adi):
        """Herhangi bir çekirdek dosyası UI/DB katmanlarından bağımsız olmalıdır"""
        dosya_yolu = Path(f"sontechsp/uygulama/cekirdek/{dosya_adi}")
        
        if not dosya_yolu.exists():
            pytest.skip(f"Dosya henüz oluşturulmamış: {dosya_adi}")
        
        dosya_içerik = dosya_yolu.read_text(encoding='utf-8')
        
        # UI katmanı bağımlılıkları (yasaklı)
        yasakli_ui_importlar = [
            "from PyQt", "import PyQt", "from PySide", "import PySide",
            "from sontechsp.uygulama.arayuz", "import sontechsp.uygulama.arayuz",
            "QWidget", "QMainWindow", "QApplication", "QDialog"
        ]
        
        # Veritabanı katmanı bağımlılıkları (yasaklı)
        yasakli_db_importlar = [
            "from sqlalchemy", "import sqlalchemy", "from alembic", "import alembic",
            "from sontechsp.uygulama.veritabani", "import sontechsp.uygulama.veritabani",
            "Session", "engine", "create_engine", "declarative_base"
        ]
        
        # İş modülü bağımlılıkları (yasaklı)
        yasakli_modul_importlar = [
            "from sontechsp.uygulama.moduller", "import sontechsp.uygulama.moduller",
            "from sontechsp.uygulama.servisler", "import sontechsp.uygulama.servisler"
        ]
        
        tüm_yasakli_importlar = yasakli_ui_importlar + yasakli_db_importlar + yasakli_modul_importlar
        
        for yasakli_import in tüm_yasakli_importlar:
            assert yasakli_import not in dosya_içerik, \
                f"{dosya_adi} dosyası yasaklı bağımlılık içeriyor: {yasakli_import}"
    
    def test_hata_siniflari_tanimli(self):
        """Hata sınıfları doğru şekilde tanımlanmış olmalıdır"""
        try:
            from sontechsp.uygulama.cekirdek.hatalar import (
                SONTECHSPHatasi, AlanHatasi, DogrulamaHatasi, EntegrasyonHatasi
            )
            
            # Temel hata sınıfı mevcut olmalı
            assert SONTECHSPHatasi is not None
            assert issubclass(SONTECHSPHatasi, Exception)
            
            # Özel hata sınıfları mevcut olmalı
            assert AlanHatasi is not None
            assert DogrulamaHatasi is not None
            assert EntegrasyonHatasi is not None
            
            # Hiyerarşi doğru olmalı
            assert issubclass(AlanHatasi, SONTECHSPHatasi)
            assert issubclass(DogrulamaHatasi, SONTECHSPHatasi)
            assert issubclass(EntegrasyonHatasi, SONTECHSPHatasi)
            
        except ImportError as e:
            pytest.fail(f"Hata sınıfları import edilemiyor: {e}")
    
    def test_log_sistemi_tanimli(self):
        """Log sistemi doğru şekilde tanımlanmış olmalıdır"""
        try:
            from sontechsp.uygulama.cekirdek.kayit import LogSistemi, log_sistemi
            
            # LogSistemi sınıfı mevcut olmalı
            assert LogSistemi is not None
            assert callable(LogSistemi)
            
            # Global log_sistemi instance mevcut olmalı
            assert log_sistemi is not None
            assert isinstance(log_sistemi, LogSistemi)
            
            # Temel metodlar mevcut olmalı
            assert hasattr(log_sistemi, 'logger_al')
            assert callable(log_sistemi.logger_al)
            
        except ImportError as e:
            pytest.fail(f"Log sistemi import edilemiyor: {e}")
    
    @given(
        modul_adi=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd'), whitelist_characters='_')),
        log_seviyesi=st.sampled_from(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    )
    @settings(max_examples=50)
    def test_log_sistemi_logger_alma_property(self, modul_adi, log_seviyesi):
        """Log sistemi herhangi bir modül için logger alabilmelidir"""
        try:
            from sontechsp.uygulama.cekirdek.kayit import log_sistemi
            
            # Logger al
            logger = log_sistemi.logger_al(modul_adi)
            assert logger is not None
            
            # Logger adı doğru olmalı
            assert modul_adi in logger.name or "sontechsp" in logger.name
            
            # Logger seviyesi ayarlanabilir olmalı
            import logging
            seviye_degeri = getattr(logging, log_seviyesi.upper())
            logger.setLevel(seviye_degeri)
            assert logger.level == seviye_degeri
            
        except ImportError:
            pytest.skip("Log sistemi henüz oluşturulmamış")
    
    def test_oturum_baglami_tanimli(self):
        """Oturum bağlamı yönetimi tanımlanmış olmalıdır"""
        try:
            from sontechsp.uygulama.cekirdek.oturum import OturumBaglami, oturum_baglami
            
            # OturumBaglami sınıfı mevcut olmalı
            assert OturumBaglami is not None
            assert callable(OturumBaglami)
            
            # Global oturum_baglami instance mevcut olmalı
            assert oturum_baglami is not None
            assert isinstance(oturum_baglami, OturumBaglami)
            
            # Temel özellikler mevcut olmalı
            assert hasattr(oturum_baglami, 'kullanici_id')
            assert hasattr(oturum_baglami, 'magaza_id')
            assert hasattr(oturum_baglami, 'terminal_id')
            
        except ImportError as e:
            pytest.fail(f"Oturum bağlamı import edilemiyor: {e}")
    
    @given(
        kullanici_id=st.one_of(st.none(), st.integers(min_value=1, max_value=999999)),
        magaza_id=st.one_of(st.none(), st.integers(min_value=1, max_value=9999)),
        terminal_id=st.one_of(st.none(), st.integers(min_value=1, max_value=99))
    )
    @settings(max_examples=50)
    def test_oturum_baglami_ayarlama_property(self, kullanici_id, magaza_id, terminal_id):
        """Oturum bağlamı herhangi bir değer kombinasyonu ile ayarlanabilmelidir"""
        try:
            from sontechsp.uygulama.cekirdek.oturum import oturum_baglami
            
            # Değerleri ayarla
            oturum_baglami.kullanici_id = kullanici_id
            oturum_baglami.magaza_id = magaza_id
            oturum_baglami.terminal_id = terminal_id
            
            # Değerlerin doğru ayarlandığını kontrol et
            assert oturum_baglami.kullanici_id == kullanici_id
            assert oturum_baglami.magaza_id == magaza_id
            assert oturum_baglami.terminal_id == terminal_id
            
        except ImportError:
            pytest.skip("Oturum bağlamı henüz oluşturulmamış")
    
    def test_ayarlar_sistemi_tanimli(self):
        """Ayarlar sistemi tanımlanmış olmalıdır"""
        try:
            from sontechsp.uygulama.cekirdek.ayarlar import AyarlarSistemi, ayarlar_sistemi
            
            # AyarlarSistemi sınıfı mevcut olmalı
            assert AyarlarSistemi is not None
            assert callable(AyarlarSistemi)
            
            # Global ayarlar_sistemi instance mevcut olmalı
            assert ayarlar_sistemi is not None
            assert isinstance(ayarlar_sistemi, AyarlarSistemi)
            
            # Temel metodlar mevcut olmalı
            assert hasattr(ayarlar_sistemi, 'ayar_al')
            assert hasattr(ayarlar_sistemi, 'ayar_ayarla')
            assert callable(ayarlar_sistemi.ayar_al)
            assert callable(ayarlar_sistemi.ayar_ayarla)
            
        except ImportError as e:
            pytest.fail(f"Ayarlar sistemi import edilemiyor: {e}")
    
    def test_yetki_sistemi_tanimli(self):
        """Yetki sistemi tanımlanmış olmalıdır"""
        try:
            from sontechsp.uygulama.cekirdek.yetki import YetkiSistemi, yetki_sistemi
            
            # YetkiSistemi sınıfı mevcut olmalı
            assert YetkiSistemi is not None
            assert callable(YetkiSistemi)
            
            # Global yetki_sistemi instance mevcut olmalı
            assert yetki_sistemi is not None
            assert isinstance(yetki_sistemi, YetkiSistemi)
            
            # Temel metodlar mevcut olmalı
            assert hasattr(yetki_sistemi, 'yetki_kontrol')
            assert callable(yetki_sistemi.yetki_kontrol)
            
        except ImportError as e:
            pytest.fail(f"Yetki sistemi import edilemiyor: {e}")