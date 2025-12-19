# Test ve Stabilizasyon Paketi - Gereksinimler Belgesi

## Giriş

SONTECHSP sistemi için kritik iş kurallarının doğruluğunu garanti eden test ve stabilizasyon paketi. Bu paket, stok tutarlılığı, negatif stok kuralları, POS transaction bütünlüğü, e-belge retry mekanizması ve offline kuyruk işleyişinin güvenilirliğini test eder.

## Sözlük

- **Test_Sistemi**: Test çalıştırma ve raporlama altyapısı
- **Stok_Negatif_Kontrol**: Negatif stok limitlerini kontrol eden sistem
- **POS_Transaction**: POS satış işlemlerinin atomik transaction yönetimi
- **EBelge_Retry**: E-belge gönderim hatalarında yeniden deneme sistemi
- **Offline_Kuyruk**: İnternet bağlantısı olmadığında işlemleri saklayan kuyruk sistemi
- **Smoke_Test**: Temel sistem fonksiyonlarının çalışırlığını kontrol eden hızlı testler

## Gereksinimler

### Gereksinim 1

**Kullanıcı Hikayesi:** Kalite güvence uzmanı olarak, test stratejisini ve çalıştırma yöntemlerini anlayabilmek için kapsamlı test dokümantasyonu istiyorum.

#### Kabul Kriterleri

1. WHEN test dokümantasyonu okunduğunda THE Test_Sistemi SHALL test stratejisini, çalıştırma yöntemlerini ve ortam gereksinimlerini açık şekilde sunmalı
2. WHEN test ortamı kurulduğunda THE Test_Sistemi SHALL ayrı test veritabanı kullanarak üretim verilerini etkilememeli
3. WHEN testler çalıştırıldığında THE Test_Sistemi SHALL her test kategorisi için ayrı çalıştırma komutları sağlamalı
4. WHEN test sonuçları raporlandığında THE Test_Sistemi SHALL başarı/başarısızlık durumlarını net şekilde göstermeli

### Gereksinim 2

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, negatif stok kurallarının doğru çalıştığından emin olmak için kapsamlı negatif stok testleri istiyorum.

#### Kabul Kriterleri

1. WHEN stok seviyesi 0 olduğunda THE Stok_Negatif_Kontrol SHALL uyarı verip işleme izin vermeli
2. WHEN stok seviyesi -1 ile -3 arasında olduğunda THE Stok_Negatif_Kontrol SHALL uyarı verip işleme izin vermeli  
3. WHEN stok seviyesi -6 veya daha düşük olduğunda THE Stok_Negatif_Kontrol SHALL DogrulamaHatasi fırlatarak işlemi engellemeli
4. WHEN farklı ürünler test edildiğinde THE Stok_Negatif_Kontrol SHALL her ürün için tutarlı kurallar uygulamalı

### Gereksinim 3

**Kullanıcı Hikayesi:** POS operatörü olarak, eş zamanlı stok işlemlerinde veri tutarlılığından emin olmak için paralel stok testleri istiyorum.

#### Kabul Kriterleri

1. WHEN aynı ürün için eş zamanlı stok düşüm işlemleri yapıldığında THE Test_Sistemi SHALL row-level lock mekanizmasını test etmeli
2. WHEN paralel işlemler çakıştığında THE Test_Sistemi SHALL sadece bir işlemin başarılı olduğunu doğrulamalı
3. WHEN stok tutarlılığı kontrol edildiğinde THE Test_Sistemi SHALL final stok seviyesinin matematiksel olarak doğru olduğunu onaylamalı
4. WHEN eş zamanlı işlemler tamamlandığında THE Test_Sistemi SHALL hiçbir veri kaybı olmadığını garanti etmeli

### Gereksinim 4

**Kullanıcı Hikayesi:** POS operatörü olarak, ödeme işlemlerinin atomik olduğundan emin olmak için transaction bütünlük testleri istiyorum.

#### Kabul Kriterleri

1. WHEN POS ödeme işlemi başlatıldığında THE POS_Transaction SHALL stok düşümü ve satış kaydını tek transaction içinde yapmalı
2. WHEN transaction sırasında hata oluştuğunda THE POS_Transaction SHALL tüm değişiklikleri geri almalı (rollback)
3. WHEN ödeme tamamlandığında THE POS_Transaction SHALL stok düşümü olmadan satış durumunun TAMAMLANDI olmamasını garanti etmeli
4. WHEN transaction başarısız olduğunda THE POS_Transaction SHALL sistem durumunu işlem öncesi haline döndürmeli

### Gereksinim 5

**Kullanıcı Hikayesi:** Sistem yöneticisi olarak, e-belge gönderim hatalarında retry mekanizmasının doğru çalıştığından emin olmak için e-belge retry testleri istiyorum.

#### Kabul Kriterleri

1. WHEN e-belge gönderimi başarısız olduğunda THE EBelge_Retry SHALL deneme_sayisi değerini artırmalı
2. WHEN maksimum deneme sayısına ulaşıldığında THE EBelge_Retry SHALL belge durumunu kalıcı HATA olarak işaretlemeli
3. WHEN DummySaglayici hata simülasyonu yapıldığında THE EBelge_Retry SHALL gerçekçi hata senaryolarını test etmeli
4. WHEN retry işlemi başarılı olduğunda THE EBelge_Retry SHALL deneme sayacını sıfırlamalı

### Gereksinim 6

**Kullanıcı Hikayesi:** POS operatörü olarak, internet bağlantısı olmadığında işlemlerin kaybolmadığından emin olmak için offline kuyruk testleri istiyorum.

#### Kabul Kriterleri

1. WHEN internet bağlantısı olmadığında THE Offline_Kuyruk SHALL işlemleri SQLite kuyruğuna kaydetmeli
2. WHEN kuyruktan kayıt okunduğunda THE Offline_Kuyruk SHALL FIFO (ilk giren ilk çıkar) sırasını korumalı
3. WHEN internet bağlantısı geri geldiğinde THE Offline_Kuyruk SHALL kuyruktaki işlemleri sırayla işlemeli
4. WHEN kuyruk işlemi tamamlandığında THE Offline_Kuyruk SHALL işlenen kaydı kuyruktan silmeli

### Gereksinim 7

**Kullanıcı Hikayesi:** Test uzmanı olarak, temel sistem fonksiyonlarının çalışırlığını hızlıca kontrol etmek için smoke testleri istiyorum.

#### Kabul Kriterleri

1. WHEN smoke test çalıştırıldığında THE Smoke_Test SHALL tüm ana modüllerin import edilebilirliğini kontrol etmeli
2. WHEN temel fonksiyonlar test edildiğinde THE Smoke_Test SHALL kritik servislerin başlatılabilirliğini doğrulamalı
3. WHEN smoke test tamamlandığında THE Smoke_Test SHALL test sonuçlarını özet rapor halinde sunmalı
4. WHERE mevcut smoke_test_calistir.py varsa THE Smoke_Test SHALL bu altyapıyı kullanarak genişletilmiş kontroller yapmalı