# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_baslik_format_tutarliligi_property
# Description: Property test - Başlık format tutarlılığı
# Changelog:
# - İlk versiyon: Property 19 testi

"""
Property Test: Başlık Format Tutarlılığı

**Feature: kod-kalitesi-standardizasyon, Property 19: Başlık Format Tutarlılığı**
**Validates: Requirements 5.5**

For any başlık standardizasyon işlemi tamamlandığında, tüm dosyalar aynı formata uymalıdır.
"""

import os
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings
from uygulama.moduller.kod_kalitesi.analizorler import BaslikAnalizoru


@settings(max_examples=50, deadline=None)
@given(dosya_sayisi=st.integers(min_value=2, max_value=5))
def test_baslik_format_tutarliligi_property(dosya_sayisi: int):
    """
    Property: For any başlık standardizasyon işlemi,
    tüm dosyalar aynı formata uymalıdır.
    
    Test eder:
    1. Standardizasyon sonrası tüm dosyalar standart uyumlu olmalı
    2. Tüm dosyalar aynı başlık formatına sahip olmalı
    """
    analizor = BaslikAnalizoru()
    
    # Geçici klasör oluştur
    with tempfile.TemporaryDirectory() as temp_dir:
        # Farklı başlık durumlarında dosyalar oluştur
        dosya_yollari = []
        
        for i in range(dosya_sayisi):
            dosya_yolu = os.path.join(temp_dir, f'test_{i}.py')
            
            if i % 3 == 0:
                # Başlıksız dosya
                icerik = "# Kod\npass\n"
            elif i % 3 == 1:
                # Eksik alanlı başlık
                icerik = "# Version: 0.1.0\n# Module: test\npass\n"
            else:
                # Tam başlık
                icerik = """# Version: 0.1.0
# Last Update: 2025-01-01
# Module: test
# Description: Test
# Changelog:
# - İlk versiyon

pass
"""
            
            with open(dosya_yolu, 'w', encoding='utf-8') as f:
                f.write(icerik)
            
            dosya_yollari.append(dosya_yolu)
        
        # Standardizasyon işlemi
        sonuclar = analizor.tum_dosyalari_standardize_et(temp_dir)
        
        # Property 1: Tüm dosyalar işlenmiş olmalı
        assert len(sonuclar) == dosya_sayisi, \
            f"Tüm dosyalar işlenmedi: {len(sonuclar)} != {dosya_sayisi}"
        
        # Property 2: Standardizasyon sonrası tüm dosyalar standart uyumlu olmalı
        raporlar = analizor.klasor_basliklarini_analiz_et(temp_dir)
        
        for rapor in raporlar:
            assert rapor.baslik_var, \
                f"Başlık yok: {rapor.dosya_yolu}"
            
            assert rapor.standart_uyumlu, \
                f"Standart uyumlu değil: {rapor.dosya_yolu}, " \
                f"Eksik alanlar: {rapor.eksik_alanlar}"
        
        # Property 3: Tüm dosyalar aynı alanlara sahip olmalı
        tum_alanlar_dolu = all(
            len(r.eksik_alanlar) == 0 for r in raporlar
        )
        assert tum_alanlar_dolu, "Bazı dosyalarda eksik alanlar var"

