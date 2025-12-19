# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_otomatik_mimari_ihlal_tespiti_property
# Description: Property test - Otomatik mimari ihlal tespiti
# Changelog:
# - İlk versiyon: Property 30 testi oluşturuldu

"""
**Feature: kod-kalitesi-standardizasyon, Property 30: Otomatik Mimari İhlal Tespiti**
**Validates: Requirements 8.3**

Property: For any import kontrol işlemi, mimari ihlallerin
otomatik tespit edilmesi gerekir
"""

import tempfile
from pathlib import Path

from hypothesis import given, settings, strategies as st

from uygulama.moduller.kod_kalitesi.otomatik_kontrol_sistemi import (
    OtomatikKontrolSistemi,
)


@st.composite
def mimari_ihlal_senaryosu(draw):
    """Rastgele mimari ihlal senaryosu üretir"""
    # UI katmanından yasak importlar
    ui_repository_import = draw(st.booleans())
    ui_database_import = draw(st.booleans())
    
    # Servis katmanından yasak importlar
    servis_ui_import = draw(st.booleans())
    
    return {
        'ui_repository_import': ui_repository_import,
        'ui_database_import': ui_database_import,
        'servis_ui_import': servis_ui_import
    }


@given(mimari_ihlal_senaryosu())
@settings(max_examples=100, deadline=None)
def test_otomatik_mimari_ihlal_tespiti_property(senaryo):
    """
    Property: Otomatik kontrol sistemi çalıştırıldığında,
    mimari ihlaller otomatik tespit edilmelidir.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        proje = Path(temp_dir)
        
        # Katman klasörleri oluştur
        ui_klasor = proje / "arayuz"
        ui_klasor.mkdir()
        
        servis_klasor = proje / "servisler"
        servis_klasor.mkdir()
        
        depo_klasor = proje / "depolar"
        depo_klasor.mkdir()
        
        db_klasor = proje / "veritabani"
        db_klasor.mkdir()
        
        # UI dosyası oluştur
        ui_dosya = ui_klasor / "test_ekran.py"
        ui_satirlar = []
        
        if senaryo['ui_repository_import']:
            ui_satirlar.append("from depolar.test_depo import TestDepo")
        
        if senaryo['ui_database_import']:
            ui_satirlar.append("from veritabani.modeller import TestModel")
        
        ui_satirlar.append("\nclass TestEkran:\n    pass")
        ui_dosya.write_text('\n'.join(ui_satirlar), encoding='utf-8')
        
        # Servis dosyası oluştur
        servis_dosya = servis_klasor / "test_servis.py"
        servis_satirlar = []
        
        if senaryo['servis_ui_import']:
            servis_satirlar.append("from arayuz.test_ekran import TestEkran")
        
        servis_satirlar.append("\nclass TestServis:\n    pass")
        servis_dosya.write_text('\n'.join(servis_satirlar), encoding='utf-8')
        
        # Otomatik kontrol sistemi oluştur
        sistem = OtomatikKontrolSistemi(proje_yolu=str(proje))
        
        # Tam kontrol yap
        rapor = sistem.tam_kontrol_yap()
        
        # Property: Mimari ihlaller otomatik tespit edilmeli
        beklenen_ihlal_var = (
            senaryo['ui_repository_import'] or
            senaryo['ui_database_import'] or
            senaryo['servis_ui_import']
        )
        
        if beklenen_ihlal_var:
            assert len(rapor.mimari_ihlaller) > 0, (
                "Mimari ihlal var ama tespit edilmedi"
            )
        else:
            # İhlal yoksa, raporda da olmamalı
            assert len(rapor.mimari_ihlaller) == 0, (
                f"İhlal yok ama {len(rapor.mimari_ihlaller)} ihlal tespit edildi"
            )


@given(st.integers(min_value=0, max_value=5))
@settings(max_examples=100, deadline=None)
def test_otomatik_mimari_coklu_ihlal_property(ihlal_sayisi):
    """
    Property: Otomatik kontrol sistemi birden fazla mimari
    ihlali aynı anda tespit edebilmelidir.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        proje = Path(temp_dir)
        
        # Katman klasörleri
        ui_klasor = proje / "arayuz"
        ui_klasor.mkdir()
        
        depo_klasor = proje / "depolar"
        depo_klasor.mkdir()
        
        # Her ihlal için ayrı UI dosyası oluştur
        for i in range(ihlal_sayisi):
            ui_dosya = ui_klasor / f"ekran_{i}.py"
            satirlar = [
                f"from depolar.depo_{i} import Depo{i}",
                f"\nclass Ekran{i}:\n    pass"
            ]
            ui_dosya.write_text('\n'.join(satirlar), encoding='utf-8')
        
        # Otomatik kontrol sistemi
        sistem = OtomatikKontrolSistemi(proje_yolu=str(proje))
        
        # Tam kontrol yap
        rapor = sistem.tam_kontrol_yap()
        
        # Property: Tüm ihlaller tespit edilmeli
        if ihlal_sayisi > 0:
            assert len(rapor.mimari_ihlaller) >= ihlal_sayisi, (
                f"Beklenen en az {ihlal_sayisi} ihlal, "
                f"bulunan {len(rapor.mimari_ihlaller)}"
            )


def test_otomatik_mimari_kontrol_raporda():
    """
    Property: Mimari ihlaller raporda yer almalıdır.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        proje = Path(temp_dir)
        
        # UI klasörü
        ui_klasor = proje / "arayuz"
        ui_klasor.mkdir()
        
        # İhlal içeren UI dosyası
        ui_dosya = ui_klasor / "test_ekran.py"
        ui_dosya.write_text(
            "from depolar.test_depo import TestDepo\n\nclass TestEkran:\n    pass",
            encoding='utf-8'
        )
        
        # Otomatik kontrol sistemi
        sistem = OtomatikKontrolSistemi(proje_yolu=str(proje))
        
        # Tam kontrol yap
        rapor = sistem.tam_kontrol_yap()
        
        # Property: Raporda mimari ihlaller bölümü olmalı
        metin_rapor = sistem.rapor_uret(rapor)
        
        assert "MİMARİ İHLALLER" in metin_rapor, (
            "Raporda mimari ihlaller bölümü yok"
        )
        
        # İhlal varsa, detaylar raporda olmalı
        if len(rapor.mimari_ihlaller) > 0:
            assert "test_ekran" in metin_rapor.lower(), (
                "İhlal yapan dosya raporda yok"
            )
