@echo off
REM Version: 0.1.0
REM Last Update: 2024-12-19
REM Module: pos_kod_kalitesi_kontrol_bat
REM Description: POS kod kalitesi kontrol Windows batch script'i
REM Changelog:
REM - İlk oluşturma - Windows batch wrapper

echo.
echo ========================================
echo   POS Kod Kalitesi Kontrol Aracı
echo ========================================
echo.

REM Python script'ini çalıştır
python scripts\pos-kod-kalitesi-kontrol.py %*

REM Çıkış kodunu koru
set EXIT_CODE=%ERRORLEVEL%

echo.
echo ========================================
echo   Analiz Tamamlandı
echo ========================================

REM Çıkış kodu ile çık
exit /b %EXIT_CODE%