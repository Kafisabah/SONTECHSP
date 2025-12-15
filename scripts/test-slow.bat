@echo off
REM Yavaş testleri çalıştır
echo Yavaş testler çalıştırılıyor...
pytest -m slow -v --tb=short
echo.
echo Yavaş testler tamamlandı.
pause