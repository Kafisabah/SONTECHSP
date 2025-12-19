@echo off
REM Version: 1.0.0
REM Last Update: 2024-12-18
REM Module: scripts.ui-smoke-test-kurulum
REM Description: UI Smoke Test sanal ortam kurulum script'i
REM Changelog:
REM - İlk versiyon: sanal ortam kurulumu ve bağımlılık yükleme

echo ========================================
echo SONTECHSP UI Smoke Test Kurulum
echo ========================================

REM Mevcut dizini kaydet
set ORIGINAL_DIR=%CD%

REM Python varlığını kontrol et
python --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Python bulunamadi! Python 3.8+ yukleyin.
    pause
    exit /b 1
)

echo ✓ Python bulundu
python --version

REM Sanal ortam oluştur
echo.
echo Sanal ortam olusturuluyor...
if exist "venv" (
    echo ⚠ Mevcut sanal ortam bulundu, siliniyor...
    rmdir /s /q venv
)

python -m venv venv
if errorlevel 1 (
    echo HATA: Sanal ortam olusturulamadi!
    pause
    exit /b 1
)

echo ✓ Sanal ortam olusturuldu

REM Sanal ortamı aktifleştir
echo.
echo Sanal ortam aktifleştiriliyor...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo HATA: Sanal ortam aktifleştirilemedi!
    pause
    exit /b 1
)

echo ✓ Sanal ortam aktifleştirildi

REM Pip'i güncelle
echo.
echo pip guncelleniyor...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo UYARI: pip guncellenemedi, devam ediliyor...
)

REM Temel bağımlılıkları yükle
echo.
echo Temel bagimliliklar yukleniyor...
pip install PyQt6 SQLAlchemy psycopg2-binary
if errorlevel 1 (
    echo HATA: Temel bagimliliklar yuklenemedi!
    pause
    exit /b 1
)

echo ✓ Temel bagimliliklar yuklendi

REM Test bağımlılıklarını yükle
echo.
echo Test bagimliliklar yukleniyor...
pip install pytest hypothesis
if errorlevel 1 (
    echo UYARI: Test bagimliliklar yuklenemedi, devam ediliyor...
)

REM Proje bağımlılıklarını yükle (eğer requirements.txt varsa)
if exist "requirements.txt" (
    echo.
    echo Proje bagimliliklar yukleniyor...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo UYARI: Bazi proje bagimliliklar yuklenemedi, devam ediliyor...
    )
    echo ✓ Proje bagimliliklar yuklendi
)

REM Kurulum doğrulaması
echo.
echo Kurulum dogrulamasi yapiliyor...
python -c "import PyQt6; print('✓ PyQt6 OK')"
if errorlevel 1 (
    echo HATA: PyQt6 import edilemedi!
    pause
    exit /b 1
)

python -c "import sqlalchemy; print('✓ SQLAlchemy OK')"
if errorlevel 1 (
    echo HATA: SQLAlchemy import edilemedi!
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ KURULUM TAMAMLANDI!
echo ========================================
echo.
echo Kullanim:
echo   1. Sanal ortami aktifleştirin: venv\Scripts\activate.bat
echo   2. Smoke test calistirin: python -m uygulama.arayuz.smoke_test_calistir
echo.
echo Ornekler:
echo   python -m uygulama.arayuz.smoke_test_calistir --help
echo   python -m uygulama.arayuz.smoke_test_calistir --csv
echo   python -m uygulama.arayuz.smoke_test_calistir --csv-file rapor.csv
echo.

pause