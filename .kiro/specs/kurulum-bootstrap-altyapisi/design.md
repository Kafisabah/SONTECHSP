# Kurulum Bootstrap Altyapısı - Tasarım Belgesi

## Genel Bakış

SONTECHSP uygulaması için Windows ortamında ilk kurulum ve çalıştırma sürecini otomatikleştiren bootstrap altyapısı tasarımı. Sistem, uygulama ilk açılışta gerekli tüm hazırlık işlemlerini otomatik olarak gerçekleştirecek ve kullanıcıya hazır bir sistem sunacaktır.

## Mimari

Bootstrap sistemi, katmanlı mimari prensiplerine uygun olarak tasarlanmıştır:

```
uygulama/kurulum/
├── sabitler.py          # Klasör ve dosya sabitleri
├── klasorler.py         # Klasör yönetimi işlemleri
├── ayar_olusturucu.py   # Yapılandırma dosyası yönetimi
├── veritabani_kontrol.py # DB bağlantı ve migration
├── admin_olusturucu.py  # Varsayılan kullanıcı oluşturma
└── baslat.py           # Ana bootstrap koordinatörü
```

## Bileşenler ve Arayüzler

### Sabitler Modülü
```python
# Klasör sabitleri
VERI_KLASORU = "veri"
LOG_KLASORU = "loglar"
YEDEK_KLASORU = "yedekler"
RAPOR_KLASORU = "raporlar"
CONFIG_DOSYA_ADI = "config.json"
```

### Klasör Yönetimi Arayüzü
```python
def klasorleri_olustur(proje_koku: Path) -> None
def klasor_var_mi(proje_koku: Path) -> bool
```

### Ayar Yönetimi Arayüzü
```python
def varsayilan_ayarlar() -> dict
def ayar_dosyasi_var_mi(proje_koku: Path) -> bool
def ayar_dosyasi_olustur(proje_koku: Path, ayarlar: dict) -> None
def ayarlari_yukle(proje_koku: Path) -> dict
```

### Veritabanı Kontrol Arayüzü
```python
def baglanti_test_et(veritabani_url: str) -> None
def gocleri_calistir(proje_koku: Path) -> None
```

### Admin Oluşturucu Arayüzü
```python
def admin_varsa_gec(session: Session) -> bool
def admin_olustur(session: Session, kullanici_adi: str, sifre: str) -> None
```

### Ana Bootstrap Arayüzü
```python
def ilk_calistirma_hazirla(proje_koku: Path) -> None
```

## Veri Modelleri

### Yapılandırma Modeli
```json
{
  "veritabani_url": "postgresql://kullanici:sifre@localhost:5432/sontechsp",
  "ortam": "dev",
  "log_seviyesi": "INFO"
}
```

### Klasör Yapısı Modeli
```
proje_koku/
├── veri/
├── loglar/
├── yedekler/
├── raporlar/
└── config.json
```

## Doğruluk Özellikleri

*Bir özellik, sistemin tüm geçerli çalıştırmalarında doğru olması gereken bir karakteristik veya davranıştır - esasen, sistemin ne yapması gerektiği hakkında resmi bir ifadedir. Özellikler, insan tarafından okunabilir spesifikasyonlar ile makine tarafından doğrulanabilir doğruluk garantileri arasında köprü görevi görür.*

### Özellik 1: Klasör Oluşturma İdempotentliği
*Herhangi bir* proje kök dizini için, klasör oluşturma işlemini iki kez çalıştırmak, bir kez çalıştırmakla aynı sonucu vermeli
**Doğrular: Gereksinimler 1.2**

### Özellik 2: Gerekli Klasörlerin Varlığı
*Herhangi bir* geçerli proje kök dizini için, bootstrap işlemi sonrasında tüm gerekli klasörler (veri, loglar, yedekler, raporlar) mevcut olmalı
**Doğrular: Gereksinimler 1.1**

### Özellik 3: Hatalı Yol Yönetimi
*Herhangi bir* geçersiz veya erişilemeyen yol için, klasör oluşturma işlemi anlaşılır hata mesajı içeren istisna fırlatmalı
**Doğrular: Gereksinimler 1.3**

### Özellik 4: Ayar Dosyası İdempotentliği
*Herhangi bir* proje kök dizini için, ayar dosyası oluşturma işlemini iki kez çalıştırmak, mevcut ayarları korumalı
**Doğrular: Gereksinimler 2.2**

### Özellik 5: Ayar Dosyası İçerik Bütünlüğü
*Herhangi bir* yeni oluşturulan ayar dosyası, veritabani_url, ortam ve log_seviyesi alanlarını içermeli
**Doğrular: Gereksinimler 2.3**

### Özellik 6: JSON Format Geçerliliği
*Herhangi bir* oluşturulan ayar dosyası, geçerli JSON formatında olmalı ve başarıyla parse edilebilmeli
**Doğrular: Gereksinimler 2.4**

### Özellik 7: Veritabanı Bağlantı Hata Yönetimi
*Herhangi bir* geçersiz veritabanı URL'i için, bağlantı testi DogrulamaHatasi istisnası fırlatmalı
**Doğrular: Gereksinimler 3.2**

### Özellik 8: Migration Hata Yönetimi
*Herhangi bir* migration hatası durumunda, sistem hata detaylarını içeren istisna fırlatmalı
**Doğrular: Gereksinimler 4.2**

### Özellik 9: Admin Kullanıcı İdempotentliği
*Herhangi bir* veritabanı durumu için, admin oluşturma işlemini iki kez çalıştırmak, mevcut admin kullanıcısını korumalı
**Doğrular: Gereksinimler 5.2**

### Özellik 10: Şifre Hash Güvenliği
*Herhangi bir* oluşturulan admin kullanıcısı için, şifre bcrypt hash algoritması ile hashlenmeli
**Doğrular: Gereksinimler 5.3**

### Özellik 11: Kullanıcı Oluşturma Hata Loglama
*Herhangi bir* kullanıcı oluşturma hatası durumunda, sistem hata detaylarını loglamalı
**Doğrular: Gereksinimler 5.4**

### Özellik 12: Bootstrap Hata Yönetimi
*Herhangi bir* bootstrap adımında hata oluştuğunda, sistem anlaşılır hata mesajı ile işlemi durdurmalı
**Doğrular: Gereksinimler 6.2**

## Hata Yönetimi

### Hata Türleri
- `DogrulamaHatasi`: Veritabanı bağlantı hataları
- `KlasorHatasi`: Klasör oluşturma/erişim hataları
- `AyarHatasi`: Yapılandırma dosyası hataları
- `MigrationHatasi`: Alembic migration hataları
- `KullaniciHatasi`: Admin kullanıcı oluşturma hataları

### Hata Yönetim Stratejisi
1. Tüm hatalar anlaşılır Türkçe mesajlarla raporlanır
2. Kritik hatalar sistem başlatmayı durdurur
3. Tüm hatalar log dosyasına kaydedilir
4. Kullanıcıya düzeltme önerileri sunulur

## Test Stratejisi

### Unit Test Yaklaşımı
- Her modül için ayrı test dosyaları
- Mock nesneler ile dış bağımlılıkları izole etme
- Hata durumları için özel test senaryoları
- Dosya sistemi işlemleri için geçici dizin kullanımı

### Property-Based Test Yaklaşımı
Property-based testler için **Hypothesis** kütüphanesi kullanılacaktır. Her property-based test minimum 100 iterasyon çalıştırılacaktır.

Property-based testler şu alanları kapsayacaktır:
- Klasör oluşturma idempotentliği
- Ayar dosyası format geçerliliği
- Veritabanı bağlantı hata yönetimi
- Admin kullanıcı oluşturma idempotentliği
- Bootstrap süreç bütünlüğü

Her property-based test, tasarım belgesindeki ilgili doğruluk özelliğine referans verecek şekilde etiketlenecektir: **Özellik: kurulum-bootstrap-altyapisi, Özellik {numara}: {özellik_metni}**

### Entegrasyon Testleri
- Tam bootstrap sürecinin end-to-end testi
- Gerçek PostgreSQL veritabanı ile test
- Windows dosya sistemi uyumluluğu testi
- Alembic migration entegrasyonu testi