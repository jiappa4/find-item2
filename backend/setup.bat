@echo off
echo ====================================
echo Price Scraper Batch Setup
echo ====================================
echo.

cd /d "%~dp0"

echo [1/4] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo Error: Python is not installed
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)
echo.

echo [2/4] Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)
echo.

echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo [4/4] Installing dependencies...
pip install -r requirements.txt
echo.

echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo To run the scraper:
echo   1. run_scraper.bat
echo.
echo To start API server:
echo   2. run_api.bat
echo.
pause
