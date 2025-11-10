@echo off
cd /d "%~dp0"

echo ================================
echo Database Migration
echo ================================
echo.

if not exist venv (
    echo Virtual environment not found. Run setup.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Running database migration...
python migrate_db.py

if %errorlevel% equ 0 (
    echo.
    echo Migration completed!
    echo.
    echo Next step: run_scraper.bat
) else (
    echo.
    echo Migration failed!
)

echo.
pause
