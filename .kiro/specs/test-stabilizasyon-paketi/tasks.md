# Test ve Stabilizasyon Paketi - Uygulama Planı

## Genel Bakış

Bu uygulama planı, SONTECHSP sistemi için kritik iş kurallarının doğruluğunu garanti eden test ve stabilizasyon paketini oluşturmak için gereken görevleri tanımlar. Her görev, mevcut sistem üzerine inşa edilecek şekilde tasarlanmıştır.

## Görev Listesi

- [x] 1. Test dokümantasyonu ve strateji rehberi oluştur





  - Test stratejisi, çalıştırma yöntemleri ve ortam gereksinimlerini içeren kapsamlı README_TEST.md dosyası oluştur
  - Test kategorileri (smoke, fast, slow, critical) ve çalıştırma komutlarını dokümante et
  - Test veritabanı kurulum ve konfigürasyon rehberini hazırla
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2. Negatif stok limit testleri uygula





  - Negatif stok kontrol kuralları için senaryo testleri yaz
  - Stok seviyesi eşik testleri (0: uyarı, -3: uyarı+izin, -6: engel) uygula
  - DogrulamaHatasi kontrolü ve test veritabanı kullanımını sağla
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 2.1 Negatif stok eşik kuralları property testi yaz


  - **Property 5: Negatif stok eşik kuralları**
  - **Validates: Requirements 2.2, 2.3**

- [x] 2.2 Negatif stok tutarlılığı property testi yaz


  - **Property 6: Negatif stok tutarlılığı**
  - **Validates: Requirements 2.4**

- [x] 3. Eş zamanlı stok işlem testleri geliştir





  - Aynı ürün için paralel stok düşüm testleri oluştur
  - Row-level lock mekanizması ve veri tutarlılığı kontrolü uygula
  - Thread-safe işlem testleri ve çakışma senaryolarını test et
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 3.1 Eş zamanlı stok kilitleme property testi yaz


  - **Property 7: Eş zamanlı stok kilitleme**
  - **Validates: Requirements 3.1, 3.2**


- [x] 3.2 Stok tutarlılık korunumu property testi yaz

  - **Property 8: Stok tutarlılık korunumu**
  - **Validates: Requirements 3.3, 3.4**



- [x] 4. POS ödeme transaction bütünlük testleri oluştur



  - POS ödeme_tamamla tek transaction mantığını test et
  - Stok düşümü + satış kaydı atomik işlem kontrolü uygula
  - Rollback mekanizması ve hata durumu testlerini geliştir
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 4.1 POS transaction atomikliği property testi yaz




  - **Property 9: POS transaction atomikliği**
  - **Validates: Requirements 4.1**

- [x] 4.2 Transaction rollback garantisi property testi yaz




  - **Property 10: Transaction rollback garantisi**
  - **Validates: Requirements 4.2, 4.4**

- [x] 4.3 Satış-stok bütünlüğü property testi yaz




  - **Property 11: Satış-stok bütünlüğü**
  - **Validates: Requirements 4.3**


- [x] 5. E-belge retry mekanizması testleri uygula





  - DummySaglayici hata simülasyonu ile retry testleri oluştur
  - Deneme sayısı artırma ve maksimum deneme sonrası HATA durumu kontrolü
  - Başarılı retry sonrası deneme sayacı sıfırlama testini geliştir
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 5.1 E-belge retry sayacı property testi yaz


  - **Property 12: E-belge retry sayacı**
  - **Validates: Requirements 5.1, 5.2**

- [x] 5.2 E-belge retry başarı sıfırlama property testi yaz


  - **Property 13: E-belge retry başarı sıfırlama**
  - **Validates: Requirements 5.4**


- [x] 6. Offline kuyruk işleyiş testleri geliştir





  - Offline kuyruğa kayıt ekleme ve kuyruktan okuma testleri oluştur
  - FIFO sırası kontrolü ve kuyruk temizleme testlerini uygula
  - İnternet bağlantı simülasyonu ile gerçekçi offline senaryoları test et
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 6.1 Offline kuyruk FIFO sırası property testi yaz
  





  - **Property 14: Offline kuyruk FIFO sırası**
  - **Validates: Requirements 6.2, 6.4**


- [x] 6.2 Offline kuyruk kayıt-işleme property testi yaz

  - **Property 15: Offline kuyruk kayıt-işleme**
  - **Validates: Requirements 6.1, 6.3**

- [x] 7. UI smoke testleri genişlet






  - Mevcut smoke_test_calistir.py altyapısını kullanarak genişletilmiş kontroller ekle
  - Tüm ana modüllerin import edilebilirliği ve kritik servislerin başlatılabilirliği kontrolü
  - Özet rapor sunumu ve temel fonksiyon kontrollerini uygula
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [x] 7.1 Smoke test kapsamlılığı property testi yaz


  - **Property 16: Smoke test kapsamlılığı**
  - **Validates: Requirements 7.1, 7.2**

- [x] 7.2 Smoke test raporlama property testi yaz


  - **Property 17: Smoke test raporlama**
  - **Validates: Requirements 7.3, 7.4**




- [x] 8. Test altyapısı ve mock servisleri oluştur




  - Test konfigürasyon sistemi ve test veritabanı bağlantı yönetimi uygula
  - DummySaglayici ve MockNetworkService mock servislerini geliştir
  - Test sonuç raporlama ve hata yönetim sistemini oluştur


  - Test kategorileri (smoke, fast, slow, critical) marker sistemini kur


- [x] 9. Checkpoint - Tüm testlerin çalıştığından emin ol




  - Tüm testlerin başarıyla çalıştığını doğrula, kullanıcıya sorular çıkarsa danış

## Görev Detayları

### Görev 1: Test Dokümantasyonu
**Dosya:** `tests/README_TEST.md`
- Test stratejisi açıklaması (Unit + Property-based)
- Çalıştırma komutları (pytest, kategoriler)
- Ortam kurulum rehberi (test DB, mock servisler)
- Test kategorileri ve marker kullanımı

### Görev 2: Negatif Stok Testleri
**Dosya:** `tests/test_stok_negatif_limit.py`
- Stok seviyesi 0: uyarı verme kontrolü
- Stok seviyesi -1 ile -3: uyarı + izin verme kontrolü
- Stok seviyesi -6 ve altı: DogrulamaHatasi fırlatma kontrolü
- Test veritabanı kullanımı ve temizlik

### Görev 3: Eş Zamanlı Stok Testleri
**Dosya:** `tests/test_stok_eszamanlilik.py`
- Threading ile paralel stok düşüm testleri
- Row-level lock mekanizması kontrolü
- Veri tutarlılığı ve çakışma çözümleme testleri
- Final stok seviyesi matematiksel doğruluk kontrolü

### Görev 4: POS Transaction Testleri
**Dosya:** `tests/test_pos_odeme_tamamla_butunluk.py`
- Atomik transaction kontrolü (stok + satış)
- Rollback mekanizması hata simülasyonu
- Satış TAMAMLANDI durumu için stok düşümü zorunluluğu
- Transaction başarısızlık sonrası sistem durumu kontrolü

### Görev 5: E-belge Retry Testleri
**Dosya:** `tests/test_ebelge_retry.py`
- DummySaglayici hata simülasyonu
- Deneme sayısı artırma kontrolü
- Maksimum deneme sonrası kalıcı HATA durumu
- Başarılı retry sonrası sayaç sıfırlama

### Görev 6: Offline Kuyruk Testleri
**Dosya:** `tests/test_offline_kuyruk.py`
- SQLite kuyruk kayıt/okuma işlemleri
- FIFO sırası korunumu kontrolü
- İnternet bağlantı simülasyonu
- Kuyruk temizleme ve işlem tamamlama

### Görev 7: UI Smoke Testleri
**Dosya:** `tests/test_ui_smoke.py`
- Mevcut smoke_test_calistir.py entegrasyonu
- Ana modül import kontrolü
- Kritik servis başlatma testleri
- Özet rapor formatı kontrolü

### Görev 8: Test Altyapısı
**Dosyalar:** Test konfigürasyon ve mock servisler
- TestConfig ve TestResult veri modelleri
- Test veritabanı bağlantı yönetimi
- Mock servis implementasyonları
- Test marker ve kategori sistemi

## Teknik Notlar

### Test Veritabanı Yaklaşımı
- Ayrı PostgreSQL test veritabanı kullanımı
- Her test öncesi temiz durum garantisi
- Test verisi otomatik oluşturma ve temizleme

### Property-Based Test Konfigürasyonu
- Hypothesis kütüphanesi kullanımı
- Minimum 100 iterasyon ile kapsamlı test
- Rastgele veri üretimi ile edge case keşfi

### Mock Servis Stratejisi
- DummySaglayici: %50 hata oranı ile gerçekçi simülasyon
- MockNetworkService: İnternet bağlantı durumu kontrolü
- Kontrollü hata senaryoları ile güvenilir test

### Test Kategorileri
- **smoke**: < 30 saniye, temel kontroller
- **fast**: < 2 dakika, hızlı unit testler
- **slow**: < 10 dakika, kapsamlı entegrasyon
- **critical**: < 5 dakika, kritik iş kuralları