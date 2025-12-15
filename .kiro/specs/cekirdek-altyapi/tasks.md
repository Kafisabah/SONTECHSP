# Çekirdek Altyapı Uygulama Planı

- [x] 1. Çekirdek altyapı temel yapısını oluştur


  - sontechsp/uygulama/cekirdek/ klasör yapısını oluştur
  - Gerekli __init__.py dosyalarını ekle
  - Temel import yapılarını hazırla
  - _Gereksinimler: 6.1, 6.2, 6.3_

- [x] 1.1 Çekirdek modül bağımsızlık property testi yaz


  - **Özellik 13: UI katman bağımsızlığı**
  - **Özellik 14: Veritabanı katman bağımsızlığı** 
  - **Özellik 15: Standart kütüphane bağımlılığı**
  - **Doğrular: Gereksinim 6.1, 6.2, 6.3**


- [x] 2. Ayarlar yönetimi modülünü implement et

  - sontechsp/uygulama/cekirdek/ayarlar.py dosyasını oluştur
  - AyarlarYoneticisi sınıfını implement et
  - .env dosya okuma fonksiyonalitesini ekle
  - Ortam değişkeni öncelik mantığını implement et
  - Zorunlu ayar doğrulama sistemini ekle
  - _Gereksinimler: 1.1, 1.2, 1.3, 1.4, 1.5, 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 2.1 Ayar okuma tutarlılığı property testi yaz


  - **Özellik 1: Ayar okuma tutarlılığı**
  - **Doğrular: Gereksinim 1.1, 1.3**

- [x] 2.2 Güvenli yapılandırma yükleme property testi yaz

  - **Özellik 18: Güvenli yapılandırma yükleme**
  - **Doğrular: Gereksinim 7.1**

- [x] 2.3 Yapılandırma doğrulama property testi yaz

  - **Özellik 19: Yapılandırma doğrulama**
  - **Doğrular: Gereksinim 7.2**

- [x] 2.4 Ortam değişkeni önceliği property testi yaz

  - **Özellik 20: Ortam değişkeni önceliği**
  - **Doğrular: Gereksinim 7.3**

- [x] 2.5 Dinamik ayar algılama property testi yaz

  - **Özellik 21: Dinamik ayar algılama**
  - **Doğrular: Gereksinim 7.5**

- [x] 3. Kayıt (logging) sistemi modülünü implement et


  - sontechsp/uygulama/cekirdek/kayit.py dosyasını oluştur
  - KayitSistemi sınıfını implement et
  - Çift çıktı (dosya + konsol) sistemini ekle
  - Log seviye filtreleme mantığını implement et
  - Otomatik dosya döndürme özelliğini ekle
  - Türkçe log mesaj desteğini ekle
  - _Gereksinimler: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 3.1 Log çift yazım garantisi property testi yaz


  - **Özellik 2: Log çift yazım garantisi**
  - **Doğrular: Gereksinim 2.1**


- [x] 3.2 Log seviye filtreleme property testi yaz


  - **Özellik 3: Log seviye filtreleme**
  - **Doğrular: Gereksinim 2.2**


- [x] 3.3 Log ayar uyumluluğu property testi yaz


  - **Özellik 4: Log ayar uyumluluğu**
  - **Doğrular: Gereksinim 2.5**

- [x] 4. Hata yönetimi modülünü implement et


  - sontechsp/uygulama/cekirdek/hatalar.py dosyasını oluştur
  - SontechHatasi temel sınıfını oluştur
  - AlanHatasi, DogrulamaHatasi, EntegrasyonHatasi sınıflarını implement et
  - Hata loglama entegrasyonunu ekle
  - Türkçe hata mesajı sistemini implement et
  - _Gereksinimler: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4.1 Hata loglama tutarlılığı property testi yaz


  - **Özellik 5: Hata loglama tutarlılığı**
  - **Doğrular: Gereksinim 3.4**

- [x] 4.2 Türkçe hata mesajı garantisi property testi yaz


  - **Özellik 6: Türkçe hata mesajı garantisi**
  - **Doğrular: Gereksinim 3.5**

- [x] 5. Yetki kontrol modülünü implement et


  - sontechsp/uygulama/cekirdek/yetki.py dosyasını oluştur
  - YetkiKontrolcu sınıfını implement et
  - izin_var_mi fonksiyonunu implement et
  - Yetki matrisi yükleme sistemini ekle
  - Rol doğrulama fonksiyonalitesini ekle
  - _Gereksinimler: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 5.1 Yetki kontrol tutarlılığı property testi yaz


  - **Özellik 7: Yetki kontrol tutarlılığı**
  - **Doğrular: Gereksinim 4.1, 4.4**

- [x] 6. Oturum yönetimi modülünü implement et



  - sontechsp/uygulama/cekirdek/oturum.py dosyasını oluştur
  - OturumBilgisi dataclass'ını oluştur
  - Oturum başlatma fonksiyonalitesini implement et
  - Bağlam güncelleme sistemini ekle
  - Oturum sonlandırma ve temizlik fonksiyonlarını implement et
  - Çoklu terminal desteğini ekle
  - _Gereksinimler: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 6.1 Oturum bilgi bütünlüğü property testi yaz


  - **Özellik 8: Oturum bilgi bütünlüğü**
  - **Doğrular: Gereksinim 5.1**

- [x] 6.2 Oturum bağlam güncelleme property testi yaz

  - **Özellik 9: Oturum bağlam güncelleme**
  - **Doğrular: Gereksinim 5.2**

- [x] 6.3 Oturum temizlik garantisi property testi yaz

  - **Özellik 10: Oturum temizlik garantisi**
  - **Doğrular: Gereksinim 5.3**

- [x] 6.4 Çoklu terminal desteği property testi yaz

  - **Özellik 11: Çoklu terminal desteği**
  - **Doğrular: Gereksinim 5.4**

- [x] 6.5 Oturum veri korunumu property testi yaz

  - **Özellik 12: Oturum veri korunumu**
  - **Doğrular: Gereksinim 5.5**

- [x] 7. Çekirdek modül entegrasyonunu tamamla


  - Tüm çekirdek modüllerin birbirleriyle entegrasyonunu sağla
  - Merkezi başlatma fonksiyonunu oluştur
  - Yapılandırma yükleme sırasını belirle
  - Hata yönetimi zincirini kur
  - _Gereksinimler: 6.4, 6.5_

- [x] 7.1 Çalışma zamanı bağımsızlığı property testi yaz


  - **Özellik 16: Çalışma zamanı bağımsızlığı**
  - **Doğrular: Gereksinim 6.4**


- [ ] 7.2 İzole test edilebilirlik property testi yaz
  - **Özellik 17: İzole test edilebilirlik**

  - **Doğrular: Gereksinim 6.5**

- [x] 8. Checkpoint - Tüm testlerin geçtiğinden emin ol

  - Tüm testlerin geçtiğinden emin ol, sorular çıkarsa kullanıcıya sor.


- [x] 9. Örnek yapılandırma dosyalarını oluştur

  - .env.example dosyasını oluştur
  - Zorunlu ayarları ve açıklamalarını ekle
  - Geliştirme ve üretim ortamı örneklerini hazırla
  - _Gereksinimler: 1.5, 7.4_


- [x] 10. Dokümantasyon ve kullanım örneklerini hazırla

  - Her modül için kullanım örnekleri yaz
  - API dokümantasyonunu oluştur
  - Yapılandırma rehberini hazırla
  - Hata ayıklama rehberini oluştur
  - _Gereksinimler: 7.4_

- [x] 11. Final Checkpoint - Tüm testlerin geçtiğinden emin ol



  - Tüm testlerin geçtiğinden emin ol, sorular çıkarsa kullanıcıya sor.