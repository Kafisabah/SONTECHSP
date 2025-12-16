# Gelişmiş Stok Yönetimi Sistemi - Gereksinimler

## Giriş

Bu dokümantasyon, SONTECHSP için gelişmiş stok yönetimi sisteminin gereksinimlerini tanımlar. Sistem, çoklu mağaza/depo ortamında çalışan, eş zamanlı erişimi destekleyen, negatif stok kontrolü yapan ve POS ile e-ticaret entegrasyonu sağlayan kapsamlı bir stok yönetimi çözümüdür.

## Sözlük

- **Stok_Sistemi**: SONTECHSP stok yönetimi ana sistemi
- **Urun_Modulu**: Ürün bilgilerini yöneten alt sistem
- **Barkod_Sistemi**: Ürün barkod yönetimi alt sistemi
- **Stok_Hareket_Sistemi**: Stok giriş/çıkış işlemlerini yöneten alt sistem
- **Negatif_Stok_Kontrolu**: Stok seviyesi sıfırın altına düştüğünde uygulanan kontrol mekanizması
- **Eslik_Kilidi**: Eş zamanlı erişimde veri tutarlılığını sağlayan PostgreSQL row-level lock mekanizması
- **Depo**: Fiziksel stok saklama alanı
- **Magaza**: Satış noktası ve stok yönetim birimi
- **Kritik_Seviye**: Ürün için tanımlanan minimum stok eşiği
- **Hareket_Turu**: Stok değişikliğinin türü (GIRIS, CIKIS, SAYIM, TRANSFER)
- **Rezervasyon**: E-ticaret siparişleri için ayrılan stok miktarı
- **Kullanilabilir_Stok**: Toplam stok miktarından rezerve edilen miktar çıkarıldıktan sonra kalan miktar
- **Transaction**: Veritabanı işlemlerinin atomik olarak gerçekleştirilmesini sağlayan mekanizma

## Gereksinimler

### Gereksinim 1

**Kullanıcı Hikayesi:** Stok yöneticisi olarak, ürün bilgilerini sisteme ekleyip yönetebilmek istiyorum, böylece stok takibinin temelini oluşturabilirim.

#### Kabul Kriterleri

1. WHEN bir kullanıcı ürün bilgilerini girer THEN Stok_Sistemi SHALL ürünü benzersiz stok kodu ile kaydetmek
2. WHEN bir ürün kaydedilir THEN Urun_Modulu SHALL stok kodu benzersizliğini, ürün adı boş olmamasını, geçerli birim değerini ve pozitif kritik seviye değerini doğrulamak
3. WHEN ürün bilgileri güncellenir THEN Stok_Sistemi SHALL değişiklikleri kaydetmek ve güncelleme zamanını işaretlemek
4. WHEN ürün aranır THEN Urun_Modulu SHALL stok kodu veya ürün adına göre arama sonuçları döndürmek
5. WHEN ürün silinmek istenirse THEN Stok_Sistemi SHALL stok hareketi varsa silme işlemini engellemek

### Gereksinim 2

**Kullanıcı Hikayesi:** Kasiyer olarak, ürünleri barkod ile hızlıca bulabilmek istiyorum, böylece satış işlemlerini hızlandırabilirim.

#### Kabul Kriterleri

1. WHEN bir ürüne barkod eklenir THEN Barkod_Sistemi SHALL barkodu benzersiz olarak kaydetmek
2. WHEN barkod ile arama yapılır THEN Barkod_Sistemi SHALL ilgili ürün bilgilerini döndürmek
3. WHEN bir ürünün birden fazla barkodu varsa THEN Barkod_Sistemi SHALL tüm barkodları desteklemek
4. WHEN geçersiz barkod girilirse THEN Barkod_Sistemi SHALL uygun hata mesajı döndürmek
5. WHEN barkod silinir THEN Barkod_Sistemi SHALL ürünün en az bir barkodunun kalmasını sağlamak

### Gereksinim 3

**Kullanıcı Hikayesi:** Depo sorumlusu olarak, stok giriş ve çıkış işlemlerini kaydetmek istiyorum, böylece stok hareketlerini takip edebilirim.

#### Kabul Kriterleri

1. WHEN stok giriş işlemi yapılır THEN Stok_Hareket_Sistemi SHALL miktarı pozitif değer olarak kaydetmek
2. WHEN stok çıkış işlemi yapılır THEN Stok_Hareket_Sistemi SHALL miktarı negatif değer olarak kaydetmek
3. WHEN stok hareketi kaydedilir THEN Stok_Sistemi SHALL hareket türü, miktar, açıklama ve referans numarasını kaydetmek
4. WHEN stok hareketi tamamlanır THEN Stok_Sistemi SHALL stok bakiyesini güncellemek
5. WHEN hareket kaydedilir THEN Stok_Hareket_Sistemi SHALL işlem zamanını ve kullanıcı bilgisini kaydetmek

### Gereksinim 4

**Kullanıcı Hikayesi:** Satış personeli olarak, stok çıkışı yaparken negatif stok kontrolü yapılmasını istiyorum, böylece stok tutarlılığını koruyabilirim.

#### Kabul Kriterleri

1. WHEN stok bakiyesi sıfıra düşer THEN Negatif_Stok_Kontrolu SHALL uyarı mesajı göstermek ancak işleme izin vermek
2. WHEN stok bakiyesi -1 ile -5 arasında olur THEN Negatif_Stok_Kontrolu SHALL uyarı mesajı göstermek ancak işleme izin vermek
3. WHEN stok bakiyesi -5'ten küçük olur THEN Negatif_Stok_Kontrolu SHALL işlemi engellemek ve hata mesajı göstermek
4. WHEN negatif stok limiti ürün bazında tanımlanırsa THEN Stok_Sistemi SHALL ürün özelindeki limiti kullanmak
5. WHEN negatif stok kontrolü devre dışı bırakılırsa THEN Stok_Sistemi SHALL sınırsız negatif stoka izin vermek

### Gereksinim 5

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, eş zamanlı stok işlemlerinde veri tutarlılığının korunmasını istiyorum, böylece çoklu kullanıcı ortamında güvenli çalışabilirim.

#### Kabul Kriterleri

1. WHEN iki kullanıcı aynı ürünün stok çıkışını yapar THEN Eslik_Kilidi SHALL sadece bir işlemin tamamlanmasına izin vermek
2. WHEN stok bakiyesi kilitlenir THEN Stok_Sistemi SHALL PostgreSQL SELECT FOR UPDATE kullanmak
3. WHEN kilitleme işlemi 5 saniyeden fazla sürer THEN Stok_Sistemi SHALL kullanıcıya bekleme mesajı göstermek
4. WHEN transaction tamamlanır THEN Stok_Sistemi SHALL kilidi serbest bırakmak
5. WHEN eş zamanlı işlem çakışması olur THEN Stok_Sistemi SHALL ikinci işlemi bekletmek ve sırayla işlemek

### Gereksinim 6

**Kullanıcı Hikayesi:** Depo sorumlusu olarak, stok sayım işlemi yapabilmek istiyorum, böylece fiziksel stok ile sistem stokunu eşleştirebilirim.

#### Kabul Kriterleri

1. WHEN stok sayım işlemi başlatılır THEN Stok_Sistemi SHALL mevcut bakiye ile sayım miktarını karşılaştırmak
2. WHEN sayım farkı tespit edilir THEN Stok_Hareket_Sistemi SHALL fark miktarını SAYIM türünde hareket olarak kaydetmek
3. WHEN sayım işlemi tamamlanır THEN Stok_Sistemi SHALL stok bakiyesini sayım sonucuna göre güncellemek
4. WHEN sayım açıklaması girilir THEN Stok_Sistemi SHALL açıklamayı hareket kaydında saklamak
5. WHEN sayım işlemi iptal edilir THEN Stok_Sistemi SHALL hiçbir değişiklik yapmamak

### Gereksinim 7

**Kullanıcı Hikayesi:** Mağaza müdürü olarak, mağazalar arası stok transfer işlemi yapabilmek istiyorum, böylece stok dağılımını optimize edebilirim.

#### Kabul Kriterleri

1. WHEN transfer işlemi başlatılır THEN Stok_Sistemi SHALL kaynak depodan çıkış ve hedef depoya giriş işlemlerini tek transaction içinde yapmak
2. WHEN kaynak depoda yeterli stok yoksa THEN Stok_Sistemi SHALL transfer işlemini engellemek
3. WHEN transfer tamamlanır THEN Stok_Hareket_Sistemi SHALL her iki depo için TRANSFER türünde hareket kaydetmek
4. WHEN transfer işlemi başarısız olur THEN Stok_Sistemi SHALL tüm değişiklikleri geri almak
5. WHEN transfer referans numarası verilir THEN Stok_Sistemi SHALL referansı her iki hareket kaydında saklamak

### Gereksinim 8

**Kullanıcı Hikayesi:** Mağaza müdürü olarak, kritik stok seviyesindeki ürünleri görebilmek istiyorum, böylece zamanında sipariş verebilirim.

#### Kabul Kriterleri

1. WHEN kritik stok listesi istenir THEN Stok_Sistemi SHALL stok bakiyesi kritik seviyenin altındaki ürünleri listelemek
2. WHEN ürün kritik seviyeye düşer THEN Stok_Sistemi SHALL otomatik uyarı oluşturmak
3. WHEN kritik seviye ürün bazında tanımlanır THEN Stok_Sistemi SHALL ürün özelindeki seviyeyi kullanmak
4. WHEN kritik seviye tanımlanmamışsa THEN Stok_Sistemi SHALL varsayılan değer olarak 10 birim kullanmak
5. WHEN kritik stok raporu alınır THEN Stok_Sistemi SHALL depo bazında gruplandırılmış sonuç döndürmek

### Gereksinim 9

**Kullanıcı Hikayesi:** Sistem entegratörü olarak, stok verilerinin diğer modüllerle tutarlı paylaşılmasını istiyorum, böylece POS ve e-ticaret sistemleri doğru çalışabilir.

#### Kabul Kriterleri

1. WHEN stok bakiyesi değişir THEN Stok_Sistemi SHALL değişikliği gerçek zamanlı olarak yansıtmak
2. WHEN POS satış işlemi yapılır THEN Stok_Sistemi SHALL otomatik stok düşümü yapmak
3. WHEN e-ticaret siparişi alınır THEN Stok_Sistemi SHALL stok rezervasyonu yapmak
4. WHEN rezervasyon iptal edilir THEN Stok_Sistemi SHALL rezerve miktarını serbest bırakmak
5. WHEN stok sorgulama yapılır THEN Stok_Sistemi SHALL kullanılabilir miktarı (toplam - rezerve) döndürmek

### Gereksinim 10

**Kullanıcı Hikayesi:** Veri analisti olarak, stok hareketlerinin detaylı raporlarını alabilmek istiyorum, böylece stok performansını analiz edebilirim.

#### Kabul Kriterleri

1. WHEN stok hareket raporu istenir THEN Stok_Sistemi SHALL tarih aralığına göre filtrelenmiş sonuçlar döndürmek
2. WHEN hareket türü bazında rapor istenir THEN Stok_Sistemi SHALL GIRIS, CIKIS, SAYIM, TRANSFER türlerini ayrı ayrı göstermek
3. WHEN ürün bazında rapor istenir THEN Stok_Sistemi SHALL ürün özelinde tüm hareketleri listelemek
4. WHEN depo bazında rapor istenir THEN Stok_Sistemi SHALL depo özelinde hareket özetini vermek
5. WHEN rapor export edilir THEN Stok_Sistemi SHALL CSV formatında veri sağlamak