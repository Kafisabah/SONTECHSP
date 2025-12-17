# E-Belge Yönetim Altyapısı Uygulama Planı

- [x] 1. Temel yapı ve DTO sınıflarını oluştur


  - E-belge modülü klasör yapısını oluştur
  - DTO sınıflarını implement et (EBelgeOlusturDTO, EBelgeGonderDTO, EBelgeSonucDTO, EBelgeDurumSorguDTO)
  - Sabitler ve enum değerlerini tanımla (BelgeTuru, KaynakTuru, OutboxDurumu)
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 1.1 DTO validation property testlerini yaz


  - **Property 1: E-belge oluşturma validation**
  - **Validates: Requirements 1.1, 1.2, 1.3**

- [x] 1.2 Varsayılan değer property testini yaz


  - **Property 3: Varsayılan değer atama**
  - **Validates: Requirements 1.5**

- [x] 2. Veritabanı modelleri ve migration oluştur


  - ebelge_cikis_kuyrugu tablosu modelini oluştur
  - ebelge_durumlari audit tablosu modelini oluştur
  - UNIQUE constraint (kaynak_turu, kaynak_id, belge_turu) ekle
  - Alembic migration dosyasını oluştur
  - _Requirements: 2.1, 2.2, 7.1, 7.2_

- [x] 2.1 Idempotency property testlerini yaz


  - **Property 4: Idempotency kontrolü**
  - **Validates: Requirements 2.1, 2.3**

- [x] 2.2 Farklı belge türü property testini yaz


  - **Property 5: Farklı belge türü desteği**
  - **Validates: Requirements 2.2**

- [x] 3. Repository katmanını implement et


  - EBelgeDeposu sınıfını oluştur
  - CRUD operasyonlarını implement et (cikis_kaydi_olustur, cikis_kaydi_getir, bekleyenleri_getir)
  - Durum güncelleme metotlarını implement et (durum_guncelle, deneme_arttir)
  - Audit logging metotlarını implement et (tarihce_ekle)
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 5.1, 5.2, 5.3, 7.1, 7.2_

- [x] 3.1 Repository filtreleme property testlerini yaz


  - **Property 6: Bekleyen belge filtreleme**
  - **Validates: Requirements 3.1, 3.2**

- [x] 3.2 Sayfalama property testini yaz

  - **Property 8: Sayfalama kontrolü**
  - **Validates: Requirements 3.4**

- [x] 3.3 Transaction property testlerini yaz

  - **Property 18: Transaction yönetimi**
  - **Validates: Requirements 11.1, 11.2, 11.4**

- [x] 4. Sağlayıcı arayüzü ve fabrikasını oluştur


  - SaglayiciArayuzu abstract base class oluştur
  - SaglayiciFabrikasi sınıfını implement et
  - DummySaglayici test implementasyonunu oluştur
  - Konfigürasyon yönetimini ekle
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 8.1, 8.2, 8.5, 9.1, 9.2, 9.3_

- [x] 4.1 Sağlayıcı interface property testlerini yaz

  - **Property 9: Sağlayıcı interface uyumluluğu**
  - **Validates: Requirements 4.1, 4.2, 4.3**

- [x] 4.2 Sağlayıcı fabrikası property testini yaz

  - **Property 16: Sağlayıcı fabrikası**
  - **Validates: Requirements 8.1, 8.2, 8.5**

- [x] 4.3 DummySaglayici property testlerini yaz

  - **Property 17: DummySaglayici davranışı**
  - **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**

- [x] 5. Ana servis katmanını implement et


  - EBelgeServisi sınıfını oluştur
  - cikis_olustur metodunu implement et (validation + idempotency kontrolü)
  - bekleyenleri_gonder metodunu implement et (batch processing)
  - durum_sorgula metodunu implement et
  - Hata yönetimi ve logging ekle
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 3.1, 3.2, 5.1, 5.2, 5.3, 6.1, 6.2, 6.3_

- [x] 5.1 JSON bütünlüğü property testini yaz

  - **Property 2: JSON veri bütünlüğü (Round-trip)**
  - **Validates: Requirements 1.4, 14.1, 14.2**

- [x] 5.2 Durum güncelleme property testlerini yaz

  - **Property 7: Durum güncelleme atomikliği**
  - **Validates: Requirements 3.3, 5.1, 5.3**

- [x] 5.3 Dış belge numarası property testini yaz

  - **Property 10: Dış belge numarası iletimi**
  - **Validates: Requirements 4.4, 5.2**

- [x] 5.4 Durum sorgulama property testini yaz

  - **Property 13: Durum sorgulama**
  - **Validates: Requirements 6.1, 6.2, 6.3**

- [x] 6. Retry mekanizmasını implement et

  - Otomatik retry logic ekle
  - Exponential backoff stratejisi implement et
  - Maksimum deneme sayısı kontrolü ekle
  - Kalıcı hata durumu yönetimi ekle
  - _Requirements: 5.3, 5.4, 10.1, 10.2, 10.3, 10.5_

- [x] 6.1 Retry mekanizması property testlerini yaz

  - **Property 11: Retry mekanizması**
  - **Validates: Requirements 5.4, 10.1, 10.2, 10.3**

- [x] 7. Audit logging sistemini tamamla

  - Durum değişikliği tracking implement et
  - Otomatik zaman damgası ekleme
  - Hata mesajı kaydetme logic
  - Durum geçmişi sorgulama metotları
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 7.1 Audit logging property testlerini yaz

  - **Property 14: Audit logging**
  - **Validates: Requirements 7.1, 7.2**

- [x] 7.2 Hata mesajı property testini yaz

  - **Property 12: Hata mesajı yönetimi**
  - **Validates: Requirements 5.5, 7.3**

- [x] 7.3 Durum geçmişi property testini yaz

  - **Property 15: Durum geçmişi sıralama**
  - **Validates: Requirements 7.4**

- [x] 8. Hata yönetimi ve validation sistemini ekle

  - EntegrasyonHatasi, BaglantiHatasi, DogrulamaHatasi exception sınıfları
  - JSON validation logic
  - Encoding sorunları önleme
  - Comprehensive error handling
  - _Requirements: 2.1, 2.3, 6.4, 6.5, 14.4, 14.5, 15.3, 15.4, 15.5_

- [x] 8.1 JSON validation property testlerini yaz

  - **Property 20: JSON validation**
  - **Validates: Requirements 14.4, 14.5**

- [x] 9. Logging ve monitoring sistemini implement et

  - Structured logging ekle
  - İşlem başlangıç/bitiş logları
  - Hata detay logları
  - Performance metrikleri
  - Audit log seviyesi kayıtlar
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_

- [x] 9.1 Logging property testlerini yaz

  - **Property 19: Logging davranışı**
  - **Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5**

- [x] 10. Durum sorgulama interface tamamla

  - Entegratör durum sorgulama metotları
  - Dış belge numarası ile sorgulama
  - Hata durumu yönetimi (belge bulunamadı, rate limit, bağlantı hatası)
  - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_

- [x] 10.1 Durum sorgulama interface property testini yaz

  - **Property 21: Durum sorgulama interface**
  - **Validates: Requirements 15.1, 15.2**

- [x] 11. Modül entegrasyonu ve paket yapısı

  - __init__.py dosyalarını oluştur ve export'ları tanımla
  - Modül bağımlılıklarını organize et
  - Import yapısını temizle
  - Katman bağımlılık kurallarını kontrol et
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 11.1 Unit testleri yaz

  - DTO sınıfları için unit testler
  - Repository metotları için unit testler
  - Servis metotları için unit testler
  - Hata durumları için unit testler

- [x] 12. Checkpoint - Tüm testlerin geçtiğinden emin ol


  - Tüm testlerin geçtiğinden emin ol, sorular çıkarsa kullanıcıya sor.