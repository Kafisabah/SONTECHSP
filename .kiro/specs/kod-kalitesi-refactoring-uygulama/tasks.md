# Kod Kalitesi Refactoring Uygulama Görev Listesi

## Genel Bakış

Bu görev listesi, kod kalitesi analizi sonuçlarına dayanarak tespit edilen sorunların sistematik çözümü için pratik refactoring adımlarını tanımlar. Güvenlik öncelikli, faz faz uygulama yaklaşımı benimsenmiştir.

## Görev Listesi

### Faz 1: Altyapı ve Güvenlik Hazırlığı

- [x] 1. Refactoring Altyapısını Hazırla





  - Mevcut kod kalitesi araçlarını refactoring için uyarla
  - Güvenlik ve yedekleme sistemlerini aktif hale getir
  - İlerleme takibi ve denetim kayıt sistemlerini hazırla
  - _Requirements: TR1, TR2, TR3, TR4_

- [x] 1.1 Yedekleme ve Geri Alma Sistemini Aktifleştir


  - `YedekYoneticisi` sınıfını refactoring için optimize et
  - Git tabanlı yedekleme stratejisini uygula
  - Geri alma mekanizmasını test et
  - _Requirements: TR1_

- [x] 1.2 Test Koruma Sistemini Hazırla


  - Mevcut test suite'ini analiz et
  - Test coverage temel seviyesini oluştur
  - Test güncelleme stratejisini hazırla
  - _Requirements: TR2_

- [x] 1.3 Import Güncelleme Sistemini Hazırla


  - Bağımlılık analiz araçlarını hazırla
  - Döngüsel import tespit sistemini aktifleştir
  - Import güncelleme algoritmalarını test et
  - _Requirements: TR3_

### Faz 2: UI Katmanı Refactoring (Yüksek Öncelik)

- [-] 2. E-Belge Ekranı Refactoring (ebelge.py - 805 satır)

  - En büyük dosyayı mantıklı modüllere böl
  - UI fonksiyonalitesini koru
  - Import yapısını güncelle
  - _Requirements: US1.1_


- [x] 2.1 E-Belge Dosyası Analizi ve Planlama

  - `ebelge.py` dosyasını AST ile analiz et
  - Fonksiyonel grupları tespit et (filtreler, işlemler, durum, tablolar)
  - Bölme planını oluştur ve kullanıcı onayı al
  - _Requirements: US1.1_


- [x] 2.2 E-Belge Filtreler Modülü Oluştur

  - `filtre_grubu_olustur` fonksiyonunu (106 satır) ayrı dosyaya taşı
  - `ebelge_filtreleri.py` dosyasını oluştur
  - Import'ları güncelle ve test et
  - _Requirements: US1.1_


- [x] 2.3 E-Belge İşlemler Modülü Oluştur

  - `islemler_grubu_olustur` fonksiyonunu (110 satır) ayrı dosyaya taşı
  - `ebelge_islemleri.py` dosyasını oluştur
  - Event handler'ları doğru şekilde bağla
  - _Requirements: US1.1_


- [x] 2.4 E-Belge Durum Modülü Oluştur

  - `durum_bilgisi_grubu_olustur` fonksiyonunu (67 satır) ayrı dosyaya taşı
  - `ebelge_durum.py` dosyasını oluştur
  - Durum güncelleme mekanizmalarını test et
  - _Requirements: US1.1_


- [ ] 2.5 E-Belge Ana Modülü Optimize Et

  - Ana sınıf ve koordinasyon kodunu `ebelge_ana.py`'da tut
  - `__init__.py` ile public API'yi export et
  - Tüm modüllerin doğru entegrasyonunu test et
  - _Requirements: US1.1_

- [ ] 2.6 E-Belge Refactoring Doğrulaması
  - UI fonksiyonalitesini test et
  - Tüm testlerin geçtiğini doğrula
  - Performans etkisini ölç
  - _Requirements: US1.1_

- [ ] 3. Raporlar Ekranı Refactoring (raporlar.py - 704 satır)
  - İkinci en büyük dosyayı mantıklı modüllere böl
  - Rapor oluşturma fonksiyonalitesini koru
  - _Requirements: US1.2_

- [ ] 3.1 Raporlar Dosyası Analizi ve Planlama
  - `raporlar.py` dosyasını analiz et
  - Rapor oluşturma, filtreler, export gruplarını tespit et
  - Bölme planını oluştur
  - _Requirements: US1.2_

- [ ] 3.2 Rapor Oluşturma Modülü Oluştur
  - `rapor_olusturma_grubu_olustur` fonksiyonunu (113 satır) ayrı dosyaya taşı
  - `rapor_olusturma.py` dosyasını oluştur
  - Rapor generation logic'ini test et
  - _Requirements: US1.2_

- [ ] 3.3 Rapor Filtreleri Modülü Oluştur
  - Filtre ile ilgili fonksiyonları `rapor_filtreleri.py`'ye taşı
  - Tarih aralığı ve diğer filtre fonksiyonlarını organize et
  - _Requirements: US1.2_

- [ ] 3.4 Rapor Export Modülü Oluştur
  - Export fonksiyonlarını `rapor_export.py`'ye taşı
  - CSV, PDF export fonksiyonalitesini test et
  - _Requirements: US1.2_

- [ ] 3.5 Raporlar Refactoring Doğrulaması
  - Rapor oluşturma sürecini end-to-end test et
  - Export fonksiyonlarını test et
  - Performance regression kontrolü yap
  - _Requirements: US1.2_

- [ ] 4. Ayarlar Ekranı Refactoring (ayarlar.py - 696 satır)
  - Üçüncü en büyük dosyayı mantıklı modüllere böl
  - Ayar yönetimi fonksiyonalitesini koru
  - _Requirements: US1.3_

- [ ] 4.1 Ayarlar Dosyası Analizi ve Planlama
  - `ayarlar.py` dosyasını analiz et
  - Butonlar, formlar, doğrulama gruplarını tespit et
  - Bölme planını oluştur
  - _Requirements: US1.3_

- [ ] 4.2 Ayar Butonları Modülü Oluştur
  - `alt_butonlar_olustur` fonksiyonunu (105 satır) ayrı dosyaya taşı
  - `ayar_butonlari.py` dosyasını oluştur
  - Button event handler'larını test et
  - _Requirements: US1.3_

- [ ] 4.3 Ayar Formları Modülü Oluştur
  - Form oluşturma fonksiyonlarını `ayar_formlari.py`'ye taşı
  - Form validation logic'ini organize et
  - _Requirements: US1.3_

- [ ] 4.4 Ayar Doğrulama Modülü Oluştur
  - Doğrulama fonksiyonlarını `ayar_dogrulama.py`'ye taşı
  - Input validation'ı test et
  - _Requirements: US1.3_

- [ ] 4.5 Ayarlar Refactoring Doğrulaması
  - Ayar kaydetme/yükleme sürecini test et
  - Form validation'ı test et
  - UI responsiveness'ı kontrol et
  - _Requirements: US1.3_

### Faz 3: Repository Katmanı Refactoring (Orta Öncelik)

- [ ] 5. POS Repository'leri Refactoring
  - Büyük repository dosyalarını optimize et
  - CRUD işlemlerini mantıklı gruplara ayır
  - _Requirements: US2.1_

- [ ] 5.1 Satış Repository Refactoring (satis_repository.py - 501 satır)
  - CRUD, sorgular, raporlar modüllerine böl
  - Transaction bütünlüğünü koru
  - Repository pattern'i bozma
  - _Requirements: US2.1_

- [ ] 5.2 Offline Kuyruk Repository Refactoring (offline_kuyruk_repository.py - 495 satır)
  - Kuyruk işlemleri, senkronizasyon, monitoring modüllerine böl
  - Offline/online geçiş fonksiyonalitesini koru
  - _Requirements: US2.1_

- [ ] 5.3 İade Repository Refactoring (iade_repository.py - 433 satır)
  - İade CRUD, iş kuralları, raporlar modüllerine böl
  - İade sürecinin bütünlüğünü koru
  - _Requirements: US2.1_

### Faz 4: Servis Katmanı Refactoring (Orta Öncelik)

- [ ] 6. Büyük Servis Fonksiyonları Refactoring
  - 25+ satırlı fonksiyonları yardımcı fonksiyonlara böl
  - İş kurallarını koru
  - _Requirements: US3.1_

- [ ] 6.1 Stok Transfer Servisi Fonksiyon Refactoring
  - `transfer_yap` fonksiyonunu (143 satır) böl
  - Ana koordinasyon + yardımcı fonksiyonlar yaklaşımı
  - Transaction bütünlüğünü koru
  - _Requirements: US3.1_

- [ ] 6.2 Diğer Büyük Servis Fonksiyonları
  - `parcali_odeme_yap` (95 satır) fonksiyonunu böl
  - `kuyruk_senkronize_et` (96 satır) fonksiyonunu böl
  - `rezervasyon_yap` (83 satır) fonksiyonunu böl
  - _Requirements: US3.1_

### Faz 5: Kod Kalitesi Araçları Refactoring (Düşük Öncelik)

- [ ] 7. Kendi Araçlarımızı Refactor Et
  - Geliştirdiğimiz kod kalitesi araçlarını da standartlara uygun hale getir
  - _Requirements: US4.1_

- [ ] 7.1 Güvenlik Sistemi Refactoring (guvenlik_sistemi.py - 523 satır)
  - Yedekleme, geri yükleme, denetim modüllerine böl
  - Güvenlik fonksiyonalitesini koru
  - _Requirements: US4.1_

- [ ] 7.2 Refactoring Orkestratörü Refactoring (refactoring_orkestratori.py - 518 satır)
  - Orkestrasyon, faz kontrolü, ilerleme takibi modüllerine böl
  - CLI arayüzünü koru
  - _Requirements: US4.1_

### Faz 6: Final Doğrulama ve Optimizasyon

- [ ] 8. Kapsamlı Sistem Doğrulaması
  - Tüm refactoring işlemlerinin başarılı olduğunu doğrula
  - Sistem geneli testleri çalıştır
  - _Requirements: QR1, QR2_

- [ ] 8.1 Fonksiyonalite Doğrulaması
  - UI ekranlarının doğru çalıştığını test et
  - İş kurallarının korunduğunu doğrula
  - API sözleşmelerinin bozulmadığını kontrol et
  - _Requirements: TR4_

- [ ] 8.2 Performans Doğrulaması
  - Temel performans ile karşılaştır
  - Bellek kullanımını kontrol et
  - Response time'ları ölç
  - _Requirements: PR1, PR2_

- [ ] 8.3 Kod Kalitesi Metrikleri Doğrulaması
  - Dosya boyut hedeflerinin karşılandığını doğrula (106 → ~30)
  - Fonksiyon boyut hedeflerinin karşılandığını doğrula (544 → ~220)
  - PEP8 uyumluluğunu kontrol et
  - _Requirements: QR1_

- [ ] 8.4 Mimari Doğrulaması
  - Katman sınırlarının korunduğunu doğrula
  - Döngüsel import'ların olmadığını kontrol et
  - Dependency injection pattern'inin uygulandığını doğrula
  - _Requirements: QR2_

- [ ] 9. Dokümantasyon ve Raporlama
  - Refactoring sürecini dokümante et
  - Başarı metriklerini rapor et
  - Gelecek iyileştirmeler için öneriler hazırla

- [ ] 9.1 Refactoring Raporu Hazırla
  - Önce/sonra karşılaştırması yap
  - Başarı metriklerini hesapla
  - Risk analizi ve çözümlerini dokümante et

- [ ] 9.2 Geliştirici Dokümantasyonu Güncelle
  - Yeni modül yapısını dokümante et
  - Import yapısı değişikliklerini açıkla
  - Best practice'leri güncelle

- [ ] 9.3 Sürekli İyileştirme Planı Oluştur
  - Otomatik kod kalitesi kontrolü için CI/CD entegrasyonu planla
  - Gelecek refactoring hedeflerini belirle
  - Ekip eğitimi planını hazırla

## Kontrol Noktaları

### Kontrol Noktası 1: Altyapı Hazırlığı Tamamlandı
- [ ] Yedekleme sistemi aktif
- [ ] Test koruma sistemi hazır
- [ ] Import güncelleme sistemi test edildi
- [ ] İlk dosya refactoring'e hazır

### Kontrol Noktası 2: UI Katmanı Refactoring Tamamlandı
- [ ] En büyük 3 UI dosyası refactor edildi
- [ ] Tüm UI testleri geçiyor
- [ ] Kullanıcı deneyimi korundu
- [ ] Repository katmanına geçiş hazır

### Kontrol Noktası 3: Repository Katmanı Refactoring Tamamlandı
- [ ] POS repository'leri refactor edildi
- [ ] Veritabanı işlemleri korundu
- [ ] Transaction bütünlüğü sağlandı
- [ ] Servis katmanına geçiş hazır

### Kontrol Noktası 4: Servis Katmanı Refactoring Tamamlandı
- [ ] Büyük fonksiyonlar bölündü
- [ ] İş kuralları korundu
- [ ] API sözleşmeleri bozulmadı
- [ ] Final doğrulamaya hazır

### Kontrol Noktası 5: Final Doğrulama Tamamlandı
- [ ] Tüm hedef metrikler karşılandı
- [ ] Sistem geneli testler geçiyor
- [ ] Performans kabul edilebilir seviyede
- [ ] Dokümantasyon tamamlandı

## Risk Yönetimi

### Yüksek Risk Görevleri
- **2.2-2.5:** E-Belge modül bölme (UI bozulma riski)
- **5.1-5.3:** Repository refactoring (veri bütünlüğü riski)
- **6.1:** Stok transfer fonksiyon bölme (iş kuralı riski)

### Risk Azaltma Stratejileri
- Her yüksek risk görev öncesi yedek al
- Adım adım uygula ve her adımda test et
- Kullanıcı onayı al
- Geri alma planını hazır tut

## Başarı Kriterleri

### Sayısal Hedefler
- [ ] 120+ satırlı dosya sayısı: 106 → 30 (%70 azalma)
- [ ] 25+ satırlı fonksiyon sayısı: 544 → 220 (%60 azalma)
- [ ] Tüm testler geçiyor (%100 test başarı oranı)
- [ ] Performans kaybı <%5

### Niteliksel Hedefler
- [ ] Kod okunabilirliği artmış
- [ ] Geliştirici deneyimi iyileşmiş
- [ ] Bakım kolaylığı artmış
- [ ] Yeni geliştirici adaptasyonu hızlanmış

## Notlar

- Her görev için yedek alınacak
- Kullanıcı onayı olmadan kritik değişiklik yapılmayacak
- Test başarısızlığı durumunda geri alma yapılacak
- İlerleme sürekli raporlanacak
- Türkçe dokümantasyon ve hata mesajları kullanılacak