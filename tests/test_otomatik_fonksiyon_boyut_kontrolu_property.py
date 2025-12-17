# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_otomatik_fonksiyon_boyut_kontrolu_property
# Description: Property test - Otomatik fonksiyon boyut kontrolü
# Changelog:
# - İlk versiyon: Property 29 testi oluşturuldu

"""
**Feature: kod-kalitesi-standardizasyon, Property 29: Otomatik Fonksiyon Boyut Kontrolü**
**Validates: Requirements 8.2**

Property: For any kod analizi işlemi, 
fonksiyon boyut kontrollerinin otomatik yapılması gerekir
"""

import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings

from uygulama.moduller.kod_kalitesi.otomatik_kontrol_sistemi import (
    OtomatikKontrolSistemi
)


@st.composite
def fonksiyon_icerigi_stratejisi(draw):
    """Rastgele fonksiyon içeriği üretir"""
    satir_sayisi = draw(st.integers(min_value=10, max_value=50))
    # Sadece ASCII küçük harfler kullan
    fonksiyon_adi = draw(st.text(
        alphabet='abcdefghijklmnopqrstuvwxyz',
        min_size=3,
        max_size=10
    ))
    
    satirlar = []
    satirlar.append(f"def {fonksiyon_adi}():")
    
    for i in range(satir_sayisi):
        satirlar.append(f"    x{i} = {i}")
    
    satirlar.append("    return True")
    
    return '\n'.join(satirlar), satir_sayisi + 2, fonksiyon_adi


@given(fonksiyon_icerigi_stratejisi())
@settings(max_examples=100, deadline=None)
def test_otomatik_fonksiyon_boyut_kontrolu_property(fonksiyon_verisi):
    """
    Property: Otomatik kontrol sistemi çalıştırıldığında,
    fonksiyon boyut kontrolü otomatik yapılmalıdır.
    """
    icerik, toplam_satir, fonksiyon_adi = fonksiyon_verisi
    
    # Geçici dizin oluştur
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test dosyası oluştur
        test_dosya = Path(temp_dir) / "test_modul.py"
        test_dosya.write_text(icerik, encoding='utf-8')
        
        # Otomatik kontrol sistemi oluştur
        sistem = OtomatikKontrolSistemi(
            proje_yolu=temp_dir,
            fonksiyon_limiti=25
        )
        
        # Tam kontrol yap
        rapor = sistem.tam_kontrol_yap()
        
        # Property: Fonksiyon boyut kontrolü yapılmış olmalı
        # Eğer fonksiyon 25 satırdan büyükse, ihlal tespit edilmeli
        if toplam_satir > 25:
            assert len(rapor.fonksiyon_boyut_ihlalleri) > 0, (
                f"Fonksiyon {toplam_satir} satır ama ihlal tespit edilmedi"
            )
            
            # İhlal edilen fonksiyon bizim test fonksiyonumuz olmalı
            ihlal_fonksiyonlari = [
                ihlal.fonksiyon_adi 
                for ihlal in rapor.fonksiyon_boyut_ihlalleri
            ]
            assert fonksiyon_adi in ihlal_fonksiyonlari, (
                f"Fonksiyon {fonksiyon_adi} ihlal listesinde değil"
            )
        else:
            # 25 satır veya daha az ise, bu fonksiyon için ihlal olmamalı
            ihlal_fonksiyonlari = [
                ihlal.fonksiyon_adi 
                for ihlal in rapor.fonksiyon_boyut_ihlalleri
            ]
            assert fonksiyon_adi not in ihlal_fonksiyonlari, (
                f"Fonksiyon {toplam_satir} satır ama ihlal olarak işaretlendi"
            )


@given(st.integers(min_value=1, max_value=5))
@settings(max_examples=100, deadline=None)
def test_otomatik_kontrol_coklu_fonksiyon_property(fonksiyon_sayisi):
    """
    Property: Otomatik kontrol sistemi birden fazla fonksiyonu
    aynı anda kontrol edebilmelidir.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Birden fazla fonksiyon içeren dosya oluştur
        satirlar = []
        beklenen_ihlal_sayisi = 0
        
        for i in range(fonksiyon_sayisi):
            satir_sayisi = 15 + (i * 10)
            satirlar.append(f"def fonksiyon_{i}():")
            
            for j in range(satir_sayisi):
                satirlar.append(f"    x{j} = {j}")
            
            satirlar.append("    return True")
            satirlar.append("")
            
            # 25 satırdan büyükse ihlal sayısını artır
            if satir_sayisi + 2 > 25:  # +2 def ve return için
                beklenen_ihlal_sayisi += 1
        
        dosya = Path(temp_dir) / "test_modul.py"
        dosya.write_text('\n'.join(satirlar), encoding='utf-8')
        
        # Otomatik kontrol sistemi
        sistem = OtomatikKontrolSistemi(
            proje_yolu=temp_dir,
            fonksiyon_limiti=25
        )
        
        # Tam kontrol yap
        rapor = sistem.tam_kontrol_yap()
        
        # Property: Sistem tüm fonksiyonları kontrol etmiş olmalı
        assert len(rapor.fonksiyon_boyut_ihlalleri) == beklenen_ihlal_sayisi, (
            f"Beklenen {beklenen_ihlal_sayisi} ihlal, "
            f"bulunan {len(rapor.fonksiyon_boyut_ihlalleri)}"
        )


def test_otomatik_kontrol_fonksiyon_ve_dosya_birlikte():
    """
    Property: Otomatik kontrol sistemi hem dosya hem de
    fonksiyon boyut kontrollerini birlikte yapabilmelidir.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Büyük dosya ve büyük fonksiyon içeren test
        satirlar = []
        
        # Büyük bir fonksiyon (30 satır)
        satirlar.append("def buyuk_fonksiyon():")
        for i in range(30):
            satirlar.append(f"    x{i} = {i}")
        satirlar.append("    return True")
        satirlar.append("")
        
        # Dosyayı 120 satırdan büyük yapmak için ek kod
        for i in range(100):
            satirlar.append(f"y{i} = {i}")
        
        dosya = Path(temp_dir) / "test_modul.py"
        dosya.write_text('\n'.join(satirlar), encoding='utf-8')
        
        # Otomatik kontrol sistemi
        sistem = OtomatikKontrolSistemi(
            proje_yolu=temp_dir,
            dosya_limiti=120,
            fonksiyon_limiti=25
        )
        
        # Tam kontrol yap
        rapor = sistem.tam_kontrol_yap()
        
        # Property: Hem dosya hem fonksiyon ihlali tespit edilmeli
        assert len(rapor.dosya_boyut_ihlalleri) > 0, "Dosya ihlali tespit edilmedi"
        assert len(rapor.fonksiyon_boyut_ihlalleri) > 0, (
            "Fonksiyon ihlali tespit edilmedi"
        )
        
        # Toplam ihlal sayısı doğru olmalı
        toplam = (
            len(rapor.dosya_boyut_ihlalleri) +
            len(rapor.fonksiyon_boyut_ihlalleri)
        )
        assert rapor.toplam_ihlal_sayisi >= toplam, (
            "Toplam ihlal sayısı yanlış hesaplanmış"
        )
