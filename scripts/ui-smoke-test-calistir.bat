@echo off
REM Version: 1.0.0
REM Last Update: 2024-12-18
REM Module: scripts.ui-smoke-test-calistir
REM Description: UI Smoke Test çalıştırma script'i
REM Changelog:
REM - İlk versiyon: smoke test çalıştırma ve rapor üretme

echo ========================================
echo SONTECHSP UI Smoke Test Calistiricisi
echo ========================================

REM Sanal ortam kontrolü
if not exist "venv\Scripts\activate.bat" (
    echo HATA: Sanal ortam bulunamadi!
    echo Once kurulum script'ini calistirin: scripts\ui-smoke-test-kurulum.bat
    pause
    exit /b 1
)

REM Sanal ortamı aktifleştir
echo Sanal ortam aktifleştiriliyor...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo HATA: Sanal ortam aktifleştirilemedi!
    pause
    exit /b 1
)

echo ✓ Sanal ortam aktifleştirildi

REM Parametreleri işle
set SMOKE_ARGS=
set CSV_FILE=
set QUIET_MODE=0

:parse_args
if "%1"=="" goto run_test
if "%1"=="--quiet" (
    set QUIET_MODE=1
    set SMOKE_ARGS=%SMOKE_ARGS% --quiet
    shift
    goto parse_args
)
if "%1"=="--csv" (
    set SMOKE_ARGS=%SMOKE_ARGS% --csv
    shift
    goto parse_args
)
if "%1"=="--csv-file" (
    set CSV_FILE=%2
    set SMOKE_ARGS=%SMOKE_ARGS% --csv-file %2
    shift
    shift
    goto parse_args
)
if "%1"=="--screens" (
    set SMOKE_ARGS=%SMOKE_ARGS% --screens
    shift
    :screens_loop
    if "%1"=="" goto run_test
    if "%1:~0,2%"=="--" goto parse_args
    set SMOKE_ARGS=%SMOKE_ARGS% %1
    shift
    goto screens_loop
)
if "%1"=="--help" (
    set SMOKE_ARGS=%SMOKE_ARGS% --help
    shift
    goto parse_args
)
REM Bilinmeyen parametre
set SMOKE_ARGS=%SMOKE_ARGS% %1
shift
goto parse_args

:run_test
REM Logs klasörünü oluştur
if not exist "logs" mkdir logs

REM Smoke test çalıştır
echo.
if %QUIET_MODE%==0 (
    echo Smoke test baslatiliyor...
    echo Komut: python -m uygulama.arayuz.smoke_test_calistir%SMOKE_ARGS%
    echo.
)

python -m uygulama.arayuz.smoke_test_calistir%SMOKE_ARGS%
set TEST_RESULT=%errorlevel%

echo.
if %TEST_RESULT%==0 (
    echo ========================================
    echo ✓ SMOKE TEST BASARILI!
    echo ========================================
    
    if not "%CSV_FILE%"=="" (
        echo ✓ CSV raporu olusturuldu: %CSV_FILE%
    )
    
    if %QUIET_MODE%==0 (
        echo.
        echo Log dosyasi: logs\ui_smoke_test.log
        echo.
        echo Ek komutlar:
        echo   CSV raporu: python -m uygulama.arayuz.smoke_test_calistir --csv
        echo   Belirli ekranlar: python -m uygulama.arayuz.smoke_test_calistir --screens pos_satis
        echo   Yardim: python -m uygulama.arayuz.smoke_test_calistir --help
    )
) else (
    echo ========================================
    echo ✗ SMOKE TEST BASARISIZ!
    echo ========================================
    echo Hata kodu: %TEST_RESULT%
    echo Log dosyasini kontrol edin: logs\ui_smoke_test.log
)

echo.
if %QUIET_MODE%==0 pause

exit /b %TEST_RESULT%