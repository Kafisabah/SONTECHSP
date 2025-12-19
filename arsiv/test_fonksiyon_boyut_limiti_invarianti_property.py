# Version: 0.1.0
# Last Update: 2025-12-17
# Module: test_fonksiyon_boyut_limiti_invarianti_property
# Description: Fonksiyon boyut limiti invariantı property testi
# Changelog:
# - İlk versiyon: Property 7 testi oluşturuldu

"""
**Feature: kod-kalitesi-standardizasyon, Property 7: Fonksiyon Boyut Limiti Invariantı**

Refactoring işlemi tamamlandığında, tüm fonksiyonlar 25 satır limitini aşmamalıdır.
**Validates: Requirements 2.5**
"""

import os
import shutil
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings
import pytest
import ast

from sontechsp.uygulama.kod_kalitesi.refactoring_orkestratori import (
    RefactoringOrkestratori, RefactoringSonucu
)


class TestFonksiyonBoyutLimitiInvarianti:
    """Fonksiyon boyut limiti invariantı property testleri"""
    
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
    
    def _buyuk_fonksiyon_olustur(self, dosya_yolu: Path, fonksiyon_satir_sayisi: int):
        """Test için büyük fonksiyon içeren dosya oluşturur"""
        satirlar = []
        satirlar.append("# Test dosyası")
        satirlar.append("")
        satirlar.append("def buyuk_fonksiyon():")
        satirlar.append('    """Büyük test fonksiyonu"""')
        
        # Gereken satır sayısına kadar kod ekle
        for i in range(4, fonksiyon_satir_sayisi + 1):
            if i % 10 == 0:
                satirlar.append(f"    # İşlem {i}")
            else:
                satirlar.append(f"    sonuc_{i} = {i} * 2")
        
        satirlar.append("    return True")
        satirlar.append("")
        satirlar.append("def kucuk_fonksiyon():")
        satirlar.append('    """Küçük fonksiyon"""')
        satirlar.append("    return 42")
        
        dosya_yolu.write_text('\n'.join(satirlar), encoding='utf-8')
    
    def _coklu_buyuk_fonksiyon_olustur(
        self, 
        dosya_yolu: Path, 
        fonksiyon_sayisi: int,
        satir_sayilari: list
    ):
        """Test için birden fazla büyük fonksiyon içeren dosya oluşturur"""
        satirlar = []
        satirlar.append("# Test dosyası - çoklu fonksiyon")
        satirlar.append("")
        
        for i in range(min(fonksiyon_sayisi, len(satir_sayilari))):
            satirlar.append(f"def buyuk_fonksiyon_{i}():")
            satirlar.append(f'    """Büyük test fonksiyonu {i}"""')
            
            # Gereken satır sayısına kadar kod ekle
            for j in range(2, satir_sayilari[i]):
                if j % 8 == 0:
                    satirlar.append(f"    # Adım {j}")
                else:
                    satirlar.append(f"    x_{j} = {j} + {i}")
            
            satirlar.append("    return True")
            satirlar.append("")
        
        dosya_yolu.write_text('\n'.join(satirlar), encoding='utf-8')
    
    @given(
        fonksiyon_satir_sayisi=st.integers(min_value=26, max_value=50)
    )
    @settings(max_examples=100, deadline=30000)
    def test_refactoring_sonrasi_fonksiyon_boyut_limiti_korunur(
        self, 
        fonksiyon_satir_sayisi: int
    ):
        """
        Property 7: Fonksiyon Boyut Limiti Invariantı
        
        For any refactoring işlemi tamamlandığında, 
        tüm fonksiyonlar 25 satır limitini aşmamalıdır.
        """
        # Arrange: Büyük fonksiyon içeren dosya oluştur
        dosya_yolu = self.test_proje_yolu / "buyuk_fonksiyon_modulu.py"
        self._buyuk_fonksiyon_olustur(dosya_yolu, fonksiyon_satir_sayisi)
        
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
        
        # Assert: Tüm fonksiyonlar 25 satır limitini aşmamalı
        for py_dosya in self.test_proje_yolu.rglob('*.py'):
            if py_dosya.name == '__init__.py':
                continue  # __init__.py dosyalarını atla
            
            fonksiyon_boyutlari = self._dosyadaki_fonksiyon_boyutlarini_hesapla(py_dosya)
            
            for fonk_adi, satir_sayisi in fonksiyon_boyutlari.items():
                assert satir_sayisi <= 25, (
                    f"Fonksiyon {fonk_adi} ({py_dosya.name}) 25 satır limitini aşıyor: "
                    f"{satir_sayisi} satır"
                )
    
    @given(
        fonksiyon_sayisi=st.integers(min_value=2, max_value=4),
        satir_sayilari=st.lists(
            st.integers(min_value=26, max_value=40),
            min_size=2, max_size=4
        )
    )
    @settings(max_examples=50, deadline=30000)
    def test_coklu_buyuk_fonksiyon_refactoring(
        self, 
        fonksiyon_sayisi: int,
        satir_sayilari: list
    ):
        """
        Birden fazla büyük fonksiyon içeren dosya refactoring testi
        """
        # Arrange
        dosya_yolu = self.test_proje_yolu / "coklu_fonksiyon_modulu.py"
        self._coklu_buyuk_fonksiyon_olustur(
            dosya_yolu, fonksiyon_sayisi, satir_sayilari
        )
        
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
        
        # Assert: Tüm fonksiyonlar limit altında olmalı
        for py_dosya in self.test_proje_yolu.rglob('*.py'):
            if py_dosya.name == '__init__.py':
                continue
            
            fonksiyon_boyutlari = self._dosyadaki_fonksiyon_boyutlarini_hesapla(py_dosya)
            
            for fonk_adi, satir_sayisi in fonksiyon_boyutlari.items():
                assert satir_sayisi <= 25, (
                    f"Fonksiyon {fonk_adi} boyut limitini aşıyor: {satir_sayisi} satır"
                )
    
    def _dosyadaki_fonksiyon_boyutlarini_hesapla(self, dosya_yolu: Path) -> dict:
        """
        Dosyadaki tüm fonksiyonların boyutlarını hesaplar
        
        Returns:
            {fonksiyon_adi: satir_sayisi} dict'i
        """
        try:
            icerik = dosya_yolu.read_text(encoding='utf-8')
            agac = ast.parse(icerik)
            
            fonksiyon_boyutlari = {}
            
            for node in ast.walk(agac):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    satir_sayisi = self._fonksiyon_satir_sayisi_hesapla(node, icerik)
                    fonksiyon_boyutlari[node.name] = satir_sayisi
            
            return fonksiyon_boyutlari
            
        except Exception:
            return {}
    
    def _fonksiyon_satir_sayisi_hesapla(
        self, 
        fonksiyon_node: ast.FunctionDef, 
        dosya_icerik: str
    ) -> int:
        """Fonksiyonun gerçek kod satırlarını sayar"""
        baslangic = fonksiyon_node.lineno
        bitis = fonksiyon_node.end_lineno or baslangic
        
        satirlar = dosya_icerik.split('\n')
        fonksiyon_satirlari = satirlar[baslangic - 1:bitis]
        
        kod_satir_sayisi = 0
        coklu_yorum = False
        
        for satir in fonksiyon_satirlari:
            temiz_satir = satir.strip()
            
            if not temiz_satir:
                continue
            
            if '"""' in temiz_satir or "'''" in temiz_satir:
                tirnak_sayisi = temiz_satir.count('"""') + temiz_satir.count("'''")
                if tirnak_sayisi == 1:
                    coklu_yorum = not coklu_yorum
                    continue
                elif tirnak_sayisi == 2:
                    continue
            
            if coklu_yorum:
                continue
            
            if temiz_satir.startswith('#'):
                continue
            
            kod_satir_sayisi += 1
        
        return kod_satir_sayisi
    
    def test_zaten_kucuk_fonksiyonlar_degismez(self):
        """
        Zaten küçük fonksiyonlar refactoring sonrası değişmemeli
        """
        # Arrange: Küçük fonksiyonlar içeren dosya oluştur
        dosya_yolu = self.test_proje_yolu / "kucuk_fonksiyonlar.py"
        kucuk_icerik = '''# Küçük fonksiyonlar dosyası

def kucuk_fonksiyon_1():
    """İlk küçük fonksiyon"""
    return "test1"

def kucuk_fonksiyon_2():
    """İkinci küçük fonksiyon"""
    x = 42
    return x * 2

def kucuk_fonksiyon_3():
    """Üçüncü küçük fonksiyon"""
    liste = [1, 2, 3]
    return sum(liste)
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
        
        # Assert: Küçük fonksiyonlar korunmalı
        assert dosya_yolu.exists()
        yeni_icerik = dosya_yolu.read_text(encoding='utf-8')
        
        # Ana fonksiyon isimleri korunmalı
        assert "kucuk_fonksiyon_1" in yeni_icerik
        assert "kucuk_fonksiyon_2" in yeni_icerik
        assert "kucuk_fonksiyon_3" in yeni_icerik
        
        # Fonksiyon boyut limiti kontrolü
        fonksiyon_boyutlari = self._dosyadaki_fonksiyon_boyutlarini_hesapla(dosya_yolu)
        for fonk_adi, satir_sayisi in fonksiyon_boyutlari.items():
            assert satir_sayisi <= 25, f"Fonksiyon {fonk_adi} boyut limitini aşıyor"
    
    def test_sadece_buyuk_fonksiyonlar_bolunur(self):
        """
        Sadece büyük fonksiyonlar bölünmeli, küçükler dokunulmamalı
        """
        # Arrange: Karışık boyutlarda fonksiyonlar
        dosya_yolu = self.test_proje_yolu / "karisik_fonksiyonlar.py"
        karisik_icerik = '''# Karışık boyutlarda fonksiyonlar

def kucuk_fonksiyon():
    """Küçük fonksiyon - dokunulmamalı"""
    return "kucuk"

def buyuk_fonksiyon():
    """Büyük fonksiyon - bölünmeli"""
    # Bu fonksiyon 25 satırdan fazla
    x1 = 1
    x2 = 2
    x3 = 3
    x4 = 4
    x5 = 5
    x6 = 6
    x7 = 7
    x8 = 8
    x9 = 9
    x10 = 10
    x11 = 11
    x12 = 12
    x13 = 13
    x14 = 14
    x15 = 15
    x16 = 16
    x17 = 17
    x18 = 18
    x19 = 19
    x20 = 20
    x21 = 21
    x22 = 22
    x23 = 23
    return x23

def orta_fonksiyon():
    """Orta boyut fonksiyon"""
    a = 1
    b = 2
    c = 3
    return a + b + c
'''
        dosya_yolu.write_text(karisik_icerik, encoding='utf-8')
        
        orkestratori = RefactoringOrkestratori(
            proje_yolu=str(self.test_proje_yolu),
            backup_klasoru=str(Path(self.temp_dir) / "backup")
        )
        
        # Act
        rapor = orkestratori.tam_refactoring_yap(
            hedef_klasorler=[str(self.test_proje_yolu)],
            kullanici_onayı_gerekli=False
        )
        
        # Assert: Tüm fonksiyonlar limit altında olmalı
        for py_dosya in self.test_proje_yolu.rglob('*.py'):
            if py_dosya.name == '__init__.py':
                continue
            
            fonksiyon_boyutlari = self._dosyadaki_fonksiyon_boyutlarini_hesapla(py_dosya)
            
            for fonk_adi, satir_sayisi in fonksiyon_boyutlari.items():
                assert satir_sayisi <= 25, (
                    f"Fonksiyon {fonk_adi} boyut limitini aşıyor: {satir_sayisi} satır"
                )
        
        # Küçük fonksiyon hala mevcut olmalı
        tum_icerik = ""
        for py_dosya in self.test_proje_yolu.rglob('*.py'):
            if py_dosya.name != '__init__.py':
                tum_icerik += py_dosya.read_text(encoding='utf-8')
        
        assert "kucuk_fonksiyon" in tum_icerik
        assert "orta_fonksiyon" in tum_icerik


if __name__ == "__main__":
    pytest.main([__file__, "-v"])