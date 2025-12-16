# Design Document

## Overview

SONTECHSP projesi için PyQt6 tabanlı kullanıcı arayüzü iskeletlerinin tasarımı. Bu sistem, katmanlı mimari prensiplerine uygun olarak sadece görsel bileşenler ve navigasyon işlevlerini içerecek, iş kuralları servis katmanına delegasyonu yapacaktır. Arayüz modüler yapıda tasarlanarak her ekranın bağımsız olarak geliştirilebilmesini sağlayacaktır.

## Architecture

### Katman Yapısı
```
uygulama/arayuz/
├── uygulama.py              # QApplication başlatma
├── ana_pencere.py           # Ana pencere ve navigasyon
├── servis_fabrikasi.py      # Servis dependency injection
├── yardimcilar.py           # UI utility fonksiyonları
└── ekranlar/                # Modül ekranları
    ├── __init__.py
    ├── gosterge_paneli.py
    ├── pos_satis.py
    ├── urunler_stok.py
    ├── musteriler.py
    ├── eticaret.py
    ├── ebelge.py
    ├── kargo.py
    ├── raporlar.py
    └── ayarlar.py
```

### Bağımlılık Yönü
- Ana Pencere → Ekranlar
- Ekranlar → Servis Fabrikası → Servisler (stub)
- Tüm UI bileşenleri → Yardımcılar

## Components and Interfaces

### Ana Uygulama Bileşeni
```python
class UygulamaBaşlatici:
    def arayuzu_baslat() -> None
    def tema_yukle() -> None
    def kaynaklari_temizle() -> None
```

### Ana Pencere Bileşeni
```python
class AnaPencere(QMainWindow):
    def __init__(servis_fabrikasi: ServisFabrikasi)
    def menu_olustur() -> None
    def ekran_degistir(ekran_adi: str) -> None
    def servis_al(servis_tipi: str) -> Any
```

### Servis Fabrikası
```python
class ServisFabrikasi:
    def stok_servisi() -> StokServisi
    def pos_servisi() -> PosServisi  
    def crm_servisi() -> CrmServisi
    def eticaret_servisi() -> EticaretServisi
    def ebelge_servisi() -> EbelgeServisi
    def kargo_servisi() -> KargoServisi
    def rapor_servisi() -> RaporServisi
    def ayar_servisi() -> AyarServisi
```

### Ekran Arayüzü
```python
class TemelEkran(QWidget):
    def __init__(servis_fabrikasi: ServisFabrikasi)
    def ekrani_hazirla() -> None
    def verileri_yukle() -> None
    def hata_goster(mesaj: str) -> None
```

## Data Models

### UI Veri Transfer Nesneleri
```python
@dataclass
class EkranDurumu:
    aktif_ekran: str
    onceki_ekran: str
    parametreler: Dict[str, Any]

@dataclass  
class MenuOgesi:
    ad: str
    simge: str
    ekran_sinifi: type
    yetki_gerekli: bool

@dataclass
class TabloVerisi:
    basliklar: List[str]
    satirlar: List[List[Any]]
    toplam_kayit: int
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Property 1: Uygulama başlatma tutarlılığı
*For any* uygulama başlatma işlemi, QApplication örneği oluşturulmalı ve ana pencere görüntülenmeli
**Validates: Requirements 1.1, 1.3**

Property 2: Navigasyon tutarlılığı  
*For any* menü öğesi tıklaması, ilgili ekran içerik alanında gösterilmeli ve ekran değişimi gerçekleşmeli
**Validates: Requirements 2.2, 2.4**

Property 3: Servis fabrikası singleton davranışı
*For any* servis tipi, aynı servis tipinin her zaman aynı örneği döndürülmeli
**Validates: Requirements 3.1**

Property 4: Servis çağrısı tutarlılığı
*For any* UI bileşeni servis ihtiyacı, ilgili servis metodunun çağrılması gerçekleşmeli
**Validates: Requirements 3.2, 3.3, 3.4, 5.1, 5.2, 6.1, 7.1, 8.2, 8.3, 8.4, 9.2, 9.3, 9.4, 10.2, 10.3, 11.2, 12.4**

Property 5: Dialog açma tutarlılığı
*For any* dialog açma işlemi, ilgili dialog penceresi görüntülenmeli
**Validates: Requirements 6.2, 6.3, 6.4, 7.2, 7.3, 7.4**

Property 6: Tablo güncelleme tutarlılığı
*For any* veri değişikliği, ilgili tablo bileşeni güncellenmiş veriyi göstermeli
**Validates: Requirements 5.3, 10.4, 11.3**

Property 7: Hata gösterim tutarlılığı
*For any* hata durumu, standart hata dialog formatında kullanıcıya mesaj gösterilmeli
**Validates: Requirements 5.4, 13.4**

Property 8: Formatlaşma tutarlılığı
*For any* veri formatlaması, belirtilen format kurallarına uygun gösterim yapılmalı
**Validates: Requirements 13.1, 13.2, 13.3**

Property 9: Ekran yapısı tutarlılığı
*For any* ekran açılışı, belirtilen UI yapısı doğru şekilde görüntülenmeli
**Validates: Requirements 2.1, 4.1, 4.2, 4.3, 9.1, 12.1**

Property 10: Kaynak temizleme tutarlılığı
*For any* uygulama kapatma işlemi, tüm kaynaklar temizlenmeli
**Validates: Requirements 1.4**

<function_calls>
<invoke name="prework">
<parameter name="featureName">pyqt-arayuz-iskeleti

## Error Handling

### Hata Yönetimi Stratejisi
- UI katmanında iş kuralı hatası yakalanmayacak
- Servis çağrısı hataları try/except ile yakalanacak
- Kullanıcıya QMessageBox ile standart hata mesajları gösterilecek
- Kritik hatalar log dosyasına kaydedilecek

### Hata Türleri
```python
class UIHataTurleri:
    SERVIS_BULUNAMADI = "Servis bulunamadı"
    BAGLANTI_HATASI = "Bağlantı hatası"
    VERI_FORMATI_HATALI = "Veri formatı hatalı"
    YETKI_YETERSIZ = "Yetki yetersiz"
```

## Testing Strategy

### Dual Testing Approach
Bu projede hem unit testler hem de property-based testler kullanılacaktır:

**Unit Testing:**
- Belirli UI bileşenlerinin doğru çalışmasını test eder
- Dialog açılması, buton tıklamaları gibi spesifik durumları kapsar
- PyQt6 test framework'ü kullanılacak
- Mock servisler ile izole testler yapılacak

**Property-Based Testing:**
- Pytest-qt ve Hypothesis kütüphaneleri kullanılacak
- Her property-based test minimum 100 iterasyon çalıştırılacak
- Her correctness property için ayrı bir property-based test yazılacak
- Test etiketleme formatı: '**Feature: pyqt-arayuz-iskeleti, Property {number}: {property_text}**'

**Test Gereksinimleri:**
- Tüm UI bileşenleri için unit testler yazılacak
- Her correctness property için property-based test implementasyonu yapılacak
- Test coverage minimum %80 olacak
- CI/CD pipeline'da otomatik test çalıştırılacak