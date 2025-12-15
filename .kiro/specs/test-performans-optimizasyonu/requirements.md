# Test Performans Optimizasyonu - Gereksinimler

## Giriş

SONTECHSP projesinde testlerin uzun sürmesi sorunu için performans optimizasyonu yapılması gerekiyor. Mevcut durumda 817 test var ve bunların çoğu parametrize edilmiş testler. Testlerin hızlı çalışması geliştirici deneyimi için kritik.

## Sözlük

- **Test Suite**: Tüm testlerin toplamı
- **Parametrize Test**: Aynı testin farklı parametrelerle çalıştırılması
- **Property Test**: Hypothesis kütüphanesi ile yapılan property-based testler
- **Test Marker**: Pytest ile testleri kategorize etme sistemi
- **Test Collection**: Pytest'in testleri bulma ve toplama süreci

## Gereksinimler

### Gereksinim 1

**Kullanıcı Hikayesi:** Geliştirici olarak, testlerin hızlı çalışmasını istiyorum ki geliştirme döngüsü kesintisiz olsun.

#### Kabul Kriterleri

1. WHEN tüm testler çalıştırıldığında THEN test süresi 2 dakikadan az OLMALI
2. WHEN hızlı testler çalıştırıldığında THEN test süresi 30 saniyeden az OLMALI  
3. WHEN yavaş testler ayrı çalıştırıldığında THEN bunlar "slow" marker ile işaretlenmeli OLMALI
4. WHEN CI/CD pipeline çalıştığında THEN sadece kritik testler çalışmalı OLMALI
5. WHEN geliştirici lokal test çalıştırdığında THEN varsayılan olarak hızlı testler çalışmalı OLMALI

### Gereksinim 2

**Kullanıcı Hikayesi:** Test mühendisi olarak, testleri kategorize etmek istiyorum ki ihtiyaca göre farklı test grupları çalıştırabileyim.

#### Kabul Kriterleri

1. WHEN testler marker ile işaretlendiğinde THEN unit, integration, property, slow kategorileri OLMALI
2. WHEN pytest çalıştırıldığında THEN marker bazlı filtreleme yapılabilmeli OLMALI
3. WHEN test konfigürasyonu güncellendiğinde THEN pyproject.toml dosyasında marker tanımları OLMALI
4. WHEN test raporu oluşturulduğunda THEN kategori bazlı sonuçlar görülebilmeli OLMALI

### Gereksinim 3

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, property-based testlerin performansını optimize etmek istiyorum ki gereksiz yere uzun sürmesini engelleyeyim.

#### Kabul Kriterleri

1. WHEN hypothesis testleri çalıştığında THEN maksimum örnek sayısı 50 OLMALI
2. WHEN hypothesis timeout ayarlandığında THEN test başına maksimum 2 saniye OLMALI
3. WHEN hypothesis profil ayarlandığında THEN hızlı profil kullanılmalı OLMALI
4. WHEN property testler çalıştığında THEN gereksiz health check'ler devre dışı OLMALI

### Gereksinim 4

**Kullanıcı Hikayesi:** Geliştirici olarak, parametrize testlerin sayısını azaltmak istiyorum ki test süresi makul seviyede olsun.

#### Kabul Kriterleri

1. WHEN dosya bazlı parametrize testler çalıştığında THEN kritik dosyalar öncelikli test edilmeli OLMALI
2. WHEN test parametreleri azaltıldığında THEN temel kapsama korunmalı OLMALI
3. WHEN sampling stratejisi uygulandığında THEN rastgele dosya seçimi yapılmalı OLMALI
4. WHEN test optimizasyonu yapıldığında THEN mevcut test mantığı korunmalı OLMALI

### Gereksinim 5

**Kullanıcı Hikayesi:** DevOps mühendisi olarak, paralel test çalıştırma desteği istiyorum ki çok çekirdekli sistemlerde testler hızlı çalışsın.

#### Kabul Kriterleri

1. WHEN pytest-xdist kurulduğunda THEN paralel test çalıştırma aktif OLMALI
2. WHEN paralel testler çalıştığında THEN CPU çekirdek sayısına göre worker sayısı ayarlanmalı OLMALI
3. WHEN paralel testler çalıştığında THEN test izolasyonu korunmalı OLMALI
4. WHEN paralel test sonuçları toplandığında THEN coverage raporu doğru hesaplanmalı OLMALI