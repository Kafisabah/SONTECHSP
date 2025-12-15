@echo off
REM Kritik testleri çalıştır (CI/CD için)
echo Kritik testler çalıştırılıyor...
pytest -m critical -v --tb=short --maxfail=5
echo.
echo Kritik testler tamamlandı.
pause