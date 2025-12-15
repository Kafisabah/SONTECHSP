@echo off
echo 🚀 SONTECHSP Otomatik Senkronizasyon
echo ====================================
echo.
echo 📅 Her 30 dakikada bir GitHub'a otomatik yükleme yapılacak
echo ⏹️  Durdurmak için Ctrl+C basın
echo.

python -m pip install schedule >nul 2>&1

python scripts/otomatik-senkron.py

pause