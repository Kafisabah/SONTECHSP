# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_otomatik_pep8_kontrolu_property
# Description: Property test - Otomatik PEP8 kontrolü
# Changelog:
# - İlk versiyon: Property 31 testi oluşturuldu

"""
**Feature: kod-kalitesi-standardizasyon, Property 31: Otomatik PEP8 Kontrolü**
**Validates: Requirements 8.4**

Property: For any kod kalitesi kontrol işlemi, 
PEP8 uyumluluğunun doğrulanması gerekir
"""

import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings

from uygulama.moduller.kod_kalitesi.pep8_kontrolcu import (
    PEP8Kontrolcu
)


@st.composite
def pep8_ihlal_senaryosu(draw):
    """Rastgele PEP8 ihlal senaryosu üretir"""
    # Uzun satır ihlali
    uzun_satir_var = draw(st.booleans())
    
    # Trailing whitespace ihlali
    trailing_whitespace_var = draw(st.booleans())
    
    # Normal kod satırları
    normal_satir_sayisi = draw(st.integers(min_value=5, max_value=20))
    
    return {
        'uzun_satir_var': uzun_satir_var,
        'trailing_whitespace_var': trailing_whitespace_var,
        'normal_satir_sayisi': normal_satir_sayisi
    }


@given(st.booleans())
@settings(max_examples=100, deadline=None)
def test_otomatik_pep8_kontrolu_property(uzun_satir_var):
    """
    Property: PEP8 kontrolcü çalıştırıldığında,
    PEP8 ihlalleri otomatik tespit edilmelidir.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        proje = Path(temp_dir)
        
        # Test dosyası oluştur
        test_dosya = proje / "test_modul.py"
        satirlar = []
        
        # Normal satırlar ekle
        for i in range(5):
            satirlar.append(f"x{i} = {i}")
        
        # Uzun satır ekle (ihlal)
        if uzun_satir_var:
            uzun_satir = "x = " + "a" * 150  # 120'den uzun
            satirlar.append(uzun_satir)
        
        test_dosya.write_text('\n'.join(satirlar), encoding='utf-8')
        
        # PEP8 kontrolcü oluştur
        kontrolcu = PEP8Kontrolcu(
            proje_yolu=str(proje),
            max_satir_uzunlugu=120
        )
        
        # Tam kontrol yap
        rapor = kontrolcu.tam_kontrol_yap()
        
        # Property: İhlaller otomatik tespit edilmeli
        if uzun_satir_var:
            assert len(rapor.ihlaller) > 0, (
                "PEP8 ihlali var ama tespit edilmedi"
            )
            assert not rapor.basarili, "İhlal var ama rapor başarılı"
        else:
            # İhlal yoksa, rapor başarılı olmalı
            assert rapor.basarili, (
                f"İhlal yok ama rapor başarısız: {len(rapor.ihlaller)} ihlal"
            )


@given(st.integers(min_value=100, max_value=200))
@settings(max_examples=100, deadline=None)
def test_pep8_satir_uzunlugu_tespiti_property(satir_uzunlugu):
    """
    Property: PEP8 kontrolcü, belirlenen limitten uzun
    satırları tespit etmelidir.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        proje = Path(temp_dir)
        
        # Test dosyası oluştur
        test_dosya = proje / "test_modul.py"
        
        # Belirli uzunlukta satır oluştur
        # "x = " 4 karakter, toplam satir_uzunlugu olacak şekilde
        if satir_uzunlugu > 4:
            satir = "x = " + "a" * (satir_uzunlugu - 4)
        else:
            satir = "a" * satir_uzunlugu
        
        test_dosya.write_text(satir, encoding='utf-8')
        
        # PEP8 kontrolcü (limit 120)
        kontrolcu = PEP8Kontrolcu(
            proje_yolu=str(proje),
            max_satir_uzunlugu=120
        )
        
        # Kontrol yap
        rapor = kontrolcu.tam_kontrol_yap()
        
        # Property: 120'den uzunsa ihlal olmalı
        if satir_uzunlugu > 120:
            assert len(rapor.ihlaller) > 0, (
                f"Satır {satir_uzunlugu} karakter ama ihlal tespit edilmedi"
            )
            
            # İhlal E501 olmalı (satır çok uzun)
            e501_ihlaller = [
                i for i in rapor.ihlaller if i.kod == 'E501'
            ]
            assert len(e501_ihlaller) > 0, "E501 ihlali tespit edilmedi"
        else:
            # 120 veya daha kısa ise ihlal olmamalı
            e501_ihlaller = [
                i for i in rapor.ihlaller if i.kod == 'E501'
            ]
            assert len(e501_ihlaller) == 0, (
                f"Satır {satir_uzunlugu} karakter ama ihlal var"
            )


@given(st.integers(min_value=1, max_value=5))
@settings(max_examples=100, deadline=None)
def test_pep8_coklu_dosya_kontrolu_property(dosya_sayisi):
    """
    Property: PEP8 kontrolcü birden fazla dosyayı
    aynı anda kontrol edebilmelidir.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        proje = Path(temp_dir)
        
        # Her dosyaya farklı ihlal ekle
        for i in range(dosya_sayisi):
            dosya = proje / f"modul_{i}.py"
            
            # Her dosyaya uzun satır ekle
            uzun_satir = "x = " + "a" * (130 + i * 10)
            dosya.write_text(uzun_satir, encoding='utf-8')
        
        # PEP8 kontrolcü
        kontrolcu = PEP8Kontrolcu(proje_yolu=str(proje))
        
        # Tam kontrol yap
        rapor = kontrolcu.tam_kontrol_yap()
        
        # Property: Tüm dosyalardaki ihlaller tespit edilmeli
        assert len(rapor.ihlaller) >= dosya_sayisi, (
            f"Beklenen en az {dosya_sayisi} ihlal, "
            f"bulunan {len(rapor.ihlaller)}"
        )
        
        # Kontrol edilen dosya sayısı doğru olmalı
        assert rapor.kontrol_edilen_dosya == dosya_sayisi, (
            f"Beklenen {dosya_sayisi} dosya, "
            f"kontrol edilen {rapor.kontrol_edilen_dosya}"
        )


def test_pep8_rapor_uretimi_property():
    """
    Property: PEP8 kontrolcü her zaman rapor üretmelidir.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        proje = Path(temp_dir)
        
        # İhlal içeren dosya
        test_dosya = proje / "test.py"
        test_dosya.write_text("x = " + "a" * 150, encoding='utf-8')
        
        # PEP8 kontrolcü
        kontrolcu = PEP8Kontrolcu(proje_yolu=str(proje))
        
        # Tam kontrol yap
        rapor = kontrolcu.tam_kontrol_yap()
        
        # Property: Rapor üretilmiş olmalı
        assert rapor is not None, "Rapor üretilmedi"
        assert hasattr(rapor, 'ihlaller'), "Rapor eksik"
        assert hasattr(rapor, 'basarili'), "Rapor eksik"
        
        # Metin raporu üret
        metin_rapor = kontrolcu.rapor_uret(rapor)
        
        # Property: Metin raporu boş olmamalı
        assert metin_rapor, "Metin raporu boş"
        assert "PEP8 UYUMLULUK RAPORU" in metin_rapor, "Rapor başlığı yok"
        
        # İhlal varsa, raporda görünmeli
        if len(rapor.ihlaller) > 0:
            assert "İHLAL" in metin_rapor, "İhlaller raporda yok"


def test_pep8_dosya_kontrolu_property():
    """
    Property: PEP8 kontrolcü tek dosya kontrolü yapabilmelidir.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        proje = Path(temp_dir)
        
        # Test dosyası
        test_dosya = proje / "test.py"
        test_dosya.write_text(
            "x = " + "a" * 150 + "\ny = 1   ",  # Uzun satır + trailing whitespace
            encoding='utf-8'
        )
        
        # PEP8 kontrolcü
        kontrolcu = PEP8Kontrolcu()
        
        # Tek dosya kontrolü
        ihlaller = kontrolcu.dosya_kontrolu(str(test_dosya))
        
        # Property: İhlaller tespit edilmeli
        assert len(ihlaller) >= 2, (
            f"Beklenen en az 2 ihlal, bulunan {len(ihlaller)}"
        )
        
        # E501 (uzun satır) olmalı
        e501_var = any(i.kod == 'E501' for i in ihlaller)
        assert e501_var, "E501 ihlali tespit edilmedi"
        
        # W291 (trailing whitespace) olmalı
        w291_var = any(i.kod == 'W291' for i in ihlaller)
        assert w291_var, "W291 ihlali tespit edilmedi"
