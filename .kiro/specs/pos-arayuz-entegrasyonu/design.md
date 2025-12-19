# POS Arayüz Entegrasyonu - Tasarım Belgesi

## Genel Bakış

Bu belge, SONTECHSP sisteminde POS arayüzünün AnaPencere'ye tam entegrasyonu ve gerçek POS ekranının teknik tasarımını açıklar. Mevcut POS altyapısı üzerine inşa edilerek, modüler ve bakım yapılabilir bir arayüz oluşturulacaktır.

## Mimari

### Katman Yapısı
```
ui/pos/
├── pos_ana_ekran.py          # Ana POS container
├── bilesenler/
│   ├── barkod_paneli.py      # Barkod giriş alanı
│   ├── sepet_tablosu.py      # Sepet görüntüleme
│   ├── odeme_paneli.py       # Ödeme türleri
│   ├── hizli_urun_paneli.py  # Hızlı ürün butonları
│   ├── islem_kisayollari.py  # İşlem butonları
│   └── eslestime_dialog.py   # Buton eşleştirme tablosu
└── handlers/
    ├── pos_handler.py        # Ana POS olayları
    ├── sepet_handler.py      # Sepet işlemleri
    ├── odeme_handler.py      # Ödeme işlemleri
    └── kisayol_handler.py    # Klavye kısayolları
```

### Entegrasyon Noktaları
- **AnaPencere**: QStackedWidget'a POS ekranı ekleme
- **Sol Menü**: "POS Satış" menü öğesi ekleme
- **Servis Katmanı**: Mevcut POS servislerini kullanma
- **Klavye Yönetimi**: Global kısayol sistemi

## Bileşenler ve Arayüzler

### Ana POS Ekranı (pos_ana_ekran.py)
```python
class POSAnaEkran(QWidget):
    def __init__(self):
        # Ana layout: Grid (3x3)
        # Sol üst: Barkod paneli (barkod alanı + EKLE butonu)
        # Sol orta: Sepet tablosu (Barkod, Ürün, Adet, Fiyat, Tutar, Sil kolonları)
        # Sol alt: Ödeme paneli (AraToplam, İndirim, GenelToplam + ödeme butonları)
        # Sağ üst: Hızlı ürün paneli (12-24 buton + kategori seçici)
        # Sağ alt: İşlem kısayolları (BEKLET, BEKLEYENLER, İADE, İPTAL, FİŞ, FATURA)
        # En alt: Eşleştirme tablosu butonu
```

### Bileşen Arayüzleri
```python
# Temel bileşen arayüzü
class POSBilesenArayuzu(ABC):
    @abstractmethod
    def baslat(self) -> None: pass
    
    @abstractmethod
    def temizle(self) -> None: pass
    
    @abstractmethod
    def guncelle(self, veri: Dict) -> None: pass
    
    @abstractmethod
    def klavye_kisayolu_isle(self, tus: str) -> bool: pass

# Klavye kısayolu yöneticisi
class KlavyeKisayolYoneticisi:
    def __init__(self):
        self.kisayollar = {
            'F2': self.barkod_odakla,
            'F4': self.nakit_odeme,
            'F5': self.kart_odeme,
            'Escape': self.islem_iptal,
            'Delete': self.satir_sil
        }
```

### Sinyal/Slot Sistemi
```python
# Ana sinyaller
class POSSinyalleri(QObject):
    urun_eklendi = pyqtSignal(dict)      # Ürün sepete eklendi
    sepet_guncellendi = pyqtSignal(list) # Sepet değişti
    sepet_satir_silindi = pyqtSignal(int) # Sepet satırı silindi
    odeme_baslatildi = pyqtSignal(str)   # Ödeme türü seçildi
    islem_tamamlandi = pyqtSignal(dict)  # Satış tamamlandı
    sepet_bekletildi = pyqtSignal(str)   # Sepet bekletildi
    bekletilen_sepet_acildi = pyqtSignal(str) # Bekletilen sepet açıldı
    iade_baslatildi = pyqtSignal()       # İade işlemi başlatıldı
    fis_yazdirildi = pyqtSignal(dict)    # Fiş yazdırıldı
    hata_olustu = pyqtSignal(str)        # Hata mesajı
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
    nakit_tutar: Optional[Decimal] = None  # Parçalı ödeme için
    kart_tutar: Optional[Decimal] = None   # Parçalı ödeme için
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
    
@dataclass
class BekletilenSepet:
    sepet_id: str
    olusturma_zamani: datetime
    sepet_ogeleri: List[SepetOgesi]
    toplam_tutar: Decimal
    kasiyer_id: int
```

## Doğruluk Özellikleri

*Bir özellik, sistemin tüm geçerli çalıştırmalarında doğru olması gereken bir karakteristik veya davranıştır - esasen, sistemin ne yapması gerektiği hakkında resmi bir ifadedir. Özellikler, insan tarafından okunabilir spesifikasyonlar ile makine tarafından doğrulanabilir doğruluk garantileri arasında köprü görevi görür.*
### Özellik Yansıması

Prework analizini gözden geçirdikten sonra, aşağıdaki özellik konsolidasyonları belirlenmiştir:

**Birleştirilebilir Özellikler:**
- Kod kalitesi kuralları (dosya boyutu, fonksiyon boyutu, PEP8) - tek kapsamlı özellikte birleştirilebilir
- Hata yönetimi davranışları - genel hata yönetimi özelliğinde birleştirilebilir

**Benzersiz Değer Sağlayan Özellikler:**
- UI bileşen varlığı özellikleri (menü entegrasyonu, ekran bileşenleri)
- İş akışı özellikleri (sepet yönetimi, ödeme işlemleri, bekletme)
- Klavye kısayolu özellikleri (her kısayol benzersiz davranış)
- Mimari uyumluluk özellikleri

## Doğruluk Özellikleri

**Özellik 1: Menü Entegrasyonu**
*Herhangi bir* uygulama başlatma durumunda, AnaPencere sol menüsünde "POS Satış" seçeneği görünür olmalı ve tıklandığında POS ekranı açılmalıdır
**Doğrular: Gereksinim 1.1, 1.2**

**Özellik 2: POS Ekran Bileşenleri**
*Herhangi bir* POS ekranı açılışında, sistem barkod alanı, sepet tablosu, ödeme paneli, hızlı ürün paneli ve işlem kısayolları panelini göstermelidir
**Doğrular: Gereksinim 2.1, 3.2, 4.1, 4.2, 5.1, 6.1**

**Özellik 3: Barkod İşleme**
*Herhangi bir* geçerli barkod girişinde, sistem ürünü sepete eklemeli; geçersiz barkod girişinde hata mesajı göstermelidir
**Doğrular: Gereksinim 2.2, 2.3, 2.4**

**Özellik 4: Sepet Yönetimi**
*Herhangi bir* sepet işleminde (ekleme, silme, güncelleme), sistem sepet tablosunu güncellemeli ve boş durumda "Sepet boş" mesajını göstermelidir
**Doğrular: Gereksinim 3.1, 3.4, 3.5**

**Özellik 5: Ödeme Türü Yönetimi**
*Herhangi bir* ödeme türü seçiminde, sistem ilgili ödeme arayüzünü göstermeli (nakit için para üstü hesaplama, parçalı için dialog, açık hesap için müşteri kontrolü)
**Doğrular: Gereksinim 4.3, 4.4, 4.5**

**Özellik 6: Hızlı Ürün Butonları**
*Herhangi bir* hızlı ürün panelinde, sistem 12-24 arası buton göstermeli, kategori değişiminde butonları güncellemeli ve boş butonlarda "Tanımsız" etiketi göstermelidir
**Doğrular: Gereksinim 5.1, 5.2, 5.4, 5.5**

**Özellik 7: İşlem Kısayolları**
*Herhangi bir* işlem kısayolu kullanımında, sistem ilgili işlemi gerçekleştirmeli (bekletme, iade dialog, fiş yazdırma)
**Doğrular: Gereksinim 6.2, 6.3, 6.4, 6.5**

**Özellik 8: Klavye Kısayolları**
*Herhangi bir* klavye kısayolu basımında, sistem ilgili işlemi gerçekleştirmelidir (F2: barkod odağı, F4: nakit ödeme, F5: kart ödeme, ESC: iptal, DEL: satır silme)
**Doğrular: Gereksinim 7.1, 7.2, 7.3, 7.4, 7.5**

**Özellik 9: Eşleştirme Tablosu**
*Herhangi bir* eşleştirme tablosu işleminde, sistem buton-handler-servis ilişkilerini göstermeli, otomatik güncellemeli ve CSV dışa aktarımını desteklemelidir
**Doğrular: Gereksinim 8.1, 8.2, 8.3, 8.4, 8.5**

**Özellik 10: Kod Kalitesi Uyumluluğu**
*Herhangi bir* POS dosyasında, sistem 120 satır dosya limiti, 25 satır fonksiyon limiti ve PEP8 standartlarına uyum sağlamalıdır
**Doğrular: Gereksinim 9.2, 9.3, 9.4**

**Özellik 11: Mimari Uyumluluk**
*Herhangi bir* UI bileşeninde, sistem iş kuralı içermemeli ve sadece servis katmanı çağrıları yapmalıdır
**Doğrular: Gereksinim 9.1, 9.5**

**Özellik 12: Hata Yönetimi**
*Herhangi bir* hata durumunda, sistem uygun mesajı göstermeli, log kaydı oluşturmalı ve çökmeden çalışmaya devam etmelidir
**Doğrular: Gereksinim 10.1, 10.2, 10.3, 10.4, 10.5**

## Hata Yönetimi

### Hata Türleri
1. **Servis Hataları**: Backend servis çağrısı başarısızlıkları
2. **Veri Doğrulama Hataları**: Geçersiz barkod, eksik müşteri bilgisi
3. **Ağ Hataları**: Bağlantı kesintileri
4. **İş Kuralı Hataları**: Stok yetersizliği, yetki eksikliği
5. **Sistem Hataları**: Beklenmeyen durumlar

### Hata Yönetim Stratejisi
```python
class POSHataYoneticisi:
    def hata_yakala(self, hata: Exception, kaynak: str):
        # 1. Log kaydet
        self.logger.error(f"{kaynak}: {str(hata)}")
        
        # 2. Kullanıcı mesajı göster
        self.mesaj_goster(self.hata_mesaji_olustur(hata))
        
        # 3. Sistem durumunu koru
        self.sistem_durumu_koru()
```

## Test Stratejisi

### Birim Testleri
- Her UI bileşeni için ayrı test sınıfı
- Handler fonksiyonları için mock servis testleri
- Veri modelleri için doğrulama testleri
- Hata senaryoları için exception testleri

### Özellik Tabanlı Testler
- **Test Kütüphanesi**: Hypothesis (Python için özellik tabanlı test kütüphanesi)
- **Minimum İterasyon**: Her özellik testi 100 iterasyon çalıştırılacak
- **Test Etiketleme**: Her özellik testi şu formatla etiketlenecek: '**Feature: pos-arayuz-entegrasyonu, Property {numara}: {özellik_metni}**'

### Test Kapsamı
- **Birim Testler**: Spesifik örnekleri ve edge case'leri doğrular
- **Özellik Testleri**: Tüm girdiler üzerinde genel doğruluğu doğrular
- **Entegrasyon Testleri**: Bileşenler arası etkileşimi test eder

### Test Gereksinimleri
- Her doğruluk özelliği TEK bir özellik tabanlı test ile uygulanmalıdır
- Testler gerçek fonksiyonaliteyi doğrulamalı, mock kullanımı minimumda tutulmalıdır
- Test jeneratörleri giriş alanını akıllıca kısıtlamalıdır