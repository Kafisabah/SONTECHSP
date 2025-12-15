# Test Performans Optimizasyonu - Tasarım

## Genel Bakış

SONTECHSP projesinde test süitinin performansını optimize etmek için kapsamlı bir yaklaşım benimsenecek. Mevcut 817 testin çoğu parametrize edilmiş testlerdir ve bu durum test süresini önemli ölçüde artırmaktadır. Bu tasarım, testleri kategorize etme, paralel çalıştırma, property-based test optimizasyonu ve akıllı test seçimi stratejilerini içermektedir.

## Mimari

### Test Kategorileri Hiyerarşisi
```
Test Suite
├── Fast Tests (< 30 saniye)
│   ├── Unit Tests
│   ├── Critical Integration Tests
│   └── Essential Property Tests
├── Slow Tests (> 30 saniye)
│   ├── Full Integration Tests
│   ├── Comprehensive Property Tests
│   └── Performance Tests
└── CI/CD Tests
    ├── Smoke Tests
    ├── Critical Path Tests
    └── Regression Tests
```

### Test Execution Pipeline
```
Test Request
    ↓
Marker Detection
    ↓
Test Selection Strategy
    ↓
Parallel Execution (pytest-xdist)
    ↓
Result Aggregation
    ↓
Coverage Report
```

## Bileşenler ve Arayüzler

### 1. Test Marker Sistemi
- **unit**: Birim testler (hızlı, izole)
- **integration**: Entegrasyon testleri (orta hız)
- **property**: Property-based testler (değişken hız)
- **slow**: Yavaş testler (> 30 saniye)
- **critical**: Kritik path testleri (CI/CD için)

### 2. Test Konfigürasyon Yöneticisi
```python
class TestConfigManager:
    def get_marker_config() -> Dict[str, Any]
    def get_hypothesis_settings() -> Dict[str, Any]
    def get_parallel_config() -> Dict[str, Any]
    def update_pyproject_config() -> None
```

### 3. Test Seçici (Test Selector)
```python
class TestSelector:
    def select_fast_tests() -> List[str]
    def select_critical_tests() -> List[str]
    def sample_parametrized_tests(ratio: float) -> List[str]
    def prioritize_tests() -> List[str]
```

### 4. Paralel Test Yöneticisi
```python
class ParallelTestManager:
    def get_optimal_worker_count() -> int
    def configure_xdist() -> Dict[str, Any]
    def ensure_test_isolation() -> None
```

## Veri Modelleri

### Test Metadata
```python
@dataclass
class TestMetadata:
    name: str
    markers: List[str]
    estimated_duration: float
    priority: int
    dependencies: List[str]
    file_path: str
```

### Performance Metrics
```python
@dataclass
class PerformanceMetrics:
    total_duration: float
    test_count: int
    worker_count: int
    coverage_percentage: float
    failed_tests: List[str]
    slow_tests: List[str]
```

### Test Configuration
```python
@dataclass
class TestConfig:
    markers: Dict[str, str]
    hypothesis_settings: Dict[str, Any]
    parallel_settings: Dict[str, Any]
    sampling_ratio: float
    timeout_settings: Dict[str, int]
```

## Doğruluk Özellikleri

*Bir özellik, sistemin tüm geçerli yürütmelerinde doğru olması gereken bir karakteristik veya davranıştır - esasen, sistemin ne yapması gerektiği hakkında resmi bir ifadedir. Özellikler, insan tarafından okunabilir spesifikasyonlar ile makine tarafından doğrulanabilir doğruluk garantileri arasında köprü görevi görür.*

### Özellik 1: Test Süresi Sınırları
*Herhangi bir* test kategorisi için, belirlenen süre sınırları aşılmamalıdır
**Doğrular: Gereksinimler 1.1, 1.2**

### Özellik 2: Marker Tabanlı Test Seçimi
*Herhangi bir* marker filtresi için, sadece o marker'a sahip testler çalıştırılmalıdır
**Doğrular: Gereksinimler 1.3, 2.2**

### Özellik 3: Varsayılan Test Davranışı
*Herhangi bir* varsayılan pytest çalıştırması için, sadece hızlı testler çalışmalıdır
**Doğrular: Gereksinimler 1.5**

### Özellik 4: CI/CD Test Seçimi
*Herhangi bir* CI/CD pipeline çalıştırması için, sadece kritik testler çalışmalıdır
**Doğrular: Gereksinimler 1.4**

### Özellik 5: Marker Konfigürasyonu
*Herhangi bir* test dosyası için, uygun marker'lar pyproject.toml'de tanımlanmalıdır
**Doğrular: Gereksinimler 2.1, 2.3**

### Özellik 6: Test Raporu Kategorileri
*Herhangi bir* test raporu için, kategori bazlı sonuçlar görüntülenmelidir
**Doğrular: Gereksinimler 2.4**

### Özellik 7: Hypothesis Optimizasyonu
*Herhangi bir* property test için, maksimum örnek sayısı 50 ve timeout 2 saniye olmalıdır
**Doğrular: Gereksinimler 3.1, 3.2**

### Özellik 8: Hypothesis Profil Ayarları
*Herhangi bir* hypothesis testi için, hızlı profil kullanılmalı ve gereksiz health check'ler devre dışı olmalıdır
**Doğrular: Gereksinimler 3.3, 3.4**

### Özellik 9: Test Önceliklendirme
*Herhangi bir* dosya bazlı parametrize test için, kritik dosyalar öncelikli test edilmelidir
**Doğrular: Gereksinimler 4.1**

### Özellik 10: Kapsama Korunması
*Herhangi bir* test optimizasyonu için, minimum kapsama seviyesi korunmalıdır
**Doğrular: Gereksinimler 4.2, 4.4**

### Özellik 11: Sampling Stratejisi
*Herhangi bir* sampling işlemi için, rastgele dosya seçimi yapılmalıdır
**Doğrular: Gereksinimler 4.3**

### Özellik 12: Paralel Test Konfigürasyonu
*Herhangi bir* paralel test çalıştırması için, worker sayısı CPU çekirdek sayısına eşit olmalıdır
**Doğrular: Gereksinimler 5.1, 5.2**

### Özellik 13: Test İzolasyonu
*Herhangi bir* paralel test çalıştırması için, testler birbirini etkilememeli ve coverage doğru hesaplanmalıdır
**Doğrular: Gereksinimler 5.3, 5.4**

## Hata Yönetimi

### Test Timeout Yönetimi
- Hypothesis testleri için 2 saniye timeout
- Genel testler için 30 saniye timeout
- Yavaş testler için 5 dakika timeout

### Paralel Test Hataları
- Worker crash durumunda otomatik yeniden başlatma
- Test izolasyon hatalarında seri çalıştırmaya geçiş
- Coverage hesaplama hatalarında uyarı verme

### Konfigürasyon Hataları
- Geçersiz marker tanımlarında varsayılan değerlere dönüş
- Eksik bağımlılıklarda uyarı mesajları
- Konfigürasyon dosyası bozukluğunda backup kullanımı

## Test Stratejisi

### Birim Testleri
- Test konfigürasyon yöneticisi için birim testler
- Test seçici algoritmaları için birim testler
- Paralel test yöneticisi için birim testler
- Marker sistemi için birim testler

### Property-Based Testleri
Property-based testler için Hypothesis kütüphanesi kullanılacak. Her property test minimum 100 iterasyon çalıştırılacak ve aşağıdaki format kullanılacak:

**Property Test 1: Test Süresi Doğrulaması**
- **Test Performans Optimizasyonu, Özellik 1: Test Süresi Sınırları**
- **Doğrular: Gereksinimler 1.1, 1.2**

**Property Test 2: Marker Filtreleme**
- **Test Performans Optimizasyonu, Özellik 2: Marker Tabanlı Test Seçimi**
- **Doğrular: Gereksinimler 1.3, 2.2**

**Property Test 3: Varsayılan Davranış**
- **Test Performans Optimizasyonu, Özellik 3: Varsayılan Test Davranışı**
- **Doğrular: Gereksinimler 1.5**

**Property Test 4: CI/CD Seçimi**
- **Test Performans Optimizasyonu, Özellik 4: CI/CD Test Seçimi**
- **Doğrular: Gereksinimler 1.4**

**Property Test 5: Konfigürasyon Doğrulaması**
- **Test Performans Optimizasyonu, Özellik 5: Marker Konfigürasyonu**
- **Doğrular: Gereksinimler 2.1, 2.3**

**Property Test 6: Rapor Kategorileri**
- **Test Performans Optimizasyonu, Özellik 6: Test Raporu Kategorileri**
- **Doğrular: Gereksinimler 2.4**

**Property Test 7: Hypothesis Ayarları**
- **Test Performans Optimizasyonu, Özellik 7: Hypothesis Optimizasyonu**
- **Doğrular: Gereksinimler 3.1, 3.2**

**Property Test 8: Hypothesis Profil**
- **Test Performans Optimizasyonu, Özellik 8: Hypothesis Profil Ayarları**
- **Doğrular: Gereksinimler 3.3, 3.4**

**Property Test 9: Test Önceliklendirme**
- **Test Performans Optimizasyonu, Özellik 9: Test Önceliklendirme**
- **Doğrular: Gereksinimler 4.1**

**Property Test 10: Kapsama Korunması**
- **Test Performans Optimizasyonu, Özellik 10: Kapsama Korunması**
- **Doğrular: Gereksinimler 4.2, 4.4**

**Property Test 11: Sampling Algoritması**
- **Test Performans Optimizasyonu, Özellik 11: Sampling Stratejisi**
- **Doğrular: Gereksinimler 4.3**

**Property Test 12: Paralel Konfigürasyon**
- **Test Performans Optimizasyonu, Özellik 12: Paralel Test Konfigürasyonu**
- **Doğrular: Gereksinimler 5.1, 5.2**

**Property Test 13: Test İzolasyonu**
- **Test Performans Optimizasyonu, Özellik 13: Test İzolasyonu**
- **Doğrular: Gereksinimler 5.3, 5.4**

### Entegrasyon Testleri
- Tam test süiti çalıştırma testleri
- Marker bazlı filtreleme entegrasyon testleri
- Paralel çalıştırma entegrasyon testleri
- Coverage raporu entegrasyon testleri

### Performans Testleri
- Test süitinin toplam çalışma süresi ölçümü
- Paralel vs seri çalıştırma karşılaştırması
- Memory kullanımı ölçümü
- CPU kullanımı ölçümü