# UI Smoke Test Script'leri

Bu klasör, SONTECHSP UI Smoke Test altyapısı için yardımcı script'leri içerir.

## Script'ler

### Windows Batch Script'leri

#### `ui-smoke-test-kurulum.bat`
- **Amaç**: Sanal ortam kurulumu ve bağımlılık yükleme
- **Kullanım**: `scripts\ui-smoke-test-kurulum.bat`
- **Özellikler**:
  - Python varlığı kontrolü
  - Sanal ortam oluşturma
  - PyQt6, SQLAlchemy, psycopg2-binary yükleme
  - Test bağımlılıkları (pytest, hypothesis)
  - Kurulum doğrulaması

#### `ui-smoke-test-calistir.bat`
- **Amaç**: Smoke test çalıştırma (tam özellikli)
- **Kullanım**: `scripts\ui-smoke-test-calistir.bat [parametreler]`
- **Parametreler**:
  - `--quiet`: Sessiz mod
  - `--csv`: CSV raporu üret
  - `--csv-file dosya.csv`: CSV'yi dosyaya kaydet
  - `--screens ekran1 ekran2`: Belirli ekranları test et
  - `--help`: Yardım göster

#### `ui-smoke-test-hizli.bat`
- **Amaç**: Hızlı test (minimal çıktı)
- **Kullanım**: `scripts\ui-smoke-test-hizli.bat`
- **Özellikler**:
  - Sessiz mod ile çalışır
  - Sadece sonuç gösterir
  - Hızlı kontrol için ideal

#### `ui-smoke-test-rapor.bat`
- **Amaç**: Detaylı rapor üretme
- **Kullanım**: `scripts\ui-smoke-test-rapor.bat`
- **Özellikler**:
  - Otomatik tarih/saat damgalı dosya adı
  - `raporlar/ui_smoke_test/` klasörüne kayıt
  - Rapor önizlemesi
  - Excel ile açma seçeneği

### Python Script'leri (Cross-Platform)

#### `ui_smoke_test_kurulum.py`
- **Amaç**: Platform bağımsız kurulum
- **Kullanım**: `python scripts/ui_smoke_test_kurulum.py`
- **Desteklenen Platformlar**: Windows, Linux, macOS
- **Özellikler**:
  - Otomatik platform algılama
  - Python 3.8+ kontrolü
  - Cross-platform sanal ortam yönetimi

#### `ui_smoke_test_calistir.py`
- **Amaç**: Platform bağımsız test çalıştırma
- **Kullanım**: `python scripts/ui_smoke_test_calistir.py [parametreler]`
- **Parametreler**: Batch script ile aynı
- **Özellikler**:
  - Argparse ile gelişmiş parametre işleme
  - Platform bağımsız yol yönetimi

## Kullanım Senaryoları

### İlk Kurulum
```bash
# Windows
scripts\ui-smoke-test-kurulum.bat

# Linux/Mac
python scripts/ui_smoke_test_kurulum.py
```

### Hızlı Test
```bash
# Windows
scripts\ui-smoke-test-hizli.bat

# Linux/Mac  
python scripts/ui_smoke_test_calistir.py --quiet
```

### Detaylı Rapor
```bash
# Windows
scripts\ui-smoke-test-rapor.bat

# Linux/Mac
python scripts/ui_smoke_test_calistir.py --csv-file "rapor_$(date +%Y%m%d_%H%M%S).csv"
```

### Belirli Ekranları Test
```bash
# Windows
scripts\ui-smoke-test-calistir.bat --screens pos_satis urunler_stok

# Linux/Mac
python scripts/ui_smoke_test_calistir.py --screens pos_satis urunler_stok
```

## Çıktı Dosyaları

### Log Dosyaları
- `logs/ui_smoke_test.log`: Ana log dosyası
- `logs/sontechsp.log`: Uygulama genel log'u

### Rapor Dosyaları
- `raporlar/ui_smoke_test/smoke_test_raporu_YYYYMMDD_HHMMSS.csv`: Tarihli raporlar
- Kullanıcı tanımlı CSV dosyaları

## Hata Çözümleri

### "Python bulunamadı"
- Python 3.8+ yükleyin
- PATH'e Python ekleyin

### "Sanal ortam aktifleştirilemedi"
- Kurulum script'ini yeniden çalıştırın
- Yönetici hakları gerekebilir

### "PyQt6 import edilemedi"
- Sanal ortamda: `pip install PyQt6`
- Sistem bağımlılıklarını kontrol edin

### "Veritabanı bağlantı hatası"
- PostgreSQL servisinin çalıştığından emin olun
- Bağlantı ayarlarını kontrol edin

## Geliştirici Notları

### Yeni Script Ekleme
1. Script'i `scripts/` klasörüne ekleyin
2. Uygun başlık yorumlarını ekleyin
3. Bu README'yi güncelleyin
4. Test edin

### Platform Desteği
- Windows: `.bat` dosyaları
- Linux/Mac: `.py` dosyaları
- Cross-platform: Python script'leri tercih edilir

### Versiyon Yönetimi
Her script dosyasında:
```
# Version: X.Y.Z
# Last Update: YYYY-MM-DD
# Module: scripts.script_name
# Description: Kısa açıklama
# Changelog:
# - Değişiklik listesi
```

## İletişim

Teknik destek için geliştirici ekibi ile iletişime geçin.