# Değişiklik Geçmişi

Bu dosya SONTECHSP projesinin tüm önemli değişikliklerini içerir.

Format [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) standardına uygun olarak hazırlanmıştır.

## [Yayınlanmamış]

### Eklenen
- Gelişmiş Stok Yönetimi Sistemi
  - Ürün yönetimi (CRUD işlemleri)
  - Çoklu barkod desteği ve benzersizlik kontrolü
  - Stok hareket takibi (giriş/çıkış/sayım/transfer)
  - Negatif stok kontrolü (0: uyarı, -1 ile -5: uyarı+izin, <-5: engel)
  - Eş zamanlı erişim kontrolü (PostgreSQL SELECT FOR UPDATE)
  - Stok rezervasyon sistemi (e-ticaret entegrasyonu için)
  - Kritik stok uyarı sistemi
  - Stok raporlama ve CSV export
  - Property-based testing ile 20 doğruluk özelliği
  - Kapsamlı hata yönetimi ve validation
  - Transaction yönetimi ve rollback mekanizması

### Teknik Detaylar
- **Katmanlı Mimari**: UI -> Service -> Repository -> Database
- **Veri Modelleri**: Urun, UrunBarkod, StokBakiye, StokHareket
- **Migration**: Alembic ile stok tabloları migration'ı
- **DTO Sınıfları**: UrunDTO, BarkodDTO, StokHareketDTO, StokRaporDTO
- **Hata Yönetimi**: Özel hata sınıfları ve çoklu validation
- **Repository Pattern**: Arayüzler ve implementasyonlar
- **Servis Katmanı**: İş kuralları ve koordinasyon
- **Property-Based Testler**: Hypothesis ile doğruluk testleri

### Dosya Yapısı
```
sontechsp/uygulama/moduller/stok/
├── dto/                    # Veri transfer objeleri
├── hatalar/               # Hata yönetimi sınıfları  
├── depolar/               # Repository katmanı
├── servisler/             # Servis katmanı
├── README.md              # Modül dokümantasyonu
└── __init__.py           # Modül exports

tests/                     # Property-based testler
├── test_urun_property.py
├── test_barkod_property.py
├── test_stok_hareket_property.py
├── test_coklu_barkod_property.py
├── test_barkod_hata_property.py
├── test_es_zamanli_erisim_property.py
└── test_transaction_property.py

sontechsp/uygulama/veritabani/gocler/versions/
└── 20241216_1400_002_stok_tablolari.py  # Stok migration
```

### Performans ve Güvenlik
- PostgreSQL row-level lock ile eş zamanlı erişim güvenliği
- Index'ler ile optimize edilmiş sorgular
- Transaction yönetimi ile veri tutarlılığı
- Validation ile veri bütünlüğü koruması
- Rollback mekanizması ile hata durumu yönetimi

## [0.1.0] - 2024-12-16

### Eklenen
- İlk proje iskeleti ve klasör yapısı
- PyQt6 entegrasyonu
- PostgreSQL + SQLite veritabanı desteği
- Alembic migration sistemi
- Property-based testing altyapısı (Hypothesis)
- Temel çekirdek modüller (ayarlar, kayıt, hatalar, yetki, oturum)
- Modüler mimari yapısı
- Katmanlı mimari (UI -> Service -> Repository -> Database)

### Teknik Altyapı
- Python 3.9+ desteği
- SQLAlchemy 2.0+ ORM
- FastAPI backend servisi
- PyInstaller build sistemi
- pytest test framework'ü
- Pre-commit hooks
- Code quality tools (black, isort, flake8, mypy)

### Dokümantasyon
- Kapsamlı README.md
- Kurulum talimatları
- Geliştirme ortamı kurulumu
- PyInstaller build notları
- Sorun giderme rehberi

---

## Sürüm Notları

### Semantic Versioning
Bu proje [Semantic Versioning](https://semver.org/) standardını takip eder:
- **MAJOR**: Geriye uyumsuz API değişiklikleri
- **MINOR**: Geriye uyumlu yeni özellikler
- **PATCH**: Geriye uyumlu hata düzeltmeleri

### Değişiklik Kategorileri
- **Eklenen**: Yeni özellikler
- **Değiştirilen**: Mevcut işlevsellikte değişiklikler
- **Kullanımdan Kaldırılan**: Yakında kaldırılacak özellikler
- **Kaldırılan**: Artık mevcut olmayan özellikler
- **Düzeltilen**: Hata düzeltmeleri
- **Güvenlik**: Güvenlik açıkları için düzeltmeler