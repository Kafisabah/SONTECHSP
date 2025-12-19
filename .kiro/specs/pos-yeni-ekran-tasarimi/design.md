# POS Yeni Ekran Tasarımı - Tasarım Belgesi

## Genel Bakış

Bu belge, SONTECHSP sisteminde POS ekranının tamamen yeniden tasarlanması için teknik tasarımı açıklar. Mevcut dağınık ve verimsiz POS arayüzü yerine, kasiyer akışına uygun, hızlı ve okunaklı bir ekran tasarlanacak. Turkuaz-gri renk teması ile modern ve göz yormayan bir arayüz oluşturulacak.

## Mimari

### Yeni Dosya Yapısı
```
uygulama/arayuz/ekranlar/pos/
├── pos_satis_ekrani.py           # Ana birleştirici (120 satır max)
├── sepet_modeli.py               # QAbstractTableModel
├── ust_bar.py                    # Üst çubuk bileşeni
├── odeme_paneli.py               # Ödeme ve toplam paneli
├── hizli_islem_seridi.py         # Alt şerit butonları
├── hizli_urunler_sekmesi.py      # Hızlı ürün grid sistemi
└── dialoglar/
    ├── parcali_odeme_dialog.py   # Nakit+kart ödeme
    ├── indirim_dialog.py         # İndirim/kupon işlemleri
    └── musteri_sec_dialog.py     # Müşteri seçimi (CRM stub)
```

### Layout Mimarisi
```
┌─────────────────────────────────────────────────────────────┐
│ ÜST BAR (tam genişlik)                                      │
│ [Barkod] [Ürün Arama] ... [Kasiyer] [Müşteri] [Saat]      │
├─────────────────────────────────────────────────────────────┤
│ ORTA ALAN                                                   │
│ ┌─────────────────────────┬─────────────────────────────┐   │
│ │ SEPET (%70)             │ ÖDEME PANELİ (%30)         │   │
│ │ QTableView              │ ┌─────────────────────────┐ │   │
│ │ [Barkod|Ürün|Adet|...]  │ │ Genel Toplam (büyük)   │ │   │
│ │                         │ │ Ara Toplam / İndirim    │ │   │
│ │ [Not][İndirim][Kupon]   │ │ [NAKİT][KART][PARÇALI]  │ │   │
│ │                         │ └─────────────────────────┘ │   │
│ │                         │ ┌─────────────────────────┐ │   │
│ │                         │ │ Hızlı Ürünler Sekmesi  │ │   │
│ │                         │ │ [Grid Butonları]        │ │   │
│ │                         │ └─────────────────────────┘ │   │
│ └─────────────────────────┴─────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│ ALT ŞERİT (tam genişlik, her zaman görünür)                │
│ [BEKLET][BEKLEYENLER][İADE][İPTAL][FİŞ][FATURA]           │
└─────────────────────────────────────────────────────────────┘
```

## Bileşenler ve Arayüzler

### Ana POS Ekranı (pos_satis_ekrani.py)
```python
class POSSatisEkrani(QWidget):
    def __init__(self):
        # Ana layout: QVBoxLayout
        # - Üst: UstBar widget
        # - Orta: QHBoxLayout (Sepet %70 + Ödeme %30)
        # - Alt: HizliIslemSeridi widget
        
    def klavye_olayini_isle(self, event):
        # F2-F10, ESC, DEL, +/- kısayolları
        pass
```

### Sepet Modeli (sepet_modeli.py)
```python
class SepetModeli(QAbstractTableModel):
    def __init__(self):
        self.kolonlar = ['Barkod', 'Ürün', 'Adet', 'Fiyat', 'Tutar', 'Sil']
        self.sepet_ogeleri = []
        
    def data(self, index, role):
        # Turkuaz tema renkleri
        # Seçili satır vurgulama
        pass
```

### Üst Bar (ust_bar.py)
```python
class UstBar(QWidget):
    def __init__(self):
        # QHBoxLayout
        # Sol: Barkod QLineEdit + Ürün arama QComboBox
        # Sağ: Kasiyer etiketi + Müşteri butonları + Saat
        
    def barkod_enter_basildi(self):
        # Servis çağrısı: ürün bul ve sepete ekle
        pass
```

### Ödeme Paneli (odeme_paneli.py)
```python
class OdemePaneli(QWidget):
    def __init__(self):
        # QVBoxLayout
        # Üst: Toplam göstergeleri (büyük font)
        # Orta: Ödeme butonları (F4-F7 kısayolları)
        # Alt: QTabWidget (Ödeme/Hızlı Ürünler)
        
    def nakit_odeme_baslat(self):
        # Para girişi ve para üstü hesaplama
        pass
```

### Hızlı İşlem Şeridi (hizli_islem_seridi.py)
```python
class HizliIslemSeridi(QWidget):
    def __init__(self):
        # QHBoxLayout - tek satır butonlar
        # Her buton büyük, net, kısayol göstergeli
        
    def beklet_islemi(self):
        # Sepeti beklet, yeni sepet başlat
        pass
```

## Veri Modelleri

### Sepet Öğesi
```python
@dataclass
class SepetOgesi:
    barkod: str
    urun_adi: str
    adet: int
    birim_fiyat: Decimal
    toplam_fiyat: Decimal
    indirim_orani: float = 0.0
    
    def toplam_hesapla(self) -> Decimal:
        return self.birim_fiyat * self.adet * (1 - self.indirim_orani)
```

### Ödeme Bilgisi
```python
@dataclass
class OdemeBilgisi:
    odeme_turu: str  # 'nakit', 'kart', 'parcali', 'acik_hesap'
    tutar: Decimal
    alinan_para: Optional[Decimal] = None
    para_ustu: Optional[Decimal] = None
    musteri_id: Optional[int] = None
    nakit_tutar: Optional[Decimal] = None  # Parçalı ödeme
    kart_tutar: Optional[Decimal] = None   # Parçalı ödeme
```

### Hızlı Ürün Butonu
```python
@dataclass
class HizliUrunButonu:
    pozisyon: int
    urun_id: Optional[int]
    urun_adi: str
    barkod: str
    fiyat: Decimal
    kategori_id: int
    aktif: bool = True
```

### UI Tema Ayarları
```python
@dataclass
class TurkuazTema:
    ana_renk: str = "#20B2AA"      # Turkuaz
    ikincil_renk: str = "#708090"   # Slate Gray
    arka_plan: str = "#F8F8FF"      # Ghost White
    vurgu_renk: str = "#48D1CC"     # Medium Turquoise
    hata_renk: str = "#FF6347"      # Tomato
    basari_renk: str = "#32CD32"    # Lime Green
```

## Doğruluk Özellikleri

*Bir özellik, sistemin tüm geçerli çalıştırmalarında doğru olması gereken bir karakteristik veya davranıştır - esasen, sistemin ne yapması gerektiği hakkında resmi bir ifadedir. Özellikler, insan tarafından okunabilir spesifikasyonlar ile makine tarafından doğrulanabilir doğruluk garantileri arasında köprü görevi görür.*

### Özellik Yansıması

Prework analizini gözden geçirdikten sonra, aşağıdaki özellik konsolidasyonları belirlenmiştir:

**Birleştirilebilir Özellikler:**
- UI bileşen varlığı özellikleri (üst bar, sepet, ödeme paneli bileşenleri) - kapsamlı UI bileşen özelliğinde birleştirilebilir
- Klavye kısayolu özellikleri (F4-F10, ESC) - genel klavye kısayolu özelliğinde birleştirilebilir
- Kod kalitesi kuralları (dosya boyutu, fonksiyon boyutu, PEP8) - tek kapsamlı özellikte birleştirilebilir
- UI stil özellikleri (tema, buton, tablo stilleri) - genel UI stil özelliğinde birleştirilebilir

**Benzersiz Değer Sağlayan Özellikler:**
- Barkod işleme ve ürün arama davranışları
- Sepet yönetimi ve ödeme işlemleri
- Hızlı ürün butonları ve kategori yönetimi
- Hata yönetimi ve log kayıt davranışları
- Menü entegrasyonu ve durum yönetimi

## Doğruluk Özellikleri

**Özellik 1: UI Bileşen Varlığı**
*Herhangi bir* POS ekranı açılışında, sistem üst bar (barkod/arama alanları, kasiyer bilgisi, müşteri butonları), orta alan (%70 sepet + %30 ödeme paneli), alt şerit (hızlı işlem butonları) ve sekme sistemi (ödeme/hızlı ürünler) bileşenlerini göstermelidir
**Doğrular: Gereksinim 1.2, 1.3, 1.4, 1.5, 3.1, 3.2, 3.5, 4.1, 4.3, 4.4, 5.1, 5.2, 6.1, 6.3**

**Özellik 2: Barkod ve Ürün Arama İşleme**
*Herhangi bir* geçerli barkod girişinde sistem ürünü sepete eklemeli, geçersiz barkod girişinde turkuaz renkli hata mesajı göstermeli ve ürün arama metni girişinde hızlı sonuç dropdown göstermelidir
**Doğrular: Gereksinim 2.1, 2.2, 2.4, 2.5**

**Özellik 3: Sepet Yönetimi**
*Herhangi bir* sepet işleminde (satır seçimi, adet değiştirme, silme), sistem QTableView ile doğru kolonları göstermeli, seçili satırda adet değiştirme imkanı sunmalı ve sepet altında işlem butonlarını göstermelidir
**Doğrular: Gereksinim 3.3, 5.4**

**Özellik 4: Ödeme Türü Yönetimi**
*Herhangi bir* ödeme türü seçiminde, sistem büyük fontla genel toplam göstermeli, ara toplam/indirim/KDV bilgilerini göstermeli ve seçilen ödeme türüne göre uygun arayüzü (nakit için para üstü, parçalı için dialog) göstermelidir
**Doğrular: Gereksinim 4.2**

**Özellik 5: Hızlı Ürün Butonları**
*Herhangi bir* hızlı ürün panelinde, sistem 12-24 arası buton grid'i göstermeli, kategori değişiminde butonları güncellemeli ve buton tıklamasında ürünü sepete eklemeli
**Doğrular: Gereksinim 6.4, 6.5**

**Özellik 6: Klavye Kısayolları**
*Herhangi bir* klavye kısayolu basımında (F2: barkod odağı, F4-F7: ödeme türleri, F8-F10: işlem kısayolları, ESC: iptal, +/-: adet değiştir), sistem ilgili işlemi gerçekleştirmelidir
**Doğrular: Gereksinim 2.3, 8.5**

**Özellik 7: UI Stil ve Tema**
*Herhangi bir* UI bileşeni görüntülendiğinde, sistem turkuaz tema renklerini, büyük/net butonları, artırılmış satır yüksekliği ile belirgin tabloları, QFrame kartları ve büyük font toplamları göstermelidir
**Doğrular: Gereksinim 9.1, 9.2, 9.3, 9.4, 9.5**

**Özellik 8: Kod Kalitesi Uyumluluğu**
*Herhangi bir* POS dosyasında, sistem modüler yapı (ayrı dosyalar), 120 satır dosya limiti, 25 satır fonksiyon limiti, PEP8 uyumluluğu ve UI'da sadece servis çağrıları kurallarına uymalıdır
**Doğrular: Gereksinim 10.1, 10.2, 10.3, 10.4, 10.5**

**Özellik 9: Hata Yönetimi**
*Herhangi bir* hata durumunda, sistem turkuaz renkli hata mesajı göstermeli, log dosyasına kayıt yazmalı, spesifik hata türleri için uygun mesajları göstermeli ve kritik hatalarda çökmeden çalışmaya devam etmelidir
**Doğrular: Gereksinim 11.1, 11.2, 11.5**

**Özellik 10: Menü Entegrasyonu ve Durum Yönetimi**
*Herhangi bir* menü geçişinde sistem ekran durumunu korumalı, POS ekranı kapatıldığında sepet verilerini güvenli şekilde saklamalı ve AnaPencere entegrasyonunu sağlamalıdır
**Doğrular: Gereksinim 12.3, 12.5**

## Hata Yönetimi

### Hata Türleri ve Renk Kodları
1. **Servis Hataları**: Turkuaz (#FF6347) arka plan ile mesaj
2. **Veri Doğrulama Hataları**: Sarı (#FFD700) kenarlık ile uyarı
3. **Ağ Hataları**: Kırmızı (#FF6347) icon ile bildirim
4. **Stok Hataları**: Turuncu (#FFA500) arka plan ile uyarı
5. **Sistem Hataları**: Gri (#708090) arka plan ile log kaydı

### Hata Yönetim Stratejisi
```python
class POSHataYoneticisi:
    def __init__(self):
        self.tema = TurkuazTema()
        
    def hata_goster(self, hata_turu: str, mesaj: str):
        # Turkuaz tema ile QMessageBox
        # Log kayıt + kullanıcı bildirimi
        # Sistem durumu koruma
        pass
```

## Test Stratejisi

### Birim Testleri
- Her UI bileşeni için ayrı test sınıfı
- Sepet modeli için CRUD işlem testleri
- Klavye kısayolu handler testleri
- Tema ve stil uygulama testleri

### Özellik Tabanlı Testler
- **Test Kütüphanesi**: Hypothesis (Python için özellik tabanlı test kütüphanesi)
- **Minimum İterasyon**: Her özellik testi 100 iterasyon çalıştırılacak
- **Test Etiketleme**: Her özellik testi şu formatla etiketlenecek: '**Feature: pos-yeni-ekran-tasarimi, Property {numara}: {özellik_metni}**'

### Test Kapsamı
- **Birim Testler**: UI bileşen varlığı, klavye kısayolları, tema uygulaması
- **Özellik Testleri**: Barkod işleme, sepet yönetimi, ödeme akışları
- **Entegrasyon Testleri**: AnaPencere entegrasyonu, servis çağrıları

### Test Gereksinimleri
- Her doğruluk özelliği TEK bir özellik tabanlı test ile uygulanmalıdır
- Testler gerçek UI fonksiyonaliteyi doğrulamalı, mock kullanımı minimumda tutulmalıdır
- Test jeneratörleri UI bileşen durumlarını akıllıca kısıtlamalıdır

## QSS Stil Tanımları

### Ana Tema Stilleri
```css
/* Ana POS Ekranı */
POSSatisEkrani {
    background-color: #F8F8FF;
    font-family: 'Segoe UI', Arial, sans-serif;
}

/* Üst Bar */
UstBar {
    background-color: #20B2AA;
    border-bottom: 2px solid #48D1CC;
    padding: 10px;
    min-height: 60px;
}

/* Sepet Tablosu */
QTableView {
    background-color: white;
    border: 1px solid #708090;
    border-radius: 8px;
    gridline-color: #E0E0E0;
}

QTableView::item {
    padding: 8px;
    min-height: 40px;
}

QTableView::item:selected {
    background-color: #48D1CC;
    color: white;
}

/* Ödeme Butonları */
QPushButton.odeme-buton {
    background-color: #20B2AA;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 15px;
    font-size: 14px;
    font-weight: bold;
    min-height: 50px;
}

QPushButton.odeme-buton:hover {
    background-color: #48D1CC;
}

QPushButton.odeme-buton:pressed {
    background-color: #008B8B;
}

/* Toplam Göstergesi */
QLabel.genel-toplam {
    font-size: 24px;
    font-weight: bold;
    color: #20B2AA;
    background-color: white;
    border: 2px solid #20B2AA;
    border-radius: 8px;
    padding: 15px;
    text-align: center;
}

/* Hızlı İşlem Şeridi */
HizliIslemSeridi {
    background-color: #708090;
    border-top: 2px solid #20B2AA;
    padding: 8px;
    min-height: 60px;
}

/* Hızlı İşlem Butonları */
QPushButton.hizli-islem {
    background-color: #708090;
    color: white;
    border: 1px solid #20B2AA;
    border-radius: 6px;
    padding: 10px 15px;
    font-size: 12px;
    min-width: 100px;
}

QPushButton.hizli-islem:hover {
    background-color: #20B2AA;
}
```