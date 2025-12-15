# Çekirdek Altyapı Tasarım Dokümanı

## Genel Bakış

SONTECHSP çekirdek altyapısı, uygulamanın tüm katmanları tarafından kullanılan temel servisleri sağlar. Bu altyapı beş ana bileşenden oluşur: ayarlar yönetimi, loglama sistemi, hata yönetimi, yetkilendirme ve oturum yönetimi. Çekirdek altyapı, diğer katmanlardan tamamen bağımsız çalışacak şekilde tasarlanmıştır.

## Mimari

Çekirdek altyapı, katmanlı mimaride en alt seviyede yer alır ve aşağıdaki prensiplere uyar:

- **Bağımsızlık**: UI ve veritabanı katmanlarından tamamen bağımsız
- **Tekil Sorumluluk**: Her bileşen tek bir sorumluluğa sahip
- **Yapılandırılabilirlik**: Tüm davranışlar yapılandırma ile kontrol edilebilir
- **Hata Güvenliği**: Tüm hata durumları graceful şekilde yönetilir

```
┌─────────────────────────────────────┐
│            UI Katmanı               │
├─────────────────────────────────────┤
│          Servis Katmanı             │
├─────────────────────────────────────┤
│        Repository Katmanı           │
├─────────────────────────────────────┤
│         Çekirdek Altyapı            │
│  ┌─────────┬─────────┬─────────┐    │
│  │ Ayarlar │  Kayıt  │  Hata   │    │
│  ├─────────┼─────────┼─────────┤    │
│  │  Yetki  │ Oturum  │         │    │
│  └─────────┴─────────┴─────────┘    │
└─────────────────────────────────────┘
```

## Bileşenler ve Arayüzler

### AyarlarYoneticisi

Uygulama yapılandırmasını yöneten merkezi bileşen.

**Arayüz:**
```python
class AyarlarYoneticisi:
    def ayar_oku(self, anahtar: str, varsayilan=None) -> Any
    def zorunlu_ayar_oku(self, anahtar: str) -> Any
    def ayar_dogrula(self) -> bool
    def ornek_dosya_olustur(self) -> None
```

**Yapılandırma Kaynakları:**
1. Ortam değişkenleri (en yüksek öncelik)
2. .env dosyası
3. Varsayılan değerler

### KayitSistemi

Uygulama olaylarını kayıt altına alan sistem.

**Arayüz:**
```python
class KayitSistemi:
    def debug(self, mesaj: str) -> None
    def info(self, mesaj: str) -> None
    def warning(self, mesaj: str) -> None
    def error(self, mesaj: str) -> None
    def critical(self, mesaj: str) -> None
```

**Özellikler:**
- Çift çıktı: dosya + konsol
- Seviye filtreleme
- Otomatik dosya döndürme
- Türkçe mesaj desteği

### HataYoneticisi

Uygulama hatalarını kategorize eden ve yöneten sistem.

**Hata Hiyerarşisi:**
```python
class SontechHatasi(Exception): pass
class AlanHatasi(SontechHatasi): pass
class DogrulamaHatasi(SontechHatasi): pass
class EntegrasyonHatasi(SontechHatasi): pass
```

### YetkiKontrolcu

Kullanıcı yetkilendirmelerini kontrol eden bileşen.

**Arayüz:**
```python
class YetkiKontrolcu:
    def izin_var_mi(self, rol: str, izin: str) -> bool
    def yetki_matrisi_yukle(self, matris: Dict) -> None
    def rol_dogrula(self, rol: str) -> bool
```

### OturumBilgisi

Aktif kullanıcı oturumu ve bağlam bilgilerini yöneten veri yapısı.

**Veri Modeli:**
```python
@dataclass
class OturumBilgisi:
    kullanici_id: int
    kullanici_adi: str
    firma_id: int
    magaza_id: int
    terminal_id: Optional[int]
    roller: List[str]
    oturum_baslangic: datetime
```

## Veri Modelleri

### Yapılandırma Modeli

```python
@dataclass
class YapilandirmaModeli:
    veritabani_url: str
    log_klasoru: str
    ortam: str  # dev/prod
    log_seviyesi: str = "INFO"
    log_dosya_boyutu: int = 10485760  # 10MB
    log_dosya_sayisi: int = 5
```

### Yetki Matrisi Modeli

```python
@dataclass
class YetkiMatrisi:
    roller: Dict[str, List[str]]  # rol -> izinler listesi
    varsayilan_roller: List[str]
    admin_rolleri: List[str]
```

## Doğruluk Özellikleri

*Bir özellik, sistemin tüm geçerli çalıştırmalarında doğru olması gereken bir karakteristik veya davranıştır - esasen, sistemin ne yapması gerektiği hakkında resmi bir ifadedir. Özellikler, insan tarafından okunabilir spesifikasyonlar ile makine tarafından doğrulanabilir doğruluk garantileri arasında köprü görevi görür.*

**Özellik 1: Ayar okuma tutarlılığı**
*Herhangi bir* geçerli ayar anahtarı için, ayar okuma işlemi tutarlı sonuç döndürmelidir
**Doğrular: Gereksinim 1.1, 1.3**

**Özellik 2: Log çift yazım garantisi**
*Herhangi bir* log mesajı için, mesaj hem dosyaya hem konsola yazılmalıdır
**Doğrular: Gereksinim 2.1**

**Özellik 3: Log seviye filtreleme**
*Herhangi bir* log seviyesi ayarı için, sadece belirtilen seviye ve üstü mesajlar kaydedilmelidir
**Doğrular: Gereksinim 2.2**

**Özellik 4: Log ayar uyumluluğu**
*Herhangi bir* log ayar kombinasyonu için, sistem ayarlara uygun davranış sergilemelidir
**Doğrular: Gereksinim 2.5**

**Özellik 5: Hata loglama tutarlılığı**
*Herhangi bir* hata tipi için, uygun log seviyesinde kayıt yapılmalıdır
**Doğrular: Gereksinim 3.4**

**Özellik 6: Türkçe hata mesajı garantisi**
*Herhangi bir* hata mesajı için, mesaj Türkçe olmalıdır
**Doğrular: Gereksinim 3.5**

**Özellik 7: Yetki kontrol tutarlılığı**
*Herhangi bir* rol-izin kombinasyonu için, yetki kontrolü tutarlı sonuç vermelidir
**Doğrular: Gereksinim 4.1, 4.4**

**Özellik 8: Oturum bilgi bütünlüğü**
*Herhangi bir* oturum açma işlemi için, gerekli tüm bilgiler (kullanıcı, firma, mağaza) tutulmalıdır
**Doğrular: Gereksinim 5.1**

**Özellik 9: Oturum bağlam güncelleme**
*Herhangi bir* bağlam değişikliği için, oturum bilgisi güncellenmelidir
**Doğrular: Gereksinim 5.2**

**Özellik 10: Oturum temizlik garantisi**
*Herhangi bir* oturum sonlandırma için, tüm bilgiler temizlenmelidir
**Doğrular: Gereksinim 5.3**

**Özellik 11: Çoklu terminal desteği**
*Herhangi bir* terminal kombinasyonu için, terminal bilgisi doğru şekilde tutulmalıdır
**Doğrular: Gereksinim 5.4**

**Özellik 12: Oturum veri korunumu**
*Herhangi bir* aktif oturum için, bağlam bilgileri korunmalıdır
**Doğrular: Gereksinim 5.5**

**Özellik 13: UI katman bağımsızlığı**
*Herhangi bir* çekirdek modül için, UI katmanından bağımsız çalışmalıdır
**Doğrular: Gereksinim 6.1**

**Özellik 14: Veritabanı katman bağımsızlığı**
*Herhangi bir* çekirdek modül için, veritabanı katmanından bağımsız çalışmalıdır
**Doğrular: Gereksinim 6.2**

**Özellik 15: Standart kütüphane bağımlılığı**
*Herhangi bir* çekirdek modül için, sadece standart kütüphaneler kullanılmalıdır
**Doğrular: Gereksinim 6.3**

**Özellik 16: Çalışma zamanı bağımsızlığı**
*Herhangi bir* çekirdek işlev için, dış bağımlılık gerektirmemelidir
**Doğrular: Gereksinim 6.4**

**Özellik 17: İzole test edilebilirlik**
*Herhangi bir* çekirdek modül için, izole test edilebilmelidir
**Doğrular: Gereksinim 6.5**

**Özellik 18: Güvenli yapılandırma yükleme**
*Herhangi bir* .env dosyası için, hassas bilgiler güvenli şekilde yüklenmelidir
**Doğrular: Gereksinim 7.1**

**Özellik 19: Yapılandırma doğrulama**
*Herhangi bir* yapılandırma için, zorunlu alanlar kontrol edilmelidir
**Doğrular: Gereksinim 7.2**

**Özellik 20: Ortam değişkeni önceliği**
*Herhangi bir* ayar çakışması için, ortam değişkeni öncelikli kullanılmalıdır
**Doğrular: Gereksinim 7.3**

**Özellik 21: Dinamik ayar algılama**
*Herhangi bir* ayar değişikliği için, sistem değişikliği algılamalıdır
**Doğrular: Gereksinim 7.5**

## Hata Yönetimi

### Hata Kategorileri

1. **AlanHatasi**: Veri alanı doğrulama hataları
2. **DogrulamaHatasi**: İş kuralı doğrulama hataları  
3. **EntegrasyonHatasi**: Dış sistem entegrasyon hataları

### Hata Yönetim Stratejisi

- Tüm hatalar merkezi olarak loglanır
- Hata mesajları Türkçe ve kullanıcı dostu
- Kritik hatalar sistem yöneticisine bildirilir
- Hata detayları geliştirme ortamında gösterilir

## Test Stratejisi

### Birim Testleri

- Her bileşen için izole testler
- Hata durumları için özel testler
- Yapılandırma senaryoları testleri
- Performans kritik noktalar için testler

### Özellik Tabanlı Testler

- Hypothesis kütüphanesi kullanılacak
- Her test minimum 100 iterasyon çalışacak
- Testler tasarım dokümanındaki özellikleri doğrulayacak
- Her özellik tek bir property-based test ile implement edilecek

**Test Kütüphanesi**: Hypothesis (Python)
**Minimum İterasyon**: 100
**Test Formatı**: Her test, tasarım dokümanındaki özellik numarasını referans alacak

### Entegrasyon Testleri

- Bileşenler arası etkileşim testleri
- Yapılandırma yükleme senaryoları
- Hata zincirleme testleri
- Performans ve bellek kullanımı testleri