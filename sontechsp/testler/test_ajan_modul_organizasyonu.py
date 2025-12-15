# Version: 0.1.0
# Last Update: 2024-12-15
# Module: test_ajan_modul_organizasyonu
# Description: SONTECHSP ajan tabanlı modül organizasyonu property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Ajan Tabanlı Modül Organizasyonu Property Testleri

Bu dosya ajan bazlı modül organizasyonunun doğruluğunu
property-based testing ile kontrol eder.

Ajan-Modül Eşleştirmesi:
- stok_ajani -> stok modülü
- pos_ajani -> pos modülü  
- crm_ajani -> crm modülü
- satis_belge_ajani -> satis_belgeleri modülü
- eticaret_ajani -> eticaret modülü
- ebelge_ajani -> ebelge modülü
- kargo_ajani -> kargo modülü
- rapor_ajani -> raporlar modülü
"""

import os
import pytest
from hypothesis import given, strategies as st
from pathlib import Path


class TestAjanModulOrganizasyonu:
    """SONTECHSP ajan tabanlı modül organizasyonu testleri"""
    
    def test_ajan_modul_eslestirmesi(self):
        """
        **Feature: sontechsp-proje-iskeleti, Property 9: Ajan tabanlı modül organizasyonu**
        
        Herhangi bir yeni modül eklendiğinde, stok/pos/crm/satis_belgeleri/eticaret/ebelge/kargo/raporlar 
        yapısına uyumlu olmalı ve katmanlı mimariyi bozmamalıdır
        **Doğrular: Gereksinim 4.3**
        """
        # Ajan-modül eşleştirmesi
        ajan_modul_eslestirmesi = {
            "stok_ajani": "stok",
            "pos_ajani": "pos", 
            "crm_ajani": "crm",
            "satis_belge_ajani": "satis_belgeleri",
            "eticaret_ajani": "eticaret",
            "ebelge_ajani": "ebelge",
            "kargo_ajani": "kargo",
            "rapor_ajani": "raporlar"
        }
        
        moduller_klasoru = "sontechsp/uygulama/moduller"
        assert os.path.exists(moduller_klasoru), "Modüller klasörü mevcut değil"
        
        for ajan, modul in ajan_modul_eslestirmesi.items():
            modul_yolu = os.path.join(moduller_klasoru, modul)
            assert os.path.exists(modul_yolu), f"{ajan} için modül klasörü mevcut değil: {modul}"
            assert os.path.isdir(modul_yolu), f"{ajan} için modül yolu bir klasör değil: {modul}"
    
    def test_modul_katman_uyumlulugu(self):
        """
        Modüllerin katmanlı mimari yapısına uyumlu olduğunu kontrol eder
        """
        moduller = ["stok", "pos", "crm", "satis_belgeleri", "eticaret", "ebelge", "kargo", "raporlar"]
        
        for modul in moduller:
            modul_yolu = f"sontechsp/uygulama/moduller/{modul}"
            
            # Modül klasörünün var olduğunu kontrol et
            assert os.path.exists(modul_yolu), f"Modül klasörü mevcut değil: {modul}"
            assert os.path.isdir(modul_yolu), f"Modül yolu bir klasör değil: {modul}"
            
            # Modülün __init__.py dosyasına sahip olduğunu kontrol et
            init_yolu = os.path.join(modul_yolu, "__init__.py")
            assert os.path.exists(init_yolu), f"Modül __init__.py dosyası mevcut değil: {modul}"
            
            # __init__.py dosyasının içeriğini kontrol et
            with open(init_yolu, 'r', encoding='utf-8') as f:
                icerik = f.read()
                assert "Version:" in icerik, f"Modül __init__.py dosyası standart başlık içermiyor: {modul}"
                assert "Module:" in icerik, f"Modül __init__.py dosyası modül bilgisi içermiyor: {modul}"
    
    def test_turkce_ascii_isimlendirme(self):
        """
        Modül isimlerinin Türkçe ASCII isimlendirme kurallarına uyduğunu kontrol eder
        """
        moduller = ["stok", "pos", "crm", "satis_belgeleri", "eticaret", "ebelge", "kargo", "raporlar"]
        
        for modul in moduller:
            # ASCII karakter kontrolü (Türkçe karakter yok)
            assert modul.isascii(), f"Modül adı ASCII karakter içermiyor: {modul}"
            
            # Küçük harf kontrolü
            assert modul.islower(), f"Modül adı küçük harf değil: {modul}"
            
            # Alt çizgi kullanımı kontrolü (satis_belgeleri gibi)
            gecerli_karakterler = set("abcdefghijklmnopqrstuvwxyz_")
            modul_karakterleri = set(modul)
            assert modul_karakterleri.issubset(gecerli_karakterler), f"Modül adı geçersiz karakter içeriyor: {modul}"
    
    @given(st.sampled_from([
        ("stok", "stok_ajani"),
        ("pos", "pos_ajani"),
        ("crm", "crm_ajani"), 
        ("satis_belgeleri", "satis_belge_ajani"),
        ("eticaret", "eticaret_ajani"),
        ("ebelge", "ebelge_ajani"),
        ("kargo", "kargo_ajani"),
        ("raporlar", "rapor_ajani")
    ]))
    def test_ajan_modul_tutarliligi_property(self, modul_ajan_bilgisi):
        """
        Property test: Herhangi bir ajan-modül çifti için tutarlılık
        """
        modul_adi, ajan_adi = modul_ajan_bilgisi
        modul_yolu = f"sontechsp/uygulama/moduller/{modul_adi}"
        
        # Modülün var olduğunu kontrol et
        assert os.path.exists(modul_yolu), f"{ajan_adi} için modül klasörü mevcut değil: {modul_adi}"
        assert os.path.isdir(modul_yolu), f"{ajan_adi} için modül yolu bir klasör değil: {modul_adi}"
        
        # __init__.py dosyasının var olduğunu kontrol et
        init_yolu = os.path.join(modul_yolu, "__init__.py")
        assert os.path.exists(init_yolu), f"{ajan_adi} için __init__.py dosyası mevcut değil"
        assert os.path.isfile(init_yolu), f"{ajan_adi} için __init__.py yolu bir dosya değil"
        
        # Modül adının Türkçe ASCII kurallarına uyduğunu kontrol et
        assert modul_adi.isascii(), f"{ajan_adi} modül adı ASCII karakter içermiyor: {modul_adi}"
        assert modul_adi.islower(), f"{ajan_adi} modül adı küçük harf değil: {modul_adi}"
    
    @given(st.sampled_from([
        "stok", "pos", "crm", "satis_belgeleri",
        "eticaret", "ebelge", "kargo", "raporlar"
    ]))
    def test_yeni_modul_ekleme_uyumlulugu_property(self, mevcut_modul):
        """
        Property test: Mevcut modüllerin yeni modül ekleme kurallarına uygunluğu
        """
        modul_yolu = f"sontechsp/uygulama/moduller/{mevcut_modul}"
        
        # Modülün katmanlı mimari yapısına uygun olduğunu kontrol et
        assert os.path.exists(modul_yolu), f"Modül klasörü mevcut değil: {mevcut_modul}"
        
        # Modülün üst klasörünün moduller olduğunu kontrol et
        ust_klasor = os.path.dirname(modul_yolu)
        assert ust_klasor.endswith("moduller"), f"Modül yanlış konumda: {mevcut_modul}"
        
        # Modülün katmanlı mimariyi bozmadığını kontrol et (moduller klasörü altında)
        moduller_klasoru = "sontechsp/uygulama/moduller"
        assert modul_yolu.startswith(moduller_klasoru), f"Modül katmanlı mimariyi bozuyor: {mevcut_modul}"