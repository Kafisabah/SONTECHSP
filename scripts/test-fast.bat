@echo off
REM Hızlı testleri çalıştır (yavaş testler hariç)
echo Hızlı testler çalıştırılıyor...
pytest -m "not slow" -v --tb=short --maxfail=10
echo.
echo Hızlı testler tamamlandı.
pause