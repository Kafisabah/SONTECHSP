# SonTechSP - Geliştirici Dokümantasyonu

**Güncelleme Tarihi:** 18 Aralık 2025  
**Versiyon:** 2.0 (Refactoring Sonrası)  
**Hedef Kitle:** Yazılım Geliştiriciler  

---

## 📋 İçindekiler

1. [Proje Genel Bakış](#proje-genel-bakış)
2. [Yeni Modül Yapısı](#yeni-modül-yapısı)
3. [Import Yapısı Değişiklikleri](#import-yapısı-değişiklikleri)
4. [Best Practices](#best-practices)
5. [Geliştirme Ortamı Kurulumu](#geliştirme-ortamı-kurulumu)
6. [Kod Kalitesi Araçları](#kod-kalitesi-araçları)
7. [Test Stratejileri](#test-stratejileri)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Proje Genel Bakış

SonTechSP, Windows üzerinde çalışan, kurulabilir (installer), çoklu mağaza/şube destekli, çoklu PC eş zamanlı çalışabilen **POS + ERP + CRM** sistemidir.

### Teknoloji Stack
- **Backend:** Python 3.13+, FastAPI
- **Frontend:** PyQt6
- **Database:** PostgreSQL (ana), SQLite (POS offline cache)
- **ORM:** SQLAlchemy
- **Migration:** Alembic
- **Paketleme:** PyInstaller (Windows)

### Mimari Prensipler
```
UI (PyQt6) → Services → Repositories → Database
```

**Katman Kuralları:**
- UI katmanında iş kuralı YASAK
- DB erişimi sadece repository katmanında
- Çoklu PC stok tutarlılığı: PostgreSQL transaction + row-level lock
- Offline POS: SQLite kuyruk + senkron servis

---

## 🏗️ Yeni Modül Yapısı

Refactoring sonrası proje yapısı modüler hale getirilmiştir. Büyük monolitik dosyalar mantıklı gruplara bölünmüştür.

### Ana Dizin Yapısı
```
sontechsp/
├── uygulama/
│   ├── arayuz/
│   │   ├── ekranlar/
│   │   │   ├── ebelge/          # E-belge ekranı modülleri
│   │   │   ├── raporlar/        # Raporlar ekranı modülleri
│   │   │   └── ayarlar/         # Ayarlar ekranı modülleri
│   │   └── taban_ekran.py       # Temel UI sınıfları
│   ├── pos/
│   │   ├── repositories/
│   │   │   ├── satis_repository/      # Satış repository modülleri
│   │   │   ├── offline_kuyruk_repository/  # Offline kuyruk modülleri
│   │   │   └── iade_repository/       # İade repository modülleri
│   │   └── services/            # POS servis katmanı
│   ├── stok/                    # Stok yönetimi modülleri
│   ├── crm/                     # CRM modülleri
│   ├── cekirdek/                # Çekirdek sistem modülleri
│   └── database/                # Veritabanı modülleri
├── kod_kalitesi_araclari/       # Kod kalitesi araçları
└── tests/                       # Test dosyaları
```

### Modül Detayları

#### E-belge Ekranı Modülleri (`uygulama/arayuz/ekranlar/ebelge/`)
```
ebelge/
├── __init__.py              # Public API tanımları
├── ebelge_ana.py           # Ana koordinasyon sınıfı
├── ebelge_filtreleri.py    # Filtre işlemleri
├── ebelge_islemleri.py     # İş işlemleri
├── ebelge_durum.py         # Durum yönetimi
├── ebelge_tablolar.py      # Tablo işlemleri
└── ebelge_veri_yoneticisi.py  # Veri yönetimi
```

#### Raporlar Ekranı Modülleri (`uygulama/arayuz/ekranlar/raporlar/`)
```
raporlar/
├── __init__.py              # Public API tanımları
├── raporlar_ana.py         # Ana koordinasyon sınıfı
├── rapor_olusturma.py      # Rapor oluşturma
├── rapor_filtreleri.py     # Filtre yönetimi
├── rapor_export.py         # Export işlemleri
└── rapor_yardimcilar.py    # Yardımcı fonksiyonlar
```

#### Ayarlar Ekranı Modülleri (`uygulama/arayuz/ekranlar/ayarlar/`)
```
ayarlar/
├── __init__.py              # Public API tanımları
├── ayarlar.py              # Ana koordinasyon sınıfı
├── ayar_formlari.py        # Form yönetimi
├── ayar_butonlari.py       # Buton işlemleri
└── ayar_dogrulama.py       # Doğrulama kuralları
```

#### Repository Modülleri
```
repositories/
├── satis_repository/
│   ├── __init__.py
│   ├── satis_crud.py       # CRUD işlemleri
│   ├── satis_sorgular.py   # Sorgu işlemleri
│   └── satis_raporlar.py   # Rapor işlemleri
├── offline_kuyruk_repository/
│   ├── __init__.py
│   ├── kuyruk_islemleri.py    # Kuyruk işlemleri
│   ├── senkronizasyon.py      # Senkronizasyon
│   └── monitoring.py          # İzleme
└── iade_repository/
    ├── __init__.py
    ├── iade_crud.py        # İade CRUD
    ├── is_kurallari.py     # İş kuralları
    └── raporlar.py         # İade raporları
```

---

## 📦 Import Yapısı Değişiklikleri

Refactoring sonrası import yapısı değişmiştir. Aşağıdaki örnekleri takip edin.

### Eski Import Yapısı (❌ Kullanmayın)
```python
# ESKİ - Monolitik dosyalardan import
from uygulama.arayuz.ekranlar.ebelge import EbelgeEkrani
from uygulama.arayuz.ekranlar.raporlar import RaporlarEkrani
from uygulama.pos.repositories.satis_repository import SatisRepository
```

### Yeni Import Yapısı (✅ Kullanın)
```python
# YENİ - Modüler yapıdan import
from uygulama.arayuz.ekranlar.ebelge import EbelgeAnaEkrani
from uygulama.arayuz.ekranlar.ebelge.ebelge_filtreleri import EbelgeFiltreleri
from uygulama.arayuz.ekranlar.ebelge.ebelge_islemleri import EbelgeIslemleri

from uygulama.arayuz.ekranlar.raporlar import RaporlarAnaEkrani
from uygulama.arayuz.ekranlar.raporlar.rapor_olusturma import RaporOlusturucu

from uygulama.pos.repositories.satis_repository import SatisCRUD
from uygulama.pos.repositories.satis_repository.satis_sorgular import SatisSorgulari
```

### Public API Kullanımı
Her modül `__init__.py` dosyasında public API tanımlar:

```python
# uygulama/arayuz/ekranlar/ebelge/__init__.py
from .ebelge_ana import EbelgeAnaEkrani
from .ebelge_filtreleri import EbelgeFiltreleri
from .ebelge_islemleri import EbelgeIslemleri

__all__ = [
    'EbelgeAnaEkrani',
    'EbelgeFiltreleri', 
    'EbelgeIslemleri'
]
```

Bu sayede temiz import yapabilirsiniz:
```python
from uygulama.arayuz.ekranlar.ebelge import EbelgeAnaEkrani, EbelgeFiltreleri
```

### Import Best Practices

#### ✅ Doğru Kullanım
```python
# Spesifik sınıfları import edin
from uygulama.arayuz.ekranlar.ebelge import EbelgeAnaEkrani
from uygulama.pos.repositories.satis_repository import SatisCRUD

# Relative import (aynı paket içinde)
from .ebelge_filtreleri import EbelgeFiltreleri
from ..taban_ekran import TabanEkran
```

#### ❌ Yanlış Kullanım
```python
# Tüm modülü import etmeyin
import uygulama.arayuz.ekranlar.ebelge

# Wildcard import kullanmayın
from uygulama.arayuz.ekranlar.ebelge import *

# Katman sınırlarını ihlal etmeyin
from uygulama.database.models import SatisBelgesi  # UI'dan database'e doğrudan erişim YASAK
```

---

## 🎯 Best Practices

### Kod Yazma Kuralları

#### Dosya Yapısı
```python
# Version: 0.1.0
# Last Update: YYYY-MM-DD
# Module: module_name
# Description: Kısa açıklama
# Changelog:
# - İlk sürüm oluşturuldu

# Import'lar
from typing import Optional, List, Dict
from PyQt6.QtWidgets import QWidget

# Sınıf tanımları
class ExampleClass:
    """Sınıf dokümantasyonu"""
    
    def __init__(self):
        """Constructor dokümantasyonu"""
        pass
```

#### Kod Kalitesi Kuralları
- **Dosya boyutu:** Maksimum 120 satır (yorumlar hariç)
- **Fonksiyon boyutu:** Maksimum 25 satır
- **PEP8 uyumluluğu:** Zorunlu
- **Dokümantasyon:** Her sınıf ve public method için docstring

#### Naming Conventions
```python
# Sınıflar: PascalCase
class EbelgeAnaEkrani:
    pass

# Fonksiyonlar ve değişkenler: snake_case
def rapor_olustur():
    kullanici_adi = "test"

# Sabitler: UPPER_SNAKE_CASE
MAX_DOSYA_BOYUTU = 1024

# Private members: _underscore prefix
class MyClass:
    def __init__(self):
        self._private_var = None
        self.__very_private = None
```

### Mimari Kuralları

#### Katman Bağımlılıkları
```python
# ✅ Doğru katman bağımlılığı
class EbelgeEkrani(TabanEkran):  # UI katmanı
    def __init__(self):
        self.ebelge_servisi = self.servis_fabrikasi.ebelge_servisi()  # Service katmanı

class EbelgeServisi:  # Service katmanı
    def __init__(self, ebelge_repository):
        self.repository = ebelge_repository  # Repository katmanı

# ❌ Yanlış katman bağımlılığı
class EbelgeEkrani(TabanEkran):  # UI katmanı
    def __init__(self):
        self.repository = EbelgeRepository()  # Repository'ye doğrudan erişim YASAK
```

#### Dependency Injection
```python
# ✅ Constructor injection kullanın
class EbelgeServisi:
    def __init__(self, ebelge_repository: EbelgeRepository):
        self.repository = ebelge_repository

# ✅ Factory pattern kullanın
class ServisFabrikasi:
    def ebelge_servisi(self) -> EbelgeServisi:
        repository = self.ebelge_repository()
        return EbelgeServisi(repository)

# ❌ Doğrudan instantiation yapmayın
class EbelgeServisi:
    def __init__(self):
        self.repository = EbelgeRepository()  # YASAK
```

### Error Handling
```python
# ✅ Spesifik exception handling
try:
    sonuc = self.ebelge_servisi.belge_olustur(veri)
except EbelgeValidationError as e:
    self.hata_goster("Doğrulama Hatası", str(e))
except EbelgeServiceError as e:
    self.hata_goster("Servis Hatası", str(e))
except Exception as e:
    self.logger.error(f"Beklenmeyen hata: {e}")
    self.hata_goster("Sistem Hatası", "Beklenmeyen bir hata oluştu")

# ❌ Generic exception handling
try:
    sonuc = self.ebelge_servisi.belge_olustur(veri)
except Exception as e:
    print(f"Hata: {e}")  # YASAK
```

---

## 🛠️ Geliştirme Ortamı Kurulumu

### Gereksinimler
- Python 3.13+
- PostgreSQL 12+
- Git
- PyQt6
- Virtual environment (venv veya conda)

### Kurulum Adımları

#### 1. Repository Clone
```bash
git clone https://github.com/company/sontechsp.git
cd sontechsp
```

#### 2. Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

#### 3. Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Geliştirme araçları
```

#### 4. Database Setup
```bash
# PostgreSQL veritabanı oluştur
createdb sontechsp

# Migration'ları çalıştır
alembic upgrade head

# Test verilerini yükle (opsiyonel)
python scripts/load_test_data.py
```

#### 5. Konfigürasyon
```bash
# .env dosyasını oluştur
cp .env.example .env

# Gerekli ayarları düzenle
notepad .env
```

### IDE Konfigürasyonu

#### VS Code Ayarları (`.vscode/settings.json`)
```json
{
    "python.defaultInterpreter": "./venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.pylintEnabled": false,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=120"],
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

#### PyCharm Ayarları
- Code Style → Python → Line length: 120
- Tools → External Tools → Black formatter
- Inspections → Python → PEP8 coding style violation: Enable

---

## 🔧 Kod Kalitesi Araçları

### Otomatik Araçlar

#### 1. Code Formatting
```bash
# Black formatter
black --line-length=120 uygulama/

# isort (import sorting)
isort uygulama/
```

#### 2. Linting
```bash
# flake8
flake8 --max-line-length=120 --ignore=E501,W503 uygulama/

# pylint
pylint uygulama/
```

#### 3. Type Checking
```bash
# mypy
mypy uygulama/
```

#### 4. Security Scanning
```bash
# bandit
bandit -r uygulama/
```

### Pre-commit Hooks
`.pre-commit-config.yaml` dosyası:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        args: [--line-length=120]
  
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
        args: [--profile=black]
  
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
        args: [--max-line-length=120, --ignore=E501,W503]
```

Kurulum:
```bash
pip install pre-commit
pre-commit install
```

### Kod Kalitesi Metrikleri

#### Günlük Kontrol
```bash
# Kod kalitesi raporu oluştur
python kod_kalitesi_analiz.py

# Performans testi
python performans_dogrulama.py

# Mimari doğrulama
python mimari_dogrulama.py
```

#### CI/CD Pipeline
```yaml
# .github/workflows/quality.yml
name: Code Quality
on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.13
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run linting
        run: flake8 uygulama/
      - name: Run type checking
        run: mypy uygulama/
      - name: Run tests
        run: pytest tests/
```

---

## 🧪 Test Stratejileri

### Test Yapısı
```
tests/
├── unit/                    # Birim testler
│   ├── test_ebelge/
│   ├── test_raporlar/
│   └── test_repositories/
├── integration/             # Entegrasyon testler
│   ├── test_database/
│   └── test_services/
├── e2e/                     # End-to-end testler
│   └── test_ui_workflows/
└── fixtures/                # Test verileri
    └── sample_data.json
```

### Unit Test Örneği
```python
# tests/unit/test_ebelge/test_ebelge_filtreleri.py
import pytest
from unittest.mock import Mock, patch

from uygulama.arayuz.ekranlar.ebelge.ebelge_filtreleri import EbelgeFiltreleri


class TestEbelgeFiltreleri:
    
    @pytest.fixture
    def ebelge_filtreleri(self):
        """Test fixture"""
        return EbelgeFiltreleri()
    
    def test_tarih_filtresi_uygula(self, ebelge_filtreleri):
        """Tarih filtresi uygulama testi"""
        # Arrange
        baslangic_tarihi = "2024-01-01"
        bitis_tarihi = "2024-12-31"
        
        # Act
        sonuc = ebelge_filtreleri.tarih_filtresi_uygula(baslangic_tarihi, bitis_tarihi)
        
        # Assert
        assert sonuc is not None
        assert sonuc['baslangic'] == baslangic_tarihi
        assert sonuc['bitis'] == bitis_tarihi
    
    @patch('uygulama.arayuz.ekranlar.ebelge.ebelge_filtreleri.datetime')
    def test_varsayilan_tarih_araligi(self, mock_datetime, ebelge_filtreleri):
        """Varsayılan tarih aralığı testi"""
        # Arrange
        mock_datetime.now.return_value.strftime.return_value = "2024-12-18"
        
        # Act
        sonuc = ebelge_filtreleri.varsayilan_tarih_araligi()
        
        # Assert
        assert sonuc is not None
        mock_datetime.now.assert_called_once()
```

### Integration Test Örneği
```python
# tests/integration/test_services/test_ebelge_service.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from uygulama.database.models import Base
from uygulama.pos.services.ebelge_service import EbelgeService
from uygulama.pos.repositories.ebelge_repository import EbelgeRepository


class TestEbelgeServiceIntegration:
    
    @pytest.fixture(scope="class")
    def db_session(self):
        """Test veritabanı session'ı"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
    
    @pytest.fixture
    def ebelge_service(self, db_session):
        """EbelgeService test instance"""
        repository = EbelgeRepository(db_session)
        return EbelgeService(repository)
    
    def test_belge_olustur_ve_getir(self, ebelge_service):
        """Belge oluşturma ve getirme entegrasyon testi"""
        # Arrange
        belge_verisi = {
            'belge_no': 'TEST001',
            'tarih': '2024-12-18',
            'tutar': 100.0
        }
        
        # Act
        olusturulan_belge = ebelge_service.belge_olustur(belge_verisi)
        getirilen_belge = ebelge_service.belge_getir(olusturulan_belge.id)
        
        # Assert
        assert olusturulan_belge.id is not None
        assert getirilen_belge.belge_no == 'TEST001'
        assert getirilen_belge.tutar == 100.0
```

### Test Çalıştırma
```bash
# Tüm testler
pytest

# Spesifik test dosyası
pytest tests/unit/test_ebelge/test_ebelge_filtreleri.py

# Coverage raporu
pytest --cov=uygulama --cov-report=html

# Verbose output
pytest -v

# Sadece failed testler
pytest --lf
```

---

## 🔍 Troubleshooting

### Yaygın Sorunlar ve Çözümleri

#### 1. Import Hataları
**Sorun:** `ModuleNotFoundError: No module named 'uygulama.arayuz.ekranlar.ebelge'`

**Çözüm:**
```bash
# PYTHONPATH'i kontrol edin
echo $PYTHONPATH

# Proje root dizinini PYTHONPATH'e ekleyin
export PYTHONPATH="${PYTHONPATH}:/path/to/sontechsp"

# Veya __init__.py dosyalarının eksik olup olmadığını kontrol edin
find uygulama/ -name "__init__.py"
```

#### 2. Database Bağlantı Sorunları
**Sorun:** `sqlalchemy.exc.OperationalError: could not connect to server`

**Çözüm:**
```bash
# PostgreSQL servisinin çalıştığını kontrol edin
pg_ctl status

# Bağlantı ayarlarını kontrol edin
cat .env | grep DATABASE

# Test bağlantısı
python -c "
from uygulama.database.baglanti import test_connection
test_connection()
"
```

#### 3. PyQt6 Import Hataları
**Sorun:** `ImportError: No module named 'PyQt6'`

**Çözüm:**
```bash
# PyQt6'yı yeniden yükleyin
pip uninstall PyQt6
pip install PyQt6

# Sistem gereksinimlerini kontrol edin
python -c "
import sys
print(f'Python version: {sys.version}')
print(f'Platform: {sys.platform}')
"
```

#### 4. Refactoring Sonrası Çalışma Zamanı Hataları
**Sorun:** `AttributeError: 'EbelgeEkrani' object has no attribute 'filtre_grubu_olustur'`

**Çözüm:**
```python
# Eski kod (çalışmaz)
self.filtre_grubu_olustur()

# Yeni kod (çalışır)
from uygulama.arayuz.ekranlar.ebelge.ebelge_filtreleri import EbelgeFiltreleri
self.filtreler = EbelgeFiltreleri(self)
self.filtreler.filtre_grubu_olustur()
```

#### 5. Test Hataları
**Sorun:** `pytest: command not found`

**Çözüm:**
```bash
# pytest'i yükleyin
pip install pytest pytest-cov pytest-mock

# Virtual environment'in aktif olduğunu kontrol edin
which python
which pip
```

### Debug Araçları

#### 1. Logging Konfigürasyonu
```python
# uygulama/cekirdek/logging_config.py
import logging
import sys

def setup_logging(level=logging.INFO):
    """Logging konfigürasyonu"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

# Kullanım
from uygulama.cekirdek.logging_config import setup_logging
setup_logging(logging.DEBUG)

logger = logging.getLogger(__name__)
logger.info("Uygulama başlatıldı")
```

#### 2. Performance Profiling
```python
# Performance profiling için
import cProfile
import pstats

def profile_function(func):
    """Fonksiyon profiling decorator'ı"""
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(10)  # Top 10 fonksiyon
        
        return result
    return wrapper

# Kullanım
@profile_function
def yavas_fonksiyon():
    # Yavaş kod
    pass
```

#### 3. Memory Profiling
```python
# Memory profiling için
import tracemalloc

def memory_usage_check():
    """Memory kullanımını kontrol et"""
    tracemalloc.start()
    
    # Kod çalıştır
    # ...
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 1024 / 1024:.2f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")
    
    tracemalloc.stop()
```

### Yardım Kaynakları

#### Dokümantasyon
- **PyQt6:** https://doc.qt.io/qtforpython/
- **SQLAlchemy:** https://docs.sqlalchemy.org/
- **FastAPI:** https://fastapi.tiangolo.com/
- **Alembic:** https://alembic.sqlalchemy.org/

#### İç Kaynaklar
- **Kod Kalitesi Araçları:** `kod_kalitesi_araclari/README.md`
- **Database Schema:** `uygulama/database/README.md`
- **API Dokümantasyonu:** `docs/api/`
- **Deployment Guide:** `docs/deployment.md`

#### İletişim
- **Teknik Sorular:** Geliştirici ekibi Slack kanalı
- **Bug Raporları:** GitHub Issues
- **Feature Requests:** Product backlog

---

## 📚 Ek Kaynaklar

### Kod Örnekleri

#### Yeni Modül Oluşturma
```python
# yeni_modul/__init__.py
"""
Yeni modül paketi
"""
from .ana_sinif import AnaSinif
from .yardimci_sinif import YardimciSinif

__all__ = ['AnaSinif', 'YardimciSinif']
__version__ = '1.0.0'
```

#### Service Sınıfı Template
```python
# Version: 0.1.0
# Last Update: YYYY-MM-DD
# Module: uygulama.services.example_service
# Description: Örnek servis sınıfı
# Changelog:
# - İlk sürüm oluşturuldu

from typing import Optional, List
import logging

from uygulama.cekirdek.hatalar import ServiceError
from uygulama.repositories.example_repository import ExampleRepository


class ExampleService:
    """Örnek servis sınıfı"""
    
    def __init__(self, repository: ExampleRepository):
        """
        Constructor
        
        Args:
            repository: Example repository instance
        """
        self.repository = repository
        self.logger = logging.getLogger(__name__)
    
    def create_item(self, data: dict) -> dict:
        """
        Yeni item oluştur
        
        Args:
            data: Item verisi
            
        Returns:
            Oluşturulan item
            
        Raises:
            ServiceError: Oluşturma hatası durumunda
        """
        try:
            # Validation
            self._validate_data(data)
            
            # Business logic
            processed_data = self._process_data(data)
            
            # Repository call
            result = self.repository.create(processed_data)
            
            self.logger.info(f"Item oluşturuldu: {result['id']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Item oluşturma hatası: {e}")
            raise ServiceError(f"Item oluşturulamadı: {str(e)}")
    
    def _validate_data(self, data: dict) -> None:
        """Veri doğrulama (private method)"""
        if not data.get('name'):
            raise ValueError("Name alanı zorunlu")
    
    def _process_data(self, data: dict) -> dict:
        """Veri işleme (private method)"""
        processed = data.copy()
        processed['processed_at'] = datetime.now()
        return processed
```

#### Repository Sınıfı Template
```python
# Version: 0.1.0
# Last Update: YYYY-MM-DD
# Module: uygulama.repositories.example_repository
# Description: Örnek repository sınıfı
# Changelog:
# - İlk sürüm oluşturuldu

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from uygulama.database.models import ExampleModel
from uygulama.cekirdek.hatalar import RepositoryError


class ExampleRepository:
    """Örnek repository sınıfı"""
    
    def __init__(self, db_session: Session):
        """
        Constructor
        
        Args:
            db_session: Database session
        """
        self.db = db_session
    
    def create(self, data: dict) -> dict:
        """
        Yeni kayıt oluştur
        
        Args:
            data: Kayıt verisi
            
        Returns:
            Oluşturulan kayıt
            
        Raises:
            RepositoryError: Database hatası durumunda
        """
        try:
            model = ExampleModel(**data)
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            
            return self._model_to_dict(model)
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError(f"Kayıt oluşturulamadı: {str(e)}")
    
    def get_by_id(self, item_id: int) -> Optional[dict]:
        """ID ile kayıt getir"""
        try:
            model = self.db.query(ExampleModel).filter(
                ExampleModel.id == item_id
            ).first()
            
            return self._model_to_dict(model) if model else None
            
        except SQLAlchemyError as e:
            raise RepositoryError(f"Kayıt getirilemedi: {str(e)}")
    
    def _model_to_dict(self, model: ExampleModel) -> dict:
        """Model'i dict'e çevir (private method)"""
        return {
            'id': model.id,
            'name': model.name,
            'created_at': model.created_at.isoformat()
        }
```

### Geliştirme Workflow'u

#### 1. Yeni Feature Geliştirme
```bash
# 1. Feature branch oluştur
git checkout -b feature/yeni-ozellik

# 2. Kodu geliştir
# ... kod yazma ...

# 3. Testleri çalıştır
pytest tests/

# 4. Kod kalitesi kontrol
flake8 uygulama/
black uygulama/

# 5. Commit ve push
git add .
git commit -m "feat: yeni özellik eklendi"
git push origin feature/yeni-ozellik

# 6. Pull request oluştur
```

#### 2. Bug Fix Workflow'u
```bash
# 1. Bug branch oluştur
git checkout -b bugfix/hata-duzeltmesi

# 2. Hatayı reproduce et
pytest tests/test_specific_bug.py

# 3. Hatayı düzelt
# ... kod düzeltme ...

# 4. Test ekle
# ... test yazma ...

# 5. Tüm testleri çalıştır
pytest

# 6. Commit ve push
git add .
git commit -m "fix: hata düzeltildi"
git push origin bugfix/hata-duzeltmesi
```

---

Bu dokümantasyon, refactoring sonrası SonTechSP projesinde geliştirme yapmak için gereken tüm bilgileri içermektedir. Sorularınız için lütfen geliştirici ekibi ile iletişime geçiniz.

**Son Güncelleme:** 18 Aralık 2024  
**Doküman Versiyonu:** 2.0