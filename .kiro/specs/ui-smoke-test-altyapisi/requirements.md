# Gereksinimler Dokümanı

## Giriş

SONTECHSP arayüzünü sanal ortamda çalıştırmak ve buton-fonksiyon-servis eşleştirmelerini görünür hale getirmek için smoke test altyapısı geliştirilecektir. Bu sistem, UI bileşenlerinin doğru çalışıp çalışmadığını hızlıca test etmeyi ve hangi butonun hangi servisi çağırdığını takip etmeyi sağlayacaktır.

## Sözlük

- **Smoke_Test_Sistemi**: UI'nin temel işlevselliğini hızlıca test eden sistem
- **Buton_Eslestirme_Kaydi**: Buton-handler-servis eşleştirmelerini kaydeden sistem
- **AnaPencere**: Uygulamanın ana pencere sınıfı
- **Handler**: Buton tıklama olaylarını işleyen fonksiyon
- **Stub_Servis**: Gerçek servis yerine test amaçlı kullanılan sahte servis

## Gereksinimler

### Gereksinim 1

**Kullanıcı Hikayesi:** Geliştirici olarak, UI için smoke test çalıştırmak istiyorum, böylece arayüzün sanal ortamda çalıştığını hızlıca doğrulayabileyim.

#### Kabul Kriterleri

1. WHEN smoke test komutu çalıştırıldığında THEN Smoke_Test_Sistemi AnaPencere arayüzünü başlatmalıdır
2. WHEN smoke test çalıştığında THEN Smoke_Test_Sistemi ekranlar arası geçişe izin vermelidir
3. WHEN smoke test tamamlandığında THEN Smoke_Test_Sistemi hatasız şekilde temiz kapanmalıdır
4. WHEN smoke test çağrıldığında THEN Smoke_Test_Sistemi "python -m uygulama.arayuz.smoke_test_calistir" komutuyla çalıştırılabilir olmalıdır

### Gereksinim 2

**Kullanıcı Hikayesi:** Geliştirici olarak, buton-fonksiyon eşleştirmelerini takip etmek istiyorum, böylece hangi butonların hangi servisleri çağırdığını anlayabileyim.

#### Kabul Kriterleri

1. WHEN bir buton eşleştirmesi kaydedildiğinde THEN Buton_Eslestirme_Kaydi ekran adı, buton adı, handler adı ve servis metodunu saklamalıdır
2. WHEN buton eşleştirmeleri istendiğinde THEN Buton_Eslestirme_Kaydi tüm kayıtlı eşleştirmelerin tam listesini döndürmelidir
3. WHEN kritik bir buton bağlandığında THEN Buton_Eslestirme_Kaydi otomatik olarak eşleştirmeyi kaydetmelidir
4. WHEN eşleştirmeler sorgulandığında THEN Buton_Eslestirme_Kaydi yapılandırılmış formatta veri sağlamalıdır

### Gereksinim 3

**Kullanıcı Hikayesi:** Geliştirici olarak, butonların eylemlerini loglamasını istiyorum, böylece test sırasında UI etkileşimlerini takip edebileyim.

#### Kabul Kriterleri

1. WHEN bir buton handler'ı çalıştığında THEN sistem hangi butonun hangi handler'ı tetiklediğini loglamalıdır
2. WHEN bir stub servis çağrıldığında THEN sistem "stub çağrıldı" mesajını loglamalıdır
3. WHEN loglama gerçekleştiğinde THEN sistem ekran adı, buton adı ve handler bilgilerini içermelidir
4. WHEN UI etkileşimleri olduğunda THEN sistem iş kuralı çalıştırmamalı, sadece loglama ve servis çağrısı yapmalıdır

### Gereksinim 4

**Kullanıcı Hikayesi:** Geliştirici olarak, net bir uygulama giriş noktası istiyorum, böylece smoke test güvenilir şekilde UI'yi başlatabilsin.

#### Kabul Kriterleri

1. WHEN uygulama başladığında THEN sistem UI başlatma için standartlaştırılmış giriş noktası sağlamalıdır
2. WHEN smoke test çalıştığında THEN sistem standart uygulama giriş noktasını kullanmalıdır
3. WHEN giriş noktası çağrıldığında THEN sistem UI bileşenlerini düzgün şekilde başlatmalıdır
4. WHEN birden fazla giriş metodu varsa THEN sistem en uygun standart metodu kullanmalıdır