# Kod Kalitesi Refactoring Uygulama Gereksinimleri

## Proje Özeti

SONTECHSP kod tabanında tespit edilen kod kalitesi sorunlarının sistematik olarak çözülmesi için pratik refactoring uygulaması. Analiz sonuçlarına göre 106 dosya ve 544 fonksiyon limit aşımı tespit edilmiş olup, bunların güvenli ve kontrollü bir şekilde refactor edilmesi hedeflenmektedir.

## Mevcut Durum Analizi

### Tespit Edilen Sorunlar
- **Toplam Dosya:** 254 dosya
- **Limit Aşan Dosya:** 106 dosya (%42)
- **Limit Aşan Fonksiyon:** 544 fonksiyon
- **En Büyük Dosya:** `ebelge.py` (805 satır - 6.7x limit aşımı)
- **Mimari İhlal:** 0 (temiz)

### Kritik Dosyalar (Top 10)
1. `uygulama/arayuz/ekranlar/ebelge.py` - 805 satır
2. `uygulama/arayuz/ekranlar/raporlar.py` - 704 satır
3. `uygulama/arayuz/ekranlar/ayarlar.py` - 696 satır
4. `uygulama/arayuz/ekranlar/kargo.py` - 644 satır
5. `uygulama/arayuz/ekranlar/musteriler.py` - 578 satır
6. `uygulama/arayuz/ekranlar/eticaret.py` - 574 satır
7. `uygulama/arayuz/ekranlar/urunler_stok.py` - 531 satır
8. `sontechsp/uygulama/kod_kalitesi/guvenlik_sistemi.py` - 523 satır
9. `sontechsp/uygulama/kod_kalitesi/refactoring_orkestratori.py` - 518 satır
10. `sontechsp/uygulama/cekirdek/hatalar.py` - 501 satır

## Kullanıcı Hikayeleri

### Epic 1: UI Katmanı Refactoring (Yüksek Öncelik)
**Hedef:** En büyük UI dosyalarını 120 satır limitine uygun hale getirmek

#### US1.1: E-Belge Ekranı Refactoring
**Olarak:** Geliştirici  
**İstiyorum ki:** `ebelge.py` dosyası (805 satır) mantıklı modüllere bölünsün  
**Böylece:** Kod okunabilirliği artacak ve bakım kolaylaşacak  

**Kabul Kriterleri:**
- [ ] Dosya 4-5 alt modüle bölünmeli (her biri max 200 satır)
- [ ] `filtre_grubu_olustur` (106 satır) ayrı dosyaya taşınmalı
- [ ] `islemler_grubu_olustur` (110 satır) ayrı dosyaya taşınmalı
- [ ] Tüm import'lar doğru şekilde güncellenmelidir
- [ ] Mevcut testler çalışmaya devam etmelidir
- [ ] UI fonksiyonalitesi korunmalıdır

#### US1.2: Raporlar Ekranı Refactoring
**Olarak:** Geliştirici  
**İstiyorum ki:** `raporlar.py` dosyası (704 satır) mantıklı modüllere bölünsün  
**Böylece:** Rapor geliştirme süreci hızlanacak  

**Kabul Kriterleri:**
- [ ] Dosya 3-4 alt modüle bölünmeli
- [ ] `rapor_olusturma_grubu_olustur` (113 satır) ayrı dosyaya taşınmalı
- [ ] Filtre ve export fonksiyonları ayrı modüllere taşınmalı
- [ ] Rapor oluşturma fonksiyonalitesi korunmalıdır

#### US1.3: Ayarlar Ekranı Refactoring
**Olarak:** Geliştirici  
**İstiyorum ki:** `ayarlar.py` dosyası (696 satır) mantıklı modüllere bölünsün  
**Böylece:** Ayar yönetimi daha modüler hale gelecek  

**Kabul Kriterleri:**
- [ ] Dosya 3-4 alt modüle bölünmeli
- [ ] `alt_butonlar_olustur` (105 satır) ayrı dosyaya taşınmalı
- [ ] Form ve doğrulama fonksiyonları ayrı modüllere taşınmalı
- [ ] Ayar kaydetme/yükleme fonksiyonalitesi korunmalıdır

### Epic 2: Repository Katmanı Refactoring (Orta Öncelik)
**Hedef:** Büyük repository dosyalarını optimize etmek

#### US2.1: POS Repository'leri Refactoring
**Olarak:** Geliştirici  
**İstiyorum ki:** POS repository dosyaları (satis_repository.py: 501 satır, offline_kuyruk_repository.py: 495 satır) bölünsün  
**Böylece:** Veritabanı işlemleri daha yönetilebilir hale gelecek  

**Kabul Kriterleri:**
- [ ] Her repository dosyası max 200 satıra indirilmeli
- [ ] CRUD işlemleri mantıklı gruplara ayrılmalı
- [ ] Veritabanı transaction'ları korunmalıdır
- [ ] Repository pattern bozulmamalıdır

### Epic 3: Servis Katmanı Refactoring (Orta Öncelik)
**Hedef:** Büyük servis fonksiyonlarını optimize etmek

#### US3.1: Stok Transfer Servisi Refactoring
**Olarak:** Geliştirici  
**İstiyorum ki:** `stok_transfer_service.py::transfer_yap` fonksiyonu (143 satır) bölünsün  
**Böylece:** Stok transfer işlemleri daha anlaşılır hale gelecek  

**Kabul Kriterleri:**
- [ ] Ana fonksiyon max 25 satıra indirilmeli
- [ ] Yardımcı fonksiyonlar oluşturulmalı
- [ ] İş kuralları korunmalıdır
- [ ] Transaction bütünlüğü sağlanmalıdır

### Epic 4: Kod Kalitesi Araçları Refactoring (Düşük Öncelik)
**Hedef:** Kendi geliştirdiğimiz araçları optimize etmek

#### US4.1: Güvenlik Sistemi Refactoring
**Olarak:** Geliştirici  
**İstiyorum ki:** `guvenlik_sistemi.py` (523 satır) ve `refactoring_orkestratori.py` (518 satır) bölünsün  
**Böylece:** Araçlarımız da standartlara uygun hale gelecek  

**Kabul Kriterleri:**
- [ ] Her dosya max 200 satıra indirilmeli
- [ ] Backup ve restore işlemleri ayrı modüllere taşınmalı
- [ ] CLI arayüzü korunmalıdır

## Teknik Gereksinimler

### TR1: Güvenlik ve Geri Alma
- [ ] Her refactoring işlemi öncesi otomatik backup alınmalı
- [ ] Rollback mekanizması çalışır durumda olmalı
- [ ] İşlem logları tutulmalı

### TR2: Test Koruma
- [ ] Mevcut tüm testler çalışmaya devam etmeli
- [ ] Test coverage düşmemeli
- [ ] Yeni modüller için testler güncellenmelidir

### TR3: Import Yapısı
- [ ] Tüm import'lar doğru şekilde güncellenmelidir
- [ ] Circular import'lar oluşmamalıdır
- [ ] Katman sınırları korunmalıdır

### TR4: Fonksiyonalite Koruma
- [ ] UI davranışları değişmemelidir
- [ ] API sözleşmeleri korunmalıdır
- [ ] Veritabanı işlemleri etkilenmemelidir

## Performans Gereksinimleri

### PR1: Refactoring Süresi
- [ ] Tek dosya refactoring max 5 dakika sürmeli
- [ ] Tüm süreç max 2 saat sürmeli
- [ ] Kullanıcı onayı adımları dahil

### PR2: Bellek Kullanımı
- [ ] Refactoring sırasında max 1GB RAM kullanılmalı
- [ ] Geçici dosyalar temizlenmeli
- [ ] Backup dosyaları optimize edilmeli

## Kalite Gereksinimleri

### QR1: Kod Standartları
- [ ] PEP8 uyumluluğu korunmalı
- [ ] Türkçe yorum ve dokümantasyon
- [ ] Standart dosya başlıkları eklenmelidir

### QR2: Mimari Uyumluluk
- [ ] Katman sınırları korunmalı
- [ ] Dependency injection pattern'i uygulanmalı
- [ ] Single responsibility principle'a uygun bölme

## Kabul Kriterleri

### Başarı Metrikleri
- [ ] 120+ satırlı dosya sayısı %70 azalmalı (106 → ~30)
- [ ] 25+ satırlı fonksiyon sayısı %60 azalmalı (544 → ~220)
- [ ] Tüm testler geçmelidir
- [ ] Mimari ihlal sayısı 0 kalmalıdır

### Kalite Metrikleri
- [ ] Kod okunabilirlik skoru artmalı
- [ ] Geliştirici onboarding süresi %50 azalmalı
- [ ] Bug fix süresi %40 azalmalı
- [ ] Kod review süresi %50 azalmalı

## Riskler ve Kısıtlar

### Yüksek Risk
- **UI Bozulması:** Ekran bölme sırasında UI bileşenleri bozulabilir
- **Test Kırılması:** Import değişiklikleri testleri etkileyebilir
- **Performans Düşüşü:** Modül bölme performansı etkileyebilir

### Orta Risk
- **Circular Import:** Yanlış bölme circular import'lara neden olabilir
- **API Değişikliği:** Public API'lar istemeden değişebilir

### Kısıtlar
- **Zaman:** Toplam süreç max 1 hafta sürmeli
- **Kaynak:** Tek geliştirici ile yapılacak
- **Ortam:** Production'ı etkilememeli

## Başarı Tanımı

Bu spec başarılı sayılacak eğer:
1. En büyük 10 dosya 300 satırın altına indirilirse
2. Tüm testler geçerse
3. UI fonksiyonalitesi korunursa
4. Kod kalitesi metrikleri hedeflenen seviyelere ulaşırsa
5. Geliştirici deneyimi iyileşirse

## Sonraki Adımlar

1. **Faz 1:** UI katmanı refactoring (ebelge.py, raporlar.py, ayarlar.py)
2. **Faz 2:** Repository katmanı refactoring
3. **Faz 3:** Servis katmanı refactoring
4. **Faz 4:** Kod kalitesi araçları refactoring
5. **Faz 5:** Final doğrulama ve optimizasyon