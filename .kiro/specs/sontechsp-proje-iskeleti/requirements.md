# Gereksinimler Belgesi

## Giriş

SONTECHSP projesi için temel proje iskeletinin oluşturulması. Bu iskelet, Windows üzerinde kurulabilen, çoklu mağaza/şube ve çoklu PC ile eş zamanlı çalışan Hızlı Satış (POS) + ERP + CRM sisteminin temel yapısını oluşturacaktır.

## Sözlük

- **Proje_Iskeleti**: Uygulamanın temel klasör yapısı ve başlangıç dosyaları (Türkçe ASCII isimlendirme)
- **Ana_Uygulama**: PyQt6 tabanlı masaüstü uygulamasının giriş noktası (ana.py)
- **Klasor_Yapisi**: Katmanlı mimariyi destekleyen dizin organizasyonu (uygulama/cekirdek/veritabani/moduller)
- **Baslangic_Dosyalari**: Projenin çalışması için gerekli minimum dosya seti
- **Katmanli_Mimari**: Arayüz -> Servis -> Depo (Repository) -> Veritabanı yapısı

## Gereksinimler

### Gereksinim 1

**Kullanıcı Hikayesi:** Bir geliştirici olarak, SONTECHSP projesinin temel iskeletini oluşturmak istiyorum, böylece katmanlı mimari ile modüler geliştirme sürecine başlayabilirim.

#### Kabul Kriterleri

1. WHEN proje iskeleti oluşturulduğunda THEN Proje_Iskeleti sontechsp/uygulama/cekirdek/veritabani/moduller klasör hiyerarşisini içermelidir
2. WHEN ana uygulama başlatıldığında THEN Ana_Uygulama PyQt6 penceresi açmalı ve log sistemi başlatmalıdır
3. WHEN proje yapısı incelendiğinde THEN Klasor_Yapisi katmanlı mimariyi (UI->Servis->Repository->DB) desteklemelidir
4. WHEN geliştirme başladığında THEN Baslangic_Dosyalari çalışır durumda olmalıdır
5. WHEN kod yazıldığında THEN her dosya PEP8 standartlarına uymalı ve 120 satırı aşmamalıdır

### Gereksinim 2

**Kullanıcı Hikayesi:** Bir sistem yöneticisi olarak, projenin bağımlılıklarını ve kurulum gereksinimlerini bilmek istiyorum, böylece Windows üzerinde sistemi doğru şekilde kurabilirim.

#### Kabul Kriterleri

1. WHEN pyproject.toml dosyası incelendiğinde THEN Python sürümü, PyQt6, SQLAlchemy, Alembic, FastAPI, pytest, hypothesis bağımlılıklarını tanımlamalıdır
2. WHEN README.md dosyası okunduğunda THEN kurulum, çalıştırma talimatları ve PyInstaller build notları açık olmalıdır
3. WHEN proje yapılandırıldığında THEN PostgreSQL ve SQLite veritabanı gereksinimleri belirtilmelidir
4. WHEN geliştirme ortamı hazırlandığında THEN tüm bağımlılıklar Windows üzerinde yüklenebilmelidir

### Gereksinim 3

**Kullanıcı Hikayesi:** Bir geliştirici olarak, uygulamanın giriş noktasının basit ve anlaşılır olmasını istiyorum, böylece katmanlı sistem mimarisini kolayca anlayabilirim.

#### Kabul Kriterleri

1. WHEN uygulama/ana.py dosyası çalıştırıldığında THEN PyQt6 AnaPencere başlatma işlemi gerçekleşmelidir
2. WHEN uygulama başladığında THEN log sistemi (dosya+console) aktif hale gelmelidir
3. WHEN ana pencere açıldığında THEN sol menü ve içerik alanı ile PyQt6 arayüzü görüntülenmelidir
4. WHEN kod incelendiğinde THEN ana.py dosyası sadece bootstrap işlevi görmeli ve iş kuralı içermemelidir
5. WHEN hata oluştuğunda THEN merkezi hata yönetimi sistemi devreye girmelidir

### Gereksinim 4

**Kullanıcı Hikayesi:** Bir proje mimarı olarak, modüler yapının doğru şekilde organize edilmesini istiyorum, böylece farklı ajanlar (stok_ajani, pos_ajani, crm_ajani vb.) farklı modüller üzerinde çalışabilsin.

#### Kabul Kriterleri

1. WHEN klasör yapısı oluşturulduğunda THEN moduller altında stok/pos/crm/satis_belgeleri/eticaret/ebelge/kargo/raporlar dizinleri olmalıdır
2. WHEN modüller arası bağımlılık kontrol edildiğinde THEN Katmanli_Mimari kuralları (UI->Servis->Repository->DB) korunmalıdır
3. WHEN yeni modül eklendiğinde THEN mevcut katmanlı yapıya uyumlu olmalı ve bağımlılık kurallarını bozmamalıdır
4. WHEN kod organizasyonu incelendiğinde THEN cekirdek/veritabani/moduller/servisler/arayuz sorumlulukları net şekilde ayrılmalıdır

### Gereksinim 5

**Kullanıcı Hikayesi:** Bir kalite kontrol uzmanı olarak, SONTECHSP kod kalitesi standartlarının baştan belirlenmesini istiyorum, böylece tutarlı kod kalitesi sağlanabilsin.

#### Kabul Kriterleri

1. WHEN kod dosyaları incelendiğinde THEN her dosya 120 satırı (yorumlar hariç) aşmamalıdır
2. WHEN fonksiyonlar kontrol edildiğinde THEN her fonksiyon 25 satırı aşmamalı, gerekirse bölünmelidir
3. WHEN kod formatı kontrol edildiğinde THEN PEP8 standartlarına zorunlu olarak uymalıdır
4. WHEN dosya başlıkları incelendiğinde THEN Version/Last Update/Module/Description/Changelog standart şablonu bulunmalıdır
5. WHEN kod yorumları okunduğunda THEN Türkçe yazılmış olmalı ve inline açıklamalar içermelidir

### Gereksinim 6

**Kullanıcı Hikayesi:** Bir veritabanı yöneticisi olarak, veritabanı yapısının Türkçe isimlendirme ile standartlaştırılmasını istiyorum, böylece sistem tutarlı ve anlaşılır olsun.

#### Kabul Kriterleri

1. WHEN veritabanı tabloları oluşturulduğunda THEN kullanicilar/roller/firmalar/magazalar/terminaller tablo isimleri kullanılmalıdır
2. WHEN stok modülü tabloları oluşturulduğunda THEN urunler/urun_barkodlari/stok_bakiyeleri/stok_hareketleri isimleri kullanılmalıdır
3. WHEN POS modülü tabloları oluşturulduğunda THEN pos_satislar/pos_satis_satirlari/odeme_kayitlari isimleri kullanılmalıdır
4. WHEN e-ticaret modülü tabloları oluşturulduğunda THEN eticaret_hesaplari/eticaret_siparisleri isimleri kullanılmalıdır
5. WHEN tüm tablo isimleri kontrol edildiğinde THEN Türkçe karakter içermemeli (ASCII Türkçe) olmalıdır

### Gereksinim 7

**Kullanıcı Hikayesi:** Bir sistem mimarı olarak, çekirdek altyapının doğru şekilde ayrıştırılmasını istiyorum, böylece sistem bileşenleri bağımsız olarak geliştirilebilsin.

#### Kabul Kriterleri

1. WHEN çekirdek modülü oluşturulduğunda THEN ayarlar/kayit/hatalar/yetki/oturum bileşenleri ayrı dosyalarda olmalıdır
2. WHEN çekirdek modülü incelendiğinde THEN UI ve veritabanı katmanlarından bağımsız olmalıdır
3. WHEN log sistemi kurulduğunda THEN dosya ve console çıktısı desteklemelidir
4. WHEN hata yönetimi oluşturulduğunda THEN AlanHatasi/DogrulamaHatasi/EntegrasyonHatasi sınıfları tanımlanmalıdır
5. WHEN oturum bağlamı kurulduğunda THEN magaza/terminal/kullanici bilgilerini yönetmelidir

### Gereksinim 8

**Kullanıcı Hikayesi:** Bir kurulum uzmanı olarak, ilk çalıştırma sürecinin otomatik olmasını istiyorum, böylece sistem kolayca kurulabilsin.

#### Kabul Kriterleri

1. WHEN ilk kurulum çalıştırıldığında THEN gerekli klasörler otomatik oluşturulmalıdır
2. WHEN veritabanı kurulumu yapıldığında THEN PostgreSQL bağlantısı test edilmeli ve migration çalıştırılmalıdır
3. WHEN admin kullanıcı oluşturulduğunda THEN varsayılan yönetici hesabı sisteme eklenmelidir
4. WHEN yapılandırma dosyası oluşturulduğunda THEN .env veya config.json şablonu üretilmelidir
5. WHEN PyInstaller build notları hazırlandığında THEN Windows kurulum talimatları README'ye eklenmelidir