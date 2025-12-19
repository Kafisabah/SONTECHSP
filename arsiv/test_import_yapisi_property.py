# Version: 0.1.0
# Last Update: 2025-12-17
# Module: tests.test_import_yapisi_property
# Description: Import yapısı analizörü property-based testleri
# Changelog:
# - İlk versiyon: Property testleri oluşturuldu

"""
**Feature: kod-kalitesi-standardizasyon, Property 8: UI Katmanı Import Kısıtlaması**

For any UI katmanındaki dosya, repository veya database katmanından 
import yapmamalıdır.

**Validates: Requirements 3.1**
"""

import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings

from uygulama.moduller.kod_kalitesi.analizorler.import_yapisi_analizoru import (
    ImportYapisiAnalizoru, KatmanTuru
)


@given(
    ui_import_sayisi=st.integers(min_value=0, max_value=5),
    servis_import_sayisi=st.integers(min_value=0, max_value=5),
    repository_import_sayisi=st.integers(min_value=0, max_value=3),
    database_import_sayisi=st.integers(min_value=0, max_value=3)
)
@settings(max_examples=100, deadline=None)
def test_ui_katmani_import_kisitlamasi(
    ui_import_sayisi,
    servis_import_sayisi,
    repository_import_sayisi,
    database_import_sayisi
):
    """
    Property: UI katmanı repository veya database katmanından import yapmamalı.
    
    Test stratejisi:
    - Rastgele import yapısı ile UI dosyası oluştur
    - Repository/database importları varsa ihlal tespit edilmeli
    - Servis importları ihlal sayılmamalı
    """
    analizor = ImportYapisiAnalizoru()
    
    # Geçici proje yapısı oluştur
    with tempfile.TemporaryDirectory() as tmpdir:
        proje = Path(tmpdir)
        
        # UI klasörü oluştur
        ui_klasor = proje / "arayuz"
        ui_klasor.mkdir()
        
        # UI dosyası oluştur
        ui_dosya = ui_klasor / "test_ekran.py"
        
        satirlar = []
        
        # UI importları ekle
        for i in range(ui_import_sayisi):
            satirlar.append(f"from arayuz.bilesenler import Bilesen{i}")
        
        # Servis importları ekle (izin verilen)
        for i in range(servis_import_sayisi):
            satirlar.append(f"from servisler.test_servis import Servis{i}")
        
        # Repository importları ekle (yasak)
        for i in range(repository_import_sayisi):
            satirlar.append(f"from depolar.test_depo import Depo{i}")
        
        # Database importları ekle (yasak)
        for i in range(database_import_sayisi):
            satirlar.append(f"from veritabani.modeller import Model{i}")
        
        satirlar.append("\nclass TestEkran:\n    pass")
        
        ui_dosya.write_text('\n'.join(satirlar), encoding='utf-8')
        
        # Mimari ihlalleri tespit et
        ihlaller = analizor.mimari_ihlalleri_tespit_et(str(proje))
        
        # Property: Repository veya database importu varsa ihlal olmalı
        beklenen_ihlal_sayisi = repository_import_sayisi + database_import_sayisi
        
        if beklenen_ihlal_sayisi > 0:
            assert len(ihlaller) > 0, \
                f"UI katmanı ihlali tespit edilmedi: {beklenen_ihlal_sayisi} ihlal bekleniyor"
            
            # Tüm ihlaller UI katmanı ihlali olmalı
            for ihlal in ihlaller:
                assert "UI" in ihlal.ihlal_turu or "KATMAN" in ihlal.ihlal_turu, \
                    f"Yanlış ihlal türü: {ihlal.ihlal_turu}"
        else:
            # Repository/database importu yoksa ihlal olmamalı
            ui_ihlalleri = [i for i in ihlaller if "UI" in i.ihlal_turu]
            assert len(ui_ihlalleri) == 0, \
                f"Yanlış ihlal tespiti: {len(ui_ihlalleri)} ihlal bulundu"
