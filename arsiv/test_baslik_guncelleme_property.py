# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_baslik_guncelleme_property
# Description: Property testler - Changelog ve tarih güncelleme
# Changelog:
# - İlk versiyon: Property 17 ve 18 testleri

"""
Property Tests: Başlık Güncelleme

**Feature: kod-kalitesi-standardizasyon, Property 17: Changelog Güncelleme**
**Feature: kod-kalitesi-standardizasyon, Property 18: Tarih Güncelleme**
**Validates: Requirements 5.3, 5.4**
"""

import os
import tempfile
from datetime import datetime
from hypothesis import given, strategies as st, settings
from uygulama.moduller.kod_kalitesi.analizorler import BaslikAnalizoru


changelog_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd', 'Zs')),
    min_size=5,
    max_size=80
).filter(lambda x: x.strip() and '\n' not in x)


@settings(max_examples=100, deadline=None)
@given(yeni_madde=changelog_strategy)
def test_changelog_guncelleme_property(yeni_madde: str):
    """Property 17: Changelog güncelleme"""
    analizor = BaslikAnalizoru()
    
    baslik = """# Version: 0.1.0
# Last Update: 2025-01-01
# Module: test
# Description: Test
# Changelog:
# - İlk versiyon

pass
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(baslik)
        dosya_yolu = f.name
    
    try:
        basari = analizor.baslik_guncelle(dosya_yolu, yeni_changelog_maddesi=yeni_madde)
        assert basari, "Güncelleme başarısız"
        
        rapor = analizor.dosya_basligini_analiz_et(dosya_yolu)
        assert len(rapor.baslik_bilgisi.changelog) == 2, "Changelog eklenmedi"
        assert yeni_madde.strip() in rapor.baslik_bilgisi.changelog[1], "Yeni madde bulunamadı"
    finally:
        if os.path.exists(dosya_yolu):
            os.unlink(dosya_yolu)


@settings(max_examples=100)
@given(st.just(None))
def test_tarih_guncelleme_property(_):
    """Property 18: Tarih güncelleme"""
    analizor = BaslikAnalizoru()
    
    baslik = """# Version: 0.1.0
# Last Update: 2020-01-01
# Module: test
# Description: Test
# Changelog:
# - İlk versiyon

pass
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(baslik)
        dosya_yolu = f.name
    
    try:
        basari = analizor.baslik_guncelle(dosya_yolu, yeni_changelog_maddesi="Güncelleme")
        assert basari, "Güncelleme başarısız"
        
        rapor = analizor.dosya_basligini_analiz_et(dosya_yolu)
        bugun = datetime.now().strftime('%Y-%m-%d')
        assert rapor.baslik_bilgisi.last_update == bugun, "Tarih güncellenmedi"
    finally:
        if os.path.exists(dosya_yolu):
            os.unlink(dosya_yolu)

