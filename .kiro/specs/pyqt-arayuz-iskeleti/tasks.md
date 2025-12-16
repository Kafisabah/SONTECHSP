# Implementation Plan

- [x] 1. Temel uygulama yapısını oluştur


  - uygulama/arayuz/ klasör yapısını oluştur
  - __init__.py dosyalarını ekle
  - PyQt6 bağımlılıklarını kontrol et
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 1.1 Uygulama başlatma property testini yaz


  - **Property 1: Uygulama başlatma tutarlılığı**
  - **Validates: Requirements 1.1, 1.3**

- [x] 2. Ana uygulama başlatıcısını implement et


  - uygulama/arayuz/uygulama.py dosyasını oluştur
  - QApplication başlatma fonksiyonunu yaz
  - Tema yükleme yer tutucusunu ekle
  - Kaynak temizleme fonksiyonunu implement et
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2.1 Kaynak temizleme property testini yaz


  - **Property 10: Kaynak temizleme tutarlılığı**
  - **Validates: Requirements 1.4**

- [x] 3. Servis fabrikasını oluştur


  - uygulama/arayuz/servis_fabrikasi.py dosyasını oluştur
  - Singleton pattern ile servis üretim metodlarını yaz
  - Tüm servis tiplerini destekleyen fabrika sınıfını implement et
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 3.1 Servis fabrikası singleton property testini yaz


  - **Property 3: Servis fabrikası singleton davranışı**
  - **Validates: Requirements 3.1**

- [x] 3.2 Servis çağrısı property testini yaz

  - **Property 4: Servis çağrısı tutarlılığı**
  - **Validates: Requirements 3.2, 3.3, 3.4**

- [x] 4. Ana pencere ve navigasyon sistemini implement et


  - uygulama/arayuz/ana_pencere.py dosyasını oluştur
  - QMainWindow tabanlı ana pencere sınıfını yaz
  - Sol menü ve QStackedWidget yapısını oluştur
  - Menü öğeleri ve navigasyon mantığını implement et
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 4.1 Navigasyon tutarlılığı property testini yaz


  - **Property 2: Navigasyon tutarlılığı**
  - **Validates: Requirements 2.2, 2.4**

- [x] 4.2 Ekran yapısı property testini yaz

  - **Property 9: Ekran yapısı tutarlılığı**
  - **Validates: Requirements 2.1**

- [x] 5. UI yardımcı fonksiyonlarını oluştur



  - uygulama/arayuz/yardimcilar.py dosyasını oluştur
  - Tablo doldurma yardımcılarını yaz
  - Para ve tarih formatlaması fonksiyonlarını implement et
  - Standart hata dialog fonksiyonunu oluştur
  - _Requirements: 13.1, 13.2, 13.3, 13.4_

- [x] 5.1 Formatlaşma tutarlılığı property testini yaz


  - **Property 8: Formatlaşma tutarlılığı**
  - **Validates: Requirements 13.1, 13.2, 13.3**

- [x] 5.2 Hata gösterim property testini yaz

  - **Property 7: Hata gösterim tutarlılığı**
  - **Validates: Requirements 5.4, 13.4**

- [x] 6. Ekranlar klasörü ve temel ekran sınıfını oluştur


  - uygulama/arayuz/ekranlar/ klasörünü oluştur
  - uygulama/arayuz/ekranlar/__init__.py dosyasını oluştur
  - TemelEkran base sınıfını implement et
  - _Requirements: Tüm ekran gereksinimleri için temel_

- [x] 7. Gösterge paneli ekranını implement et


  - uygulama/arayuz/ekranlar/gosterge_paneli.py dosyasını oluştur
  - Günlük ciro, kritik stok, bekleyen sipariş kartlarını oluştur
  - Hızlı erişim butonlarını implement et
  - Sinyal-slot bağlantılarını kur
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 8. POS satış ekranını implement et


  - uygulama/arayuz/ekranlar/pos_satis.py dosyasını oluştur
  - Barkod girişi ve sepet tablosunu oluştur
  - Ödeme butonları ve stub fonksiyonlarını implement et
  - Hata yakalama ve gösterim mantığını ekle
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 8.1 Tablo güncelleme property testini yaz


  - **Property 6: Tablo güncelleme tutarlılığı**
  - **Validates: Requirements 5.3**


- [x] 9. Ürünler ve stok ekranını implement et

  - uygulama/arayuz/ekranlar/urunler_stok.py dosyasını oluştur
  - Ürün listesi tablosunu ve arama fonksiyonlarını oluştur
  - Dialog açma butonları ve stub fonksiyonlarını implement et
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 9.1 Dialog açma property testini yaz


  - **Property 5: Dialog açma tutarlılığı**
  - **Validates: Requirements 6.2, 6.3, 6.4**

- [x] 10. Müşteriler ekranını implement et



  - uygulama/arayuz/ekranlar/musteriler.py dosyasını oluştur
  - Müşteri listesi ve arama fonksiyonlarını oluştur
  - Müşteri işlem butonları ve stub fonksiyonlarını implement et
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [x] 11. E-ticaret ekranını implement et



  - uygulama/arayuz/ekranlar/eticaret.py dosyasını oluştur
  - Mağaza seçimi ve işlem butonlarını oluştur
  - Sipariş listesi alanını implement et
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 12. E-belge ekranını implement et


  - uygulama/arayuz/ekranlar/ebelge.py dosyasını oluştur
  - Sekmeli yapı (bekleyen/gönderilen/hatalı) oluştur
  - E-belge işlem butonları ve stub fonksiyonlarını implement et
  - _Requirements: 9.1, 9.2, 9.3, 9.4_


- [x] 13. Kargo ekranını implement et

  - uygulama/arayuz/ekranlar/kargo.py dosyasını oluştur
  - Taşıyıcı seçimi ve işlem butonlarını oluştur
  - Kargo listesi tablosunu implement et
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [x] 14. Raporlar ekranını implement et


  - uygulama/arayuz/ekranlar/raporlar.py dosyasını oluştur
  - Parametre seçimi alanlarını oluştur
  - Rapor butonları ve sonuç tablosunu implement et
  - Dışa aktarma seçeneklerini ekle
  - _Requirements: 11.1, 11.2, 11.3, 11.4_

- [x] 15. Ayarlar ekranını implement et


  - uygulama/arayuz/ekranlar/ayarlar.py dosyasını oluştur
  - Sol liste ve sağ içerik alanı yapısını oluştur
  - Ayar kategorileri ve değişiklik yönetimini implement et
  - _Requirements: 12.1, 12.2, 12.3, 12.4_

- [x] 16. Checkpoint - Tüm testlerin çalıştığından emin ol


  - Tüm testlerin geçtiğini kontrol et, kullanıcıya sorular varsa sor

- [x] 17. Unit testleri yaz


  - Ana pencere unit testleri
  - Ekran bileşenleri unit testleri
  - Servis fabrikası unit testleri
  - UI yardımcıları unit testleri

- [x] 18. Entegrasyon ve son kontroller


  - Tüm ekranların ana pencerede doğru çalıştığını kontrol et
  - Navigasyon akışlarını test et
  - Hata senaryolarını kontrol et
  - _Requirements: Tüm gereksinimler_

- [x] 19. Final Checkpoint - Tüm testlerin geçtiğinden emin ol



  - Tüm testlerin geçtiğini kontrol et, kullanıcıya sorular varsa sor