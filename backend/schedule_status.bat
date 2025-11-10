@echo off
echo ====================================
echo View Scheduled Tasks Status
echo ====================================
echo.

set TASK_NAME=PriceScraperHourly

echo Checking task status...
echo.

schtasks /Query /TN "%TASK_NAME%" /FO LIST /V 2>nul

if %errorlevel% neq 0 (
    echo ====================================
    echo Task not found: %TASK_NAME%
    echo ====================================
    echo.
    echo The hourly scraper is NOT scheduled.
    echo Run schedule_hourly.bat to enable it.
    echo.
) else (
    echo.
    echo ====================================
    echo Task is ACTIVE
    echo ====================================
    echo.
    echo To view all details:
    echo 1. Press Win + R
    echo 2. Type: taskschd.msc
    echo 3. Find: %TASK_NAME%
    echo.
)

echo.
echo Recent task runs (if any):
schtasks /Query /TN "%TASK_NAME%" /FO TABLE /V 2>nul | findstr /I "Last Next"

echo.
pause
