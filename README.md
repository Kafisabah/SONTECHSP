# SONTECHSP - Çoklu Mağaza POS + ERP + CRM Sistemi

## Genel Bakış

SONTECHSP, Windows üzerinde çalışan, çoklu mağaza/şube ve çoklu PC ile eş zamanlı çalışabilen modern Hızlı Satış (POS) + ERP + CRM sistemidir. PyQt6 tabanlı masaüstü arayüzü ile kullanıcı dostu deneyim sunar.

### Temel Özellikler

- **Çoklu Mağaza/Şube Desteği**: Merkezi veritabanı ile birden fazla mağaza yönetimi
- **Eş Zamanlı Çalışma**: PostgreSQL tabanlı çoklu PC desteği
- **Offline POS**: SQLite cache ile internet bağlantısı olmadan satış
- **Entegrasyonlar**: E-ticaret, pazaryerleri, e-Fatura/e-Arşiv/e-İrsaliye, kargo
- **Modüler Yapı**: Stok, POS, CRM, Satış Belgeleri, E-ticaret, E-belge, Kargo, Raporlar

## Teknoloji Yığını

- **Programlama Dili**: Python 3.9+
- **GUI Framework**: PyQt6
- **Backend**: FastAPI (lokalde servis)
- **Veritabanı**: PostgreSQL (ana) + SQLite (POS offline cache)
- **ORM**: SQLAlchemy 2.0+
- **Migration**: Alembic
- **Paketleme**: PyInstaller (Windows)
- **Test**: pytest + hypothesis (Property-Based Testing)

## Sistem Gereksinimleri

### Minimum Gereksinimler

- **İşletim Sistemi**: Windows 10 (64-bit) veya üzeri
- **Python**: 3.9 veya üzeri
- **RAM**: 4 GB (8 GB önerilir)
- **Disk Alanı**: 2 GB boş alan
- **Ekran Çözünürlüğü**: 1366x768 (1920x1080 önerilir)

### Veritabanı Gereksinimleri

#### PostgreSQL (Ana Veritabanı)
- **Sürüm**: PostgreSQL 12+ 
- **Kurulum**: [PostgreSQL İndirme Sayfası](https://www.postgresql.org/download/windows/)
- **Yapılandırma**: UTF-8 encoding, Turkish locale desteği
- **Bağlantı**: TCP/IP bağlantısı aktif olmalı (port 5432)

#### SQLite (POS Offline Cache)
- Python ile birlikte gelir, ayrı kurulum gerekmez
- Otomatik olarak yerel dosya sisteminde oluşturulur

## Kurulum Talimatları

### 1. Python Kurulumu

```bash
# Python 3.9+ indirin ve kurun
# https://www.python.org/downloads/windows/

# Python sürümünü kontrol edin
python --version
```

### 2. Proje İndirme ve Kurulum

```bash
# Projeyi klonlayın
git clone https://github.com/sontechsp/sontechsp.git
cd sontechsp

# Sanal ortam oluşturun (önerilir)
python -m venv venv
venv\Scripts\activate

# Bağımlılıkları yükleyin
pip install -e .

# Geliştirme bağımlılıklarını yükleyin (opsiyonel)
pip install -e .[dev]
```

### 3. PostgreSQL Kurulumu ve Yapılandırması

```bash
# PostgreSQL'i indirin ve kurun
# https://www.postgresql.org/download/windows/

# Kurulum sonrası:
# 1. pgAdmin ile bağlantı test edin
# 2. Yeni veritabanı oluşturun: sontechsp_db
# 3. Kullanıcı oluşturun: sontechsp_user
```

### 4. Veritabanı Yapılandırması

```bash
# .env dosyası oluşturun (kök dizinde)
DATABASE_URL=postgresql://sontechsp_user:password@localhost:5432/sontechsp_db
SQLITE_PATH=data/pos_cache.db
LOG_LEVEL=INFO
```

### 5. İlk Kurulum ve Bootstrap

SONTECHSP otomatik kurulum sistemi ile tüm hazırlık işlemleri tek komutla tamamlanır:

```bash
# Otomatik kurulum ve yapılandırma
python -m uygulama.kurulum.baslat

# Bu komut otomatik olarak:
# 1. Gerekli klasörleri oluşturur (veri, loglar, yedekler, raporlar)
# 2. config.json ayar dosyasını hazırlar
# 3. PostgreSQL bağlantısını test eder
# 4. Alembic migration'larını çalıştırır (uygulama/veritabani/gocler dizininden)
# 5. Varsayılan admin kullanıcısını oluşturur (admin/admin123)

# Uygulamayı başlatın
python -m uygulama.ana
```

#### Yapılandırma Dosyası (config.json)

İlk kurulum sonrası proje kök dizininde `config.json` dosyası otomatik oluşturulur:

```json
{
  "veritabani_url": "postgresql://kullanici:sifre@localhost:5432/sontechsp",
  "ortam": "dev",
  "log_seviyesi": "INFO"
}
```

**Kurulum Detayları:**
- **Klasör Yapısı**: Sistem otomatik olarak veri/, loglar/, yedekler/, raporlar/ klasörlerini oluşturur
- **İdempotent İşlemler**: Kurulum birden fazla kez çalıştırılabilir, mevcut ayarlar korunur
- **Hata Yönetimi**: Her adımda detaylı hata mesajları ve çözüm önerileri
- **Migration Yönetimi**: Alembic programatik olarak çalıştırılır, manuel komut gerekmez
- **Güvenlik**: Şifreler bcrypt ile hashlenir

**Önemli**: Güvenlik için varsayılan admin şifresini (admin123) ilk girişten sonra değiştirin!

## Geliştirme Ortamı Kurulumu

### Gerekli Araçlar

```bash
# Geliştirme bağımlılıklarını yükleyin
pip install -e .[dev]

# Pre-commit hook'larını kurun
pre-commit install

# Testleri çalıştırın
pytest

# Kod kalitesi kontrolü
black .
isort .
flake8 .
mypy .
```

### Test Çalıştırma

```bash
# Tüm testleri çalıştır
pytest

# Property-based testleri çalıştır
pytest -m property

# Coverage raporu ile
pytest --cov=sontechsp --cov-report=html

# Belirli bir test dosyası
pytest sontechsp/testler/test_stok.py -v
```

## PyInstaller Build Notları

### Windows Executable Oluşturma

```bash
# Build bağımlılıklarını yükleyin
pip install -e .[build]

# Executable oluşturun
pyinstaller --clean sontechsp.spec

# Veya otomatik build scripti
python scripts/build_windows.py
```

### Build Yapılandırması

PyInstaller yapılandırması `pyproject.toml` dosyasında tanımlanmıştır:

- **Hidden Imports**: PyQt6, SQLAlchemy dialects, psycopg2, Alembic
- **Data Files**: Migration dosyaları, assets
- **Exclude Modules**: tkinter, matplotlib (boyut optimizasyonu)

### Build Sorunları ve Çözümleri

#### PyQt6 Import Hataları
```bash
# PyQt6 modüllerini manuel olarak dahil edin
--hidden-import=PyQt6.QtCore
--hidden-import=PyQt6.QtGui
--hidden-import=PyQt6.QtWidgets
```

#### PostgreSQL Driver Hataları
```bash
# psycopg2 binary'yi dahil edin
--hidden-import=psycopg2
--collect-binaries=psycopg2
```

#### SQLAlchemy Dialect Hataları
```bash
# Veritabanı dialect'larını dahil edin
--hidden-import=sqlalchemy.dialects.postgresql
--hidden-import=sqlalchemy.dialects.sqlite
```

## Çalıştırma Rehberi

### Normal Çalıştırma

```bash
# Ana uygulamayı başlat
python -m sontechsp.uygulama.ana

# Veya executable ile
sontechsp.exe
```

### Geliştirme Modu

```bash
# Debug modu ile
python -m sontechsp.uygulama.ana --debug

# Belirli modül ile
python -m sontechsp.uygulama.ana --module=pos

# Test veritabanı ile
python -m sontechsp.uygulama.ana --test-db
```

### Kurulum Yardımcısı

```bash
# İlk kurulum sihirbazı (otomatik bootstrap)
python -m uygulama.kurulum.baslat

# Kurulum adımları:
# 1. Klasör oluşturma (idempotent)
# 2. Ayar dosyası hazırlama (mevcut korunur)
# 3. PostgreSQL bağlantı testi
# 4. Alembic migration çalıştırma
# 5. Admin kullanıcı oluşturma (mevcut korunur)

# Manuel migration çalıştırma
python -c "from uygulama.kurulum.veritabani_kontrol import gocleri_calistir; gocleri_calistir('.')"
```

## Proje Yapısı

```
sontechsp/
├── uygulama/                   # Ana uygulama kodu
│   ├── ana.py                  # Giriş noktası
│   ├── cekirdek/               # Çekirdek sistem bileşenleri
│   │   ├── ayarlar.py          # Yapılandırma yönetimi
│   │   ├── kayit.py            # Log sistemi
│   │   ├── hatalar.py          # Hata sınıfları
│   │   ├── yetki.py            # Rol/yetki sistemi
│   │   └── oturum.py           # Oturum yönetimi
│   ├── veritabani/             # Veritabanı katmanı
│   │   ├── modeller/           # SQLAlchemy modelleri
│   │   ├── depolar/            # Repository pattern
│   │   ├── baglanti.py         # DB bağlantı yönetimi
│   │   └── gocler/             # Alembic migrations
│   ├── moduller/               # İş modülleri
│   │   ├── stok/               # Stok yönetimi
│   │   ├── pos/                # Hızlı satış
│   │   ├── crm/                # Müşteri ilişkileri
│   │   ├── satis_belgeleri/    # Satış belgeleri
│   │   ├── eticaret/           # E-ticaret entegrasyonu
│   │   ├── ebelge/             # E-belge entegrasyonu
│   │   ├── kargo/              # Kargo entegrasyonu
│   │   └── raporlar/           # Raporlama
│   ├── servisler/              # İş mantığı katmanı
│   ├── arayuz/                 # PyQt6 UI bileşenleri
│   └── kurulum/                # Kurulum ve yapılandırma
├── testler/                    # Test dosyaları
├── pyproject.toml              # Proje yapılandırması
└── README.md                   # Bu dosya
```

## Katkıda Bulunma

### Kod Standartları

- **PEP8**: Zorunlu kod formatı
- **Dosya Limiti**: Maksimum 120 satır (yorumlar hariç)
- **Fonksiyon Limiti**: Maksimum 25 satır
- **Dokümantasyon**: Türkçe inline açıklamalar
- **Test Coverage**: Minimum %80

### Geliştirme Süreci

1. Fork yapın ve feature branch oluşturun
2. Kod değişikliklerini yapın
3. Testleri çalıştırın ve geçtiğinden emin olun
4. Pre-commit hook'larını çalıştırın
5. Pull request oluşturun

### Test Yazma

```python
# Unit test örneği
def test_stok_ekleme():
    stok_servisi = StokServisi()
    urun = stok_servisi.urun_ekle("Test Ürün", "12345")
    assert urun.ad == "Test Ürün"

# Property-based test örneği
@given(st.text(min_size=1))
def test_urun_adi_property(urun_adi):
    stok_servisi = StokServisi()
    urun = stok_servisi.urun_ekle(urun_adi, "12345")
    assert urun.ad == urun_adi
```

## Sorun Giderme

### Yaygın Sorunlar

#### PyQt6 Import Hatası
```bash
# Çözüm: PyQt6'yı yeniden yükleyin
pip uninstall PyQt6
pip install PyQt6>=6.5.0
```

#### PostgreSQL Bağlantı Hatası
```bash
# Çözüm: Bağlantı ayarlarını kontrol edin
# 1. PostgreSQL servisinin çalıştığından emin olun
# 2. .env dosyasındaki DATABASE_URL'yi kontrol edin
# 3. Firewall ayarlarını kontrol edin
```

#### Migration Hatası
```bash
# Çözüm: Migration'ları sıfırlayın
python -m alembic stamp head
python -m alembic revision --autogenerate -m "Initial migration"
python -m alembic upgrade head
```

### Log Dosyaları

- **Uygulama Logları**: `logs/sontechsp.log`
- **Hata Logları**: `logs/errors.log`
- **POS Logları**: `logs/pos.log`
- **Veritabanı Logları**: `logs/database.log`

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## İletişim

- **Web Sitesi**: https://sontechsp.com
- **Dokümantasyon**: https://docs.sontechsp.com
- **Destek**: support@sontechsp.com
- **Geliştirici**: dev@sontechsp.com

## Sürüm Geçmişi

### v0.1.0 (Geliştirme)
- İlk proje iskeleti
- Temel klasör yapısı
- PyQt6 entegrasyonu
- PostgreSQL + SQLite desteği
- Property-based testing altyapısı
- **Gelişmiş Stok Yönetimi Sistemi** ✅
  - Ürün yönetimi (CRUD işlemleri)
  - Çoklu barkod desteği
  - Stok hareket takibi (giriş/çıkış/sayım/transfer)
  - Negatif stok kontrolü
  - Eş zamanlı erişim kontrolü (PostgreSQL SELECT FOR UPDATE)
  - Stok rezervasyon sistemi
  - 20 Property-based test ile doğruluk garantisi