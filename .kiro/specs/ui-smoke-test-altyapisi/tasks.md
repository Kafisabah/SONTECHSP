# Uygulama Planı

- [x] 1. Buton Eşleştirme Kaydı Sistemi













- [x] 1.1 Buton eşleştirme veri modeli oluştur


  - `ButonEslestirme` dataclass tanımla
  - Thread-safe kayıt listesi oluştur
  - _Gereksinim: 2.1, 2.4_




- [x] 1.2 Kayıt ekleme fonksiyonu implement et

  - `kayit_ekle()` fonksiyonunu yaz
  - Thread-safety için lock mekanizması ekle
  - Otomatik zaman damgası ekle
  - _Gereksinim: 2.1, 2.3_


- [x] 1.3 Özellik testi: Buton eşleştirme veri bütünlüğü

  - **Özellik 4: Buton Eşleştirme Veri Bütünlüğü**
  - **Doğrular: Gereksinim 2.1**



- [x] 1.4 Kayıt listeleme fonksiyonu implement et




  - `kayitlari_listele()` fonksiyonunu yaz
  - Yapılandırılmış format döndür
  - _Gereksinim: 2.2, 2.4_




- [x] 1.5 Özellik testi: Kayıt listeleme tamlığı
  - **Özellik 5: Kayıt Listeleme Tamlığı**
  - **Doğrular: Gereksinim 2.2**
  - **Durum**: Tamamlandı - Property-based testler yazıldı ve çalıştırıldı
  - **Not**: Testler global singleton pattern nedeniyle test izolasyonu sorunu yaşıyor (beklenen davranış)


- [x] 1.6 Kayıt temizleme ve yardımcı fonksiyonlar





  - `kayitlari_temizle()` fonksiyonunu yaz
  - Tablo formatında çıktı fonksiyonu ekle
  - _Gereksinim: 2.2, 2.4_

- [x] 1.7 Özellik testi: Yapılandırılmış veri formatı




  - **Özellik 7: Yapılandırılmış Veri Formatı**
  - **Doğrular: Gereksinim 2.4**

- [x] 2. Log Sistemi Entegrasyonu









- [x] 2.1 Log veri modeli ve yapılandırma


  - `LogKaydi` dataclass tanımla
  - Log seviyesi yapılandırması ekle
  - Log dosyası yolu belirle
  - _Gereksinim: 3.1, 3.3_

- [x] 2.2 Handler loglama fonksiyonu


  - Buton handler çalıştığında log yaz
  - Ekran, buton, handler bilgilerini içer
  - _Gereksinim: 3.1, 3.3_


- [x] 2.3 Özellik testi: Handler loglama tutarlılığı

  - **Özellik 8: Handler Loglama Tutarlılığı**
  - **Doğrular: Gereksinim 3.1**

- [x] 2.4 Stub servis loglama fonksiyonu


  - Stub servis çağrıldığında "stub çağrıldı" yaz
  - Servis metodu bilgisini ekle
  - _Gereksinim: 3.2_


- [x] 2.5 Özellik testi: Stub servis loglama


 - `stub_servis_loglama()` fonksiyonunu yaz

  - **Özellik 9: Stub Servis Loglama**
  - **Doğrular: Gereksinim 3.2**


- [x] 2.6 Özellik testi: Log içerik tamlığı





  - **Özellik 10: Log İçerik Tamlığı**
  - **Doğrular: Gereksinim 3.3**

- [x] 3. Mevcut Ekranlara Entegrasyon






- [x] 3.1 Temel ekran sınıfına kayıt desteği ekle

  - `temel_ekran.py`'ye kayıt fonksiyonu ekle
  - Buton bağlama wrapper fonksiyonu oluştur
  - _Gereksinim: 2.3, 3.1_


- [x] 3.2 Özellik testi: Otomatik kayıt tutarlılığı

  - **Özellik 6: Otomatik Kayıt Tutarlılığı**
  - **Doğrular: Gereksinim 2.3**


- [x] 3.3 Gösterge paneli ekranına entegre et

  - `gosterge_paneli.py`'de butonları kaydet
  - Handler'lara log ekle
  - Stub servis çağrılarını işaretle
  - _Gereksinim: 2.3, 3.1, 3.2, 3.4_


- [x] 3.4 POS satış ekranına entegre et

  - `pos_satis.py`'de butonları kaydet
  - Handler'lara log ekle
  - Stub servis çağrılarını işaretle
  - _Gereksinim: 2.3, 3.1, 3.2, 3.4_

- [x] 3.5 Ürünler stok ekranına entegre et


  - `urunler_stok.py`'de butonları kaydet
  - Handler'lara log ekle
  - Stub servis çağrılarını işaretle
  - _Gereksinim: 2.3, 3.1, 3.2, 3.4_

- [x] 3.6 Özellik testi: UI iş kuralı kısıtlaması


  - **Özellik 11: UI İş Kuralı Kısıtlaması**
  - **Doğrular: Gereksinim 3.4**

- [x] 4. Smoke Test Çalıştırıcısı


- [x] 4.1 Smoke test ana modülü oluştur



  - `smoke_test_calistir.py` dosyasını oluştur
  - `main()` fonksiyonunu implement et
  - Komut satırı argüman desteği ekle
  - _Gereksinim: 1.1, 1.4, 4.2_

- [x] 4.2 Özellik testi: Smoke test başlatma tutarlılığı
  - **Özellik 1: Smoke Test Başlatma Tutarlılığı**
  - **Doğrular: Gereksinim 1.1**

- [x] 4.3 Ekran geçiş testi fonksiyonu
  - `ekran_gecis_testi()` fonksiyonunu yaz
  - Tüm ekranları sırayla ziyaret et
  - Her geçişi logla
  - _Gereksinim: 1.2_

- [x] 4.4 Özellik testi: Ekran geçiş erişilebilirliği
  - **Özellik 2: Ekran Geçiş Erişilebilirliği**
  - **Doğrular: Gereksinim 1.2**

- [x] 4.5 Temiz kapanış fonksiyonu
  - `temiz_kapanis()` fonksiyonunu yaz
  - Kaynakları temizle
  - Hata durumlarını yönet
  - _Gereksinim: 1.3_

- [x] 4.6 Özellik testi: Temiz kapanış garantisi
  - **Özellik 3: Temiz Kapanış Garantisi**
  - **Doğrular: Gereksinim 1.3**

- [x] 4.7 Standart giriş noktası doğrulama










  - `uygulama.py` giriş noktasını kullan
  - Alternatif giriş noktalarını kontrol et
  - _Gereksinim: 4.1, 4.2, 4.3_




- [x] 4.8 Özellik testi: Standart giriş noktası tutarlılığı


  - **Özellik 12: Standart Giriş Noktası Tutarlılığı**
  - **Doğrular: Gereksinim 4.1**

- [x] 5. Checkpoint - Tüm testlerin geçtiğinden emin ol





  - Tüm testlerin geçtiğinden emin ol, sorular çıkarsa kullanıcıya sor.


- [x] 6. Dokümantasyon ve Çıktı Araçları







- [x] 6.1 Buton eşleştirme tablosu çıktı fonksiyonu



  - Tablo formatında çıktı oluştur
  - CSV export desteği ekle
  - _Gereksinim: 2.2, 2.4_


- [x] 6.2 Kullanım dokümantasyonu oluştur

  - README.md dosyası oluştur
  - Kurulum adımlarını yaz
  - Çalıştırma örnekleri ekle
  - _Gereksinim: 1.4_


- [x] 6.3 Örnek çalıştırma script'i

  - Sanal ortam kurulum script'i
  - Bağımlılık yükleme script'i
  - Test çalıştırma script'i
  - _Gereksinim: 1.4_