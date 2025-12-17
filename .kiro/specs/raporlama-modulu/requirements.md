# Gereksinimler Dokümanı

## Giriş

SONTECHSP için raporlama modülü geliştirilecektir. Bu modül, satış özeti, stok durumu, ürün performansı ve karlılık analizleri gibi temel raporları üretecek ve CSV/PDF formatlarında dışa aktarım imkanı sağlayacaktır. Modül, UI katmanından bağımsız olarak servis ve repository katmanlarında çalışacak, ağır sorguları optimize edilmiş şekilde gerçekleştirecektir.

## Sözlük

- **Raporlama_Sistemi**: Satış, stok ve performans verilerini analiz ederek raporlar üreten sistem
- **Sorgu_Katmani**: Veritabanı sorgularını optimize edilmiş şekilde gerçekleştiren katman
- **Disari_Aktarim_Servisi**: Raporları CSV ve PDF formatlarında dışa aktaran servis
- **Satis_Ozeti**: Belirli tarih aralığında mağaza bazında satış performansını gösteren rapor
- **Kritik_Stok**: Stok seviyesi kritik eşiğin altında olan ürünleri listeleyen rapor
- **Urun_Performansi**: Ürünlerin satış miktarı ve ciro bazında performansını gösteren rapor
- **Karlilik_Raporu**: Ürün ve mağaza bazında karlılık analizini gösteren rapor (MVP'de placeholder)

## Gereksinimler

### Gereksinim 1

**Kullanıcı Hikayesi:** Mağaza müdürü olarak, belirli tarih aralıkları için satış özet raporlarını görüntülemek istiyorum, böylece mağaza performansını analiz edebilir ve bilinçli iş kararları verebilirim.

#### Kabul Kriterleri

1. Kullanıcı bir tarih aralığı için satış özeti talep ettiğinde, Raporlama_Sistemi belirtilen mağaza için brüt satış, indirim toplamları, net satış ve satış sayısını döndürmelidir
2. Satış özetini hesaplarken, Raporlama_Sistemi yalnızca TAMAMLANDI durumundaki tamamlanmış satış işlemlerini filtrelemelidir
3. Belirtilen dönem için satış verisi bulunmadığında, Raporlama_Sistemi tüm metrikler için sıfır değerleri döndürmelidir
4. Satış özeti talebini işlerken, Raporlama_Sistemi verileri mağaza bazında gruplandırmalı ve toplamları doğru şekilde toplamalıdır
5. Satış özeti oluşturulduğunda, Raporlama_Sistemi iade tutarlarını hesaplamaya dahil etmelidir

### Gereksinim 2

**Kullanıcı Hikayesi:** Depo sorumlusu olarak, kritik stok seviyelerini izlemek istiyorum, böylece stok tükenmelerini önleyebilir ve yeterli envanter seviyelerini koruyabilirim.

#### Kabul Kriterleri

1. Kritik stok raporu talep edildiğinde, Raporlama_Sistemi mevcut stoğu kritik eşikte veya altında olan ürünleri döndürmelidir
2. Kritik stok listesi oluştururken, Raporlama_Sistemi ürün ve stok bakiye tablolarını doğru şekilde birleştirmelidir
3. Kritik seviyede ürün bulunmadığında, Raporlama_Sistemi boş bir liste döndürmelidir
4. Belirli depo için kritik stok raporu talep edildiğinde, Raporlama_Sistemi sonuçları depo ID'sine göre filtrelemelidir
5. Kritik stok görüntülenirken, Raporlama_Sistemi ürün ID'si, adı, depo ID'si, mevcut miktar ve kritik seviyeyi göstermelidir

### Gereksinim 3

**Kullanıcı Hikayesi:** Satış müdürü olarak, en çok satan ürünler raporunu görmek istiyorum, böylece en iyi performans gösterenleri belirleyebilir ve envanter kararlarını optimize edebilirim.

#### Kabul Kriterleri

1. En çok satan ürünler talep edildiğinde, Raporlama_Sistemi ürünleri toplam satılan miktara göre sıralanmış şekilde döndürmelidir
2. En çok satan raporu oluştururken, Raporlama_Sistemi satış verilerini ürüne göre gruplandırmalı ve miktarları toplamalıdır
3. Limit parametresi belirtildiğinde, Raporlama_Sistemi tam olarak o sayıda en iyi ürünü döndürmelidir
4. Dönem için satış bulunmadığında, Raporlama_Sistemi boş bir liste döndürmelidir
5. Ürün performansını hesaplarken, Raporlama_Sistemi hem miktar hem de gelir toplamlarını içermelidir

### Gereksinim 4

**Kullanıcı Hikayesi:** Muhasebe sorumlusu olarak, raporları CSV ve PDF formatlarında dışa aktarmak istiyorum, böylece verileri dış paydaşlarla paylaşabilir ve kayıtları tutabilirim.

#### Kabul Kriterleri

1. CSV formatına dışa aktarırken, Disari_Aktarim_Servisi başlıklar ve veri satırları ile düzgün formatlanmış bir CSV dosyası oluşturmalıdır
2. PDF formatına dışa aktarırken, Disari_Aktarim_Servisi tablo şeklinde veri sunumu ile bir PDF belgesi oluşturmalıdır
3. Dışa aktarma işlemi başarıyla tamamlandığında, Disari_Aktarim_Servisi oluşturulan belgenin tam dosya yolunu döndürmelidir
4. Dosya sistemi sorunları nedeniyle dışa aktarma başarısız olduğunda, Disari_Aktarim_Servisi açıklayıcı mesajla uygun hata fırlatmalıdır
5. Dışa aktarma dosya adları oluştururken, Disari_Aktarim_Servisi benzersizlik için zaman damgası ve rapor türünü içermelidir

### Gereksinim 5

**Kullanıcı Hikayesi:** Genel müdür olarak, karlılık raporlarına erişmek istiyorum, böylece iş marjlarını analiz edebilir ve stratejik kararlar verebilirim.

#### Kabul Kriterleri

1. Karlılık raporu talep edildiğinde, Raporlama_Sistemi MVP uygulaması için placeholder veri yapısı döndürmelidir
2. Karlılık hesaplaması mevcut olmadığında, Raporlama_Sistemi null/boş karlılık alanları ile rapor satırları döndürmelidir
3. Karlılık raporu talep edildiğinde, Raporlama_Sistemi çökmemeli veya hata fırlatmamalıdır
4. MVP karlılık raporu oluşturulduğunda, Raporlama_Sistemi placeholder kar alanları ile birlikte ürün ve satış verilerini içermelidir
5. Karlılık servisi çağrıldığında, Raporlama_Sistemi bunun MVP placeholder işlevselliği olduğunu loglamalıdır

### Gereksinim 6

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, raporlama sisteminin veritabanı sorgularını verimli şekilde işlemesini istiyorum, böylece raporlar sistem performansını etkilemeden hızlıca oluşturulabilir.

#### Kabul Kriterleri

1. Rapor sorguları çalıştırırken, Sorgu_Katmani salt okunur veritabanı oturumları kullanmalıdır
2. Büyük veri setlerini işlerken, Sorgu_Katmani uygun sorgu optimizasyon tekniklerini uygulamalıdır
3. Aynı anda birden fazla rapor talep edildiğinde, Sorgu_Katmani eş zamanlı erişimi güvenli şekilde işlemelidir
4. Veritabanı bağlantısı başarısız olduğunda, Sorgu_Katmani uygun veritabanı bağlantı hatalarını fırlatmalıdır
5. Sorgu yürütme makul zaman sınırlarını aştığında, Sorgu_Katmani performans uyarılarını loglamalıdır

### Gereksinim 7

**Kullanıcı Hikayesi:** Yazılım geliştirici olarak, raporlama modülünün temiz mimari prensiplerine uymasını istiyorum, böylece kod sürdürülebilir ve test edilebilir olsun.

#### Kabul Kriterleri

1. Raporlama servislerini uygularken, Raporlama_Sistemi hiçbir UI bileşenini import etmemelidir
2. Kod yapısını organize ederken, Raporlama_Sistemi endişeleri DTO, servis ve sorgu katmanlarına ayırmalıdır
3. Veri transferini işlerken, Raporlama_Sistemi tüm veri yapıları için güçlü tipli DTO sınıfları kullanmalıdır
4. İş mantığını uygularken, Raporlama_Sistemi tüm mantığı sorgu katmanında değil, servis katmanında tutmalıdır
5. Bağımlılıkları yönetirken, Raporlama_Sistemi sistemin kurulu bağımlılık enjeksiyon desenlerini takip etmelidir