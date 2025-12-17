# CRM Çekirdek Modülü Tasarım Dokümanı

## Genel Bakış

CRM Çekirdek Modülü, SONTECHSP sisteminin müşteri yönetimi ve sadakat programı işlevselliğini sağlayan temel bileşendir. Modül, temiz mimari prensipleri doğrultusunda servis, repository ve model katmanlarından oluşur. POS ve satış belgeleri sistemleri ile entegrasyon için hook sözleşmeleri sağlar.

## Mimari

### Katman Yapısı
```
uygulama/moduller/crm/
├── dto.py              # Veri transfer objeleri
├── sabitler.py         # Sabit değerler ve enum'lar
├── depolar.py          # Repository katmanı
├── servisler.py        # İş mantığı katmanı
├── entegrasyon_kancalari.py  # Entegrasyon hook'ları
└── __init__.py         # Modül export'ları

uygulama/veritabani/modeller/
└── crm.py              # SQLAlchemy modelleri

uygulama/veritabani/gocler/versions/
└── xxxx_crm_musteri_sadakat.py  # Alembic migration
```

### Bağımlılık Yönü
```
UI Katmanı (Gelecekte)
    ↓
Servis Katmanı (servisler.py)
    ↓
Repository Katmanı (depolar.py)
    ↓
Model Katmanı (crm.py)
    ↓
Veritabanı
```

## Bileşenler ve Arayüzler

### DTO Sınıfları
- **MusteriOlusturDTO**: Yeni müşteri oluşturma için veri transfer objesi
- **MusteriGuncelleDTO**: Müşteri güncelleme için opsiyonel alanlar
- **PuanIslemDTO**: Puan işlemleri için veri transfer objesi
- **MusteriAraDTO**: Müşteri arama kriterleri için veri transfer objesi

### Servis Sınıfları
- **MusteriServisi**: Müşteri CRUD işlemleri ve arama
- **SadakatServisi**: Puan kazanım, harcama ve bakiye yönetimi

### Repository Sınıfları
- **MusteriDeposu**: Müşteri veritabanı erişim katmanı
- **SadakatDeposu**: Sadakat puan veritabanı erişim katmanı

### Entegrasyon Arayüzleri
- **pos_satis_tamamlandi()**: POS satış sonrası puan kazanımı
- **satis_belgesi_olustu()**: Satış belgesi sonrası puan kazanımı

## Veri Modelleri

### Musteriler Tablosu
```sql
CREATE TABLE musteriler (
    id SERIAL PRIMARY KEY,
    ad VARCHAR(100) NOT NULL,
    soyad VARCHAR(100) NOT NULL,
    telefon VARCHAR(20) UNIQUE,
    eposta VARCHAR(255) UNIQUE,
    vergi_no VARCHAR(20),
    adres TEXT,
    aktif_mi BOOLEAN DEFAULT TRUE,
    olusturulma_zamani TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    guncellenme_zamani TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Sadakat_Puanlari Tablosu
```sql
CREATE TABLE sadakat_puanlari (
    id SERIAL PRIMARY KEY,
    musteri_id INTEGER REFERENCES musteriler(id),
    islem_turu VARCHAR(20) NOT NULL,
    puan INTEGER NOT NULL,
    aciklama TEXT,
    referans_turu VARCHAR(50),
    referans_id INTEGER,
    olusturulma_zamani TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### İndeksler
- `idx_musteriler_telefon` ON musteriler(telefon)
- `idx_musteriler_eposta` ON musteriler(eposta)
- `idx_sadakat_musteri_id` ON sadakat_puanlari(musteri_id)
- `idx_sadakat_referans` ON sadakat_puanlari(referans_turu, referans_id)

## Doğruluk Özellikleri

*Bir özellik, sistemin tüm geçerli çalıştırmalarında doğru olması gereken bir karakteristik veya davranıştır - esasen, sistemin ne yapması gerektiği hakkında resmi bir ifadedir. Özellikler, insan tarafından okunabilir spesifikasyonlar ile makine tarafından doğrulanabilir doğruluk garantileri arasında köprü görevi görür.*

### Property Reflection

Prework analizinde belirlenen testable property'leri gözden geçirdiğimde, bazı redundant property'ler tespit ettim:

**Redundant Property'ler:**
- 1.2 ve 2.2 (telefon benzersizliği) → tek property'de birleştirilebilir
- 1.3 ve 2.3 (e-posta geçerliliği ve benzersizliği) → tek property'de birleştirilebilir  
- 8.2 ve 9.2 (1 TL = 1 puan kuralı) → tek property'de birleştirilebilir
- 8.1 ve 9.1 (puan hesaplama fonksiyonu çağırma) → tek property'de birleştirilebilir

**Birleştirilebilir Property'ler:**
- 4.2, 5.4, 10.1 (işlem türü atama) → tek comprehensive property
- 1.5, 2.4, 4.5 (otomatik timestamp atama) → tek property
- 8.3 ve 9.4 (geçersiz müşteri ID handling) → tek property

Bu reflection sonrasında, her property'nin benzersiz validation değeri sağladığından emin oldum.

**Property 1: Müşteri alan zorunluluğu**
*Her* müşteri oluşturma işlemi için, ad ve soyad alanları boş olamaz
**Validates: Requirements 1.1**

**Property 2: Telefon benzersizliği**
*Her* telefon numarası için, sistemde sadece bir müşteri kaydı bulunabilir (oluşturma ve güncelleme)
**Validates: Requirements 1.2, 2.2**

**Property 3: E-posta geçerliliği ve benzersizliği**
*Her* e-posta adresi için, geçerli format kontrolü yapılır ve sistemde sadece bir müşteri kaydı bulunabilir
**Validates: Requirements 1.3, 2.3**

**Property 4: Varsayılan aktif durum**
*Her* yeni oluşturulan müşteri için, aktif_mi alanı True olarak atanır
**Validates: Requirements 1.4**

**Property 5: Otomatik zaman damgası**
*Her* müşteri ve puan işlemi için, oluşturulma ve güncellenme zamanları otomatik atanır
**Validates: Requirements 1.5, 2.4, 4.5**

**Property 6: Kısmi güncelleme**
*Her* müşteri güncelleme işlemi için, sadece gönderilen alanlar değişir, diğerleri korunur
**Validates: Requirements 2.1**

**Property 7: Geçersiz ID hata yönetimi**
*Her* geçersiz müşteri ID'si ile yapılan işlem için, DogrulamaHatasi fırlatılır
**Validates: Requirements 2.5**

**Property 8: Ad/soyad kısmi arama**
*Her* ad/soyad arama işlemi için, kısmi eşleşme ile sonuç döndürülür
**Validates: Requirements 3.1**

**Property 9: Telefon/e-posta tam arama**
*Her* telefon veya e-posta arama işlemi için, sadece tam eşleşen sonuçlar döndürülür
**Validates: Requirements 3.2, 3.3**

**Property 10: Çoklu kriter AND mantığı**
*Her* birden fazla arama kriteri için, AND mantığı ile filtreleme yapılır
**Validates: Requirements 3.4**

**Property 11: Pozitif puan kontrolü**
*Her* puan kazanım işlemi için, sadece pozitif puan değerleri kabul edilir
**Validates: Requirements 4.1**

**Property 12: İşlem türü otomatik atama**
*Her* puan işlemi için, işlem türü otomatik olarak doğru değere atanır (KAZANIM, HARCAMA, DUZELTME)
**Validates: Requirements 4.2, 5.4, 10.1**

**Property 13: Referans bilgisi saklama**
*Her* referans bilgisi verilen puan işlemi için, referans türü ve ID'si kaydedilir
**Validates: Requirements 4.3, 8.4, 9.3**

**Property 14: Bakiye kontrolü**
*Her* puan harcama işlemi için, müşteri bakiyesi kontrol edilir ve yetersizse DogrulamaHatasi fırlatılır
**Validates: Requirements 5.1, 5.2**

**Property 15: Başarılı harcama kaydı**
*Her* yeterli bakiyeli puan harcama işlemi için, işlem başarıyla kaydedilir
**Validates: Requirements 5.3**

**Property 16: Bakiye hesaplama formülü**
*Her* bakiye sorgulaması için, KAZANIM - HARCAMA formülü kullanılarak doğru bakiye hesaplanır
**Validates: Requirements 6.1, 6.4**

**Property 17: Hareket listesi sıralama**
*Her* puan hareketleri sorgulaması için, sonuçlar tarih sırasına göre sıralanır
**Validates: Requirements 7.1**

**Property 18: Limit parametresi**
*Her* limit parametresi verilen sorgu için, belirtilen sayıda kayıt döndürülür
**Validates: Requirements 7.2, 7.3**

**Property 19: Puan hesaplama kuralı**
*Her* entegrasyon işlemi için, 1 TL = 1 puan kuralı uygulanır
**Validates: Requirements 8.2, 9.2**

**Property 20: Entegrasyon hata yönetimi**
*Her* geçersiz müşteri ID'si ile entegrasyon işlemi için, işlem sessizce atlanır
**Validates: Requirements 8.3, 9.4**

**Property 21: Entegrasyon başarısızlık yönetimi**
*Her* başarısız puan işlemi için, hata loglanır ancak ana işlem (POS/satış belgesi) durdurulmaz
**Validates: Requirements 8.5**

**Property 22: Düzeltme bakiye kontrolü**
*Her* negatif puan düzeltme işlemi için, bakiye kontrolü yapılır
**Validates: Requirements 10.2, 10.3**

**Property 23: Düzeltme açıklama zorunluluğu**
*Her* puan düzeltme işlemi için, açıklama alanı zorunludur
**Validates: Requirements 10.4**

## Hata Yönetimi

### Hata Türleri
- **DogrulamaHatasi**: Veri doğrulama hataları (yetersiz bakiye, geçersiz ID, vb.)
- **AlanHatasi**: Alan seviyesi doğrulama hataları (geçersiz e-posta formatı, vb.)
- **EntegrasyonHatasi**: Dış sistem entegrasyon hataları

### Hata Yönetimi Stratejisi
- Tüm hatalar Türkçe mesajlarla fırlatılır
- Kritik hatalar loglanır
- Entegrasyon hataları ana işlemi durdurmaz
- Transaction rollback otomatik yapılır

## Test Stratejisi

### Dual Testing Yaklaşımı

Hem unit testler hem de property-based testler kullanılacaktır:

**Unit Testler:**
- Spesifik örnekleri doğrular
- Edge case'leri test eder
- Entegrasyon noktalarını kontrol eder

**Property-Based Testler:**
- Evrensel özellikleri doğrular
- Rastgele veri ile geniş kapsamlı test sağlar
- Hypothesis kütüphanesi kullanılacak
- Her test minimum 100 iterasyon çalışacak

### Test Kütüphanesi
- **Property-Based Testing**: Hypothesis (Python)
- **Unit Testing**: pytest
- **Database Testing**: pytest-postgresql

### Test Gereksinimleri
- Her property-based test, tasarım dokümanındaki correctness property'yi referans alacak
- Test etiketleme formatı: `**Feature: crm-cekirdek-modulu, Property {number}: {property_text}**`
- Her correctness property tek bir property-based test ile implement edilecek
- Test coverage minimum %80 olacak

### Test Veri Üretimi
- Müşteri verileri için smart generator'lar
- Geçerli/geçersiz e-posta formatları
- Türkçe karakter desteği
- Telefon numarası formatları
- Puan işlem senaryoları