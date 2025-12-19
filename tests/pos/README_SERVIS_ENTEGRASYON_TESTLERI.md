# POS Servis Entegrasyon Testleri

## Genel Bakış

Bu klasör POS yeni ekran tasarımı için servis entegrasyon testlerini içerir. Testler, POS UI bileşenleri ile servis katmanı arasındaki entegrasyonu doğrular.

## Test Dosyaları

### 1. test_pos_ui_servis_entegrasyonu.py
**Amaç**: POS UI bileşenleri ile servis katmanı arasındaki entegrasyonu test eder.

**Test Sınıfları**:
- `TestPOSUIServisEntegrasyonu`: Ana UI-Servis entegrasyon testleri
  - Barkod ekleme entegrasyonu
  - Sepet toplam güncelleme
  - Nakit/Parçalı ödeme entegrasyonu
  - Klavye kısayolları entegrasyonu
  - Hata yönetimi entegrasyonu
  - Offline kuyruk entegrasyonu
  - Müşteri seçim entegrasyonu
  - Sepet satır işlemleri

- `TestMockServisEntegrasyonu`: Mock servislerle entegrasyon testleri
  - Mock servis ile tam akış
  - End-to-end akış mock testi
  - Hızlı ürün butonları entegrasyonu
  - Tema uygulama entegrasyonu

- `TestServisHataYonetimi`: Servis hata yönetimi testleri
  - Sepet servisi hata yönetimi
  - Ödeme servisi hata yönetimi
  - Network hatası yönetimi

- `TestPerformansEntegrasyonu`: Performans entegrasyon testleri
  - Çoklu ürün ekleme performansı
  - Sepet toplam hesaplama performansı

**Çalıştırma**:
```bash
pytest tests/pos/test_pos_ui_servis_entegrasyonu.py -v
```

### 2. test_pos_mock_servis_testleri.py
**Amaç**: POS servisleri için mock implementasyonları ve testleri.

**Mock Servis Sınıfları**:
- `MockSepetService`: Mock sepet servisi
  - Sepet oluşturma, barkod ekleme, adet değiştirme
  - Sepet toplam hesaplama, sepet boşaltma
  
- `MockOdemeService`: Mock ödeme servisi
  - Tek ödeme, parçalı ödeme
  - Ödeme tutarı kontrolü
  
- `MockStokService`: Mock stok servisi
  - Ürün bilgisi getirme
  - Stok kontrolü, stok düşümü
  
- `MockOfflineKuyrukService`: Mock offline kuyruk servisi
  - Kuyruğa ekleme, senkronizasyon
  - Kuyruk istatistikleri

**Test Sınıfları**:
- `TestMockSepetService`: Mock sepet servisi testleri
- `TestMockOdemeService`: Mock ödeme servisi testleri
- `TestMockStokService`: Mock stok servisi testleri
- `TestMockOfflineKuyrukService`: Mock offline kuyruk servisi testleri
- `TestMockServisEntegrasyonu`: Mock servis entegrasyon testleri

**Çalıştırma**:
```bash
pytest tests/pos/test_pos_mock_servis_testleri.py -v
```

### 3. test_pos_end_to_end_akis.py
**Amaç**: POS sisteminin tam akış senaryolarını test eder.

**Test Sınıfları**:
- `TestPOSEndToEndAkis`: End-to-end akış testleri
  - Basit satış akışı (tek ürün, nakit ödeme)
  - Çoklu ürün satış akışı
  - Parçalı ödeme akışı
  - İndirim uygulama akışı
  - Müşteri seçim ve açık hesap akışı
  - Sepet bekletme akışı
  - Klavye kısayolları akışı
  - Hata yönetimi akışı
  - Offline mod akışı
  - Performans akışı
  - Tam satış döngüsü akışı
  - İptal ve temizleme akışı
  - Hızlı ürün entegrasyon akışı

- `TestPOSStresTestleri`: Stres testleri
  - Yüksek hacim ürün ekleme (500 ürün)
  - Sürekli adet değiştirme
  - Bellek kullanımı testi

**Çalıştırma**:
```bash
pytest tests/pos/test_pos_end_to_end_akis.py -v
```

## Test Kapsamı

### UI Bileşenleri
- ✅ POS Satış Ekranı
- ✅ Üst Bar (Barkod/Arama)
- ✅ Sepet Modeli ve Tablo
- ✅ Ödeme Paneli
- ✅ Hızlı İşlem Şeridi
- ✅ Hızlı Ürünler Sekmesi
- ✅ Klavye Kısayol Yöneticisi
- ✅ Hata Yöneticisi

### Servis Entegrasyonları
- ✅ Sepet Servisi
- ✅ Ödeme Servisi
- ✅ Stok Servisi
- ✅ Offline Kuyruk Servisi

### İş Akışları
- ✅ Barkod ekleme ve ürün arama
- ✅ Sepet yönetimi (ekleme, silme, adet değiştirme)
- ✅ Ödeme işlemleri (nakit, kart, parçalı, açık hesap)
- ✅ İndirim ve kupon uygulama
- ✅ Müşteri seçimi
- ✅ Sepet bekletme
- ✅ Klavye kısayolları
- ✅ Hata yönetimi
- ✅ Offline mod ve senkronizasyon

### Performans Testleri
- ✅ Çoklu ürün ekleme (50-500 ürün)
- ✅ Toplam hesaplama performansı
- ✅ Adet değiştirme performansı
- ✅ Bellek kullanımı

## Gereksinimler

```bash
pip install pytest pytest-qt PyQt6
```

## Tüm Testleri Çalıştırma

```bash
# Tüm POS servis entegrasyon testleri
pytest tests/pos/test_pos_ui_servis_entegrasyonu.py tests/pos/test_pos_mock_servis_testleri.py tests/pos/test_pos_end_to_end_akis.py -v

# Sadece entegrasyon testleri
pytest tests/pos/test_pos_ui_servis_entegrasyonu.py -v

# Sadece mock servis testleri
pytest tests/pos/test_pos_mock_servis_testleri.py -v

# Sadece end-to-end testleri
pytest tests/pos/test_pos_end_to_end_akis.py -v

# Belirli bir test sınıfı
pytest tests/pos/test_pos_ui_servis_entegrasyonu.py::TestPOSUIServisEntegrasyonu -v

# Belirli bir test
pytest tests/pos/test_pos_ui_servis_entegrasyonu.py::TestPOSUIServisEntegrasyonu::test_barkod_ekleme_ui_servis_entegrasyonu -v
```

## Test Raporlama

```bash
# HTML rapor oluşturma
pytest tests/pos/test_pos_ui_servis_entegrasyonu.py --html=test_reports/pos_entegrasyon_raporu.html

# Coverage raporu
pytest tests/pos/ --cov=sontechsp.uygulama.arayuz.ekranlar.pos --cov-report=html
```

## Mock Servis Kullanımı

Mock servisler gerçek servis davranışlarını simüle eder ve test izolasyonu sağlar:

```python
from tests.pos.test_pos_mock_servis_testleri import MockSepetService, MockOdemeService

# Mock servis oluşturma
sepet_service = MockSepetService()
odeme_service = MockOdemeService()

# Sepet oluşturma
sepet_id = sepet_service.yeni_sepet_olustur(terminal_id=1, kasiyer_id=1)

# Barkod ekleme
sepet_service.barkod_ekle(sepet_id, "1234567890")

# Ödeme yapma
odeme_service.tek_odeme_yap(sepet_id, OdemeTuru.NAKIT, Decimal('10.50'))
```

## Notlar

- Testler PyQt6 QApplication gerektirir
- Mock servisler gerçek veritabanı bağlantısı gerektirmez
- Performans testleri sistem kaynaklarına bağlı olarak değişebilir
- End-to-end testler tam kullanıcı senaryolarını simüle eder

## Sorun Giderme

### QApplication Hatası
```python
# Test başında QApplication oluşturulduğundan emin olun
if not QApplication.instance():
    app = QApplication([])
```

### Import Hataları
```bash
# Proje kök dizinini Python path'e ekleyin
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Timeout Hataları
```bash
# Timeout süresini artırın
pytest tests/pos/ --timeout=60
```

## Katkıda Bulunma

Yeni test senaryoları eklerken:
1. Test adını açıklayıcı yapın
2. Docstring ekleyin
3. Mock servisleri kullanın
4. Assert mesajları ekleyin
5. Cleanup işlemlerini unutmayın (pos_ekran.close())

## Lisans

Bu testler SONTECHSP projesi kapsamındadır.
