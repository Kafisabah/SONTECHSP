# Test Performans Optimizasyonu - Görev Listesi

- [x] 1. Test konfigürasyon sistemini kur


  - pyproject.toml dosyasında test marker'larını tanımla
  - Hypothesis ayarlarını optimize et (max_examples=50, deadline=2000ms)
  - pytest-xdist bağımlılığını ekle
  - Test kategorileri için marker tanımları oluştur
  - _Gereksinimler: 2.1, 2.3, 3.1, 3.2, 5.1_

- [x] 1.1 Test konfigürasyon doğrulaması için property test yaz


  - **Özellik 5: Marker Konfigürasyonu**
  - **Doğrular: Gereksinimler 2.1, 2.3**

- [x] 1.2 Hypothesis ayarları için property test yaz


  - **Özellik 7: Hypothesis Optimizasyonu**
  - **Doğrular: Gereksinimler 3.1, 3.2**

- [x] 2. Test marker sistemini uygula


  - Mevcut testleri kategorize et (unit, integration, property, slow)
  - Kritik testleri "critical" marker ile işaretle
  - Yavaş testleri "slow" marker ile işaretle
  - Test dosyalarına uygun marker'ları ekle
  - _Gereksinimler: 1.3, 2.1, 2.2_

- [x] 2.1 Marker tabanlı test seçimi için property test yaz


  - **Özellik 2: Marker Tabanlı Test Seçimi**
  - **Doğrular: Gereksinimler 1.3, 2.2**

- [x] 2.2 Varsayılan test davranışı için property test yaz


  - **Özellik 3: Varsayılan Test Davranışı**
  - **Doğrular: Gereksinimler 1.5**

- [x] 3. Test seçici ve önceliklendirme sistemi oluştur


  - TestSelector sınıfını implement et
  - Kritik dosyalar için önceliklendirme algoritması yaz
  - Parametrize testler için sampling stratejisi uygula
  - Fast/slow test ayrımı için algoritma geliştir
  - _Gereksinimler: 4.1, 4.2, 4.3, 4.4_

- [x] 3.1 Test önceliklendirme için property test yaz


  - **Özellik 9: Test Önceliklendirme**
  - **Doğrular: Gereksinimler 4.1**

- [x] 3.2 Sampling stratejisi için property test yaz

  - **Özellik 11: Sampling Stratejisi**
  - **Doğrular: Gereksinimler 4.3**

- [x] 3.3 Kapsama korunması için property test yaz

  - **Özellik 10: Kapsama Korunması**
  - **Doğrular: Gereksinimler 4.2, 4.4**

- [x] 4. Paralel test yöneticisi uygula


  - ParallelTestManager sınıfını oluştur
  - CPU çekirdek sayısına göre worker sayısı hesaplama
  - Test izolasyonu için konfigürasyon ayarları
  - Coverage raporu birleştirme mekanizması
  - _Gereksinimler: 5.1, 5.2, 5.3, 5.4_

- [x] 4.1 Paralel test konfigürasyonu için property test yaz


  - **Özellik 12: Paralel Test Konfigürasyonu**
  - **Doğrular: Gereksinimler 5.1, 5.2**

- [x] 4.2 Test izolasyonu için property test yaz

  - **Özellik 13: Test İzolasyonu**
  - **Doğrular: Gereksinimler 5.3, 5.4**

- [x] 5. CI/CD test seçimi sistemi kur


  - CI/CD için kritik test listesi oluştur
  - GitHub Actions/CI için test konfigürasyonu
  - Hızlı feedback döngüsü için test seçimi
  - Smoke test kategorisi tanımla
  - _Gereksinimler: 1.4_

- [x] 5.1 CI/CD test seçimi için property test yaz


  - **Özellik 4: CI/CD Test Seçimi**
  - **Doğrular: Gereksinimler 1.4**

- [x] 6. Test raporu ve metrikleri sistemi oluştur


  - PerformanceMetrics sınıfını implement et
  - Kategori bazlı test raporu oluşturma
  - Test süresi ölçümü ve raporlama
  - Coverage raporu kategori bazlı gösterim
  - _Gereksinimler: 2.4_

- [x] 6.1 Test raporu kategorileri için property test yaz


  - **Özellik 6: Test Raporu Kategorileri**
  - **Doğrular: Gereksinimler 2.4**

- [x] 7. Hypothesis profil optimizasyonu uygula

  - Hızlı profil konfigürasyonu oluştur
  - Gereksiz health check'leri devre dışı bırak
  - Property testler için timeout ayarları
  - Hypothesis settings profili tanımla
  - _Gereksinimler: 3.3, 3.4_

- [x] 7.1 Hypothesis profil ayarları için property test yaz

  - **Özellik 8: Hypothesis Profil Ayarları**
  - **Doğrular: Gereksinimler 3.3, 3.4**

- [x] 8. Mevcut testleri optimize et

  - Parametrize testlerin sayısını azalt
  - Yavaş testleri belirle ve işaretle
  - Import hatalarını düzelt
  - Test dosyalarını yeniden organize et
  - _Gereksinimler: 4.2, 4.4_

- [x] 9. Test komutları ve kısayolları oluştur


  - Hızlı testler için pytest komutu (pytest -m "not slow")
  - Yavaş testler için pytest komutu (pytest -m slow)
  - CI testleri için pytest komutu (pytest -m critical)
  - Paralel test çalıştırma komutu (pytest -n auto)
  - _Gereksinimler: 1.2, 1.3, 1.4, 1.5_

- [x] 10. Checkpoint - Tüm testlerin geçtiğinden emin ol


  - Tüm testlerin geçtiğinden emin ol, sorular çıkarsa kullanıcıya sor.

- [x] 10.1 Test süresi sınırları için property test yaz

  - **Özellik 1: Test Süresi Sınırları**
  - **Doğrular: Gereksinimler 1.1, 1.2**

- [x] 11. Dokümantasyon ve kullanım kılavuzu oluştur

  - Test kategorileri için README güncellemesi
  - Geliştirici için test çalıştırma kılavuzu
  - CI/CD konfigürasyon dokümantasyonu
  - Performans metrikleri açıklaması
  - _Gereksinimler: Tüm gereksinimler_

- [x] 12. Final checkpoint - Performans hedeflerini doğrula



  - Tüm testlerin geçtiğinden emin ol, sorular çıkarsa kullanıcıya sor.