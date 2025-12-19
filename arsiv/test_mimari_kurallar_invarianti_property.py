# Version: 0.1.0
# Last Update: 2025-12-17
# Module: test_mimari_kurallar_invarianti_property
# Description: Mimari kurallar invariantı property testi
# Changelog:
# - İlk versiyon: Property 11 testi oluşturuldu

"""
**Feature: kod-kalitesi-standardizasyon, Property 11: Mimari Kurallar Invariantı**

Mimari düzenleme işlemi tamamlandığında, tüm katmanlar mimari kurallara uymalıdır.
**Validates: Requirements 3.5**
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


class TestMimariKurallarInvarianti:
    """Mimari kurallar invariantı property testleri"""
    
    def setup_method(self):
        """Her test öncesi çalışır"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_proje_yolu = Path(self.temp_dir) / "test_proje"
        self.test_proje_yolu.mkdir(parents=True)
        
        # Test için __init__.py oluştur
        (self.test_proje_yolu / "__init__.py").write_text("")
        
        # Katman klasörlerini oluştur
        self._katman_yapisini_olustur()
    
    def teardown_method(self):
        """Her test sonrası çalışır"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _katman_yapisini_olustur(self):
        """Test için katmanlı mimari yapısını oluşturur"""
        # UI katmanı
        ui_klasor = self.test_proje_yolu / "ui"
        ui_klasor.mkdir()
        (ui_klasor / "__init__.py").write_text("")
        
        # Servis katmanı
        servis_klasor = self.test_proje_yolu / "servisler"
        servis_klasor.mkdir()
        (servis_klasor / "__init__.py").write_text("")
        
        # Repository katmanı
        repo_klasor = self.test_proje_yolu / "repositories"
        repo_klasor.mkdir()
        (repo_klasor / "__init__.py").write_text("")
        
        # Database katmanı
        db_klasor = self.test_proje_yolu / "database"
        db_klasor.mkdir()
        (db_klasor / "__init__.py").write_text("")
    
    def _mimari_ihlalli_dosya_olustur(
        self, 
        dosya_yolu: Path, 
        katman: str,
        ihlal_turu: str
    ):
        """Mimari ihlali içeren dosya oluşturur"""
        satirlar = []
        satirlar.append(f"# {katman} katmanı dosyası")
        satirlar.append("")
        
        if ihlal_turu == "ui_repository_import":
            # UI katmanı repository import ediyor (yasak)
            satirlar.append("from ..repositories.user_repository import UserRepository")
            satirlar.append("")
            satirlar.append("class UserUI:")
            satirlar.append("    def __init__(self):")
            satirlar.append("        self.repo = UserRepository()  # Mimari ihlali")
            satirlar.append("")
            satirlar.append("    def show_users(self):")
            satirlar.append("        users = self.repo.get_all()")
            satirlar.append("        return users")
        
        elif ihlal_turu == "ui_database_import":
            # UI katmanı database import ediyor (yasak)
            satirlar.append("from ..database.models import User")
            satirlar.append("")
            satirlar.append("class UserUI:")
            satirlar.append("    def show_user(self, user_id):")
            satirlar.append("        user = User.query.get(user_id)  # Mimari ihlali")
            satirlar.append("        return user")
        
        elif ihlal_turu == "servis_ui_import":
            # Servis katmanı UI import ediyor (yasak)
            satirlar.append("from ..ui.user_ui import UserUI")
            satirlar.append("")
            satirlar.append("class UserService:")
            satirlar.append("    def __init__(self):")
            satirlar.append("        self.ui = UserUI()  # Mimari ihlali")
        
        elif ihlal_turu == "repository_servis_import":
            # Repository katmanı servis import ediyor (yasak)
            satirlar.append("from ..servisler.user_service import UserService")
            satirlar.append("")
            satirlar.append("class UserRepository:")
            satirlar.append("    def __init__(self):")
            satirlar.append("        self.service = UserService()  # Mimari ihlali")
        
        else:
            # Geçerli katman yapısı
            satirlar.append("class ValidClass:")
            satirlar.append("    def __init__(self):")
            satirlar.append("        pass")
            satirlar.append("")
            satirlar.append("    def valid_method(self):")
            satirlar.append("        return True")
        
        dosya_yolu.write_text('\n'.join(satirlar), encoding='utf-8')
    
    @given(
        ihlal_sayisi=st.integers(min_value=1, max_value=3)
    )
    @settings(max_examples=50, deadline=30000)
    def test_refactoring_sonrasi_mimari_kurallar_korunur(self, ihlal_sayisi: int):
        """
        Property 11: Mimari Kurallar Invariantı
        
        For any mimari düzenleme işlemi tamamlandığında, 
        tüm katmanlar mimari kurallara uymalıdır.
        """
        # Arrange: Mimari ihlalleri içeren dosyalar oluştur
        ihlal_turleri = [
            "ui_repository_import",
            "ui_database_import", 
            "servis_ui_import"
        ]
        
        for i in range(min(ihlal_sayisi, len(ihlal_turleri))):
            ihlal_turu = ihlal_turleri[i]
            
            if ihlal_turu.startswith("ui_"):
                dosya_yolu = self.test_proje_yolu / "ui" / f"ihlalli_ui_{i}.py"
                katman = "UI"
            elif ihlal_turu.startswith("servis_"):
                dosya_yolu = self.test_proje_yolu / "servisler" / f"ihlalli_servis_{i}.py"
                katman = "Servis"
            else:
                dosya_yolu = self.test_proje_yolu / "repositories" / f"ihlalli_repo_{i}.py"
                katman = "Repository"
            
            self._mimari_ihlalli_dosya_olustur(dosya_yolu, katman, ihlal_turu)
        
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
        
        # Assert: Mimari kurallar korunmalı
        self._mimari_kurallari_kontrol_et()
    
    def _mimari_kurallari_kontrol_et(self):
        """Mimari kuralların korunduğunu kontrol eder"""
        # UI katmanı dosyalarını kontrol et
        ui_klasor = self.test_proje_yolu / "ui"
        if ui_klasor.exists():
            for py_dosya in ui_klasor.rglob('*.py'):
                if py_dosya.name == '__init__.py':
                    continue
                
                icerik = py_dosya.read_text(encoding='utf-8')
                
                # UI katmanı repository import etmemeli
                assert "from ..repositories" not in icerik, (
                    f"UI dosyası {py_dosya.name} repository import ediyor"
                )
                
                # UI katmanı database import etmemeli
                assert "from ..database" not in icerik, (
                    f"UI dosyası {py_dosya.name} database import ediyor"
                )
        
        # Servis katmanı dosyalarını kontrol et
        servis_klasor = self.test_proje_yolu / "servisler"
        if servis_klasor.exists():
            for py_dosya in servis_klasor.rglob('*.py'):
                if py_dosya.name == '__init__.py':
                    continue
                
                icerik = py_dosya.read_text(encoding='utf-8')
                
                # Servis katmanı UI import etmemeli
                assert "from ..ui" not in icerik, (
                    f"Servis dosyası {py_dosya.name} UI import ediyor"
                )
        
        # Repository katmanı dosyalarını kontrol et
        repo_klasor = self.test_proje_yolu / "repositories"
        if repo_klasor.exists():
            for py_dosya in repo_klasor.rglob('*.py'):
                if py_dosya.name == '__init__.py':
                    continue
                
                icerik = py_dosya.read_text(encoding='utf-8')
                
                # Repository katmanı servis import etmemeli
                assert "from ..servisler" not in icerik, (
                    f"Repository dosyası {py_dosya.name} servis import ediyor"
                )
                
                # Repository katmanı UI import etmemeli
                assert "from ..ui" not in icerik, (
                    f"Repository dosyası {py_dosya.name} UI import ediyor"
                )
    
    def test_gecerli_mimari_yapisi_korunur(self):
        """
        Geçerli mimari yapısı refactoring sonrası korunmalı
        """
        # Arrange: Geçerli mimari yapısı oluştur
        
        # UI dosyası - sadece servis import eder
        ui_dosya = self.test_proje_yolu / "ui" / "user_ui.py"
        ui_icerik = '''# UI katmanı dosyası
from ..servisler.user_service import UserService

class UserUI:
    def __init__(self):
        self.service = UserService()  # Geçerli
    
    def show_users(self):
        return self.service.get_all_users()
'''
        ui_dosya.write_text(ui_icerik, encoding='utf-8')
        
        # Servis dosyası - repository import eder
        servis_dosya = self.test_proje_yolu / "servisler" / "user_service.py"
        servis_icerik = '''# Servis katmanı dosyası
from ..repositories.user_repository import UserRepository

class UserService:
    def __init__(self):
        self.repo = UserRepository()  # Geçerli
    
    def get_all_users(self):
        return self.repo.find_all()
'''
        servis_dosya.write_text(servis_icerik, encoding='utf-8')
        
        # Repository dosyası - database import eder
        repo_dosya = self.test_proje_yolu / "repositories" / "user_repository.py"
        repo_icerik = '''# Repository katmanı dosyası
from ..database.models import User

class UserRepository:
    def find_all(self):
        return User.query.all()  # Geçerli
'''
        repo_dosya.write_text(repo_icerik, encoding='utf-8')
        
        # Database dosyası
        db_dosya = self.test_proje_yolu / "database" / "models.py"
        db_icerik = '''# Database katmanı dosyası

class User:
    def __init__(self, name):
        self.name = name
    
    @classmethod
    def query(cls):
        return cls
    
    @classmethod
    def all(cls):
        return []
'''
        db_dosya.write_text(db_icerik, encoding='utf-8')
        
        orkestratori = RefactoringOrkestratori(
            proje_yolu=str(self.test_proje_yolu),
            backup_klasoru=str(Path(self.temp_dir) / "backup")
        )
        
        # Act
        rapor = orkestratori.tam_refactoring_yap(
            hedef_klasorler=[str(self.test_proje_yolu)],
            kullanici_onayı_gerekli=False
        )
        
        # Assert: Geçerli yapı korunmalı
        assert ui_dosya.exists() or any(
            "UserUI" in f.read_text(encoding='utf-8') 
            for f in self.test_proje_yolu.rglob('*.py')
            if f.name != '__init__.py'
        )
        
        assert servis_dosya.exists() or any(
            "UserService" in f.read_text(encoding='utf-8') 
            for f in self.test_proje_yolu.rglob('*.py')
            if f.name != '__init__.py'
        )
        
        # Mimari kurallar hala geçerli olmalı
        self._mimari_kurallari_kontrol_et()
    
    def test_tek_katman_ihlali_duzeltilir(self):
        """
        Tek katman ihlali düzeltilmeli
        """
        # Arrange: UI katmanında repository import ihlali
        ui_dosya = self.test_proje_yolu / "ui" / "ihlalli_ui.py"
        self._mimari_ihlalli_dosya_olustur(
            ui_dosya, "UI", "ui_repository_import"
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
        
        # Assert: İhlal düzeltilmeli
        self._mimari_kurallari_kontrol_et()
    
    def test_bos_katmanlar_sorun_cikarmiyor(self):
        """
        Boş katmanlar refactoring sonrası sorun çıkarmamalı
        """
        # Arrange: Sadece boş katman klasörleri
        orkestratori = RefactoringOrkestratori(
            proje_yolu=str(self.test_proje_yolu),
            backup_klasoru=str(Path(self.temp_dir) / "backup")
        )
        
        # Act
        rapor = orkestratori.tam_refactoring_yap(
            hedef_klasorler=[str(self.test_proje_yolu)],
            kullanici_onayı_gerekli=False
        )
        
        # Assert: Başarılı olmalı
        assert rapor.durum == RefactoringSonucu.BASARILI
        
        # Katman klasörleri hala var olmalı
        assert (self.test_proje_yolu / "ui").exists()
        assert (self.test_proje_yolu / "servisler").exists()
        assert (self.test_proje_yolu / "repositories").exists()
        assert (self.test_proje_yolu / "database").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])