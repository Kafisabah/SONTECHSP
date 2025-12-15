# Veritabanı Migration Tamamlama Uygulama Planı

- [x] 1. Eksik modelleri tamamla ve düzenle


  - Firma ve mağaza modellerini kontrol et ve eksiklikleri tamamla
  - Terminal modeli oluştur
  - Model ilişkilerini doğrula
  - __init__.py dosyasını güncelle
  - _Gereksinimler: 2.3, 2.4, 2.5, 3.1, 3.2, 3.3_

- [x] 1.1 Tablo isimlendirme standardı property testi yaz


  - **Property 4: Tablo İsimlendirme Standardı**
  - **Validates: Requirements 3.1, 3.2**

- [x] 1.2 Foreign key bütünlüğü property testi yaz

  - **Property 5: Foreign Key Bütünlüğü**
  - **Validates: Requirements 3.3**

- [x] 1.3 Unique constraint korunumu property testi yaz

  - **Property 6: Unique Constraint Korunumu**
  - **Validates: Requirements 3.4**

- [x] 2. Bağlantı test fonksiyonlarını geliştir


  - baglanti_yardimci.py dosyasını güncelle
  - PostgreSQL bağlantı test fonksiyonu ekle
  - SQLite bağlantı test fonksiyonu ekle
  - Hata yönetimi ve loglama ekle
  - _Gereksinimler: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2.1 Bağlantı test tutarlılığı property testi yaz


  - **Property 1: Bağlantı Test Tutarlılığı**
  - **Validates: Requirements 1.1, 1.3**

- [x] 2.2 SQLite bağlantı güvenilirliği property testi yaz

  - **Property 2: SQLite Bağlantı Güvenilirliği**
  - **Validates: Requirements 1.4**

- [x] 2.3 Bağlantı test loglama property testi yaz

  - **Property 3: Bağlantı Test Loglama**
  - **Validates: Requirements 1.5**

- [x] 3. Session yönetimini iyileştir


  - Session factory yapılandırmasını kontrol et
  - Context manager exception handling'i güçlendir
  - Session commit/rollback davranışını optimize et
  - Kaynak temizliği mekanizmasını geliştir
  - _Gereksinimler: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 3.1 Session commit davranışı property testi yaz


  - **Property 7: Session Commit Davranışı**
  - **Validates: Requirements 4.2**


- [x] 3.2 Session rollback davranışı property testi yaz
  - **Property 8: Session Rollback Davranışı**
  - **Validates: Requirements 4.3**


- [x] 3.3 Session kaynak temizliği property testi yaz
  - **Property 9: Session Kaynak Temizliği**

  - **Validates: Requirements 4.4**


- [x] 3.4 Context manager exception handling property testi yaz
  - **Property 10: Context Manager Exception Handling**
  - **Validates: Requirements 4.5**

- [x] 4. İlk migration dosyasını oluştur

  - Alembic ile ilk migration dosyasını generate et
  - Temel tabloları (kullanicilar, roller, firmalar, magazalar, terminaller) içerecek şekilde düzenle
  - Upgrade ve downgrade fonksiyonlarını implement et
  - Migration dosyasını test et
  - _Gereksinimler: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 4.1 Migration upgrade/downgrade unit testleri yaz


  - İlk migration upgrade testini yaz
  - Migration downgrade testini yaz
  - Tablo oluşturma doğrulaması testlerini yaz
  - _Gereksinimler: 2.1, 2.2, 2.3, 2.4, 2.5, 5.1, 5.2_

- [x] 5. Migration yönetim fonksiyonlarını ekle


  - Migration durum sorgulama fonksiyonu ekle
  - Migration geçmiş listeleme fonksiyonu ekle
  - Migration çakışma kontrolü ekle
  - Migration yardımcı sınıfı oluştur
  - _Gereksinimler: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 5.1 Migration durum sorgusu property testi yaz


  - **Property 11: Migration Durum Sorgusu**
  - **Validates: Requirements 5.3**

- [x] 5.2 Migration geçmiş listesi property testi yaz

  - **Property 12: Migration Geçmiş Listesi**
  - **Validates: Requirements 5.4**

- [x] 6. Temel veri yükleme sistemini oluştur


  - VeriYukleyici sınıfını oluştur
  - Admin kullanıcı oluşturma fonksiyonu ekle
  - Sistem rolleri oluşturma fonksiyonu ekle
  - Sistem yetkileri oluşturma fonksiyonu ekle
  - Varsayılan firma ve mağaza oluşturma fonksiyonu ekle
  - _Gereksinimler: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 6.1 Temel veri tutarlılığı property testi yaz


  - **Property 13: Temel Veri Tutarlılığı**
  - **Validates: Requirements 6.5**

- [x] 6.2 Temel veri yükleme unit testleri yaz

  - Admin kullanıcı oluşturma testini yaz
  - Sistem rolleri oluşturma testini yaz
  - Sistem yetkileri oluşturma testini yaz
  - Varsayılan firma/mağaza oluşturma testini yaz
  - _Gereksinimler: 6.1, 6.2, 6.3, 6.4_

- [x] 7. Checkpoint - Tüm testlerin geçtiğinden emin ol


  - Tüm testlerin geçtiğinden emin ol, sorular çıkarsa kullanıcıya sor.

- [x] 8. Hata yönetimi ve loglama entegrasyonu

  - Özel hata sınıfları oluştur (BaglantiHatasi, MigrationHatasi, VeriYuklemeHatasi)
  - Hata loglama entegrasyonunu ekle
  - Türkçe hata mesajları tanımla
  - Hata kodları standardını oluştur
  - _Gereksinimler: 1.2, 5.5_

- [x] 9. Dokümantasyon ve kullanım örnekleri


  - Migration kullanım rehberi oluştur
  - Bağlantı test örnekleri hazırla
  - Temel veri yükleme rehberi yaz
  - Hata ayıklama rehberi oluştur
  - _Gereksinimler: Tüm gereksinimler_

- [x] 10. Final Checkpoint - Tüm testlerin geçtiğinden emin ol



  - Tüm testlerin geçtiğinden emin ol, sorular çıkarsa kullanıcıya sor.