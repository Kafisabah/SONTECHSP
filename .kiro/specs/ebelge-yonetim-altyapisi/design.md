# E-Belge Yönetim Altyapısı Tasarım Dokümanı

## Genel Bakış

E-Belge Yönetim Altyapısı, SONTECHSP projesi için yasal geçerliliği olan belgelerin (e-Fatura, e-Arşiv, e-İrsaliye) oluşturulması ve entegratörlere iletilmesini yöneten merkezi bir modüldür. Sistem, Outbox Pattern kullanarak güvenilir mesaj iletimi sağlar ve Provider-Agnostic yaklaşımla farklı entegratör sağlayıcılarına kolayca geçiş imkanı sunar.

Temel özellikler:
- Outbox Pattern ile güvenilir mesaj kuyruğu
- Provider-Agnostic entegratör desteği
- Idempotency kontrolü ile mükerrer belge önleme
- Comprehensive audit logging
- Automatic retry mechanism
- Asenkron işlem desteği

## Mimari

### Katman Yapısı

```
┌─────────────────────────────────────────────────────────────┐
│                    Dış Sistemler                           │
│              (POS, Satış Belgeleri, vb.)                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 Servis Katmanı                             │
│              (EBelgeServisi)                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│               Repository Katmanı                           │
│              (EBelgeDeposu)                                │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│               Veritabanı Katmanı                           │
│        (ebelge_cikis_kuyrugu, ebelge_durumlari)           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Entegratör Katmanı                            │
│    ┌─────────────────┐    ┌─────────────────────────────┐   │
│    │ SaglayiciArayuzu│    │   SaglayiciFabrikasi        │   │
│    │   (Abstract)    │    │                             │   │
│    └─────────────────┘    └─────────────────────────────┘   │
│              │                          │                  │
│    ┌─────────▼─────────┐    ┌──────────▼──────────────┐   │
│    │  DummySaglayici   │    │  UyumsoftSaglayici      │   │
│    │   (Test/Dev)      │    │    (Production)         │   │
│    └───────────────────┘    └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Veri Akışı

1. **Belge Oluşturma**: Dış sistem (POS/Satış) EBelgeServisi.cikis_olustur() çağırır
2. **Kuyruk Kaydı**: Belge bilgileri ebelge_cikis_kuyrugu tablosuna BEKLIYOR durumunda kaydedilir
3. **Asenkron Gönderim**: EBelgeServisi.bekleyenleri_gonder() periyodik olarak çalışır
4. **Entegratör İletişimi**: SaglayiciFabrikasi üzerinden uygun sağlayıcı seçilir ve belge gönderilir
5. **Durum Güncelleme**: Gönderim sonucuna göre durum güncellenir ve audit log kaydedilir

## Bileşenler ve Arayüzler

### DTO Sınıfları

**EBelgeOlusturDTO**
```python
@dataclass
class EBelgeOlusturDTO:
    kaynak_turu: str          # POS_SATIS, SATIS_BELGESI, IADE_BELGESI
    kaynak_id: int            # Kaynak sistemdeki belge ID'si
    belge_turu: str           # EFATURA, EARSIV, EIRSALIYE
    musteri_ad: str           # Müşteri adı
    vergi_no: str             # Müşteri vergi/TC numarası
    toplam_tutar: Decimal     # Belge toplam tutarı
    para_birimi: str = "TRY"  # Para birimi
    belge_json: dict          # Belge detay verileri
    aciklama: Optional[str] = None  # İsteğe bağlı açıklama
```

**EBelgeGonderDTO**
```python
@dataclass
class EBelgeGonderDTO:
    cikis_id: int            # Kuyruk kaydı ID'si
    belge_json: dict         # Entegratöre gönderilecek JSON verisi
```

**EBelgeSonucDTO**
```python
@dataclass
class EBelgeSonucDTO:
    basarili_mi: bool                    # İşlem başarı durumu
    dis_belge_no: Optional[str] = None   # Entegratörden alınan belge numarası
    durum_kodu: Optional[str] = None     # Entegratör durum kodu
    mesaj: Optional[str] = None          # Hata/başarı mesajı
    ham_cevap_json: Optional[dict] = None # Entegratörden gelen ham cevap
```

### Servis Arayüzleri

**SaglayiciArayuzu (Abstract Base Class)**
```python
class SaglayiciArayuzu(ABC):
    @abstractmethod
    def gonder(self, dto: EBelgeGonderDTO) -> EBelgeSonucDTO:
        """Belgeyi entegratöre gönderir"""
        pass
    
    @abstractmethod
    def durum_sorgula(self, dis_belge_no: str) -> EBelgeSonucDTO:
        """Belge durumunu entegratörden sorgular"""
        pass
```

**EBelgeServisi**
```python
class EBelgeServisi:
    def cikis_olustur(self, dto: EBelgeOlusturDTO) -> int:
        """Yeni e-belge çıkış kaydı oluşturur"""
        
    def bekleyenleri_gonder(self, limit: int = 10) -> List[int]:
        """Bekleyen belgeleri entegratöre gönderir"""
        
    def durum_sorgula(self, cikis_id: int) -> EBelgeSonucDTO:
        """Belge durumunu sorgular ve günceller"""
```

## Veri Modelleri

### ebelge_cikis_kuyrugu Tablosu

| Alan | Tür | Açıklama | Kısıtlamalar |
|------|-----|----------|--------------|
| id | Integer | Primary Key | AUTO_INCREMENT |
| kaynak_turu | String(50) | Kaynak sistem türü | NOT NULL |
| kaynak_id | Integer | Kaynak sistem ID'si | NOT NULL |
| belge_turu | String(20) | E-belge türü | NOT NULL |
| musteri_ad | String(200) | Müşteri adı | NOT NULL |
| vergi_no | String(20) | Vergi/TC numarası | NOT NULL |
| toplam_tutar | Decimal(15,2) | Belge tutarı | NOT NULL |
| para_birimi | String(3) | Para birimi | DEFAULT 'TRY' |
| belge_json | Text | JSON belge verisi | NOT NULL |
| durum | String(20) | Kayıt durumu | NOT NULL, INDEX |
| mesaj | Text | Durum mesajı | NULL |
| dis_belge_no | String(100) | Dış belge numarası | NULL |
| deneme_sayisi | Integer | Retry sayacı | DEFAULT 0 |
| aciklama | Text | Açıklama | NULL |
| olusturulma_zamani | DateTime | Oluşturma zamanı | NOT NULL |
| guncellenme_zamani | DateTime | Güncelleme zamanı | NOT NULL |

**Unique Constraint**: (kaynak_turu, kaynak_id, belge_turu)

### ebelge_durumlari Tablosu (Audit Log)

| Alan | Tür | Açıklama | Kısıtlamalar |
|------|-----|----------|--------------|
| id | Integer | Primary Key | AUTO_INCREMENT |
| cikis_id | Integer | Kuyruk kaydı referansı | NOT NULL, FK |
| durum | String(20) | Durum değeri | NOT NULL |
| mesaj | Text | Durum mesajı | NULL |
| olusturulma_zamani | DateTime | Kayıt zamanı | NOT NULL |
## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: E-belge oluşturma validation
*For any* e-belge oluşturma isteği, kaynak türü, kaynak ID, belge türü, müşteri adı ve vergi numarası alanları zorunlu olmalı ve geçerli değerler içermeli
**Validates: Requirements 1.1, 1.2, 1.3**

### Property 2: JSON veri bütünlüğü (Round-trip)
*For any* geçerli belge JSON verisi, kaydedilip okunduğunda orijinal yapısını korumalı
**Validates: Requirements 1.4, 14.1, 14.2**

### Property 3: Varsayılan değer atama
*For any* e-belge oluşturma isteği, para birimi belirtilmediğinde varsayılan olarak "TRY" değeri atanmalı
**Validates: Requirements 1.5**

### Property 4: Idempotency kontrolü
*For any* kaynak türü, kaynak ID ve belge türü kombinasyonu, ikinci kez aynı kombinasyonla istek yapıldığında EntegrasyonHatasi fırlatılmalı
**Validates: Requirements 2.1, 2.3**

### Property 5: Farklı belge türü desteği
*For any* kaynak, farklı belge türleri ile ayrı kayıtlar oluşturulabilmeli
**Validates: Requirements 2.2**

### Property 6: Bekleyen belge filtreleme
*For any* belge durumu sorgusu, sadece BEKLIYOR durumundaki veya (HATA durumunda ve deneme sayısı maksimumdan az olan) kayıtlar döndürülmeli
**Validates: Requirements 3.1, 3.2**

### Property 7: Durum güncelleme atomikliği
*For any* gönderim işlemi, kayıt durumu GONDERILIYOR olarak güncellenmeli ve işlem sonucuna göre GONDERILDI veya HATA durumuna geçmeli
**Validates: Requirements 3.3, 5.1, 5.3**

### Property 8: Sayfalama kontrolü
*For any* limit parametresi, belirtilen sayıda kayıt döndürülmeli ve limit aşılmamalı
**Validates: Requirements 3.4**

### Property 9: Sağlayıcı interface uyumluluğu
*For any* sağlayıcı implementasyonu, EBelgeGonderDTO kabul etmeli ve EBelgeSonucDTO döndürmeli
**Validates: Requirements 4.1, 4.2, 4.3**

### Property 10: Dış belge numarası iletimi
*For any* başarılı gönderim, dış belge numarası sonuçta iletilmeli ve veritabanına kaydedilmeli
**Validates: Requirements 4.4, 5.2**

### Property 11: Retry mekanizması
*For any* başarısız gönderim, deneme sayısı artırılmalı ve maksimum deneme sayısına ulaşıldığında kalıcı hata durumuna geçilmeli
**Validates: Requirements 5.4, 10.1, 10.2, 10.3**

### Property 12: Hata mesajı yönetimi
*For any* hata durumu, hata mesajı kaydedilmeli ve durum geçmişine eklenmelidir
**Validates: Requirements 5.5, 7.3**

### Property 13: Durum sorgulama
*For any* geçerli çıkış ID, güncel durum bilgisi döndürülmeli ve dış belge numarası varsa entegratörden sorgulanmalı
**Validates: Requirements 6.1, 6.2, 6.3**

### Property 14: Audit logging
*For any* durum değişikliği, durum geçmişi tablosuna otomatik zaman damgası ile kayıt eklenmelidir
**Validates: Requirements 7.1, 7.2**

### Property 15: Durum geçmişi sıralama
*For any* durum geçmişi sorgusu, kayıtlar kronolojik sırada listelenmeli
**Validates: Requirements 7.4**

### Property 16: Sağlayıcı fabrikası
*For any* konfigürasyon, uygun sağlayıcı implementasyonu döndürülmeli ve geçersiz konfigürasyonda hata fırlatılmalı
**Validates: Requirements 8.1, 8.2, 8.5**

### Property 17: DummySaglayici davranışı
*For any* DummySaglayici kullanımı, gerçek API çağrısı yapılmamalı ve konfigürasyona göre simülasyon davranışı sergilenmelidir
**Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**

### Property 18: Transaction yönetimi
*For any* e-belge işlemi, transaction kullanılmalı ve hata durumunda rollback yapılmalı
**Validates: Requirements 11.1, 11.2, 11.4**

### Property 19: Logging davranışı
*For any* e-belge işlemi, başlangıç, başarı ve hata durumları loglanmalı
**Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5**

### Property 20: JSON validation
*For any* bozuk JSON verisi, doğrulama hatası fırlatılmalı ve encoding sorunları önlenmelidir
**Validates: Requirements 14.4, 14.5**

### Property 21: Durum sorgulama interface
*For any* durum sorgulama isteği, dış belge numarası parametre olarak kabul edilmeli ve uygun sonuç döndürülmelidir
**Validates: Requirements 15.1, 15.2**

## Hata Yönetimi

### Hata Türleri

**EntegrasyonHatasi**
- Mükerrer belge oluşturma girişimi
- Geçersiz belge türü
- Zorunlu alan eksikliği
- JSON format hatası

**BaglantiHatasi**
- Entegratör erişim sorunu
- Network timeout
- API rate limit aşımı

**DogrulamaHatasi**
- Geçersiz çıkış ID
- Belge bulunamadı
- Konfigürasyon hatası

### Hata Yönetim Stratejisi

1. **Graceful Degradation**: Entegratör erişilemediğinde sistem çalışmaya devam eder
2. **Retry Mechanism**: Geçici hatalar için otomatik tekrar deneme
3. **Circuit Breaker**: Sürekli başarısız olan entegratörler için devre kesici
4. **Comprehensive Logging**: Tüm hatalar detaylı şekilde loglanır
5. **User-Friendly Messages**: Kullanıcıya anlaşılır hata mesajları

## Test Stratejisi

### Unit Testing Yaklaşımı

Unit testler şu alanları kapsar:
- DTO validation kuralları
- Servis metotlarının temel işlevselliği
- Repository CRUD operasyonları
- Hata durumları ve exception handling
- Sağlayıcı fabrikası logic

### Property-Based Testing Yaklaşımı

Property-based testler için **Hypothesis** kütüphanesi kullanılacak. Her property-based test minimum 100 iterasyon çalıştırılacak.

Property testler şu alanları kapsar:
- E-belge oluşturma validation kuralları (Property 1, 3)
- JSON round-trip bütünlüğü (Property 2)
- Idempotency kontrolü (Property 4, 5)
- Durum yönetimi ve geçişleri (Property 6, 7, 11)
- Sağlayıcı interface uyumluluğu (Property 9, 10)
- Audit logging tutarlılığı (Property 14, 15)
- Transaction atomikliği (Property 18)

Her property-based test, tasarım dokümanındaki ilgili correctness property'yi referans alacak ve şu format ile etiketlenecek:
`**Feature: ebelge-yonetim-altyapisi, Property {number}: {property_text}**`

### Test Veri Üretimi

Property-based testler için akıllı veri üreticileri:
- Geçerli/geçersiz kaynak türleri
- Geçerli/geçersiz belge türleri  
- Rastgele JSON yapıları
- Farklı durum kombinasyonları
- Çeşitli hata senaryoları