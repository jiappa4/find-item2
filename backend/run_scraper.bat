@echo off
cd /d "%~dp0"

echo ================================
echo Price Scraper (Batch)
echo ================================
echo.

if not exist venv (
    echo Virtual environment not found. Run setup.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Running scraper...
python scraper.py

echo.
echo Scraping completed!
echo.
pause
