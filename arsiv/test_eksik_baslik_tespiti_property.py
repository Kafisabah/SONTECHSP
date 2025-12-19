# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_eksik_baslik_tespiti_property
# Description: Property test - Eksik başlık tespiti
# Changelog:
# - İlk versiyon: Property 16 testi oluşturuldu

"""
Property Test: Eksik Başlık Tespiti

**Feature: kod-kalitesi-standardizasyon, Property 16: Eksik Başlık Tespiti**
**Validates: Requirements 5.2**

For any dosya başlık kontrol işlemi, eksik başlık bilgilerini doğru tespit etmelidir.
"""

import os
import tempfile
from hypothesis import given, strategies as st, settings
from uygulama.moduller.kod_kalitesi.analizorler import BaslikAnalizoru


# Eksik alan kombinasyonları için strateji
eksik_alan_strategy = st.lists(
    st.sampled_from(['version', 'last_update', 'module', 'description', 'changelog']),
    min_size=1,
    max_size=5,
    unique=True
)


def baslik_olustur_eksik_alanlarla(eksik_alanlar: list) -> str:
    """Belirtilen alanları eksik bırakan başlık oluşturur"""
    satirlar = []
    
    if 'version' not in eksik_alanlar:
        satirlar.append("# Version: 0.1.0")
    
    if 'last_update' not in eksik_alanlar:
        satirlar.append("# Last Update: 2025-12-17")
    
    if 'module' not in eksik_alanlar:
        satirlar.append("# Module: test.module")
    
    if 'description' not in eksik_alanlar:
        satirlar.append("# Description: Test açıklama")
    
    if 'changelog' not in eksik_alanlar:
        satirlar.append("# Changelog:")
        satirlar.append("# - İlk versiyon")
    
    return "\n".join(satirlar) + "\n\n"


@settings(max_examples=100)
@given(eksik_alanlar=eksik_alan_strategy)
def test_eksik_baslik_tespiti_property(eksik_alanlar: list):
    """
    Property: For any dosya başlık kontrol işlemi,
    eksik başlık bilgilerini doğru tespit etmelidir.
    
    Test eder:
    1. Eksik alanlar doğru tespit edilmeli
    2. Rapor eksik alanları içermeli
    3. Standart uyumlu olmamalı (eksik alan varsa)
    """
    # Tüm alanlar eksikse başlık yok demektir, bu durumu atla
    tum_alanlar = {'version', 'last_update', 'module', 'description', 'changelog'}
    if set(eksik_alanlar) == tum_alanlar:
        return
    
    analizor = BaslikAnalizoru()
    
    # Eksik alanlı başlık oluştur
    baslik_icerik = baslik_olustur_eksik_alanlarla(eksik_alanlar)
    
    # Geçici dosya oluştur
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.py',
        delete=False,
        encoding='utf-8'
    ) as f:
        f.write(baslik_icerik)
        f.write('# Kod içeriği\n')
        f.write('pass\n')
        dosya_yolu = f.name
    
    try:
        # Dosyayı analiz et
        rapor = analizor.dosya_basligini_analiz_et(dosya_yolu)
        
        # Property 1: Başlık var olmalı (kısmi başlık bile olsa)
        assert rapor.baslik_var, "Başlık tespit edilemedi"
        
        # Property 2: Eksik alanlar doğru tespit edilmeli
        tespit_edilen_eksikler = set(rapor.eksik_alanlar)
        beklenen_eksikler = set(eksik_alanlar)
        
        assert tespit_edilen_eksikler == beklenen_eksikler, \
            f"Eksik alanlar yanlış tespit edildi. " \
            f"Beklenen: {beklenen_eksikler}, Tespit edilen: {tespit_edilen_eksikler}"
        
        # Property 3: Eksik alan varsa standart uyumlu olmamalı
        if len(eksik_alanlar) > 0:
            assert not rapor.standart_uyumlu, \
                "Eksik alan olmasına rağmen standart uyumlu olarak işaretlendi"
        
        # Property 4: Eksik alan sayısı doğru olmalı
        assert len(rapor.eksik_alanlar) == len(eksik_alanlar), \
            f"Eksik alan sayısı yanlış: {len(rapor.eksik_alanlar)} != {len(eksik_alanlar)}"
        
    finally:
        # Geçici dosyayı temizle
        if os.path.exists(dosya_yolu):
            os.unlink(dosya_yolu)


@settings(max_examples=50)
@given(st.just([]))
def test_tam_baslik_eksik_alan_yok_property(_):
    """
    Property: Tam başlık varsa eksik alan tespit edilmemeli.
    """
    analizor = BaslikAnalizoru()
    
    # Tam başlık oluştur
    tam_baslik = """# Version: 0.1.0
# Last Update: 2025-12-17
# Module: test.module
# Description: Test açıklama
# Changelog:
# - İlk versiyon

"""
    
    # Geçici dosya oluştur
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.py',
        delete=False,
        encoding='utf-8'
    ) as f:
        f.write(tam_baslik)
        f.write('pass\n')
        dosya_yolu = f.name
    
    try:
        # Dosyayı analiz et
        rapor = analizor.dosya_basligini_analiz_et(dosya_yolu)
        
        # Property: Eksik alan olmamalı
        assert len(rapor.eksik_alanlar) == 0, \
            f"Tam başlıkta eksik alan tespit edildi: {rapor.eksik_alanlar}"
        
        # Property: Standart uyumlu olmalı
        assert rapor.standart_uyumlu, \
            "Tam başlık standart uyumlu değil"
        
    finally:
        # Geçici dosyayı temizle
        if os.path.exists(dosya_yolu):
            os.unlink(dosya_yolu)


@settings(max_examples=50)
@given(st.just([]))
def test_baslik_yok_tum_alanlar_eksik_property(_):
    """
    Property: Başlık yoksa tüm alanlar eksik olarak tespit edilmeli.
    """
    analizor = BaslikAnalizoru()
    
    # Başlıksız dosya
    icerik = """# Sadece yorum
pass
"""
    
    # Geçici dosya oluştur
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.py',
        delete=False,
        encoding='utf-8'
    ) as f:
        f.write(icerik)
        dosya_yolu = f.name
    
    try:
        # Dosyayı analiz et
        rapor = analizor.dosya_basligini_analiz_et(dosya_yolu)
        
        # Property: Başlık yok olmalı
        assert not rapor.baslik_var, "Başlık var olarak tespit edildi"
        
        # Property: Tüm alanlar eksik olmalı
        beklenen_eksikler = {'version', 'last_update', 'module', 'description', 'changelog'}
        tespit_edilen_eksikler = set(rapor.eksik_alanlar)
        
        assert tespit_edilen_eksikler == beklenen_eksikler, \
            f"Tüm alanlar eksik olarak tespit edilmedi. " \
            f"Tespit edilen: {tespit_edilen_eksikler}"
        
    finally:
        # Geçici dosyayı temizle
        if os.path.exists(dosya_yolu):
            os.unlink(dosya_yolu)

