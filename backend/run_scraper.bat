@echo off
echo ====================================
echo Running Price Scraper Batch
echo ====================================
echo.

cd /d "%~dp0"

call venv\Scripts\activate.bat

python scraper.py

echo.
echo ====================================
echo Batch Complete!
echo ====================================
echo.
echo Check the generated JSON files
echo.
pause
