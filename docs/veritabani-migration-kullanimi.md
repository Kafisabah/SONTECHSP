# SONTECHSP Veritabanı Migration Kullanım Rehberi

## Genel Bakış

Bu dokümantasyon SONTECHSP projesi için veritabanı migration sisteminin kullanımını açıklar. Sistem Alembic tabanlı olup PostgreSQL ve SQLite desteği sağlar.

## Kurulum ve Yapılandırma

### 1. Veritabanı Bağlantısı

```python
from sontechsp.uygulama.veritabani.baglanti import postgresql_session, sqlite_session

# PostgreSQL kullanımı
with postgresql_session() as session:
    # Veritabanı işlemleri
    pass

# SQLite kullanımı (offline POS için)
with sqlite_session() as session:
    # Veritabanı işlemleri
    pass
```

### 2. Bağlantı Testi

```python
from sontechsp.uygulama.veritabani.baglanti import baglanti_test_et

# PostgreSQL bağlantı testi
if baglanti_test_et("postgresql"):
    print("PostgreSQL bağlantısı başarılı")

# SQLite bağlantı testi
if baglanti_test_et("sqlite"):
    print("SQLite bağlantısı başarılı")
```

## Migration Yönetimi

### 1. Migration Durumu Sorgulama

```python
from sontechsp.uygulama.veritabani.migration_yoneticisi import migration_durumu

durum = migration_durumu()
print(f"Mevcut versiyon: {durum['current_revision']}")
print(f"Hedef versiyon: {durum['head_revision']}")
print(f"Güncel mi: {durum['is_up_to_date']}")
print(f"Bekleyen migration sayısı: {durum['pending_count']}")
```

### 2. Migration Geçmişi

```python
from sontechsp.uygulama.veritabani.migration_yoneticisi import migration_gecmisi

gecmis = migration_gecmisi()
for migration in gecmis:
    print(f"Versiyon: {migration['revision']}")
    print(f"Açıklama: {migration['description']}")
    print(f"Uygulandı: {migration['is_applied']}")
```

### 3. Migration Çalıştırma

```python
from sontechsp.uygulama.veritabani.migration_yoneticisi import migration_calistir

# En son versiyona güncelle
sonuc = migration_calistir("head")
print(f"Başarılı: {sonuc['success']}")
print(f"Önceki versiyon: {sonuc['previous_revision']}")
print(f"Yeni versiyon: {sonuc['current_revision']}")

# Belirli bir versiyona güncelle
sonuc = migration_calistir("001")
```

### 4. Migration Geri Alma

```python
from sontechsp.uygulama.veritabani.migration_yoneticisi import migration_geri_al

# Belirli bir versiyona geri al
sonuc = migration_geri_al("base")  # Tüm migration'ları geri al
print(f"Başarılı: {sonuc['success']}")
```

### 5. Çakışma Kontrolü

```python
from sontechsp.uygulama.veritabani.migration_yoneticisi import migration_cakisma_kontrolu

kontrol = migration_cakisma_kontrolu()
if kontrol['has_conflict']:
    print(f"Çakışma var: {kontrol['conflict_message']}")
    print(f"Head sayısı: {kontrol['head_count']}")
else:
    print("Çakışma yok")
```

## Temel Veri Yükleme

### 1. Tüm Temel Verileri Yükleme

```python
from sontechsp.uygulama.veritabani.veri_yukleyici import temel_verileri_yukle

sonuc = temel_verileri_yukle()
print(f"Başarılı: {sonuc['success']}")
print(f"Yüklenen veriler: {sonuc['loaded_data']}")
```

### 2. Özel Veri Yükleme

```python
from sontechsp.uygulama.veritabani.veri_yukleyici import VeriYukleyici

yukleyici = VeriYukleyici()

with postgresql_session() as session:
    # Sistem yetkilerini yükle
    yetkiler = yukleyici.sistem_yetkilerini_olustur(session)
    
    # Sistem rollerini yükle
    roller = yukleyici.sistem_rollerini_olustur(session)
    
    # Admin kullanıcı oluştur
    admin = yukleyici.admin_kullanici_olustur(session)
    
    # Varsayılan firma/mağaza oluştur
    firma, magaza = yukleyici.varsayilan_firma_magaza_olustur(session)
```

## Hata Yönetimi

### 1. Hata Türleri

```python
from sontechsp.uygulama.cekirdek.hatalar import (
    VeritabaniHatasi, MigrationHatasi, VeriYuklemeHatasi
)

try:
    # Veritabanı işlemi
    pass
except VeritabaniHatasi as e:
    print(f"Veritabanı hatası: {e}")
except MigrationHatasi as e:
    print(f"Migration hatası: {e}")
except VeriYuklemeHatasi as e:
    print(f"Veri yükleme hatası: {e}")
```

### 2. Hata Loglama

```python
import logging

# Logger yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hatalar otomatik olarak loglanır
try:
    # Veritabanı işlemi
    pass
except Exception as e:
    logger.error(f"İşlem hatası: {e}")
```

## Komut Satırı Kullanımı

### 1. Alembic Komutları

```bash
# Migration durumu
alembic current

# Migration geçmişi
alembic history

# Migration çalıştırma
alembic upgrade head

# Migration geri alma
alembic downgrade -1

# Yeni migration oluşturma
alembic revision --autogenerate -m "Açıklama"
```

### 2. Python Scriptleri

```python
# migration_kontrol.py
from sontechsp.uygulama.veritabani.migration_yoneticisi import (
    migration_durumu, migration_calistir
)

def main():
    durum = migration_durumu()
    if not durum['is_up_to_date']:
        print(f"{durum['pending_count']} migration bekliyor")
        migration_calistir("head")
        print("Migration'lar tamamlandı")
    else:
        print("Veritabanı güncel")

if __name__ == "__main__":
    main()
```

## En İyi Uygulamalar

### 1. Migration Güvenliği

- Migration'ları test ortamında önce test edin
- Üretim öncesi veritabanı yedeği alın
- Migration'ları küçük parçalar halinde yapın
- Geri alma planınızı hazırlayın

### 2. Veri Tutarlılığı

- Foreign key constraint'leri kullanın
- Unique constraint'leri tanımlayın
- Index'leri performans için ekleyin
- Veri doğrulama kuralları yazın

### 3. Performans

- Büyük tablolarda migration'ları parçalayın
- Index ekleme/kaldırma işlemlerini dikkatli yapın
- Transaction boyutlarını kontrol edin
- Yoğun saatlerde migration yapmayın

### 4. Monitoring

- Migration sürelerini takip edin
- Hata loglarını izleyin
- Veritabanı boyutunu kontrol edin
- Performans metriklerini ölçün

## Sorun Giderme

### 1. Bağlantı Sorunları

```python
# Bağlantı testi
from sontechsp.uygulama.veritabani.baglanti import baglanti_test_et

if not baglanti_test_et("postgresql"):
    print("PostgreSQL bağlantı sorunu:")
    print("1. Veritabanı servisi çalışıyor mu?")
    print("2. Bağlantı bilgileri doğru mu?")
    print("3. Firewall ayarları uygun mu?")
```

### 2. Migration Sorunları

```python
# Migration çakışması
from sontechsp.uygulama.veritabani.migration_yoneticisi import migration_cakisma_kontrolu

kontrol = migration_cakisma_kontrolu()
if kontrol['has_conflict']:
    print("Migration çakışması çözümü:")
    print("1. alembic merge komutu kullanın")
    print("2. Çakışan migration'ları manuel birleştirin")
    print("3. Yeni merge migration oluşturun")
```

### 3. Veri Yükleme Sorunları

```python
# Veri tutarlılık kontrolü
from sontechsp.uygulama.veritabani.modeller import Kullanici, Rol

with postgresql_session() as session:
    # Admin kullanıcı kontrolü
    admin = session.query(Kullanici).filter_by(kullanici_adi='admin').first()
    if not admin:
        print("Admin kullanıcı eksik - temel verileri yeniden yükleyin")
    
    # Sistem rolleri kontrolü
    roller = session.query(Rol).filter_by(sistem_rolu=True).count()
    if roller == 0:
        print("Sistem rolleri eksik - temel verileri yeniden yükleyin")
```

## Örnek Senaryolar

### 1. Yeni Kurulum

```python
from sontechsp.uygulama.veritabani.baglanti import tablolari_olustur
from sontechsp.uygulama.veritabani.migration_yoneticisi import migration_calistir
from sontechsp.uygulama.veritabani.veri_yukleyici import temel_verileri_yukle

# 1. Tabloları oluştur
tablolari_olustur("postgresql")

# 2. Migration'ları çalıştır
migration_calistir("head")

# 3. Temel verileri yükle
temel_verileri_yukle()

print("Sistem kurulumu tamamlandı")
```

### 2. Güncelleme

```python
from sontechsp.uygulama.veritabani.migration_yoneticisi import (
    migration_durumu, migration_calistir
)

# 1. Mevcut durumu kontrol et
durum = migration_durumu()
print(f"Mevcut versiyon: {durum['current_revision']}")

# 2. Güncelleme gerekli mi?
if not durum['is_up_to_date']:
    print(f"{durum['pending_count']} migration uygulanacak")
    
    # 3. Migration'ları çalıştır
    sonuc = migration_calistir("head")
    
    if sonuc['success']:
        print("Güncelleme tamamlandı")
    else:
        print("Güncelleme başarısız")
else:
    print("Sistem güncel")
```

### 3. Yedekleme ve Geri Yükleme

```bash
# PostgreSQL yedekleme
pg_dump -h localhost -U postgres -d sontechsp > backup.sql

# Geri yükleme
psql -h localhost -U postgres -d sontechsp < backup.sql

# Migration durumunu sıfırla
alembic stamp head
```