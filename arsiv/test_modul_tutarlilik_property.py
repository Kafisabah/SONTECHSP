# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_modul_tutarlilik_property
# Description: Modül tutarlılığı ve public API koruma property testleri
# Changelog:
# - İlk versiyon: Property 26 ve 27 testleri oluşturuldu

"""
Modül Tutarlılığı Property Testleri

**Feature: kod-kalitesi-standardizasyon, Property 26: Modül Tutarlılığı**
**Validates: Requirements 7.3**

**Feature: kod-kalitesi-standardizasyon, Property 27: Public API Korunumu**
**Validates: Requirements 7.4**
"""

import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from uygulama.moduller.kod_kalitesi.refactoring import (
    ModulTutarlilikKoruyucu
)


# Test için kod şablonları
BASIT_FONKSIYON = """
def {isim}():
    return "test"
"""

PUBLIC_FONKSIYON = """
def public_function(x, y):
    return x + y
"""

PRIVATE_FONKSIYON = """
def _private_function():
    return "private"
"""

SINIF_SABLONU = """
class {isim}:
    def __init__(self):
        self.value = 0
    
    def method(self):
        return self.value
"""


@st.composite
def python_modul_stratejisi(draw):
    """Python modülü oluşturur"""
    fonksiyon_sayisi = draw(st.integers(min_value=1, max_value=5))
    
    kod_parcalari = []
    for i in range(fonksiyon_sayisi):
        isim = f"func{i}"
        kod_parcalari.append(BASIT_FONKSIYON.format(isim=isim))
    
    return '\n'.join(kod_parcalari)


@given(python_modul_stratejisi())
@settings(max_examples=100, deadline=None)
def test_modul_tutarliligi_property(modul_icerik):
    """
    Property 26: Modül Tutarlılığı
    
    For any alt dosya oluşturma işlemi, modül içi tutarlılığın
    korunması gerekir.
    
    Bu test, herhangi bir Python modülü için tutarlılık kontrolünün
    doğru çalıştığını doğrular.
    """
    # Geçici modül klasörü oluştur
    with tempfile.TemporaryDirectory() as temp_dir:
        modul_yolu = Path(temp_dir)
        
        # Test dosyası oluştur
        test_dosya = modul_yolu / "test_module.py"
        test_dosya.write_text(modul_icerik, encoding='utf-8')
        
        # Tutarlılık koruyucu oluştur
        koruyucu = ModulTutarlilikKoruyucu()
        
        # Tutarlılık kontrolü yap
        sonuc = koruyucu.modul_tutarliligini_kontrol_et(str(modul_yolu))
        
        # Property 1: Sonuç nesnesi oluşturulmalı
        assert sonuc is not None, "Tutarlılık sonucu None olmamalı"
        
        # Property 2: Sonuç tutarlı veya tutarsız olmalı (boolean)
        assert isinstance(sonuc.tutarli, bool), \
            "Tutarlılık durumu boolean olmalı"
        
        # Property 3: Hatalar listesi olmalı
        assert isinstance(sonuc.hatalar, list), \
            "Hatalar listesi olmalı"
        
        # Property 4: Uyarılar listesi olmalı
        assert isinstance(sonuc.uyarilar, list), \
            "Uyarılar listesi olmalı"
        
        # Property 5: Eğer hatalar varsa, tutarlı olmamalı
        if len(sonuc.hatalar) > 0:
            assert not sonuc.tutarli, \
                "Hatalar varsa modül tutarlı olmamalı"


@given(st.text(min_size=1, max_size=20, alphabet=st.characters(
    whitelist_categories=('Ll', 'Lu'),
    blacklist_characters='_'
)))
@settings(max_examples=100, deadline=None)
def test_public_api_korunumu_property(fonksiyon_adi):
    """
    Property 27: Public API Korunumu
    
    For any dosya bölme işlemi, public API'nin değişmemesi gerekir.
    
    Bu test, dosya değişikliklerinde public API'nin korunduğunu
    doğrular.
    """
    # Geçersiz karakterleri temizle
    fonksiyon_adi = ''.join(c for c in fonksiyon_adi if c.isalnum() or c == '_')
    assume(len(fonksiyon_adi) > 0)
    assume(fonksiyon_adi[0].isalpha() or fonksiyon_adi[0] == '_')
    
    # Geçici dosyalar oluştur
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.py',
        delete=False,
        encoding='utf-8'
    ) as f1:
        # Orijinal dosya - public fonksiyon içerir
        f1.write(PUBLIC_FONKSIYON)
        f1.write('\n')
        f1.write(PRIVATE_FONKSIYON)
        onceki_dosya = f1.name
    
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.py',
        delete=False,
        encoding='utf-8'
    ) as f2:
        # Yeni dosya - aynı public fonksiyon içerir
        f2.write(PUBLIC_FONKSIYON)
        f2.write('\n')
        f2.write(PRIVATE_FONKSIYON)
        f2.write('\n')
        # Yeni private fonksiyon ekle (public API'yi etkilememeli)
        f2.write(f"def _{fonksiyon_adi}():\n    pass\n")
        sonraki_dosya = f2.name
    
    try:
        # API koruyucu oluştur
        koruyucu = ModulTutarlilikKoruyucu()
        
        # API bilgilerini çıkart
        onceki_api = koruyucu.api_bilgisi_cikart(onceki_dosya)
        sonraki_api = koruyucu.api_bilgisi_cikart(sonraki_dosya)
        
        # Property 1: Public fonksiyonlar korunmalı
        assert onceki_api.fonksiyonlar == sonraki_api.fonksiyonlar, \
            "Public fonksiyonlar değişmemeli"
        
        # Property 2: Public sınıflar korunmalı
        assert onceki_api.siniflar == sonraki_api.siniflar, \
            "Public sınıflar değişmemeli"
        
        # Property 3: API korunumu kontrolü doğru çalışmalı
        korunuyor, hatalar = koruyucu.public_api_korunuyor_mu(
            onceki_dosya, sonraki_dosya
        )
        assert korunuyor, f"Public API korunmalı, hatalar: {hatalar}"
        assert len(hatalar) == 0, "Hata olmamalı"
    
    finally:
        # Geçici dosyaları temizle
        Path(onceki_dosya).unlink(missing_ok=True)
        Path(sonraki_dosya).unlink(missing_ok=True)


@given(st.text(min_size=1, max_size=20, alphabet=st.characters(
    whitelist_categories=('Ll', 'Lu'),
    blacklist_characters='_'
)))
@settings(max_examples=100, deadline=None)
def test_public_api_degisiklik_tespiti_property(fonksiyon_adi):
    """
    Property 27 (ek): Public API Değişiklik Tespiti
    
    Public API'de değişiklik olduğunda bunun tespit edilmesi gerekir.
    """
    # Geçersiz karakterleri temizle
    fonksiyon_adi = ''.join(c for c in fonksiyon_adi if c.isalnum() or c == '_')
    assume(len(fonksiyon_adi) > 0)
    assume(fonksiyon_adi[0].isalpha() or fonksiyon_adi[0] == '_')
    
    # Geçici dosyalar oluştur
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.py',
        delete=False,
        encoding='utf-8'
    ) as f1:
        # Orijinal dosya
        f1.write(PUBLIC_FONKSIYON)
        onceki_dosya = f1.name
    
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.py',
        delete=False,
        encoding='utf-8'
    ) as f2:
        # Yeni dosya - public fonksiyon SİLİNMİŞ
        f2.write(PRIVATE_FONKSIYON)
        sonraki_dosya = f2.name
    
    try:
        # API koruyucu oluştur
        koruyucu = ModulTutarlilikKoruyucu()
        
        # API farklarını tespit et
        fark = koruyucu.api_farklarini_tespit_et(
            onceki_dosya, sonraki_dosya
        )
        
        # Property 1: Silinen fonksiyonlar tespit edilmeli
        assert len(fark.silinen_fonksiyonlar) > 0, \
            "Silinen public fonksiyon tespit edilmeli"
        
        # Property 2: API korunumu kontrolü başarısız olmalı
        korunuyor, hatalar = koruyucu.public_api_korunuyor_mu(
            onceki_dosya, sonraki_dosya
        )
        assert not korunuyor, "Public API değiştiğinde korunma başarısız olmalı"
        assert len(hatalar) > 0, "Hatalar rapor edilmeli"
    
    finally:
        # Geçici dosyaları temizle
        Path(onceki_dosya).unlink(missing_ok=True)
        Path(sonraki_dosya).unlink(missing_ok=True)


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
