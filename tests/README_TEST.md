# Version: 1.0.0
# Last Update: 2024-12-18
# Module: tests.README_TEST
# Description: SONTECHSP Test Stratejisi ve Çalıştırma Rehberi
# Changelog:
# - İlk sürüm: Kapsamlı test dokümantasyonu oluşturuldu

# SONTECHSP Test Stratejisi ve Çalıştırma Rehberi

## Genel Bakış

SONTECHSP sistemi için kritik iş kurallarının doğruluğunu garanti eden kapsamlı test paketi. Bu rehber, test stratejisi, çalıştırma yöntemleri ve ortam gereksinimlerini açıklar.

## Test Stratejisi

### Dual Test Yaklaşımı

SONTECHSP projesi **iki tamamlayıcı test yaklaşımı** kullanır:

#### 1. Unit Testler
- **Amaç**: Belirli senaryoları ve edge case'leri test eder
- **Özellikler**: 
  - Hızlı çalışır (< 2 saniye/test)
  - İzole edilmiş test ortamı
  - Belirli hata durumlarını kapsar
- **Örnek**: Stok seviyesi tam 0 olduğunda uyarı verme kontrolü

#### 2. Property-Based Testler (PBT)
- **Amaç**: Evrensel kuralları çok sayıda rastgele veri ile test eder
- **Özellikler**:
  - Hypothesis kütüphanesi kullanır
  - Minimum 100 iterasyon çalışır
  - Beklenmeyen edge case'leri keşfeder
- **Örnek**: Tüm negatif stok seviyeleri için kuralların tutarlı uygulanması

### Test Kategorileri

| Kategori | Süre Hedefi | Açıklama | Marker |
|----------|-------------|----------|---------|
| **smoke** | < 30 saniye | Temel sistem sağlığı kontrolü | `@pytest.mark.smoke` |
| **fast** | < 2 dakika | Hızlı unit testler | `@pytest.mark.unit` |
| **critical** | < 5 dakika | Kritik iş kuralı testleri | `@pytest.mark.critical` |
| **slow** | < 10 dakika | Kapsamlı entegrasyon testleri | `@pytest.mark.slow` |
| **property** | Değişken | Property-based testler | `@pytest.mark.property` |

## Test Ortamı Kurulumu

### Gereksinimler

#### Python Bağımlılıkları
```bash
# Test framework'leri
pip install pytest>=7.4.0
pip install pytest-cov>=4.1.0
pip install pytest-xdist>=3.3.0  # Paralel çalıştırma
pip install pytest-mock>=3.12.0

# Property-based testing
pip install hypothesis>=6.88.0

# Veritabanı test desteği
pip install pytest-postgresql>=5.0.0
```

#### Test Veritabanı Kurulumu

**UYARI**: Test ortamı **MUTLAKA** ayrı veritabanı kullanmalıdır!

##### PostgreSQL Test Veritabanı
```bash
# Test veritabanı oluştur
createdb sontechsp_test

# Test kullanıcısı oluştur
psql -c "CREATE USER test_user WITH PASSWORD 'test_pass';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE sontechsp_test TO test_user;"
```

##### Ortam Değişkenleri
```bash
# .env.test dosyası oluştur
DATABASE_URL=postgresql://test_user:test_pass@localhost/sontechsp_test
TEST_MODE=true
LOG_LEVEL=WARNING
```

### Test Konfigürasyonu

#### pytest.ini Ayarları
Proje kök dizinindeki `pyproject.toml` dosyasında test konfigürasyonu tanımlıdır:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "unit: Birim testler (hızlı, izole)",
    "integration: Entegrasyon testleri (orta hız)", 
    "property: Property-based testler (değişken hız)",
    "slow: Yavaş çalışan testler (> 30 saniye)",
    "critical: Kritik path testleri (CI/CD için)",
    "smoke: Temel işlevsellik testleri",
]
```

## Test Çalıştırma Komutları

### Temel Komutlar

#### Tüm Testler
```bash
# Tüm testleri çalıştır
pytest

# Verbose çıktı ile
pytest -v

# Paralel çalıştırma (önerilen)
pytest -n auto
```

#### Kategori Bazlı Çalıştırma
```bash
# Smoke testler (en hızlı)
pytest -m smoke

# Hızlı testler (geliştirme için)
pytest -m "not slow"

# Kritik testler (CI/CD için)
pytest -m critical

# Property-based testler
pytest -m property

# Yavaş testler
pytest -m slow
```

### Gelişmiş Komutlar

#### Coverage Raporları
```bash
# HTML coverage raporu
pytest --cov=sontechsp --cov-report=html

# Terminal coverage raporu
pytest --cov=sontechsp --cov-report=term-missing

# Minimum coverage kontrolü
pytest --cov=sontechsp --cov-fail-under=80
```

#### Paralel Test Çalıştırma
```bash
# Otomatik worker sayısı
pytest -n auto

# Belirli worker sayısı
pytest -n 4

# Paralel + coverage
pytest -n auto --cov=sontechsp --cov-report=html
```

#### Hata Ayıklama
```bash
# İlk hatada dur
pytest --maxfail=1

# Sadece başarısız testleri tekrar çalıştır
pytest --lf

# Test sürelerini göster
pytest --durations=10

# Detaylı traceback
pytest --tb=long
```

### Hazır Batch Dosyaları (Windows)

Proje `scripts/` klasöründe hazır komutlar:

```bash
# Hızlı testler
scripts\test-fast.bat

# Kritik testler  
scripts\test-critical.bat

# Smoke testler
scripts\test-smoke.bat

# Paralel testler
scripts\test-parallel.bat

# Yavaş testler
scripts\test-slow.bat
```

## Özel Test Türleri

### 1. Negatif Stok Testleri
**Dosya**: `test_stok_negatif_limit.py`

**Amaç**: Negatif stok kurallarının doğru çalıştığını test eder

**Test Senaryoları**:
- Stok seviyesi 0: Uyarı + İzin
- Stok seviyesi -1 ile -3: Uyarı + İzin  
- Stok seviyesi -6 ve altı: DogrulamaHatasi

```bash
# Sadece negatif stok testleri
pytest tests/test_stok_negatif_limit.py -v
```

### 2. Eş Zamanlı Stok Testleri
**Dosya**: `test_stok_eszamanlilik.py`

**Amaç**: Paralel stok işlemlerinde veri tutarlılığını test eder

**Test Senaryoları**:
- Row-level lock mekanizması
- Thread-safe işlemler
- Final stok seviyesi doğruluğu

```bash
# Eş zamanlı stok testleri
pytest tests/test_stok_eszamanlilik.py -v -s
```

### 3. POS Transaction Testleri
**Dosya**: `test_pos_odeme_tamamla_butunluk.py`

**Amaç**: POS ödeme işlemlerinin atomik olduğunu test eder

**Test Senaryoları**:
- Stok düşümü + satış kaydı bütünlüğü
- Rollback mekanizması
- Transaction başarısızlık durumları

```bash
# POS transaction testleri
pytest tests/test_pos_odeme_tamamla_butunluk.py -v
```

### 4. E-belge Retry Testleri
**Dosya**: `test_ebelge_retry.py`

**Amaç**: E-belge gönderim hatalarında retry mekanizmasını test eder

**Test Senaryoları**:
- DummySaglayici hata simülasyonu
- Deneme sayısı kontrolü
- Maksimum deneme sonrası HATA durumu

```bash
# E-belge retry testleri
pytest tests/test_ebelge_retry.py -v
```

### 5. Offline Kuyruk Testleri
**Dosya**: `test_offline_kuyruk.py`

**Amaç**: Internet kesintisinde offline kuyruk işleyişini test eder

**Test Senaryoları**:
- SQLite kuyruk kayıt/okuma
- FIFO sırası korunumu
- Kuyruk temizleme

```bash
# Offline kuyruk testleri
pytest tests/test_offline_kuyruk.py -v
```

### 6. UI Smoke Testleri
**Dosya**: `test_ui_smoke.py`

**Amaç**: Temel UI fonksiyonlarının çalışırlığını test eder

**Mevcut Altyapı**: `uygulama.arayuz.smoke_test_calistir` modülü kullanır

```bash
# UI smoke testleri
pytest tests/test_ui_smoke.py -v

# Mevcut smoke test altyapısı
python -m uygulama.arayuz.smoke_test_calistir
```

## Mock Servisler

### DummySaglayici
E-belge sağlayıcı simülasyonu için:

```python
class DummySaglayici:
    def __init__(self, fail_rate: float = 0.5):
        self.fail_rate = fail_rate
    
    def belge_gonder(self, belge_data: dict) -> bool:
        return random.random() > self.fail_rate
```

### MockNetworkService
İnternet bağlantı simülasyonu için:

```python
class MockNetworkService:
    def __init__(self, is_online: bool = True):
        self.is_online = is_online
    
    def check_connection(self) -> bool:
        return self.is_online
```

## Property-Based Test Konfigürasyonu

### Hypothesis Ayarları
```python
from hypothesis import settings, strategies as st

# Test konfigürasyonu
@settings(max_examples=100, deadline=2000)
@given(stok_seviyesi=st.decimals(min_value=-10, max_value=100))
def test_negatif_stok_kurallari(stok_seviyesi):
    # Test implementasyonu
    pass
```

### Property Test Formatı
Her property-based test şu format ile etiketlenir:

```python
# **Feature: test-stabilizasyon-paketi, Property 5: Negatif stok eşik kuralları**
# **Validates: Requirements 2.2, 2.3**
```

## Performans Hedefleri

| Test Kategorisi | Hedef Süre | Maksimum Süre |
|----------------|------------|---------------|
| Smoke testler | < 15 saniye | 30 saniye |
| Hızlı testler | < 30 saniye | 2 dakika |
| Kritik testler | < 5 dakika | 10 dakika |
| Yavaş testler | < 5 dakika | 10 dakika |
| Tüm testler (paralel) | < 2 dakika | 5 dakika |

## Geliştirme Akışı

### 1. Geliştirme Sırasında
```bash
# Hızlı feedback döngüsü
pytest -m "not slow" -n auto --maxfail=3
```

### 2. Commit Öncesi
```bash
# Kritik testleri çalıştır
pytest -m critical --maxfail=1
```

### 3. Push Öncesi
```bash
# Coverage ile kapsamlı test
pytest -m "not slow" --cov=sontechsp --cov-fail-under=80
```

### 4. Haftalık Kontrol
```bash
# Tüm testleri çalıştır
pytest -n auto --cov=sontechsp --cov-report=html
```

## CI/CD Pipeline Komutları

### Pull Request
```bash
pytest -m "critical or smoke" -n 2 --maxfail=5 --cov=sontechsp --cov-report=xml
```

### Main Branch
```bash
pytest -m "not slow" -n auto --cov=sontechsp --cov-report=xml --cov-fail-under=75
```

### Release
```bash
pytest -n auto --cov=sontechsp --cov-report=xml --cov-report=html --cov-fail-under=80
```

## Hata Yönetimi

### Test Hataları
- **TestConfigurationError**: Test konfigürasyonu hatası
- **TestDatabaseError**: Test veritabanı bağlantı hatası  
- **MockServiceError**: Mock servis simülasyon hatası
- **TestTimeoutError**: Test zaman aşımı hatası

### Hata Çözüm Adımları

#### 1. Test Veritabanı Bağlantı Hatası
```bash
# Veritabanı durumunu kontrol et
pg_isready -h localhost -p 5432

# Test veritabanını yeniden oluştur
dropdb sontechsp_test
createdb sontechsp_test
```

#### 2. Import Hataları
```bash
# Python path'i kontrol et
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Modül import'larını test et
python -c "import sontechsp; print('OK')"
```

#### 3. Paralel Test Çakışmaları
```bash
# Tek thread ile çalıştır
pytest -n 1

# Test isolation'ı kontrol et
pytest --forked
```

## Test Sonuç Raporları

### HTML Coverage Raporu
```bash
pytest --cov=sontechsp --cov-report=html
# Rapor: htmlcov/index.html
```

### XML Coverage Raporu (CI/CD)
```bash
pytest --cov=sontechsp --cov-report=xml
# Rapor: coverage.xml
```

### Test Süre Raporu
```bash
pytest --durations=20 > test_durations.txt
```

## Sorun Giderme

### Sık Karşılaşılan Sorunlar

#### 1. "No tests ran" Hatası
**Çözüm**: Test dosya isimlerinin `test_` ile başladığından emin olun

#### 2. Import ModuleNotFoundError
**Çözüm**: PYTHONPATH'e proje kök dizinini ekleyin

#### 3. Database Connection Error
**Çözüm**: Test veritabanının çalıştığından ve erişilebilir olduğundan emin olun

#### 4. Hypothesis Timeout
**Çözüm**: `@settings(deadline=None)` ile timeout'u devre dışı bırakın

### Debug Komutları
```bash
# Test discovery kontrolü
pytest --collect-only

# Verbose import kontrolü
pytest -v --tb=long --no-header

# Specific test debug
pytest tests/test_specific.py::test_function -v -s --tb=long
```

## İletişim ve Destek

Test ile ilgili sorular için:
- **Dokümantasyon**: Bu README_TEST.md dosyası
- **Test Komutları**: `test-commands.md` dosyası
- **Konfigürasyon**: `pyproject.toml` dosyası

---

**Son Güncelleme**: 2024-12-18  
**Sürüm**: 1.0.0  
**Sorumlu**: SONTECHSP Test Ekibi