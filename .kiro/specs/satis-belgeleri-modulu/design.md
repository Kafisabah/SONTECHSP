# Satış Belgeleri Modülü - Tasarım Belgesi

## Genel Bakış

Satış Belgeleri Modülü, SONTECHSP POS + ERP + CRM sisteminin sipariş, irsaliye ve fatura belgelerini yöneten kritik bir bileşenidir. Bu modül, belge yaşam döngüsü boyunca durum yönetimi, numara üretimi, veri tutarlılığı ve entegrasyon hazırlığı sağlar.

Modül, mevcut POS sistemi ile entegre çalışarak satış işlemlerinden belge üretimi yaparken, gelecekte e-belge ve kargo entegrasyonları için temel altyapıyı oluşturur.

## Mimari

### Katmanlı Yapı

```
UI Katmanı (PyQt6)
    ↓
Servis Katmanı (İş Kuralları)
    ↓
Repository Katmanı (Veri Erişimi)
    ↓
Veritabanı Katmanı (PostgreSQL)
```

### Modül Yapısı

```
sontechsp/uygulama/moduller/satis_belgeleri/
├── servisler/
│   ├── belge_servisi.py          # Ana belge işlemleri
│   ├── durum_akis_servisi.py     # Durum geçiş yönetimi
│   ├── numara_servisi.py         # Belge numarası üretimi
│   └── dogrulama_servisi.py      # Veri doğrulama
├── depolar/
│   ├── belge_deposu.py           # Belge CRUD işlemleri
│   ├── belge_satir_deposu.py     # Belge satır işlemleri
│   └── numara_sayac_deposu.py    # Numara sayacı işlemleri
├── modeller/
│   ├── satis_belgesi.py          # Ana belge modeli
│   ├── belge_satiri.py           # Belge satır modeli
│   ├── belge_durumu.py           # Durum modeli
│   └── numara_sayaci.py          # Numara sayacı modeli
└── dto/
    ├── belge_dto.py              # Belge veri transfer nesnesi
    ├── belge_satir_dto.py        # Belge satır DTO
    └── belge_ozet_dto.py         # Belge özet DTO
```

## Bileşenler ve Arayüzler

### Ana Servisler

#### BelgeServisi
- **Sorumluluk**: Belge yaşam döngüsü yönetimi
- **Ana Metodlar**:
  - `siparis_olustur(siparis_bilgileri: SiparisBilgileriDTO) -> BelgeDTO`
  - `irsaliye_olustur(siparis_id: int) -> BelgeDTO`
  - `fatura_olustur(kaynak_belge_id: int, kaynak_tip: str) -> BelgeDTO`
  - `belge_sil(belge_id: int) -> bool`

#### DurumAkisServisi
- **Sorumluluk**: Belge durum geçişlerini yönetir
- **Ana Metodlar**:
  - `durum_guncelle(belge_id: int, yeni_durum: BelgeDurumu) -> bool`
  - `gecerli_gecisler(mevcut_durum: BelgeDurumu) -> List[BelgeDurumu]`
  - `durum_gecmisi(belge_id: int) -> List[DurumGecmisiDTO]`

#### NumaraServisi
- **Sorumluluk**: Benzersiz belge numarası üretimi
- **Ana Metodlar**:
  - `numara_uret(magaza_id: int, belge_turu: BelgeTuru) -> str`
  - `numara_rezerve_et(magaza_id: int, belge_turu: BelgeTuru) -> str`

### Repository Arayüzleri

#### IBelgeDeposu
```python
from abc import ABC, abstractmethod
from typing import List, Optional

class IBelgeDeposu(ABC):
    @abstractmethod
    def ekle(self, belge: SatisBelgesi) -> SatisBelgesi:
        pass
    
    @abstractmethod
    def guncelle(self, belge: SatisBelgesi) -> SatisBelgesi:
        pass
    
    @abstractmethod
    def bul(self, belge_id: int) -> Optional[SatisBelgesi]:
        pass
    
    @abstractmethod
    def listele(self, filtre: BelgeFiltresiDTO) -> List[SatisBelgesi]:
        pass
```

## Veri Modelleri

### SatisBelgesi (Ana Tablo: satis_belgeleri)

```python
class SatisBelgesi(Base):
    __tablename__ = 'satis_belgeleri'
    
    id: int                           # Primary key
    belge_numarasi: str              # Benzersiz belge numarası
    belge_turu: BelgeTuru            # SIPARIS, IRSALIYE, FATURA
    belge_durumu: BelgeDurumu        # TASLAK, ONAYLANDI, FATURALANDI, IPTAL
    magaza_id: int                   # Mağaza referansı
    musteri_id: Optional[int]        # Müşteri referansı
    toplam_tutar: Decimal            # Toplam tutar
    kdv_tutari: Decimal              # KDV tutarı
    genel_toplam: Decimal            # Genel toplam
    olusturma_tarihi: datetime       # Oluşturma zamanı
    guncelleme_tarihi: datetime      # Son güncelleme zamanı
    olusturan_kullanici_id: int      # Oluşturan kullanıcı
    kaynak_belge_id: Optional[int]   # Kaynak belge referansı
    kaynak_belge_turu: Optional[str] # Kaynak belge türü
    iptal_nedeni: Optional[str]      # İptal nedeni
```

### BelgeSatiri (Tablo: belge_satirlari)

```python
class BelgeSatiri(Base):
    __tablename__ = 'belge_satirlari'
    
    id: int                    # Primary key
    belge_id: int             # Belge referansı
    urun_id: int              # Ürün referansı
    miktar: Decimal           # Miktar
    birim_fiyat: Decimal      # Birim fiyat
    kdv_orani: Decimal        # KDV oranı
    satir_tutari: Decimal     # Satır tutarı
    kdv_tutari: Decimal       # Satır KDV tutarı
    satir_toplami: Decimal    # Satır toplamı
    sira_no: int              # Satır sıra numarası
```

### NumaraSayaci (Tablo: numara_sayaclari)

```python
class NumaraSayaci(Base):
    __tablename__ = 'numara_sayaclari'
    
    id: int                   # Primary key
    magaza_id: int           # Mağaza ID
    belge_turu: BelgeTuru    # Belge türü
    yil: int                 # Yıl
    ay: int                  # Ay
    son_numara: int          # Son kullanılan numara
    guncelleme_tarihi: datetime # Son güncelleme
```

### Enum Tanımları

```python
class BelgeTuru(Enum):
    SIPARIS = "SIPARIS"
    IRSALIYE = "IRSALIYE"
    FATURA = "FATURA"

class BelgeDurumu(Enum):
    TASLAK = "TASLAK"
    ONAYLANDI = "ONAYLANDI"
    FATURALANDI = "FATURALANDI"
    IPTAL = "IPTAL"
```

## Doğruluk Özellikleri

*Bir özellik, sistemin tüm geçerli yürütmelerinde doğru olması gereken bir karakteristik veya davranıştır - esasen, sistemin ne yapması gerektiği hakkında resmi bir ifadedir. Özellikler, insan tarafından okunabilir spesifikasyonlar ile makine tarafından doğrulanabilir doğruluk garantileri arasında köprü görevi görür.*

### Property 1: Sipariş oluşturma tutarlılığı
*Herhangi bir* geçerli sipariş bilgisi için, sipariş oluşturma işlemi başarılı olduğunda belge TASLAK durumunda kaydedilmeli ve benzersiz numara atanmalıdır
**Validates: Requirements 1.1, 1.2**

### Property 2: Belge satır tutarlılığı
*Herhangi bir* belge satırı eklendiğinde, ürün bilgileri doğrulanmalı ve toplam tutarlar doğru hesaplanmalıdır
**Validates: Requirements 1.3**

### Property 3: Transaction bütünlüğü
*Herhangi bir* belge işlemi için, tüm veritabanı değişiklikleri transaction içinde gerçekleştirilmeli ve hata durumunda geri alınmalıdır
**Validates: Requirements 1.4, 1.5**

### Property 4: Durum tabanlı belge oluşturma
*Herhangi bir* ONAYLANDI durumundaki sipariş için irsaliye oluşturulabilmeli, TASLAK durumundaki siparişler için reddedilmelidir
**Validates: Requirements 2.1, 2.4**

### Property 5: Belge numarası benzersizliği
*Herhangi bir* belge türü ve mağaza kombinasyonu için üretilen numara benzersiz olmalı ve format kurallarına uymalıdır
**Validates: Requirements 2.2, 4.1, 4.2**

### Property 6: Durum güncelleme tutarlılığı
*Herhangi bir* başarılı belge oluşturma işlemi sonrasında kaynak belgenin durumu uygun şekilde güncellenmelidir
**Validates: Requirements 2.3, 3.4**

### Property 7: Fatura oluşturma tutarlılığı
*Herhangi bir* onaylanmış sipariş veya POS satışı için fatura oluşturulabilmeli ve KDV hesaplamaları doğru yapılmalıdır
**Validates: Requirements 3.1, 3.2, 3.3**

### Property 8: Hata durumu yönetimi
*Herhangi bir* belge oluşturma hatası durumunda tüm değişiklikler geri alınmalı ve hata mesajı dönülmelidir
**Validates: Requirements 3.5**

### Property 9: Ay değişimi numara sıfırlama
*Herhangi bir* ay değişimi durumunda, aynı mağaza ve belge türü için sıra numarası sıfırdan başlatılmalıdır
**Validates: Requirements 4.3**

### Property 10: Numara çakışması çözümü
*Herhangi bir* numara çakışması durumunda sistem işlemi tekrar denemeli ve benzersizliği garanti etmelidir
**Validates: Requirements 4.4**

### Property 11: Durum geçiş kontrolü
*Herhangi bir* durum güncelleme işlemi için geçiş kuralları kontrol edilmeli ve geçersiz geçişler reddedilmelidir
**Validates: Requirements 5.1, 5.3**

### Property 12: Geçerli durum geçişi
*Herhangi bir* geçerli durum geçişi için belge durumu güncellenmeli ve zaman damgası eklenmelidir
**Validates: Requirements 5.2**

### Property 13: İptal durumu yönetimi
*Herhangi bir* belge iptal edildiğinde iptal nedeni kaydedilmeli ve sonraki durum geçişleri reddedilmelidir
**Validates: Requirements 5.4, 5.5**

### Property 14: Veri doğrulama tutarlılığı
*Herhangi bir* belge satırı için ürün bilgileri doğrulanmalı ve toplam tutarlar satır toplamları ile uyumlu olmalıdır
**Validates: Requirements 6.2, 6.3**

### Property 15: Silme işlemi kontrolü
*Herhangi bir* belge silme işlemi için bağımlı kayıtlar kontrol edilmeli ve uygun işlem yapılmalıdır
**Validates: Requirements 6.4**

### Property 16: Eş zamanlı erişim kontrolü
*Herhangi bir* eş zamanlı belge işlemi için row-level lock kullanılarak veri tutarlılığı korunmalıdır
**Validates: Requirements 6.5**

### Property 17: DTO format tutarlılığı
*Herhangi bir* belge sorgusu için veriler DTO formatında dönülmeli ve durum bilgileri zaman damgası ile birlikte sağlanmalıdır
**Validates: Requirements 7.1, 7.2**

### Property 18: Liste sorgu desteği
*Herhangi bir* belge listesi sorgusu için filtreleme ve sayfalama desteği sağlanmalıdır
**Validates: Requirements 7.3**

### Property 19: Geçmiş sorgu tutarlılığı
*Herhangi bir* belge geçmiş sorgusu için durum değişiklik geçmişi tam olarak dönülmelidir
**Validates: Requirements 7.4**

## Hata Yönetimi

### Hata Türleri

1. **Doğrulama Hataları**
   - Geçersiz belge bilgileri
   - Eksik zorunlu alanlar
   - Format hataları

2. **İş Kuralı Hataları**
   - Geçersiz durum geçişleri
   - Yetkisiz işlemler
   - Stok yetersizliği

3. **Sistem Hataları**
   - Veritabanı bağlantı hataları
   - Transaction hataları
   - Eş zamanlı erişim çakışmaları

### Hata Yönetim Stratejisi

- Tüm hatalar merkezi hata yönetim sistemi üzerinden loglanır
- Kullanıcı dostu hata mesajları döndürülür
- Kritik hatalar sistem yöneticisine bildirilir
- Transaction rollback otomatik gerçekleştirilir

## Test Stratejisi

### İkili Test Yaklaşımı

Modül hem birim testleri hem de özellik tabanlı testlerle kapsamlı şekilde test edilecektir:

**Birim Testleri**:
- Spesifik örnekleri doğrular
- Entegrasyon noktalarını test eder
- Kenar durumları ve hata koşullarını kapsar

**Özellik Tabanlı Testler**:
- Evrensel özellikleri tüm girdi alanında doğrular
- Hypothesis kütüphanesi kullanılacak
- Her test minimum 100 iterasyon çalıştırılacak
- Her özellik tabanlı test, tasarım belgesindeki doğruluk özelliğini referans alacak
- Test etiketleme formatı: '**Feature: satis-belgeleri-modulu, Property {numara}: {özellik_metni}**'

**Test Kapsamı**:
- Belge yaşam döngüsü testleri
- Durum geçiş testleri
- Numara üretimi testleri
- Veri tutarlılığı testleri
- Eş zamanlı erişim testleri
- Hata durumu testleri

**Test Araçları**:
- Pytest (birim testler)
- Hypothesis (özellik tabanlı testler)
- SQLAlchemy test fixtures
- Transaction rollback testleri