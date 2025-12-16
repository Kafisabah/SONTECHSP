# Requirements Document

## Introduction

SONTECHSP projesi için PyQt6 tabanlı kullanıcı arayüzü iskeletlerinin geliştirilmesi. Bu sistem, POS + ERP + CRM işlevlerini destekleyen, çoklu mağaza/şube yapısında çalışabilen bir masaüstü uygulamasının arayüz katmanını oluşturacaktır. Arayüz katmanı sadece görsel bileşenler ve navigasyon ile sınırlı olup, iş kuralları içermeyecektir.

## Glossary

- **UI_Katmani**: PyQt6 ile oluşturulan kullanıcı arayüzü katmanı
- **Servis_Fabrikasi**: UI katmanına servis örneklerini sağlayan fabrika sınıfı
- **Ana_Pencere**: Uygulamanın ana penceresi ve navigasyon merkezi
- **Ekran_Modulu**: Belirli bir işlev için tasarlanmış UI bileşeni
- **Stub_Fonksiyon**: Gerçek iş mantığı olmadan sadece servis çağrısı yapan yer tutucu fonksiyon
- **Wireframe**: Arayüz tasarımının iskelet yapısı

## Requirements

### Requirement 1

**User Story:** Sistem yöneticisi olarak, uygulamayı başlatabilmek istiyorum ki kullanıcılar sisteme erişebilsin.

#### Acceptance Criteria

1. WHEN uygulama başlatıldığında THEN UI_Katmani SHALL PyQt6 QApplication örneğini oluşturmalı
2. WHEN tema ayarları yüklendiğinde THEN UI_Katmani SHALL stylesheet yer tutucularını hazırlamalı
3. WHEN ana pencere açıldığında THEN UI_Katmani SHALL arayuzu_baslat fonksiyonu ile pencereyi görüntülemeli
4. WHEN uygulama kapatıldığında THEN UI_Katmani SHALL tüm kaynakları temizlemeli

### Requirement 2

**User Story:** Kullanıcı olarak, ana pencerede farklı modüller arasında gezinebilmek istiyorum ki işlerimi kolayca yapabileyim.

#### Acceptance Criteria

1. WHEN ana pencere açıldığında THEN Ana_Pencere SHALL sol menü ve içerik alanı ile QStackedWidget yapısını göstermeli
2. WHEN menü öğesi tıklandığında THEN Ana_Pencere SHALL ilgili ekranı içerik alanında göstermeli
3. WHEN servis gerektiğinde THEN Ana_Pencere SHALL Servis_Fabrikasi üzerinden servis örneklerini almalı
4. WHEN navigasyon yapıldığında THEN Ana_Pencere SHALL aktif ekranı değiştirmeli ve önceki durumu korumalı

### Requirement 3

**User Story:** Geliştirici olarak, servis bağımlılıklarını merkezi bir yerden yönetebilmek istiyorum ki kod tekrarını önleyebileyim.

#### Acceptance Criteria

1. WHEN servis talep edildiğinde THEN Servis_Fabrikasi SHALL singleton pattern ile servis örneklerini üretmeli
2. WHEN stok servisi istendiğinde THEN Servis_Fabrikasi SHALL stok_servisi metodunu çağırmalı
3. WHEN POS servisi istendiğinde THEN Servis_Fabrikasi SHALL pos_servisi metodunu çağırmalı
4. WHEN CRM servisi istendiğinde THEN Servis_Fabrikasi SHALL crm_servisi metodunu çağırmalı

### Requirement 4

**User Story:** Mağaza müdürü olarak, günlük özet bilgileri görebilmek istiyorum ki işletme durumunu takip edebileyim.

#### Acceptance Criteria

1. WHEN gösterge paneli açıldığında THEN Ekran_Modulu SHALL günlük ciro kartını göstermeli
2. WHEN kritik stok bilgisi görüntülendiğinde THEN Ekran_Modulu SHALL kritik stok sayısını göstermeli
3. WHEN bekleyen sipariş bilgisi görüntülendiğinde THEN Ekran_Modulu SHALL bekleyen sipariş sayısını göstermeli
4. WHEN hızlı erişim butonları tıklandığında THEN Ekran_Modulu SHALL ana pencereye sinyal göndererek ekran değişimi yapmalı

### Requirement 5

**User Story:** Kasiyer olarak, POS satış işlemlerini gerçekleştirebilmek istiyorum ki müşterilere hizmet verebilleyim.

#### Acceptance Criteria

1. WHEN barkod girişi yapıldığında THEN POS_Ekrani SHALL pos_servisi.barkod_ekle metodunu çağırmalı
2. WHEN ödeme işlemi başlatıldığında THEN POS_Ekrani SHALL ödeme türüne göre ilgili pos_servisi metodunu çağırmalı
3. WHEN sepet işlemleri yapıldığında THEN POS_Ekrani SHALL sepet tablosunu güncellemeli
4. WHEN hata oluştuğunda THEN POS_Ekrani SHALL QMessageBox ile kullanıcıya hata mesajını göstermeli

### Requirement 6

**User Story:** Stok sorumlusu olarak, ürün ve stok yönetimi yapabilmek istiyorum ki envanter kontrolünü sağlayabileyim.

#### Acceptance Criteria

1. WHEN ürün arama yapıldığında THEN Urun_Stok_Ekrani SHALL stok_servisi.urun_ara metodunu çağırmalı
2. WHEN yeni ürün ekleme işlemi başlatıldığında THEN Urun_Stok_Ekrani SHALL ürün kartı dialogunu açmalı
3. WHEN stok sayım işlemi yapıldığında THEN Urun_Stok_Ekrani SHALL sayım dialogunu açmalı
4. WHEN stok transfer işlemi yapıldığında THEN Urun_Stok_Ekrani SHALL transfer dialogunu açmalı

### Requirement 7

**User Story:** Müşteri temsilcisi olarak, müşteri bilgilerini yönetebilmek istiyorum ki müşteri ilişkilerini geliştirebilleyim.

#### Acceptance Criteria

1. WHEN müşteri arama yapıldığında THEN Musteri_Ekrani SHALL crm_servisi üzerinden arama yapmalı
2. WHEN yeni müşteri ekleme işlemi başlatıldığında THEN Musteri_Ekrani SHALL müşteri kartı dialogunu açmalı
3. WHEN müşteri detay görüntüleme yapıldığında THEN Musteri_Ekrani SHALL detay dialogunu açmalı
4. WHEN puan işlemi yapıldığında THEN Musteri_Ekrani SHALL puan işlem dialogunu açmalı

### Requirement 8

**User Story:** E-ticaret sorumlusu olarak, çoklu mağaza entegrasyonlarını yönetebilmek istiyorum ki online satışları koordine edebileyim.

#### Acceptance Criteria

1. WHEN mağaza seçimi yapıldığında THEN Eticaret_Ekrani SHALL seçili mağaza için işlemleri aktif hale getirmeli
2. WHEN sipariş çekme işlemi başlatıldığında THEN Eticaret_Ekrani SHALL eticaret_servisi.siparis_cek metodunu çağırmalı
3. WHEN stok gönderme işlemi yapıldığında THEN Eticaret_Ekrani SHALL eticaret_servisi.stok_gonder metodunu çağırmalı
4. WHEN fiyat gönderme işlemi yapıldığında THEN Eticaret_Ekrani SHALL eticaret_servisi.fiyat_gonder metodunu çağırmalı

### Requirement 9

**User Story:** Muhasebe sorumlusu olarak, e-belge işlemlerini takip edebilmek istiyorum ki yasal yükümlülükleri yerine getirebilleyim.

#### Acceptance Criteria

1. WHEN e-belge durumu görüntülendiğinde THEN Ebelge_Ekrani SHALL bekleyen, gönderilen ve hatalı sekmelerini göstermeli
2. WHEN belge gönderme işlemi yapıldığında THEN Ebelge_Ekrani SHALL ebelge_servisi.gonder metodunu çağırmalı
3. WHEN durum sorgulama yapıldığında THEN Ebelge_Ekrani SHALL ebelge_servisi.durum_sorgula metodunu çağırmalı
4. WHEN tekrar deneme işlemi yapıldığında THEN Ebelge_Ekrani SHALL ebelge_servisi.tekrar_dene metodunu çağırmalı

### Requirement 10

**User Story:** Kargo sorumlusu olarak, kargo işlemlerini yönetebilmek istiyorum ki sevkiyat süreçlerini takip edebileyim.

#### Acceptance Criteria

1. WHEN taşıyıcı seçimi yapıldığında THEN Kargo_Ekrani SHALL seçili taşıyıcı için işlemleri aktif hale getirmeli
2. WHEN etiket oluşturma işlemi yapıldığında THEN Kargo_Ekrani SHALL kargo_servisi.etiket_olustur metodunu çağırmalı
3. WHEN durum sorgulama yapıldığında THEN Kargo_Ekrani SHALL kargo_servisi.durum_sorgula metodunu çağırmalı
4. WHEN kargo listesi görüntülendiğinde THEN Kargo_Ekrani SHALL kargo bilgilerini tablo formatında göstermeli

### Requirement 11

**User Story:** İşletme sahibi olarak, detaylı raporlar alabilmek istiyorum ki iş performansını analiz edebileyim.

#### Acceptance Criteria

1. WHEN rapor parametreleri seçildiğinde THEN Rapor_Ekrani SHALL tarih aralığı ve mağaza seçimini kabul etmeli
2. WHEN rapor oluşturma işlemi yapıldığında THEN Rapor_Ekrani SHALL rapor_servisi üzerinden ilgili rapor metodunu çağırmalı
3. WHEN rapor sonuçları görüntülendiğinde THEN Rapor_Ekrani SHALL sonuçları tablo formatında göstermeli
4. WHEN rapor dışa aktarma yapıldığında THEN Rapor_Ekrani SHALL CSV ve PDF formatlarında dışa aktarma seçeneklerini sunmalı

### Requirement 12

**User Story:** Sistem yöneticisi olarak, uygulama ayarlarını yapılandırabilmek istiyorum ki sistem gereksinimlerine göre özelleştirebilleyim.

#### Acceptance Criteria

1. WHEN ayarlar ekranı açıldığında THEN Ayarlar_Ekrani SHALL sol liste ve sağ içerik alanı yapısını göstermeli
2. WHEN ayar kategorisi seçildiğinde THEN Ayarlar_Ekrani SHALL ilgili ayar grubunu sağ panelde göstermeli
3. WHEN ayar değişikliği yapıldığında THEN Ayarlar_Ekrani SHALL değişiklikleri geçici olarak saklayabilmeli
4. WHEN ayarlar kaydedildiğinde THEN Ayarlar_Ekrani SHALL ayar_servisi.kaydet metodunu çağırmalı

### Requirement 13

**User Story:** Geliştirici olarak, UI yardımcı fonksiyonlarını kullanabilmek istiyorum ki kod tekrarını önleyebileyim.

#### Acceptance Criteria

1. WHEN tablo doldurma işlemi yapıldığında THEN UI_Yardimcilari SHALL tablo verilerini formatlamalı
2. WHEN para formatlaması gerektiğinde THEN UI_Yardimcilari SHALL Türk Lirası formatında gösterim yapmalı
3. WHEN tarih formatlaması gerektiğinde THEN UI_Yardimcilari SHALL yerel tarih formatında gösterim yapmalı
4. WHEN hata mesajı gösterildiğinde THEN UI_Yardimcilari SHALL standart hata dialog formatını kullanmalı