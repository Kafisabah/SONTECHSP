# POS Çekirdek Modülü Uygulama Planı

- [x] 1. Proje yapısı ve temel arayüzleri kurma


  - POS modülü için klasör yapısını oluştur (ui/, services/, repositories/, database/)
  - Temel arayüzleri (interfaces) tanımla
  - Test framework'ünü kur ve yapılandır
  - _Requirements: 1.1, 2.1, 3.1_

- [x] 2. Veri modelleri ve doğrulama implementasyonu


- [x] 2.1 Sepet ve SepetSatiri modellerini oluştur

  - SQLAlchemy modellerini yaz
  - Veri doğrulama fonksiyonlarını implement et
  - _Requirements: 1.1, 1.2, 2.1_

- [x] 2.2 Sepet modeli için özellik testi yaz


  - **Özellik 1: Barkod Doğrulama ve Sepete Ekleme**
  - **Doğrular: Requirements 1.1, 1.2**

- [x] 2.3 Aynı ürün ekleme için özellik testi yaz


  - **Özellik 2: Aynı Ürün Adet Artırma**
  - **Doğrular: Requirements 1.3**

- [x] 2.4 Satis ve SatisOdeme modellerini oluştur


  - Satış kayıtları için SQLAlchemy modelleri
  - Ödeme türleri ve validasyon kuralları
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 2.5 Ödeme işlemleri için özellik testleri yaz


  - **Özellik 9: Tek Ödeme İşlemi**
  - **Özellik 10: Parçalı Ödeme İşlemi**
  - **Doğrular: Requirements 3.1, 3.2**

- [x] 2.6 Iade ve IadeSatiri modellerini oluştur


  - İade işlemleri için veri modelleri
  - İade doğrulama kuralları
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 2.7 İade işlemleri için özellik testleri yaz


  - **Özellik 14: İade İşlemi Başlatma**
  - **Özellik 15: İade Tutarı Hesaplama**
  - **Doğrular: Requirements 4.1, 4.2**


- [x] 2.8 OfflineKuyruk modelini oluştur

  - SQLite tabanlı kuyruk modeli
  - Kuyruk durumları ve hata yönetimi
  - _Requirements: 5.1, 5.2_

- [x] 2.9 Offline kuyruk için özellik testleri yaz






  - **Özellik 18: Offline İşlem Kaydetme**
  - **Özellik 19: Offline Durum Bildirimi**
  - **Doğrular: Requirements 5.1, 5.2**

- [x] 3. Repository katmanını implement et





- [x] 3.1 SepetRepository'yi oluştur



  - CRUD operasyonları
  - Sepet satırı yönetimi
  - _Requirements: 1.1, 1.2, 2.1, 2.2_

- [x] 3.2 SatisRepository'yi oluştur


  - Satış kayıtları yönetimi
  - Transaction desteği
  - _Requirements: 3.1, 3.3, 7.4_

- [x] 3.3 IadeRepository'yi oluştur


  - İade kayıtları yönetimi
  - Orijinal satış doğrulama
  - _Requirements: 4.1, 4.3_

- [x] 3.4 OfflineKuyrukRepository'yi oluştur


  - SQLite kuyruk operasyonları
  - Kuyruk durumu yönetimi
  - _Requirements: 5.1, 5.3, 5.4_

- [x] 3.5 Repository katmanı için birim testler yaz


  - SepetRepository CRUD testleri
  - SatisRepository transaction testleri
  - IadeRepository doğrulama testleri
  - OfflineKuyrukRepository kuyruk testleri
  - _Requirements: 1.1, 3.1, 4.1, 5.1_


- [x] 4. Service katmanını implement et









- [x] 4.1 SepetService'i oluştur


  - Barkod doğrulama ve ürün ekleme
  - Sepet yönetimi işlemleri
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 2.4_

- [x] 4.2 Sepet yönetimi için özellik testleri yaz


  - **Özellik 3: Geçersiz Barkod Hata Yönetimi**
  - **Özellik 5: Sepet Satırı Silme**
  - **Özellik 6: Ürün Adedi Değiştirme**
  - **Özellik 7: İndirim Uygulama**
  - **Özellik 8: Sepet Boşaltma**
  - **Doğrular: Requirements 1.4, 2.1, 2.2, 2.3, 2.4**

- [x] 4.3 OdemeService'i oluştur


  - Tek ve parçalı ödeme işlemleri
  - Ödeme doğrulama ve stok düşümü
  - _Requirements: 3.1, 3.2, 3.3, 3.4_


- [x] 4.4 Ödeme doğrulama için özellik testleri yaz



  - **Özellik 11: Ödeme Tutarı Eşleşmesi**
  - **Özellik 12: Yetersiz Ödeme Kontrolü**
  - **Doğrular: Requirements 3.3, 3.4**

- [x] 4.5 IadeService'i oluştur


  - İade işlemi başlatma ve doğrulama
  - İade tutarı hesaplama ve stok girişi
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 4.6 İade onaylama için özellik testi yaz


  - **Özellik 16: İade Onaylama**
  - **Doğrular: Requirements 4.3**

- [x] 4.7 FisService'i oluştur


  - Fiş formatlaması ve içerik oluşturma
  - Yazdırma hazırlığı
  - _Requirements: 3.5, 6.1, 6.2, 6.3_


- [x] 4.8 Fiş işlemleri için özellik testleri yaz

  - **Özellik 13: Satış Tamamlama ve Fiş Oluşturma**
  - **Özellik 17: İade Fişi Yazdırma**
  - **Özellik 22: Fiş Formatlaması**
  - **Özellik 23: Fiş Yazdırma**
  - **Doğrular: Requirements 3.5, 4.4, 6.1, 6.2, 6.3**

- [x] 4.9 OfflineKuyrukService'i oluştur



  - Network durumu kontrolü
  - Kuyruk yönetimi ve senkronizasyon
  - _Requirements: 5.1, 5.2, 5.3, 5.4_


- [x] 4.10 Offline kuyruk senkronizasyonu için özellik testleri yaz

  - **Özellik 20: Kuyruk Senkronizasyonu**
  - **Özellik 21: Kuyruk Hata Yönetimi**
  - **Doğrular: Requirements 5.3, 5.4**

- [x] 5. Stok yönetimi entegrasyonu







- [x] 5.1 Stok servisi arayüzünü oluştur


  - Stok kontrolü ve kilitleme arayüzü
  - Stok düşümü ve rezervasyon
  - _Requirements: 1.5, 7.1, 7.2, 7.3, 7.4_

- [x] 5.2 Stok kontrolü için özellik testleri yaz







  - **Özellik 4: Stok Yetersizliği Kontrolü**
  - **Özellik 25: Eş Zamanlı Stok Kilitleme**
  - **Özellik 26: Güncel Stok Kontrolü**
  - **Özellik 27: Stok Yetersizliği İptal**
  - **Özellik 28: Transaction Stok Düşümü**
  - **Doğrular: Requirements 1.5, 7.1, 7.2, 7.3, 7.4**

- [x] 6. Hata yönetimi ve logging sistemi









- [x] 6.1 POS hata sınıflarını oluştur




  - BarkodHatasi, StokHatasi, OdemeHatasi sınıfları
  - IadeHatasi, NetworkHatasi, YazdirmaHatasi sınıfları
  - _Requirements: 1.4, 1.5, 3.4, 4.1, 5.1, 6.4_

- [x] 6.2 Hata yönetimi için özellik testi yaz


  - **Özellik 24: Yazdırma Hata Yönetimi**
  - **Doğrular: Requirements 6.4**

- [x] 6.3 Logging ve monitoring sistemi


  - POS işlemleri için detaylı loglama
  - Performans metrikleri
  - _Requirements: Tüm requirements_

- [x] 7. Satış iptal işlemleri








- [x] 7.1 Satış iptal servisini implement et





  - İptal nedeni sorgulama
  - Sepet temizleme ve satış durumu güncelleme
  - _Requirements: 8.1, 8.2_



- [x] 7.2 Satış iptal için özellik testleri yaz



  - **Özellik 29: Satış İptal Süreci**
  - **Özellik 30: Stok Rezervasyon Serbest Bırakma**
  - **Özellik 31: İptal Sonrası Hazır Duruma Geçme**
  - **Doğrular: Requirements 8.1, 8.2, 8.3, 8.4**

- [x] 7.3 Stok rezervasyon yönetimi

  - Rezervasyon serbest bırakma
  - Yeni satış için hazırlık
  - _Requirements: 8.3, 8.4_

- [x] 8. Checkpoint - Tüm testlerin geçtiğinden emin ol






  - Tüm testlerin geçtiğinden emin ol, sorular çıkarsa kullanıcıya sor.

- [x] 9. UI katmanı temel iskeletleri









- [x] 9.1 SepetEkrani PyQt6 arayüzü




  - Sepet görüntüleme ve yönetim ekranı
  - Barkod okuma arayüzü
  - _Requirements: 1.1, 1.2, 2.1, 2.2_

- [x] 9.2 OdemeEkrani PyQt6 arayüzü


  - Ödeme yöntemi seçimi
  - Tutar girişi ve doğrulama
  - _Requirements: 3.1, 3.2, 3.3_

- [x] 9.3 IadeEkrani PyQt6 arayüzü


  - İade işlemi başlatma
  - Kalem seçimi ve tutar hesaplama
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 9.4 UI katmanı için birim testler yaz






  - Ekran yükleme testleri
  - Signal/slot bağlantı testleri
  - Service çağrı testleri
  - _Requirements: 1.1, 3.1, 4.1_

- [x] 10. Entegrasyon ve sistem testleri







- [x] 10.1 End-to-end satış senaryosu testi


  - Barkod okuma -> sepet -> ödeme -> fiş akışı
  - _Requirements: 1.1, 1.2, 3.1, 3.5_

- [x] 10.2 Offline-online geçiş testi






  - Network kesintisi simülasyonu
  - Kuyruk senkronizasyon testi
  - _Requirements: 5.1, 5.3_

- [x] 10.3 Eş zamanlı işlem testi


  - Çoklu terminal stok kilitleme
  - Transaction tutarlılığı
  - _Requirements: 7.1, 7.4_


- [x] 10.4 Sistem entegrasyon testleri yaz



  - Katmanlar arası entegrasyon testleri
  - Database transaction testleri
  - Error recovery testleri
  - _Requirements: Tüm requirements_




- [x] 11. Final Checkpoint - Tüm testlerin geçtiğinden emin ol









  - Tüm testlerin geçtiğinden emin ol, sorular çıkarsa kullanıcıya sor.