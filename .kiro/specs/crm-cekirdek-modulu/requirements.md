# CRM Çekirdek Modülü Gereksinimleri

## Giriş

SONTECHSP CRM çekirdek modülü, müşteri yönetimi ve sadakat programı işlevselliğini sağlayan temel bileşenleri içerir. Bu modül, POS ve satış belgeleri ile entegre edilecek şekilde tasarlanmış "hook" sözleşmeleri ile diğer modüllerle etkileşim kurar. Modül sadece servis, depo ve model katmanlarını içerir; UI bileşenleri içermez.

## Sözlük

- **MusteriYoneticisi**: Müşteri bilgilerini yöneten sistem bileşeni
- **SadakatSistemi**: Müşteri sadakat puanlarını yöneten sistem
- **PuanIslemTuru**: Puan işlemlerinin türünü belirten sabit değerler (KAZANIM, HARCAMA, DUZELTME)
- **ReferansTuru**: Puan işlemlerinin hangi sistemden kaynaklandığını belirten değerler (POS_SATIS, SATIS_BELGESI)
- **EntegrasyonKancasi**: Diğer modüllerle etkileşim için tanımlanan sözleşme arayüzleri
- **MusteriDeposu**: Müşteri verilerine erişim sağlayan repository katmanı
- **SadakatDeposu**: Sadakat puan verilerine erişim sağlayan repository katmanı

## Gereksinimler

### Gereksinim 1

**Kullanıcı Hikayesi:** Satış temsilcisi olarak, yeni müşteri kaydı oluşturabilmek istiyorum ki müşteri bilgilerini sistemde tutabileyim.

#### Kabul Kriterleri

1. WHEN müşteri oluşturma isteği yapıldığında THEN MusteriYoneticisi SHALL ad ve soyad alanlarını zorunlu tutar
2. WHEN telefon numarası girildiğinde THEN MusteriYoneticisi SHALL benzersizlik kontrolü yapar
3. WHEN e-posta adresi girildiğinde THEN MusteriYoneticisi SHALL geçerlilik ve benzersizlik kontrolü yapar
4. WHERE müşteri aktif durumda oluşturulduğunda THEN MusteriYoneticisi SHALL aktif_mi alanını True olarak ayarlar
5. WHEN müşteri kaydı oluşturulduğunda THEN MusteriYoneticisi SHALL oluşturulma ve güncellenme zamanlarını otomatik atar

### Gereksinim 2

**Kullanıcı Hikayesi:** Satış temsilcisi olarak, mevcut müşteri bilgilerini güncelleyebilmek istiyorum ki müşteri verilerini güncel tutabileyim.

#### Kabul Kriterleri

1. WHEN müşteri güncelleme isteği yapıldığında THEN MusteriYoneticisi SHALL sadece gönderilen alanları günceller
2. WHEN telefon numarası güncellendiğinde THEN MusteriYoneticisi SHALL benzersizlik kontrolü yapar
3. WHEN e-posta adresi güncellendiğinde THEN MusteriYoneticisi SHALL geçerlilik ve benzersizlik kontrolü yapar
4. WHEN güncelleme işlemi yapıldığında THEN MusteriYoneticisi SHALL güncellenme_zamani alanını otomatik günceller
5. IF geçersiz müşteri ID'si verildiğinde THEN MusteriYoneticisi SHALL DogrulamaHatasi fırlatır

### Gereksinim 3

**Kullanıcı Hikayesi:** Satış temsilcisi olarak, müşteri arama yapabilmek istiyorum ki hızlı şekilde müşteri bulabileyim.

#### Kabul Kriterleri

1. WHEN ad/soyad ile arama yapıldığında THEN MusteriYoneticisi SHALL kısmi eşleşme ile sonuç döndürür
2. WHEN telefon numarası ile arama yapıldığında THEN MusteriYoneticisi SHALL tam eşleşme ile sonuç döndürür
3. WHEN e-posta ile arama yapıldığında THEN MusteriYoneticisi SHALL tam eşleşme ile sonuç döndürür
4. WHERE birden fazla kriter verildiğinde THEN MusteriYoneticisi SHALL AND mantığı ile filtreler
5. WHEN arama sonucu bulunamadığında THEN MusteriYoneticisi SHALL boş liste döndürür

### Gereksinim 4

**Kullanıcı Hikayesi:** Kasiyer olarak, müşteri puan kazanımı işlemi yapabilmek istiyorum ki sadakat programını uygulayabileyim.

#### Kabul Kriterleri

1. WHEN puan kazanım işlemi yapıldığında THEN SadakatSistemi SHALL pozitif puan değeri kabul eder
2. WHEN puan kaydı oluşturulduğunda THEN SadakatSistemi SHALL işlem türünü KAZANIM olarak ayarlar
3. WHEN referans bilgisi verildiğinde THEN SadakatSistemi SHALL referans türü ve ID'sini kaydeder
4. WHERE açıklama metni verildiğinde THEN SadakatSistemi SHALL açıklamayı kaydeder
5. WHEN puan işlemi tamamlandığında THEN SadakatSistemi SHALL işlem zamanını otomatik atar

### Gereksinim 5

**Kullanıcı Hikayesi:** Kasiyer olarak, müşteri puan harcama işlemi yapabilmek istiyorum ki müşteri puanlarını kullanabileyim.

#### Kabul Kriterleri

1. WHEN puan harcama isteği yapıldığında THEN SadakatSistemi SHALL müşteri bakiyesini kontrol eder
2. WHEN bakiye yetersizse THEN SadakatSistemi SHALL DogrulamaHatasi fırlatır
3. WHEN bakiye yeterliyse THEN SadakatSistemi SHALL puan harcama işlemini kaydeder
4. WHEN puan harcandığında THEN SadakatSistemi SHALL işlem türünü HARCAMA olarak ayarlar
5. WHERE transaction içinde işlem yapıldığında THEN SadakatSistemi SHALL atomik işlem sağlar

### Gereksinim 6

**Kullanıcı Hikayesi:** Müşteri olarak, puan bakiyemi sorgulayabilmek istiyorum ki mevcut puanlarımı bilebileyim.

#### Kabul Kriterleri

1. WHEN puan bakiyesi sorgulandığında THEN SadakatSistemi SHALL güncel bakiyeyi hesaplar
2. WHEN müşteri ID geçersizse THEN SadakatSistemi SHALL sıfır bakiye döndürür
3. WHEN puan hareketi yoksa THEN SadakatSistemi SHALL sıfır bakiye döndürür
4. WHERE bakiye hesaplaması yapıldığında THEN SadakatSistemi SHALL KAZANIM - HARCAMA formülünü kullanır
5. WHILE bakiye sorgulanırken THEN SadakatSistemi SHALL performanslı çalışır

### Gereksinim 7

**Kullanıcı Hikayesi:** Müşteri olarak, puan hareketlerimi görebilmek istiyorum ki puan geçmişimi takip edebileyim.

#### Kabul Kriterleri

1. WHEN puan hareketleri sorgulandığında THEN SadakatSistemi SHALL tarih sırasına göre listeler
2. WHEN limit parametresi verildiğinde THEN SadakatSistemi SHALL belirtilen sayıda kayıt döndürür
3. WHERE limit verilmediğinde THEN SadakatSistemi SHALL varsayılan 100 kayıt döndürür
4. WHEN hareket listesi boşsa THEN SadakatSistemi SHALL boş liste döndürür
5. WHILE hareket sorgulanırken THEN SadakatSistemi SHALL sayfalama desteği sağlar

### Gereksinim 8

**Kullanıcı Hikayesi:** POS sistemi olarak, satış tamamlandığında müşteriye puan kazandırabilmek istiyorum ki entegrasyon sağlayabileyim.

#### Kabul Kriterleri

1. WHEN POS satış tamamlandığında THEN EntegrasyonKancasi SHALL puan hesaplama fonksiyonunu çağırır
2. WHEN toplam tutar verildiğinde THEN EntegrasyonKancasi SHALL 1 TL = 1 puan kuralını uygular
3. WHEN müşteri ID geçersizse THEN EntegrasyonKancasi SHALL işlemi sessizce atlar
4. WHERE referans bilgisi verildiğinde THEN EntegrasyonKancasi SHALL POS_SATIS türünde kaydeder
5. IF puan kazanım işlemi başarısızsa THEN EntegrasyonKancasi SHALL hata loglar ama POS işlemini durdurmaz

### Gereksinim 9

**Kullanıcı Hikayesi:** Satış belgeleri sistemi olarak, belge oluşturulduğunda müşteriye puan kazandırabilmek istiyorum ki entegrasyon sağlayabileyim.

#### Kabul Kriterleri

1. WHEN satış belgesi oluşturulduğunda THEN EntegrasyonKancasi SHALL puan hesaplama fonksiyonunu çağırır
2. WHEN belge tutarı verildiğinde THEN EntegrasyonKancasi SHALL 1 TL = 1 puan kuralını uygular
3. WHERE referans bilgisi verildiğinde THEN EntegrasyonKancasi SHALL SATIS_BELGESI türünde kaydeder
4. WHEN müşteri bilgisi eksikse THEN EntegrasyonKancasi SHALL işlemi sessizce atlar
5. WHILE entegrasyon çalışırken THEN EntegrasyonKancasi SHALL asenkron işlem desteği sağlar

### Gereksinim 10

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, puan düzeltme işlemi yapabilmek istiyorum ki hatalı puan işlemlerini düzeltebileyim.

#### Kabul Kriterleri

1. WHEN puan düzeltme işlemi yapıldığında THEN SadakatSistemi SHALL DUZELTME türünde kayıt oluşturur
2. WHEN pozitif düzeltme yapıldığında THEN SadakatSistemi SHALL bakiyeyi artırır
3. WHEN negatif düzeltme yapıldığında THEN SadakatSistemi SHALL bakiye kontrolü yapar
4. WHERE açıklama zorunlu olduğunda THEN SadakatSistemi SHALL açıklama alanını kontrol eder
5. IF düzeltme işlemi geçersizse THEN SadakatSistemi SHALL DogrulamaHatasi fırlatır

### Gereksinim 11

**Kullanıcı Hikayesi:** Geliştirici olarak, veritabanı işlemlerinin tutarlı olmasını istiyorum ki veri bütünlüğü sağlayabileyim.

#### Kabul Kriterleri

1. WHEN puan işlemi yapıldığında THEN SadakatDeposu SHALL transaction kullanır
2. WHEN müşteri işlemi yapıldığında THEN MusteriDeposu SHALL transaction kullanır
3. WHERE eş zamanlı erişim olduğunda THEN sistem SHALL row-level lock uygular
4. IF transaction başarısızsa THEN sistem SHALL rollback yapar
5. WHILE veritabanı işlemi yapılırken THEN sistem SHALL ACID özelliklerini korur

### Gereksinim 12

**Kullanıcı Hikayesi:** Geliştirici olarak, CRM modülünün diğer katmanlardan bağımsız olmasını istiyorum ki temiz mimari sağlayabileyim.

#### Kabul Kriterleri

1. WHEN CRM modülü import edildiğinde THEN sistem SHALL UI katmanından bağımsız çalışır
2. WHEN CRM servisleri kullanıldığında THEN sistem SHALL sadece repository katmanını kullanır
3. WHERE bağımlılık analizi yapıldığında THEN CRM modülü SHALL temiz katman yapısını korur
4. IF CRM modülü test edildiğinde THEN sistem SHALL izole test edilebilir
5. WHILE CRM işlevleri çalışırken THEN sistem SHALL performanslı çalışır