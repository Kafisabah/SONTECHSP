# POS Çekirdek Modülü Tasarım Dokümanı

## Genel Bakış

POS (Point of Sale) çekirdek modülü, SONTECHSP sisteminin satış noktası işlemlerini yöneten temel bileşendir. Bu modül, barkodlu satış, sepet yönetimi, ödeme işlemleri, iade süreçleri, fiş oluşturma ve offline kuyruk yönetimi işlevlerini sağlar. Sistem, çoklu mağaza/şube ve çoklu PC eş zamanlı çalışma desteği ile tasarlanmıştır.

Modül, katmanlı mimari prensiplerine uygun olarak UI -> Service -> Repository -> Database akışını takip eder ve offline durumda SQLite tabanlı kuyruk sistemi ile iş sürekliliği sağlar.

## Mimari

### Katman Yapısı

```
pos/
├── ui/                     # PyQt6 arayüz katmanı
│   ├── sepet_ekrani.py
│   ├── odeme_ekrani.py
│   └── iade_ekrani.py
├── services/               # İş kuralları katmanı
│   ├── sepet_service.py
│   ├── odeme_service.py
│   ├── iade_service.py
│   ├── fis_service.py
│   └── offline_kuyruk_service.py
├── repositories/           # Veri erişim katmanı
│   ├── sepet_repository.py
│   ├── satis_repository.py
│   ├── iade_repository.py
│   └── offline_kuyruk_repository.py
└── database/              # Veri modelleri
    ├── models/
    │   ├── sepet.py
    │   ├── satis.py
    │   ├── iade.py
    │   └── offline_kuyruk.py
    └── migrations/
```

### Bağımlılık Yönü
- UI katmanı sadece Service katmanını çağırır
- Service katmanı Repository katmanını kullanır
- Repository katmanı Database modellerini kullanır
- Çapraz katman erişimi yasaktır

## Bileşenler ve Arayüzler

### Sepet Yönetimi
- **SepetService**: Sepet işlemlerinin iş kurallarını yönetir
- **SepetRepository**: Sepet verilerinin PostgreSQL'de saklanması
- **Sepet Model**: Sepet ve sepet satırı veri yapıları

### Ödeme İşlemleri
- **OdemeService**: Tek ve parçalı ödeme işlemlerini yönetir
- **OdemeRepository**: Ödeme kayıtlarının saklanması
- **Odeme Model**: Ödeme türleri ve tutarları

### İade İşlemleri
- **IadeService**: İade süreçlerinin iş kuralları
- **IadeRepository**: İade kayıtlarının yönetimi
- **Iade Model**: İade belgeleri ve detayları

### Fiş Yönetimi
- **FisService**: Fiş formatlaması ve yazdırma
- **FisRepository**: Fiş kayıtlarının saklanması
- **Fis Model**: Fiş içeriği ve formatı

### Offline Kuyruk
- **OfflineKuyrukService**: Network kesintilerinde işlem kuyruğu
- **OfflineKuyrukRepository**: SQLite tabanlı kuyruk yönetimi
- **OfflineKuyruk Model**: Kuyruk kayıtları

## Veri Modelleri

### Sepet Modeli
```python
class Sepet:
    id: int
    terminal_id: int
    kasiyer_id: int
    olusturma_tarihi: datetime
    durum: SepetDurum
    toplam_tutar: Decimal
    
class SepetSatiri:
    id: int
    sepet_id: int
    urun_id: int
    barkod: str
    adet: int
    birim_fiyat: Decimal
    indirim_tutari: Decimal
    toplam_tutar: Decimal
```

### Satış Modeli
```python
class Satis:
    id: int
    sepet_id: int
    terminal_id: int
    kasiyer_id: int
    satis_tarihi: datetime
    toplam_tutar: Decimal
    durum: SatisDurum
    fis_no: str
    
class SatisOdeme:
    id: int
    satis_id: int
    odeme_turu: OdemeTuru
    tutar: Decimal
    referans_no: str
```

### İade Modeli
```python
class Iade:
    id: int
    orijinal_satis_id: int
    terminal_id: int
    kasiyer_id: int
    iade_tarihi: datetime
    toplam_tutar: Decimal
    neden: str
    
class IadeSatiri:
    id: int
    iade_id: int
    urun_id: int
    adet: int
    birim_fiyat: Decimal
    toplam_tutar: Decimal
```

### Offline Kuyruk Modeli
```python
class OfflineKuyruk:
    id: int
    islem_turu: IslemTuru
    veri: JSON
    olusturma_tarihi: datetime
    durum: KuyrukDurum
    hata_mesaji: str
    deneme_sayisi: int
```

## Doğruluk Özellikleri

*Bir özellik, sistemin tüm geçerli yürütmelerinde doğru olması gereken bir karakteristik veya davranıştır - esasen, sistemin ne yapması gerektiği hakkında resmi bir ifadedir. Özellikler, insan tarafından okunabilir spesifikasyonlar ile makine tarafından doğrulanabilir doğruluk garantileri arasında köprü görevi görür.*

### Özellik 1: Barkod Doğrulama ve Sepete Ekleme
*Herhangi bir* geçerli barkod için, barkod okutulduğunda sistem ürün bilgilerini doğru şekilde getirmeli ve sepete eklemeli, sepet toplamını güncellemeli
**Doğrular: Requirements 1.1, 1.2**

### Özellik 2: Aynı Ürün Adet Artırma
*Herhangi bir* ürün için, aynı ürün tekrar sepete eklendiğinde yeni satır oluşturmak yerine mevcut satırın adedini artırmalı
**Doğrular: Requirements 1.3**

### Özellik 3: Geçersiz Barkod Hata Yönetimi
*Herhangi bir* geçersiz barkod için, sistem hata mesajı göstermeli ve sepeti değiştirmemeli
**Doğrular: Requirements 1.4**

### Özellik 4: Stok Yetersizliği Kontrolü
*Herhangi bir* stok yetersizliği durumunda, sistem uyarı vermeli ve satışa izin vermemeli
**Doğrular: Requirements 1.5**

### Özellik 5: Sepet Satırı Silme
*Herhangi bir* sepet satırı için, silme işlemi seçili satırı sepetten kaldırmalı
**Doğrular: Requirements 2.1**

### Özellik 6: Ürün Adedi Değiştirme
*Herhangi bir* ürün için, adet değiştirme işlemi yeni adedi doğrulamalı ve sepet toplamını güncellemeli
**Doğrular: Requirements 2.2**

### Özellik 7: İndirim Uygulama
*Herhangi bir* indirim tutarı için, sistem indirim tutarını sepet toplamından düşmeli
**Doğrular: Requirements 2.3**

### Özellik 8: Sepet Boşaltma
*Herhangi bir* sepet durumu için, boşaltma işlemi tüm satırları temizlemeli ve toplamı sıfırlamalı
**Doğrular: Requirements 2.4**

### Özellik 9: Tek Ödeme İşlemi
*Herhangi bir* tek ödeme yöntemi ve tutarı için, sistem ödeme tutarını doğrulamalı ve satışı tamamlamalı
**Doğrular: Requirements 3.1**

### Özellik 10: Parçalı Ödeme İşlemi
*Herhangi bir* parçalı ödeme kombinasyonu için, sistem birden fazla ödeme yöntemini kabul etmeli
**Doğrular: Requirements 3.2**

### Özellik 11: Ödeme Tutarı Eşleşmesi
*Herhangi bir* sepet ve ödeme tutarı eşleşmesi için, sistem satışı onaylamalı ve stok düşümü yapmalı
**Doğrular: Requirements 3.3**

### Özellik 12: Yetersiz Ödeme Kontrolü
*Herhangi bir* yetersiz ödeme durumu için, sistem eksik tutarı bildirmeli ve satışı tamamlamamalı
**Doğrular: Requirements 3.4**

### Özellik 13: Satış Tamamlama ve Fiş Oluşturma
*Herhangi bir* tamamlanan satış için, sistem fiş oluşturmalı ve yazdırma için hazırlamalı
**Doğrular: Requirements 3.5**

### Özellik 14: İade İşlemi Başlatma
*Herhangi bir* iade işlemi için, sistem orijinal satış kaydını doğrulamalı
**Doğrular: Requirements 4.1**

### Özellik 15: İade Tutarı Hesaplama
*Herhangi bir* iade kalemi seçimi için, sistem iade tutarını doğru hesaplamalı
**Doğrular: Requirements 4.2**

### Özellik 16: İade Onaylama
*Herhangi bir* iade onayı için, sistem stok girişi yapmalı ve iade kaydı oluşturmalı
**Doğrular: Requirements 4.3**

### Özellik 17: İade Fişi Yazdırma
*Herhangi bir* iade fişi için, sistem iade fişi formatında çıktı üretmeli
**Doğrular: Requirements 4.4**

### Özellik 18: Offline İşlem Kaydetme
*Herhangi bir* satış işlemi için, network kesintisi durumunda sistem işlemi Offline_Kuyruk'a kaydetmeli
**Doğrular: Requirements 5.1**

### Özellik 19: Offline Durum Bildirimi
*Herhangi bir* offline işlem için, sistem kullanıcıya offline durumu bildirmeli
**Doğrular: Requirements 5.2**

### Özellik 20: Kuyruk Senkronizasyonu
*Herhangi bir* kuyruk durumu için, network bağlantısı geri geldiğinde sistem kuyruktan işlemleri sırayla göndermeli
**Doğrular: Requirements 5.3**

### Özellik 21: Kuyruk Hata Yönetimi
*Herhangi bir* kuyruk işlemi hatası için, sistem hata durumunu kaydetmeli ve tekrar deneme yapmalı
**Doğrular: Requirements 5.4**

### Özellik 22: Fiş Formatlaması
*Herhangi bir* tamamlanan satış için, sistem fiş içeriğini doğru formatlamalı ve mağaza bilgileri, ürün listesi, ödeme detaylarını içermeli
**Doğrular: Requirements 6.1, 6.2**

### Özellik 23: Fiş Yazdırma
*Herhangi bir* fiş yazdırma işlemi için, sistem Fiş_Yazıcı'ya metin formatında göndermeli
**Doğrular: Requirements 6.3**

### Özellik 24: Yazdırma Hata Yönetimi
*Herhangi bir* yazdırma hatası için, sistem hata mesajı göstermeli ve fiş içeriğini saklamalı
**Doğrular: Requirements 6.4**

### Özellik 25: Eş Zamanlı Stok Kilitleme
*Herhangi bir* eş zamanlı satış durumu için, birden fazla terminal aynı ürünü satmaya çalıştığında sistem stok kilitleme uygulamalı
**Doğrular: Requirements 7.1**

### Özellik 26: Güncel Stok Kontrolü
*Herhangi bir* stok kontrolü için, sistem güncel stok durumunu Stok_Servisi'nden almalı
**Doğrular: Requirements 7.2**

### Özellik 27: Stok Yetersizliği İptal
*Herhangi bir* stok yetersizliği durumu için, sistem satış işlemini iptal etmeli ve stok kilidini serbest bırakmalı
**Doğrular: Requirements 7.3**

### Özellik 28: Transaction Stok Düşümü
*Herhangi bir* satış tamamlama işlemi için, sistem transaction içinde stok düşümü yapmalı
**Doğrular: Requirements 7.4**

### Özellik 29: Satış İptal Süreci
*Herhangi bir* satış iptal işlemi için, sistem iptal nedenini sormalı ve onaylandığında sepeti temizlemeli, satış kaydını iptal durumuna getirmeli
**Doğrular: Requirements 8.1, 8.2**

### Özellik 30: Stok Rezervasyon Serbest Bırakma
*Herhangi bir* stok rezervasyonu için, iptal işleminde sistem stok rezervasyonunu serbest bırakmalı
**Doğrular: Requirements 8.3**

### Özellik 31: İptal Sonrası Hazır Duruma Geçme
*Herhangi bir* iptal tamamlama işlemi için, sistem yeni satış için hazır duruma geçmeli
**Doğrular: Requirements 8.4**

## Hata Yönetimi

### Hata Türleri
- **BarkodHatasi**: Geçersiz veya bulunamayan barkod durumları
- **StokHatasi**: Yetersiz stok veya stok kilitleme hataları
- **OdemeHatasi**: Ödeme işlemi ve tutar doğrulama hataları
- **IadeHatasi**: İade işlemi ve orijinal satış doğrulama hataları
- **NetworkHatasi**: Bağlantı kesintisi ve offline kuyruk hataları
- **YazdirmaHatasi**: Fiş yazdırma ve yazıcı bağlantı hataları

### Hata Yönetim Stratejisi
- Tüm kritik işlemler try-catch blokları ile korunur
- Hata mesajları kullanıcı dostu ve Türkçe olarak gösterilir
- Sistem durumu hata sonrasında tutarlı kalır
- Offline durumda işlemler kuyrukta saklanır
- Hata logları detaylı olarak kaydedilir

## Test Stratejisi

### İkili Test Yaklaşımı

Sistem hem birim testleri hem de özellik tabanlı testler ile kapsamlı şekilde test edilecektir:

**Birim Testleri:**
- Belirli örnekleri ve kenar durumları doğrular
- Bileşenler arası entegrasyon noktalarını test eder
- Hata durumlarını ve istisna senaryolarını kapsar

**Özellik Tabanlı Testler:**
- Tüm girdiler üzerinde geçerli olması gereken evrensel özellikleri doğrular
- Python Hypothesis kütüphanesi kullanılacak
- Her özellik tabanlı test minimum 100 iterasyon çalıştırılacak
- Her test, tasarım dokümanındaki ilgili özelliği açıkça referans alacak
- Test etiketleme formatı: '**Feature: pos-cekirdek-modulu, Property {numara}: {özellik_metni}**'

**Test Kapsamı:**
- Sepet yönetimi işlemleri
- Ödeme süreçleri (tek ve parçalı)
- İade işlemleri
- Offline kuyruk yönetimi
- Fiş oluşturma ve yazdırma
- Eş zamanlı stok kontrolü
- Hata durumları ve kurtarma

Her doğruluk özelliği için ayrı bir özellik tabanlı test implementasyonu yapılacak ve bu testler ilgili özellik numarası ile etiketlenecektir.