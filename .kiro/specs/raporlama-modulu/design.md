# Tasarım Dokümanı

## Genel Bakış

Raporlama modülü, SONTECHSP sisteminin analitik ihtiyaçlarını karşılamak için tasarlanmış bir modüldür. Modül, satış performansı, stok durumu, ürün analizleri ve karlılık raporları üretir. Clean Architecture prensiplerine uygun olarak, UI katmanından tamamen bağımsız çalışır ve optimize edilmiş veritabanı sorguları kullanır.

## Mimari

Modül üç ana katmandan oluşur:

1. **DTO Katmanı**: Veri transfer nesneleri ve sabitler
2. **Servis Katmanı**: İş mantığı ve koordinasyon
3. **Sorgu Katmanı**: Optimize edilmiş veritabanı sorguları
4. **Dışa Aktarım Katmanı**: CSV/PDF export işlemleri

```
┌─────────────────┐
│   UI Layer      │ (Bu modülde YOK)
└─────────────────┘
         │
┌─────────────────┐
│ Service Layer   │ (RaporServisi)
└─────────────────┘
         │
┌─────────────────┐    ┌─────────────────┐
│ Query Layer     │    │ Export Layer    │
│ (sorgular.py)   │    │ (disari_aktarim)│
└─────────────────┘    └─────────────────┘
         │                       │
┌─────────────────┐    ┌─────────────────┐
│   Database      │    │  File System    │
└─────────────────┘    └─────────────────┘
```

## Bileşenler ve Arayüzler

### DTO Bileşenleri

**TarihAraligiDTO**
```python
@dataclass
class TarihAraligiDTO:
    baslangic_tarihi: date
    bitis_tarihi: date
```

**SatisOzetiDTO**
```python
@dataclass
class SatisOzetiDTO:
    magaza_id: int
    brut_satis: Decimal
    indirim_toplam: Decimal
    net_satis: Decimal
    satis_adedi: int
    iade_toplam: Decimal = Decimal('0')
```

**UrunPerformansDTO**
```python
@dataclass
class UrunPerformansDTO:
    urun_id: int
    urun_adi: str
    miktar_toplam: int
    ciro_toplam: Decimal
```

**KritikStokDTO**
```python
@dataclass
class KritikStokDTO:
    urun_id: int
    urun_adi: str
    depo_id: int
    miktar: int
    kritik_seviye: int
```

### Servis Arayüzü

**RaporServisi**
```python
class RaporServisi:
    def satis_ozeti_al(self, magaza_id: int, tarih_araligi: TarihAraligiDTO) -> SatisOzetiDTO
    def kritik_stok_al(self, depo_id: Optional[int] = None) -> List[KritikStokDTO]
    def en_cok_satan_al(self, magaza_id: int, tarih_araligi: TarihAraligiDTO, limit: int = 20) -> List[UrunPerformansDTO]
    def karlilik_al(self, magaza_id: int, tarih_araligi: TarihAraligiDTO) -> List[RaporSatirDTO]
    def disari_aktar(self, rapor_turu: str, veri: Any, disari_aktar_dto: DisariAktarDTO) -> str
```

### Sorgu Katmanı Arayüzü

**Sorgular**
```python
def satis_ozeti(session: Session, magaza_id: int, tarih_araligi: TarihAraligiDTO) -> Dict
def kritik_stok_listesi(session: Session, depo_id: Optional[int] = None) -> List[Dict]
def en_cok_satan_urunler(session: Session, magaza_id: int, tarih_araligi: TarihAraligiDTO, limit: int = 20) -> List[Dict]
def karlilik_ozeti(session: Session, magaza_id: int, tarih_araligi: TarihAraligiDTO) -> List[Dict]
```

## Veri Modelleri

Mevcut modelleri kullanır:
- `pos_satislar` (satış belgeleri)
- `pos_satis_satirlari` (satış satırları)
- `urunler` (ürün bilgileri)
- `stok_bakiyeleri` (stok durumu)
- `depolar` (depo bilgileri)

Yeni model (opsiyonel):
```python
class RaporArsivi(Base):
    __tablename__ = 'rapor_arsivi'
    
    id = Column(Integer, primary_key=True)
    rapor_turu = Column(String(50), nullable=False)
    parametre_json = Column(Text)
    dosya_yolu = Column(String(500))
    olusturulma_zamani = Column(DateTime, default=datetime.utcnow)
```

## Hata Yönetimi

### Hata Türleri

1. **VeriTabaniHatasi**: Veritabanı bağlantı ve sorgu hataları
2. **DosyaIslemHatasi**: Export işlemlerinde dosya sistemi hataları
3. **ParametreHatasi**: Geçersiz parametre değerleri
4. **VeriYokHatasi**: Rapor için veri bulunamadığında

### Hata Yönetimi Stratejisi

- Tüm servis metodları try-catch blokları kullanır
- Hatalar uygun exception türleriyle fırlatılır
- Kritik hatalar log'a kaydedilir
- Kullanıcı dostu hata mesajları döndürülür

## Test Stratejisi

### Birim Testleri

- Her DTO sınıfı için veri doğrulama testleri
- Servis metodları için mock veritabanı testleri
- Export fonksiyonları için dosya oluşturma testleri
- Hata senaryoları için exception testleri

### Özellik Tabanlı Testler

Doğruluk Özellikleri bölümünde tanımlanacak özellikler için property-based testler yazılacak. Python'da Hypothesis kütüphanesi kullanılacak, her test minimum 100 iterasyon çalışacak.

### Entegrasyon Testleri

- Gerçek veritabanı ile sorgu testleri
- CSV/PDF dosya oluşturma testleri
- Performans testleri (büyük veri setleri)

## Doğruluk Özellikleri

*Bir özellik, sistemin tüm geçerli yürütmelerinde doğru olması gereken bir karakteristik veya davranıştır - esasen sistemin ne yapması gerektiği hakkında resmi bir ifadedir. Özellikler, insan tarafından okunabilir spesifikasyonlar ile makine tarafından doğrulanabilir doğruluk garantileri arasında köprü görevi görür.*

**Özellik 1: Satış özeti tamlığı**
*Herhangi bir* geçerli mağaza ID'si ve tarih aralığı için, satış özeti tüm gerekli alanları (brüt satış, indirimler, net satış, satış sayısı, iadeler) null olmayan değerlerle içermelidir
**Doğrular: Gereksinim 1.1**

**Özellik 2: Satış durumu filtreleme**
*Herhangi bir* satış özeti hesaplamasında, yalnızca TAMAMLANDI durumundaki işlemler toplamaya dahil edilmelidir
**Doğrular: Gereksinim 1.2**

**Özellik 3: Satış toplama doğruluğu**
*Herhangi bir* mağaza bazında gruplandırılmış satış verisi seti için, bireysel işlem tutarlarının toplamı toplam tutara eşit olmalıdır
**Doğrular: Gereksinim 1.4**

**Özellik 4: İade tutarı dahil etme**
*Herhangi bir* iade içeren satış özeti için, iade tutarları uygun toplamlardan düzgün şekilde çıkarılmalı veya eklenmelidir
**Doğrular: Gereksinim 1.5**

**Özellik 5: Kritik stok filtreleme**
*Herhangi bir* ürün ve stok verisi için, kritik stok raporunda döndürülen ürünlerin mevcut stoğu kritik eşikte veya altında olmalıdır
**Doğrular: Gereksinim 2.1**

**Özellik 6: Stok verisi bütünlüğü**
*Herhangi bir* kritik stok raporu sonucu için, döndürülen her kayıt düzgün tablo birleştirmelerinden geçerli ürün ve stok bakiye verilerine sahip olmalıdır
**Doğrular: Gereksinim 2.2**

**Özellik 7: Depo filtreleme**
*Herhangi bir* depo ID parametresi için, kritik stok sonuçları yalnızca o belirli depodan ürünleri içermelidir
**Doğrular: Gereksinim 2.4**

**Özellik 8: Kritik stok alan tamlığı**
*Herhangi bir* kritik stok raporu girişi için, tüm gerekli alanlar (ürün ID, ad, depo ID, mevcut miktar, kritik seviye) mevcut olmalıdır
**Doğrular: Gereksinim 2.5**

**Özellik 9: En iyi ürün sıralaması**
*Herhangi bir* en çok satan ürünler raporu için, sonuçlar toplam satılan miktara göre azalan sırada düzenlenmeli
**Doğrular: Gereksinim 3.1**

**Özellik 10: Ürün satış toplamı**
*Herhangi bir* en çok satan rapordaki ürün için, toplam miktar o ürün için tüm bireysel satış miktarlarının toplamına eşit olmalıdır
**Doğrular: Gereksinim 3.2**

**Özellik 11: Limit parametresi saygısı**
*Herhangi bir* geçerli limit parametresi için, en çok satan ürünler raporu tam olarak o sayıda ürün döndürmelidir (yetersiz veri varsa daha az)
**Doğrular: Gereksinim 3.3**

**Özellik 12: Performans verisi tamlığı**
*Herhangi bir* ürün performans girişi için, hem miktar toplamları hem de gelir toplamları hesaplanmalı ve dahil edilmelidir
**Doğrular: Gereksinim 3.5**

**Özellik 13: CSV format geçerliliği**
*Herhangi bir* CSV'ye aktarılan veri için, sonuç dosyası düzgün başlıklar ve kaçırılmış verilerle geçerli CSV formatında olmalıdır
**Doğrular: Gereksinim 4.1**

**Özellik 14: PDF dışa aktarma kararlılığı**
*Herhangi bir* PDF'ye aktarılan veri için, dışa aktarma işlemi hatasız tamamlanmalıdır (MVP placeholder olsa bile)
**Doğrular: Gereksinim 4.2**

**Özellik 15: Dışa aktarma dosya yolu dönüşü**
*Herhangi bir* başarılı dışa aktarma işlemi için, döndürülen dosya yolu mevcut, erişilebilir bir dosyayı işaret etmelidir
**Doğrular: Gereksinim 4.3**

**Özellik 16: Dışa aktarma hata yönetimi**
*Herhangi bir* dosya sistemi hatalarıyla karşılaşan dışa aktarma işlemi için, açıklayıcı mesajla uygun bir istisna fırlatılmalıdır
**Doğrular: Gereksinim 4.4**

**Özellik 17: Dışa aktarma dosya adı benzersizliği**
*Herhangi bir* dışa aktarma işlemi için, oluşturulan dosya adları benzersizliği sağlamak için zaman damgası ve rapor türü içermelidir
**Doğrular: Gereksinim 4.5**

**Özellik 18: Karlılık placeholder yapısı**
*Herhangi bir* karlılık raporu talebi için, döndürülen veri placeholder kar alanları ile tutarlı yapıya sahip olmalıdır
**Doğrular: Gereksinim 5.2**

**Özellik 19: Karlılık MVP kararlılığı**
*Herhangi bir* karlılık raporu talebi için, işlem istisna fırlatmadan tamamlanmalıdır
**Doğrular: Gereksinim 5.3**

**Özellik 20: Karlılık veri tamlığı**
*Herhangi bir* MVP karlılık raporu için, ürün ve satış verileri placeholder kar alanları ile birlikte dahil edilmelidir
**Doğrular: Gereksinim 5.4**

**Özellik 21: Karlılık loglama**
*Herhangi bir* karlılık servis çağrısı için, MVP placeholder durumunu belirten uygun log girişleri oluşturulmalıdır
**Doğrular: Gereksinim 5.5**

**Özellik 22: Salt okunur veritabanı oturumları**
*Herhangi bir* rapor sorgu yürütmesi için, veritabanı oturumu salt okunur olarak yapılandırılmalıdır
**Doğrular: Gereksinim 6.1**

**Özellik 23: Eş zamanlı erişim güvenliği**
*Herhangi bir* eş zamanlı rapor talebi için, sistem bunları veri bozulması veya kilitlenmeler olmadan güvenli şekilde işlemelidir
**Doğrular: Gereksinim 6.3**

**Özellik 24: Veritabanı hata yönetimi**
*Herhangi bir* veritabanı bağlantı başarısızlığı için, uygun veritabanına özgü istisnalar fırlatılmalıdır
**Doğrular: Gereksinim 6.4**

**Özellik 25: Performans loglama**
*Herhangi bir* makul yürütme süresini aşan sorgu için, performans uyarıları loglanmalıdır
**Doğrular: Gereksinim 6.5**

**Özellik 26: UI import kısıtlaması**
*Herhangi bir* raporlama modül dosyası için, kodda hiçbir UI bileşen importu bulunmamalıdır
**Doğrular: Gereksinim 7.1**

**Özellik 27: Katman ayrımı**
*Herhangi bir* raporlama modül bileşeni için, uygun sorumluluklarla tam olarak bir katmana (DTO, servis veya sorgu) ait olmalıdır
**Doğrular: Gereksinim 7.2**

**Özellik 28: DTO tip güvenliği**
*Herhangi bir* veri transfer işlemi için, tüm veri yapıları için güçlü tipli DTO sınıfları kullanılmalıdır
**Doğrular: Gereksinim 7.3**

**Özellik 29: İş mantığı yerleşimi**
*Herhangi bir* iş mantığı uygulaması için, sorgu katmanında değil servis katmanında bulunmalıdır
**Doğrular: Gereksinim 7.4**

**Özellik 30: Bağımlılık enjeksiyon uyumluluğu**
*Herhangi bir* bağımlılık kullanımı için, sistemin kurulu bağımlılık enjeksiyon desenlerini takip etmelidir
**Doğrular: Gereksinim 7.5**

## Performans Değerlendirmeleri

### Sorgu Optimizasyonu

- Uygun indeksler kullanılacak
- JOIN işlemleri optimize edilecek
- Büyük veri setleri için pagination uygulanacak
- Salt okunur bağlantı havuzu kullanılacak

### Bellek Yönetimi

- Büyük raporlar için akış dışa aktarımı
- Gereksiz veri yüklenmeyecek
- Bağlantılar düzgün kapatılacak

### Önbellekleme Stratejisi

MVP'de önbellek yok, gelecekte:
- Sık kullanılan raporlar için Redis önbelleği
- Parametre bazlı önbellek anahtarları
- TTL ile otomatik temizlik