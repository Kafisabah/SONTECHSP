# Kurulum Bootstrap Altyapısı - Uygulama Planı

- [x] 1. Temel kurulum modülü yapısını oluştur


  - uygulama/kurulum/ klasörünü oluştur
  - __init__.py dosyasını ekle
  - Modül düzeyinde hata sınıflarını tanımla
  - _Gereksinimler: 1.1, 2.1, 3.1_

- [x] 1.1 Kurulum modülü için unit testler yaz


  - Test klasör yapısını oluştur
  - Temel test yardımcı fonksiyonlarını yaz
  - _Gereksinimler: 1.1, 2.1, 3.1_

- [x] 2. Sabitler modülünü implement et


  - uygulama/kurulum/sabitler.py dosyasını oluştur
  - Klasör sabitlerini tanımla (VERI_KLASORU, LOG_KLASORU, vb.)
  - Config dosyası adını tanımla
  - _Gereksinimler: 1.1_

- [x] 2.1 Sabitler modülü için property test yaz


  - **Özellik 2: Gerekli Klasörlerin Varlığı**
  - **Doğrular: Gereksinimler 1.1**

- [x] 3. Klasör yönetimi modülünü implement et


  - uygulama/kurulum/klasorler.py dosyasını oluştur
  - klasorleri_olustur() fonksiyonunu yaz
  - klasor_var_mi() fonksiyonunu yaz
  - Windows uyumlu pathlib kullanımını implement et
  - _Gereksinimler: 1.1, 1.2, 1.3, 1.4_

- [x] 3.1 Klasör yönetimi için property testler yaz


  - **Özellik 1: Klasör Oluşturma İdempotentliği**
  - **Doğrular: Gereksinimler 1.2**

- [x] 3.2 Klasör hata yönetimi için property test yaz


  - **Özellik 3: Hatalı Yol Yönetimi**
  - **Doğrular: Gereksinimler 1.3**

- [x] 4. Ayar dosyası yönetimi modülünü implement et


  - uygulama/kurulum/ayar_olusturucu.py dosyasını oluştur
  - varsayilan_ayarlar() fonksiyonunu yaz
  - ayar_dosyasi_var_mi() fonksiyonunu yaz
  - ayar_dosyasi_olustur() fonksiyonunu yaz
  - ayarlari_yukle() fonksiyonunu yaz
  - _Gereksinimler: 2.1, 2.2, 2.3, 2.4_

- [x] 4.1 Ayar dosyası idempotentlik property testi yaz


  - **Özellik 4: Ayar Dosyası İdempotentliği**
  - **Doğrular: Gereksinimler 2.2**

- [x] 4.2 Ayar dosyası içerik bütünlüğü property testi yaz


  - **Özellik 5: Ayar Dosyası İçerik Bütünlüğü**
  - **Doğrular: Gereksinimler 2.3**

- [x] 4.3 JSON format geçerliliği property testi yaz


  - **Özellik 6: JSON Format Geçerliliği**
  - **Doğrular: Gereksinimler 2.4**

- [x] 5. Veritabanı kontrol modülünü implement et



  - uygulama/kurulum/veritabani_kontrol.py dosyasını oluştur
  - baglanti_test_et() fonksiyonunu yaz
  - gocleri_calistir() fonksiyonunu yaz
  - Alembic programatik entegrasyonunu implement et
  - _Gereksinimler: 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 4.4_

- [x] 5.1 Veritabanı bağlantı hata yönetimi property testi yaz


  - **Özellik 7: Veritabanı Bağlantı Hata Yönetimi**
  - **Doğrular: Gereksinimler 3.2**

- [x] 5.2 Migration hata yönetimi property testi yaz




  - **Özellik 8: Migration Hata Yönetimi**
  - **Doğrular: Gereksinimler 4.2**

- [x] 6. Admin kullanıcı oluşturucu modülünü implement et
  - uygulama/kurulum/admin_olusturucu.py dosyasını oluştur
  - admin_varsa_gec() fonksiyonunu yaz
  - admin_olustur() fonksiyonunu yaz
  - bcrypt şifre hashleme entegrasyonunu implement et
  - _Gereksinimler: 5.1, 5.2, 5.3, 5.4_

- [x] 6.1 Admin kullanıcı idempotentlik property testi yaz
  - **Özellik 9: Admin Kullanıcı İdempotentliği**
  - **Doğrular: Gereksinimler 5.2**

- [x] 6.2 Şifre hash güvenliği property testi yaz
  - **Özellik 10: Şifre Hash Güvenliği**
  - **Doğrular: Gereksinimler 5.3**

- [x] 6.3 Kullanıcı oluşturma hata loglama property testi yaz
  - **Özellik 11: Kullanıcı Oluşturma Hata Loglama**
  - **Doğrular: Gereksinimler 5.4**

- [x] 7. Ana bootstrap koordinatörünü implement et


  - uygulama/kurulum/baslat.py dosyasını oluştur
  - ilk_calistirma_hazirla() fonksiyonunu yaz
  - Tüm kurulum adımlarını sırasıyla koordine et
  - Hata yönetimi ve loglama implement et
  - _Gereksinimler: 6.1, 6.2, 6.3, 6.4_

- [x] 7.1 Bootstrap hata yönetimi property testi yaz


  - **Özellik 12: Bootstrap Hata Yönetimi**
  - **Doğrular: Gereksinimler 6.2**



- [x] 8. Checkpoint - Tüm testlerin geçtiğinden emin ol


  - Tüm testlerin geçtiğinden emin ol, sorular çıkarsa kullanıcıya sor.


- [x] 9. README.md dokümantasyonunu güncelle


  - Kurulum bölümünü ekle
  - config.json konumu ve örneğini belirt
  - PostgreSQL bağlantı örneğini ekle
  - Otomatik migration bilgisini ekle
  - PyInstaller build adımlarını açıkla
  - _Gereksinimler: 7.1, 7.2, 7.3, 7.4_


- [x] 10. pyproject.toml bağımlılıklarını güncelle

  - PyQt6, FastAPI, SQLAlchemy bağımlılıklarını ekle
  - Alembic, psycopg2-binary paketlerini ekle
  - passlib[bcrypt] güvenlik paketini ekle
  - python-dotenv yapılandırma paketini ekle
  - _Gereksinimler: 8.1, 8.2, 8.3, 8.4_

- [x] 10.1 Bağımlılık entegrasyonu için unit testler yaz


  - Tüm gerekli paketlerin import edilebilirliğini test et
  - Paket versiyonu uyumluluğunu kontrol et
  - _Gereksinimler: 8.1, 8.2, 8.3, 8.4_


- [x] 11. Final Checkpoint - Tüm testlerin geçtiğinden emin ol


  - Tüm testlerin geçtiğinden emin ol, sorular çıkarsa kullanıcıya sor.