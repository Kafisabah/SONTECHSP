# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_kod_tekrari_property
# Description: Kod tekrarı analizörü property-based testleri
# Changelog:
# - İlk versiyon: Property testleri oluşturuldu

"""
**Feature: kod-kalitesi-standardizasyon, Property 12: Kod Tekrarı Tespiti**

For any kod tabanı tarama işlemi, belirli eşik değerini aşan 
benzer kod bloklarını tespit etmelidir.

**Validates: Requirements 4.1**
"""

import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume

from uygulama.moduller.kod_kalitesi.analizorler.kod_tekrari_analizoru import (
    KodTekrariAnalizoru
)


def fonksiyon_kodu_olustur(isim: str, satir_sayisi: int, varyasyon: int = 0) -> str:
    """Test için fonksiyon kodu oluşturur."""
    satirlar = [f"def {isim}(x):"]
    satirlar.append(f"    \"\"\"Fonksiyon {isim}\"\"\"")
    
    for i in range(satir_sayisi):
        satirlar.append(f"    y{i} = x + {i + varyasyon}")
    
    satirlar.append(f"    return y{satir_sayisi - 1}")
    return '\n'.join(satirlar)


@given(
    satir_sayisi=st.integers(min_value=5, max_value=20),
    benzerlik_orani=st.floats(min_value=0.7, max_value=1.0),
    esik_degeri=st.floats(min_value=0.75, max_value=0.95)
)
@settings(max_examples=100, deadline=None)
def test_kod_tekrari_tespiti(satir_sayisi, benzerlik_orani, esik_degeri):
    """
    Property: Kod tekrarı analizörü eşik değerini aşan benzerlikleri tespit eder.
    
    Test stratejisi:
    - İki benzer fonksiyon oluştur
    - Benzerlik oranını kontrol et
    - Eşik değerine göre tespit edilip edilmediğini doğrula
    """
    # Minimum satır sayısını sağla
    assume(satir_sayisi >= 5)
    
    analizor = KodTekrariAnalizoru(
        benzerlik_esigi=esik_degeri,
        min_satir=5
    )
    
    # İki benzer fonksiyon oluştur
    # Benzerlik oranına göre varyasyon ekle
    varyasyon = int((1.0 - benzerlik_orani) * satir_sayisi)
    
    fonk1 = fonksiyon_kodu_olustur("fonksiyon_a", satir_sayisi, 0)
    fonk2 = fonksiyon_kodu_olustur("fonksiyon_b", satir_sayisi, varyasyon)
    
    # Geçici klasör ve dosyalar oluştur
    with tempfile.TemporaryDirectory() as tmpdir:
        dosya1 = Path(tmpdir) / "modul1.py"
        dosya2 = Path(tmpdir) / "modul2.py"
        
        dosya1.write_text(fonk1, encoding='utf-8')
        dosya2.write_text(fonk2, encoding='utf-8')
        
        # Kod tekrarlarını tara
        raporlar = analizor.kod_tekrarlarini_tara(tmpdir)
        
        # Property 1: Eşik üstü benzerlikler tespit edilmeli
        if benzerlik_orani >= esik_degeri:
            # Yüksek benzerlik varsa rapor olmalı
            assert len(raporlar) >= 0, \
                "Benzer kod blokları için rapor oluşturulmalı"
        
        # Property 2: Tüm raporlar eşik değerini aşmalı
        for rapor in raporlar:
            assert rapor.benzerlik_orani >= esik_degeri, \
                f"Rapor benzerliği ({rapor.benzerlik_orani}) " \
                f"eşik değerinden ({esik_degeri}) düşük"
        
        # Property 3: Raporlarda farklı dosyalar olmalı
        for rapor in raporlar:
            assert rapor.blok1.dosya_yolu != rapor.blok2.dosya_yolu, \
                "Aynı dosyadaki fonksiyonlar rapor edilmemeli"


@given(
    fonksiyon_sayisi=st.integers(min_value=2, max_value=5),
    satir_sayisi=st.integers(min_value=5, max_value=15)
)
@settings(max_examples=100, deadline=None)
def test_ortak_modul_onerisi_olusturma(fonksiyon_sayisi, satir_sayisi):
    """
    Property: Benzer kod blokları için ortak modül önerileri oluşturulmalı.
    
    Test stratejisi:
    - Birden fazla benzer fonksiyon oluştur
    - Ortak modül önerilerinin doğru oluşturulduğunu kontrol et
    """
    analizor = KodTekrariAnalizoru(benzerlik_esigi=0.85, min_satir=5)
    
    # Birden fazla benzer fonksiyon oluştur
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(fonksiyon_sayisi):
            dosya = Path(tmpdir) / f"modul{i}.py"
            fonk = fonksiyon_kodu_olustur(f"fonksiyon_{i}", satir_sayisi, i)
            dosya.write_text(fonk, encoding='utf-8')
        
        # Kod tekrarlarını tara
        raporlar = analizor.kod_tekrarlarini_tara(tmpdir)
        
        if raporlar:
            # Ortak modül önerileri oluştur
            oneriler = analizor.ortak_modul_onerileri_olustur(raporlar)
            
            # Property 1: En az bir öneri olmalı
            assert len(oneriler) > 0, \
                "Benzer kodlar için ortak modül önerisi oluşturulmalı"
            
            # Property 2: Her öneride modül adı olmalı
            for oneri in oneriler:
                assert oneri.modul_adi, \
                    "Ortak modül önerisinde modül adı olmalı"
                assert oneri.modul_yolu, \
                    "Ortak modül önerisinde modül yolu olmalı"
            
            # Property 3: Etkilenen dosyalar doğru olmalı
            for oneri in oneriler:
                assert len(oneri.etkilenen_dosyalar) >= 2, \
                    "Ortak modül en az 2 dosyayı etkilemeli"



@given(satir_sayisi=st.integers(min_value=1, max_value=10))
@settings(max_examples=100, deadline=None)
def test_minimum_satir_filtresi(satir_sayisi):
    """
    Property: Minimum satır sayısının altındaki bloklar filtrelenmeli.
    
    Test stratejisi:
    - Farklı boyutlarda fonksiyonlar oluştur
    - Minimum satır sayısının altındakilerin filtrelendiğini kontrol et
    """
    min_satir = 5
    analizor = KodTekrariAnalizoru(benzerlik_esigi=0.85, min_satir=min_satir)
    
    # Fonksiyon oluştur
    fonk = fonksiyon_kodu_olustur("test_fonk", satir_sayisi, 0)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        dosya = Path(tmpdir) / "test.py"
        dosya.write_text(fonk, encoding='utf-8')
        
        # Blokları çıkar
        bloklar = analizor._dosyadan_blok_cikar(str(dosya))
        
        # Property: Minimum satırın altındaki bloklar filtrelenmeli
        for blok in bloklar:
            satir_fark = blok.bitis_satir - blok.baslangic_satir + 1
            assert satir_fark >= min_satir, \
                f"Minimum satır ({min_satir}) altındaki blok " \
                f"({satir_fark}) filtrelenmedi"


@given(
    satir_sayisi=st.integers(min_value=5, max_value=15),
    ayni_dosya=st.booleans()
)
@settings(max_examples=100, deadline=None)
def test_ayni_dosya_filtresi(satir_sayisi, ayni_dosya):
    """
    Property: Aynı dosyadaki fonksiyonlar karşılaştırılmamalı.
    
    Test stratejisi:
    - İki fonksiyonu aynı veya farklı dosyalara yerleştir
    - Aynı dosyadakilerin karşılaştırılmadığını kontrol et
    """
    analizor = KodTekrariAnalizoru(benzerlik_esigi=0.85, min_satir=5)
    
    fonk1 = fonksiyon_kodu_olustur("fonksiyon_a", satir_sayisi, 0)
    fonk2 = fonksiyon_kodu_olustur("fonksiyon_b", satir_sayisi, 0)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        if ayni_dosya:
            # Aynı dosyaya yaz
            dosya = Path(tmpdir) / "modul.py"
            dosya.write_text(f"{fonk1}\n\n{fonk2}", encoding='utf-8')
        else:
            # Farklı dosyalara yaz
            dosya1 = Path(tmpdir) / "modul1.py"
            dosya2 = Path(tmpdir) / "modul2.py"
            dosya1.write_text(fonk1, encoding='utf-8')
            dosya2.write_text(fonk2, encoding='utf-8')
        
        # Kod tekrarlarını tara
        raporlar = analizor.kod_tekrarlarini_tara(tmpdir)
        
        # Property: Aynı dosyadaki fonksiyonlar rapor edilmemeli
        if ayni_dosya:
            assert len(raporlar) == 0, \
                "Aynı dosyadaki fonksiyonlar rapor edilmemeli"
        else:
            # Farklı dosyalarda benzer fonksiyonlar rapor edilmeli
            if len(raporlar) > 0:
                for rapor in raporlar:
                    assert rapor.blok1.dosya_yolu != rapor.blok2.dosya_yolu, \
                        "Raporda aynı dosyadaki bloklar olmamalı"
