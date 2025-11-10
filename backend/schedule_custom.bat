@echo off
cd /d "%~dp0"

echo ================================
echo Custom Schedule Setup
echo ================================
echo.
echo Enter custom schedule interval:
echo Examples:
echo - Daily at 9AM: /sc daily /st 09:00
echo - Every 30 min: /sc minute /mo 30
echo - Mon-Fri 9AM: /sc weekly /d MON,TUE,WED,THU,FRI /st 09:00
echo.

set /p SCHEDULE_PARAMS=Enter schedule parameters: 

set SCRIPT_PATH=%~dp0run_scraper.bat

schtasks /create /tn "PriceScraper_Custom" /tr "%SCRIPT_PATH%" %SCHEDULE_PARAMS% /f

if %errorlevel% equ 0 (
    echo.
    echo Scheduled successfully!
    echo Task: PriceScraper_Custom
    echo.
    echo To check: schedule_status.bat
    echo To stop: schedule_stop.bat
) else (
    echo.
    echo Schedule failed!
)

echo.
pause
