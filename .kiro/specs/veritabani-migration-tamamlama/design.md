# Veritabanı Migration Tamamlama Tasarım Dokümanı

## Genel Bakış

Bu tasarım, SONTECHSP projesi için PostgreSQL bağlantı katmanı ve Alembic göç sisteminin tamamlanmasını kapsar. Mevcut veritabanı altyapısı büyük ölçüde hazır durumda ancak ilk migration dosyası ve bazı yardımcı fonksiyonlar eksik. Bu tasarım, eksik kısımları tamamlayarak tam işlevsel bir veritabanı altyapısı sağlayacak.

## Mimari

### Katmanlar
```
┌─────────────────────────────────────┐
│           UI Katmanı                │
├─────────────────────────────────────┤
│         Servis Katmanı              │
├─────────────────────────────────────┤
│       Repository Katmanı            │
├─────────────────────────────────────┤
│       Veritabanı Katmanı            │
│  ┌─────────────┬─────────────────┐  │
│  │  PostgreSQL │     SQLite      │  │
│  │   (Ana DB)  │  (Offline POS)  │  │
│  └─────────────┴─────────────────┘  │
└─────────────────────────────────────┘
```

### Bileşenler
- **Bağlantı Yöneticisi**: PostgreSQL ve SQLite bağlantılarını yönetir
- **Session Factory**: SQLAlchemy session'larını oluşturur ve yönetir
- **Migration Sistemi**: Alembic ile şema değişikliklerini yönetir
- **Veri Yükleme Sistemi**: İlk kurulum için temel verileri yükler

## Bileşenler ve Arayüzler

### VeriTabaniBaglanti Sınıfı
```python
class VeriTabaniBaglanti:
    def postgresql_engine_al() -> Engine
    def sqlite_engine_al(dosya_yolu: str) -> Engine
    def postgresql_session() -> ContextManager[Session]
    def sqlite_session() -> ContextManager[Session]
    def baglanti_test_et(veritabani_tipi: str) -> bool
    def tablolari_olustur(veritabani_tipi: str) -> None
```

### Migration Yöneticisi
```python
class MigrationYoneticisi:
    def ilk_migration_olustur() -> str
    def migration_calistir(hedef_versiyon: str = "head") -> None
    def migration_geri_al(hedef_versiyon: str) -> None
    def migration_durumu() -> Dict[str, Any]
```

### Veri Yükleme Sistemi
```python
class VeriYukleyici:
    def temel_verileri_yukle() -> None
    def admin_kullanici_olustur() -> None
    def sistem_rollerini_olustur() -> None
    def sistem_yetkilerini_olustur() -> None
```

## Veri Modelleri

### Temel Tablolar
1. **kullanicilar**: Sistem kullanıcıları
2. **roller**: Kullanıcı rolleri
3. **yetkiler**: Sistem yetkileri
4. **kullanici_rolleri**: Kullanıcı-rol ilişkisi
5. **rol_yetkileri**: Rol-yetki ilişkisi
6. **firmalar**: Firma bilgileri
7. **magazalar**: Mağaza bilgileri
8. **terminaller**: POS terminal bilgileri

### Tablo İlişkileri
```
kullanicilar ←→ kullanici_rolleri ←→ roller
                                      ↓
                                 rol_yetkileri
                                      ↓
                                   yetkiler

firmalar ←→ magazalar ←→ terminaller
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Bağlantı Test Tutarlılığı
*For any* geçerli veritabanı bağlantı parametresi, bağlantı testi başarılı olduğunda aynı parametrelerle tekrar test edildiğinde yine başarılı olmalı
**Validates: Requirements 1.1, 1.3**

### Property 2: SQLite Bağlantı Güvenilirliği  
*For any* geçerli SQLite dosya yolu, bağlantı testi başarılı olmalı ve dosya oluşturulmalı
**Validates: Requirements 1.4**

### Property 3: Bağlantı Test Loglama
*For any* bağlantı testi, test sonucu ne olursa olsun log kaydı oluşturulmalı
**Validates: Requirements 1.5**

### Property 4: Tablo İsimlendirme Standardı
*For any* oluşturulan tablo, ismi Türkçe ASCII karakterler ve snake_case formatında olmalı
**Validates: Requirements 3.1, 3.2**

### Property 5: Foreign Key Bütünlüğü
*For any* foreign key ilişkisi, referans edilen kayıt silindiğinde bağımlı kayıtlar da uygun şekilde işlenmeli
**Validates: Requirements 3.3**

### Property 6: Unique Constraint Korunumu
*For any* unique constraint tanımlı alan, aynı değerle ikinci kayıt eklenmeye çalışıldığında hata vermeli
**Validates: Requirements 3.4**

### Property 7: Session Commit Davranışı
*For any* başarılı veritabanı işlemi, session otomatik olarak commit edilmeli
**Validates: Requirements 4.2**

### Property 8: Session Rollback Davranışı
*For any* hata durumu, session otomatik olarak rollback yapılmalı
**Validates: Requirements 4.3**

### Property 9: Session Kaynak Temizliği
*For any* session kullanımı, context manager çıkışında kaynak temizliği yapılmalı
**Validates: Requirements 4.4**

### Property 10: Context Manager Exception Handling
*For any* context manager kullanımı, exception durumunda otomatik rollback ve temizlik yapılmalı
**Validates: Requirements 4.5**

### Property 11: Migration Durum Sorgusu
*For any* migration durumu, mevcut veritabanı versiyonu doğru şekilde raporlanmalı
**Validates: Requirements 5.3**

### Property 12: Migration Geçmiş Listesi
*For any* migration geçmiş sorgusu, tüm uygulanan migration'lar kronolojik sırada listelenmeli
**Validates: Requirements 5.4**

### Property 13: Temel Veri Tutarlılığı
*For any* temel veri yükleme işlemi, yüklenen veriler referans bütünlüğünü korumalı
**Validates: Requirements 6.5**

## Hata Yönetimi

### Hata Türleri
1. **BaglantiHatasi**: Veritabanı bağlantı hataları
2. **MigrationHatasi**: Migration işlem hataları  
3. **VeriYuklemeHatasi**: Temel veri yükleme hataları
4. **SessionHatasi**: Session yönetim hataları

### Hata İşleme Stratejisi
- Tüm hatalar loglanacak
- Kritik hatalar için sistem yöneticisi bilgilendirilecek
- Hata mesajları Türkçe olacak
- Hata kodları standart olacak

## Test Stratejisi

### Unit Testler
- Bağlantı test fonksiyonları
- Session yönetim fonksiyonları
- Migration yardımcı fonksiyonları
- Veri yükleme fonksiyonları

### Property-Based Testler
Property-based testler **Hypothesis** kütüphanesi kullanılarak yazılacak ve minimum **100 iterasyon** çalıştırılacak.

Her property-based test şu format ile etiketlenecek:
`**Feature: veritabani-migration-tamamlama, Property {number}: {property_text}**`

Property testler şu alanları kapsayacak:
- Bağlantı test tutarlılığı
- Session davranış doğruluğu
- Migration durum sorguları
- Veri tutarlılık kontrolleri

### Entegrasyon Testleri
- PostgreSQL bağlantı testleri
- SQLite bağlantı testleri
- Migration upgrade/downgrade testleri
- Temel veri yükleme testleri

### Test Veri Yönetimi
- Test veritabanları izole edilecek
- Her test sonrası temizlik yapılacak
- Test verileri rastgele üretilecek
- Gerçek veriler test ortamında kullanılmayacak