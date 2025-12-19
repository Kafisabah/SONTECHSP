@echo off
REM Version: 1.0.0
REM Last Update: 2024-12-18
REM Module: scripts.ui-smoke-test-rapor
REM Description: UI smoke test rapor üretme script'i
REM Changelog:
REM - İlk versiyon: CSV rapor üretme ve analiz

setlocal enabledelayedexpansion

echo ========================================
echo SONTECHSP UI Smoke Test Rapor Uretici
echo ========================================

REM Sanal ortam kontrolü
if not exist "venv\Scripts\activate.bat" (
    echo HATA: Sanal ortam bulunamadi!
    echo Once kurulum script'ini calistirin: scripts\ui-smoke-test-kurulum.bat
    pause
    exit /b 1
)

REM Sanal ortamı aktifleştir
call venv\Scripts\activate.bat >nul 2>&1
if errorlevel 1 (
    echo HATA: Sanal ortam aktifleştirilemedi!
    pause
    exit /b 1
)

REM Tarih ve saat için dosya adı oluştur
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "datestamp=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"

REM Raporlar klasörünü oluştur
if not exist "raporlar" mkdir raporlar
if not exist "raporlar\ui_smoke_test" mkdir raporlar\ui_smoke_test

set RAPOR_DOSYASI=raporlar\ui_smoke_test\smoke_test_raporu_%datestamp%.csv

echo Smoke test calistiriliyor ve rapor uretiliyor...
echo Rapor dosyasi: %RAPOR_DOSYASI%
echo.

REM Smoke test çalıştır ve CSV raporu oluştur
python -m uygulama.arayuz.smoke_test_calistir --csv-file %RAPOR_DOSYASI%
set TEST_RESULT=%errorlevel%

echo.
if %TEST_RESULT%==0 (
    echo ========================================
    echo ✓ RAPOR BASARIYLA OLUSTURULDU!
    echo ========================================
    echo.
    echo Rapor dosyasi: %RAPOR_DOSYASI%
    
    REM Dosya boyutunu kontrol et
    for %%A in ("%RAPOR_DOSYASI%") do set DOSYA_BOYUTU=%%~zA
    echo Dosya boyutu: !DOSYA_BOYUTU! byte
    
    REM İlk birkaç satırı göster
    echo.
    echo Rapor onizlemesi:
    echo ------------------
    for /f "skip=0 tokens=*" %%i in ('type "%RAPOR_DOSYASI%" ^| more +0') do (
        echo %%i
        set /a "line_count+=1"
        if !line_count! geq 5 goto preview_done
    )
    :preview_done
    
    echo.
    echo Raporu acmak icin:
    echo   Excel: start excel "%RAPOR_DOSYASI%"
    echo   Notepad: notepad "%RAPOR_DOSYASI%"
    echo.
    
    REM Kullanıcıya raporu açma seçeneği sun
    set /p OPEN_CHOICE="Raporu Excel ile acmak istiyor musunuz? (E/H): "
    if /i "!OPEN_CHOICE!"=="E" (
        echo Excel ile aciliyor...
        start excel "%RAPOR_DOSYASI%"
    )
    
) else (
    echo ========================================
    echo ✗ RAPOR OLUSTURULAMADI!
    echo ========================================
    echo Hata kodu: %TEST_RESULT%
    echo Log dosyasini kontrol edin: logs\ui_smoke_test.log
)

echo.
echo Diger rapor komutlari:
echo   Tablo raporu: python -m uygulama.arayuz.smoke_test_calistir
echo   Konsol CSV: python -m uygulama.arayuz.smoke_test_calistir --csv
echo   Belirli ekranlar: python -m uygulama.arayuz.smoke_test_calistir --screens pos_satis --csv-file rapor.csv
echo.

pause
exit /b %TEST_RESULT%