# Kargo Entegrasyon Altyapısı - Görev Listesi

- [x] 1. Kargo modülü temel yapısını oluştur


  - Kargo modülü klasör yapısını oluştur
  - __init__.py dosyasını hazırla
  - Temel export'ları tanımla
  - _Gereksinimler: 1.1, 5.1_

- [x] 2. DTO ve sabitler katmanını implement et

  - [x] 2.1 Kargo sabitlerini tanımla


    - Kaynak türleri, etiket durumları, takip durumları sabitlerini oluştur
    - Taşıyıcı kodları sabitlerini tanımla
    - _Gereksinimler: 2.1, 2.2_

  - [x] 2.2 Kargo DTO'larını implement et


    - KargoEtiketOlusturDTO dataclass'ını oluştur
    - KargoEtiketSonucDTO dataclass'ını oluştur
    - KargoDurumDTO dataclass'ını oluştur
    - _Gereksinimler: 1.1, 3.1_

- [x] 3. Taşıyıcı arayüz katmanını oluştur

  - [x] 3.1 Taşıyıcı arayüzünü tanımla


    - TasiyiciArayuzu abstract base class'ını oluştur
    - etiket_olustur ve durum_sorgula metodlarını tanımla
    - _Gereksinimler: 5.1, 5.3_

  - [x] 3.2 Dummy taşıyıcı implementasyonunu yaz


    - DummyTasiyici class'ını implement et
    - Sahte takip numarası üretimi ekle
    - Test amaçlı sahte durum döndürme ekle
    - _Gereksinimler: 5.5_

  - [x] 3.3 Taşıyıcı fabrikasını implement et


    - TasiyiciFabrikasi class'ını oluştur
    - Taşıyıcı koduna göre carrier döndürme mantığını ekle
    - MVP aşaması için DummyTasiyici döndürme
    - _Gereksinimler: 5.2_

- [x] 4. Veritabanı modellerini oluştur

  - [x] 4.1 Kargo SQLAlchemy modellerini yaz


    - kargo_etiketleri tablosu modelini oluştur
    - kargo_takipleri tablosu modelini oluştur
    - Foreign key ilişkilerini tanımla
    - Unique constraint'leri ekle
    - _Gereksinimler: 1.3, 7.2_

  - [x] 4.2 Alembic migration dosyasını oluştur


    - Kargo tabloları için migration script'i yaz
    - Index'leri tanımla (takip_no, durum, kaynak_turu+kaynak_id)
    - Foreign key constraint'leri ekle
    - _Gereksinimler: 8.1, 8.3_

- [x] 5. Repository katmanını implement et


  - [x] 5.1 KargoDeposu class'ını oluştur

    - Temel CRUD metodlarını implement et
    - etiket_kaydi_olustur metodunu yaz
    - etiket_getir ve etiket_durum_guncelle metodlarını ekle
    - _Gereksinimler: 1.4, 6.1_

  - [x] 5.2 Takip ve sorgulama metodlarını ekle


    - takip_kaydi_ekle metodunu implement et
    - bekleyen_etiketleri_al metodunu yaz
    - etiket_kaynaktan_bul metodunu ekle (benzersizlik kontrolü)
    - _Gereksinimler: 3.2, 4.2, 1.3_

- [x] 6. Servis katmanını implement et

  - [x] 6.1 KargoServisi temel metodlarını yaz


    - etiket_olustur metodunu implement et
    - Benzersizlik kontrolü ve doğrulama ekle
    - Carrier seçimi ve etiket oluşturma orchestration'ı
    - _Gereksinimler: 1.1, 1.2, 1.3_

  - [x] 6.2 Retry mekanizmasını implement et


    - bekleyen_etiketleri_isle metodunu yaz
    - Deneme sayısı yönetimi ekle
    - Hata durumu yönetimi implement et
    - _Gereksinimler: 4.1, 4.2, 4.3_

  - [x] 6.3 Durum sorgulama servisini ekle


    - durum_sorgula metodunu implement et
    - Takip geçmişi kaydetme mantığını ekle
    - Carrier hata yönetimi implement et
    - _Gereksinimler: 3.1, 3.3, 3.4_

- [x] 7. Checkpoint - Temel testleri çalıştır


  - Tüm testlerin geçtiğinden emin ol, sorular çıkarsa kullanıcıya sor


- [x] 8. Property-based testleri implement et




  - [x] 8.1 Etiket oluşturma doğrulama property testi


    - **Property 1: Etiket Oluşturma Doğrulama**
    - **Doğrular: Gereksinimler 1.1, 1.2, 1.3, 1.4, 1.5**

  - [x] 8.2 Kaynak türü yönetimi property testi


    - **Property 2: Kaynak Türü Yönetimi**
    - **Doğrular: Gereksinimler 2.1, 2.2, 2.3, 2.4**

  - [x] 8.3 Varsayılan değer atama property testi


    - **Property 3: Varsayılan Değer Atama**
    - **Doğrular: Gereksinimler 2.5**

  - [x] 8.4 Durum sorgulama property testi


    - **Property 4: Durum Sorgulama İşlemleri**
    - **Doğrular: Gereksinimler 3.1, 3.2, 3.5**

  - [x] 8.5 Hata yönetimi property testi

    - **Property 5: Hata Yönetimi**
    - **Doğrular: Gereksinimler 3.3, 3.4**

  - [x] 8.6 Retry mekanizması property testi

    - **Property 6: Retry Mekanizması**
    - **Doğrular: Gereksinimler 4.1, 4.2, 4.3, 4.4, 4.5**

  - [x] 8.7 Taşıyıcı arayüz uyumluluğu property testi

    - **Property 7: Taşıyıcı Arayüz Uyumluluğu**
    - **Doğrular: Gereksinimler 5.1, 5.2, 5.3, 5.4, 5.5**

  - [x] 8.8 Zaman damgası yönetimi property testi

    - **Property 8: Zaman Damgası Yönetimi**
    - **Doğrular: Gereksinimler 6.1, 6.2, 6.3**

  - [x] 8.9 Sorgulama işlemleri property testi

    - **Property 9: Sorgulama İşlemleri**
    - **Doğrular: Gereksinimler 6.4, 6.5**

  - [x] 8.10 Transaction yönetimi property testi

    - **Property 10: Transaction Yönetimi**
    - **Doğrular: Gereksinimler 7.1, 7.2, 7.3, 7.5**

  - [x] 8.11 Eş zamanlı erişim güvenliği property testi

    - **Property 11: Eş Zamanlı Erişim Güvenliği**
    - **Doğrular: Gereksinimler 7.4**

  - [x] 8.12 Performans optimizasyonu property testi

    - **Property 12: Performans Optimizasyonu**
    - **Doğrular: Gereksinimler 8.1, 8.2, 8.3**

  - [x] 8.13 Büyük veri yönetimi property testi

    - **Property 13: Büyük Veri Yönetimi**
    - **Doğrular: Gereksinimler 8.4, 8.5**

- [x] 9. Unit testleri implement et

  - [x] 9.1 Etiket oluşturma unit testleri


    - Geçersiz veri ile etiket oluşturma testleri
    - Benzersizlik kısıtlama testleri
    - _Gereksinimler: 1.3, 2.3_

  - [x] 9.2 Hata senaryoları unit testleri

    - Exception handling testleri
    - Carrier hata simülasyon testleri
    - _Gereksinimler: 3.4, 5.4_

  - [x] 9.3 Edge case unit testleri

    - Boş/null değer testleri
    - Maksimum deneme sayısı testleri
    - _Gereksinimler: 4.4, 2.5_

- [x] 10. Final Checkpoint - Tüm testleri çalıştır



  - Tüm testlerin geçtiğinden emin ol, sorular çıkarsa kullanıcıya sor