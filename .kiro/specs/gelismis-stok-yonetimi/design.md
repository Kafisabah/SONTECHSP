# Gelişmiş Stok Yönetimi Sistemi - Tasarım Dokümanı

## Genel Bakış

Bu dokümantasyon, SONTECHSP için gelişmiş stok yönetimi sisteminin teknik tasarımını tanımlar. Sistem, çoklu mağaza/depo ortamında çalışan, eş zamanlı erişimi destekleyen, negatif stok kontrolü yapan ve POS ile e-ticaret entegrasyonu sağlayan kapsamlı bir stok yönetimi çözümüdür.

Sistem, katmanlı mimari prensiplerine uygun olarak tasarlanmış olup, UI -> Service -> Repository -> Database katman yapısını takip eder. PostgreSQL ana veritabanı olarak kullanılırken, POS offline durumları için SQLite cache mekanizması entegre edilmiştir.

## Mimari

### Katman Yapısı

```
┌─────────────────────────────────────────┐
│              UI Katmanı                 │
│         (PyQt6 Arayüzleri)             │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│            Servis Katmanı               │
│        (İş Kuralları & Akış)           │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          Repository Katmanı             │
│        (Veri Erişim Katmanı)           │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          Veritabanı Katmanı             │
│    (SQLAlchemy Modeller & Alembic)     │
└─────────────────────────────────────────┘
```

### Modül Organizasyonu

```
sontechsp/uygulama/moduller/stok/
├── models/              # SQLAlchemy modelleri
│   ├── urun.py         # Ürün modeli
│   ├── barkod.py       # Barkod modeli
│   ├── stok_hareket.py # Stok hareket modeli
│   └── stok_bakiye.py  # Stok bakiye modeli
├── repositories/        # Veri erişim katmanı
│   ├── urun_repository.py
│   ├── barkod_repository.py
│   ├── stok_hareket_repository.py
│   └── stok_bakiye_repository.py
├── services/           # İş kuralları katmanı
│   ├── urun_service.py
│   ├── barkod_service.py
│   ├── stok_hareket_service.py
│   └── stok_yonetim_service.py
└── dto/               # Veri transfer objeleri
    ├── urun_dto.py
    ├── stok_hareket_dto.py
    └── stok_rapor_dto.py
```

## Bileşenler ve Arayüzler

### Ana Bileşenler

#### 1. Ürün Yönetimi Bileşeni
- **UrunService**: Ürün CRUD işlemleri ve iş kuralları
- **UrunRepository**: Ürün veri erişim işlemleri
- **Urun Model**: SQLAlchemy ürün modeli

#### 2. Barkod Yönetimi Bileşeni
- **BarkodService**: Barkod işlemleri ve doğrulama
- **BarkodRepository**: Barkod veri erişim işlemleri
- **Barkod Model**: SQLAlchemy barkod modeli

#### 3. Stok Hareket Bileşeni
- **StokHareketService**: Stok giriş/çıkış işlemleri
- **StokHareketRepository**: Hareket kayıtları veri erişimi
- **StokHareket Model**: SQLAlchemy stok hareket modeli

#### 4. Stok Yönetim Bileşeni
- **StokYonetimService**: Ana stok yönetim koordinatörü
- **StokBakiyeRepository**: Stok bakiye hesaplamaları
- **NegatifStokKontrol**: Negatif stok kontrol mekanizması

### Arayüz Sözleşmeleri

#### IUrunRepository
```python
class IUrunRepository:
    def ekle(self, urun: UrunDTO) -> int
    def guncelle(self, urun_id: int, urun: UrunDTO) -> bool
    def sil(self, urun_id: int) -> bool
    def id_ile_getir(self, urun_id: int) -> UrunDTO
    def stok_kodu_ile_getir(self, stok_kodu: str) -> UrunDTO
    def ara(self, arama_terimi: str) -> List[UrunDTO]
```

#### IStokHareketRepository
```python
class IStokHareketRepository:
    def hareket_ekle(self, hareket: StokHareketDTO) -> int
    def bakiye_getir(self, urun_id: int, depo_id: int) -> Decimal
    def hareket_listesi(self, filtre: StokHareketFiltreDTO) -> List[StokHareketDTO]
    def kilitle_ve_bakiye_getir(self, urun_id: int, depo_id: int) -> Decimal
```

## Veri Modelleri

### Ürün Modeli
```python
class Urun:
    id: int (PK)
    stok_kodu: str (UNIQUE, NOT NULL)
    urun_adi: str (NOT NULL)
    birim: str (NOT NULL)
    kdv_orani: Decimal (NOT NULL)
    kritik_seviye: Decimal (DEFAULT 10)
    aktif: bool (DEFAULT True)
    olusturma_tarihi: datetime
    guncelleme_tarihi: datetime
```

### Barkod Modeli
```python
class Barkod:
    id: int (PK)
    urun_id: int (FK -> Urun.id)
    barkod: str (UNIQUE, NOT NULL)
    aktif: bool (DEFAULT True)
    olusturma_tarihi: datetime
```

### Stok Hareket Modeli
```python
class StokHareket:
    id: int (PK)
    urun_id: int (FK -> Urun.id)
    depo_id: int (FK -> Depo.id)
    hareket_turu: str (GIRIS/CIKIS/SAYIM/TRANSFER)
    miktar: Decimal (NOT NULL)
    birim_fiyat: Decimal
    aciklama: str
    referans_no: str
    kullanici_id: int (FK -> Kullanici.id)
    hareket_tarihi: datetime (DEFAULT NOW)
```

### Stok Bakiye Modeli
```python
class StokBakiye:
    id: int (PK)
    urun_id: int (FK -> Urun.id)
    depo_id: int (FK -> Depo.id)
    toplam_miktar: Decimal (DEFAULT 0)
    rezerve_miktar: Decimal (DEFAULT 0)
    kullanilabilir_miktar: Decimal (COMPUTED)
    son_guncelleme: datetime
    
    # Composite unique constraint
    UNIQUE(urun_id, depo_id)
```
## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

Gereksinimler dokümanındaki 50 kabul kriteri analiz edildi. Redundancy analizi sonrası aşağıdaki properties birleştirildi veya elendi:

- **Stok hareket kayıt properties (3.3, 3.5)** → Tek property'de birleştirildi
- **Negatif stok kontrol properties (4.1, 4.2, 4.3)** → Edge case olarak işaretlendi, tek property'de toplandı  
- **Transaction properties (5.4, 7.1, 7.4)** → Transaction tutarlılığı property'sinde birleştirildi
- **Rapor properties (10.1-10.5)** → Rapor filtreleme property'sinde birleştirildi
- **Barkod yönetim properties (2.1, 2.2)** → Barkod benzersizliği property'sinde birleştirildi

### Core Properties

**Property 1: Ürün kayıt tutarlılığı**
*For any* geçerli ürün bilgisi, sistem ürünü benzersiz stok kodu ile kaydetmeli ve tüm zorunlu alanları doğrulamalı
**Validates: Requirements 1.1, 1.2**

**Property 2: Ürün güncelleme izlenebilirliği**
*For any* ürün güncelleme işlemi, sistem değişiklikleri kaydetmeli ve güncelleme zamanını işaretlemeli
**Validates: Requirements 1.3**

**Property 3: Ürün arama tutarlılığı**
*For any* arama terimi, sistem stok kodu veya ürün adına göre ilgili sonuçları döndürmeli
**Validates: Requirements 1.4**

**Property 4: Ürün silme koruması**
*For any* stok hareketi olan ürün, sistem silme işlemini engellemeli
**Validates: Requirements 1.5**

**Property 5: Barkod benzersizliği ve arama tutarlılığı**
*For any* ürüne eklenen barkod, sistem barkodu benzersiz olarak kaydetmeli ve barkod ile arama yapıldığında doğru ürün bilgilerini döndürmeli
**Validates: Requirements 2.1, 2.2**

**Property 6: Çoklu barkod desteği ve koruma**
*For any* ürün, sistem birden fazla barkodu desteklemeli ancak barkod silindiğinde en az bir barkodun kalmasını sağlamalı
**Validates: Requirements 2.3, 2.5**

**Property 7: Barkod hata yönetimi**
*For any* geçersiz barkod girişi, sistem uygun hata mesajı döndürmeli
**Validates: Requirements 2.4**

**Property 8: Stok hareket kayıt tutarlılığı**
*For any* stok hareketi, sistem hareket türüne göre doğru işaret (pozitif/negatif) ile kaydedmeli ve tüm gerekli bilgileri saklamalı
**Validates: Requirements 3.1, 3.2, 3.3, 3.5**

**Property 9: Stok bakiye güncelleme tutarlılığı**
*For any* stok hareketi tamamlandığında, sistem stok bakiyesini doğru şekilde güncellemeli
**Validates: Requirements 3.4**

**Property 10: Negatif stok kontrol kuralları**
*For any* stok çıkış işlemi, sistem stok bakiyesine göre uygun kontrol yapmalı: sıfırda uyarı, -1 ile -5 arası uyarı ile izin, -5'ten küçükte engelleme
**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

**Property 11: Eş zamanlı erişim kontrolü**
*For any* eş zamanlı stok işlemi, sistem PostgreSQL SELECT FOR UPDATE kullanarak sadece bir işlemin tamamlanmasına izin vermeli ve çakışmaları sırayla işlemeli
**Validates: Requirements 5.1, 5.2, 5.5**

**Property 12: Transaction tutarlılığı ve kilit yönetimi**
*For any* transaction işlemi, sistem başarısızlık durumunda tüm değişiklikleri geri almalı, başarı durumunda kilitleri serbest bırakmalı ve 5 saniyeden fazla süren kilitlemelerde kullanıcıya bilgi vermeli
**Validates: Requirements 5.3, 5.4, 7.1, 7.4**

**Property 13: Stok sayım tutarlılığı**
*For any* stok sayım işlemi, sistem mevcut bakiye ile sayım miktarını karşılaştırmalı, farkı kaydetmeli ve bakiyeyi güncellemeli
**Validates: Requirements 6.1, 6.2, 6.3, 6.4**

**Property 14: Sayım iptal koruması**
*For any* iptal edilen sayım işlemi, sistem hiçbir değişiklik yapmamalı
**Validates: Requirements 6.5**

**Property 15: Transfer işlem tutarlılığı**
*For any* stok transfer işlemi, sistem kaynak depoda yeterli stok kontrolü yapmalı, tek transaction içinde her iki depo için TRANSFER türünde hareket kaydetmeli ve referans numarasını saklamalı
**Validates: Requirements 7.1, 7.2, 7.3, 7.5**

**Property 16: Kritik stok yönetimi**
*For any* kritik stok sorgusu, sistem stok bakiyesi kritik seviyenin altındaki ürünleri listelemeli, ürün bazlı tanımlı seviyeyi öncelemeli, tanımsızsa varsayılan 10 birim kullanmalı ve depo bazında gruplandırmalı
**Validates: Requirements 8.1, 8.3, 8.4, 8.5**

**Property 17: Kritik stok uyarı sistemi**
*For any* kritik seviyeye düşen ürün, sistem otomatik uyarı oluşturmalı
**Validates: Requirements 8.2**

**Property 18: Gerçek zamanlı stok entegrasyonu**
*For any* stok değişikliği, sistem değişikliği gerçek zamanlı olarak yansıtmalı ve POS/e-ticaret entegrasyonlarını doğru işlemeli
**Validates: Requirements 9.1, 9.2**

**Property 19: Stok rezervasyon yönetimi**
*For any* rezervasyon işlemi, sistem rezervasyonu doğru yapmalı, iptal durumunda serbest bırakmalı ve kullanılabilir miktarı doğru hesaplamalı
**Validates: Requirements 9.3, 9.4, 9.5**

**Property 20: Rapor filtreleme tutarlılığı**
*For any* rapor talebi, sistem tarih aralığı, hareket türü, ürün ve depo bazlı filtrelemeler yapmalı ve CSV export sağlamalı
**Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5**

## Hata Yönetimi

### Hata Kategorileri

#### 1. Veri Doğrulama Hataları
- **UrunValidationError**: Ürün bilgilerinde eksik/hatalı veri
- **BarkodValidationError**: Barkod formatı/benzersizlik hataları
- **StokHareketValidationError**: Stok hareket bilgilerinde hata

#### 2. İş Kuralı Hataları
- **NegatifStokError**: Negatif stok limit aşımı
- **YetersizStokError**: Transfer için yetersiz stok
- **EsZamanliErisimError**: Eş zamanlı erişim çakışması

#### 3. Sistem Hataları
- **VeritabaniError**: Veritabanı bağlantı/işlem hataları
- **TransactionError**: Transaction rollback hataları
- **KilitlenmeError**: Deadlock durumları

### Hata Yönetim Stratejisi

```python
class StokHataYoneticisi:
    def hata_yakala(self, hata: Exception) -> HataYaniti:
        if isinstance(hata, VeriDogrulamaHatasi):
            return self.dogrulama_hatasi_isle(hata)
        elif isinstance(hata, IsKuraliHatasi):
            return self.is_kurali_hatasi_isle(hata)
        elif isinstance(hata, SistemHatasi):
            return self.sistem_hatasi_isle(hata)
        else:
            return self.bilinmeyen_hata_isle(hata)
```

## Test Stratejisi

### Dual Testing Yaklaşımı

Sistem hem unit testler hem de property-based testler ile kapsamlı şekilde test edilecektir:

#### Unit Testing
- Spesifik örnekler ve edge case'ler için unit testler yazılacak
- Bileşenler arası entegrasyon noktaları test edilecek
- Hata durumları ve exception handling test edilecek
- Mock objeler kullanılarak izole testler yapılacak

#### Property-Based Testing
- **Hypothesis** kütüphanesi kullanılacak (Python için PBT kütüphanesi)
- Her property-based test minimum 100 iterasyon çalıştırılacak
- Her property test, tasarım dokümanındaki ilgili correctness property'yi implement edecek
- Property testler şu format ile etiketlenecek: **Feature: gelismis-stok-yonetimi, Property {number}: {property_text}**

#### Test Konfigürasyonu
```python
# Hypothesis ayarları
@given(strategies.text(), strategies.integers())
@settings(max_examples=100, deadline=None)
def test_property_urun_kayit_tutarliligi(urun_adi, stok_kodu):
    # Property 1 implementasyonu
    pass
```

#### Test Kapsamı
- **Unit testler**: Spesifik senaryolar, hata durumları, entegrasyon noktaları
- **Property testler**: Genel davranış kuralları, veri tutarlılığı, iş kuralları
- **Integration testler**: Katmanlar arası etkileşim, veritabanı işlemleri
- **Performance testler**: Eş zamanlı erişim, büyük veri setleri

Her correctness property için ayrı bir property-based test yazılacak ve bu testler implementation sırasında ilgili kod ile birlikte geliştirilecektir.