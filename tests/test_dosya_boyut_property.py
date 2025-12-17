# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_dosya_boyut_property
# Description: Dosya boyut analizörü property-based testleri
# Changelog:
# - İlk versiyon: Property testleri oluşturuldu

"""
**Feature: kod-kalitesi-standardizasyon, Property 1: Dosya Boyut Tespiti Doğruluğu**

For any Python dosyası ve satır sayısı, dosya boyut analizörü 
120 satırı aşan dosyaları doğru tespit etmelidir.

**Validates: Requirements 1.1**
"""

import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings

from uygulama.moduller.kod_kalitesi.analizorler.dosya_boyut_analizoru import (
    DosyaBoyutAnalizoru
)


@given(
    satir_sayisi=st.integers(min_value=1, max_value=300),
    yorum_orani=st.floats(min_value=0.0, max_value=0.5)
)
@settings(max_examples=100, deadline=None)
def test_dosya_boyut_tespiti_dogruluğu(satir_sayisi, yorum_orani):
    """
    Property: Dosya boyut analizörü 120 satırı aşan dosyaları doğru tespit eder.
    
    Test stratejisi:
    - Rastgele satır sayısı ile dosya oluştur
    - Yorum satırları ekle
    - Analizörün doğru tespit ettiğini kontrol et
    """
    analizor = DosyaBoyutAnalizoru(satir_limiti=120)
    
    # Rastgele Python kodu oluştur
    yorum_sayisi = int(satir_sayisi * yorum_orani)
    kod_sayisi = satir_sayisi - yorum_sayisi
    
    satirlar = []
    for i in range(kod_sayisi):
        satirlar.append(f"x{i} = {i}")
    
    for i in range(yorum_sayisi):
        satirlar.append(f"# Yorum satırı {i}")
    
    icerik = '\n'.join(satirlar)
    
    # Geçici dosya oluştur
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.py', delete=False, encoding='utf-8'
    ) as f:
        f.write(icerik)
        dosya_yolu = f.name
    
    try:
        # Satır sayısını hesapla
        hesaplanan = analizor.satir_sayisi_hesapla(dosya_yolu)
        
        # Property: Hesaplanan satır sayısı kod satırlarına eşit olmalı
        assert hesaplanan == kod_sayisi, \
            f"Beklenen: {kod_sayisi}, Hesaplanan: {hesaplanan}"
        
        # Property: 120'den büyükse tespit edilmeli
        with tempfile.TemporaryDirectory() as tmpdir:
            hedef = Path(tmpdir) / "test.py"
            hedef.write_text(icerik, encoding='utf-8')
            
            raporlar = analizor.buyuk_dosyalari_tespit_et(tmpdir)
            
            if kod_sayisi > 120:
                assert len(raporlar) == 1, \
                    f"120+ satırlı dosya tespit edilmedi: {kod_sayisi}"
                assert raporlar[0].satir_sayisi == kod_sayisi
            else:
                assert len(raporlar) == 0, \
                    f"120- satırlı dosya yanlış tespit edildi: {kod_sayisi}"
    
    finally:
        Path(dosya_yolu).unlink(missing_ok=True)
