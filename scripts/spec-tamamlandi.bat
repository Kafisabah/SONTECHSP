@echo off
echo 🎯 SONTECHSP Spec Tamamlama Scripti
echo =====================================

if "%1"=="" (
    echo Kullanim: spec-tamamlandi.bat [spec_adi] [version_tipi]
    echo Ornek: spec-tamamlandi.bat "stok-yonetimi" minor
    exit /b 1
)

set SPEC_NAME=%1
set VERSION_TYPE=%2
if "%VERSION_TYPE%"=="" set VERSION_TYPE=minor

echo 📋 Spec: %SPEC_NAME%
echo 🔢 Version Tipi: %VERSION_TYPE%
echo.

python scripts/spec-tamamlandi.py "%SPEC_NAME%" --version-type %VERSION_TYPE%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Spec tamamlama işlemi başarılı!
    echo 🔗 GitHub'da kontrol edin: https://github.com/Kafisabah/SONTECHSP
) else (
    echo.
    echo ❌ Hata oluştu! Lütfen logları kontrol edin.
)

pause