# Tasarım Belgesi

## Genel Bakış

SONTECHSP proje iskeleti, Windows üzerinde kurulabilen, çoklu mağaza/şube ve çoklu PC ile eş zamanlı çalışan Hızlı Satış (POS) + ERP + CRM sisteminin temelini oluşturan klasör yapısı ve başlangıç dosyalarını içerir. Bu tasarım, katmanlı mimariyi (UI->Servis->Repository->DB) destekleyen, ölçeklenebilir ve bakım yapılabilir bir yapı sağlar.

## Mimari

### Katmanlı Mimari (SONTECHSP Standardı)
```
Arayüz (PyQt6) -> Servisler -> Depolar (Repository) -> Veritabanı (PostgreSQL/SQLite)
```

**Katman Bağımlılık Kuralları:**
- UI katmanı sadece Servis katmanını çağırabilir
- Servis katmanı sadece Repository katmanını çağırabilir  
- Repository katmanı sadece Veritabanı katmanını erişebilir
- Çekirdek modülü tüm katmanlardan bağımsızdır

### Klasör Yapısı (Türkçe ASCII İsimlendirme)
```
sontechsp/
├── uygulama/
│   ├── __init__.py
│   ├── ana.py              # Bootstrap giriş noktası
│   ├── cekirdek/           # Temel sistem bileşenleri
│   │   ├── ayarlar.py      # Yapılandırma yönetimi
│   │   ├── kayit.py        # Log sistemi (dosya+console)
│   │   ├── hatalar.py      # Hata sınıfları
│   │   ├── yetki.py        # Rol/yetki sistemi
│   │   └── oturum.py       # Oturum bağlamı
│   ├── veritabani/         # DB modelleri ve bağlantılar
│   │   ├── modeller/       # SQLAlchemy modelleri
│   │   ├── depolar/        # Repository katmanı
│   │   ├── baglanti.py     # DB bağlantı yönetimi
│   │   ├── taban.py        # DeclarativeBase
│   │   └── gocler/         # Alembic migration'ları
│   ├── moduller/           # İş modülleri (Ajan bazlı)
│   │   ├── stok/           # stok_ajani sorumluluğu
│   │   ├── pos/            # pos_ajani sorumluluğu
│   │   ├── crm/            # crm_ajani sorumluluğu
│   │   ├── satis_belgeleri/ # satis_belge_ajani sorumluluğu
│   │   ├── eticaret/       # eticaret_ajani sorumluluğu
│   │   ├── ebelge/         # ebelge_ajani sorumluluğu
│   │   ├── kargo/          # kargo_ajani sorumluluğu
│   │   └── raporlar/       # rapor_ajani sorumluluğu
│   ├── servisler/          # İş mantığı katmanı
│   ├── arayuz/             # PyQt6 UI bileşenleri
│   │   ├── ana_pencere.py  # Sol menü + içerik alanı
│   │   └── ekranlar/       # UI ekranları
│   └── kurulum/            # Kurulum ve yapılandırma
│       └── baslat.py       # İlk kurulum bootstrap
├── testler/                # Test dosyaları
├── pyproject.toml          # Python bağımlılıkları
└── README.md               # Kurulum + PyInstaller notları
```

## Bileşenler ve Arayüzler

### Ana Uygulama (ana.py)
- **Sorumluluk**: Sadece bootstrap işlevi (iş kuralı YOK)
- PyQt6 AnaPencere başlatma
- Log sistemi kurulumu (dosya+console)
- Merkezi hata yönetimi sistemi
- Sol menü ve içerik alanı UI başlatma

### Çekirdek Modülü (cekirdek/)
- **ayarlar.py**: Yapılandırma okuma (.env/config.json)
- **kayit.py**: Log sistemi (dosya+console çıktı)
- **hatalar.py**: AlanHatasi/DogrulamaHatasi/EntegrasyonHatasi sınıfları
- **yetki.py**: Rol/yetki sistemi iskeleti
- **oturum.py**: Magaza/terminal/kullanici bağlam yönetimi

### Veritabanı Katmanı (veritabani/)
- **baglanti.py**: SQLAlchemy engine/sessionmaker
- **taban.py**: DeclarativeBase tanımı
- **modeller/**: Türkçe tablo isimleri (kullanicilar, urunler, pos_satislar vb.)
- **depolar/**: Repository pattern uygulaması
- **gocler/**: Alembic migration yönetimi

### Proje Yapılandırması (pyproject.toml)
- Python sürüm gereksinimleri (3.9+)
- **Temel bağımlılıklar**: PyQt6, SQLAlchemy, Alembic, FastAPI
- **Test bağımlılıkları**: pytest, hypothesis
- **Build araçları**: PyInstaller yapılandırması

### Dokümantasyon (README.md)
- Windows kurulum talimatları
- Çalıştırma rehberi
- PyInstaller build notları
- PostgreSQL/SQLite kurulum gereksinimleri
- Geliştirme ortamı kurulumu

## Veri Modelleri

### Klasör Yapısı Modeli (SONTECHSP Standardı)
```python
# SONTECHSP klasör yapısı (Türkçe ASCII)
KLASOR_YAPISI = {
    'uygulama': {
        'cekirdek': ['ayarlar', 'kayit', 'hatalar', 'yetki', 'oturum'],
        'veritabani': ['modeller', 'depolar', 'gocler', 'baglanti', 'taban'],
        'moduller': [
            'stok',           # stok_ajani
            'pos',            # pos_ajani  
            'crm',            # crm_ajani
            'satis_belgeleri', # satis_belge_ajani
            'eticaret',       # eticaret_ajani
            'ebelge',         # ebelge_ajani
            'kargo',          # kargo_ajani
            'raporlar'        # rapor_ajani
        ],
        'servisler': [],      # İş mantığı katmanı
        'arayuz': ['ana_pencere', 'ekranlar'],
        'kurulum': ['baslat']
    },
    'testler': []
}
```

### Veritabanı Tablo İsimleri (Türkçe ASCII)
```python
# SONTECHSP tablo isimlendirme standardı
TABLO_ISIMLERI = {
    'yetki_kullanici': ['kullanicilar', 'roller', 'yetkiler', 'kullanici_rolleri', 'rol_yetkileri'],
    'firma_magaza': ['firmalar', 'magazalar', 'terminaller', 'depolar'],
    'stok': ['urunler', 'urun_barkodlari', 'stok_bakiyeleri', 'stok_hareketleri'],
    'crm': ['musteriler', 'sadakat_puanlari'],
    'pos': ['pos_satislar', 'pos_satis_satirlari', 'odeme_kayitlari'],
    'belgeler': ['satis_belgeleri', 'satis_belge_satirlari'],
    'eticaret': ['eticaret_hesaplari', 'eticaret_siparisleri'],
    'ebelge': ['ebelge_cikis_kuyrugu', 'ebelge_durumlari'],
    'kargo': ['kargo_etiketleri', 'kargo_takipleri']
}
```

### Dosya Şablonu Yapısı (SONTECHSP Standardı)
```python
# Standart dosya başlığı şablonu
DOSYA_BASLIGI = """
# Version: 0.1.0
# Last Update: {tarih}
# Module: {modul_adi}
# Description: {aciklama}
# Changelog:
# - İlk oluşturma
"""

# Kod kalitesi kuralları
KOD_KURALLARI = {
    'max_dosya_satir': 120,    # Yorumlar hariç
    'max_fonksiyon_satir': 25, # Gerekirse böl
    'format': 'PEP8',          # Zorunlu
    'yorum_dili': 'Türkçe',    # Inline açıklamalar
    'karakter_seti': 'ASCII'   # Türkçe karakter yok
}
```

## Doğruluk Özellikleri

*Bir özellik, sistemin tüm geçerli yürütmelerinde doğru olması gereken bir karakteristik veya davranıştır - esasen, sistemin ne yapması gerektiği hakkında resmi bir ifadedir. Özellikler, insan tarafından okunabilir spesifikasyonlar ile makine tarafından doğrulanabilir doğruluk garantileri arasında köprü görevi görür.*

**Özellik 1: SONTECHSP klasör hiyerarşisi tutarlılığı**
*Herhangi bir* proje iskeleti oluşturulduğunda, sontechsp/uygulama/cekirdek/veritabani/moduller klasör hiyerarşisi mevcut olmalıdır
**Doğrular: Gereksinim 1.1**

**Özellik 2: PyQt6 uygulama başlatma bütünlüğü**
*Herhangi bir* ana uygulama başlatıldığında, PyQt6 penceresi açılmalı ve log sistemi (dosya+console) aktif hale gelmelidir
**Doğrular: Gereksinim 1.2, 3.1, 3.2, 3.3**

**Özellik 3: Katmanlı mimari uyumluluğu**
*Herhangi bir* proje yapısında, UI->Servis->Repository->DB katman kuralları korunmalı ve modüller kendi dizinlerinde olmalıdır
**Doğrular: Gereksinim 1.3, 4.1, 4.2, 4.4**

**Özellik 4: SONTECHSP bağımlılık standardı**
*Herhangi bir* pyproject.toml dosyası, PyQt6, SQLAlchemy, Alembic, FastAPI, pytest, hypothesis bağımlılıklarını tanımlamalıdır
**Doğrular: Gereksinim 2.1**

**Özellik 5: Windows kurulum dokümantasyonu**
*Herhangi bir* README.md dosyası, Windows kurulum talimatları ve PyInstaller build notlarını içermelidir
**Doğrular: Gereksinim 2.2**

**Özellik 6: Veritabanı gereksinim belirtimi**
*Herhangi bir* proje yapılandırmasında, PostgreSQL ve SQLite veritabanı gereksinimleri belirtilmeli ve Windows üzerinde yüklenebilir olmalıdır
**Doğrular: Gereksinim 2.3, 2.4**

**Özellik 7: Bootstrap işlevi sadeliği**
*Herhangi bir* ana.py dosyası, sadece PyQt6 AnaPencere başlatma işlevini görmeli ve iş kuralları içermemelidir
**Doğrular: Gereksinim 3.4**

**Özellik 8: Merkezi hata yönetimi**
*Herhangi bir* hata durumunda, merkezi hata yönetimi sistemi devreye girmeli ve AlanHatasi/DogrulamaHatasi/EntegrasyonHatasi sınıfları kullanılmalıdır
**Doğrular: Gereksinim 3.5, 7.4**

**Özellik 9: Ajan tabanlı modül organizasyonu**
*Herhangi bir* yeni modül eklendiğinde, stok/pos/crm/satis_belgeleri/eticaret/ebelge/kargo/raporlar yapısına uyumlu olmalı ve katmanlı mimariyi bozmamalıdır
**Doğrular: Gereksinim 4.3**

**Özellik 10: SONTECHSP kod kalitesi standardı**
*Herhangi bir* Python dosyası, PEP8 standartlarına uymalı, 120 satırı (yorumlar hariç) aşmamalı ve her fonksiyon 25 satırı aşmamalıdır
**Doğrular: Gereksinim 1.5, 5.1, 5.2, 5.3**

**Özellik 11: Türkçe dokümantasyon standardı**
*Herhangi bir* kod dosyası, Version/Last Update/Module/Description/Changelog şablonu ve Türkçe inline açıklamalar içermelidir
**Doğrular: Gereksinim 5.4, 5.5**

**Özellik 12: Türkçe ASCII tablo isimlendirmesi**
*Herhangi bir* veritabanı tablosu, kullanicilar/urunler/pos_satislar gibi Türkçe ASCII isimlendirme standardını kullanmalıdır
**Doğrular: Gereksinim 6.1, 6.2, 6.3, 6.4, 6.5**

**Özellik 13: Çekirdek modül bağımsızlığı**
*Herhangi bir* çekirdek modülü, ayarlar/kayit/hatalar/yetki/oturum bileşenlerini ayrı dosyalarda içermeli ve UI/veritabanı katmanlarından bağımsız olmalıdır
**Doğrular: Gereksinim 7.1, 7.2, 7.3, 7.5**

**Özellik 14: Otomatik kurulum süreci**
*Herhangi bir* ilk kurulum işlemi, klasör oluşturma, PostgreSQL bağlantı testi, migration çalıştırma ve admin kullanıcı oluşturmayı otomatik yapmalıdır
**Doğrular: Gereksinim 8.1, 8.2, 8.3, 8.4, 8.5**

**Özellik 15: Başlangıç dosyaları çalışabilirliği**
*Herhangi bir* başlangıç dosyası seti, hatasız çalıştırılabilir olmalı ve sistem gereksinimlerini karşılamalıdır
**Doğrular: Gereksinim 1.4**

## Hata Yönetimi

### Hata Türleri
- **Yapılandırma Hataları**: Eksik veya hatalı yapılandırma dosyaları
- **Bağımlılık Hataları**: Eksik Python paketleri veya sürüm uyumsuzlukları
- **Dosya Sistemi Hataları**: Klasör oluşturma veya dosya erişim sorunları
- **UI Hataları**: PyQt6 başlatma sorunları

### Hata Yönetimi Stratejisi
- Tüm hatalar merkezi log sistemine kaydedilir
- Kritik hatalar kullanıcıya anlaşılır mesajlarla bildirilir
- Kurtarılabilir hatalar için otomatik düzeltme mekanizmaları
- Hata durumlarında graceful shutdown

## Test Stratejisi

### İkili Test Yaklaşımı

**Unit Testler:**
- Belirli örnekleri ve edge case'leri doğrular
- Bileşenler arası entegrasyon noktalarını test eder
- Hata koşullarını ve sınır değerlerini kontrol eder

**Property-Based Testler:**
- Tüm girdiler boyunca geçerli olması gereken evrensel özellikleri doğrular
- Minimum 100 iterasyon ile çalıştırılır
- Her property-based test, tasarım belgesindeki doğruluk özelliklerini referans alır
- Python için `hypothesis` kütüphanesi kullanılır

**SONTECHSP Test Gereksinimleri:**
- Her doğruluk özelliği TEK bir property-based test ile uygulanır
- Her property-based test şu formatla etiketlenir: '**Feature: sontechsp-proje-iskeleti, Property {numara}: {özellik_metni}**'
- Unit testler ve property testler birbirini tamamlar: unit testler spesifik hataları yakalar, property testler genel doğruluğu doğrular
- Property-based testler minimum 100 iterasyon ile çalıştırılır
- Test framework olarak `pytest` ve `hypothesis` kütüphaneleri kullanılır
- Test dosyaları `testler/` klasöründe organize edilir
- Her ajan modülü için ayrı test dosyaları oluşturulur
- Kritik senaryolar: stok kilitleme, negatif stok eşiği, POS ödeme bütünlüğü, e-belge outbox retry
