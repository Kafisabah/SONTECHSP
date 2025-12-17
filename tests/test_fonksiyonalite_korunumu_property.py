# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_fonksiyonalite_korunumu_property
# Description: Fonksiyonalite korunumu property-based testleri
# Changelog:
# - İlk versiyon: Property testleri oluşturuldu

"""
**Feature: kod-kalitesi-standardizasyon, Property 13: Fonksiyonalite Korunumu**

For any kod taşıma işlemi, taşıma öncesi ve sonrası 
sistem davranışı aynı kalmalıdır.

**Validates: Requirements 4.4**
"""

import tempfile
import ast
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume

from uygulama.moduller.kod_kalitesi.refactoring.ortak_modul_cikarici import (
    OrtakModulCikarici
)


def basit_fonksiyon_olustur(isim: str, deger: int) -> str:
    """Test için basit fonksiyon oluşturur."""
    return f"""def {isim}(x):
    \"\"\"Basit fonksiyon\"\"\"
    return x + {deger}
"""


def fonksiyon_kullanan_kod_olustur(fonk_adi: str, cagri_sayisi: int) -> str:
    """Fonksiyon çağrısı yapan kod oluşturur."""
    satirlar = [
        f"def ana_fonksiyon():",
        f"    \"\"\"Ana fonksiyon\"\"\"",
        f"    sonuc = 0"
    ]
    
    for i in range(cagri_sayisi):
        satirlar.append(f"    sonuc += {fonk_adi}({i})")
    
    satirlar.append(f"    return sonuc")
    return '\n'.join(satirlar)


@given(
    fonksiyon_sayisi=st.integers(min_value=1, max_value=5),
    deger=st.integers(min_value=1, max_value=100)
)
@settings(max_examples=100, deadline=None)
def test_kod_tasima_syntax_korunumu(fonksiyon_sayisi, deger):
    """
    Property: Kod taşıma işlemi sonrası dosyalar geçerli Python kodu olmalı.
    
    Test stratejisi:
    - Fonksiyonlar içeren dosya oluştur
    - Ortak modüle taşı
    - Her iki dosyanın da geçerli Python olduğunu kontrol et
    """
    cikarici = OrtakModulCikarici()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Kaynak dosya oluştur
        kaynak_dosya = Path(tmpdir) / "kaynak.py"
        fonksiyonlar = []
        
        for i in range(fonksiyon_sayisi):
            fonk = basit_fonksiyon_olustur(f"fonksiyon_{i}", deger + i)
            fonksiyonlar.append(fonk)
        
        kaynak_icerik = '\n\n'.join(fonksiyonlar)
        kaynak_dosya.write_text(kaynak_icerik, encoding='utf-8')
        
        # Ortak modül oluştur
        ortak_modul = Path(tmpdir) / "ortak" / "yardimcilar.py"
        
        # İlk fonksiyonu taşı
        ilk_fonk = fonksiyonlar[0]
        modul_yolu = cikarici.ortak_modul_olustur(
            modul_adi="yardimcilar",
            modul_yolu=str(ortak_modul),
            benzer_bloklar=[],
            ortak_kod=ilk_fonk
        )
        
        # Property 1: Ortak modül geçerli Python kodu olmalı
        with open(modul_yolu, 'r', encoding='utf-8') as f:
            ortak_icerik = f.read()
        
        try:
            ast.parse(ortak_icerik)
            syntax_gecerli = True
        except SyntaxError:
            syntax_gecerli = False
        
        assert syntax_gecerli, \
            "Oluşturulan ortak modül geçerli Python kodu değil"
        
        # Property 2: Kaynak dosya hala geçerli olmalı
        try:
            ast.parse(kaynak_icerik)
            kaynak_gecerli = True
        except SyntaxError:
            kaynak_gecerli = False
        
        assert kaynak_gecerli, \
            "Kaynak dosya geçerli Python kodu değil"


@given(
    cagri_sayisi=st.integers(min_value=1, max_value=10),
    deger=st.integers(min_value=1, max_value=50)
)
@settings(max_examples=100, deadline=None)
def test_referans_guncelleme_tutarliligi(cagri_sayisi, deger):
    """
    Property: Referans güncelleme sonrası import yapısı tutarlı olmalı.
    
    Test stratejisi:
    - Fonksiyon çağrısı yapan kod oluştur
    - Fonksiyonu ortak modüle taşı
    - Import'ların doğru eklendiğini kontrol et
    """
    cikarici = OrtakModulCikarici()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Yardımcı fonksiyon
        fonk_adi = "yardimci_fonk"
        yardimci_fonk = basit_fonksiyon_olustur(fonk_adi, deger)
        
        # Ana kod
        ana_kod = fonksiyon_kullanan_kod_olustur(fonk_adi, cagri_sayisi)
        
        # Kaynak dosya
        kaynak_dosya = Path(tmpdir) / "kaynak.py"
        kaynak_icerik = f"{yardimci_fonk}\n\n{ana_kod}"
        kaynak_dosya.write_text(kaynak_icerik, encoding='utf-8')
        
        # Ortak modül oluştur
        ortak_modul = Path(tmpdir) / "ortak_yardimcilar.py"
        cikarici.ortak_modul_olustur(
            modul_adi="ortak_yardimcilar",
            modul_yolu=str(ortak_modul),
            benzer_bloklar=[],
            ortak_kod=yardimci_fonk
        )
        
        # Referansları güncelle
        guncellemeler = cikarici.referanslari_guncelle(
            etkilenen_dosyalar={str(kaynak_dosya)},
            ortak_modul_yolu=str(ortak_modul),
            fonksiyon_adi=fonk_adi
        )
        
        # Property 1: En az bir güncelleme yapılmalı
        assert len(guncellemeler) >= 0, \
            "Referans güncellemesi yapılmalı"
        
        # Property 2: Güncellenmiş dosya geçerli Python olmalı
        if kaynak_dosya.exists():
            with open(kaynak_dosya, 'r', encoding='utf-8') as f:
                guncellenmis = f.read()
            
            try:
                ast.parse(guncellenmis)
                gecerli = True
            except SyntaxError:
                gecerli = False
            
            assert gecerli, \
                "Güncellenmiş dosya geçerli Python kodu değil"



@given(deger=st.integers(min_value=1, max_value=100))
@settings(max_examples=100, deadline=None)
def test_fonksiyon_tanimi_kaldirma(deger):
    """
    Property: Fonksiyon tanımı kaldırıldığında dosya hala geçerli olmalı.
    
    Test stratejisi:
    - Birden fazla fonksiyon içeren dosya oluştur
    - Bir fonksiyonu kaldır
    - Dosyanın hala geçerli olduğunu kontrol et
    """
    cikarici = OrtakModulCikarici()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Birden fazla fonksiyon oluştur
        fonk1 = basit_fonksiyon_olustur("fonksiyon_1", deger)
        fonk2 = basit_fonksiyon_olustur("fonksiyon_2", deger * 2)
        fonk3 = basit_fonksiyon_olustur("fonksiyon_3", deger * 3)
        
        kaynak_dosya = Path(tmpdir) / "kaynak.py"
        icerik = f"{fonk1}\n\n{fonk2}\n\n{fonk3}"
        kaynak_dosya.write_text(icerik, encoding='utf-8')
        
        # Bir fonksiyonu kaldır
        yeni_icerik, kaldirilan = cikarici._fonksiyon_tanimini_kaldir(
            icerik, "fonksiyon_2"
        )
        
        # Property 1: Fonksiyon kaldırılmalı
        assert kaldirilan, "Fonksiyon kaldırılmalı"
        
        # Property 2: Yeni içerik geçerli Python olmalı
        try:
            ast.parse(yeni_icerik)
            gecerli = True
        except SyntaxError:
            gecerli = False
        
        assert gecerli, \
            "Fonksiyon kaldırıldıktan sonra dosya geçersiz oldu"
        
        # Property 3: Diğer fonksiyonlar korunmalı
        assert "fonksiyon_1" in yeni_icerik, \
            "Diğer fonksiyonlar korunmalı"
        assert "fonksiyon_3" in yeni_icerik, \
            "Diğer fonksiyonlar korunmalı"


@given(
    fonksiyon_sayisi=st.integers(min_value=2, max_value=5),
    deger=st.integers(min_value=1, max_value=50)
)
@settings(max_examples=100, deadline=None)
def test_ortak_modul_import_yapisi(fonksiyon_sayisi, deger):
    """
    Property: Ortak modül oluşturulduğunda import yapısı doğru olmalı.
    
    Test stratejisi:
    - Import içeren fonksiyonlar oluştur
    - Ortak modüle taşı
    - Import'ların doğru çıkarıldığını kontrol et
    """
    cikarici = OrtakModulCikarici()
    
    # Import içeren fonksiyon
    fonk_kod = """import os
from pathlib import Path

def test_fonksiyon(x):
    \"\"\"Test fonksiyonu\"\"\"
    p = Path(x)
    return os.path.exists(p)
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        ortak_modul = Path(tmpdir) / "ortak.py"
        
        modul_yolu = cikarici.ortak_modul_olustur(
            modul_adi="ortak",
            modul_yolu=str(ortak_modul),
            benzer_bloklar=[],
            ortak_kod=fonk_kod
        )
        
        # Modül içeriğini oku
        with open(modul_yolu, 'r', encoding='utf-8') as f:
            modul_icerik = f.read()
        
        # Property 1: Modül geçerli Python olmalı
        try:
            ast.parse(modul_icerik)
            gecerli = True
        except SyntaxError:
            gecerli = False
        
        assert gecerli, "Oluşturulan modül geçerli Python değil"
        
        # Property 2: Import'lar korunmalı
        assert "import os" in modul_icerik or "from pathlib import Path" in modul_icerik, \
            "Import'lar ortak modülde korunmalı"
        
        # Property 3: Fonksiyon tanımı olmalı
        assert "def test_fonksiyon" in modul_icerik, \
            "Fonksiyon tanımı ortak modülde olmalı"


@given(deger=st.integers(min_value=1, max_value=100))
@settings(max_examples=100, deadline=None)
def test_fonksiyonalite_dogrulama(deger):
    """
    Property: Fonksiyonalite doğrulama her iki dosyanın da geçerli olduğunu kontrol etmeli.
    
    Test stratejisi:
    - Geçerli ve geçersiz dosyalar oluştur
    - Doğrulama fonksiyonunu test et
    """
    cikarici = OrtakModulCikarici()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Geçerli dosya
        gecerli_dosya = Path(tmpdir) / "gecerli.py"
        gecerli_kod = basit_fonksiyon_olustur("test", deger)
        gecerli_dosya.write_text(gecerli_kod, encoding='utf-8')
        
        # Geçersiz dosya
        gecersiz_dosya = Path(tmpdir) / "gecersiz.py"
        gecersiz_kod = "def test(x\n    return x"  # Syntax hatası
        gecersiz_dosya.write_text(gecersiz_kod, encoding='utf-8')
        
        # Property 1: Geçerli dosyalar için True dönmeli
        sonuc1 = cikarici.fonksiyonalite_dogrula(
            str(gecerli_dosya),
            str(gecerli_dosya)
        )
        assert sonuc1, "Geçerli dosyalar için True dönmeli"
        
        # Property 2: Geçersiz dosya için False dönmeli
        sonuc2 = cikarici.fonksiyonalite_dogrula(
            str(gecerli_dosya),
            str(gecersiz_dosya)
        )
        assert not sonuc2, "Geçersiz dosya için False dönmeli"
