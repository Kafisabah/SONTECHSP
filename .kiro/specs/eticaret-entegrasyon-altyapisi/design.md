# Tasarım Dokümanı

## Genel Bakış

E-Ticaret Entegrasyon Altyapısı, SONTECHSP projesi için merkezi bir entegrasyon omurgası sağlayacaktır. Sistem, çoklu e-ticaret platformlarını (Trendyol, Shopify, Amazon vb.) standart bir arayüz üzerinden yönetecek, asenkron iş kuyruğu ile performanslı operasyonlar sunacak ve çoklu mağaza desteği ile ölçeklenebilir bir yapı oluşturacaktır.

Sistem tamamen backend odaklı (headless) olarak tasarlanmış olup, UI bağımlılığı bulunmamaktadır. Service-Repository pattern kullanılarak katmanlar arası net ayrım sağlanmış, her platform için ortak bir soyutlama katmanı (abstraction layer) oluşturulmuştur.

## Mimari

### Katman Yapısı

```
┌─────────────────────────────────────────────────────────────┐
│                    Servis Katmanı                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ EticaretServisi │  │   JobKoşucusu   │  │ İzleme      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Depo Katmanı                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ EticaretDeposu  │  │   JobDeposu     │  │ TemelDepo   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 Entegrasyon Katmanı                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │BaglantiArayuzu  │  │BaglantiFabrikasi│  │ Bağlayıcılar│ │
│  │   (Arayüz)      │  │   (Fabrika)     │  │ (Somut)     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Veritabanı Katmanı                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │eticaret_hesaplari│  │eticaret_siparisleri│ │eticaret_is_│ │
│  │                 │  │                 │  │   kuyrugu   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Bağımlılık Yönü
- Servis Katmanı → Depo Katmanı → Veritabanı Katmanı
- Servis Katmanı → Entegrasyon Katmanı (Bağlayıcı kullanımı için)
- Entegrasyon Katmanı → Depo Katmanı (veri kalıcılığı için)

## Bileşenler ve Arayüzler

### 1. Veri Transfer Nesneleri (DTOs)

**MagazaHesabiOlusturDTO**
- platform: str (zorunlu)
- magaza_adi: str (zorunlu)
- aktif_mi: bool = True
- kimlik_json: dict (şifrelenmiş credentials)
- ayar_json: dict = None (platform-specific settings)

**SiparisDTO**
- platform: str
- dis_siparis_no: str
- magaza_hesabi_id: int
- siparis_zamani: datetime
- musteri_ad_soyad: str
- toplam_tutar: Decimal
- para_birimi: str = "TRY"
- durum: str
- kargo_tasiyici: str = None
- takip_no: str = None
- ham_veri_json: dict

**StokGuncelleDTO & FiyatGuncelleDTO**
- Toplu operasyonlar için optimize edilmiş veri yapıları

### 2. Entegrasyon Soyutlama Katmanı

**BaglantiArayuzu (Soyut Temel Sınıf)**
```python
@abstractmethod
def siparisleri_cek(self, sonra: datetime = None) -> List[SiparisDTO]
def stok_gonder(self, guncellemeler: List[StokGuncelleDTO]) -> None
def fiyat_gonder(self, guncellemeler: List[FiyatGuncelleDTO]) -> None
def siparis_durum_guncelle(self, dis_siparis_no: str, yeni_durum: str, takip_no: str = None) -> None
```

**BaglantiFabrikasi**
- Factory pattern ile platform tipine göre uygun bağlayıcı örneği döndürür
- Şu aşamada DummyConnector implementasyonu içerir
- Gelecekte gerçek platform bağlayıcıları eklenebilir

### 3. Depo Katmanı

**EticaretDeposu**
- Mağaza hesapları CRUD operasyonları
- Sipariş kaydetme ve sorgulama (unique constraint kontrolü ile)
- Filtreleme ve sayfalama desteği

**JobDeposu**
- Asenkron iş kuyruğu yönetimi
- FIFO iş çekme mekanizması
- İş durum takibi ve hata kayıtları

### 4. Servis Katmanı

**EticaretServisi**
- Ana iş mantığı katmanı
- Transaction yönetimi
- Hata yakalama ve EntegrasyonHatasi fırlatma
- DTO doğrulaması

**JobKoşucusu**
- Zamanlanmış ve manuel iş yürütme
- Toplu işleme (yapılandırılabilir limitler)
- Hata yönetimi ve yeniden deneme mantığı
- Üstel geri çekilme implementasyonu

## Veri Modelleri

### eticaret_hesaplari
```sql
CREATE TABLE eticaret_hesaplari (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    magaza_adi VARCHAR(200) NOT NULL,
    aktif_mi BOOLEAN DEFAULT TRUE,
    kimlik_json JSONB NOT NULL,  -- Şifrelenmiş kimlik bilgileri
    ayar_json JSONB,             -- Platform ayarları
    olusturma_zamani TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    guncelleme_zamani TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_eticaret_hesaplari_platform ON eticaret_hesaplari(platform);
CREATE INDEX idx_eticaret_hesaplari_aktif ON eticaret_hesaplari(aktif_mi);
```

### eticaret_siparisleri
```sql
CREATE TABLE eticaret_siparisleri (
    id SERIAL PRIMARY KEY,
    magaza_hesabi_id INTEGER REFERENCES eticaret_hesaplari(id),
    platform VARCHAR(50) NOT NULL,
    dis_siparis_no VARCHAR(100) NOT NULL,
    siparis_zamani TIMESTAMP NOT NULL,
    musteri_ad_soyad VARCHAR(200),
    toplam_tutar DECIMAL(15,2),
    para_birimi VARCHAR(3) DEFAULT 'TRY',
    durum VARCHAR(20) NOT NULL,
    kargo_tasiyici VARCHAR(100),
    takip_no VARCHAR(100),
    ham_veri_json JSONB,
    olusturma_zamani TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    guncelleme_zamani TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_siparis_unique UNIQUE(magaza_hesabi_id, dis_siparis_no)
);

CREATE INDEX idx_eticaret_siparisleri_platform ON eticaret_siparisleri(platform);
CREATE INDEX idx_eticaret_siparisleri_durum ON eticaret_siparisleri(durum);
CREATE INDEX idx_eticaret_siparisleri_siparis_zamani ON eticaret_siparisleri(siparis_zamani);
```

### eticaret_is_kuyrugu
```sql
CREATE TABLE eticaret_is_kuyrugu (
    id SERIAL PRIMARY KEY,
    magaza_hesabi_id INTEGER REFERENCES eticaret_hesaplari(id),
    tur VARCHAR(50) NOT NULL,  -- SIPARIS_CEK, STOK_GONDER, vb.
    payload_json JSONB NOT NULL,
    durum VARCHAR(20) DEFAULT 'BEKLIYOR',  -- BEKLIYOR, GONDERILDI, HATA
    hata_mesaji TEXT,
    deneme_sayisi INTEGER DEFAULT 0,
    sonraki_deneme TIMESTAMP,
    olusturma_zamani TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    guncelleme_zamani TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_eticaret_is_kuyrugu_durum ON eticaret_is_kuyrugu(durum);
CREATE INDEX idx_eticaret_is_kuyrugu_tur ON eticaret_is_kuyrugu(tur);
CREATE INDEX idx_eticaret_is_kuyrugu_sonraki_deneme ON eticaret_is_kuyrugu(sonraki_deneme);
```

## Doğruluk Özellikleri

*Bir özellik, sistemin tüm geçerli yürütmelerinde doğru olması gereken bir karakteristik veya davranıştır - esasen, sistemin ne yapması gerektiği hakkında resmi bir ifadedir. Özellikler, insan tarafından okunabilir spesifikasyonlar ile makine tarafından doğrulanabilir doğruluk garantileri arasında köprü görevi görür.*

### Özellik Yansıması

Ön çalışmada tanımlanan tüm özellikler gözden geçirildikten sonra, birkaç gereksizlik tespit edildi ve birleştirildi:

- İş durumu güncellemeleri ile ilgili özellikler (4.5, 5.5, 7.4) tek bir kapsamlı iş tamamlama özelliğinde birleştirildi
- Hata yönetimi özellikleri (4.2, 5.2, 6.3, 7.3, 8.1, 8.3) kapsamlı hata yönetimi özelliklerinde gruplandırıldı
- Doğrulama özellikleri (4.4, 5.4, 6.5) tek bir veri doğrulama özelliğinde birleştirildi
- Toplu işleme özellikleri (4.3, 5.3) tek bir toplu operasyon özelliğinde birleştirildi

Özellik 1: Mağaza hesabı veri kalıcılığı
*Herhangi bir* geçerli mağaza hesabı verisi için, sisteme kaydedildiğinde, tüm gerekli alanlar (platform, mağaza adı, kimlik bilgileri, ayarlar) değişmeden geri alınabilir olmalıdır
**Doğrular: Gereksinim 1.1**

Özellik 2: Mağaza hesabı güncelleme bütünlüğü
*Herhangi bir* mevcut mağaza hesabı için, geçerli verilerle güncellendiğinde, değişiklikler uygulanırken güncellenmemiş tüm alanlar korunmalı ve veri tutarlılığı sağlanmalıdır
**Doğrular: Gereksinim 1.2**

Özellik 3: Yumuşak silme korunması
*Herhangi bir* mağaza hesabı için, devre dışı bırakıldığında, hesap pasif olarak işaretlenmeli ancak tüm geçmiş veriler erişilebilir kalmalıdır
**Doğrular: Gereksinim 1.3**

Özellik 4: Kimlik bilgisi şifreleme
*Herhangi bir* hassas kimlik bilgisi verisi için, kimlik_json alanında saklandığında, veri şifrelenmiş olmalı ve düz metin olarak okunabilir olmamalıdır
**Doğrular: Gereksinim 1.4**

Özellik 5: Platform başına çoklu hesap
*Herhangi bir* platform türü için, sistem çakışma olmadan birden fazla mağaza hesabının oluşturulmasına ve saklanmasına izin vermelidir
**Doğrular: Gereksinim 1.5**

Özellik 6: Arayüz uyumluluğu
*Herhangi bir* platform bağlayıcı implementasyonu için, BaglantiArayuzu arayüzünden tüm gerekli metotları doğru imzalarla implement etmelidir
**Doğrular: Gereksinim 2.1, 2.2**

Özellik 7: Fabrika deseni doğruluğu
*Herhangi bir* geçerli platform türü için, fabrika o platform için doğru türde bir bağlayıcı örneği döndürmelidir
**Doğrular: Gereksinim 2.4**

Özellik 8: Standartlaştırılmış hata yönetimi
*Herhangi bir* hatayla karşılaşan bağlayıcı operasyonu için, açıklayıcı hata mesajları ile EntegrasyonHatasi fırlatmalıdır
**Doğrular: Gereksinim 2.5, 8.3**

Özellik 9: Sipariş saklama tamlığı
*Herhangi bir* platformlardan alınan sipariş verisi için, saklandığında, tüm gerekli alanlar (dış sipariş numarası, müşteri bilgisi, tutarlar, durum, kargo) korunmalıdır
**Doğrular: Gereksinim 3.1, 3.3**

Özellik 10: Yinelenen sipariş önleme
*Herhangi bir* aynı platform, dış sipariş numarası ve mağaza hesabı kombinasyonuna sahip sipariş için, veritabanında yalnızca bir kayıt bulunmalıdır
**Doğrular: Gereksinim 3.2**

Özellik 11: Ham veri korunması
*Herhangi bir* sipariş senkronizasyonu için, orijinal platform verisi ham_veri_json alanında değişmeden saklanmalıdır
**Doğrular: Gereksinim 3.4**

Özellik 12: Sipariş filtreleme doğruluğu
*Herhangi bir* mağaza hesabı ve durum filtreleri ile sipariş sorgusu için, yalnızca belirtilen kriterlere uyan siparişler döndürülmelidir
**Doğrular: Gereksinim 3.5**

Özellik 13: Operasyon yönlendirme doğruluğu
*Herhangi bir* stok veya fiyat güncelleme isteği için, operasyon doğru platforma karşılık gelen bağlayıcıya yönlendirilmelidir
**Doğrular: Gereksinim 4.1, 5.1**

Özellik 14: Toplu operasyon verimliliği
*Herhangi bir* aynı platform için birden fazla stok veya fiyat güncellemesi için, bunlar ayrı çağrılar yerine tek bir toplu operasyon olarak işlenmelidir
**Doğrular: Gereksinim 4.3, 5.3**

Özellik 15: Veri doğrulama zorlaması
*Herhangi bir* geçersiz veriye sahip stok güncellemesi, fiyat güncellemesi veya durum değişikliği için, operasyon platformlara iletilmeden önce reddedilmelidir
**Doğrular: Gereksinim 4.4, 5.4, 6.5**

Özellik 16: İş tamamlama takibi
*Herhangi bir* başarıyla tamamlanan entegrasyon operasyonu için, karşılık gelen iş durumu GONDERILDI olarak güncellenmelidir
**Doğrular: Gereksinim 4.5, 5.5, 7.4**

Özellik 17: Durum güncelleme dahil etme
*Herhangi bir* takip bilgisi ile sipariş durum güncellemesi için, hem yeni durum hem de takip numarası platform güncellemesine dahil edilmelidir
**Doğrular: Gereksinim 6.1, 6.2**

Özellik 18: Desteklenen durum doğrulaması
*Herhangi bir* sipariş durum operasyonu için, yalnızca geçerli durumlar (YENI, HAZIRLANIYOR, KARGODA, TESLIM, IPTAL) kabul edilmelidir
**Doğrular: Gereksinim 6.4**

Özellik 19: İş kuyruğa alma doğruluğu
*Herhangi bir* entegrasyon operasyon isteği için, uygun iş türü (SIPARIS_CEK, STOK_GONDER, FIYAT_GONDER, DURUM_GUNCELLE) ile iş olarak kuyruğa alınmalıdır
**Doğrular: Gereksinim 7.1, 7.5**

Özellik 20: FIFO iş işleme
*Herhangi bir* kuyruğa alınmış iş seti için, yapılandırılabilir toplu limitlerle ilk giren ilk çıkar sırasında işlenmelidir
**Doğrular: Gereksinim 7.2**

Özellik 21: Kapsamlı hata yönetimi
*Herhangi bir* başarısız entegrasyon operasyonu için, sistem detaylı hata bilgilerini loglamalı, iş durumunu HATA olarak güncellemeli ve yeniden deneme için hata detaylarını kaydetmelidir
**Doğrular: Gereksinim 4.2, 5.2, 6.3, 7.3, 8.1**

Özellik 22: Transaction geri alma güvenliği
*Herhangi bir* hatayla karşılaşan veritabanı operasyonu için, transaction geri alınmalı ve veri tutarlılığı korunmalıdır
**Doğrular: Gereksinim 8.2**

Özellik 23: Üstel geri çekilme yeniden deneme
*Herhangi bir* tekrar tekrar başarısız olan iş için, sistem aşırı yüklenmesini önlemek için yeniden deneme aralıkları üstel olarak artmalıdır
**Doğrular: Gereksinim 8.4**

Özellik 24: İzleme verisi kullanılabilirliği
*Herhangi bir* sistem operasyonu için, iş kuyruğu sağlığı ve hata oranları için izleme verisi mevcut ve doğru olmalıdır
**Doğrular: Gereksinim 8.5**

Özellik 25: DTO kullanım tutarlılığı
*Herhangi bir* sistem katmanları arası veri transferi için, tür güvenliği ve doğrulama için DTO sınıfları kullanılmalıdır
**Doğrular: Gereksinim 9.1**

Özellik 26: Depo deseni bağlılığı
*Herhangi bir* veritabanı operasyonu için, doğrudan veritabanı erişimi yerine depo sınıfları aracılığıyla gerçekleştirilmelidir
**Doğrular: Gereksinim 9.2**

Özellik 27: Servis katmanı ayrımı
*Herhangi bir* iş mantığı yürütmesi için, servis katmanında implement edilmeli ve veri erişim kodu ile karıştırılmamalıdır
**Doğrular: Gereksinim 9.3**

Özellik 28: Bağımlılık yönü uyumluluğu
*Herhangi bir* modül import'u için, bağımlılık yönü Servis -> Depo -> Veritabanı desenini takip etmelidir
**Doğrular: Gereksinim 9.4**

Özellik 29: Yalnızca arayüz genişletme
*Herhangi bir* yeni platform eklenmesi için, çekirdek sistem değişiklikleri olmadan yalnızca BaglantiArayuzu arayüz implementasyonu gerekli olmalıdır
**Doğrular: Gereksinim 9.5**

Özellik 30: Veritabanı kısıtlama zorlaması
*Herhangi bir* unique kısıtlamaları (mağaza hesapları, sipariş kombinasyonları) veya foreign key ilişkilerini ihlal etme girişimi için, veritabanı operasyonu reddetmelidir
**Doğrular: Gereksinim 10.1, 10.2, 10.4**

Özellik 31: İndeks kullanımı
*Herhangi bir* sık erişilen alanlarda (platform, durum) veritabanı sorgusu için, performans için uygun indeksler kullanılmalıdır
**Doğrular: Gereksinim 10.3**

Özellik 32: Migration desteği
*Herhangi bir* şema evrim gereksinimi için, veritabanı migration'ları yürütülebilir olmalı ve şema değişikliklerini doğru şekilde uygulamalıdır
**Doğrular: Gereksinim 10.5**

## Hata Yönetimi

### İstisna Hiyerarşisi
```python
class EntegrasyonHatasi(Exception):
    """Entegrasyon hataları için temel istisna"""
    pass

class BaglantiHatasi(EntegrasyonHatasi):
    """Bağlantı ile ilgili hatalar"""
    pass

class VeriDogrulamaHatasi(EntegrasyonHatasi):
    """Veri doğrulama hataları"""
    pass

class PlatformHatasi(EntegrasyonHatasi):
    """Platform-spesifik hatalar"""
    pass
```

### Hata Yönetimi Stratejisi
1. **Servis Katmanı**: Tüm istisnaları yakala, detayları logla, EntegrasyonHatasi ile sar
2. **Depo Katmanı**: Veritabanı istisnalarının yukarı çıkmasına izin ver, SQL hatalarını logla
3. **Entegrasyon Katmanı**: Platform-spesifik hataları yakala, EntegrasyonHatasi olarak standartlaştır
4. **İş İşleme**: Başarısız işler HATA olarak işaretle, hata detayları ile yeniden deneme için zamanla

### Yeniden Deneme Mantığı
- Üstel geri çekilme: 1dk, 2dk, 4dk, 8dk, 16dk, 32dk
- Maksimum yeniden deneme girişimi: 6
- Kalıcı olarak başarısız işler için ölü mektup kuyruğu

## Test Stratejisi

### Birim Test Yaklaşımı
- **Depo Testleri**: Veritabanı operasyonları, kısıtlama doğrulaması, sorgu doğruluğu
- **Servis Testleri**: İş mantığı, transaction yönetimi, hata senaryoları
- **Entegrasyon Testleri**: Uçtan uca iş akışları, bağlayıcı davranışı
- **DTO Testleri**: Veri doğrulaması, serileştirme/deserileştirme

### Özellik Tabanlı Test Yaklaşımı
Sistem Python için **Hypothesis** özellik tabanlı test kütüphanesini kullanacaktır. Her özellik tabanlı test, giriş alanında kapsamlı kapsama sağlamak için minimum 100 iterasyon çalışacaktır.

**Özellik Tabanlı Test Gereksinimleri:**
- Her doğruluk özelliği tek bir özellik tabanlı test ile implement edilmelidir
- Testler tasarım dokümanı özelliğine referans veren yorumlarla etiketlenmelidir
- Etiket formatı: `**Feature: eticaret-entegrasyon-altyapisi, Property {numara}: {özellik_metni}**`
- Girdileri geçerli iş alanlarına kısıtlamak için akıllı üreticiler oluşturulacaktır
- Testler değişmezler, gidiş-dönüş özellikleri ve metamorfik ilişkilere odaklanacaktır

**İkili Test Faydaları:**
- Birim testler spesifik örneklerin ve kenar durumların doğru çalıştığını doğrular
- Özellik testleri tüm geçerli girdiler boyunca evrensel özelliklerin geçerli olduğunu doğrular
- Birlikte kapsamlı kapsama sağlarlar: birim testler somut hataları yakalar, özellik testleri genel doğruluğu doğrular

**Test Verisi Üretimi:**
- Çeşitli platform türleri ve konfigürasyonları ile mağaza hesapları
- Farklı durumlar, tutarlar ve müşteri verileri ile siparişler
- Çeşitli iş türleri ve başarısızlık senaryoları ile iş kuyrukları
- Doğrulama testi için geçersiz veriler