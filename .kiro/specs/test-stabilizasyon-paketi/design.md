# Test ve Stabilizasyon Paketi - Tasarım Belgesi

## Genel Bakış

SONTECHSP sistemi için kritik iş kurallarının doğruluğunu garanti eden kapsamlı test paketi. Bu paket, stok tutarlılığı, negatif stok kuralları, POS transaction bütünlüğü, e-belge retry mekanizması ve offline kuyruk işleyişinin güvenilirliğini test eder.

## Mimari

### Test Katmanları

```
Test Dokümantasyon Katmanı
    ↓
Senaryo Test Katmanı (Negatif Stok, POS Transaction, E-belge Retry)
    ↓
Entegrasyon Test Katmanı (Eş Zamanlı Stok, Offline Kuyruk)
    ↓
Smoke Test Katmanı (Temel Fonksiyon Kontrolü)
    ↓
Test Altyapı Katmanı (Test DB, Mock Servisler)
```

### Test Stratejisi

- **Senaryo Testleri**: Belirli iş kurallarını test eden odaklanmış testler
- **Property-Based Testler**: Genel kuralları çok sayıda rastgele veri ile test eden testler
- **Entegrasyon Testleri**: Modüller arası etkileşimi test eden testler
- **Smoke Testler**: Temel sistem sağlığını hızlıca kontrol eden testler

## Bileşenler ve Arayüzler

### Test Dokümantasyon Modülü
- **README_TEST.md**: Ana test rehberi
- Test stratejisi açıklaması
- Çalıştırma komutları
- Ortam kurulum rehberi

### Negatif Stok Test Modülü
- **test_stok_negatif_limit.py**: Negatif stok kuralları testleri
- Stok seviyesi eşik testleri (0, -3, -6)
- DogrulamaHatasi kontrolü
- Test veritabanı kullanımı

### Eş Zamanlı Stok Test Modülü
- **test_stok_eszamanlilik.py**: Paralel stok işlem testleri
- Row-level lock testleri
- Veri tutarlılığı kontrolü
- Thread-safe işlem testleri

### POS Transaction Test Modülü
- **test_pos_odeme_tamamla_butunluk.py**: Atomik transaction testleri
- Stok düşümü + satış kaydı bütünlüğü
- Rollback mekanizması testleri
- Transaction başarısızlık senaryoları

### E-belge Retry Test Modülü
- **test_ebelge_retry.py**: E-belge yeniden deneme testleri
- DummySaglayici hata simülasyonu
- Deneme sayısı kontrolü
- Maksimum deneme sonrası HATA durumu

### Offline Kuyruk Test Modülü
- **test_offline_kuyruk.py**: Offline işlem kuyruk testleri
- SQLite kuyruk kayıt/okuma
- FIFO sırası kontrolü
- Kuyruk temizleme testleri

### UI Smoke Test Modülü
- **test_ui_smoke.py**: Temel UI fonksiyon testleri
- Import kontrolü
- Servis başlatma testleri
- Mevcut smoke_test_calistir.py entegrasyonu

## Veri Modelleri

### Test Konfigürasyon Modeli
```python
@dataclass
class TestConfig:
    test_db_url: str
    max_retry_count: int
    negative_stock_limits: Dict[str, Decimal]
    smoke_test_modules: List[str]
```

### Test Sonuç Modeli
```python
@dataclass
class TestResult:
    test_name: str
    status: TestStatus  # PASS, FAIL, SKIP
    execution_time: float
    error_message: Optional[str]
    details: Dict[str, Any]
```

### Mock Servis Modeli
```python
class DummySaglayici:
    def __init__(self, fail_rate: float = 0.5):
        self.fail_rate = fail_rate
        self.call_count = 0
    
    def belge_gonder(self, belge_data: dict) -> bool:
        # Hata simülasyonu
        pass
```

## Doğruluk Özellikleri

*Bir özellik, sistemin tüm geçerli çalıştırmalarında doğru olması gereken bir karakteristik veya davranıştır - esasen, sistemin ne yapması gerektiği hakkında resmi bir ifadedir. Özellikler, insan tarafından okunabilir spesifikasyonlar ile makine tarafından doğrulanabilir doğruluk garantileri arasında köprü görevi görür.*

### Özellik 1: Test Dokümantasyon Tamlığı
*For any* test dokümantasyonu, test stratejisi, çalıştırma komutları ve ortam gereksinimleri bilgilerini içermeli
**Validates: Requirements 1.1**

### Özellik 2: Test Ortamı İzolasyonu
*For any* test çalıştırması, production veritabanına bağlanmamalı ve ayrı test veritabanı kullanmalı
**Validates: Requirements 1.2**

### Özellik 3: Test Kategori Komutları
*For any* test kategorisi, ayrı çalıştırma komutu mevcut olmalı ve çalıştırılabilir olmalı
**Validates: Requirements 1.3**

### Özellik 4: Test Sonuç Raporlama
*For any* test çalıştırması, başarı/başarısızlık durumunu net şekilde raporlamalı
**Validates: Requirements 1.4**

### Özellik 5: Negatif Stok Eşik Kuralları
*For any* stok seviyesi, -1 ile -3 arası uyarı+izin, -6 ve altı DogrulamaHatasi fırlatmalı
**Validates: Requirements 2.2, 2.3**

### Özellik 6: Negatif Stok Tutarlılığı
*For any* ürün, negatif stok kontrol kuralları tutarlı şekilde uygulanmalı
**Validates: Requirements 2.4**

### Özellik 7: Eş Zamanlı Stok Kilitleme
*For any* aynı ürüne eş zamanlı erişim, row-level lock ile sadece bir işlemin başarılı olmasını sağlamalı
**Validates: Requirements 3.1, 3.2**

### Özellik 8: Stok Tutarlılık Korunumu
*For any* stok işlem serisi, final stok seviyesi matematiksel olarak doğru olmalı ve veri kaybı olmamalı
**Validates: Requirements 3.3, 3.4**

### Özellik 9: POS Transaction Atomikliği
*For any* POS ödeme işlemi, stok düşümü ve satış kaydı tek transaction içinde yapılmalı
**Validates: Requirements 4.1**

### Özellik 10: Transaction Rollback Garantisi
*For any* transaction hatası, tüm değişiklikler geri alınmalı ve sistem önceki duruma dönmeli
**Validates: Requirements 4.2, 4.4**

### Özellik 11: Satış-Stok Bütünlüğü
*For any* tamamlanmış satış, stok düşümü olmadan TAMAMLANDI durumunda olmamalı
**Validates: Requirements 4.3**

### Özellik 12: E-belge Retry Sayacı
*For any* e-belge gönderim hatası, deneme sayısı artmalı ve maksimum deneme sonrası HATA durumu olmalı
**Validates: Requirements 5.1, 5.2**

### Özellik 13: E-belge Retry Başarı Sıfırlama
*For any* başarılı e-belge retry işlemi, deneme sayacı sıfırlanmalı
**Validates: Requirements 5.4**

### Özellik 14: Offline Kuyruk FIFO Sırası
*For any* offline kuyruk işlemi, FIFO sırası korunmalı ve işlenen kayıtlar silinmeli
**Validates: Requirements 6.2, 6.4**

### Özellik 15: Offline Kuyruk Kayıt-İşleme
*For any* internet kesintisi, işlemler SQLite kuyruğuna kaydedilmeli ve bağlantı gelince işlenmeli
**Validates: Requirements 6.1, 6.3**

### Özellik 16: Smoke Test Kapsamlılığı
*For any* smoke test çalıştırması, tüm ana modüllerin import edilebilirliği ve kritik servislerin başlatılabilirliği kontrol edilmeli
**Validates: Requirements 7.1, 7.2**

### Özellik 17: Smoke Test Raporlama
*For any* smoke test tamamlanması, özet rapor sunulmalı ve mevcut altyapı kullanılmalı
**Validates: Requirements 7.3, 7.4**

## Hata Yönetimi

### Test Hataları
- **TestConfigurationError**: Test konfigürasyonu hatası
- **TestDatabaseError**: Test veritabanı bağlantı hatası
- **MockServiceError**: Mock servis simülasyon hatası
- **TestTimeoutError**: Test zaman aşımı hatası

### Hata Yönetim Stratejisi
- Test hatalarında detaylı log kayıtları
- Hata durumunda test ortamı temizliği
- Başarısız testler için yeniden çalıştırma seçeneği
- Test sonuçlarının merkezi raporlama sistemi

## Test Stratejisi

### Dual Test Yaklaşımı

Bu tasarım hem unit testleri hem de property-based testleri içerir:

**Unit Testler:**
- Belirli senaryoları test eder (örn: stok=0 durumu)
- Edge case'leri ve hata durumlarını kapsar
- Entegrasyon noktalarını doğrular

**Property-Based Testler:**
- Evrensel kuralları test eder (örn: tüm negatif stok seviyeleri)
- Çok sayıda rastgele veri ile kapsamlı test sağlar
- Beklenmeyen edge case'leri keşfeder

**Property-Based Test Konfigürasyonu:**
- Test kütüphanesi: **Hypothesis** (Python için)
- Minimum iterasyon sayısı: **100** (rastgele test süreci için)
- Her property-based test şu format ile etiketlenir: **Feature: test-stabilizasyon-paketi, Property {numara}: {özellik_metni}**

**Test Gereksinimleri:**
- Her doğruluk özelliği TEK bir property-based test ile uygulanır
- Property-based testler tasarım belgesindeki özelliklere açık referans verir
- Unit testler ve property testler birbirini tamamlar: unit testler belirli bugları yakalar, property testler genel doğruluğu doğrular

### Test Ortamı

**Test Veritabanı:**
- Ayrı PostgreSQL test veritabanı
- Her test çalıştırması öncesi temiz durum
- Test verisi otomatik oluşturma

**Mock Servisler:**
- DummySaglayici: E-belge hata simülasyonu
- MockNetworkService: İnternet bağlantı simülasyonu
- TestStokService: Kontrollü stok işlemleri

**Test Kategorileri:**
- **smoke**: Hızlı temel kontroller (< 30 saniye)
- **fast**: Hızlı unit testler (< 2 dakika)
- **slow**: Kapsamlı entegrasyon testleri (< 10 dakika)
- **critical**: Kritik iş kuralı testleri (< 5 dakika)

### Çalıştırma Komutları

```bash
# Tüm testler
python -m pytest tests/

# Kategori bazlı
python -m pytest -m smoke tests/
python -m pytest -m fast tests/
python -m pytest -m critical tests/

# Belirli test dosyası
python -m pytest tests/test_stok_negatif_limit.py
python -m pytest tests/test_pos_odeme_tamamla_butunluk.py

# Paralel çalıştırma
python -m pytest -n auto tests/

# Kapsamlı rapor
python -m pytest --cov=sontechsp --cov-report=html tests/
```