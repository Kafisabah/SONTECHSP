# CRM Çekirdek Modülü Uygulama Planı

- [x] 1. Proje yapısı ve temel bileşenleri oluştur





  - CRM modül klasör yapısını oluştur
  - Temel __init__.py dosyalarını hazırla
  - Sabitler ve enum değerlerini tanımla
  - _Requirements: 1.1, 4.2, 5.4, 10.1_

- [x] 2. Veri transfer objelerini (DTO) implement et





  - MusteriOlusturDTO sınıfını oluştur
  - MusteriGuncelleDTO sınıfını oluştur
  - PuanIslemDTO sınıfını oluştur
  - MusteriAraDTO sınıfını oluştur
  - _Requirements: 1.1, 2.1, 4.1, 3.1_

- [x] 3. Veritabanı modellerini oluştur





  - Musteriler SQLAlchemy modelini implement et
  - Sadakat_puanlari SQLAlchemy modelini implement et
  - Model ilişkilerini ve constraint'leri tanımla
  - _Requirements: 1.1, 1.2, 1.3, 4.1_

- [x] 4. Alembic migration dosyasını oluştur




  - CRM tabloları için migration script'i yaz
  - Foreign key constraint'lerini ekle
  - İndeksleri tanımla
  - _Requirements: 1.2, 1.3, 4.3_

- [x] 5. Repository katmanını implement et







- [x] 5.1 MusteriDeposu sınıfını oluştur


  - musteri_olustur metodunu implement et
  - musteri_guncelle metodunu implement et
  - musteri_getir metodunu implement et
  - musteri_ara metodunu implement et
  - _Requirements: 1.1, 2.1, 3.1, 3.2, 3.3_

- [x] 5.2 Property test: Müşteri alan zorunluluğu


  - **Property 1: Müşteri alan zorunluluğu**
  - **Validates: Requirements 1.1**

- [x] 5.3 Property test: Telefon benzersizliği


  - **Property 2: Telefon benzersizliği**
  - **Validates: Requirements 1.2, 2.2**

- [x] 5.4 Property test: E-posta geçerliliği ve benzersizliği


  - **Property 3: E-posta geçerliliği ve benzersizliği**
  - **Validates: Requirements 1.3, 2.3**

- [x] 5.5 SadakatDeposu sınıfını oluştur


  - puan_kaydi_ekle metodunu implement et
  - puan_bakiyesi_getir metodunu implement et
  - puan_hareketleri_listele metodunu implement et
  - _Requirements: 4.1, 6.1, 7.1_

- [x] 5.6 Property test: Varsayılan aktif durum




  - **Property 4: Varsayılan aktif durum**
  - **Validates: Requirements 1.4**

- [x] 5.7 Property test: Otomatik zaman damgası


  - **Property 5: Otomatik zaman damgası**
  - **Validates: Requirements 1.5, 2.4, 4.5**


- [x] 6. Servis katmanını implement et






- [x] 6.1 MusteriServisi sınıfını oluştur


  - musteri_olustur metodunu implement et
  - musteri_guncelle metodunu implement et
  - musteri_getir metodunu implement et
  - musteri_ara metodunu implement et
  - Validation ve hata yönetimi ekle
  - _Requirements: 1.1, 2.1, 2.5, 3.1_


- [x] 6.2 Property test: Kısmi güncelleme

  - **Property 6: Kısmi güncelleme**
  - **Validates: Requirements 2.1**

- [x] 6.3 Property test: Geçersiz ID hata yönetimi


  - **Property 7: Geçersiz ID hata yönetimi**
  - **Validates: Requirements 2.5**

- [x] 6.4 Property test: Ad/soyad kısmi arama


  - **Property 8: Ad/soyad kısmi arama**
  - **Validates: Requirements 3.1**

- [x] 6.5 Property test: Telefon/e-posta tam arama


  - **Property 9: Telefon/e-posta tam arama**
  - **Validates: Requirements 3.2, 3.3**

- [x] 6.6 Property test: Çoklu kriter AND mantığı


  - **Property 10: Çoklu kriter AND mantığı**
  - **Validates: Requirements 3.4**

- [x] 6.7 SadakatServisi sınıfını oluştur


  - puan_kazan metodunu implement et
  - puan_harca metodunu implement et
  - bakiye_getir metodunu implement et
  - hareketler metodunu implement et
  - Transaction yönetimi ekle
  - _Requirements: 4.1, 5.1, 5.2, 6.1, 7.1_

- [x] 6.8 Property test: Pozitif puan kontrolü



  - **Property 11: Pozitif puan kontrolü**
  - **Validates: Requirements 4.1**

- [x] 6.9 Property test: İşlem türü otomatik atama


  - **Property 12: İşlem türü otomatik atama**
  - **Validates: Requirements 4.2, 5.4, 10.1**

- [x] 6.10 Property test: Referans bilgisi saklama


  - **Property 13: Referans bilgisi saklama**
  - **Validates: Requirements 4.3, 8.4, 9.3**

- [x] 6.11 Property test: Bakiye kontrolü


  - **Property 14: Bakiye kontrolü**
  - **Validates: Requirements 5.1, 5.2**

- [x] 6.12 Property test: Başarılı harcama kaydı




  - **Property 15: Başarılı harcama kaydı**
  - **Validates: Requirements 5.3**

- [x] 6.13 Property test: Bakiye hesaplama formülü


  - **Property 16: Bakiye hesaplama formülü**
  - **Validates: Requirements 6.1, 6.4**

- [x] 6.14 Property test: Hareket listesi sıralama


  - **Property 17: Hareket listesi sıralama**
  - **Validates: Requirements 7.1**

- [x] 6.15 Property test: Limit parametresi


  - **Property 18: Limit parametresi**
  - **Validates: Requirements 7.2, 7.3**

- [x] 7. Checkpoint - Temel CRM işlevselliği testi


  - Tüm testlerin geçtiğinden emin ol, kullanıcıya sor

- [-] 8. Entegrasyon hook'larını implement et

- [x] 8.1 EntegrasyonKancasi arayüzlerini oluştur


  - pos_satis_tamamlandi fonksiyonunu tanımla
  - satis_belgesi_olustu fonksiyonunu tanımla
  - Puan hesaplama mantığını implement et
  - Hata yönetimi ve loglama ekle
  - _Requirements: 8.1, 8.2, 9.1, 9.2_

- [x] 8.2 Property test: Puan hesaplama kuralı



  - **Property 19: Puan hesaplama kuralı**
  - **Validates: Requirements 8.2, 9.2**

- [x] 8.3 Property test: Entegrasyon hata yönetimi
  - **Property 20: Entegrasyon hata yönetimi**
  - **Validates: Requirements 8.3, 9.4**

- [x] 8.4 Property test: Entegrasyon başarısızlık yönetimi
  - **Property 21: Entegrasyon başarısızlık yönetimi**
  - **Validates: Requirements 8.5**

- [x] 9. Puan düzeltme işlevselliğini implement et





- [x] 9.1 SadakatServisi'ne puan düzeltme metodları ekle


  - puan_duzelt metodunu implement et
  - Pozitif/negatif düzeltme kontrollerini ekle
  - Açıklama zorunluluğu kontrolü ekle
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [x] 9.2 Property test: Düzeltme bakiye kontrolü


  - **Property 22: Düzeltme bakiye kontrolü**
  - **Validates: Requirements 10.2, 10.3**

- [x] 9.3 Property test: Düzeltme açıklama zorunluluğu


  - **Property 23: Düzeltme açıklama zorunluluğu**
  - **Validates: Requirements 10.4**

- [x] 10. Modül export'larını tamamla





  - __init__.py dosyalarında tüm public API'leri export et
  - Modül dokümantasyonunu ekle
  - Sürüm bilgilerini güncelle
  - _Requirements: 12.1, 12.2_

- [x] 11. Unit testler


  - Müşteri CRUD işlemleri için unit testler
  - Puan işlemleri için unit testler
  - Entegrasyon hook'ları için unit testler
  - Edge case'ler için unit testler
  - _Requirements: Tüm gereksinimler_

- [x] 12. Final Checkpoint - Tüm testlerin geçmesi



  - Tüm testlerin geçtiğinden emin ol, kullanıcıya sor