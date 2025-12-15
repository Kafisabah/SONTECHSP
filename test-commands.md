# SONTECHSP Test Komutları

Bu dosya, SONTECHSP projesi için optimize edilmiş test komutlarını içerir.

## Hızlı Testler (Geliştirme için)
```bash
# Yavaş testler hariç tüm testler (30 saniye hedef)
pytest -m "not slow" -v --tb=short --maxfail=10

# Paralel hızlı testler
pytest -m "not slow" -n auto -v --tb=short --maxfail=10
```

## Kritik Testler (CI/CD için)
```bash
# Sadece kritik testler (10 dakika hedef)
pytest -m critical -v --tb=short --maxfail=5

# Kritik + smoke testler
pytest -m "critical or smoke" -v --tb=short --maxfail=5
```

## Kategori Bazlı Testler
```bash
# Birim testler
pytest -m unit -v --tb=short

# Entegrasyon testleri
pytest -m integration -v --tb=short

# Property-based testler
pytest -m property -v --tb=short

# Yavaş testler
pytest -m slow -v --tb=short

# Smoke testler
pytest -m smoke -v --tb=short
```

## Paralel Test Çalıştırma
```bash
# Otomatik worker sayısı
pytest -n auto -v --tb=short

# Belirli worker sayısı
pytest -n 4 -v --tb=short

# Paralel + coverage
pytest -n auto --cov=sontechsp --cov-report=html --cov-report=term-missing
```

## Coverage Raporları
```bash
# HTML coverage raporu
pytest --cov=sontechsp --cov-report=html

# Terminal coverage raporu
pytest --cov=sontechsp --cov-report=term-missing

# XML coverage raporu (CI/CD için)
pytest --cov=sontechsp --cov-report=xml
```

## Performans Testleri
```bash
# Test sürelerini göster
pytest --durations=10

# En yavaş 20 testi göster
pytest --durations=20

# Sadece yavaş testleri çalıştır
pytest -m slow --durations=0
```

## Hata Ayıklama
```bash
# İlk hatada dur
pytest --maxfail=1

# Detaylı traceback
pytest --tb=long

# Sadece başarısız testleri tekrar çalıştır
pytest --lf

# Son çalıştırmadan bu yana değişen testleri çalıştır
pytest --ff
```

## Özel Kombinasyonlar
```bash
# Hızlı + paralel + coverage
pytest -m "not slow" -n auto --cov=sontechsp --cov-report=html

# Kritik testler + paralel
pytest -m critical -n 2 --maxfail=3

# Property testler + detaylı çıktı
pytest -m property -v -s --tb=short

# Entegrasyon testleri + yavaş timeout
pytest -m integration --timeout=300
```

## Windows Batch Dosyaları

Proje `scripts/` klasöründe hazır batch dosyaları içerir:

- `scripts/test-fast.bat` - Hızlı testler
- `scripts/test-slow.bat` - Yavaş testler  
- `scripts/test-critical.bat` - Kritik testler
- `scripts/test-parallel.bat` - Paralel testler
- `scripts/test-smoke.bat` - Smoke testler

## Performans Hedefleri

- **Hızlı testler**: < 30 saniye
- **Kritik testler**: < 10 dakika
- **Smoke testler**: < 15 saniye
- **Tüm testler (paralel)**: < 2 dakika
- **Yavaş testler**: < 5 dakika

## Önerilen Geliştirme Akışı

1. **Geliştirme sırasında**: `pytest -m "not slow" -n auto`
2. **Commit öncesi**: `pytest -m critical`
3. **Push öncesi**: `pytest -m "not slow" --cov=sontechsp`
4. **Haftalık**: `pytest -m slow`

## CI/CD Pipeline Komutları

```yaml
# Pull Request
pytest -m "critical or smoke" -n 2 --maxfail=5

# Main Branch
pytest -m "not slow" -n auto --cov=sontechsp --cov-report=xml

# Release
pytest -n auto --cov=sontechsp --cov-report=xml --cov-report=html

# Scheduled (haftalık)
pytest -m slow -n auto --cov=sontechsp
```