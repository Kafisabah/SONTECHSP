# POS Arayüz Entegrasyonu - Uygulama Planı

- [x] 1. POS UI altyapısını oluştur





  - POS UI klasör yapısını oluştur (ui/pos/, bilesenler/, handlers/)
  - Temel POS bileşen arayüzlerini tanımla (POSBilesenArayuzu)
  - POS sinyal/slot sistemini kur (POSSinyalleri)
  - _Gereksinimler: 9.1_

- [x] 1.1 POS altyapısı için özellik testi yaz


  - **Özellik 11: Mimari Uyumluluk**
  - **Doğrular: Gereksinim 9.1, 9.5**

- [x] 2. Ana POS ekranını oluştur





  - POSAnaEkran widget'ını oluştur
  - Grid layout (3x3) yapısını kur
  - Bileşen container'larını yerleştir
  - _Gereksinimler: 2.1, 3.2, 4.1, 5.1, 6.1_

- [x] 2.1 POS ekran bileşenleri için özellik testi yaz


  - **Özellik 2: POS Ekran Bileşenleri**
  - **Doğrular: Gereksinim 2.1, 3.2, 4.1, 4.2, 5.1, 6.1**

- [x] 3. Barkod paneli bileşenini oluştur





  - BarkodPaneli widget'ını oluştur
  - Barkod giriş alanı ve EKLE butonunu ekle
  - Barkod doğrulama ve ürün ekleme handler'ını yaz
  - _Gereksinimler: 2.1, 2.2, 2.3, 2.4_

- [x] 3.1 Barkod işleme için özellik testi yaz


  - **Özellik 3: Barkod İşleme**
  - **Doğrular: Gereksinim 2.2, 2.3, 2.4**

- [x] 4. Sepet tablosu bileşenini oluştur
  - SepetTablosu widget'ını oluştur
  - Tablo kolonlarını tanımla (Barkod, Ürün, Adet, Fiyat, Tutar, Sil)
  - Sepet güncelleme ve satır silme handler'larını yaz
  - Boş sepet durumu için "Sepet boş" mesajını ekle
  - _Gereksinimler: 3.1, 3.2, 3.4, 3.5_

- [x] 4.1 Sepet yönetimi için özellik testi yaz
  - **Özellik 4: Sepet Yönetimi**
  - **Doğrular: Gereksinim 3.1, 3.4, 3.5**

- [x] 5. Ödeme paneli bileşenini oluştur



  - OdemePaneli widget'ını oluştur
  - AraToplam, İndirim, GenelToplam göstergelerini ekle
  - NAKİT, KART, PARÇALI, AÇIK HESAP butonlarını ekle
  - Ödeme türü handler'larını yaz
  - _Gereksinimler: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 5.1 Ödeme türü yönetimi için özellik testi yaz


  - **Özellik 5: Ödeme Türü Yönetimi**
  - **Doğrular: Gereksinim 4.3, 4.4, 4.5**

- [x] 6. Hızlı ürün paneli bileşenini oluştur







  - HizliUrunPaneli widget'ını oluştur
  - 12-24 arası dinamik buton sistemi kur
  - Kategori seçici ekle
  - Hızlı ürün handler'ını yaz
  - Boş butonlar için "Tanımsız" etiketi ekle
  - _Gereksinimler: 5.1, 5.2, 5.4, 5.5_

- [x] 6.1 Hızlı ürün butonları için özellik testi yaz




  - **Özellik 6: Hızlı Ürün Butonları**
  - **Doğrular: Gereksinim 5.1, 5.2, 5.4, 5.5**


- [x] 7. İşlem kısayolları panelini oluştur

  - IslemKisayollari widget'ını oluştur
  - BEKLET, BEKLEYENLER, İADE, İPTAL, FİŞ YAZDIR, FATURA butonlarını ekle
  - İşlem handler'larını yaz (bekletme, iade dialog, fiş yazdırma)
  - _Gereksinimler: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 7.1 İşlem kısayolları için özellik testi yaz


  - **Özellik 7: İşlem Kısayolları**
  - **Doğrular: Gereksinim 6.2, 6.3, 6.4, 6.5**


- [x] 8. Klavye kısayolu sistemini oluştur


  - KlavyeKisayolYoneticisi sınıfını oluştur
  - F2, F4, F5, ESC, DEL kısayollarını tanımla
  - Global klavye event handler'ını yaz
  - _Gereksinimler: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 8.1 Klavye kısayolları için özellik testi yaz


  - **Özellik 8: Klavye Kısayolları**
  - **Doğrular: Gereksinim 7.1, 7.2, 7.3, 7.4, 7.5**

- [x] 9. Eşleştirme tablosu dialogunu oluştur









  - EslestirmeDialog widget'ını oluştur
  - Ekran, Buton, Handler, Servis Metodu kolonlarını ekle
  - Otomatik güncelleme sistemini kur
  - CSV dışa aktarım özelliğini ekle
  - _Gereksinimler: 8.1, 8.2, 8.3, 8.4, 8.5_



- [x] 9.1 Eşleştirme tablosu için özellik testi yaz



  - **Özellik 9: Eşleştirme Tablosu**
  - **Doğrular: Gereksinim 8.1, 8.2, 8.3, 8.4, 8.5**

- [x] 10. AnaPencere entegrasyonunu tamamla








  - AnaPencere'ye POS menü öğesi ekle
  - QStackedWidget'a POS ekranını ekle
  - Menü geçiş handler'ını yaz
  - Ekran durumu koruma sistemini kur
  - _Gereksinimler: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 10.1 Menü entegrasyonu için özellik testi yaz


  - **Özellik 1: Menü Entegrasyonu**
  - **Doğrular: Gereksinim 1.1, 1.2**

- [x] 11. Hata yönetimi sistemini oluştur




  - POSHataYoneticisi sınıfını oluştur
  - QMessageBox hata gösterimi ekle
  - Log kayıt sistemini entegre et
  - Sistem durumu koruma mekanizması kur
  - _Gereksinimler: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 11.1 Hata yönetimi için özellik testi yaz




  - **Özellik 12: Hata Yönetimi**
  - **Doğrular: Gereksinim 10.1, 10.2, 10.3, 10.4, 10.5**

- [x] 12. Kod kalitesi kontrollerini uygula





  - Dosya boyutu limiti (120 satır) kontrolü ekle
  - Fonksiyon boyutu limiti (25 satır) kontrolü ekle
  - PEP8 uyumluluk kontrolü ekle
  - Otomatik kod kalitesi raporlama sistemi kur
  - _Gereksinimler: 9.2, 9.3, 9.4_

- [x] 12.1 Kod kalitesi için özellik testi yaz


  - **Özellik 10: Kod Kalitesi Uyumluluğu**
  - **Doğrular: Gereksinim 9.2, 9.3, 9.4**

- [x] 13. Checkpoint - Tüm testlerin geçtiğinden emin ol





  - Tüm testlerin geçtiğinden emin ol, sorular çıkarsa kullanıcıya sor.

- [x] 14. POS servis entegrasyonunu tamamla







  - Mevcut POS servislerini UI'ya bağla
  - Sepet, ödeme, stok servislerini entegre et
  - Offline kuyruk servisini bağla
  - Servis çağrı hata yönetimini ekle
  - _Gereksinimler: 9.5_

- [x] 14.1 Entegrasyon testleri yaz


  - POS UI - Servis entegrasyon testleri
  - Mock servis testleri
  - End-to-end akış testleri

- [x] 15. Final Checkpoint - Sistem entegrasyonu testi







  - Tüm testlerin geçtiğinden emin ol, sorular çıkarsa kullanıcıya sor.