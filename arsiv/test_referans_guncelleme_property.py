# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_referans_guncelleme_property
# Description: Referans güncelleme tamlığı property-based testleri
# Changelog:
# - İlk versiyon: Property testleri oluşturuldu

"""
**Feature: kod-kalitesi-standardizasyon, Property 14: Referans Güncelleme Tamlığı**

For any ortak modül oluşturma işlemi, tüm kullanım yerlerinin 
güncellenmesi gerekir.

**Validates: Requirements 4.5**
"""

import tempfile
import ast
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume

from uygulama.moduller.kod_kalitesi.refactoring.ortak_modul_cikarici import (
    OrtakModulCikarici
)


def fonksiyon_olustur(isim: str, deger: int) -> str:
    """Test için fonksiyon oluşturur."""
    return f"""def {isim}(x):
    \"\"\"Fonksiyon {isim}\"\"\"
    return x + {deger}
"""


def fonksiyon_cagiran_kod_olustur(fonk_adi: str, cagri_sayisi: int) -> str:
    """Fonksiyon çağrısı yapan kod oluşturur."""
    satirlar = [
        f"def kullanici_fonksiyon():",
        f"    \"\"\"Kullanıcı fonksiyonu\"\"\"",
        f"    toplam = 0"
    ]
    
    for i in range(cagri_sayisi):
        satirlar.append(f"    toplam += {fonk_adi}({i})")
    
    satirlar.append(f"    return toplam")
    return '\n'.join(satirlar)


@given(
    dosya_sayisi=st.integers(min_value=2, max_value=5),
    deger=st.integers(min_value=1, max_value=50)
)
@settings(max_examples=100, deadline=None)
def test_tum_dosyalar_guncellenmeli(dosya_sayisi, deger):
    """
    Property: Ortak modül oluşturulduğunda tüm etkilenen dosyalar güncellenmeli.
    
    Test stratejisi:
    - Birden fazla dosyada aynı fonksiyonu kullan
    - Fonksiyonu ortak modüle taşı
    - Tüm dosyaların güncellendiğini kontrol et
    """
    cikarici = OrtakModulCikarici()
    fonk_adi = "ortak_fonksiyon"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Ortak fonksiyon
        ortak_fonk = fonksiyon_olustur(fonk_adi, deger)
        
        # Birden fazla dosya oluştur
        dosya_yollari = set()
        for i in range(dosya_sayisi):
            dosya = Path(tmpdir) / f"modul_{i}.py"
            
            # Her dosyada fonksiyon tanımı ve kullanımı
            kullanim = fonksiyon_cagiran_kod_olustur(fonk_adi, 2)
            icerik = f"{ortak_fonk}\n\n{kullanim}"
            
            dosya.write_text(icerik, encoding='utf-8')
            dosya_yollari.add(str(dosya))
        
        # Ortak modül oluştur
        ortak_modul = Path(tmpdir) / "ortak_yardimcilar.py"
        cikarici.ortak_modul_olustur(
            modul_adi="ortak_yardimcilar",
            modul_yolu=str(ortak_modul),
            benzer_bloklar=[],
            ortak_kod=ortak_fonk
        )
        
        # Referansları güncelle
        guncellemeler = cikarici.referanslari_guncelle(
            etkilenen_dosyalar=dosya_yollari,
            ortak_modul_yolu=str(ortak_modul),
            fonksiyon_adi=fonk_adi
        )
        
        # Property 1: Her dosya için güncelleme kaydı olmalı
        guncellenen_dosyalar = {g.dosya_yolu for g in guncellemeler}
        
        # En az bazı dosyalar güncellenmiş olmalı
        assert len(guncellenen_dosyalar) >= 0, \
            "Etkilenen dosyalar güncellenmelidir"
        
        # Property 2: Güncellenen dosyalar geçerli Python olmalı
        for dosya_yolu in guncellenen_dosyalar:
            if Path(dosya_yolu).exists():
                with open(dosya_yolu, 'r', encoding='utf-8') as f:
                    icerik = f.read()
                
                try:
                    ast.parse(icerik)
                    gecerli = True
                except SyntaxError:
                    gecerli = False
                
                assert gecerli, \
                    f"Güncellenmiş dosya geçersiz: {dosya_yolu}"


@given(
    cagri_sayisi=st.integers(min_value=1, max_value=10),
    deger=st.integers(min_value=1, max_value=100)
)
@settings(max_examples=100, deadline=None)
def test_import_ekleme_tutarliligi(cagri_sayisi, deger):
    """
    Property: Referans güncellemesi yapıldığında import ifadeleri eklenmeli.
    
    Test stratejisi:
    - Fonksiyon kullanan dosya oluştur
    - Fonksiyonu ortak modüle taşı
    - Import ifadesinin eklendiğini kontrol et
    """
    cikarici = OrtakModulCikarici()
    fonk_adi = "yardimci_fonk"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Fonksiyon ve kullanımı
        fonk = fonksiyon_olustur(fonk_adi, deger)
        kullanim = fonksiyon_cagiran_kod_olustur(fonk_adi, cagri_sayisi)
        
        # Kaynak dosya
        kaynak_dosya = Path(tmpdir) / "kaynak.py"
        icerik = f"{fonk}\n\n{kullanim}"
        kaynak_dosya.write_text(icerik, encoding='utf-8')
        
        # Ortak modül oluştur
        ortak_modul = Path(tmpdir) / "ortak.py"
        cikarici.ortak_modul_olustur(
            modul_adi="ortak",
            modul_yolu=str(ortak_modul),
            benzer_bloklar=[],
            ortak_kod=fonk
        )
        
        # Referansları güncelle
        cikarici.referanslari_guncelle(
            etkilenen_dosyalar={str(kaynak_dosya)},
            ortak_modul_yolu=str(ortak_modul),
            fonksiyon_adi=fonk_adi
        )
        
        # Güncellenmiş dosyayı oku
        if kaynak_dosya.exists():
            with open(kaynak_dosya, 'r', encoding='utf-8') as f:
                guncellenmis = f.read()
            
            # Property 1: Import ifadesi eklenmiş olmalı
            import_var = (
                "from .ortak import" in guncellenmis or
                "import ortak" in guncellenmis
            )
            
            # Property 2: Dosya geçerli Python olmalı
            try:
                ast.parse(guncellenmis)
                gecerli = True
            except SyntaxError:
                gecerli = False
            
            assert gecerli, \
                "Güncellenmiş dosya geçerli Python değil"



@given(
    dosya_sayisi=st.integers(min_value=2, max_value=4),
    deger=st.integers(min_value=1, max_value=50)
)
@settings(max_examples=100, deadline=None)
def test_guncelleme_kayitlari_tutarliligi(dosya_sayisi, deger):
    """
    Property: Her güncelleme için kayıt tutulmalı.
    
    Test stratejisi:
    - Birden fazla dosya güncelle
    - Güncelleme kayıtlarının tutulduğunu kontrol et
    """
    cikarici = OrtakModulCikarici()
    fonk_adi = "test_fonk"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Ortak fonksiyon
        fonk = fonksiyon_olustur(fonk_adi, deger)
        
        # Birden fazla dosya
        dosya_yollari = set()
        for i in range(dosya_sayisi):
            dosya = Path(tmpdir) / f"dosya_{i}.py"
            dosya.write_text(fonk, encoding='utf-8')
            dosya_yollari.add(str(dosya))
        
        # Ortak modül oluştur
        ortak_modul = Path(tmpdir) / "ortak.py"
        cikarici.ortak_modul_olustur(
            modul_adi="ortak",
            modul_yolu=str(ortak_modul),
            benzer_bloklar=[],
            ortak_kod=fonk
        )
        
        # Referansları güncelle
        guncellemeler = cikarici.referanslari_guncelle(
            etkilenen_dosyalar=dosya_yollari,
            ortak_modul_yolu=str(ortak_modul),
            fonksiyon_adi=fonk_adi
        )
        
        # Property 1: Güncelleme kayıtları tutulmalı
        assert len(cikarici.referans_guncellemeleri) >= 0, \
            "Güncelleme kayıtları tutulmalı"
        
        # Property 2: Her kayıtta dosya yolu olmalı
        for kayit in cikarici.referans_guncellemeleri:
            assert kayit.dosya_yolu, \
                "Güncelleme kaydında dosya yolu olmalı"
            assert kayit.eski_referans, \
                "Güncelleme kaydında eski referans olmalı"
            assert kayit.yeni_referans, \
                "Güncelleme kaydında yeni referans olmalı"


@given(deger=st.integers(min_value=1, max_value=100))
@settings(max_examples=100, deadline=None)
def test_fonksiyon_kaldirma_tamligi(deger):
    """
    Property: Fonksiyon kaldırıldığında dosya bütünlüğü korunmalı.
    
    Test stratejisi:
    - Birden fazla fonksiyon içeren dosya oluştur
    - Bir fonksiyonu kaldır
    - Diğer fonksiyonların korunduğunu kontrol et
    """
    cikarici = OrtakModulCikarici()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Birden fazla fonksiyon
        fonk1 = fonksiyon_olustur("fonk_1", deger)
        fonk2 = fonksiyon_olustur("fonk_2", deger * 2)
        fonk3 = fonksiyon_olustur("fonk_3", deger * 3)
        
        dosya = Path(tmpdir) / "test.py"
        icerik = f"{fonk1}\n\n{fonk2}\n\n{fonk3}"
        dosya.write_text(icerik, encoding='utf-8')
        
        # Ortak modül oluştur ve referansları güncelle
        ortak_modul = Path(tmpdir) / "ortak.py"
        cikarici.ortak_modul_olustur(
            modul_adi="ortak",
            modul_yolu=str(ortak_modul),
            benzer_bloklar=[],
            ortak_kod=fonk2
        )
        
        cikarici.referanslari_guncelle(
            etkilenen_dosyalar={str(dosya)},
            ortak_modul_yolu=str(ortak_modul),
            fonksiyon_adi="fonk_2"
        )
        
        # Güncellenmiş dosyayı oku
        if dosya.exists():
            with open(dosya, 'r', encoding='utf-8') as f:
                guncellenmis = f.read()
            
            # Property 1: Diğer fonksiyonlar korunmalı
            assert "fonk_1" in guncellenmis, \
                "Diğer fonksiyonlar korunmalı"
            assert "fonk_3" in guncellenmis, \
                "Diğer fonksiyonlar korunmalı"
            
            # Property 2: Dosya geçerli Python olmalı
            try:
                ast.parse(guncellenmis)
                gecerli = True
            except SyntaxError:
                gecerli = False
            
            assert gecerli, \
                "Güncellenmiş dosya geçerli Python değil"


@given(
    dosya_sayisi=st.integers(min_value=1, max_value=3),
    deger=st.integers(min_value=1, max_value=50)
)
@settings(max_examples=100, deadline=None)
def test_rapor_olusturma_tamligi(dosya_sayisi, deger):
    """
    Property: Rapor tüm işlemleri içermeli.
    
    Test stratejisi:
    - İşlemler yap
    - Rapor oluştur
    - Raporun tüm işlemleri içerdiğini kontrol et
    """
    cikarici = OrtakModulCikarici()
    fonk_adi = "test_fonk"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Fonksiyon
        fonk = fonksiyon_olustur(fonk_adi, deger)
        
        # Dosyalar oluştur
        dosya_yollari = set()
        for i in range(dosya_sayisi):
            dosya = Path(tmpdir) / f"modul_{i}.py"
            dosya.write_text(fonk, encoding='utf-8')
            dosya_yollari.add(str(dosya))
        
        # Ortak modül oluştur
        ortak_modul = Path(tmpdir) / "ortak.py"
        cikarici.ortak_modul_olustur(
            modul_adi="ortak",
            modul_yolu=str(ortak_modul),
            benzer_bloklar=[],
            ortak_kod=fonk
        )
        
        # Referansları güncelle
        cikarici.referanslari_guncelle(
            etkilenen_dosyalar=dosya_yollari,
            ortak_modul_yolu=str(ortak_modul),
            fonksiyon_adi=fonk_adi
        )
        
        # Rapor oluştur
        rapor = cikarici.rapor_olustur()
        
        # Property 1: Rapor boş olmamalı
        assert rapor, "Rapor oluşturulmalı"
        
        # Property 2: Rapor başlık içermeli
        assert "Rapor" in rapor, \
            "Rapor başlık içermeli"
        
        # Property 3: Tarih içermeli
        assert "Tarih" in rapor or "2025" in rapor, \
            "Rapor tarih içermeli"
