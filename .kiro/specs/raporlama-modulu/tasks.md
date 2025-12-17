# Uygulama Planı

- [x] 1. Raporlama modül yapısını ve temel DTO'ları kur


  - Raporlama modülü için dizin yapısı oluştur
  - TarihAraligiDTO, SatisOzetiDTO, UrunPerformansDTO, KritikStokDTO, RaporSatirDTO, DisariAktarDTO sınıflarını uygula
  - Raporlama sabitleri ve enum'ları tanımla
  - _Gereksinimler: 7.1, 7.2, 7.3_

- [x] 1.1 DTO tamlığı için özellik testi yaz


  - **Özellik 1: Satış özeti tamlığı**
  - **Doğrular: Gereksinim 1.1**

- [x] 1.2 DTO tip güvenliği için özellik testi yaz


  - **Özellik 28: DTO tip güvenliği**
  - **Doğrular: Gereksinim 7.3**


- [x] 2. Veritabanı işlemleri için sorgu katmanını uygula



  - Optimize edilmiş veritabanı sorguları ile sorgular.py oluştur
  - satis_ozeti, kritik_stok_listesi, en_cok_satan_urunler, karlilik_ozeti fonksiyonlarını uygula
  - Salt okunur oturum kullanımı ve düzgün hata yönetimi sağla
  - _Gereksinimler: 1.2, 2.1, 2.2, 3.1, 3.2, 6.1, 6.4_

- [x] 2.1 Satış durumu filtreleme için özellik testi yaz


  - **Özellik 2: Satış durumu filtreleme**
  - **Doğrular: Gereksinim 1.2**

- [x] 2.2 Kritik stok filtreleme için özellik testi yaz


  - **Özellik 5: Kritik stok filtreleme**
  - **Doğrular: Gereksinim 2.1**


- [x] 2.3 Stok verisi bütünlüğü için özellik testi yaz


  - **Özellik 6: Stok verisi bütünlüğü**
  - **Doğrular: Gereksinim 2.2**

- [x] 2.4 En iyi ürün sıralaması için özellik testi yaz


  - **Özellik 9: En iyi ürün sıralaması**
  - **Doğrular: Gereksinim 3.1**

- [x] 2.5 Salt okunur veritabanı oturumları için özellik testi yaz


  - **Özellik 22: Salt okunur veritabanı oturumları**
  - **Doğrular: Gereksinim 6.1**

- [x] 3. CSV ve PDF için dışa aktarma işlevselliği oluştur

  - CSV dışa aktarma işlevselliği ile disari_aktarim.py uygula
  - PDF dışa aktarma iskeleti oluştur (MVP placeholder)
  - Dosya yolu oluşturma ve hata yönetimi yardımcıları ekle
  - _Gereksinimler: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 3.1 CSV format geçerliliği için özellik testi yaz

  - **Özellik 13: CSV format geçerliliği**
  - **Doğrular: Gereksinim 4.1**

- [x] 3.2 PDF dışa aktarma kararlılığı için özellik testi yaz

  - **Özellik 14: PDF dışa aktarma kararlılığı**
  - **Doğrular: Gereksinim 4.2**

- [x] 3.3 Dışa aktarma dosya yolu dönüşü için özellik testi yaz

  - **Özellik 15: Dışa aktarma dosya yolu dönüşü**
  - **Doğrular: Gereksinim 4.3**

- [x] 3.4 Dışa aktarma dosya adı benzersizliği için özellik testi yaz

  - **Özellik 17: Dışa aktarma dosya adı benzersizliği**
  - **Doğrular: Gereksinim 4.5**

- [x] 4. Raporlama servis katmanını uygula

  - Tüm ana raporlama metodları ile RaporServisi sınıfı oluştur
  - satis_ozeti_al, kritik_stok_al, en_cok_satan_al metodlarını uygula
  - Karlılık placeholder uygulaması ekle
  - Dışa aktarma işlevselliğini entegre et
  - _Gereksinimler: 1.1, 1.4, 1.5, 2.4, 2.5, 3.3, 3.5, 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 4.1 Satış toplama doğruluğu için özellik testi yaz

  - **Özellik 3: Satış toplama doğruluğu**
  - **Doğrular: Gereksinim 1.4**

- [x] 4.2 Depo filtreleme için özellik testi yaz

  - **Özellik 7: Depo filtreleme**
  - **Doğrular: Gereksinim 2.4**

- [x] 4.3 Limit parametresi saygısı için özellik testi yaz

  - **Özellik 11: Limit parametresi saygısı**
  - **Doğrular: Gereksinim 3.3**

- [x] 4.4 Karlılık MVP kararlılığı için özellik testi yaz

  - **Özellik 19: Karlılık MVP kararlılığı**
  - **Doğrular: Gereksinim 5.3**

- [x] 4.5 İş mantığı yerleşimi için özellik testi yaz

  - **Özellik 29: İş mantığı yerleşimi**
  - **Doğrular: Gereksinim 7.4**

- [x] 5. Kapsamlı hata yönetimi ve loglama ekle

  - Tüm servis metodları için düzgün istisna yönetimi uygula
  - Yavaş sorgular için performans loglaması ekle
  - Veritabanı bağlantı hata yönetimi oluştur

  - Karlılık MVP loglaması ekle
  - _Gereksinimler: 6.4, 6.5, 5.5_

- [x] 5.1 Veritabanı hata yönetimi için özellik testi yaz


  - **Özellik 24: Veritabanı hata yönetimi**
  - **Doğrular: Gereksinim 6.4**


- [x] 5.2 Performans loglama için özellik testi yaz

  - **Özellik 25: Performans loglama**
  - **Doğrular: Gereksinim 6.5**

- [x] 5.3 Karlılık loglama için özellik testi yaz

  - **Özellik 21: Karlılık loglama**
  - **Doğrular: Gereksinim 5.5**

- [x] 6. Eş zamanlı erişim güvenliği ve optimizasyon uygula

  - Thread-safe veritabanı oturum yönetimi ekle
  - Sorgu optimizasyon tekniklerini uygula
  - Eş zamanlı erişim test desteği ekle
  - _Gereksinimler: 6.2, 6.3_

- [x] 6.1 Eş zamanlı erişim güvenliği için özellik testi yaz

  - **Özellik 23: Eş zamanlı erişim güvenliği**
  - **Doğrular: Gereksinim 6.3**

- [x] 7. Modül başlatma ve dışa aktarımları oluştur

  - Düzgün dışa aktarımlarla __init__.py kur
  - Temiz mimari uyumluluğu sağla
  - UI importlarının bulunmadığını doğrula
  - _Gereksinimler: 7.1, 7.2, 7.5_


- [x] 7.1 UI import kısıtlaması için özellik testi yaz

  - **Özellik 26: UI import kısıtlaması**
  - **Doğrular: Gereksinim 7.1**

- [x] 7.2 Katman ayrımı için özellik testi yaz

  - **Özellik 27: Katman ayrımı**
  - **Doğrular: Gereksinim 7.2**

- [x] 8. Kontrol Noktası - Tüm testlerin geçtiğinden emin ol

  - Tüm testlerin geçtiğinden emin ol, sorular çıkarsa kullanıcıya sor.

- [x] 9. Kenar durum yönetimi ve doğrulama ekle

  - Tüm rapor metresi doğrulaması ekle
  - Eksik veri için zarif bozulma uygula
  - _Gereksinimler: 1.3, 2.3, 3.4_

- [x] 9.1 Kenar durumlar için birim testleri yaz

  - Boş satış verisi senaryolarını test et
  - Kritik stok bulunmayan senaryoları test et
  - En çok satan ürün bulunmayan senaryoları test et
  - _Gereksinimler: 1.3, 2.3, 3.4_

- [x] 10. Son entegrasyon ve doğrulama

  - Tam raporlama iş akışını uçtan uca test et
  - Tüm DTO eşlemelerinin doğru çalıştığını doğrula
  - Dışa aktarma dosya oluşturmayı doğrula
  - Performans gereksinimlerinin karşılandığından emin ol
  - _Gereksinimler: Tüm gereksinim entegrasyonu_

- [x] 10.1 Entegrasyon testleri yaz

  - Tam raporlama servis iş akışlarını test et
  - Gerçek veri ile veritabanı entegrasyonunu test et
  - _Gereksinimler: Tüm gereksinim entegrasyonu_

- [x] 11. Son Kontrol Noktası - Tüm testlerin geçtiğinden emin ol


  - Tüm testlerin geçtiğinden emin ol, sorular çıkarsa kullanıcıya sor.
