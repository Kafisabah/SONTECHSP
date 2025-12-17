# Kargo Entegrasyon Altyapısı - Gereksinimler Belgesi

## Giriş

SONTECHSP sistemi için taşıyıcı-bağımsız kargo entegrasyon altyapısı. Bu aşamada gerçek kargo firması API'lerine bağlanma olmayacak; carrier-agnostic çatı (arayüz + etiket + takip + outbox benzeri işleyiş) oluşturulacak. Sistem, satış belgeleri ve POS satışları için kargo etiketleri oluşturma, takip etme ve durum yönetimi sağlayacak.

## Sözlük

- **Kargo_Sistemi**: Kargo etiketleri ve takip işlemlerini yöneten sistem
- **Tasiyici**: Kargo taşıma hizmeti sağlayan firma (Yurtiçi, Aras, MNG, PTT, Sürat)
- **Etiket**: Kargo gönderimi için oluşturulan dijital etiket
- **Takip_No**: Kargo paketini takip etmek için kullanılan benzersiz numara
- **Kaynak**: Kargo etiketinin oluşturulduğu belge (POS satışı veya satış belgesi)
- **Carrier_Arayuzu**: Farklı taşıyıcılarla iletişim için standart arayüz
- **Outbox_Sistemi**: Başarısız işlemleri yeniden deneme mekanizması

## Gereksinimler

### Gereksinim 1

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, farklı kargo taşıyıcıları için etiket oluşturabilmek istiyorum, böylece müşterilere çeşitli kargo seçenekleri sunabilirim.

#### Kabul Kriterleri

1. WHEN sistem bir etiket oluşturma talebi aldığında THEN Kargo_Sistemi geçerli taşıyıcı bilgilerini doğrulayacak
2. WHEN etiket oluşturma işlemi başlatıldığında THEN Kargo_Sistemi kaynak türü ve kaynak ID'sini kontrol edecek
3. WHEN aynı kaynak ve taşıyıcı kombinasyonu için ikinci etiket talebi geldiğinde THEN Kargo_Sistemi benzersizlik kuralını uygulayacak
4. WHEN etiket başarıyla oluşturulduğunda THEN Kargo_Sistemi takip numarası ve etiket durumunu kayıt edecek
5. WHEN etiket oluşturma işlemi tamamlandığında THEN Kargo_Sistemi sonuç bilgilerini döndürecek

### Gereksinim 2

**Kullanıcı Hikayesi:** Satış personeli olarak, POS satışları ve satış belgeleri için kargo etiketleri oluşturabilmek istiyorum, böylece müşteri siparişlerini hızlıca kargoya verebilirim.

#### Kabul Kriterleri

1. WHEN POS satışı için etiket oluşturulduğunda THEN Kargo_Sistemi kaynak türünü POS_SATIS olarak kayıt edecek
2. WHEN satış belgesi için etiket oluşturulduğunda THEN Kargo_Sistemi kaynak türünü SATIS_BELGESI olarak kayıt edecek
3. WHEN etiket oluşturma verisi eksik olduğunda THEN Kargo_Sistemi doğrulama hatası verecek
4. WHEN alıcı bilgileri geçersiz olduğunda THEN Kargo_Sistemi uygun hata mesajı döndürecek
5. WHEN paket ağırlığı belirtilmediğinde THEN Kargo_Sistemi varsayılan 1.0 kg değerini kullanacak

### Gereksinim 3

**Kullanıcı Hikayesi:** Müşteri hizmetleri personeli olarak, kargo durumlarını sorgulayabilmek istiyorum, böylece müşterilere güncel bilgi verebilirim.

#### Kabul Kriterleri

1. WHEN takip numarası ile durum sorgulandığında THEN Kargo_Sistemi güncel durum bilgisini döndürecek
2. WHEN durum sorgusu yapıldığında THEN Kargo_Sistemi takip geçmişine yeni kayıt ekleyecek
3. WHEN takip numarası geçersiz olduğunda THEN Kargo_Sistemi uygun hata mesajı verecek
4. WHEN taşıyıcı servisi erişilemez olduğunda THEN Kargo_Sistemi bağlantı hatası döndürecek
5. WHEN durum bilgisi alındığında THEN Kargo_Sistemi zaman damgası ile birlikte kayıt edecek

### Gereksinim 4

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, başarısız kargo işlemlerinin otomatik yeniden denenmesini istiyorum, böylece geçici hatalar nedeniyle kayıp yaşanmasın.

#### Kabul Kriterleri

1. WHEN etiket oluşturma işlemi başarısız olduğunda THEN Kargo_Sistemi durumu HATA olarak işaretleyecek
2. WHEN bekleyen etiketler işlendiğinde THEN Kargo_Sistemi BEKLIYOR ve HATA durumundaki etiketleri yeniden deneyecek
3. WHEN yeniden deneme yapıldığında THEN Kargo_Sistemi deneme sayısını artıracak
4. WHEN maksimum deneme sayısına ulaşıldığında THEN Kargo_Sistemi işlemi durdurarak hata kaydı tutacak
5. WHEN işlem başarılı olduğunda THEN Kargo_Sistemi durumu OLUSTURULDU olarak güncelleyecek

### Gereksinim 5

**Kullanıcı Hikayesi:** Geliştirici olarak, farklı kargo taşıyıcıları için standart arayüz kullanabilmek istiyorum, böylece yeni taşıyıcı entegrasyonları kolayca ekleyebilirim.

#### Kabul Kriterleri

1. WHEN yeni taşıyıcı eklendiğinde THEN Carrier_Arayuzu standart etiket oluşturma metodunu sağlayacak
2. WHEN taşıyıcı seçildiğinde THEN Kargo_Sistemi uygun carrier implementasyonunu döndürecek
3. WHEN carrier metodu çağrıldığında THEN sistem standart veri formatını kullanacak
4. WHEN carrier hatası oluştuğunda THEN sistem EntegrasyonHatasi olarak ele alacak
5. WHEN dummy taşıyıcı kullanıldığında THEN sistem sahte verilerle test edilebilir sonuçlar döndürecek

### Gereksinim 6

**Kullanıcı Hikayesi:** Veri analisti olarak, kargo işlemlerinin geçmişini sorgulayabilmek istiyorum, böylece performans analizi yapabilirim.

#### Kabul Kriterleri

1. WHEN etiket kaydı oluşturulduğunda THEN Kargo_Sistemi oluşturulma zamanını kayıt edecek
2. WHEN etiket durumu güncellendiğinde THEN Kargo_Sistemi güncellenme zamanını kayıt edecek
3. WHEN takip kaydı eklendiğinde THEN Kargo_Sistemi zaman damgası ile birlikte saklayacak
4. WHEN kaynak bazlı sorgulama yapıldığında THEN Kargo_Sistemi ilgili etiketleri döndürecek
5. WHEN durum bazlı filtreleme yapıldığında THEN Kargo_Sistemi uygun kayıtları listeleyecek

### Gereksinim 7

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, kargo verilerinin tutarlılığını korumak istiyorum, böylece veri bütünlüğü sağlanır.

#### Kabul Kriterleri

1. WHEN etiket işlemleri yapıldığında THEN Kargo_Sistemi transaction kullanacak
2. WHEN veri kaydedildiğinde THEN Kargo_Sistemi foreign key kısıtlamalarını kontrol edecek
3. WHEN benzersizlik kuralı ihlal edildiğinde THEN Kargo_Sistemi uygun hata mesajı verecek
4. WHEN eş zamanlı erişim olduğunda THEN Kargo_Sistemi veri tutarlılığını koruyacak
5. WHEN sistem hatası oluştuğunda THEN Kargo_Sistemi rollback işlemi gerçekleştirecek

### Gereksinim 8

**Kullanıcı Hikayesi:** Performans analisti olarak, kargo sorgularının hızlı çalışmasını istiyorum, böylece sistem yanıt süreleri kabul edilebilir seviyede kalır.

#### Kabul Kriterleri

1. WHEN takip numarası ile arama yapıldığında THEN Kargo_Sistemi index kullanacak
2. WHEN durum bazlı filtreleme yapıldığında THEN Kargo_Sistemi optimize edilmiş sorgu çalıştıracak
3. WHEN kaynak bazlı arama yapıldığında THEN Kargo_Sistemi composite index kullanacak
4. WHEN büyük veri setlerinde çalışıldığında THEN Kargo_Sistemi sayfalama desteği sağlayacak
5. WHEN sık kullanılan sorgular çalıştırıldığında THEN Kargo_Sistemi performans optimizasyonu uygulayacak