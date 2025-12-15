@echo off
REM Paralel test çalıştırma (tüm testler)
echo Paralel testler çalıştırılıyor...
pytest -n auto -v --tb=short --cov=sontechsp --cov-report=html --cov-report=term-missing
echo.
echo Paralel testler tamamlandı. Coverage raporu htmlcov/ klasöründe.
pause