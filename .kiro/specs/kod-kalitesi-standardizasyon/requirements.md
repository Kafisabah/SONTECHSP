# Kod Kalitesi ve Standardizasyon Gereksinimleri

## Giriş

SONTECHSP kod tabanının mevcut durumunu analiz ederek, kod kalitesi standartlarına uygun hale getirilmesi ve sürdürülebilir bir yapıya kavuşturulması için gerekli düzenlemelerin yapılması.

## Sözlük

- **Kod Tabanı**: Proje içindeki tüm Python dosyaları (.py uzantılı)
- **Dosya Boyut Limiti**: Tek dosyada maksimum 120 satır kod (yorumlar hariç)
- **Fonksiyon Boyut Limiti**: Tek fonksiyonda maksimum 25 satır kod
- **Katmanlı Mimari**: UI → Servis → Repository → Database yönlü bağımlılık
- **Modülerleştirme**: Büyük dosyaların mantıklı alt dosyalara bölünmesi
- **Import Düzeni**: Bağımlılık yönüne uygun import yapısı
- **Refactoring**: Mevcut kodu yeniden yapılandırma işlemi

## Gereksinimler

### Gereksinim 1

**Kullanıcı Hikayesi:** Geliştirici olarak, kod tabanındaki dosya boyutlarının standartlara uygun olmasını istiyorum, böylece kodun okunabilirliği ve bakımı kolaylaşsın.

#### Kabul Kriterleri

1. WHEN sistem tüm Python dosyalarını taradığında THEN 120 satırı aşan dosyalar tespit edilmeli
2. WHEN büyük dosyalar tespit edildiğinde THEN mantıklı alt modüllere bölünme planı oluşturulmalı
3. WHEN dosya bölme işlemi yapıldığında THEN mevcut import yapısı korunmalı
4. WHEN yeni alt dosyalar oluşturulduğunda THEN __init__.py dosyaları güncellenmelidir
5. WHEN refactoring tamamlandığında THEN tüm dosyalar 120 satır limitine uymalıdır

### Gereksinim 2

**Kullanıcı Hikayesi:** Geliştirici olarak, fonksiyonların boyutlarının standartlara uygun olmasını istiyorum, böylece kod karmaşıklığı azalsın ve test edilebilirlik artsın.

#### Kabul Kriterleri

1. WHEN sistem tüm fonksiyonları taradığında THEN 25 satırı aşan fonksiyonlar tespit edilmeli
2. WHEN büyük fonksiyonlar tespit edildiğinde THEN yardımcı fonksiyonlara bölünme planı oluşturulmalı
3. WHEN fonksiyon bölme işlemi yapıldığında THEN fonksiyonel davranış korunmalıdır
4. WHEN yardımcı fonksiyonlar oluşturulduğında THEN uygun isimlendirme yapılmalıdır
5. WHEN refactoring tamamlandığında THEN tüm fonksiyonlar 25 satır limitine uymalıdır

### Gereksinim 3

**Kullanıcı Hikayesi:** Sistem mimarı olarak, katmanlı mimarinin import kurallarına uygun olmasını istiyorum, böylece bağımlılık yönetimi sağlıklı olsun.

#### Kabul Kriterleri

1. WHEN sistem import yapılarını kontrol ettiğinde THEN UI katmanının repository/database import etmediği doğrulanmalı
2. WHEN mimari ihlaller tespit edildiğinde THEN düzeltme planı oluşturulmalıdır
3. WHEN import düzenlemesi yapıldığında THEN katman sınırları korunmalıdır
4. WHEN yeni import yapısı oluşturulduğında THEN dependency injection kullanılmalıdır
5. WHEN mimari düzenleme tamamlandığında THEN tüm katmanlar kurallara uymalıdır

### Gereksinim 4

**Kullanıcı Hikayesi:** Geliştirici olarak, tekrarlanan kodların ortak modüllere taşınmasını istiyorum, böylece kod tekrarı azalsın ve bakım kolaylaşsın.

#### Kabul Kriterleri

1. WHEN sistem kod tekrarlarını taradığında THEN benzer kod blokları tespit edilmeli
2. WHEN kod tekrarları tespit edildiğinde THEN ortak yardımcı modüller oluşturulmalıdır
3. WHEN ortak modüller oluşturulduğında THEN uygun klasör yapısına yerleştirilmelidir
4. WHEN kod taşıma işlemi yapıldığında THEN mevcut fonksiyonalite korunmalıdır
5. WHEN ortak modüller oluşturulduğunda THEN tüm kullanım yerleri güncellenmelidir

### Gereksinim 5

**Kullanıcı Hikayesi:** Proje yöneticisi olarak, tüm dosyaların standart başlık bilgilerine sahip olmasını istiyorum, böylece versiyon takibi ve dokümantasyon tutarlı olsun.

#### Kabul Kriterleri

1. WHEN yeni dosyalar oluşturulduğunda THEN standart sürüm başlığı eklenmelidir
2. WHEN dosya başlıkları kontrol edildiğinde THEN eksik başlık bilgileri tespit edilmeli
3. WHEN başlık güncellemesi yapıldığında THEN changelog bilgileri eklenmelidir
4. WHEN dosya değişikliği yapıldığında THEN son güncelleme tarihi güncellenmelidir
5. WHEN başlık standardizasyonu tamamlandığında THEN tüm dosyalar aynı formata uymalıdır

### Gereksinim 6

**Kullanıcı Hikayesi:** Kalite kontrol uzmanı olarak, refactoring işleminin mevcut testleri bozmadığını doğrulamak istiyorum, böylece sistem güvenilirliği korunsun.

#### Kabul Kriterleri

1. WHEN refactoring işlemi başlatıldığında THEN mevcut testler çalıştırılmalıdır
2. WHEN dosya bölme işlemi yapıldığında THEN ilgili testler güncellenmelidir
3. WHEN yeni modüller oluşturulduğında THEN test import yapıları düzenlenmelidir
4. WHEN refactoring tamamlandığında THEN tüm testler başarılı olmalıdır
5. WHEN test güncellemesi yapıldığında THEN test coverage korunmalıdır

### Gereksinim 7

**Kullanıcı Hikayesi:** Geliştirici olarak, büyük dosyaların mantıklı alt dosyalara bölünmesini istiyorum, böylece kod organizasyonu iyileşsin.

#### Kabul Kriterleri

1. WHEN büyük dosyalar analiz edildiğinde THEN fonksiyonel gruplar tespit edilmeli
2. WHEN bölme stratejisi oluşturulduğında THEN *_yardimcilari.py, *_dogrulama.py gibi anlamlı isimler kullanılmalıdır
3. WHEN alt dosyalar oluşturulduğında THEN modül içi tutarlılık korunmalıdır
4. WHEN dosya bölme işlemi yapıldığında THEN public API değişmemelidir
5. WHEN bölme tamamlandığında THEN her alt dosya tek bir sorumluluğa sahip olmalıdır

### Gereksinim 8

**Kullanıı Hikayesi:** Sistem yöneticisi olarak, refactoring sürecinin otomatik doğrulama ile desteklenmesini istiyorum, böylece insan hatası riski azalsın.

#### Kabul Kriterleri

1. WHEN refactoring araçları çalıştırıldığında THEN dosya boyut kontrolleri otomatik yapılmalıdır
2. WHEN kod analizi yapıldığında THEN fonksiyon boyut kontrolleri otomatik yapılmalıdır
3. WHEN import kontrolleri yapıldığında THEN mimari ihlaller otomatik tespit edilmelidir
4. WHEN kod kalitesi kontrolleri yapıldığında THEN PEP8 uyumluluğu doğrulanmalıdır
5. WHEN otomatik kontroller tamamlandığında THEN detaylı rapor üretilmelidir