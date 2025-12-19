@echo off
REM Version: 1.0.0
REM Last Update: 2024-12-18
REM Module: scripts.ui-smoke-test-hizli
REM Description: Hızlı UI smoke test script'i - minimal çıktı ile
REM Changelog:
REM - İlk versiyon: hızlı test çalıştırma

echo SONTECHSP Hizli Smoke Test
echo ===========================

REM Sanal ortam kontrolü ve aktifleştirme
if not exist "venv\Scripts\activate.bat" (
    echo HATA: Sanal ortam yok! Kurulum: scripts\ui-smoke-test-kurulum.bat
    exit /b 1
)

call venv\Scripts\activate.bat >nul 2>&1
if errorlevel 1 (
    echo HATA: Sanal ortam aktifleştirilemedi!
    exit /b 1
)

REM Hızlı test (sessiz mod)
python -m uygulama.arayuz.smoke_test_calistir --quiet
set RESULT=%errorlevel%

if %RESULT%==0 (
    echo ✓ Test BASARILI
) else (
    echo ✗ Test BASARISIZ ^(kod: %RESULT%^)
    echo Log: logs\ui_smoke_test.log
)

exit /b %RESULT%