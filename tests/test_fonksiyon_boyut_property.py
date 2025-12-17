# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_fonksiyon_boyut_property
# Description: Fonksiyon boyut analizörü property-based testleri
# Changelog:
# - İlk versiyon: Property testleri oluşturuldu

"""
**Feature: kod-kalitesi-standardizasyon, Property 5: Fonksiyon Boyut Tespiti Doğruluğu**

For any Python fonksiyonu, fonksiyon boyut analizörü 
25 satırı aşan fonksiyonları doğru tespit etmelidir.

**Validates: Requirements 2.1**
"""

import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings

from uygulama.moduller.kod_kalitesi.analizorler.fonksiyon_boyut_analizoru import (
    FonksiyonBoyutAnalizoru
)


@given(
    fonksiyon_satir_sayisi=st.integers(min_value=1, max_value=100),
    yorum_orani=st.floats(min_value=0.0, max_value=0.4)
)
@settings(max_examples=100, deadline=None)
def test_fonksiyon_boyut_tespiti_dogruluğu(fonksiyon_satir_sayisi, yorum_orani):
    """
    Property: Fonksiyon boyut analizörü 25 satırı aşan fonksiyonları doğru tespit eder.
    
    Test stratejisi:
    - Rastgele satır sayısı ile fonksiyon oluştur
    - Yorum satırları ekle
    - Analizörün doğru tespit ettiğini kontrol et
    """
    analizor = FonksiyonBoyutAnalizoru(satir_limiti=25)
    
    # Rastgele fonksiyon kodu oluştur
    yorum_sayisi = int(fonksiyon_satir_sayisi * yorum_orani)
    kod_sayisi = fonksiyon_satir_sayisi - yorum_sayisi
    
    satirlar = ["def test_fonksiyon():"]
    
    for i in range(kod_sayisi):
        satirlar.append(f"    x{i} = {i}")
    
    for i in range(yorum_sayisi):
        satirlar.append(f"    # Yorum satırı {i}")
    
    icerik = '\n'.join(satirlar)
    
    # Geçici dosya oluştur
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.py', delete=False, encoding='utf-8'
    ) as f:
        f.write(icerik)
        dosya_yolu = f.name
    
    try:
        # Fonksiyonları analiz et
        raporlar = analizor.buyuk_fonksiyonlari_tespit_et(dosya_yolu)
        
        # Property: 25'ten büyükse tespit edilmeli
        # +1 çünkü def satırı da sayılıyor
        gercek_satir = kod_sayisi + 1
        
        if gercek_satir > 25:
            assert len(raporlar) == 1, \
                f"25+ satırlı fonksiyon tespit edilmedi: {gercek_satir}"
            assert raporlar[0].fonksiyon_adi == "test_fonksiyon"
            assert raporlar[0].satir_sayisi == gercek_satir
        else:
            assert len(raporlar) == 0, \
                f"25- satırlı fonksiyon yanlış tespit edildi: {gercek_satir}"
    
    finally:
        Path(dosya_yolu).unlink(missing_ok=True)
