# Kod Kalitesi ve Standardizasyon Tasarım Dokümanı

## Genel Bakış

Bu tasarım dokümanı, SONTECHSP kod tabanının mevcut durumunu analiz ederek kod kalitesi standartlarına uygun hale getirilmesi için gerekli refactoring işlemlerini tanımlar. Sistem, otomatik kod analizi, dosya/fonksiyon boyut kontrolü, mimari uyumluluk denetimi ve refactoring araçları içerir.

## Mimari

### Katmanlı Yapı

```
Analiz Katmanı
├── Dosya Boyut Analizörü
├── Fonksiyon Boyut Analizörü
├── Import Yapısı Analizörü
└── Kod Tekrarı Analizörü

Refactoring Katmanı
├── Dosya Bölücü
├── Fonksiyon Bölücü
├── Import Düzenleyici
└── Ortak Modül Çıkarıcı

Doğrulama Katmanı
├── Test Çalıştırıcı
├── Mimari Doğrulayıcı
└── Kalite Kontrol

Raporlama Katmanı
├── Sorun Raporu Üretici
├── İlerleme Takipçi
└── Başarı Metrikleri
```

### Veri Akışı

1. **Analiz Aşaması**: Kod tabanı taranır, sorunlar tespit edilir
2. **Planlama Aşaması**: Refactoring stratejisi oluşturulur
3. **Uygulama Aşaması**: Otomatik refactoring işlemleri yapılır
4. **Doğrulama Aşaması**: Testler çalıştırılır, kalite kontrol yapılır
5. **Raporlama Aşaması**: Sonuçlar raporlanır

## Bileşenler ve Arayüzler

### Kod Analizörü Bileşenleri

#### DosyaBoyutAnalizoru
```python
class DosyaBoyutAnalizoru:
    def buyuk_dosyalari_tespit_et(self, klasor_yolu: str) -> List[DosyaRaporu]
    def satir_sayisi_hesapla(self, dosya_yolu: str) -> int
    def yorum_satirlarini_filtrele(self, icerik: str) -> int
```

#### FonksiyonBoyutAnalizoru
```python
class FonksiyonBoyutAnalizoru:
    def buyuk_fonksiyonlari_tespit_et(self, dosya_yolu: str) -> List[FonksiyonRaporu]
    def fonksiyon_satirlarini_say(self, fonksiyon_icerik: str) -> int
    def ast_ile_fonksiyon_analizi(self, dosya_icerik: str) -> List[FonksiyonBilgisi]
```

#### ImportYapisiAnalizoru
```python
class ImportYapisiAnalizoru:
    def mimari_ihlalleri_tespit_et(self, proje_yolu: str) -> List[MimariIhlal]
    def katman_belirle(self, dosya_yolu: str) -> KatmanTuru
    def import_bagimlilikları_analiz_et(self, dosya_yolu: str) -> List[ImportBilgisi]
```

### Refactoring Bileşenleri

#### DosyaBolucu
```python
class DosyaBolucu:
    def dosyayi_bol(self, dosya_yolu: str, bolme_stratejisi: BolmeStratejisi) -> List[YeniDosya]
    def fonksiyonel_gruplari_tespit_et(self, dosya_icerik: str) -> List[FonksiyonelGrup]
    def init_dosyasini_guncelle(self, modul_yolu: str, yeni_dosyalar: List[str]) -> None
```

#### FonksiyonBolucu
```python
class FonksiyonBolucu:
    def fonksiyonu_bol(self, fonksiyon_icerik: str) -> List[YardimciFonksiyon]
    def yardimci_fonksiyon_olustur(self, kod_blogu: str, isim: str) -> str
    def ana_fonksiyonu_guncelle(self, ana_fonksiyon: str, yardimcilar: List[str]) -> str
```

### Doğrulama Bileşenleri

#### TestCalistirici
```python
class TestCalistirici:
    def tum_testleri_calistir(self) -> TestSonucu
    def etkilenen_testleri_guncelle(self, degisen_dosyalar: List[str]) -> None
    def test_coverage_hesapla(self) -> float
```

#### MimariDogrulayici
```python
class MimariDogrulayici:
    def katman_kurallarini_kontrol_et(self) -> List[MimariIhlal]
    def dependency_injection_kontrol_et(self) -> List[DIIhlal]
    def circular_dependency_kontrol_et(self) -> List[CircularDependency]
```

## Veri Modelleri

### Analiz Sonuçları

```python
@dataclass
class DosyaRaporu:
    dosya_yolu: str
    satir_sayisi: int
    limit_asimi: int
    onerilen_bolme: List[str]

@dataclass
class FonksiyonRaporu:
    dosya_yolu: str
    fonksiyon_adi: str
    satir_sayisi: int
    karmasiklik_skoru: int
    bolme_onerileri: List[str]

@dataclass
class MimariIhlal:
    kaynak_dosya: str
    hedef_dosya: str
    ihlal_turu: str
    cozum_onerisi: str
```

### Refactoring Planı

```python
@dataclass
class RefactoringPlani:
    bolunecek_dosyalar: List[DosyaBolmePlani]
    bolunecek_fonksiyonlar: List[FonksiyonBolmePlani]
    duzeltilecek_importlar: List[ImportDuzeltmePlani]
    ortak_moduller: List[OrtakModulPlani]

@dataclass
class DosyaBolmePlani:
    kaynak_dosya: str
    hedef_dosyalar: List[str]
    tasima_haritasi: Dict[str, str]
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Dosya Boyut Tespiti Doğruluğu
*For any* Python dosyası ve satır sayısı, dosya boyut analizörü 120 satırı aşan dosyaları doğru tespit etmelidir
**Validates: Requirements 1.1**

### Property 2: Import Yapısı Korunumu
*For any* dosya bölme işlemi, bölme öncesi ve sonrası import yapısının işlevsel olarak eşdeğer olması gerekir
**Validates: Requirements 1.3**

### Property 3: Init Dosyası Güncelleme Tutarlılığı
*For any* yeni alt dosya oluşturma işlemi, ilgili __init__.py dosyasının otomatik güncellenmesi gerekir
**Validates: Requirements 1.4**

### Property 4: Dosya Boyut Limiti Invariantı
*For any* refactoring işlemi tamamlandığında, tüm dosyalar 120 satır limitini aşmamalıdır
**Validates: Requirements 1.5**

### Property 5: Fonksiyon Boyut Tespiti Doğruluğu
*For any* Python fonksiyonu, fonksiyon boyut analizörü 25 satırı aşan fonksiyonları doğru tespit etmelidir
**Validates: Requirements 2.1**

### Property 6: Fonksiyonel Davranış Korunumu
*For any* fonksiyon bölme işlemi, bölme öncesi ve sonrası fonksiyonun aynı girdi için aynı çıktıyı üretmesi gerekir
**Validates: Requirements 2.3**

### Property 7: Fonksiyon Boyut Limiti Invariantı
*For any* refactoring işlemi tamamlandığında, tüm fonksiyonlar 25 satır limitini aşmamalıdır
**Validates: Requirements 2.5**

### Property 8: UI Katmanı Import Kısıtlaması
*For any* UI katmanındaki dosya, repository veya database katmanından import yapmamalıdır
**Validates: Requirements 3.1**

### Property 9: Katman Sınırları Invariantı
*For any* import düzenlemesi işlemi, katman sınırları korunmalıdır
**Validates: Requirements 3.3**

### Property 10: Dependency Injection Kullanımı
*For any* yeni import yapısı, dependency injection pattern'ini kullanmalıdır
**Validates: Requirements 3.4**

### Property 11: Mimari Kurallar Invariantı
*For any* mimari düzenleme işlemi tamamlandığında, tüm katmanlar mimari kurallara uymalıdır
**Validates: Requirements 3.5**

### Property 12: Kod Tekrarı Tespiti
*For any* kod tabanı tarama işlemi, belirli eşik değerini aşan benzer kod bloklarını tespit etmelidir
**Validates: Requirements 4.1**

### Property 13: Fonksiyonalite Korunumu
*For any* kod taşıma işlemi, taşıma öncesi ve sonrası sistem davranışı aynı kalmalıdır
**Validates: Requirements 4.4**

### Property 14: Referans Güncelleme Tamlığı
*For any* ortak modül oluşturma işlemi, tüm kullanım yerlerinin güncellenmesi gerekir
**Validates: Requirements 4.5**

### Property 15: Standart Başlık Ekleme
*For any* yeni dosya oluşturma işlemi, standart sürüm başlığının eklenmesi gerekir
**Validates: Requirements 5.1**

### Property 16: Eksik Başlık Tespiti
*For any* dosya başlık kontrol işlemi, eksik başlık bilgilerini doğru tespit etmelidir
**Validates: Requirements 5.2**

### Property 17: Changelog Güncelleme
*For any* başlık güncelleme işlemi, changelog bilgilerinin eklenmesi gerekir
**Validates: Requirements 5.3**

### Property 18: Tarih Güncelleme
*For any* dosya değişiklik işlemi, son güncelleme tarihinin güncellenmesi gerekir
**Validates: Requirements 5.4**

### Property 19: Başlık Format Tutarlılığı
*For any* başlık standardizasyon işlemi tamamlandığında, tüm dosyalar aynı formata uymalıdır
**Validates: Requirements 5.5**

### Property 20: Test Güncelleme Tutarlılığı
*For any* dosya bölme işlemi, ilgili testlerin güncellenmesi gerekir
**Validates: Requirements 6.2**

### Property 21: Test Import Güncelleme
*For any* yeni modül oluşturma işlemi, test import yapılarının düzenlenmesi gerekir
**Validates: Requirements 6.3**

### Property 22: Test Başarı Invariantı
*For any* refactoring işlemi tamamlandığında, tüm testler başarılı olmalıdır
**Validates: Requirements 6.4**

### Property 23: Test Coverage Korunumu
*For any* test güncelleme işlemi, test coverage değeri korunmalıdır
**Validates: Requirements 6.5**

### Property 24: Fonksiyonel Gruplama
*For any* büyük dosya analizi, fonksiyonel grupların tespit edilmesi gerekir
**Validates: Requirements 7.1**

### Property 25: İsimlendirme Kuralları
*For any* bölme stratejisi, *_yardimcilari.py, *_dogrulama.py gibi anlamlı isimlerin kullanılması gerekir
**Validates: Requirements 7.2**

### Property 26: Modül Tutarlılığı
*For any* alt dosya oluşturma işlemi, modül içi tutarlılığın korunması gerekir
**Validates: Requirements 7.3**

### Property 27: Public API Korunumu
*For any* dosya bölme işlemi, public API'nin değişmemesi gerekir
**Validates: Requirements 7.4**

### Property 28: Otomatik Dosya Boyut Kontrolü
*For any* refactoring araçları çalıştırma işlemi, dosya boyut kontrollerinin otomatik yapılması gerekir
**Validates: Requirements 8.1**

### Property 29: Otomatik Fonksiyon Boyut Kontrolü
*For any* kod analizi işlemi, fonksiyon boyut kontrollerinin otomatik yapılması gerekir
**Validates: Requirements 8.2**

### Property 30: Otomatik Mimari İhlal Tespiti
*For any* import kontrol işlemi, mimari ihlallerin otomatik tespit edilmesi gerekir
**Validates: Requirements 8.3**

### Property 31: Otomatik PEP8 Kontrolü
*For any* kod kalitesi kontrol işlemi, PEP8 uyumluluğunun doğrulanması gerekir
**Validates: Requirements 8.4**

### Property 32: Otomatik Rapor Üretimi
*For any* otomatik kontrol işlemi tamamlandığında, detaylı raporun üretilmesi gerekir
**Validates: Requirements 8.5**

## Hata Yönetimi

### Hata Türleri

1. **Analiz Hataları**: Dosya okuma, AST parsing hataları
2. **Refactoring Hataları**: Dosya yazma, import güncelleme hataları
3. **Test Hataları**: Test çalıştırma, coverage hesaplama hataları
4. **Doğrulama Hataları**: Mimari kontrol, kalite kontrol hataları

### Hata Kurtarma Stratejileri

- **Geri Alma (Rollback)**: Başarısız refactoring işlemlerinde orijinal duruma dönüş
- **Kısmi Uygulama**: Başarılı olan kısımları koruyarak devam etme
- **Hata Raporlama**: Detaylı hata logları ve kullanıcı bildirimleri
- **Güvenli Mod**: Sadece analiz yapma, değişiklik yapmama seçeneği

## Test Stratejisi

### Unit Testler

- Dosya boyut hesaplama fonksiyonları
- Fonksiyon analiz algoritmaları
- Import yapısı parsing işlemleri
- Refactoring yardımcı fonksiyonları

### Property-Based Testler

- Dosya bölme işlemlerinin tutarlılığı
- Import yapısı korunumu
- Fonksiyonel davranış eşdeğerliği
- Mimari kural uyumluluğu

Her property-based test minimum 100 iterasyon çalıştırılacak ve Hypothesis kütüphanesi kullanılacaktır. Her test, tasarım dokümanındaki ilgili correctness property'yi referans alacak ve şu format kullanılacak: '**Feature: kod-kalitesi-standardizasyon, Property {number}: {property_text}**'

### Entegrasyon Testleri

- Tam refactoring sürecinin end-to-end testi
- Gerçek kod tabanı üzerinde güvenli testler
- Test sonrası otomatik geri alma
- Performans ve bellek kullanımı testleri

### Test Konfigürasyonu

Property-based testler Hypothesis kütüphanesi ile yapılacak ve her test minimum 100 iterasyon çalıştırılacaktır. Unit testler ve property testler birbirini tamamlayacak şekilde tasarlanacaktır: unit testler spesifik örnekleri test ederken, property testler evrensel kuralları doğrulayacaktır.