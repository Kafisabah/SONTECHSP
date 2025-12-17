# Satış Belgeleri Modülü - Uygulama Planı

- [x] 1. Temel veri modelleri ve enum tanımlarını oluştur


  - SQLAlchemy modelleri için SatisBelgesi, BelgeSatiri, NumaraSayaci sınıflarını yaz
  - BelgeTuru ve BelgeDurumu enum'larını tanımla
  - Veritabanı ilişkilerini ve kısıtlamaları kur
  - _Requirements: 1.1, 1.2, 4.1, 6.2_

- [x] 1.1 Property test yaz - Belge model doğrulama


  - **Property 1: Sipariş oluşturma tutarlılığı**
  - **Validates: Requirements 1.1, 1.2**

- [x] 2. Belge numarası üretim servisini implement et


  - NumaraServisi sınıfını oluştur
  - Mağaza kodu, yıl, ay ve sıra numarasından numara üretim algoritmasını yaz
  - Numara çakışması durumunda retry mekanizmasını implement et
  - NumaraSayaci repository ile entegrasyonu sağla
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 2.1 Property test yaz - Numara benzersizliği


  - **Property 5: Belge numarası benzersizliği**
  - **Validates: Requirements 2.2, 4.1, 4.2**

- [x] 2.2 Property test yaz - Ay değişimi sıfırlama

  - **Property 9: Ay değişimi numara sıfırlama**
  - **Validates: Requirements 4.3**

- [x] 2.3 Property test yaz - Numara çakışması çözümü

  - **Property 10: Numara çakışması çözümü**
  - **Validates: Requirements 4.4**

- [x] 3. Durum akış yönetim servisini implement et




  - DurumAkisServisi sınıfını oluştur
  - Durum geçiş kurallarını tanımla (TASLAK->ONAYLANDI->FATURALANDI, IPTAL)
  - Geçerli/geçersiz durum geçiş kontrollerini implement et
  - Durum geçmiş takibini sağla
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 3.1 Property test yaz - Durum geçiş kontrolü





  - **Property 11: Durum geçiş kontrolü**
  - **Validates: Requirements 5.1, 5.3**

- [x] 3.2 Property test yaz - Geçerli durum geçişi



  - **Property 12: Geçerli durum geçişi**
  - **Validates: Requirements 5.2**


- [x] 3.3 Property test yaz - İptal durumu yönetimi



  - **Property 13: İptal durumu yönetimi**
  - **Validates: Requirements 5.4, 5.5**

- [x] 4. Repository katmanını implement et




  - IBelgeDeposu arayüzünü tanımla
  - BelgeDeposu, BelgeSatirDeposu, NumaraSayacDeposu sınıflarını yaz
  - CRUD işlemlerini transaction içinde gerçekleştir
  - Row-level lock mekanizmasını implement et
  - _Requirements: 6.1, 6.4, 6.5_

- [x] 4.1 Property test yaz - Transaction bütünlüğü




  - **Property 3: Transaction bütünlüğü**
  - **Validates: Requirements 1.4, 1.5**


- [x] 4.2 Property test yaz - Eş zamanlı erişim kontrolü


  - **Property 16: Eş zamanlı erişim kontrolü**
  - **Validates: Requirements 6.5**

- [x] 5. Veri doğrulama servisini implement et



  - DogrulamaServisi sınıfını oluştur
  - Belge ve satır bilgileri doğrulama kurallarını yaz
  - Toplam tutar hesaplama ve doğrulama algoritmasını implement et
  - KDV hesaplama fonksiyonlarını yaz
  - _Requirements: 1.3, 6.2, 6.3_

- [x] 5.1 Property test yaz - Belge satır tutarlılığı


  - **Property 2: Belge satır tutarlılığı**
  - **Validates: Requirements 1.3**

- [x] 5.2 Property test yaz - Veri doğrulama tutarlılığı

  - **Property 14: Veri doğrulama tutarlılığı**
  - **Validates: Requirements 6.2, 6.3**

- [x] 6. Ana belge servisini implement et


  - BelgeServisi sınıfını oluştur
  - Sipariş oluşturma metodunu yaz
  - İrsaliye oluşturma metodunu implement et
  - Fatura oluşturma (sipariş ve POS'tan) metodlarını yaz
  - Belge silme ve güncelleme işlemlerini implement et
  - _Requirements: 1.1, 2.1, 3.1, 3.2, 3.3_

- [x] 6.1 Property test yaz - Durum tabanlı belge oluşturma




  - **Property 4: Durum tabanlı belge oluşturma**
  - **Validates: Requirements 2.1, 2.4**

- [x] 6.2 Property test yaz - Durum güncelleme tutarlılığı


  - **Property 6: Durum güncelleme tutarlılığı**
  - **Validates: Requirements 2.3, 3.4**

- [x] 6.3 Property test yaz - Fatura oluşturma tutarlılığı


  - **Property 7: Fatura oluşturma tutarlılığı**
  - **Validates: Requirements 3.1, 3.2, 3.3**

- [x] 7. Checkpoint - Temel işlevsellik testleri



  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. DTO sınıflarını implement et





  - BelgeDTO, BelgeSatirDTO, BelgeOzetDTO sınıflarını oluştur
  - Model-DTO dönüşüm metodlarını yaz
  - Filtreleme ve sayfalama DTO'larını tanımla
  - _Requirements: 7.1, 7.2, 7.3_

- [x] 8.1 Property test yaz - DTO format tutarlılığı



  - **Property 17: DTO format tutarlılığı**
  - **Validates: Requirements 7.1, 7.2**


- [x] 9. Sorgu servislerini implement et

  - Belge listesi sorgu metodlarını yaz
  - Filtreleme ve sayfalama desteğini implement et
  - Belge geçmiş sorgu metodunu oluştur
  - Durum bazlı sorgu metodlarını yaz
  - _Requirements: 7.3, 7.4_

- [x] 9.1 Property test yaz - Liste sorgu desteği


  - **Property 18: Liste sorgu desteği**
  - **Validates: Requirements 7.3**


- [x] 9.2 Property test yaz - Geçmiş sorgu tutarlılığı

  - **Property 19: Geçmiş sorgu tutarlılığı**
  - **Validates: Requirements 7.4**

- [x] 10. Hata yönetimi ve logging implement et


  - Merkezi hata yönetim sınıfını oluştur
  - Belge işlemleri için özel exception sınıflarını tanımla
  - Hata durumlarında rollback mekanizmasını implement et
  - Logging ve monitoring entegrasyonunu sağla
  - _Requirements: 1.5, 3.5_

- [x] 10.1 Property test yaz - Hata durumu yönetimi


  - **Property 8: Hata durumu yönetimi**
  - **Validates: Requirements 3.5**

- [x] 11. Silme işlemi kontrollerini implement et


  - Belge silme öncesi bağımlılık kontrolü metodunu yaz
  - Cascade silme kurallarını implement et
  - Silme yetki kontrollerini ekle
  - _Requirements: 6.4_

- [x] 11.1 Property test yaz - Silme işlemi kontrolü


  - **Property 15: Silme işlemi kontrolü**
  - **Validates: Requirements 6.4**

- [x] 12. Entegrasyon testleri ve son kontroller


  - Modül bileşenleri arası entegrasyon testlerini yaz
  - POS sistemi ile entegrasyon noktalarını test et
  - Performans testlerini çalıştır
  - _Requirements: Tüm gereksinimler_


- [x] 12.1 Unit testler - Entegrasyon senaryoları

  - Sipariş-İrsaliye-Fatura akış testleri
  - POS entegrasyon testleri
  - Hata durumu entegrasyon testleri



- [x] 13. Final Checkpoint - Tüm testlerin geçmesi

  - Ensure all tests pass, ask the user if questions arise.