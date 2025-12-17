# Satış Belgeleri Modülü - Gereksinimler Belgesi

## Giriş

SONTECHSP POS + ERP + CRM sistemi için satış belgeleri modülü geliştirilecektir. Bu modül sipariş, irsaliye ve fatura belgelerinin oluşturulması, yönetimi ve durum takibini sağlayacaktır. Modül, e-belge ve kargo entegrasyonları için temel altyapıyı oluşturacak ve mevcut POS sistemi ile entegre çalışacaktır.

## Sözlük

- **SatisBelgesiSistemi**: Sipariş, irsaliye ve fatura belgelerini yöneten sistem
- **BelgeTuru**: Belge tipini tanımlayan enum (SIPARIS, IRSALIYE, FATURA)
- **BelgeDurumu**: Belgenin mevcut durumunu tanımlayan enum (TASLAK, ONAYLANDI, FATURALANDI, IPTAL)
- **BelgeNumarasi**: Mağaza kodu, yıl, ay ve sıra numarasından oluşan benzersiz belge numarası
- **BelgeSatiri**: Belgeye ait ürün satırı bilgileri
- **DurumAkisi**: Belge durumları arasındaki geçiş kuralları
- **NumaraSayaci**: Belge numarası üretimi için kullanılan sayaç mekanizması

## Gereksinimler

### Gereksinim 1

**Kullanıcı Hikayesi:** Satış personeli olarak, müşteri siparişlerini sisteme kaydedebilmek istiyorum, böylece sipariş takibi yapabileyim.

#### Kabul Kriterleri

1. WHEN bir kullanıcı sipariş bilgilerini girer THEN SatisBelgesiSistemi yeni bir sipariş belgesi oluşturur ve TASLAK durumunda kaydeder
2. WHEN sipariş oluşturulur THEN SatisBelgesiSistemi benzersiz bir belge numarası üretir ve atar
3. WHEN sipariş satırları eklenir THEN SatisBelgesiSistemi her satır için ürün bilgilerini doğrular ve toplam tutarları hesaplar
4. WHEN sipariş kaydedilir THEN SatisBelgesiSistemi tüm bilgileri veritabanına transaction içinde yazar
5. IF sipariş oluşturma başarısız olur THEN SatisBelgesiSistemi hata mesajı döner ve veritabanı değişikliklerini geri alır

### Gereksinim 2

**Kullanıcı Hikayesi:** Depo personeli olarak, onaylanmış siparişlerden irsaliye oluşturabilmek istiyorum, böylece sevkiyat sürecini başlatabilirim.

#### Kabul Kriterleri

1. WHEN bir sipariş ONAYLANDI durumunda iken irsaliye oluşturulur THEN SatisBelgesiSistemi sipariş bilgilerini kopyalayarak yeni irsaliye belgesi oluşturur
2. WHEN irsaliye oluşturulur THEN SatisBelgesiSistemi irsaliye için yeni belge numarası üretir
3. WHEN irsaliye başarıyla oluşturulur THEN SatisBelgesiSistemi sipariş durumunu FATURALANDI olarak günceller
4. WHILE sipariş TASLAK durumunda iken irsaliye oluşturma denenirse THEN SatisBelgesiSistemi işlemi reddeder ve hata mesajı döner

### Gereksinim 3

**Kullanıcı Hikayesi:** Muhasebe personeli olarak, siparişlerden ve POS satışlarından fatura oluşturabilmek istiyorum, böylece mali işlemleri tamamlayabileyim.

#### Kabul Kriterleri

1. WHEN onaylanmış bir siparişten fatura oluşturulur THEN SatisBelgesiSistemi sipariş bilgilerini kullanarak fatura belgesi oluşturur
2. WHEN POS satışından fatura oluşturulur THEN SatisBelgesiSistemi POS satış bilgilerini okuyarak fatura belgesi oluşturur
3. WHEN fatura oluşturulur THEN SatisBelgesiSistemi KDV hesaplamalarını yapar ve toplam tutarları belirler
4. WHEN fatura başarıyla oluşturulur THEN SatisBelgesiSistemi kaynak belgenin durumunu FATURALANDI olarak günceller
5. IF fatura oluşturma sırasında hata oluşur THEN SatisBelgesiSistemi tüm değişiklikleri geri alır ve hata mesajı döner

### Gereksinim 4

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, belge numaralarının benzersiz ve sıralı olmasını istiyorum, böylece mali mevzuata uygun numara düzeni sağlayabileyim.

#### Kabul Kriterleri

1. WHEN yeni belge oluşturulur THEN SatisBelgesiSistemi mağaza kodu, yıl, ay ve sıra numarasından oluşan benzersiz numara üretir
2. WHEN aynı mağaza ve belge türü için numara üretilir THEN SatisBelgesiSistemi sıra numarasını bir artırır
3. WHEN ay değişir THEN SatisBelgesiSistemi sıra numarasını sıfırdan başlatır
4. IF numara üretimi sırasında çakışma oluşur THEN SatisBelgesiSistemi işlemi tekrar dener ve benzersizliği garanti eder

### Gereksinim 5

**Kullanıcı Hikayesi:** Satış müdürü olarak, belge durumlarını takip edebilmek istiyorum, böylece iş akışını kontrol edebileyim.

#### Kabul Kriterleri

1. WHEN belge durumu güncellenmeye çalışılır THEN SatisBelgesiSistemi durum akış kurallarını kontrol eder
2. WHEN geçerli durum geçişi yapılır THEN SatisBelgesiSistemi belge durumunu günceller ve zaman damgası ekler
3. IF geçersiz durum geçişi denenirse THEN SatisBelgesiSistemi işlemi reddeder ve hata mesajı döner
4. WHEN belge IPTAL durumuna alınır THEN SatisBelgesiSistemi iptal nedenini kaydeder
5. WHILE belge IPTAL durumunda iken başka durum geçişi denenirse THEN SatisBelgesiSistemi işlemi reddeder

### Gereksinim 6

**Kullanıcı Hikayesi:** Sistem geliştiricisi olarak, belge verilerinin tutarlı saklanmasını istiyorum, böylece veri bütünlüğü sağlanabilsin.

#### Kabul Kriterleri

1. WHEN belge işlemleri yapılır THEN SatisBelgesiSistemi tüm veritabanı işlemlerini transaction içinde gerçekleştirir
2. WHEN belge satırları kaydedilir THEN SatisBelgesiSistemi ürün bilgilerinin geçerliliğini kontrol eder
3. WHEN toplam tutarlar hesaplanır THEN SatisBelgesiSistemi satır toplamları ile genel toplamın uyumunu doğrular
4. WHEN belge silinmeye çalışılır THEN SatisBelgesiSistemi bağımlı kayıtları kontrol eder ve uygun işlemi yapar
5. WHEN eş zamanlı belge işlemleri yapılır THEN SatisBelgesiSistemi row-level lock kullanarak veri tutarlılığını korur

### Gereksinim 7

**Kullanıcı Hikayesi:** Sistem entegratörü olarak, belge verilerine programatik erişim sağlayabilmek istiyorum, böylece e-belge ve kargo entegrasyonları yapabileyim.

#### Kabul Kriterleri

1. WHEN belge verileri sorgulanır THEN SatisBelgesiSistemi belge ve satır bilgilerini DTO formatında döner
2. WHEN belge durumu sorgulanır THEN SatisBelgesiSistemi güncel durum bilgisini zaman damgası ile birlikte döner
3. WHEN belge listesi istenir THEN SatisBelgesiSistemi filtreleme ve sayfalama desteği sağlar
4. WHEN belge geçmişi sorgulanır THEN SatisBelgesiSistemi durum değişiklik geçmişini döner