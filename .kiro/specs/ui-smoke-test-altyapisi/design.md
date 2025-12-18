# Tasarım Dokümanı

## Genel Bakış

UI Smoke Test ve Buton Eşleştirme Altyapısı, SONTECHSP arayüzünün sanal ortamda test edilmesini ve buton-fonksiyon-servis eşleştirmelerinin takip edilmesini sağlayan bir sistemdir. Bu sistem, mevcut PyQt6 arayüz yapısına minimal müdahale ile entegre olacak şekilde tasarlanmıştır.

## Mimari

### Bileşen Diyagramı

```
┌─────────────────────────────────────────────────────────────┐
│                    UI Smoke Test Sistemi                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Smoke Test      │  │ Buton Eşleştirme│  │ Log Sistemi │ │
│  │ Çalıştırıcısı   │  │ Kaydı           │  │             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    Mevcut UI Katmanı                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ AnaPencere      │  │ Ekranlar        │  │ Servis      │ │
│  │                 │  │                 │  │ Fabrikası   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Veri Akışı

1. **Smoke Test Başlatma**: `smoke_test_calistir.py` → `UygulamaBaslatici` → `AnaPencere`
2. **Buton Eşleştirme**: Ekran yüklendiğinde → `buton_eslestirme_kaydi.kayit_ekle()`
3. **Buton Tıklama**: Buton click → Handler → Log + Servis çağrısı
4. **Kayıt Sorgulama**: `kayitlari_listele()` → Eşleştirme tablosu

## Bileşenler ve Arayüzler

### 1. Smoke Test Çalıştırıcısı (`smoke_test_calistir.py`)

**Sorumluluklar:**
- UI'yi test modunda başlatma
- Ekranlar arası geçiş testi
- Temiz kapanış sağlama

**Arayüz:**
```python
def main() -> int:
    """Ana smoke test fonksiyonu"""
    
def ekran_gecis_testi() -> bool:
    """Ekranlar arası geçiş testi"""
    
def temiz_kapanis() -> None:
    """Uygulamayı temiz şekilde kapatma"""
```

### 2. Buton Eşleştirme Kaydı (`buton_eslestirme_kaydi.py`)

**Sorumluluklar:**
- Buton-handler-servis eşleştirmelerini kaydetme
- Kayıtları sorgulama ve listeleme
- Thread-safe kayıt yönetimi

**Arayüz:**
```python
def kayit_ekle(ekran_adi: str, buton_adi: str, handler_adi: str, servis_metodu: str = None) -> None:
    """Yeni buton eşleştirmesi kaydet"""
    
def kayitlari_listele() -> List[Dict[str, str]]:
    """Tüm kayıtları listele"""
    
def kayitlari_temizle() -> None:
    """Tüm kayıtları temizle"""
```

### 3. Log Sistemi

**Sorumluluklar:**
- Buton tıklama olaylarını loglama
- Stub servis çağrılarını işaretleme
- Yapılandırılabilir log seviyesi

## Veri Modelleri

### Buton Eşleştirme Kaydı

```python
@dataclass
class ButonEslestirme:
    ekran_adi: str
    buton_adi: str
    handler_adi: str
    servis_metodu: Optional[str] = None
    kayit_zamani: datetime = field(default_factory=datetime.now)
    cagrilma_sayisi: int = 0
```

### Log Kaydı

```python
@dataclass
class LogKaydi:
    zaman: datetime
    ekran_adi: str
    buton_adi: str
    handler_adi: str
    servis_metodu: Optional[str]
    durum: str  # "basarili", "hata", "stub"
    detay: Optional[str] = None
```

## Doğruluk Özellikleri

*Bir özellik, sistemin tüm geçerli çalıştırmalarında doğru olması gereken bir karakteristik veya davranıştır - esasen, sistemin ne yapması gerektiği hakkında resmi bir ifadedir. Özellikler, insan tarafından okunabilir spesifikasyonlar ile makine tarafından doğrulanabilir doğruluk garantileri arasında köprü görevi görür.*

<function_calls>
<invoke name="prework">
<parameter name="featureName">ui-smoke-test-altyapisi

**Özellik 1: Smoke Test Başlatma Tutarlılığı**
*Herhangi bir* smoke test komutu çalıştırıldığında, sistem AnaPencere arayüzünü başlatmalıdır
**Doğrular: Gereksinim 1.1**

**Özellik 2: Ekran Geçiş Erişilebilirliği**
*Herhangi bir* smoke test çalışması sırasında, sistem tüm ekranlar arası geçişlere izin vermelidir
**Doğrular: Gereksinim 1.2**

**Özellik 3: Temiz Kapanış Garantisi**
*Herhangi bir* smoke test tamamlandığında, sistem hatasız şekilde temiz kapanmalıdır
**Doğrular: Gereksinim 1.3**

**Özellik 4: Buton Eşleştirme Veri Bütünlüğü**
*Herhangi bir* buton eşleştirmesi kaydedildiğinde, sistem ekran adı, buton adı, handler adı ve servis metodunu saklamalıdır
**Doğrular: Gereksinim 2.1**

**Özellik 5: Kayıt Listeleme Tamlığı**
*Herhangi bir* buton eşleştirme sorgusu yapıldığında, sistem tüm kayıtlı eşleştirmelerin tam listesini döndürmelidir
**Doğrular: Gereksinim 2.2**

**Özellik 6: Otomatik Kayıt Tutarlılığı**
*Herhangi bir* kritik buton bağlandığında, sistem otomatik olarak eşleştirmeyi kaydetmelidir
**Doğrular: Gereksinim 2.3**

**Özellik 7: Yapılandırılmış Veri Formatı**
*Herhangi bir* eşleştirme sorgulandığında, sistem yapılandırılmış formatta veri sağlamalıdır
**Doğrular: Gereksinim 2.4**

**Özellik 8: Handler Loglama Tutarlılığı**
*Herhangi bir* buton handler'ı çalıştığında, sistem hangi butonun hangi handler'ı tetiklediğini loglamalıdır
**Doğrular: Gereksinim 3.1**

**Özellik 9: Stub Servis Loglama**
*Herhangi bir* stub servis çağrıldığında, sistem "stub çağrıldı" mesajını loglamalıdır
**Doğrular: Gereksinim 3.2**

**Özellik 10: Log İçerik Tamlığı**
*Herhangi bir* loglama gerçekleştiğinde, sistem ekran adı, buton adı ve handler bilgilerini içermelidir
**Doğrular: Gereksinim 3.3**

**Özellik 11: UI İş Kuralı Kısıtlaması**
*Herhangi bir* UI etkileşimi olduğunda, sistem iş kuralı çalıştırmamalı, sadece loglama ve servis çağrısı yapmalıdır
**Doğrular: Gereksinim 3.4**

**Özellik 12: Standart Giriş Noktası Tutarlılığı**
*Herhangi bir* uygulama başlatıldığında, sistem UI başlatma için standartlaştırılmış giriş noktası sağlamalıdır
**Doğrular: Gereksinim 4.1**

## Hata Yönetimi

### Hata Türleri ve Yönetim Stratejileri

1. **UI Başlatma Hataları**
   - PyQt6 başlatma sorunları
   - Servis fabrikası oluşturma hataları
   - Ekran yükleme hataları

2. **Kayıt Sistemi Hataları**
   - Thread-safety sorunları
   - Bellek yetersizliği
   - Dosya erişim sorunları

3. **Log Sistemi Hataları**
   - Log dosyası yazma hataları
   - Format hataları
   - Disk alanı sorunları

### Hata Yönetim Mekanizmaları

```python
class SmokeTestHatasi(Exception):
    """Smoke test özel hata sınıfı"""
    pass

class ButonEslestirmeHatasi(Exception):
    """Buton eşleştirme özel hata sınıfı"""
    pass
```

## Test Stratejisi

### Birim Testleri

- **Smoke Test Çalıştırıcısı**: UI başlatma, ekran geçişi, kapanış testleri
- **Buton Eşleştirme Kaydı**: Kayıt ekleme, listeleme, temizleme testleri
- **Log Sistemi**: Log yazma, format doğrulama testleri

### Özellik Tabanlı Testler

Özellik tabanlı testler için **Hypothesis** kütüphanesi kullanılacaktır. Her test minimum 100 iterasyon çalıştırılacaktır.

**Test Etiketleme Formatı**: `**Özellik: ui-smoke-test-altyapisi, Özellik {numara}: {özellik_metni}**`

### Entegrasyon Testleri

- **UI-Servis Entegrasyonu**: Buton tıklama → Handler → Servis çağrısı akışı
- **Kayıt-Log Entegrasyonu**: Buton kaydı → Log yazma → Sorgu akışı
- **Smoke Test Tam Akışı**: Başlatma → Geçiş → Kapanış tam döngüsü

### Test Ortamı Gereksinimleri

- Python 3.8+
- PyQt6
- Hypothesis (özellik tabanlı testler için)
- pytest (test çalıştırıcısı)
- Sanal ekran desteği (headless test için Xvfb)

## Performans Gereksinimleri

- **UI Başlatma**: < 3 saniye
- **Ekran Geçişi**: < 500ms
- **Buton Kayıt**: < 10ms
- **Log Yazma**: < 5ms
- **Bellek Kullanımı**: < 50MB (temel UI için)

## Güvenlik Gereksinimleri

- Log dosyalarında hassas bilgi bulunmamalı
- Kayıt sistemi thread-safe olmalı
- Stub servisler gerçek veri işlememeli
- Test modunda gerçek veritabanı bağlantısı yapılmamalı