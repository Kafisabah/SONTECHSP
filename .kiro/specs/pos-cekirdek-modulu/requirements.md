# Requirements Document

## Introduction

POS (Point of Sale) çekirdek modülü, SONTECHSP sisteminin satış noktası işlemlerini yöneten temel bileşenidir. Bu modül barkodlu satış, sepet yönetimi, ödeme işlemleri, iade süreçleri, fiş oluşturma ve offline kuyruk yönetimi işlevlerini sağlar. Sistem çoklu mağaza/şube ve çoklu PC eş zamanlı çalışma desteği ile tasarlanmıştır.

## Glossary

- **POS_Sistemi**: Satış noktası işlemlerini yöneten ana sistem
- **Sepet**: Müşterinin satın almak istediği ürünlerin geçici olarak tutulduğu liste
- **Barkod_Okuyucu**: Ürün barkodlarını okuyarak sistem girdisi sağlayan cihaz
- **Offline_Kuyruk**: Network bağlantısı olmadığında işlemlerin geçici olarak saklandığı SQLite tabanlı kuyruk sistemi
- **Fiş_Yazıcı**: Satış fişi çıktısı üreten cihaz
- **Stok_Servisi**: Ürün stok durumlarını yöneten harici servis modülü
- **Terminal**: Satış işlemlerinin gerçekleştirildiği fiziksel nokta
- **Kasiyer**: Satış işlemlerini gerçekleştiren kullanıcı

## Requirements

### Requirement 1

**User Story:** Kasiyer olarak, barkod okutarak ürünleri sepete eklemek istiyorum, böylece hızlı ve doğru satış işlemi gerçekleştirebilirim.

#### Acceptance Criteria

1. WHEN kasiyer bir barkod okuttuğunda, THE POS_Sistemi SHALL barkodu Stok_Servisi üzerinden doğrular ve ürün bilgilerini getirir
2. WHEN geçerli bir ürün bulunduğunda, THE POS_Sistemi SHALL ürünü sepete ekler ve sepet toplamını günceller
3. WHEN aynı üründen birden fazla adet eklendiğinde, THE POS_Sistemi SHALL mevcut satır adedini artırır
4. WHEN geçersiz barkod okutulduğunda, THE POS_Sistemi SHALL hata mesajı gösterir ve sepeti değiştirmez
5. WHEN stok yetersiz ise, THE POS_Sistemi SHALL uyarı verir ve satışa izin vermez

### Requirement 2

**User Story:** Kasiyer olarak, sepetteki ürünleri yönetmek istiyorum, böylece müşteri taleplerini karşılayabilirim.

#### Acceptance Criteria

1. WHEN kasiyer sepet satırı silmek istediğinde, THE POS_Sistemi SHALL seçili satırı sepetten kaldırır
2. WHEN kasiyer ürün adedi değiştirmek istediğinde, THE POS_Sistemi SHALL yeni adedi doğrular ve sepet toplamını günceller
3. WHEN kasiyer indirim uygulamak istediğinde, THE POS_Sistemi SHALL indirim tutarını sepet toplamından düşer
4. WHEN sepet boşaltılmak istendiğinde, THE POS_Sistemi SHALL tüm satırları temizler ve toplamı sıfırlar

### Requirement 3

**User Story:** Kasiyer olarak, farklı ödeme yöntemleriyle satış tamamlamak istiyorum, böylece müşteri tercihlerini karşılayabilirim.

#### Acceptance Criteria

1. WHEN kasiyer tek ödeme yöntemi seçtiğinde, THE POS_Sistemi SHALL ödeme tutarını doğrular ve satışı tamamlar
2. WHEN kasiyer parçalı ödeme yapmak istediğinde, THE POS_Sistemi SHALL birden fazla ödeme yöntemini kabul eder
3. WHEN ödeme tutarı sepet toplamına eşit olduğunda, THE POS_Sistemi SHALL satışı onaylar ve stok düşümü yapar
4. WHEN ödeme tutarı yetersiz olduğunda, THE POS_Sistemi SHALL eksik tutarı bildirir ve satışı tamamlamaz
5. WHEN satış tamamlandığında, THE POS_Sistemi SHALL fiş oluşturur ve yazdırma için hazırlar

### Requirement 4

**User Story:** Kasiyer olarak, iade işlemlerini gerçekleştirmek istiyorum, böylece müşteri memnuniyetini sağlayabilirim.

#### Acceptance Criteria

1. WHEN kasiyer iade işlemi başlattığında, THE POS_Sistemi SHALL orijinal satış kaydını doğrular
2. WHEN iade edilecek kalemler seçildiğinde, THE POS_Sistemi SHALL iade tutarını hesaplar
3. WHEN iade onaylandığında, THE POS_Sistemi SHALL stok girişi yapar ve iade kaydı oluşturur
4. WHEN iade fiş yazdırılmak istendiğinde, THE POS_Sistemi SHALL iade fişi formatında çıktı üretir

### Requirement 5

**User Story:** Sistem yöneticisi olarak, offline durumda satış işlemlerinin kaybolmamasını istiyorum, böylece network kesintilerinde iş sürekliliği sağlanabilir.

#### Acceptance Criteria

1. WHEN network bağlantısı kesildiğinde, THE POS_Sistemi SHALL satış işlemlerini Offline_Kuyruk'a kaydeder
2. WHEN offline işlem kaydedildiğinde, THE POS_Sistemi SHALL kullanıcıya offline durumu bildirir
3. WHEN network bağlantısı geri geldiğinde, THE POS_Sistemi SHALL kuyruktan işlemleri sırayla gönderir
4. WHEN kuyruk işlemi başarısız olduğunda, THE POS_Sistemi SHALL hata durumunu kaydeder ve tekrar deneme yapar

### Requirement 6

**User Story:** Kasiyer olarak, satış fişi yazdırmak istiyorum, böylece müşteriye makbuz verebilirim.

#### Acceptance Criteria

1. WHEN satış tamamlandığında, THE POS_Sistemi SHALL fiş içeriğini formatlar
2. WHEN fiş formatlanırken, THE POS_Sistemi SHALL mağaza bilgileri, ürün listesi ve ödeme detaylarını içerir
3. WHEN fiş yazdırma komutu verildiğinde, THE POS_Sistemi SHALL Fiş_Yazıcı'ya metin formatında gönderir
4. WHEN yazdırma hatası oluştuğunda, THE POS_Sistemi SHALL hata mesajı gösterir ve fiş içeriğini saklar

### Requirement 7

**User Story:** Sistem yöneticisi olarak, eş zamanlı satış işlemlerinde stok tutarlılığının korunmasını istiyorum, böylece negatif stok durumları önlenebilir.

#### Acceptance Criteria

1. WHEN birden fazla Terminal aynı ürünü satmaya çalıştığında, THE POS_Sistemi SHALL stok kilitleme uygular
2. WHEN stok kontrolü yapılırken, THE POS_Sistemi SHALL güncel stok durumunu Stok_Servisi'nden alır
3. WHEN stok yetersiz ise, THE POS_Sistemi SHALL satış işlemini iptal eder ve stok kilidini serbest bırakır
4. WHEN satış tamamlandığında, THE POS_Sistemi SHALL transaction içinde stok düşümü yapar

### Requirement 8

**User Story:** Kasiyer olarak, satış işlemini iptal edebilmek istiyorum, böylece hatalı işlemleri düzeltebilirim.

#### Acceptance Criteria

1. WHEN kasiyer satış iptal etmek istediğinde, THE POS_Sistemi SHALL iptal nedenini sorar
2. WHEN iptal onaylandığında, THE POS_Sistemi SHALL sepeti temizler ve satış kaydını iptal durumuna getirir
3. WHEN rezerve edilmiş stok varsa, THE POS_Sistemi SHALL stok rezervasyonunu serbest bırakır
4. WHEN iptal işlemi tamamlandığında, THE POS_Sistemi SHALL yeni satış için hazır duruma geçer