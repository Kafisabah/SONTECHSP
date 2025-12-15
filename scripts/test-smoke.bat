@echo off
REM Smoke testleri çalıştır (temel işlevsellik)
echo Smoke testler çalıştırılıyor...
pytest -m smoke -v --tb=short
echo.
echo Smoke testler tamamlandı.
pause