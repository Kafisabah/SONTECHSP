# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_katman_sinirlari_invarianti_property
# Description: Katman sınırları invariantı property testi
# Changelog:
# - İlk versiyon: Property 9 testi oluşturuldu

"""
**Feature: kod-kalitesi-standardizasyon, Property 9: Katman Sınırları Invariantı**
**Validates: Requirements 3.3**

Property: For any import düzenlemesi işlemi, katman sınırları korunmalıdır.
"""

import tempfile
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from uygulama.moduller.kod_kalitesi.refactoring.import_duzenleyici import (
    ImportDuzenleyici, KatmanTuru
)


def dosya_icerik_olustur(katman: KatmanTuru, import_satirlari: list) -> str:
    """Test dosyası içeriği oluşturur"""
    icerik_parcalari = [
        "# Test dosyası",
        ""
    ]
    
    # Import'ları ekle
    icerik_parcalari.extend(import_satirlari)
    icerik_parcalari.append("")
    
    # Basit bir fonksiyon ekle
    icerik_parcalari.append("def test_fonksiyon():")
    icerik_parcalari.append("    pass")
    
    return '\n'.join(icerik_parcalari)


@given(
    import_sayisi=st.integers(min_value=1, max_value=5)
)
@settings(max_examples=100, deadline=None)
def test_katman_sinirlari_invarianti(import_sayisi):
    """
    **Feature: kod-kalitesi-standardizasyon, Property 9: Katman Sınırları Invariantı**
    **Validates: Requirements 3.3**
    
    Property: Import düzenlemesi sonrasında, katman sınırları korunmalıdır.
    UI katmanı sadece servis katmanını import edebilir.
    
    Test stratejisi:
    - UI katmanında bir dosya oluştur
    - Çeşitli import'lar ekle (bazıları ihlal içerir)
    - Import düzenleyiciyi çalıştır
    - Düzenleme sonrası sadece izin verilen import'ların kaldığını doğrula
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # UI katmanında bir dosya oluştur
        ui_klasor = Path(temp_dir) / "arayuz"
        ui_klasor.mkdir()
        
        # Test import'ları oluştur
        test_importlari = []
        
        # İzin verilen import'lar (servis katmanı)
        for i in range(import_sayisi):
            test_importlari.append(f"from uygulama.servisler import servis_{i}")
        
        # İhlal eden import'lar (repository katmanı - UI'dan yasak)
        test_importlari.append("from uygulama.depolar import depo_1")
        test_importlari.append("from uygulama.veritabani import model_1")
        
        # Dosya içeriğini oluştur
        dosya_icerik = dosya_icerik_olustur(KatmanTuru.UI, test_importlari)
        
        # Dosyayı yaz
        test_dosya = ui_klasor / "test_ekran.py"
        test_dosya.write_text(dosya_icerik, encoding='utf-8')
        
        # Import düzenleyiciyi çalıştır
        duzenleyici = ImportDuzenleyici()
        plan = duzenleyici.import_yapisini_duzenle(str(test_dosya))
        
        # Property 1: Katman doğru tespit edilmeli
        assert plan.katman == KatmanTuru.UI, (
            f"Katman yanlış tespit edildi: {plan.katman}"
        )
        
        # Property 2: İhlaller tespit edilmeli
        assert len(plan.ihlaller) > 0, (
            "Repository ve database import'ları ihlal olarak tespit edilmedi"
        )
        
        # Property 3: Yeni import'larda ihlal olmamalı
        for yeni_import in plan.yeni_importlar:
            if not yeni_import.strip():
                continue
            
            # Repository veya database katmanından import olmamalı
            # 'depolar' veya 'veritabani' klasörlerinden import kontrolü
            assert '.depolar' not in yeni_import.lower() and 'from uygulama.depolar' not in yeni_import.lower(), (
                f"İhlal eden repository import düzeltilmedi: {yeni_import}"
            )
            assert '.veritabani' not in yeni_import.lower() and 'from uygulama.veritabani' not in yeni_import.lower(), (
                f"İhlal eden database import düzeltilmedi: {yeni_import}"
            )


@given(
    servis_import_sayisi=st.integers(min_value=1, max_value=3)
)
@settings(max_examples=100, deadline=None)
def test_servis_katmani_ui_import_edemez(servis_import_sayisi):
    """
    Property: Servis katmanı UI katmanını import edemez.
    
    Test stratejisi:
    - Servis katmanında bir dosya oluştur
    - UI import'ları ekle (ihlal)
    - Import düzenleyiciyi çalıştır
    - UI import'larının kaldırıldığını doğrula
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Servis katmanında bir dosya oluştur
        servis_klasor = Path(temp_dir) / "servisler"
        servis_klasor.mkdir()
        
        # Test import'ları oluştur
        test_importlari = []
        
        # İzin verilen import'lar (repository katmanı)
        for i in range(servis_import_sayisi):
            test_importlari.append(f"from uygulama.depolar import depo_{i}")
        
        # İhlal eden import (UI katmanı - servis'ten yasak)
        test_importlari.append("from uygulama.arayuz import ekran_1")
        
        # Dosya içeriğini oluştur
        dosya_icerik = dosya_icerik_olustur(KatmanTuru.SERVIS, test_importlari)
        
        # Dosyayı yaz
        test_dosya = servis_klasor / "test_servis.py"
        test_dosya.write_text(dosya_icerik, encoding='utf-8')
        
        # Import düzenleyiciyi çalıştır
        duzenleyici = ImportDuzenleyici()
        plan = duzenleyici.import_yapisini_duzenle(str(test_dosya))
        
        # Property: UI import'u kaldırılmalı
        for yeni_import in plan.yeni_importlar:
            if not yeni_import.strip():
                continue
            
            assert 'arayuz' not in yeni_import.lower(), (
                f"UI import'u kaldırılmadı: {yeni_import}"
            )
            assert 'ui' not in yeni_import.lower(), (
                f"UI import'u kaldırılmadı: {yeni_import}"
            )
