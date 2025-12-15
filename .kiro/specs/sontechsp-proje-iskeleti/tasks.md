# Uygulama Planı

- [x] 1. SONTECHSP temel proje yapısını oluştur





  - sontechsp/uygulama/cekirdek/veritabani/moduller klasör hiyerarşisini oluştur
  - Ajan bazlı modül dizinlerini oluştur (stok/pos/crm/satis_belgeleri/eticaret/ebelge/kargo/raporlar)
  - Her modül için gerekli __init__.py dosyalarını ekle
  - Türkçe ASCII isimlendirme kurallarını uygula
  - _Gereksinimler: 1.1, 1.3, 4.1_

- [x] 1.1 SONTECHSP klasör hiyerarşisi tutarlılığı property testi yaz


  - **Özellik 1: SONTECHSP klasör hiyerarşisi tutarlılığı**
  - **Doğrular: Gereksinim 1.1**

- [x] 1.2 Katmanlı mimari uyumluluğu property testi yaz


  - **Özellik 3: Katmanlı mimari uyumluluğu**
  - **Doğrular: Gereksinim 1.3, 4.1, 4.2, 4.4**

- [x] 1.3 Ajan tabanlı modül organizasyonu property testi yaz


  - **Özellik 9: Ajan tabanlı modül organizasyonu**
  - **Doğrular: Gereksinim 4.3**

- [x] 2. SONTECHSP proje yapılandırma dosyalarını oluştur





  - pyproject.toml dosyasını Python sürümü ve SONTECHSP bağımlılıklarla oluştur
  - PyQt6, SQLAlchemy, Alembic, FastAPI, pytest, hypothesis paketlerini tanımla
  - PyInstaller build yapılandırmasını ekle
  - PostgreSQL ve SQLite veritabanı gereksinimlerini belirt
  - _Gereksinimler: 2.1, 2.3_

- [x] 2.1 SONTECHSP bağımlılık standardı property testi yaz


  - **Özellik 4: SONTECHSP bağımlılık standardı**
  - **Doğrular: Gereksinim 2.1**

- [x] 2.2 Veritabanı gereksinim belirtimi property testi yaz


  - **Özellik 6: Veritabanı gereksinim belirtimi**
  - **Doğrular: Gereksinim 2.3, 2.4**

- [x] 3. Windows kurulum dokümantasyonu oluştur (README.md)




  - SONTECHSP proje açıklaması ve genel bakış ekle
  - Windows kurulum talimatlarını detaylı şekilde yaz
  - PyInstaller build notlarını ve Windows gereksinimlerini ekle
  - PostgreSQL/SQLite kurulum rehberini açıkla
  - Çalıştırma rehberini ve geliştirme ortamı kurulumunu ekle
  - _Gereksinimler: 2.2_

- [x] 3.1 Windows kurulum dokümantasyonu property testi yaz


  - **Özellik 5: Windows kurulum dokümantasyonu**
  - **Doğrular: Gereksinim 2.2**

- [x] 4. Ana uygulama giriş noktasını oluştur (uygulama/ana.py)





  - PyQt6 AnaPencere başlatma kodunu yaz (sol menü + içerik alanı)
  - Log sistemi kurulumunu ekle (dosya+console çıktı)
  - Merkezi hata yönetimi sistemi uygula
  - Bootstrap işlevi olarak sadece başlatma kodunu içer (iş kuralı YOK)
  - SONTECHSP standart dosya başlığını ekle
  - _Gereksinimler: 1.2, 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4.1 PyQt6 uygulama başlatma bütünlüğü property testi yaz


  - **Özellik 2: PyQt6 uygulama başlatma bütünlüğü**
  - **Doğrular: Gereksinim 1.2, 3.1, 3.2, 3.3**


- [x] 4.2 Bootstrap işlevi sadeliği property testi yaz


  - **Özellik 7: Bootstrap işlevi sadeliği**
  - **Doğrular: Gereksinim 3.4**

- [x] 4.3 Merkezi hata yönetimi property testi yaz



  - **Özellik 8: Merkezi hata yönetimi**
  - **Doğrular: Gereksinim 3.5, 7.4**

- [x] 5. SONTECHSP çekirdek modül iskeletlerini oluştur





  - uygulama/cekirdek/ altında ayarlar.py, kayit.py, hatalar.py, yetki.py, oturum.py oluştur
  - AlanHatasi/DogrulamaHatasi/EntegrasyonHatasi sınıflarını tanımla
  - Magaza/terminal/kullanici oturum bağlamı yönetimi ekle
  - UI ve veritabanı katmanlarından bağımsız olarak tasarla
  - SONTECHSP standart dosya başlıklarını ekle
  - _Gereksinimler: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 5.1 Çekirdek modül bağımsızlığı property testi yaz


  - **Özellik 13: Çekirdek modül bağımsızlığı**
  - **Doğrular: Gereksinim 7.1, 7.2, 7.3, 7.5**

- [x] 6. SONTECHSP veritabanı modül iskeletini oluştur





  - uygulama/veritabani/ altında modeller, depolar, gocler klasörlerini oluştur
  - baglanti.py (SQLAlchemy engine/sessionmaker) ve taban.py (DeclarativeBase) oluştur
  - Türkçe ASCII tablo isimleri için temel modelleri hazırla (kullanicilar, roller, firmalar vb.)
  - Alembic migration yapılandırmasını hazırla
  - Repository pattern temel sınıflarını oluştur
  - _Gereksinimler: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 6.1 Türkçe ASCII tablo isimlendirmesi property testi yaz


  - **Özellik 12: Türkçe ASCII tablo isimlendirmesi**
  - **Doğrular: Gereksinim 6.1, 6.2, 6.3, 6.4, 6.5**

- [x] 7. İş modülü iskeletlerini oluştur





  - uygulama/moduller/ altında tüm iş modüllerini (stok, pos, crm, vb.) oluştur
  - Her modül için temel klasör yapısını ve __init__.py dosyalarını ekle
  - Modül sınırlarını net şekilde tanımla
  - _Gereksinimler: 4.1, 4.3, 4.4_



- [x] 8. Servis ve arayüz katmanı iskeletlerini oluştur





  - uygulama/servisler/ ve uygulama/arayuz/ klasörlerini oluştur
  - PyQt6 temel pencere iskeletini hazırla
  - Servis katmanı temel sınıflarını oluştur
  - Katmanlar arası bağımlılık kurallarını uygula
  - _Gereksinimler: 4.2, 4.4_

- [x] 9. SONTECHSP kod kalitesi standartlarını uygula


  - Tüm Python dosyalarına Version/Last Update/Module/Description/Changelog şablonunu ekle
  - PEP8 formatını zorunlu olarak tüm dosyalarda uygula
  - 120 satır (yorumlar hariç) ve 25 satır fonksiyon limitlerini kontrol et
  - Türkçe inline açıklamaları tüm dosyalara ekle
  - ASCII Türkçe isimlendirme kurallarını uygula
  - _Gereksinimler: 1.5, 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 9.1 SONTECHSP kod kalitesi standardı property testi yaz


  - **Özellik 10: SONTECHSP kod kalitesi standardı**
  - **Doğrular: Gereksinim 1.5, 5.1, 5.2, 5.3**

- [x] 9.2 Türkçe dokümantasyon standardı property testi yaz


  - **Özellik 11: Türkçe dokümantasyon standardı**
  - **Doğrular: Gereksinim 5.4, 5.5**

- [x] 10. Test altyapısını kur


  - uygulama/testler/ klasörünü oluştur
  - pytest ve hypothesis yapılandırmasını ekle
  - Test yardımcı fonksiyonlarını ve fixture'ları hazırla
  - Property-based test şablonlarını oluştur
  - _Gereksinimler: 1.4_

- [x] 10.1 Başlangıç dosyaları çalışabilirliği property testi yaz


  - **Özellik 15: Başlangıç dosyaları çalışabilirliği**
  - **Doğrular: Gereksinim 1.4**

- [x] 11. SONTECHSP otomatik kurulum modülünü oluştur


  - uygulama/kurulum/baslat.py oluştur
  - Gerekli klasörleri otomatik oluşturan fonksiyonları yaz
  - PostgreSQL bağlantı testi ve migration çalıştırma ekle
  - Varsayılan admin kullanıcı oluşturma işlevi ekle
  - .env veya config.json şablonu üretme fonksiyonu ekle
  - Windows kurulum talimatları için README güncellemesi ekle
  - _Gereksinimler: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 11.1 Otomatik kurulum süreci property testi yaz


  - **Özellik 14: Otomatik kurulum süreci**
  - **Doğrular: Gereksinim 8.1, 8.2, 8.3, 8.4, 8.5**

- [x] 12. Checkpoint - Tüm testlerin geçtiğinden emin ol


  - Tüm testlerin geçtiğinden emin ol, sorular çıkarsa kullanıcıya sor.

- [x] 13. Entegrasyon testi ve doğrulama


  - Ana uygulamanın başlatılabildiğini doğrula
  - Tüm modüllerin import edilebilirliğini test et
  - Klasör yapısının tam olduğunu kontrol et
  - Bağımlılıkların yüklenebilirliğini test et
  - _Gereksinimler: 1.4, 2.4_

- [x] 14. Final Checkpoint - Tüm testlerin geçtiğinden emin ol



  - Tüm testlerin geçtiğinden emin ol, sorular çıkarsa kullanıcıya sor.