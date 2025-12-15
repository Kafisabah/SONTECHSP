# Çekirdek Altyapı Gereksinimleri

## Giriş

SONTECHSP çekirdek altyapısı, uygulamanın temel işlevselliğini sağlayan merkezi bileşenleri içerir. Bu altyapı, ayarlar yönetimi, loglama, hata yönetimi, yetkilendirme ve oturum yönetimi gibi tüm modüller tarafından kullanılan ortak servisleri sunar.

## Sözlük

- **CekirdekSistem**: Uygulamanın temel altyapı bileşenlerini sağlayan sistem
- **AyarlarYoneticisi**: Uygulama yapılandırma ayarlarını yöneten bileşen
- **KayitSistemi**: Log kayıtlarını yöneten sistem
- **HataYoneticisi**: Uygulama hatalarını kategorize eden ve yöneten sistem
- **YetkiKontrolcu**: Kullanıcı yetkilendirmelerini kontrol eden bileşen
- **OturumBilgisi**: Aktif kullanıcı oturumu ve bağlam bilgilerini tutan veri yapısı

## Gereksinimler

### Gereksinim 1

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, uygulama ayarlarını merkezi bir yerden yönetebilmek istiyorum ki farklı ortamlarda tutarlı yapılandırma sağlayabileyim.

#### Kabul Kriterleri

1. WHEN sistem başlatıldığında THEN CekirdekSistem SHALL .env dosyasından ayarları okuyabilir
2. WHEN zorunlu ayarlar eksik olduğunda THEN CekirdekSistem SHALL uygun hata mesajı verir
3. WHEN ayar değeri okunduğunda THEN CekirdekSistem SHALL tip güvenli değer döndürür
4. WHEN ortam değişkeni mevcut değilse THEN CekirdekSistem SHALL varsayılan değeri kullanır
5. WHERE ayar dosyası mevcut değilse THEN CekirdekSistem SHALL örnek ayar dosyası oluşturur

### Gereksinim 2

**Kullanıcı Hikayesi:** Geliştirici olarak, uygulama olaylarını takip edebilmek istiyorum ki hata ayıklama ve sistem izleme yapabileyim.

#### Kabul Kriterleri

1. WHEN log mesajı yazıldığında THEN KayitSistemi SHALL hem dosyaya hem konsola yazır
2. WHEN log seviyesi ayarlandığında THEN KayitSistemi SHALL sadece belirtilen seviye ve üstü mesajları kaydeder
3. WHEN log dosyası boyutu sınırı aşıldığında THEN KayitSistemi SHALL dosyayı döndürür
4. WHEN log klasörü mevcut değilse THEN KayitSistemi SHALL otomatik oluşturur
5. WHERE log ayarları yapılandırıldığında THEN KayitSistemi SHALL ayarlara göre davranır

### Gereksinim 3

**Kullanıcı Hikayesi:** Geliştirici olarak, hataları kategorize edebilmek istiyorum ki uygun hata yönetimi ve kullanıcı deneyimi sağlayabileyim.

#### Kabul Kriterleri

1. WHEN alan doğrulama hatası oluştuğunda THEN HataYoneticisi SHALL AlanHatasi fırlatır
2. WHEN veri doğrulama hatası oluştuğunda THEN HataYoneticisi SHALL DogrulamaHatasi fırlatır
3. WHEN dış sistem entegrasyon hatası oluştuğunda THEN HataYoneticisi SHALL EntegrasyonHatasi fırlatır
4. WHEN hata yakalandığında THEN HataYoneticisi SHALL uygun log seviyesinde kaydeder
5. WHERE hata mesajı Türkçe olmalıdır THEN HataYoneticisi SHALL Türkçe hata mesajı sağlar

### Gereksinim 4

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, kullanıcı yetkilerini kontrol edebilmek istiyorum ki güvenli erişim sağlayabileyim.

#### Kabul Kriterleri

1. WHEN kullanıcı yetki kontrolü yapıldığında THEN YetkiKontrolcu SHALL rol ve izin eşleşmesini kontrol eder
2. WHEN geçersiz rol verildiğinde THEN YetkiKontrolcu SHALL False döndürür
3. WHEN geçersiz izin sorgulandığında THEN YetkiKontrolcu SHALL False döndürür
4. WHERE yetki matrisi tanımlandığında THEN YetkiKontrolcu SHALL matrise göre kontrol yapar
5. WHILE yetki kontrolü yapılırken THEN YetkiKontrolcu SHALL performanslı çalışır

### Gereksinim 5

**Kullanıcı Hikayesi:** Kullanıcı olarak, oturum bilgilerimin güvenli şekilde yönetilmesini istiyorum ki sistem genelinde tutarlı bağlam sağlansın.

#### Kabul Kriterleri

1. WHEN kullanıcı oturum açtığında THEN OturumBilgisi SHALL kullanıcı, firma, mağaza bilgilerini tutar
2. WHEN oturum bağlamı değiştiğinde THEN OturumBilgisi SHALL yeni bağlamı günceller
3. WHEN oturum sonlandırıldığında THEN OturumBilgisi SHALL tüm bilgileri temizler
4. WHERE çoklu terminal desteği gerektiğinde THEN OturumBilgisi SHALL terminal bilgisini tutar
5. WHILE oturum aktifken THEN OturumBilgisi SHALL bağlam bilgilerini korur

### Gereksinim 6

**Kullanıcı Hikayesi:** Geliştirici olarak, çekirdek modüllerin diğer katmanlardan bağımsız olmasını istiyorum ki temiz mimari sağlayabileyim.

#### Kabul Kriterleri

1. WHEN çekirdek modül import edildiğinde THEN CekirdekSistem SHALL UI katmanından bağımsız çalışır
2. WHEN çekirdek modül kullanıldığında THEN CekirdekSistem SHALL veritabanı katmanından bağımsız çalışır
3. WHERE bağımlılık analizi yapıldığında THEN CekirdekSistem SHALL sadece standart kütüphaneleri kullanır
4. WHILE çekirdek işlevler çalışırken THEN CekirdekSistem SHALL dış bağımlılık gerektirmez
5. IF çekirdek modül test edildiğinde THEN CekirdekSistem SHALL izole test edilebilir

### Gereksinim 7

**Kullanıcı Hikayesi:** Geliştirici olarak, yapılandırma dosyalarının güvenli şekilde yönetilmesini istiyorum ki hassas bilgiler korunabilsin.

#### Kabul Kriterleri

1. WHEN .env dosyası okunduğunda THEN AyarlarYoneticisi SHALL hassas bilgileri güvenli şekilde yükler
2. WHEN yapılandırma doğrulaması yapıldığında THEN AyarlarYoneticisi SHALL zorunlu alanları kontrol eder
3. WHERE ortam değişkenleri öncelikli olduğunda THEN AyarlarYoneticisi SHALL ortam değişkenini kullanır
4. IF yapılandırma hatası varsa THEN AyarlarYoneticisi SHALL açıklayıcı hata mesajı verir
5. WHILE uygulama çalışırken THEN AyarlarYoneticisi SHALL ayar değişikliklerini algılar