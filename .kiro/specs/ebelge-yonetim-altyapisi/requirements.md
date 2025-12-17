# E-Belge Yönetim Altyapısı Gereksinimleri

## Giriş

SONTECHSP E-Belge yönetim altyapısı, yasal geçerliliği olan belgelerin (e-Fatura, e-Arşiv, e-İrsaliye) oluşturulmasını ve entegratörlere iletilmesini yönetecek merkezi bir modüldür. Bu modül, dış kaynaklardan (POS, Satış vb.) gelen belge taleplerini karşılar, bunları bir Outbox (Kuyruk) yapısında saklar ve asenkron olarak entegratör firmaya (Provider) iletir.

## Sözlük

- **EBelgeYoneticisi**: E-belge oluşturma ve gönderme işlemlerini yöneten sistem bileşeni
- **CikisKuyrugu**: Gönderilmek üzere bekleyen e-belgelerin saklandığı outbox tablosu
- **SaglayiciArayuzu**: Tüm entegratörlerin uyması gereken soyut sınıf arayüzü
- **SaglayiciFabrikasi**: Konfigürasyona göre uygun sağlayıcı implementasyonunu döndüren fabrika sınıfı
- **EBelgeDeposu**: E-belge verilerine erişim sağlayan repository katmanı
- **BelgeTuru**: E-belge türlerini belirten sabit değerler (EFATURA, EARSIV, EIRSALIYE)
- **KaynakTuru**: Belge talebinin hangi sistemden geldiğini belirten değerler (POS_SATIS, SATIS_BELGESI, IADE_BELGESI)
- **OutboxDurumu**: Kuyruk kayıtlarının durumunu belirten değerler (BEKLIYOR, GONDERILIYOR, GONDERILDI, HATA, IPTAL)
- **EntegrasyonHatasi**: E-belge işlemlerinde oluşan özel hata türü
- **IdempotencyKontrolu**: Aynı kaynak için mükerrer belge oluşturulmasını engelleyen mekanizma

## Gereksinimler

### Gereksinim 1

**Kullanıcı Hikayesi:** POS sistemi olarak, satış tamamlandığında e-fatura oluşturabilmek istiyorum ki yasal yükümlülükleri yerine getirebileyim.

#### Kabul Kriterleri

1. WHEN e-belge oluşturma isteği yapıldığında THEN EBelgeYoneticisi SHALL kaynak türü ve kaynak ID'sini zorunlu tutar
2. WHEN belge türü belirtildiğinde THEN EBelgeYoneticisi SHALL geçerli belge türlerini (EFATURA, EARSIV, EIRSALIYE) kabul eder
3. WHEN müşteri bilgileri verildiğinde THEN EBelgeYoneticisi SHALL müşteri adı ve vergi numarasını zorunlu tutar
4. WHEN belge JSON verisi sağlandığında THEN EBelgeYoneticisi SHALL JSON formatının geçerliliğini kontrol eder
5. WHERE para birimi belirtilmediğinde THEN EBelgeYoneticisi SHALL varsayılan olarak TRY kullanır

### Gereksinim 2

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, aynı satış için birden fazla fatura oluşturulmasını engellemek istiyorum ki mükerrer belge sorunu yaşamayayım.

#### Kabul Kriterleri

1. WHEN aynı kaynak türü ve kaynak ID ile ikinci belge oluşturma isteği yapıldığında THEN EBelgeYoneticisi SHALL EntegrasyonHatasi fırlatır
2. WHEN farklı belge türü ile aynı kaynak için istek yapıldığında THEN EBelgeYoneticisi SHALL yeni kayıt oluşturur
3. WHERE UNIQUE constraint ihlali oluştuğunda THEN EBelgeYoneticisi SHALL anlamlı hata mesajı döndürür
4. IF mükerrer kayıt tespit edildiğinde THEN EBelgeYoneticisi SHALL mevcut kaydın ID'sini döndürür
5. WHILE idempotency kontrolü yapılırken THEN EBelgeYoneticisi SHALL performanslı çalışır

### Gereksinim 3

**Kullanıcı Hikayesi:** E-belge sistemi olarak, oluşturulan belgeleri sırayla entegratöre gönderebilmek istiyorum ki kesintisiz işlem sağlayabileyim.

#### Kabul Kriterleri

1. WHEN bekleyen belgeler sorgulandığında THEN EBelgeYoneticisi SHALL BEKLIYOR durumundaki kayıtları getirir
2. WHEN hatalı belgeler sorgulandığında THEN EBelgeYoneticisi SHALL HATA durumunda ve deneme sayısı maksimumdan az olan kayıtları getirir
3. WHEN gönderim işlemi başlatıldığında THEN EBelgeYoneticisi SHALL kayıt durumunu GONDERILIYOR olarak günceller
4. WHERE limit parametresi verildiğinde THEN EBelgeYoneticisi SHALL belirtilen sayıda kayıt döndürür
5. IF bekleyen kayıt yoksa THEN EBelgeYoneticisi SHALL boş liste döndürür
### Gereksinim 4

**Kullanıcı Hikayesi:** Entegratör sağlayıcısı olarak, belge gönderim taleplerini alabilmek istiyorum ki e-belge işlemlerini gerçekleştirebileyim.

#### Kabul Kriterleri

1. WHEN sağlayıcı gönderim metodu çağrıldığında THEN SaglayiciArayuzu SHALL EBelgeGonderDTO parametresini kabul eder
2. WHEN gönderim başarılı olduğunda THEN SaglayiciArayuzu SHALL EBelgeSonucDTO ile başarı durumunu döndürür
3. WHEN gönderim başarısız olduğunda THEN SaglayiciArayuzu SHALL hata mesajı ile EBelgeSonucDTO döndürür
4. WHERE dış belge numarası alındığında THEN SaglayiciArayuzu SHALL dış belge numarasını sonuçta iletir
5. IF sağlayıcı erişilemezse THEN SaglayiciArayuzu SHALL bağlantı hatası döndürür

### Gereksinim 5

**Kullanıcı Hikayesi:** E-belge sistemi olarak, gönderim sonuçlarını işleyebilmek istiyorum ki belge durumlarını güncel tutabileyim.

#### Kabul Kriterleri

1. WHEN gönderim başarılı olduğunda THEN EBelgeYoneticisi SHALL kayıt durumunu GONDERILDI olarak günceller
2. WHEN dış belge numarası alındığında THEN EBelgeYoneticisi SHALL dış belge numarasını kaydeder
3. WHEN gönderim başarısız olduğunda THEN EBelgeYoneticisi SHALL deneme sayısını artırır
4. WHEN deneme sayısı maksimuma ulaştığında THEN EBelgeYoneticisi SHALL kalıcı hata durumuna geçer
5. WHERE hata mesajı alındığında THEN EBelgeYoneticisi SHALL hata mesajını kaydeder

### Gereksinim 6

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, belge durumlarını sorgulayabilmek istiyorum ki işlem takibi yapabileyim.

#### Kabul Kriterleri

1. WHEN belge durumu sorgulandığında THEN EBelgeYoneticisi SHALL güncel durum bilgisini döndürür
2. WHEN dış belge numarası mevcutsa THEN EBelgeYoneticisi SHALL entegratörden son durumu sorgular
3. WHEN durum güncellemesi yapıldığında THEN EBelgeYoneticisi SHALL veritabanı kaydını günceller
4. WHERE belge bulunamadığında THEN EBelgeYoneticisi SHALL uygun hata mesajı döndürür
5. IF entegratör sorgusu başarısızsa THEN EBelgeYoneticisi SHALL mevcut durumu döndürür

### Gereksinim 7

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, belge durum değişikliklerini izleyebilmek istiyorum ki audit trail sağlayabileyim.

#### Kabul Kriterleri

1. WHEN belge durumu değiştiğinde THEN EBelgeYoneticisi SHALL durum geçmişi tablosuna kayıt ekler
2. WHEN durum değişikliği kaydedildiğinde THEN EBelgeYoneticisi SHALL zaman damgasını otomatik atar
3. WHERE hata mesajı varsa THEN EBelgeYoneticisi SHALL hata mesajını durum geçmişine kaydeder
4. WHEN durum geçmişi sorgulandığında THEN EBelgeYoneticisi SHALL kronolojik sırada listeler
5. IF durum geçmişi boşsa THEN EBelgeYoneticisi SHALL boş liste döndürür
### Gereksinim 8

**Kullanıcı Hikayesi:** Geliştirici olarak, farklı entegratör sağlayıcılarını kolayca değiştirebilmek istiyorum ki vendor bağımlılığı yaşamayayım.

#### Kabul Kriterleri

1. WHEN sağlayıcı fabrikası çağrıldığında THEN SaglayiciFabrikasi SHALL konfigürasyona göre uygun sağlayıcıyı döndürür
2. WHEN yeni sağlayıcı eklendiğinde THEN SaglayiciFabrikasi SHALL SaglayiciArayuzu implementasyonunu kabul eder
3. WHERE sağlayıcı bulunamadığında THEN SaglayiciFabrikasi SHALL varsayılan DummySaglayici döndürür
4. WHEN sağlayıcı değiştirildiğinde THEN sistem SHALL mevcut işlemleri etkilemez
5. IF sağlayıcı konfigürasyonu geçersizse THEN SaglayiciFabrikasi SHALL konfigürasyon hatası fırlatır

### Gereksinim 9

**Kullanıcı Hikayesi:** Test ortamında çalışan geliştirici olarak, gerçek entegratör olmadan test yapabilmek istiyorum ki geliştirme sürecini hızlandırabileyim.

#### Kabul Kriterleri

1. WHEN DummySaglayici kullanıldığında THEN sistem SHALL gerçek API çağrısı yapmaz
2. WHEN simülasyon modu aktifse THEN DummySaglayici SHALL rastgele başarı/başarısızlık döndürür
3. WHEN her zaman başarılı modu aktifse THEN DummySaglayici SHALL her zaman başarılı sonuç döndürür
4. WHERE log seviyesi ayarlandığında THEN DummySaglayici SHALL işlem detaylarını loglar
5. IF test senaryosu belirtildiğinde THEN DummySaglayici SHALL belirtilen senaryoyu simüle eder

### Gereksinim 10

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, başarısız belge gönderimlerinin otomatik tekrar denenmesini istiyorum ki manuel müdahale gerektirmeyeyim.

#### Kabul Kriterleri

1. WHEN gönderim başarısız olduğunda THEN EBelgeYoneticisi SHALL deneme sayısını bir artırır
2. WHEN deneme sayısı maksimum değerin altındaysa THEN EBelgeYoneticisi SHALL kaydı tekrar deneme için işaretler
3. WHEN maksimum deneme sayısına ulaşıldığında THEN EBelgeYoneticisi SHALL kaydı kalıcı hata durumuna geçirir
4. WHERE retry işlemi yapıldığında THEN EBelgeYoneticisi SHALL exponential backoff uygular
5. IF sistem yeniden başlatıldığında THEN EBelgeYoneticisi SHALL bekleyen kayıtları otomatik işler

### Gereksinim 11

**Kullanıcı Hikayesi:** Geliştirici olarak, e-belge işlemlerinin atomik olmasını istiyorum ki veri tutarlılığı sağlayabileyim.

#### Kabul Kriterleri

1. WHEN e-belge işlemi yapıldığında THEN EBelgeDeposu SHALL transaction kullanır
2. WHEN durum güncellemesi yapıldığında THEN EBelgeDeposu SHALL durum geçmişi ile birlikte atomik günceller
3. WHERE eş zamanlı erişim olduğunda THEN sistem SHALL row-level lock uygular
4. IF transaction başarısızsa THEN sistem SHALL rollback yapar
5. WHILE veritabanı işlemi yapılırken THEN sistem SHALL ACID özelliklerini korur
### Gereksinim 12

**Kullanıcı Hikayesi:** Geliştirici olarak, e-belge modülünün diğer katmanlardan bağımsız olmasını istiyorum ki temiz mimari sağlayabileyim.

#### Kabul Kriterleri

1. WHEN e-belge modülü import edildiğinde THEN sistem SHALL UI katmanından bağımsız çalışır
2. WHEN e-belge servisleri kullanıldığında THEN sistem SHALL sadece repository katmanını kullanır
3. WHERE bağımlılık analizi yapıldığında THEN e-belge modülü SHALL temiz katman yapısını korur
4. IF e-belge modülü test edildiğinde THEN sistem SHALL izole test edilebilir
5. WHILE e-belge işlevleri çalışırken THEN sistem SHALL performanslı çalışır

### Gereksinim 13

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, e-belge işlemlerinin loglanmasını istiyorum ki sorun giderme yapabileyim.

#### Kabul Kriterleri

1. WHEN e-belge işlemi başlatıldığında THEN sistem SHALL işlem başlangıcını loglar
2. WHEN gönderim başarılı olduğunda THEN sistem SHALL başarı durumunu loglar
3. WHEN hata oluştuğunda THEN sistem SHALL hata detaylarını loglar
4. WHERE kritik işlem yapıldığında THEN sistem SHALL audit log seviyesinde kayıt tutar
5. IF performans sorunu tespit edildiğinde THEN sistem SHALL performans metriklerini loglar

### Gereksinim 14

**Kullanıcı Hikayesi:** E-belge sistemi olarak, belge JSON verilerini doğru şekilde saklayabilmek istiyorum ki veri kaybı yaşamayayım.

#### Kabul Kriterleri

1. WHEN belge JSON verisi kaydedildiğinde THEN sistem SHALL JSON formatının bütünlüğünü korur
2. WHEN JSON verisi okunduğunda THEN sistem SHALL orijinal yapıyı geri döndürür
3. WHERE büyük JSON verileri işlendiğinde THEN sistem SHALL performanslı çalışır
4. IF JSON verisi bozuksa THEN sistem SHALL doğrulama hatası fırlatır
5. WHILE JSON işlemi yapılırken THEN sistem SHALL encoding sorunlarını önler

### Gereksinim 15

**Kullanıcı Hikayesi:** Entegratör sağlayıcısı olarak, belge durumu sorgulayabilmek istiyorum ki güncel durum bilgisi sağlayabileyim.

#### Kabul Kriterleri

1. WHEN durum sorgulama metodu çağrıldığında THEN SaglayiciArayuzu SHALL dış belge numarasını parametre olarak kabul eder
2. WHEN durum sorgusu başarılı olduğunda THEN SaglayiciArayuzu SHALL güncel durum bilgisini döndürür
3. WHEN belge bulunamadığında THEN SaglayiciArayuzu SHALL belge bulunamadı hatası döndürür
4. WHERE API limiti aşıldığında THEN SaglayiciArayuzu SHALL rate limit hatası döndürür
5. IF bağlantı sorunu varsa THEN SaglayiciArayuzu SHALL bağlantı hatası döndürür