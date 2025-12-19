# SONTECHSP UI Smoke Test Altyapısı

## Genel Bakış

SONTECHSP UI Smoke Test Altyapısı, PyQt6 tabanlı arayüzün sanal ortamda test edilmesini ve buton-fonksiyon-servis eşleştirmelerinin takip edilmesini sağlayan bir sistemdir. Bu altyapı, UI bileşenlerinin doğru çalışıp çalışmadığını hızlıca test etmeyi ve hangi butonun hangi servisi çağırdığını görünür hale getirmeyi amaçlar.

## Özellikler

- ✅ **Smoke Test Çalıştırıcısı**: UI'nin temel işlevselliğini hızlıca test eder
- ✅ **Buton Eşleştirme Kaydı**: Buton-handler-servis eşleştirmelerini otomatik kaydeder
- ✅ **Log Sistemi**: UI etkileşimlerini ve servis çağrılarını loglar
- ✅ **Rapor Üretimi**: Tablo ve CSV formatında raporlar üretir
- ✅ **Thread-Safe**: Çoklu thread ortamında güvenli çalışır
- ✅ **Komut Satırı Desteği**: Esnek kullanım için CLI arayüzü

## Kurulum

### Gereksinimler

- Python 3.8+
- PyQt6
- SQLAlchemy
- PostgreSQL (ana veritabanı)
- SQLite (offline cache)

### Bağımlılıklar

```bash
pip install PyQt6 SQLAlchemy psycopg2-binary
```

### Proje Yapısı

```
uygulama/arayuz/
├── smoke_test_calistir.py      # Ana smoke test çalıştırıcısı
├── buton_eslestirme_kaydi.py   # Buton eşleştirme kayıt sistemi
├── log_sistemi.py              # Log yönetimi
├── ana_pencere.py              # Ana pencere sınıfı
├── uygulama.py                 # Uygulama başlatıcısı
├── servis_fabrikasi.py         # Servis fabrikası
└── ekranlar/                   # UI ekranları
    ├── temel_ekran.py          # Temel ekran sınıfı
    ├── pos_satis.py            # POS satış ekranı
    ├── urunler_stok.py         # Ürünler/stok ekranı
    └── gosterge_paneli.py      # Gösterge paneli
```

## Kullanım

### Temel Smoke Test

En basit kullanım:

```bash
python -m uygulama.arayuz.smoke_test_calistir
```

### Komut Satırı Seçenekleri

```bash
# Sessiz mod (minimal çıktı)
python -m uygulama.arayuz.smoke_test_calistir --quiet

# Belirli ekranları test et
python -m uygulama.arayuz.smoke_test_calistir --screens pos_satis urunler_stok

# CSV formatında rapor üret
python -m uygulama.arayuz.smoke_test_calistir --csv

# CSV raporunu dosyaya kaydet
python -m uygulama.arayuz.smoke_test_calistir --csv-file rapor.csv

# Yardım
python -m uygulama.arayuz.smoke_test_calistir --help
```

### Programatik Kullanım

```python
from uygulama.arayuz.smoke_test_calistir import smoke_test_calistir

# Smoke test çalıştır
sonuc = smoke_test_calistir(
    verbose=True,
    ekranlar=['pos_satis', 'urunler_stok'],
    csv_export=True,
    csv_dosya='test_raporu.csv'
)

if sonuc == 0:
    print("Test başarılı!")
else:
    print("Test başarısız!")
```

### Buton Eşleştirme Sistemi

```python
from uygulama.arayuz.buton_eslestirme_kaydi import (
    kayit_ekle,
    kayitlari_listele,
    tablo_formatinda_cikti,
    csv_formatinda_cikti,
    csv_dosyasina_kaydet
)

# Yeni kayıt ekle
kayit_ekle('PosEkran', 'SatisButon', 'satis_handler', 'satis_servisi')

# Kayıtları listele
kayitlar = kayitlari_listele()

# Tablo formatında çıktı
print(tablo_formatinda_cikti())

# CSV formatında çıktı
csv_icerik = csv_formatinda_cikti()

# CSV dosyasına kaydet
csv_dosyasina_kaydet('buton_eslestirmeleri.csv')
```

## Test Akışı

1. **Başlatma**: Standart giriş noktası doğrulanır ve uygulama başlatılır
2. **Ekran Geçişi**: Tüm ekranlar sırayla ziyaret edilir
3. **Buton Kaydı**: Her ekrandaki butonlar otomatik olarak kaydedilir
4. **Log Kaydı**: UI etkileşimleri ve servis çağrıları loglanır
5. **Rapor Üretimi**: Test sonuçları tablo ve/veya CSV formatında raporlanır
6. **Temiz Kapanış**: Kaynaklar temizlenir ve uygulama kapatılır

## Çıktı Formatları

### Tablo Formatı

```
Ekran                Buton                Handler                   Servis                    Zaman               
--------------------------------------------------------------------------------------------------------------
PosEkran             SatisButon           satis_handler             satis_servisi             12:30:45            
UrunlerEkran         UrunEkleButon        urun_ekle_handler         urun_servisi              12:30:46            
```

### CSV Formatı

```csv
Ekran,Buton,Handler,Servis,Zaman,Cagrilma_Sayisi
PosEkran,SatisButon,satis_handler,satis_servisi,2024-12-18T12:30:45.123456,0
UrunlerEkran,UrunEkleButon,urun_ekle_handler,urun_servisi,2024-12-18T12:30:46.789012,0
```

## Log Sistemi

Log dosyası: `logs/ui_smoke_test.log`

### Log Seviyeleri

- **INFO**: Genel bilgi mesajları
- **DEBUG**: Detaylı debug bilgileri
- **WARNING**: Uyarı mesajları
- **ERROR**: Hata mesajları

### Log Formatı

```
2024-12-18 12:30:45,123 - INFO - [PosEkran] Buton tıklandı: SatisButon -> satis_handler
2024-12-18 12:30:45,124 - DEBUG - [PosEkran] Stub servis çağrıldı: satis_servisi
```

## Hata Yönetimi

### Yaygın Hatalar ve Çözümleri

1. **PyQt6 Import Hatası**
   ```bash
   pip install PyQt6
   ```

2. **Veritabanı Bağlantı Hatası**
   - PostgreSQL servisinin çalıştığından emin olun
   - Bağlantı ayarlarını kontrol edin

3. **Ekran Yükleme Hatası**
   - Servis fabrikasının doğru yapılandırıldığından emin olun
   - Gerekli modüllerin import edildiğini kontrol edin

4. **Log Dosyası Yazma Hatası**
   - `logs/` klasörünün var olduğundan emin olun
   - Yazma izinlerini kontrol edin

## Geliştirici Notları

### Yeni Ekran Ekleme

1. `ekranlar/` klasörüne yeni ekran dosyası ekleyin
2. `TemelEkran` sınıfından türetin
3. Butonları `kayit_ekle()` ile kaydedin
4. Handler'larda `handler_loglama()` kullanın
5. Stub servisler için `stub_servis_loglama()` kullanın

### Örnek Ekran Implementasyonu

```python
from ..temel_ekran import TemelEkran
from ..buton_eslestirme_kaydi import kayit_ekle
from ..log_sistemi import handler_loglama, stub_servis_loglama

class YeniEkran(TemelEkran):
    def __init__(self, servis_fabrikasi):
        super().__init__(servis_fabrikasi)
        self.setupUI()
        self.butonlari_kaydet()
    
    def setupUI(self):
        # UI bileşenlerini oluştur
        pass
    
    def butonlari_kaydet(self):
        kayit_ekle('YeniEkran', 'TestButon', 'test_handler', 'test_servisi')
    
    def test_handler(self):
        handler_loglama('YeniEkran', 'TestButon', 'test_handler')
        stub_servis_loglama('test_servisi')
```

### Thread Safety

Buton eşleştirme sistemi thread-safe'dir. Çoklu thread ortamında güvenle kullanılabilir:

```python
import threading
from uygulama.arayuz.buton_eslestirme_kaydi import kayit_ekle

def worker_thread(thread_id):
    for i in range(100):
        kayit_ekle(f'Thread{thread_id}', f'Buton{i}', f'handler{i}')

# Çoklu thread test
threads = []
for i in range(5):
    t = threading.Thread(target=worker_thread, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

## Sık Sorulan Sorular

**S: Smoke test ne kadar sürer?**
C: Genellikle 10-30 saniye arası, ekran sayısına bağlı olarak değişir.

**S: Test sırasında gerçek veriler etkilenir mi?**
C: Hayır, test modunda stub servisler kullanılır, gerçek veriler etkilenmez.

**S: Hangi ekranlar test edilir?**
C: Varsayılan olarak tüm ekranlar, `--screens` parametresi ile belirli ekranlar seçilebilir.

**S: CSV raporu nasıl analiz edilir?**
C: Excel, LibreOffice Calc veya herhangi bir CSV okuyucusu ile açılabilir.

## Lisans

Bu proje SONTECHSP'nin mülkiyetindedir. Tüm hakları saklıdır.

## İletişim

Teknik destek için: geliştirici ekibi ile iletişime geçin.