@echo off
cd /d "%~dp0"

echo ================================
echo Schedule Hourly Scraping
echo ================================
echo.

set SCRIPT_PATH=%~dp0run_scraper.bat

schtasks /create /tn "PriceScraper_Hourly" /tr "%SCRIPT_PATH%" /sc hourly /f

if %errorlevel% equ 0 (
    echo.
    echo Scheduled successfully!
    echo Task: PriceScraper_Hourly
    echo Frequency: Every hour
    echo.
    echo To check status: schedule_status.bat
    echo To stop: schedule_stop.bat
) else (
    echo.
    echo Schedule failed!
    echo Run as Administrator
)

echo.
pause
