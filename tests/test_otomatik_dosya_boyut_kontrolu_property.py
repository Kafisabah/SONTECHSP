# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_otomatik_dosya_boyut_kontrolu_property
# Description: Property test - Otomatik dosya boyut kontrolü
# Changelog:
# - İlk versiyon: Property 28 testi oluşturuldu

"""
**Feature: kod-kalitesi-standardizasyon, Property 28: Otomatik Dosya Boyut Kontrolü**
**Validates: Requirements 8.1**

Property: For any refactoring araçları çalıştırma işlemi, 
dosya boyut kontrollerinin otomatik yapılması gerekir
"""

import tempfile
import shutil
from pathlib import Path
from hypothesis import given, strategies as st, settings

from uygulama.moduller.kod_kalitesi.otomatik_kontrol_sistemi import (
    OtomatikKontrolSistemi
)


@st.composite
def dosya_icerigi_stratejisi(draw):
    """Rastgele Python dosya içeriği üretir"""
    kod_satir_sayisi = draw(st.integers(min_value=50, max_value=200))
    
    satirlar = []
    # Basit kod satırları (yorum/boş satır yok)
    for i in range(kod_satir_sayisi):
        satirlar.append(f"x{i} = {i}")
    
    return '\n'.join(satirlar), kod_satir_sayisi


@given(dosya_icerigi_stratejisi())
@settings(max_examples=100, deadline=None)
def test_otomatik_dosya_boyut_kontrolu_property(dosya_verisi):
    """
    Property: Otomatik kontrol sistemi çalıştırıldığında,
    dosya boyut kontrolü otomatik yapılmalıdır.
    """
    icerik, kod_satir_sayisi = dosya_verisi
    
    # Geçici dizin oluştur
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test dosyası oluştur
        test_dosya = Path(temp_dir) / "test_modul.py"
        test_dosya.write_text(icerik, encoding='utf-8')
        
        # Otomatik kontrol sistemi oluştur
        sistem = OtomatikKontrolSistemi(
            proje_yolu=temp_dir,
            dosya_limiti=120
        )
        
        # Tam kontrol yap
        rapor = sistem.tam_kontrol_yap()
        
        # Property: Dosya boyut kontrolü yapılmış olmalı
        # Eğer dosya 120 satırdan büyükse, ihlal tespit edilmeli
        if kod_satir_sayisi > 120:
            assert len(rapor.dosya_boyut_ihlalleri) > 0, (
                f"Dosya {kod_satir_sayisi} kod satırı ama ihlal tespit edilmedi"
            )
            
            # İhlal edilen dosya bizim test dosyamız olmalı
            ihlal_dosyalari = [
                ihlal.dosya_yolu for ihlal in rapor.dosya_boyut_ihlalleri
            ]
            assert any(
                'test_modul.py' in dosya for dosya in ihlal_dosyalari
            ), "Test dosyası ihlal listesinde değil"
        else:
            # 120 satır veya daha az ise, bu dosya için ihlal olmamalı
            ihlal_dosyalari = [
                ihlal.dosya_yolu for ihlal in rapor.dosya_boyut_ihlalleri
            ]
            test_dosyasi_ihlal = any(
                'test_modul.py' in dosya for dosya in ihlal_dosyalari
            )
            assert not test_dosyasi_ihlal, (
                f"Dosya {kod_satir_sayisi} kod satırı ama ihlal olarak işaretlendi"
            )


@given(st.integers(min_value=1, max_value=5))
@settings(max_examples=100, deadline=None)
def test_otomatik_kontrol_coklu_dosya_property(dosya_sayisi):
    """
    Property: Otomatik kontrol sistemi birden fazla dosyayı
    aynı anda kontrol edebilmelidir.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Birden fazla dosya oluştur
        for i in range(dosya_sayisi):
            dosya = Path(temp_dir) / f"modul_{i}.py"
            # Her dosyaya farklı satır sayısı
            satir_sayisi = 100 + (i * 30)
            satirlar = [f"x{j} = {j}" for j in range(satir_sayisi)]
            dosya.write_text('\n'.join(satirlar), encoding='utf-8')
        
        # Otomatik kontrol sistemi
        sistem = OtomatikKontrolSistemi(
            proje_yolu=temp_dir,
            dosya_limiti=120
        )
        
        # Tam kontrol yap
        rapor = sistem.tam_kontrol_yap()
        
        # Property: Sistem tüm dosyaları kontrol etmiş olmalı
        # 120 satırdan büyük dosyalar tespit edilmeli
        beklenen_ihlal_sayisi = sum(
            1 for i in range(dosya_sayisi) if (100 + i * 30) > 120
        )
        
        assert len(rapor.dosya_boyut_ihlalleri) == beklenen_ihlal_sayisi, (
            f"Beklenen {beklenen_ihlal_sayisi} ihlal, "
            f"bulunan {len(rapor.dosya_boyut_ihlalleri)}"
        )


def test_otomatik_kontrol_rapor_uretimi():
    """
    Property: Otomatik kontrol sistemi her zaman rapor üretmelidir.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Boş proje
        sistem = OtomatikKontrolSistemi(proje_yolu=temp_dir)
        
        # Tam kontrol yap
        rapor = sistem.tam_kontrol_yap()
        
        # Property: Rapor üretilmiş olmalı
        assert rapor is not None, "Rapor üretilmedi"
        assert hasattr(rapor, 'toplam_ihlal_sayisi'), "Rapor eksik"
        assert hasattr(rapor, 'basarili'), "Rapor eksik"
        
        # Metin raporu üret
        metin_rapor = sistem.rapor_uret(rapor)
        
        # Property: Metin raporu boş olmamalı
        assert metin_rapor, "Metin raporu boş"
        assert "KALİTE KONTROL RAPORU" in metin_rapor, "Rapor başlığı yok"
