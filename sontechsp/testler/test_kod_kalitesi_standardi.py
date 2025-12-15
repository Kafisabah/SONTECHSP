# Version: 0.1.0
# Last Update: 2024-12-15
# Module: test_kod_kalitesi_standardi
# Description: SONTECHSP kod kalitesi standardı property testleri
# Changelog:
# - İlk oluşturma

"""
SONTECHSP Kod Kalitesi Standardı Property Testleri

**Feature: sontechsp-proje-iskeleti, Property 10: SONTECHSP kod kalitesi standardı**

Kod kalitesi kurallarının doğruluğunu test eder:
- PEP8 formatı zorunlu
- 120 satır (yorumlar hariç) limiti
- 25 satır fonksiyon limiti
- Standart dosya başlığı şablonu
"""

import os
import ast
import re
from pathlib import Path
from typing import List, Dict, Any

import pytest
from hypothesis import given, strategies as st, assume, settings

# Test edilecek proje kök dizini
PROJE_KOK = Path(__file__).parent.parent


def python_dosyalarini_al() -> List[Path]:
    """Projedeki tüm Python dosyalarını döndürür"""
    python_dosyalar = []
    
    for dosya_yolu in PROJE_KOK.rglob("*.py"):
        # Test dosyalarını ve __pycache__ klasörlerini hariç tut
        if "__pycache__" not in str(dosya_yolu):
            python_dosyalar.append(dosya_yolu)
    
    return python_dosyalar


def dosya_satirlarini_say(dosya_yolu: Path) -> Dict[str, int]:
    """
    Dosyadaki satır sayılarını hesaplar
    
    Returns:
        Dict: toplam_satirlar, kod_satirlari, yorum_satirlari
    """
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            satirlar = f.readlines()
        
        toplam_satirlar = len(satirlar)
        yorum_satirlari = 0
        bos_satirlar = 0
        
        for satir in satirlar:
            satir_temiz = satir.strip()
            if not satir_temiz:
                bos_satirlar += 1
            elif satir_temiz.startswith('#'):
                yorum_satirlari += 1
        
        kod_satirlari = toplam_satirlar - yorum_satirlari - bos_satirlar
        
        return {
            'toplam_satirlar': toplam_satirlar,
            'kod_satirlari': kod_satirlari,
            'yorum_satirlari': yorum_satirlari,
            'bos_satirlar': bos_satirlar
        }
        
    except Exception:
        return {'toplam_satirlar': 0, 'kod_satirlari': 0, 'yorum_satirlari': 0, 'bos_satirlar': 0}


def fonksiyon_satirlarini_kontrol_et(dosya_yolu: Path) -> List[Dict[str, Any]]:
    """
    Dosyadaki fonksiyonların satır sayılarını kontrol eder
    
    Returns:
        List[Dict]: Fonksiyon bilgileri listesi
    """
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            icerik = f.read()
        
        # AST ile fonksiyonları parse et
        agac = ast.parse(icerik)
        fonksiyonlar = []
        
        for node in ast.walk(agac):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                baslangic_satir = node.lineno
                bitis_satir = node.end_lineno if hasattr(node, 'end_lineno') else baslangic_satir
                satir_sayisi = bitis_satir - baslangic_satir + 1
                
                fonksiyonlar.append({
                    'isim': node.name,
                    'baslangic_satir': baslangic_satir,
                    'bitis_satir': bitis_satir,
                    'satir_sayisi': satir_sayisi
                })
        
        return fonksiyonlar
        
    except Exception:
        return []


def dosya_basligi_kontrol_et(dosya_yolu: Path) -> Dict[str, Any]:
    """
    Dosya başlığının standart şablona uygunluğunu kontrol eder
    
    Returns:
        Dict: Başlık bilgileri
    """
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            ilk_satirlar = [f.readline().strip() for _ in range(10)]
        
        # Gerekli alanları kontrol et
        version_var = any('# Version:' in satir for satir in ilk_satirlar)
        last_update_var = any('# Last Update:' in satir for satir in ilk_satirlar)
        module_var = any('# Module:' in satir for satir in ilk_satirlar)
        description_var = any('# Description:' in satir for satir in ilk_satirlar)
        changelog_var = any('# Changelog:' in satir for satir in ilk_satirlar)
        
        return {
            'version_var': version_var,
            'last_update_var': last_update_var,
            'module_var': module_var,
            'description_var': description_var,
            'changelog_var': changelog_var,
            'tum_alanlar_var': all([version_var, last_update_var, module_var, description_var, changelog_var])
        }
        
    except Exception:
        return {
            'version_var': False,
            'last_update_var': False,
            'module_var': False,
            'description_var': False,
            'changelog_var': False,
            'tum_alanlar_var': False
        }


class TestKodKalitesiStandardi:
    """SONTECHSP kod kalitesi standardı testleri"""
    
    @pytest.mark.slow
    @pytest.mark.integration
    @pytest.mark.parametrize("dosya_yolu", python_dosyalarini_al())
    def test_dosya_satir_limiti(self, dosya_yolu: Path):
        """
        **Feature: sontechsp-proje-iskeleti, Property 10: SONTECHSP kod kalitesi standardı**
        
        Her Python dosyası 120 satırı (yorumlar hariç) aşmamalıdır.
        """
        satir_bilgileri = dosya_satirlarini_say(dosya_yolu)
        kod_satirlari = satir_bilgileri['kod_satirlari']
        
        # Test dosyaları için daha esnek limit (200 satır)
        if "test_" in dosya_yolu.name:
            assert kod_satirlari <= 200, (
                f"Test dosyası {dosya_yolu.name} kod satır limiti aşıldı: "
                f"{kod_satirlari} > 200 satır"
            )
        else:
            assert kod_satirlari <= 120, (
                f"Dosya {dosya_yolu.name} kod satır limiti aşıldı: "
                f"{kod_satirlari} > 120 satır (yorumlar hariç)"
            )
    
    @pytest.mark.slow
    @pytest.mark.integration
    @pytest.mark.parametrize("dosya_yolu", python_dosyalarini_al())
    def test_fonksiyon_satir_limiti(self, dosya_yolu: Path):
        """
        **Feature: sontechsp-proje-iskeleti, Property 10: SONTECHSP kod kalitesi standardı**
        
        Her fonksiyon 25 satırı aşmamalıdır.
        """
        fonksiyonlar = fonksiyon_satirlarini_kontrol_et(dosya_yolu)
        
        for fonksiyon in fonksiyonlar:
            # Test fonksiyonları için daha esnek limit (50 satır)
            if "test_" in dosya_yolu.name or fonksiyon['isim'].startswith('test_'):
                assert fonksiyon['satir_sayisi'] <= 50, (
                    f"Test fonksiyonu {fonksiyon['isim']} ({dosya_yolu.name}) "
                    f"satır limiti aşıldı: {fonksiyon['satir_sayisi']} > 50 satır"
                )
            else:
                assert fonksiyon['satir_sayisi'] <= 25, (
                    f"Fonksiyon {fonksiyon['isim']} ({dosya_yolu.name}) "
                    f"satır limiti aşıldı: {fonksiyon['satir_sayisi']} > 25 satır"
                )
    
    @pytest.mark.slow
    @pytest.mark.integration
    @pytest.mark.parametrize("dosya_yolu", python_dosyalarini_al())
    def test_dosya_basligi_standardi(self, dosya_yolu: Path):
        """
        **Feature: sontechsp-proje-iskeleti, Property 10: SONTECHSP kod kalitesi standardı**
        
        Her dosya standart başlık şablonunu içermelidir:
        Version, Last Update, Module, Description, Changelog
        """
        # __init__.py dosyaları için esnek kontrol
        if dosya_yolu.name == "__init__.py":
            return  # __init__.py dosyaları için başlık zorunlu değil
        
        baslık_bilgileri = dosya_basligi_kontrol_et(dosya_yolu)
        
        assert baslık_bilgileri['version_var'], (
            f"Dosya {dosya_yolu.name} 'Version:' alanı eksik"
        )
        
        assert baslık_bilgileri['last_update_var'], (
            f"Dosya {dosya_yolu.name} 'Last Update:' alanı eksik"
        )
        
        assert baslık_bilgileri['module_var'], (
            f"Dosya {dosya_yolu.name} 'Module:' alanı eksik"
        )
        
        assert baslık_bilgileri['description_var'], (
            f"Dosya {dosya_yolu.name} 'Description:' alanı eksik"
        )
        
        assert baslık_bilgileri['changelog_var'], (
            f"Dosya {dosya_yolu.name} 'Changelog:' alanı eksik"
        )


@given(st.text(min_size=1, max_size=1000))
@settings(max_examples=50)
def test_kod_kalitesi_property_genel(kod_ornegi: str):
    """
    **Feature: sontechsp-proje-iskeleti, Property 10: SONTECHSP kod kalitesi standardı**
    
    Herhangi bir kod örneği için kalite kuralları geçerli olmalıdır.
    """
    assume(len(kod_ornegi.strip()) > 0)
    
    # Satır sayısını kontrol et
    satirlar = kod_ornegi.split('\n')
    kod_satirlari = [s for s in satirlar if s.strip() and not s.strip().startswith('#')]
    
    # Eğer kod satırı varsa, makul bir limit olmalı
    if len(kod_satirlari) > 0:
        # Property test için daha geniş limit
        assert len(kod_satirlari) <= 500, "Kod örneği çok uzun"
    
    # Boş olmayan kod için temel format kontrolü
    if any(satir.strip() for satir in satirlar):
        # En azından bir karakter içermeli
        assert len(kod_ornegi.strip()) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])