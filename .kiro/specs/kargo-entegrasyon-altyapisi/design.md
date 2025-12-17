# Kargo Entegrasyon Altyapısı - Tasarım Belgesi

## Genel Bakış

Kargo entegrasyon altyapısı, SONTECHSP sistemi için taşıyıcı-bağımsız kargo yönetimi sağlar. Sistem, etiket oluşturma, takip etme ve durum yönetimi için modüler bir yapı sunar. Bu aşamada gerçek API entegrasyonu olmayacak; standart arayüzler ve dummy implementasyonlar kullanılacak.

## Mimari

### Katman Yapısı

```
UI Layer (PyQt) 
    ↓
Service Layer (Kargo Servisleri)
    ↓  
Repository Layer (Kargo Depoları)
    ↓
Database Layer (PostgreSQL)
```

### Modül Bağımlılıkları

```
kargo/servisler.py → kargo/depolar.py → veritabani/modeller/kargo.py
kargo/servisler.py → kargo/tasiyici_fabrikasi.py → kargo/tasiyici_arayuzu.py
```

## Bileşenler ve Arayüzler

### 1. DTO Katmanı (kargo/dto.py)

**KargoEtiketOlusturDTO**: Etiket oluşturma için giriş verisi
- Zorunlu alanlar: kaynak_turu, kaynak_id, alici_ad, alici_telefon, alici_adres, alici_il, alici_ilce, tasiyici
- Opsiyonel alanlar: gonderen_ad, gonderen_telefon, paket_agirlik_kg, servis_kodu, aciklama

**KargoEtiketSonucDTO**: Etiket oluşturma sonucu
- etiket_id, durum, takip_no, mesaj alanları

**KargoDurumDTO**: Takip durum bilgisi
- etiket_id, takip_no, durum, aciklama, zaman alanları

### 2. Sabitler (kargo/sabitler.py)

**Kaynak Türleri**: POS_SATIS, SATIS_BELGESI
**Etiket Durumları**: BEKLIYOR, OLUSTURULDU, HATA  
**Takip Durumları**: BILINMIYOR, KARGODA, TESLIM, IPTAL
**Taşıyıcılar**: YURTICI, ARAS, MNG, PTT, SURAT

### 3. Taşıyıcı Arayüzü (kargo/tasiyici_arayuzu.py)

```python
class TasiyiciArayuzu(ABC):
    @abstractmethod
    def etiket_olustur(self, payload: dict) -> dict:
        """Etiket oluşturur ve sonuç döndürür"""
        pass
    
    @abstractmethod  
    def durum_sorgula(self, takip_no: str) -> dict:
        """Takip numarası ile durum sorgular"""
        pass
```

### 4. Taşıyıcı Fabrikası (kargo/tasiyici_fabrikasi.py)

Taşıyıcı adına göre uygun carrier implementasyonu döndürür. MVP aşamasında DummyTasiyici kullanılır.

### 5. Repository Katmanı (kargo/depolar.py)

**KargoDeposu**: Veritabanı işlemleri
- etiket_kaydi_olustur(): Yeni etiket kaydı oluşturur
- etiket_getir(): ID ile etiket getirir
- etiket_durum_guncelle(): Etiket durumunu günceller
- takip_kaydi_ekle(): Takip geçmişi ekler
- bekleyen_etiketleri_al(): Yeniden deneme için etiketler
- etiket_kaynaktan_bul(): Benzersizlik kontrolü

### 6. Servis Katmanı (kargo/servisler.py)

**KargoServisi**: İş kuralları ve orchestration
- etiket_olustur(): Ana etiket oluşturma işlemi
- bekleyen_etiketleri_isle(): Retry mekanizması
- durum_sorgula(): Takip durum sorgulama

## Veri Modelleri

### kargo_etiketleri Tablosu

| Alan | Tür | Açıklama |
|------|-----|----------|
| id | SERIAL PRIMARY KEY | Benzersiz etiket ID |
| kaynak_turu | VARCHAR(50) | POS_SATIS veya SATIS_BELGESI |
| kaynak_id | INTEGER | Kaynak belge ID |
| tasiyici | VARCHAR(50) | Taşıyıcı kodu |
| servis_kodu | VARCHAR(50) NULL | Taşıyıcı servis kodu |
| alici_ad | VARCHAR(255) | Alıcı adı |
| alici_telefon | VARCHAR(20) | Alıcı telefonu |
| alici_adres | TEXT | Alıcı adresi |
| alici_il | VARCHAR(100) | Alıcı ili |
| alici_ilce | VARCHAR(100) | Alıcı ilçesi |
| paket_agirlik_kg | DECIMAL(10,2) | Paket ağırlığı |
| durum | VARCHAR(50) | Etiket durumu |
| mesaj | TEXT NULL | Hata/bilgi mesajı |
| takip_no | VARCHAR(100) NULL | Takip numarası |
| deneme_sayisi | INTEGER DEFAULT 0 | Retry sayısı |
| olusturulma_zamani | TIMESTAMP | Oluşturulma zamanı |
| guncellenme_zamani | TIMESTAMP | Güncellenme zamanı |

**Kısıtlamalar**: UNIQUE(kaynak_turu, kaynak_id, tasiyici)

### kargo_takipleri Tablosu

| Alan | Tür | Açıklama |
|------|-----|----------|
| id | SERIAL PRIMARY KEY | Benzersiz takip ID |
| etiket_id | INTEGER FK | Etiket referansı |
| takip_no | VARCHAR(100) | Takip numarası |
| durum | VARCHAR(50) | Takip durumu |
| aciklama | TEXT NULL | Durum açıklaması |
| zaman | TIMESTAMP NULL | Durum zamanı |
| olusturulma_zamani | TIMESTAMP | Kayıt zamanı |

**İndeksler**: takip_no, durum, (kaynak_turu, kaynak_id)

## Doğruluk Özellikleri

*Bir özellik, sistemin tüm geçerli çalıştırmalarında doğru kalması gereken bir karakteristik veya davranıştır - esasen, sistemin ne yapması gerektiği hakkında resmi bir ifadedir. Özellikler, insan tarafından okunabilir spesifikasyonlar ile makine tarafından doğrulanabilir doğruluk garantileri arasında köprü görevi görür.*

### Özellik Yansıması

Prework analizinde 40 testable property tespit edildi. Aşağıdaki redundancy analizi yapıldı:

**Birleştirilebilir Özellikler:**
- Özellik 1.1-1.5: Etiket oluşturma doğrulama kuralları → tek kapsamlı özellik
- Özellik 2.1-2.2: Kaynak türü kaydetme → tek özellik  
- Özellik 3.1-3.5: Durum sorgulama işlemleri → iki ana özellik
- Özellik 6.1-6.3: Zaman damgası kaydetme → tek özellik
- Özellik 7.1-7.5: Transaction ve veri tutarlılığı → iki ana özellik
- Özellik 8.1-8.5: Performans optimizasyonları → iki ana özellik

**Özellik 1: Etiket Oluşturma Doğrulama**
*Herhangi bir* etiket oluşturma talebi için, sistem geçerli taşıyıcı bilgilerini doğrulayacak, kaynak türü ve ID'sini kontrol edecek, benzersizlik kuralını uygulayacak ve başarılı işlemlerde takip numarası ile sonuç döndürecek
**Doğrular: Gereksinimler 1.1, 1.2, 1.3, 1.4, 1.5**

**Özellik 2: Kaynak Türü Yönetimi**
*Herhangi bir* etiket oluşturma işleminde, sistem kaynak türünü (POS_SATIS veya SATIS_BELGESI) doğru şekilde kayıt edecek ve eksik/geçersiz veriler için uygun hata mesajları döndürecek
**Doğrular: Gereksinimler 2.1, 2.2, 2.3, 2.4**

**Özellik 3: Varsayılan Değer Atama**
*Herhangi bir* etiket oluşturma işleminde paket ağırlığı belirtilmediğinde, sistem varsayılan 1.0 kg değerini kullanacak
**Doğrular: Gereksinimler 2.5**

**Özellik 4: Durum Sorgulama İşlemleri**
*Herhangi bir* geçerli takip numarası için durum sorgulandığında, sistem güncel durum bilgisini döndürecek ve takip geçmişine yeni kayıt ekleyecek
**Doğrular: Gereksinimler 3.1, 3.2, 3.5**

**Özellik 5: Hata Yönetimi**
*Herhangi bir* geçersiz takip numarası veya taşıyıcı servis hatası durumunda, sistem uygun hata mesajları döndürecek
**Doğrular: Gereksinimler 3.3, 3.4**

**Özellik 6: Retry Mekanizması**
*Herhangi bir* başarısız etiket oluşturma işlemi için, sistem durumu HATA olarak işaretleyecek, bekleyen etiketleri yeniden deneyecek, deneme sayısını artıracak ve maksimum denemeye ulaşıldığında işlemi durduracak
**Doğrular: Gereksinimler 4.1, 4.2, 4.3, 4.4, 4.5**

**Özellik 7: Taşıyıcı Arayüz Uyumluluğu**
*Herhangi bir* taşıyıcı implementasyonu için, sistem standart arayüzü sağlayacak, uygun carrier döndürecek, standart veri formatı kullanacak ve hataları EntegrasyonHatasi olarak ele alacak
**Doğrular: Gereksinimler 5.1, 5.2, 5.3, 5.4, 5.5**

**Özellik 8: Zaman Damgası Yönetimi**
*Herhangi bir* etiket kaydı, durum güncellemesi veya takip kaydı işleminde, sistem uygun zaman damgalarını kayıt edecek
**Doğrular: Gereksinimler 6.1, 6.2, 6.3**

**Özellik 9: Sorgulama İşlemleri**
*Herhangi bir* kaynak bazlı veya durum bazlı sorgulama işleminde, sistem ilgili kayıtları doğru şekilde döndürecek
**Doğrular: Gereksinimler 6.4, 6.5**

**Özellik 10: Transaction Yönetimi**
*Herhangi bir* etiket işlemi için, sistem transaction kullanacak, foreign key kısıtlamalarını kontrol edecek, benzersizlik ihlallerinde hata verecek ve sistem hatalarında rollback yapacak
**Doğrular: Gereksinimler 7.1, 7.2, 7.3, 7.5**

**Özellik 11: Eş Zamanlı Erişim Güvenliği**
*Herhangi bir* eş zamanlı erişim durumunda, sistem veri tutarlılığını koruyacak
**Doğrular: Gereksinimler 7.4**

**Özellik 12: Performans Optimizasyonu**
*Herhangi bir* takip numarası, durum veya kaynak bazlı arama işleminde, sistem uygun indexleri kullanacak ve optimize edilmiş sorgular çalıştıracak
**Doğrular: Gereksinimler 8.1, 8.2, 8.3**

**Özellik 13: Büyük Veri Yönetimi**
*Herhangi bir* büyük veri seti işleminde, sistem sayfalama desteği sağlayacak ve sık kullanılan sorgular için performans optimizasyonu uygulayacak
**Doğrular: Gereksinimler 8.4, 8.5**

## Hata Yönetimi

### Hata Türleri

1. **DogrulamaHatasi**: Geçersiz giriş verileri
2. **EntegrasyonHatasi**: Taşıyıcı API hataları  
3. **VeriTabaniHatasi**: Veritabanı kısıtlama ihlalleri
4. **BenzersizlikHatasi**: Duplicate etiket oluşturma denemeleri

### Hata Yönetim Stratejisi

- Tüm hatalar uygun exception türleri ile ele alınır
- Hata mesajları kullanıcı dostu ve bilgilendirici olur
- Kritik hatalar log'a kaydedilir
- Transaction hataları otomatik rollback yapar

## Test Stratejisi

### İkili Test Yaklaşımı

**Unit Testler**: Spesifik örnekler, edge case'ler ve hata durumları
- Geçersiz veri ile etiket oluşturma denemeleri
- Benzersizlik kısıtlama testleri
- Hata senaryoları ve exception handling

**Property-Based Testler**: Evrensel özellikler (minimum 100 iterasyon)
- Hypothesis kütüphanesi kullanılacak
- Her property test, tasarım belgesindeki ilgili özelliği implement edecek
- Test etiketleme formatı: '**Feature: kargo-entegrasyon-altyapisi, Property {number}: {property_text}**'
- Rastgele veri üretimi ile kapsamlı test coverage

### Test Konfigürasyonu

- Property testler minimum 100 iterasyon çalıştırılacak
- Her correctness property tek bir property-based test ile implement edilecek
- Test verileri gerçek senaryoları simüle edecek şekilde üretilecek
