# Kurulum Bootstrap Altyapısı - Gereksinimler Belgesi

## Giriş

SONTECHSP uygulaması için Windows ortamında ilk kurulum ve çalıştırma sürecini otomatikleştiren bootstrap altyapısı. Uygulama ilk açılışta gerekli klasörleri oluşturacak, ayar dosyalarını hazırlayacak, PostgreSQL bağlantısını test edecek, Alembic göçlerini çalıştıracak ve varsayılan admin kullanıcısını oluşturacak.

## Sözlük

- **Bootstrap_Sistemi**: Uygulamanın ilk çalıştırılması için gerekli tüm hazırlık işlemlerini gerçekleştiren sistem
- **Ayar_Dosyasi**: Uygulama yapılandırma bilgilerini içeren config.json dosyası
- **Alembic_Gocleri**: Veritabanı şema değişikliklerini yöneten migration dosyaları
- **Admin_Kullanici**: Sistem yöneticisi yetkilerine sahip varsayılan kullanıcı hesabı
- **Proje_Koku**: Uygulamanın ana dizini (root directory)
- **Klasor_Yapisi**: Uygulamanın çalışması için gerekli dizin hiyerarşisi

## Gereksinimler

### Gereksinim 1

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, uygulamayı ilk kez çalıştırdığımda gerekli klasör yapısının otomatik oluşmasını istiyorum, böylece manuel klasör oluşturma işlemi yapmam gerekmez.

#### Kabul Kriterleri

1. WHEN uygulama ilk kez çalıştırıldığında THEN Bootstrap_Sistemi SHALL veri, loglar, yedekler ve raporlar klasörlerini oluştur
2. WHEN klasörler zaten mevcutsa THEN Bootstrap_Sistemi SHALL mevcut klasörleri korumalı ve hata vermemeli
3. WHEN klasör oluşturma işlemi başarısızsa THEN Bootstrap_Sistemi SHALL anlaşılır hata mesajı döndürmeli
4. WHEN Windows işletim sisteminde çalışırken THEN Bootstrap_Sistemi SHALL pathlib kullanarak platform uyumlu yol yönetimi yapmalı

### Gereksinim 2

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, uygulama ayarlarının otomatik oluşmasını istiyorum, böylece manuel yapılandırma dosyası hazırlamam gerekmez.

#### Kabul Kriterleri

1. WHEN Ayar_Dosyasi mevcut değilse THEN Bootstrap_Sistemi SHALL varsayılan ayarlarla config.json dosyasını oluşturmalı
2. WHEN Ayar_Dosyasi zaten mevcutsa THEN Bootstrap_Sistemi SHALL mevcut ayarları korumalı ve üzerine yazmamalı
3. WHEN ayar dosyası oluşturulduğunda THEN Bootstrap_Sistemi SHALL veritabani_url, ortam ve log_seviyesi alanlarını içermeli
4. WHEN ayar dosyası okunduğunda THEN Bootstrap_Sistemi SHALL geçerli JSON formatında veri döndürmeli

### Gereksinim 3

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, veritabanı bağlantısının otomatik test edilmesini istiyorum, böylece bağlantı sorunlarını erken tespit edebilim.

#### Kabul Kriterleri

1. WHEN veritabanı bağlantı testi yapıldığında THEN Bootstrap_Sistemi SHALL PostgreSQL bağlantısını doğrulamalı
2. WHEN veritabanı bağlantısı başarısızsa THEN Bootstrap_Sistemi SHALL DogrulamaHatasi istisnası fırlatmalı
3. WHEN bağlantı URL'i geçersizse THEN Bootstrap_Sistemi SHALL anlaşılır hata mesajı içeren istisna fırlatmalı
4. WHEN bağlantı başarılıysa THEN Bootstrap_Sistemi SHALL sessizce devam etmeli

### Gereksinim 4

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, veritabanı şemasının otomatik güncellenmesini istiyorum, böylece manuel migration çalıştırmam gerekmez.

#### Kabul Kriterleri

1. WHEN Alembic_Gocleri çalıştırıldığında THEN Bootstrap_Sistemi SHALL programatik olarak alembic upgrade head komutunu çalıştırmalı
2. WHEN migration işlemi başarısızsa THEN Bootstrap_Sistemi SHALL hata detaylarını içeren istisna fırlatmalı
3. WHEN alembic config dosyası bulunamazsa THEN Bootstrap_Sistemi SHALL uygulama/veritabani/gocler dizininde arayacak
4. WHEN migration başarılıysa THEN Bootstrap_Sistemi SHALL işlemi loglamalı

### Gereksinim 5

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, varsayılan admin kullanıcısının otomatik oluşmasını istiyorum, böylece sisteme ilk girişi yapabilim.

#### Kabul Kriterleri

1. WHEN Admin_Kullanici oluşturulduğunda THEN Bootstrap_Sistemi SHALL kullanici_adi "admin" ve sifre "admin123" ile hesap oluşturmalı
2. WHEN admin kullanıcısı zaten mevcutsa THEN Bootstrap_Sistemi SHALL mevcut kullanıcıyı korumalı ve tekrar oluşturmamalı
3. WHEN şifre kaydedildiğinde THEN Bootstrap_Sistemi SHALL bcrypt hash algoritması kullanmalı
4. WHEN kullanıcı oluşturma işlemi başarısızsa THEN Bootstrap_Sistemi SHALL hata detaylarını loglamalı

### Gereksinim 6

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, tüm kurulum işlemlerinin tek bir komutla çalışmasını istiyorum, böylece karmaşık kurulum adımları yapmam gerekmez.

#### Kabul Kriterleri

1. WHEN ilk_calistirma_hazirla fonksiyonu çağrıldığında THEN Bootstrap_Sistemi SHALL tüm kurulum adımlarını sırasıyla çalıştırmalı
2. WHEN herhangi bir adım başarısızsa THEN Bootstrap_Sistemi SHALL anlaşılır hata mesajı ile işlemi durdurmalı
3. WHEN tüm adımlar başarılıysa THEN Bootstrap_Sistemi SHALL "kurulum tamam" mesajını loglamalı
4. WHEN kurulum tamamlandığında THEN Bootstrap_Sistemi SHALL sistem kullanıma hazır durumda olmalı

### Gereksinim 7

**Kullanıcı Hikayesi:** Geliştirici olarak, kurulum sürecinin dokümante edilmesini istiyorum, böylece kullanıcılar sistemi doğru şekilde kurabilsin.

#### Kabul Kriterleri

1. WHEN README.md güncellendiğinde THEN Bootstrap_Sistemi SHALL config.json dosyasının konumunu belirtmeli
2. WHEN kurulum talimatları yazıldığında THEN Bootstrap_Sistemi SHALL PostgreSQL bağlantı örneğini içermeli
3. WHEN dokümantasyon hazırlandığında THEN Bootstrap_Sistemi SHALL PyInstaller build adımlarını açıklamalı
4. WHEN kullanım kılavuzu oluşturulduğunda THEN Bootstrap_Sistemi SHALL otomatik migration bilgisini içermeli

### Gereksinim 8

**Kullanıcı Hikayesi:** Geliştirici olarak, proje bağımlılıklarının tanımlanmasını istiyorum, böylece gerekli paketler otomatik yüklenebilsin.

#### Kabul Kriterleri

1. WHEN pyproject.toml güncellendiğinde THEN Bootstrap_Sistemi SHALL PyQt6, FastAPI, SQLAlchemy bağımlılıklarını içermeli
2. WHEN bağımlılık listesi hazırlandığında THEN Bootstrap_Sistemi SHALL Alembic, psycopg2-binary paketlerini içermeli
3. WHEN güvenlik gereksinimleri tanımlandığında THEN Bootstrap_Sistemi SHALL passlib[bcrypt] paketini içermeli
4. WHEN yapılandırma yönetimi için THEN Bootstrap_Sistemi SHALL python-dotenv paketini içermeli