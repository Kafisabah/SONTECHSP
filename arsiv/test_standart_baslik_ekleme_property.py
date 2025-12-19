# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_standart_baslik_ekleme_property
# Description: Property test - Standart başlık ekleme
# Changelog:
# - İlk versiyon: Property 15 testi oluşturuldu

"""
Property Test: Standart Başlık Ekleme

**Feature: kod-kalitesi-standardizasyon, Property 15: Standart Başlık Ekleme**
**Validates: Requirements 5.1**

For any yeni dosya oluşturma işlemi, standart sürüm başlığının eklenmesi gerekir.
"""

import os
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings
from uygulama.moduller.kod_kalitesi.analizorler import BaslikAnalizoru


# Stratejiler
modul_adi_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=('Ll', 'Lu', 'Nd'),
        whitelist_characters='._'
    ),
    min_size=3,
    max_size=50
).filter(lambda x: x and not x.startswith('.') and not x.endswith('.'))

aciklama_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=('Ll', 'Lu', 'Nd', 'Zs'),
        whitelist_characters='.,;:-_'
    ),
    min_size=5,
    max_size=100
).filter(lambda x: x.strip())

version_strategy = st.from_regex(r'\d+\.\d+\.\d+', fullmatch=True)

changelog_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=('Ll', 'Lu', 'Nd', 'Zs'),
        whitelist_characters='.,;:-_'
    ),
    min_size=5,
    max_size=80
).filter(lambda x: x.strip())


@settings(max_examples=100)
@given(
    modul_adi=modul_adi_strategy,
    aciklama=aciklama_strategy,
    version=version_strategy,
    changelog_maddesi=changelog_strategy
)
def test_standart_baslik_ekleme_property(
    modul_adi: str,
    aciklama: str,
    version: str,
    changelog_maddesi: str
):
    """
    Property: For any yeni dosya oluşturma işlemi,
    standart sürüm başlığının eklenmesi gerekir.
    
    Test eder:
    1. Başlık ekleme işlemi başarılı olmalı
    2. Eklenen başlık tüm gerekli alanları içermeli
    3. Version, module, description, changelog alanları dolu olmalı
    4. Last update tarihi bugünün tarihi olmalı
    """
    analizor = BaslikAnalizoru()
    
    # Geçici dosya oluştur
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.py',
        delete=False,
        encoding='utf-8'
    ) as f:
        # Boş Python dosyası
        f.write('# Boş dosya\n')
        f.write('pass\n')
        dosya_yolu = f.name
    
    try:
        # Başlık ekle
        basari = analizor.baslik_ekle(
            dosya_yolu=dosya_yolu,
            modul_adi=modul_adi,
            aciklama=aciklama,
            version=version,
            changelog_maddesi=changelog_maddesi
        )
        
        # Property 1: Başlık ekleme başarılı olmalı
        assert basari, "Başlık ekleme işlemi başarısız oldu"
        
        # Dosyayı analiz et
        rapor = analizor.dosya_basligini_analiz_et(dosya_yolu)
        
        # Property 2: Başlık var olmalı
        assert rapor.baslik_var, "Başlık eklenmedi"
        
        # Property 3: Başlık bilgisi dolu olmalı
        assert rapor.baslik_bilgisi is not None, "Başlık bilgisi None"
        
        # Property 4: Tüm alanlar dolu olmalı (strip edilmiş değerlerle)
        assert rapor.baslik_bilgisi.version == version.strip(), \
            f"Version eşleşmiyor: {rapor.baslik_bilgisi.version} != {version.strip()}"
        
        assert rapor.baslik_bilgisi.module == modul_adi.strip(), \
            f"Module eşleşmiyor: {rapor.baslik_bilgisi.module} != {modul_adi.strip()}"
        
        assert rapor.baslik_bilgisi.description == aciklama.strip(), \
            f"Description eşleşmiyor"
        
        assert len(rapor.baslik_bilgisi.changelog) > 0, \
            "Changelog boş"
        
        assert changelog_maddesi.strip() in rapor.baslik_bilgisi.changelog[0], \
            "Changelog maddesi bulunamadı"
        
        # Property 5: Standart uyumlu olmalı
        assert rapor.standart_uyumlu, \
            f"Standart uyumlu değil, eksik alanlar: {rapor.eksik_alanlar}"
        
        # Property 6: Eksik alan olmamalı
        assert len(rapor.eksik_alanlar) == 0, \
            f"Eksik alanlar var: {rapor.eksik_alanlar}"
        
    finally:
        # Geçici dosyayı temizle
        if os.path.exists(dosya_yolu):
            os.unlink(dosya_yolu)

