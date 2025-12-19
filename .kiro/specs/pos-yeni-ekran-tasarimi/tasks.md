# POS Yeni Ekran Tasarımı - Uygulama Planı

- [x] 1. POS yeni ekran altyapısını oluştur





  - POS yeni ekran klasör yapısını oluştur (uygulama/arayuz/ekranlar/pos/)
  - Temel widget sınıflarının iskeletlerini oluştur
  - Turkuaz tema sınıfını ve QSS stillerini tanımla
  - _Gereksinimler: 10.1_

- [x] 1.1 POS altyapısı için özellik testi yaz


  - **Özellik 8: Kod Kalitesi Uyumluluğu**
  - **Doğrular: Gereksinim 10.1, 10.2, 10.3, 10.4, 10.5**

- [x] 2. Sepet modeli oluştur





  - QAbstractTableModel tabanlı SepetModeli sınıfını yaz
  - Barkod, Ürün, Adet, Fiyat, Tutar, Sil kolonlarını tanımla
  - Turkuaz tema ile satır renklendirme ve seçim vurgulama ekle

  - _Gereksinimler: 3.2_

- [x] 2.1 Sepet modeli için özellik testi yaz

  - **Özellik 3: Sepet Yönetimi**
  - **Doğrular: Gereksinim 3.3, 5.4**

- [x] 3. Üst bar bileşenini oluştur





  - UstBar widget'ını oluştur
  - Sol: Barkod QLineEdit + Ürün arama QComboBox ekle
  - Sağ: Kasiyer etiketi + Müşteri butonları + Saat widget'ı ekle
  - Enter tuşu ile barkod işleme handler'ını yaz
  - _Gereksinimler: 1.2, 1.3, 1.4, 1.5, 2.1, 2.2_

- [x] 3.1 Barkod ve ürün arama için özellik testi yaz


  - **Özellik 2: Barkod ve Ürün Arama İşleme**
  - **Doğrular: Gereksinim 2.1, 2.2, 2.4, 2.5**



- [x] 4. Ödeme paneli bileşenini oluştur



  - OdemePaneli widget'ını oluştur
  - Büyük fontla Genel Toplam göstergesi ekle
  - Ara Toplam, İndirim, KDV toplam alanlarını ekle
  - NAKİT F4, KART F5, PARÇALI F6, AÇIK HESAP F7 butonlarını ekle
  - Nakit ödeme için para girişi ve para üstü hesaplama alanı ekle
  - _Gereksinimler: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 4.1 Ödeme türü yönetimi için özellik testi yaz


  - **Özellik 4: Ödeme Türü Yönetimi**
  - **Doğrular: Gereksinim 4.2**

- [x] 5. Hızlı işlem şeridi oluştur





  - HizliIslemSeridi widget'ını oluştur
  - BEKLET F8, BEKLEYENLER F9, İADE F10, İPTAL ESC, FİŞ YAZDIR, FATURA butonlarını ekle
  - Tek satır layout ile her zaman görünür butonlar yap
  - Bekletme ve iade işlemi handler'larını yaz
  - _Gereksinimler: 5.1, 5.2, 5.3, 5.4, 5.5_




- [x] 6. Hızlı ürünler sekmesi oluştur


  - HizliUrunlerSekmesi widget'ını oluştur
  - QTabWidget ile Ödeme/Hızlı Ürünler sekmelerini kur
  - 12-24 arası grid buton sistemi oluştur
  - Kategori dropdown menüsü ekle
  - Hızlı ürün buton tıklama handler'ını yaz
  - _Gereksinimler: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 6.1 Hızlı ürün butonları için özellik testi yaz


  - **Özellik 5: Hızlı Ürün Butonları**
  - **Doğrular: Gereksinim 6.4, 6.5**


- [x] 7. Ana POS satış ekranını birleştir




  - POSSatisEkrani ana widget'ını oluştur
  - QVBoxLayout ile Üst Bar + Orta Alan + Alt Şerit yerleştir
  - Orta alanda QHBoxLayout ile %70 sepet + %30 ödeme paneli kur
  - Tüm bileşenleri entegre et ve sinyal/slot bağlantıları yap
  - _Gereksinimler: 3.1, 4.1, 5.1_

- [x] 7.1 UI bileşen varlığı için özellik testi yaz


  - **Özellik 1: UI Bileşen Varlığı**
  - **Doğrular: Gereksinim 1.2, 1.3, 1.4, 1.5, 3.1, 3.2, 3.5, 4.1, 4.3, 4.4, 5.1, 5.2, 6.1, 6.3**

- [x] 8. Klavye kısayolu sistemini oluştur





  - Global klavye event handler'ını yaz
  - F2: barkod odağı, F4-F7: ödeme türleri kısayollarını tanımla
  - F8-F10: işlem kısayolları, ESC: iptal, +/-: adet değiştir kısayollarını ekle
  - Tüm widget'larda klavye olaylarını yakala ve yönlendir
  - _Gereksinimler: 2.3, 7.1, 7.2, 7.3, 7.4, 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 8.1 Klavye kısayolları için özellik testi yaz



  - **Özellik 6: Klavye Kısayolları**
  - **Doğrular: Gereksinim 2.3, 8.5**


- [x] 9. Parçalı ödeme dialogunu oluştur


  - ParcaliOdemeDialog widget'ını oluştur
  - Nakit ve kart tutar girişi alanlarını ekle
  - Toplam kontrol ve doğrulama mantığını yaz
  - Turkuaz tema ile dialog stilini uygula
  - _Gereksinimler: 7.3, 7.5_


- [x] 10. İndirim ve kupon dialogunu oluştur


  - IndirimDialog widget'ını oluştur
  - İndirim yüzdesi ve tutar girişi alanları ekle
  - Kupon kodu girişi ve doğrulama alanı ekle
  - Sepet güncellemesi için sinyal/slot sistemi kur
  - _Gereksinimler: 3.5_


- [x] 11. Müşteri seçim dialogunu oluştur


  - MusteriSecDialog widget'ını oluştur (CRM yoksa stub)
  - Müşteri arama ve seçim arayüzü oluştur
  - Açık hesap ödeme için müşteri kontrolü ekle
  - Müşteri temizleme fonksiyonalitesi ekle
  - _Gereksinimler: 1.5, 7.4_


- [x] 12. Hata yönetimi sistemini oluştur






  - POSHataYoneticisi sınıfını oluştur
  - Turkuaz tema ile QMessageBox hata gösterimi ekle
  - Log kayıt sistemini entegre et
  - Spesifik hata türleri için renk kodları tanımla
  - Sistem durumu koruma mekanizması kur
  - _Gereksinimler: 11.1, 11.2, 11.3, 11.4, 11.5_

- [x] 12.1 Hata yönetimi için özellik testi yaz


  - **Özellik 9: Hata Yönetimi**

  - **Doğrular: Gereksinim 11.1, 11.2, 11.5**


- [x] 13. UI stil ve tema sistemini uygula



  - TurkuazTema sınıfını tamamla
  - QSS stil dosyalarını oluştur ve uygula
  - Büyük butonlar, artırılmış satır yüksekliği stillerini ekle
  - QFrame kartlar ve spacing ayarlarını yap
  - Büyük font toplam göstergelerini stil ile vurgula
  - _Gereksinimler: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 13.1 UI stil ve tema için özellik testi yaz


  - **Özellik 7: UI Stil ve Tema**
  - **Doğrular: Gereksinim 9.1, 9.2, 9.3, 9.4, 9.5**

- [x] 14. AnaPencere entegrasyonunu tamamla

  - AnaPencere menüsüne "POS Satış" yeni ekran bağlantısı ekle
  - Mevcut eski POS widget'ı varsa yönlendirme yap
  - QStackedWidget'a yeni POS ekranını ekle
  - Menü geçiş durumu koruma sistemini kur
  - POS ekranı kapatma ve sepet verisi saklama işlemini ekle
  - _Gereksinimler: 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 14.1 Menü entegrasyonu için özellik testi yaz
  - **Özellik 10: Menü Entegrasyonu ve Durum Yönetimi**
  - **Doğrular: Gereksinim 12.3, 12.5**

- [x] 15. Checkpoint - Tüm testlerin geçtiğinden emin ol

  - Tüm testlerin geçtiğinden emin ol, sorular çıkarsa kullanıcıya sor.


- [x] 16. POS servis entegrasyonunu tamamla
  - Mevcut POS servislerini yeni UI'ya bağla
  - Sepet, ödeme, stok servislerini entegre et
  - Offline kuyruk servisini bağla
  - Servis çağrı hata yönetimini yeni hata sistemi ile entegre et
  - _Gereksinimler: 10.5_

- [x] 16.1 Servis entegrasyon testleri yaz
  - POS UI - Servis entegrasyon testleri
  - Mock servis testleri
  - End-to-end akış testleri

- [x] 17. Final Checkpoint - Sistem entegrasyonu testi

  - Tüm testlerin geçtiğinden emin ol, sorular çıkarsa kullanıcıya sor.