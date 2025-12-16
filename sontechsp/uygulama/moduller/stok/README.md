# SONTECHSP Gelişmiş Stok Yönetimi Sistemi

## Genel Bakış

Bu modül, SONTECHSP için gelişmiş stok yönetimi sistemini içerir. Çoklu mağaza/depo ortamında çalışan, eş zamanlı erişimi destekleyen, negatif stok kontrolü yapan ve POS ile e-ticaret entegrasyonu sağlayan kapsamlı bir stok yönetimi çözümüdür.

## Özellikler

### Temel Özellikler
- ✅ Ürün yönetimi (CRUD işlemleri)
- ✅ Çoklu barkod desteği
- ✅ Stok hareket takibi (giriş/çıkış/sayım/transfer)
- ✅ Negatif stok kontrolü
- ✅ Eş zamanlı erişim kontrolü (PostgreSQL SELECT FOR UPDATE)
- ✅ Stok rezervasyon sistemi

### Gelişmiş Özellikler
- ✅ Property-based testing ile doğruluk garantisi
- ✅ Katmanlı mimari (UI -> Service -> Repository -> DB)
- ✅ Comprehensive error handling
- ✅ Transaction yönetimi
- ✅ Kritik stok uyarıları

## Mimari

```
┌─────────────────────────────────────────┐
│              UI Katmanı                 │
│         (PyQt6 Arayüzleri)             │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│            Servis Katmanı               │
│        (İş Kuralları & Akış)           │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          Repository Katmanı             │
│        (Veri Erişim Katmanı)           │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          Veritabanı Katmanı             │
│    (SQLAlchemy Modeller & Alembic)     │
└─────────────────────────────────────────┘
```

## Kullanım

### Temel Kullanım

```python
from sontechsp.uygulama.moduller.stok import StokYonetimService, UrunDTO

# Ana servis
stok_service = StokYonetimService()

# Ürün ekleme
urun = UrunDTO(
    urun_kodu="URN001",
    urun_adi="Test Ürün",
    birim="adet",
    kdv_orani=18.00
)

urun_id = stok_service.urun_service.urun_ekle(urun)
```

### Stok Hareketi

```python
from sontechsp.uygulama.moduller.stok import StokHareketDTO

# Stok giriş hareketi
hareket = StokHareketDTO(
    urun_id=urun_id,
    magaza_id=1,
    hareket_tipi="GIRIS",
    miktar=100.0000,
    birim_fiyat=25.50
)

hareket_id = stok_service.stok_hareket_yap_ve_bakiye_guncelle(hareket)
```

## Testler

Sistem kapsamlı test edilmiştir:

### Property-Based Testler
- Ürün kayıt tutarlılığı
- Barkod benzersizliği
- Stok hareket tutarlılığı
- Eş zamanlı erişim kontrolü
- Transaction tutarlılığı

### Unit Testler
- Repository katmanı testleri
- Service katmanı testleri
- Hata durumu testleri

## Veritabanı

### Tablolar
- `urunler`: Ürün ana bilgileri
- `urun_barkodlari`: Ürün barkod bilgileri
- `stok_bakiyeleri`: Mağaza/depo bazında stok bakiyeleri
- `stok_hareketleri`: Tüm stok giriş/çıkış hareketleri

### Migration
```bash
# Migration çalıştırma
alembic upgrade head
```

## Geliştirici Notları

### Katman Kuralları
- UI katmanı repository/database import edemez
- Services katmanı UI import edemez
- Repositories katmanı services/ui import edemez

### Performans
- PostgreSQL row-level lock ile eş zamanlı erişim
- Index'ler performans için optimize edildi
- Transaction yönetimi ile veri tutarlılığı

### Hata Yönetimi
- Özel hata sınıfları ile detaylı hata bilgisi
- Validation hatalarında çoklu hata mesajı
- Rollback mekanizması ile veri tutarlılığı

## Sürüm

**Versiyon:** 0.1.0  
**Son Güncelleme:** 2024-12-16  
**Durum:** Tamamlandı ✅