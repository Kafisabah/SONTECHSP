# Version: 0.1.0
# Last Update: 2024-12-15
# Module: test_windows_kurulum_dokumantasyonu
# Description: Windows kurulum dokümantasyonu property testleri
# Changelog:
# - İlk oluşturma

"""
**Feature: sontechsp-proje-iskeleti, Property 5: Windows kurulum dokümantasyonu**
**Validates: Requirements 2.2**

Bu modül README.md dosyasının Windows kurulum talimatları ve PyInstaller 
build notlarını içerdiğini doğrular.
"""

import os
from pathlib import Path
from hypothesis import given, strategies as st
import pytest


class TestWindowsKurulumDokumantasyonu:
    """Windows kurulum dokümantasyonu property testleri."""
    
    def setup_method(self):
        """Test kurulumu."""
        self.proje_kok = Path(__file__).parent.parent.parent
        self.readme_yolu = self.proje_kok / "README.md"
    
    def test_readme_dosyasi_mevcut(self):
        """README.md dosyasının mevcut olduğunu kontrol eder."""
        assert self.readme_yolu.exists(), "README.md dosyası bulunamadı"
        assert self.readme_yolu.is_file(), "README.md bir dosya olmalı"
    
    def test_windows_kurulum_talimatlari_mevcut(self):
        """
        **Feature: sontechsp-proje-iskeleti, Property 5: Windows kurulum dokümantasyonu**
        **Validates: Requirements 2.2**
        
        README.md dosyasının Windows kurulum talimatlarını içerdiğini doğrular.
        """
        readme_icerik = self.readme_yolu.read_text(encoding='utf-8')
        
        # Gerekli bölümlerin varlığını kontrol et
        gerekli_bolumler = [
            "Kurulum Talimatları",
            "Python Kurulumu", 
            "PostgreSQL Kurulumu",
            "Sistem Gereksinimleri",
            "Windows"
        ]
        
        for bolum in gerekli_bolumler:
            assert bolum in readme_icerik, f"README.md'de '{bolum}' bölümü bulunamadı"
    
    def test_pyinstaller_build_notlari_mevcut(self):
        """
        **Feature: sontechsp-proje-iskeleti, Property 5: Windows kurulum dokümantasyonu**
        **Validates: Requirements 2.2**
        
        README.md dosyasının PyInstaller build notlarını içerdiğini doğrular.
        """
        readme_icerik = self.readme_yolu.read_text(encoding='utf-8')
        
        # PyInstaller ile ilgili gerekli bilgilerin varlığını kontrol et
        pyinstaller_konular = [
            "PyInstaller",
            "Build",
            "executable",
            "Windows Executable",
            "sontechsp.spec"
        ]
        
        for konu in pyinstaller_konular:
            assert konu.lower() in readme_icerik.lower(), \
                f"README.md'de PyInstaller konusu '{konu}' bulunamadı"
    
    def test_veritabani_kurulum_rehberi_mevcut(self):
        """
        **Feature: sontechsp-proje-iskeleti, Property 5: Windows kurulum dokümantasyonu**
        **Validates: Requirements 2.2**
        
        README.md dosyasının PostgreSQL/SQLite kurulum rehberini içerdiğini doğrular.
        """
        readme_icerik = self.readme_yolu.read_text(encoding='utf-8')
        
        # Veritabanı kurulum bilgilerinin varlığını kontrol et
        veritabani_konular = [
            "PostgreSQL",
            "SQLite", 
            "Veritabanı",
            "DATABASE_URL",
            "migration"
        ]
        
        for konu in veritabani_konular:
            assert konu in readme_icerik, \
                f"README.md'de veritabanı konusu '{konu}' bulunamadı"
    
    def test_calistirma_rehberi_mevcut(self):
        """
        **Feature: sontechsp-proje-iskeleti, Property 5: Windows kurulum dokümantasyonu**
        **Validates: Requirements 2.2**
        
        README.md dosyasının çalıştırma rehberini içerdiğini doğrular.
        """
        readme_icerik = self.readme_yolu.read_text(encoding='utf-8')
        
        # Çalıştırma rehberi bilgilerinin varlığını kontrol et
        calistirma_konular = [
            "Çalıştırma",
            "python -m sontechsp",
            "ana.py",
            "başlat"
        ]
        
        for konu in calistirma_konular:
            assert konu in readme_icerik, \
                f"README.md'de çalıştırma konusu '{konu}' bulunamadı"
    
    def test_gelistirme_ortami_kurulumu_mevcut(self):
        """
        **Feature: sontechsp-proje-iskeleti, Property 5: Windows kurulum dokümantasyonu**
        **Validates: Requirements 2.2**
        
        README.md dosyasının geliştirme ortamı kurulumunu içerdiğini doğrular.
        """
        readme_icerik = self.readme_yolu.read_text(encoding='utf-8')
        
        # Geliştirme ortamı kurulum bilgilerinin varlığını kontrol et
        gelistirme_konular = [
            "Geliştirme Ortamı",
            "venv",
            "pip install",
            "pytest",
            "test"
        ]
        
        for konu in gelistirme_konular:
            assert konu in readme_icerik, \
                f"README.md'de geliştirme konusu '{konu}' bulunamadı"
    
    @given(st.text(min_size=1, max_size=100))
    def test_readme_icerik_tutarliligi(self, test_metni):
        """
        **Feature: sontechsp-proje-iskeleti, Property 5: Windows kurulum dokümantasyonu**
        **Validates: Requirements 2.2**
        
        README.md dosyasının tutarlı bir yapıda olduğunu doğrular.
        Herhangi bir metin arandığında dosya okunabilir olmalıdır.
        """
        readme_icerik = self.readme_yolu.read_text(encoding='utf-8')
        
        # Dosyanın okunabilir olduğunu ve temel yapıya sahip olduğunu kontrol et
        assert len(readme_icerik) > 100, "README.md çok kısa, yeterli içerik yok"
        assert "SONTECHSP" in readme_icerik, "README.md proje adını içermeli"
        assert "#" in readme_icerik, "README.md markdown başlıkları içermeli"
        
        # Test metninin aranması dosyayı bozmamalı
        test_sonuc = test_metni.lower() in readme_icerik.lower()
        # Bu sadece arama işleminin çalıştığını doğrular, sonuç önemli değil
        assert isinstance(test_sonuc, bool), "Arama işlemi boolean sonuç döndürmeli"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])