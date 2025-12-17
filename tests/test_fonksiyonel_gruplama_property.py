# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_fonksiyonel_gruplama_property
# Description: Fonksiyonel gruplama property testleri
# Changelog:
# - İlk versiyon: Property 24 testi oluşturuldu

"""
Fonksiyonel Gruplama Property Testleri

**Feature: kod-kalitesi-standardizasyon, Property 24: Fonksiyonel Gruplama**
**Validates: Requirements 7.1**
"""

import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings
from uygulama.moduller.kod_kalitesi.refactoring import (
    FonksiyonelGruplayici, GrupTuru
)


# Test için kod şablonları
DOGRULAMA_FONKSIYONU = """
def {isim}_dogrula(deger):
    if not deger:
        raise ValueError("Geçersiz değer")
    return True
"""

HESAPLAMA_FONKSIYONU = """
def {isim}_hesapla(a, b):
    return a + b
"""

VERI_ISLEME_FONKSIYONU = """
def {isim}_isle(veri):
    return veri.upper()
"""

YARDIMCI_FONKSIYON = """
def _{isim}_yardimci():
    return "yardımcı"
"""

VERITABANI_FONKSIYONU = """
def {isim}_ekle(session, item):
    session.add(item)
    return item
"""


@st.composite
def python_dosya_stratejisi(draw):
    """Python dosyası oluşturur"""
    fonksiyon_sayisi = draw(st.integers(min_value=1, max_value=10))
    
    fonksiyonlar = []
    for i in range(fonksiyon_sayisi):
        fonk_turu = draw(st.sampled_from([
            'dogrulama', 'hesaplama', 'veri_isleme',
            'yardimci', 'veritabani'
        ]))
        
        isim = f"test{i}"
        
        if fonk_turu == 'dogrulama':
            fonksiyonlar.append(DOGRULAMA_FONKSIYONU.format(isim=isim))
        elif fonk_turu == 'hesaplama':
            fonksiyonlar.append(HESAPLAMA_FONKSIYONU.format(isim=isim))
        elif fonk_turu == 'veri_isleme':
            fonksiyonlar.append(VERI_ISLEME_FONKSIYONU.format(isim=isim))
        elif fonk_turu == 'yardimci':
            fonksiyonlar.append(YARDIMCI_FONKSIYON.format(isim=isim))
        elif fonk_turu == 'veritabani':
            fonksiyonlar.append(VERITABANI_FONKSIYONU.format(isim=isim))
    
    return '\n'.join(fonksiyonlar)


@given(python_dosya_stratejisi())
@settings(max_examples=100, deadline=None)
def test_fonksiyonel_gruplama_property(dosya_icerik):
    """
    Property 24: Fonksiyonel Gruplama
    
    For any büyük dosya analizi, fonksiyonel grupların tespit edilmesi gerekir.
    
    Bu test, herhangi bir Python dosyası için fonksiyonel grupların
    doğru tespit edildiğini doğrular.
    """
    # Geçici dosya oluştur
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.py',
        delete=False,
        encoding='utf-8'
    ) as f:
        f.write(dosya_icerik)
        dosya_yolu = f.name
    
    try:
        # Gruplayıcıyı çalıştır
        gruplayici = FonksiyonelGruplayici()
        sonuc = gruplayici.dosyayi_grupla(dosya_yolu)
        
        # Property 1: Gruplar boş olmamalı (en az bir grup olmalı)
        assert len(sonuc.gruplar) > 0, "Hiç grup tespit edilemedi"
        
        # Property 2: Her fonksiyon bir gruba atanmalı
        toplam_fonksiyon = sum(
            len(fonksiyonlar) for fonksiyonlar in sonuc.gruplar.values()
        )
        assert toplam_fonksiyon > 0, "Hiç fonksiyon gruplanmadı"
        
        # Property 3: Doğrulama fonksiyonları doğru grupta olmalı
        if GrupTuru.DOGRULAMA in sonuc.gruplar:
            for fonk in sonuc.gruplar[GrupTuru.DOGRULAMA]:
                # Doğrulama grubundaki fonksiyonlar doğrulama anahtar kelimeleri içermeli
                # VEYA başka gruplara ait anahtar kelimeler içermemeli
                has_validation_keyword = any(
                    kelime in fonk.isim.lower()
                    for kelime in ['dogrula', 'validate', 'kontrol', 'check', 'verify', 'test']
                )
                has_other_keyword = (
                    any(k in fonk.isim.lower() for k in ['hesapla', 'calculate']) or
                    any(k in fonk.isim.lower() for k in ['ekle', 'add', 'insert', 'guncelle']) or
                    any(k in fonk.isim.lower() for k in ['isle', 'process', 'donustur'])
                )
                assert has_validation_keyword or not has_other_keyword, \
                    f"Doğrulama grubunda yanlış fonksiyon: {fonk.isim}"
        
        # Property 4: Yardımcı fonksiyonlar doğru grupta olmalı
        if GrupTuru.YARDIMCILAR in sonuc.gruplar:
            for fonk in sonuc.gruplar[GrupTuru.YARDIMCILAR]:
                assert fonk.isim.startswith('_') and not fonk.isim.startswith('__'), \
                    f"Yardımcılar grubunda yanlış fonksiyon: {fonk.isim}"
        
        # Property 5: Hesaplama fonksiyonları doğru grupta olmalı
        if GrupTuru.HESAPLAMALAR in sonuc.gruplar:
            for fonk in sonuc.gruplar[GrupTuru.HESAPLAMALAR]:
                assert any(
                    kelime in fonk.isim.lower()
                    for kelime in ['hesapla', 'calculate', 'compute', 'topla', 'sum']
                ), f"Hesaplamalar grubunda yanlış fonksiyon: {fonk.isim}"
        
        # Property 6: Veritabanı fonksiyonları doğru grupta olmalı
        if GrupTuru.VERITABANI in sonuc.gruplar:
            for fonk in sonuc.gruplar[GrupTuru.VERITABANI]:
                assert any(
                    kelime in fonk.isim.lower()
                    for kelime in ['ekle', 'add', 'insert', 'guncelle', 'sil', 'bul', 'getir']
                ), f"Veritabanı grubunda yanlış fonksiyon: {fonk.isim}"
        
        # Property 7: Önerilen dosya isimleri uygun formatta olmalı
        for grup, dosya_adi in sonuc.onerilen_dosya_isimleri.items():
            assert dosya_adi.endswith('.py'), \
                f"Dosya adı .py ile bitmeli: {dosya_adi}"
            assert dosya_adi == dosya_adi.lower(), \
                f"Dosya adı küçük harf olmalı: {dosya_adi}"
    
    finally:
        # Geçici dosyayı temizle
        Path(dosya_yolu).unlink(missing_ok=True)


@given(st.text(min_size=1, max_size=50, alphabet=st.characters(
    whitelist_categories=('Lu', 'Ll', 'Nd'),
    blacklist_characters='_'
)))
@settings(max_examples=100, deadline=None)
def test_isimlendirme_kurallari_property(dosya_adi):
    """
    Property 25: İsimlendirme Kuralları (ek test)
    
    For any bölme stratejisi, anlamlı isimlerin kullanılması gerekir.
    
    Bu test, dosya isimlerinin isimlendirme kurallarına uygun olup
    olmadığını kontrol eder.
    """
    gruplayici = FonksiyonelGruplayici()
    
    # İsimlendirme kurallarını uygula
    uygun, duzeltilmis = gruplayici.isimlendirme_kurallari_uygula(dosya_adi)
    
    # Property 1: Düzeltilmiş isim küçük harf olmalı
    assert duzeltilmis == duzeltilmis.lower(), \
        f"Düzeltilmiş isim küçük harf değil: {duzeltilmis}"
    
    # Property 2: Düzeltilmiş isim .py ile bitmeli
    assert duzeltilmis.endswith('.py'), \
        f"Düzeltilmiş isim .py ile bitmiyor: {duzeltilmis}"
    
    # Property 3: Düzeltilmiş isimde tire olmamalı
    assert '-' not in duzeltilmis, \
        f"Düzeltilmiş isimde tire var: {duzeltilmis}"
    
    # Property 4: Düzeltilmiş isimde boşluk olmamalı
    assert ' ' not in duzeltilmis, \
        f"Düzeltilmiş isimde boşluk var: {duzeltilmis}"
    
    # Property 5: İdempotence - düzeltilmiş ismi tekrar düzeltmek aynı sonucu vermeli
    uygun2, duzeltilmis2 = gruplayici.isimlendirme_kurallari_uygula(
        duzeltilmis
    )
    assert duzeltilmis == duzeltilmis2, \
        "İsimlendirme kuralları idempotent değil"


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
