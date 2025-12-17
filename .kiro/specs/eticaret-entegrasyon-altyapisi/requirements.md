# Gereksinimler Dokümanı

## Giriş

SONTECHSP projesi için merkezi bir E-Ticaret Entegrasyon Omurgası (Backbone) geliştirilecektir. Bu sistem, gelecekte eklenecek tüm e-ticaret platformlarını (Trendyol, Shopify, Amazon vb.) standart bir yapıda yönetecek soyutlama katmanını, iş kuyruğu mekanizmasını ve veri kalıcılık katmanını sağlayacaktır. Sistem backend-only (headless) olarak tasarlanacak ve çoklu mağaza desteği sunacaktır.

## Sözlük

- **E-Ticaret Sistemi**: Çoklu platform entegrasyonu destekleyen merkezi e-ticaret yönetim sistemi
- **Platform**: Trendyol, Shopify, Amazon gibi e-ticaret platformları
- **Mağaza Hesabı**: Bir platformdaki mağaza kimlik bilgileri ve ayarları
- **Bağlantı Bileşeni**: Belirli bir platform ile iletişim kuran entegrasyon bileşeni
- **İş Kuyruğu**: Asenkron işlemlerin sıralandığı ve yürütüldüğü sistem
- **VTO**: Veri transfer nesnesi (Data Transfer Object)
- **Depo**: Veri erişim katmanı soyutlaması

## Gereksinimler

### Gereksinim 1

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, çoklu e-ticaret platform hesaplarını yönetmek istiyorum, böylece farklı mağazaları çeşitli platformlarla entegre edebilirim.

#### Kabul Kriterleri

1. WHEN bir yönetici yeni mağaza hesabı oluşturduğunda THEN E-Ticaret Sistemi platform türü, mağaza adı, kimlik bilgileri ve yapılandırma ayarlarını depolamalıdır
2. WHEN bir yönetici mağaza hesabı bilgilerini güncellediğinde THEN E-Ticaret Sistemi veri bütünlüğünü koruyarak mevcut kaydı değiştirmelidir
3. WHEN bir yönetici mağaza hesabını devre dışı bıraktığında THEN E-Ticaret Sistemi geçmiş verileri silmeden hesabı pasif olarak işaretlemelidir
4. WHEN sistem hassas kimlik bilgilerini depoladığında THEN E-Ticaret Sistemi kimlik_json alanındaki kimlik verilerini şifrelemelidir
5. E-Ticaret Sistemi platform türü başına birden fazla mağaza hesabını desteklemelidir

### Gereksinim 2

**Kullanıcı Hikayesi:** Sistem entegratörü olarak, tüm e-ticaret platformları için standartlaştırılmış bir arayüz istiyorum, böylece yeni platformlar temel iş mantığını değiştirmeden eklenebilir.

#### Kabul Kriterleri

1. WHEN yeni bir platform bağlantı bileşeni uygulandığında THEN Bağlantı Bileşeni standart BaglantiArayuzu arayüzünü uygulamalıdır
2. WHEN sistem herhangi bir platformla iletişim kurması gerektiğinde THEN E-Ticaret Sistemi platform türünden bağımsız olarak aynı metot imzalarını kullanmalıdır
3. WHEN platforma özgü bir işlem talep edildiğinde THEN BaglantiArayuzu sipariş alma, stok güncelleme, fiyat güncelleme ve durum güncelleme metotlarını sağlamalıdır
4. E-Ticaret Sistemi platform türüne göre doğru bağlantı bileşenini örneklemek için fabrika desenini kullanmalıdır
5. WHEN bir bağlantı bileşeni hatayla karşılaştığında THEN BaglantiArayuzu standartlaştırılmış EntegrasyonHatasi istisnalarını fırlatmalıdır

### Gereksinim 3

**Kullanıcı Hikayesi:** Mağaza müdürü olarak, e-ticaret platformlarından siparişleri senkronize etmek istiyorum, böylece tüm siparişleri merkezi bir sistemde yönetebilirim.

#### Kabul Kriterleri

1. WHEN sistem bir platformdan siparişleri aldığında THEN E-Ticaret Sistemi platforma özgü dış sipariş numaraları ile sipariş verilerini depolamalıdır
2. WHEN yinelenen siparişler alındığında THEN E-Ticaret Sistemi platform, dış sipariş numarası ve mağaza hesabı üzerinde benzersiz kısıtlamalar kullanarak yinelenen girişleri önlemelidir
3. WHEN sipariş verileri depolandığında THEN E-Ticaret Sistemi müşteri bilgileri, toplam tutar, para birimi, durum ve kargo detaylarını içermelidir
4. WHEN siparişler senkronize edildiğinde THEN E-Ticaret Sistemi orijinal ham verileri ham_veri_json alanında korumalıdır
5. E-Ticaret Sistemi siparişleri mağaza hesabı ve duruma göre filtrelemeyi desteklemelidir

### Gereksinim 4

**Kullanıcı Hikayesi:** Envanter müdürü olarak, birden fazla platformda stok seviyelerini güncellemek istiyorum, böylece envanter senkronize kalır.

#### Kabul Kriterleri

1. WHEN stok güncellemeleri talep edildiğinde THEN E-Ticaret Sistemi güncellemeleri uygun platform bağlantı bileşenine göndermelidir
2. WHEN stok senkronizasyonu başarısız olduğunda THEN E-Ticaret Sistemi hatayı kaydetmeli ve işi yeniden deneme için hata durumunda tutmalıdır
3. WHEN birden fazla stok güncellemesi işlendiğinde THEN E-Ticaret Sistemi bunları toplu işlemler olarak ele almalıdır
4. E-Ticaret Sistemi platformlara göndermeden önce stok güncelleme verilerini doğrulamalıdır
5. WHEN stok güncellemeleri tamamlandığında THEN E-Ticaret Sistemi iş durumunu tamamlandı olarak güncellemelidir

### Gereksinim 5

**Kullanıcı Hikayesi:** Fiyatlandırma müdürü olarak, platformlar arası ürün fiyatlarını güncellemek istiyorum, böylece fiyatlandırma tutarlı kalır.

#### Kabul Kriterleri

1. WHEN fiyat güncellemeleri talep edildiğinde THEN E-Ticaret Sistemi fiyat değişikliklerini uygun platform bağlantı bileşenine göndermelidir
2. WHEN fiyat senkronizasyonu hatalarla karşılaştığında THEN E-Ticaret Sistemi hata detaylarını kaydetmeli ve işi yeniden deneme için tutmalıdır
3. WHEN birden fazla fiyat güncellemesi işlendiğinde THEN E-Ticaret Sistemi bunları toplu işlemlerde verimli şekilde ele almalıdır
4. E-Ticaret Sistemi iletimden önce fiyat veri formatını ve para birimini doğrulamalıdır
5. WHEN fiyat güncellemeleri başarılı olduğunda THEN E-Ticaret Sistemi ilgili işleri tamamlandı olarak işaretlemelidir

### Gereksinim 6

**Kullanıcı Hikayesi:** Kargo müdürü olarak, sipariş durumlarını ve takip bilgilerini güncellemek istiyorum, böylece müşteriler doğru teslimat bilgilerini alır.

#### Kabul Kriterleri

1. WHEN sipariş durum güncellemeleri gönderildiğinde THEN E-Ticaret Sistemi platformu yeni durum ve takip bilgileri ile güncellemelidir
2. WHEN takip numaraları sağlandığında THEN E-Ticaret Sistemi bunları platforma durum güncellemesine dahil etmelidir
3. WHEN durum güncellemesi başarısız olduğunda THEN E-Ticaret Sistemi başarısızlığı kaydetmeli ve işi yeniden deneme için tutmalıdır
4. E-Ticaret Sistemi standart sipariş durumlarını desteklemelidir: YENI, HAZIRLANIYOR, KARGODA, TESLIM, IPTAL
5. WHEN durum güncellemeleri işlendiğinde THEN E-Ticaret Sistemi durum geçişinin geçerli olduğunu doğrulamalıdır

### Gereksinim 7

**Kullanıcı Hikayesi:** Sistem operatörü olarak, asenkron iş kuyruğu sistemi istiyorum, böylece entegrasyon işlemleri ana uygulamayı bloke etmez.

#### Kabul Kriterleri

1. WHEN entegrasyon işlemleri talep edildiğinde THEN E-Ticaret Sistemi bunları uygun iş türleri ile kuyruğa almalıdır
2. WHEN işler işlendiğinde THEN İş Koşucusu bunları yapılandırılabilir toplu limitlerle FIFO sırasında yürütmelidir
3. WHEN işler yürütme sırasında başarısız olduğunda THEN E-Ticaret Sistemi iş durumunu HATA olarak güncellemeli ve hata detaylarını kaydetmelidir
4. WHEN işler başarıyla tamamlandığında THEN E-Ticaret Sistemi iş durumunu GONDERILDI olarak güncellemelidir
5. E-Ticaret Sistemi şu iş türlerini desteklemelidir: SIPARIS_CEK, STOK_GONDER, FIYAT_GONDER, DURUM_GUNCELLE

### Gereksinim 8

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, kapsamlı hata yönetimi ve kayıt tutma istiyorum, böylece entegrasyon sorunları teşhis edilip çözülebilir.

#### Kabul Kriterleri

1. WHEN herhangi bir entegrasyon işlemi başarısız olduğunda THEN E-Ticaret Sistemi zaman damgası ve bağlam dahil detaylı hata bilgilerini kaydetmelidir
2. WHEN veritabanı işlemleri hatalarla karşılaştığında THEN E-Ticaret Sistemi işlemleri geri almalı ve veri tutarlılığını korumalıdır
3. WHEN bağlantı bileşeni işlemleri başarısız olduğunda THEN E-Ticaret Sistemi açıklayıcı hata mesajları ile EntegrasyonHatasi fırlatmalıdır
4. WHEN işler tekrar tekrar başarısız olduğunda THEN E-Ticaret Sistemi üstel geri çekilme yeniden deneme mantığı uygulamalıdır
5. E-Ticaret Sistemi iş kuyruğu sağlığı ve hata oranları için izleme yetenekleri sağlamalıdır

### Gereksinim 9

**Kullanıcı Hikayesi:** Geliştirici olarak, net sorumluluk ayrımı olan modüler bir mimari istiyorum, böylece sistem sürdürülebilir ve genişletilebilir olur.

#### Kabul Kriterleri

1. WHEN katmanlar arası veri transferi gerçekleştiğinde THEN E-Ticaret Sistemi tür güvenliği ve doğrulama için VTO sınıfları kullanmalıdır
2. WHEN veritabanı işlemleri gerçekleştirildiğinde THEN E-Ticaret Sistemi veri erişimini soyutlamak için depo desenini kullanmalıdır
3. WHEN iş mantığı yürütüldüğünde THEN E-Ticaret Sistemi bunu veri erişiminden ayrı servis katmanında uygulamalıdır
4. E-Ticaret Sistemi şu bağımlılık yönünü takip etmelidir: Servis -> Depo -> Veritabanı
5. WHEN yeni platformlar eklendiğinde THEN E-Ticaret Sistemi sadece BaglantiArayuzu arayüzünün uygulanmasını gerektirmelidir

### Gereksinim 10

**Kullanıcı Hikayesi:** Sistem mimarı olarak, kısıtlamalar ve indeksler ile uygun veritabanı şeması istiyorum, böylece veri bütünlüğü ve performans korunur.

#### Kabul Kriterleri

1. WHEN mağaza hesapları oluşturulduğunda THEN E-Ticaret Sistemi uygun yerlerde platform ve mağaza kombinasyonları üzerinde benzersiz kısıtlamaları zorlamalıdır
2. WHEN siparişler depolandığında THEN E-Ticaret Sistemi magaza_hesabi_id ve dis_siparis_no kombinasyonu üzerinde benzersiz kısıtlamayı zorlamalıdır
3. WHEN veritabanı sorguları yürütüldüğünde THEN E-Ticaret Sistemi platform ve durum gibi sık sorgulanan alanlarda indeksleri kullanmalıdır
4. WHEN yabancı anahtar ilişkileri mevcut olduğunda THEN E-Ticaret Sistemi tablolar arası referans bütünlüğünü korumalıdır
5. E-Ticaret Sistemi şema evrimi için veritabanı göçlerini desteklemelidir