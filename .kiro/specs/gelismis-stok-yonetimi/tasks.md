# Gelişmiş Stok Yönetimi Sistemi - Uygulama Planı

## Genel Bakış

Bu uygulama planı, gelişmiş stok yönetimi sisteminin adım adım kodlanması için hazırlanmıştır. Her görev, önceki görevler üzerine inşa edilecek şekilde tasarlanmış olup, hiçbir kod parçası bağımsız kalmayacaktır.

## Görevler

- [x] 1. Proje yapısı ve temel modeller
  - Stok modülü klasör yapısını oluştur (models, repositories, services, dto)
  - SQLAlchemy base model ve veritabanı bağlantı yapılandırması
  - Alembic migration yapılandırması
  - _Requirements: 1.1, 2.1, 3.1_

- [x] 1.1 Ürün ve Barkod modellerini oluştur
  - Urun SQLAlchemy modeli (id, stok_kodu, urun_adi, birim, kdv_orani, kritik_seviye, aktif, timestamps)
  - Barkod SQLAlchemy modeli (id, urun_id, barkod, aktif, olusturma_tarihi)
  - Model ilişkileri ve constraint'leri tanımla
  - _Requirements: 1.1, 1.2, 2.1_

- [x] 1.2 Ürün kayıt tutarlılığı property testi


  - **Property 1: Ürün kayıt tutarlılığı**
  - **Validates: Requirements 1.1, 1.2**


- [x] 1.3 Barkod benzersizliği property testi

  - **Property 5: Barkod benzersizliği ve arama tutarlılığı**
  - **Validates: Requirements 2.1, 2.2**

- [x] 1.4 Stok hareket ve bakiye modellerini oluştur
  - StokHareket SQLAlchemy modeli (id, urun_id, depo_id, hareket_turu, miktar, birim_fiyat, aciklama, referans_no, kullanici_id, hareket_tarihi)
  - StokBakiye SQLAlchemy modeli (id, urun_id, depo_id, toplam_miktar, rezerve_miktar, kullanilabilir_miktar, son_guncelleme)
  - Composite unique constraint ve computed column tanımları
  - _Requirements: 3.1, 3.2, 3.4_


- [x] 1.6 Stok hareket kayıt tutarlılığı property testi

  - **Property 8: Stok hareket kayıt tutarlılığı**
  - **Validates: Requirements 3.1, 3.2, 3.3, 3.5**


- [x] 1.7 Stok tabloları için Alembic migration oluştur

  - Stok tabloları (urunler, urun_barkodlari, stok_bakiyeleri, stok_hareketleri) migration dosyası
  - Index ve constraint tanımları
  - Foreign key ilişkileri
  - _Requirements: 1.1, 2.1, 3.1_


- [x] 2. DTO sınıfları ve hata yönetimi

  - UrunDTO, BarkodDTO, StokHareketDTO, StokRaporDTO sınıfları
  - Hata yönetimi sınıfları (UrunValidationError, BarkodValidationError, NegatifStokError)
  - Veri doğrulama kuralları
  - _Requirements: 1.1, 2.1, 3.1_


- [x] 3. Veri erişim katmanı (Repository)

  - IUrunRepository arayüz tanımı
  - IBarkodRepository arayüz tanımı
  - IStokHareketRepository arayüz tanımı
  - IStokBakiyeRepository arayüz tanımı
  - _Requirements: 1.1, 2.1, 3.1_

- [x] 3.1 Ürün repository implementasyonu


  - UrunRepository sınıfı (ekle, guncelle, sil, id_ile_getir, stok_kodu_ile_getir, ara)
  - Ürün silme koruması (stok hareketi kontrolü)
  - Stok kodu benzersizlik kontrolü
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_


- [x] 3.2 Ürün güncelleme izlenebilirliği property testi

  - **Property 2: Ürün güncelleme izlenebilirliği**
  - **Validates: Requirements 1.3**


- [x] 3.3 Ürün arama tutarlılığı property testi

  - **Property 3: Ürün arama tutarlılığı**
  - **Validates: Requirements 1.4**

- [x] 3.4 Ürün silme koruması property testi

  - **Property 4: Ürün silme koruması**
  - **Validates: Requirements 1.5**


- [x] 3.5 Barkod repository implementasyonu

  - BarkodRepository sınıfı (ekle, sil, barkod_ile_ara, urun_barkodlari_getir)
  - Barkod benzersizlik kontrolü
  - Çoklu barkod desteği ve minimum barkod koruması
  - _Requirements: 2.1, 2.2, 2.3, 2.5_


- [x] 3.6 Çoklu barkod desteği property testi


  - **Property 6: Çoklu barkod desteği ve koruma**
  - **Validates: Requirements 2.3, 2.5**


- [x] 3.7 Barkod hata yönetimi property testi


  - **Property 7: Barkod hata yönetimi**
  - **Validates: Requirements 2.4**


- [x] 3.8 Stok hareket repository implementasyonu

  - StokHareketRepository sınıfı (hareket_ekle, hareket_listesi, kilitle_ve_bakiye_getir)
  - PostgreSQL SELECT FOR UPDATE implementasyonu
  - Transaction yönetimi ve rollback mekanizması
  - _Requirements: 3.1, 3.3, 5.1, 5.2, 5.4_



- [x] 3.9 Eş zamanlı erişim kontrolü property testi

  - **Property 11: Eş zamanlı erişim kontrolü**
  - **Validates: Requirements 5.1, 5.2, 5.5**


- [x] 3.10 Stok bakiye repository implementasyonu

  - StokBakiyeRepository sınıfı (bakiye_getir, bakiye_guncelle, rezervasyon_yap, rezervasyon_iptal)
  - Kullanılabilir stok hesaplama (toplam - rezerve)
  - Atomik bakiye güncelleme işlemleri
  - _Requirements: 3.4, 9.3, 9.4, 9.5_



- [x] 3.11 Transaction tutarlılığı property testi

  - **Property 12: Transaction tutarlılığı ve kilit yönetimi**
  - **Validates: Requirements 5.3, 5.4, 7.1, 7.4**



- [x] 4. Checkpoint - Repository katmanı testleri




  - Ensure all tests pass, ask the user if questions arise.



- [x] 5. İş kuralları katmanı (Service)

  - Temel servis sınıfları ve arayüz tanımları
  - Servis katmanı dependency injection yapılandırması
  - _Requirements: 1.1, 2.1, 3.1_

- [x] 5.1 Ürün servis implementasyonu


  - UrunService sınıfı (urun_ekle, urun_guncelle, urun_sil, urun_ara)
  - Ürün validasyon kuralları (zorunlu alanlar, pozitif değerler)
  - Repository katmanı entegrasyonu
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_


- [x] 5.2 Barkod servis implementasyonu


  - BarkodService sınıfı (barkod_ekle, barkod_sil, barkod_ara, barkod_dogrula)
  - Barkod format validasyonu
  - Çoklu barkod yönetimi
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_



- [x] 5.3 Negatif stok kontrol servisi

  - NegatifStokKontrol sınıfı (kontrol_yap, limit_belirle)
  - Stok seviyesi kuralları (0: uyarı, -1 ile -5: uyarı+izin, <-5: engel)
  - Ürün bazlı ve varsayılan limit yönetimi
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_




- [x] 5.4 Negatif stok kontrol kuralları property testi



  - **Property 10: Negatif stok kontrol kuralları**
  - **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**






- [x] 5.5 Stok hareket servisi


  - StokHareketService sınıfı (stok_girisi, stok_cikisi, hareket_listesi)
  - Hareket türü validasyonu (GIRIS: pozitif, CIKIS: negatif)
  - Negatif stok kontrolü entegrasyonu
  - _Requirements: 3.1, 3.2, 3.3, 3.5, 4.1_


- [x] 5.6 Stok bakiye güncelleme tutarlılığı property testi

  - **Property 9: Stok bakiye güncelleme tutarlılığı**
  - **Validates: Requirements 3.4**



- [x] 6. Stok sayım ve transfer işlemleri

  - StokSayimService sınıfı (sayim_baslat, sayim_tamamla, sayim_iptal)
  - Sayım farkı hesaplama ve SAYIM türü hareket kaydı
  - Sayım iptal koruması
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 6.1 Stok sayım tutarlılığı property testi

  - **Property 13: Stok sayım tutarlılığı**
  - **Validates: Requirements 6.1, 6.2, 6.3, 6.4**


- [x] 6.2 Sayım iptal koruması property testi

  - **Property 14: Sayım iptal koruması**
  - **Validates: Requirements 6.5**



- [x] 6.3 Stok transfer servisi


  - StokTransferService sınıfı (transfer_yap, transfer_iptal)
  - Kaynak depo stok kontrolü
  - Tek transaction içinde çift yönlü hareket kaydı
  - Transfer referans numarası yönetimi
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_


- [x] 6.4 Transfer işlem tutarlılığı property testi

  - **Property 15: Transfer işlem tutarlılığı**
  - **Validates: Requirements 7.1, 7.2, 7.3, 7.5**


- [x] 7. Kritik stok ve rezervasyon yönetimi





  - KritikStokService sınıfı (kritik_stok_listesi, uyari_olustur)
  - Ürün bazlı ve varsayılan kritik seviye yönetimi
  - Depo bazında gruplandırma
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 7.1 Kritik stok yönetimi property testi

  - **Property 16: Kritik stok yönetimi**
  - **Validates: Requirements 8.1, 8.3, 8.4, 8.5**



- [x] 7.2 Kritik stok uyarı sistemi property testi


  - **Property 17: Kritik stok uyarı sistemi**
  - **Validates: Requirements 8.2**




- [x] 7.3 Stok rezervasyon servisi

  - StokRezervasyonService sınıfı (rezervasyon_yap, rezervasyon_iptal, kullanilabilir_stok_getir)
  - E-ticaret entegrasyonu için rezervasyon yönetimi
  - Kullanılabilir stok hesaplama (toplam - rezerve)
  - _Requirements: 9.3, 9.4, 9.5_




- [x] 7.4 Stok rezervasyon yönetimi property testi


  - **Property 19: Stok rezervasyon yönetimi**
  - **Validates: Requirements 9.3, 9.4, 9.5**


- [x] 8. Entegrasyon ve gerçek zamanlı güncellemeler




  - StokEntegrasyonService sınıfı (pos_satisi_isle, eticaret_guncelle)
  - Gerçek zamanlı stok güncelleme mekanizması
  - POS otomatik stok düşümü
  - _Requirements: 9.1, 9.2_

- [x] 8.1 Gerçek zamanlı stok entegrasyonu property testi

  - **Property 18: Gerçek zamanlı stok entegrasyonu**
  - **Validates: Requirements 9.1, 9.2**

- [x] 9. Raporlama servisi

  - StokRaporService sınıfı (hareket_raporu, stok_durum_raporu, csv_export)
  - Tarih aralığı, hareket türü, ürün ve depo bazlı filtreleme
  - CSV export fonksiyonalitesi
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 9.1 Rapor filtreleme tutarlılığı property testi

  - **Property 20: Rapor filtreleme tutarlılığı**
  - **Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5**



- [x] 10. Ana stok yönetim koordinatörü

  - StokYonetimService sınıfı (tum servisleri koordine eden ana servis)
  - Servisler arası entegrasyon ve iş akışı yönetimi
  - Hata yönetimi ve logging entegrasyonu
  - _Requirements: Tüm gereksinimler_

- [x] 10.1 Unit testler

  - Repository katmanı unit testleri
  - Service katmanı unit testleri
  - Hata durumları ve exception handling testleri
  - _Requirements: Tüm gereksinimler_


- [x] 11. Final Checkpoint - Tüm testlerin geçmesi

  - Ensure all tests pass, ask the user if questions arise.