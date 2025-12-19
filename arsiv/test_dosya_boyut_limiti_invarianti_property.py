# Version: 0.1.0
# Last Update: 2025-12-17
# Module: test_dosya_boyut_limiti_invarianti_property
# Description: Dosya boyut limiti invariantı property testi
# Changelog:
# - İlk versiyon: Property 4 testi oluşturuldu

"""
**Feature: kod-kalitesi-standardizasyon, Property 4: Dosya Boyut Limiti Invariantı**

Refactoring işlemi tamamlandığında, tüm dosyalar 120 satır limitini aşmamalıdır.
**Validates: Requirements 1.5**
"""

import os
import shutil
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings
import pytest

from sontechsp.uygulama.kod_kalitesi.refactoring_orkestratori import (
    RefactoringOrkestratori, RefactoringSonucu
)


class TestDosyaBoyutLimitiInvarianti:
    """Dosya boyut limiti invariantı property testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_proje_yolu = Path(self.temp_dir) / "test_proje"
        self.test_proje_yolu.mkdir(parents=True)
        
        # Test için __init__.py oluştur
        (self.test_proje_yolu / "__init__.py").write_text("")
    
    def teardown_method(self):
        """Her test sonrası çalışır"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _buyuk_dosya_olustur(self, dosya_yolu: Path, satir_sayisi: int):
        """Test için büyük dosya oluşturur"""
        satirlar = []
        satirlar.append("# Test dosyası")
        satirlar.append("def test_fonksiyon():")
        satirlar.append('    """Test fonksiyonu"""')
        
        # Gereken satır sayısına kadar kod ekle
        for i in range(4, satir_sayisi + 1):
            if i % 10 == 0:
                satirlar.append(f"    # Satır {i}")
            else:
                satirlar.append(f"    x{i} = {i}")
        
        satirlar.append("    return True")
        
        dosya_yolu.write_text('\n'.join(satirlar), encoding='utf-8')
    
    @given(
        dosya_sayisi=st.integers(min_value=1, max_value=5),
        satir_sayilari=st.lists(
            st.integers(min_value=121, max_value=200),
            min_size=1, max_size=5
        )
    )
    @settings(max_examples=100, deadline=30000)
    def test_refactoring_sonrasi_dosya_boyut_limiti_korunur(
        self, 
        dosya_sayisi: int, 
        satir_sayilari: list
    ):
        """
        Property 4: Dosya Boyut Limiti Invariantı
        
        For any refactoring işlemi tamamlandığında, 
        tüm dosyalar 120 satır limitini aşmamalıdır.
        """
        # Arrange: Test dosyalarını oluştur
        dosya_yollari = []
        for i in range(min(dosya_sayisi, len(satir_sayilari))):
            dosya_yolu = self.test_proje_yolu / f"test_modul_{i}.py"
            self._buyuk_dosya_olustur(dosya_yolu, satir_sayilari[i])
            dosya_yollari.append(dosya_yolu)
        
        # Orkestratörü başlat
        orkestratori = RefactoringOrkestratori(
            proje_yolu=str(self.test_proje_yolu),
            backup_klasoru=str(Path(self.temp_dir) / "backup")
        )
        
        # Act: Refactoring işlemini yap
        rapor = orkestratori.tam_refactoring_yap(
            hedef_klasorler=[str(self.test_proje_yolu)],
            kullanici_onayı_gerekli=False
        )
        
        # Assert: Refactoring başarılı olmalı
        assert rapor.durum in [
            RefactoringSonucu.BASARILI, 
            RefactoringSonucu.KISMI_BASARILI
        ], f"Refactoring başarısız: {rapor.durum}"
        
        # Assert: Tüm Python dosyaları 120 satır limitini aşmamalı
        for py_dosya in self.test_proje_yolu.rglob('*.py'):
            if py_dosya.name == '__init__.py':
                continue  # __init__.py dosyalarını atla
            
            satir_sayisi = self._dosya_satir_sayisi_hesapla(py_dosya)
            assert satir_sayisi <= 120, (
                f"Dosya {py_dosya.name} 120 satır limitini aşıyor: "
                f"{satir_sayisi} satır"
            )
    
    def _dosya_satir_sayisi_hesapla(self, dosya_yolu: Path) -> int:
        """Dosyadaki gerçek kod satırlarını sayar"""
        try:
            icerik = dosya_yolu.read_text(encoding='utf-8')
            return self._yorum_satirlarini_filtrele(icerik)
        except Exception:
            return 0
    
    def _yorum_satirlarini_filtrele(self, icerik: str) -> int:
        """İçerikteki yorum ve boş satırları filtreler"""
        satirlar = icerik.split('\n')
        kod_satir_sayisi = 0
        coklu_yorum = False
        
        for satir in satirlar:
            temiz_satir = satir.strip()
            
            # Boş satırları atla
            if not temiz_satir:
                continue
            
            # Çoklu satır yorum kontrolü
            if '"""' in temiz_satir or "'''" in temiz_satir:
                tirnak_sayisi = temiz_satir.count('"""') + temiz_satir.count("'''")
                if tirnak_sayisi == 1:
                    coklu_yorum = not coklu_yorum
                    continue
                elif tirnak_sayisi == 2:
                    # Tek satırda açılıp kapanan docstring
                    continue
            
            # Çoklu yorum içindeyse atla
            if coklu_yorum:
                continue
            
            # Tek satır yorum kontrolü
            if temiz_satir.startswith('#'):
                continue
            
            # Gerçek kod satırı
            kod_satir_sayisi += 1
        
        return kod_satir_sayisi
    
    @given(
        satir_sayisi=st.integers(min_value=121, max_value=150)
    )
    @settings(max_examples=50, deadline=20000)
    def test_tek_dosya_refactoring_boyut_limiti(self, satir_sayisi: int):
        """
        Tek dosya refactoring sonrası boyut limiti kontrolü
        """
        # Arrange
        dosya_yolu = self.test_proje_yolu / "buyuk_modul.py"
        self._buyuk_dosya_olustur(dosya_yolu, satir_sayisi)
        
        orkestratori = RefactoringOrkestratori(
            proje_yolu=str(self.test_proje_yolu),
            backup_klasoru=str(Path(self.temp_dir) / "backup")
        )
        
        # Act
        rapor = orkestratori.tam_refactoring_yap(
            hedef_klasorler=[str(self.test_proje_yolu)],
            kullanici_onayı_gerekli=False
        )
        
        # Assert: Refactoring başarılı olmalı
        assert rapor.durum in [
            RefactoringSonucu.BASARILI, 
            RefactoringSonucu.KISMI_BASARILI
        ]
        
        # Assert: Tüm dosyalar limit altında olmalı
        for py_dosya in self.test_proje_yolu.rglob('*.py'):
            if py_dosya.name == '__init__.py':
                continue
            
            satir_sayisi = self._dosya_satir_sayisi_hesapla(py_dosya)
            assert satir_sayisi <= 120, (
                f"Dosya {py_dosya.name} boyut limitini aşıyor: {satir_sayisi} satır"
            )
    
    def test_zaten_kucuk_dosyalar_degismez(self):
        """
        Zaten küçük dosyalar refactoring sonrası değişmemeli
        """
        # Arrange: Küçük dosya oluştur
        dosya_yolu = self.test_proje_yolu / "kucuk_modul.py"
        kucuk_icerik = '''# Küçük test dosyası
def kucuk_fonksiyon():
    """Küçük fonksiyon"""
    return "test"

x = 42
'''
        dosya_yolu.write_text(kucuk_icerik, encoding='utf-8')
        
        orkestratori = RefactoringOrkestratori(
            proje_yolu=str(self.test_proje_yolu),
            backup_klasoru=str(Path(self.temp_dir) / "backup")
        )
        
        # Act
        rapor = orkestratori.tam_refactoring_yap(
            hedef_klasorler=[str(self.test_proje_yolu)],
            kullanici_onayı_gerekli=False
        )
        
        # Assert: Küçük dosya değişmemeli
        assert dosya_yolu.exists()
        yeni_icerik = dosya_yolu.read_text(encoding='utf-8')
        
        # Başlık eklenmiş olabilir, ama ana içerik korunmalı
        assert "kucuk_fonksiyon" in yeni_icerik
        assert 'return "test"' in yeni_icerik
        
        # Boyut limiti kontrolü
        satir_sayisi = self._dosya_satir_sayisi_hesapla(dosya_yolu)
        assert satir_sayisi <= 120
    
    def test_bos_proje_refactoring(self):
        """
        Boş proje refactoring sonrası sorun çıkarmamalı
        """
        # Arrange: Sadece __init__.py olan proje
        orkestratori = RefactoringOrkestratori(
            proje_yolu=str(self.test_proje_yolu),
            backup_klasoru=str(Path(self.temp_dir) / "backup")
        )
        
        # Act
        rapor = orkestratori.tam_refactoring_yap(
            hedef_klasorler=[str(self.test_proje_yolu)],
            kullanici_onayı_gerekli=False
        )
        
        # Assert: Başarılı olmalı (yapılacak bir şey olmasa da)
        assert rapor.durum == RefactoringSonucu.BASARILI
        
        # __init__.py hala var olmalı
        assert (self.test_proje_yolu / "__init__.py").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])