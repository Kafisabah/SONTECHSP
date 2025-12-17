# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_otomatik_rapor_uretimi_property
# Description: Property test - Otomatik rapor üretimi
# Changelog:
# - İlk versiyon: Property 32 testi oluşturuldu

"""
**Feature: kod-kalitesi-standardizasyon, Property 32: Otomatik Rapor Üretimi**
**Validates: Requirements 8.5**

Property: For any otomatik kontrol işlemi tamamlandığında, 
detaylı raporun üretilmesi gerekir
"""

import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings

from uygulama.moduller.kod_kalitesi.otomatik_kontrol_sistemi import (
    OtomatikKontrolSistemi
)


@given(st.booleans())
@settings(max_examples=50, deadline=None)
def test_otomatik_rapor_uretimi_property(ihlal_var):
    """
    Property: Otomatik kontrol sistemi her zaman rapor üretmelidir.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        proje = Path(temp_dir)
        
        # Test dosyası oluştur
        test_dosya = proje / "test.py"
        
        if ihlal_var:
            # İhlal içeren dosya
            test_dosya.write_text("x = " + "a" * 150, encoding='utf-8')
        else:
            # İhlal içermeyen dosya
            test_dosya.write_text("x = 1", encoding='utf-8')
        
        # Otomatik kontrol sistemi
        sistem = OtomatikKontrolSistemi(proje_yolu=str(proje))
        
        # Tam kontrol yap
        rapor = sistem.tam_kontrol_yap()
        
        # Property: Rapor üretilmiş olmalı
        assert rapor is not None, "Rapor üretilmedi"
        
        # Metin raporu üret
        metin_rapor = sistem.rapor_uret(rapor)
        
        # Property: Metin raporu boş olmamalı
        assert metin_rapor, "Metin raporu boş"
        assert "KALİTE KONTROL RAPORU" in metin_rapor, "Rapor başlığı yok"
        
        # Property: Rapor durum bilgisi içermeli
        assert "Durum:" in metin_rapor, "Durum bilgisi yok"
        
        # Property: Rapor ihlal sayısı içermeli
        assert "Toplam İhlal Sayısı:" in metin_rapor, "İhlal sayısı yok"


def test_rapor_ihlal_detaylari_property():
    """
    Property: Rapor ihlal varsa detayları içermelidir.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        proje = Path(temp_dir)
        
        # İhlal içeren dosya
        test_dosya = proje / "test.py"
        test_dosya.write_text("x = " + "a" * 150, encoding='utf-8')
        
        # Otomatik kontrol sistemi
        sistem = OtomatikKontrolSistemi(proje_yolu=str(proje))
        
        # Tam kontrol yap
        rapor = sistem.tam_kontrol_yap()
        
        # Metin raporu üret
        metin_rapor = sistem.rapor_uret(rapor)
        
        # Property: İhlal varsa, raporda görünmeli
        if len(rapor.dosya_boyut_ihlalleri) > 0:
            assert "DOSYA BOYUT İHLALLERİ" in metin_rapor, (
                "Dosya boyut ihlalleri raporda yok"
            )
        
        if len(rapor.pep8_ihlalleri) > 0:
            assert "PEP8 İHLALLERİ" in metin_rapor, (
                "PEP8 ihlalleri raporda yok"
            )


def test_rapor_basarili_durum_property():
    """
    Property: İhlal yoksa rapor başarılı olmalıdır.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        proje = Path(temp_dir)
        
        # İhlal içermeyen dosya
        test_dosya = proje / "test.py"
        test_dosya.write_text("x = 1", encoding='utf-8')
        
        # Otomatik kontrol sistemi
        sistem = OtomatikKontrolSistemi(proje_yolu=str(proje))
        
        # Tam kontrol yap
        rapor = sistem.tam_kontrol_yap()
        
        # Metin raporu üret
        metin_rapor = sistem.rapor_uret(rapor)
        
        # Property: İhlal yoksa başarılı olmalı
        if rapor.toplam_ihlal_sayisi == 0:
            assert "✓ BAŞARILI" in metin_rapor, "Başarılı durumu yok"
        else:
            assert "✗ BAŞARISIZ" in metin_rapor, "Başarısız durumu yok"
