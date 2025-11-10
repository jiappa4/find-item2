@echo off
echo ====================================
echo Custom Schedule Setup
echo 원하는 시간 간격으로 설정
echo ====================================
echo.

cd /d "%~dp0"

set SCRIPT_PATH=%CD%\run_scraper.bat
set TASK_NAME=PriceScraperCustom

echo Select schedule interval:
echo.
echo 1. Every 30 minutes
echo 2. Every 1 hour (recommended)
echo 3. Every 2 hours
echo 4. Every 3 hours
echo 5. Every 6 hours
echo 6. Every 12 hours
echo 7. Daily at 09:00
echo.
set /p CHOICE="Enter choice (1-7): "

if "%CHOICE%"=="1" (
    set SCHEDULE=MINUTE
    set INTERVAL=30
    set DESC=매 30분마다
)
if "%CHOICE%"=="2" (
    set SCHEDULE=HOURLY
    set INTERVAL=1
    set DESC=매 1시간마다
)
if "%CHOICE%"=="3" (
    set SCHEDULE=HOURLY
    set INTERVAL=2
    set DESC=매 2시간마다
)
if "%CHOICE%"=="4" (
    set SCHEDULE=HOURLY
    set INTERVAL=3
    set DESC=매 3시간마다
)
if "%CHOICE%"=="5" (
    set SCHEDULE=HOURLY
    set INTERVAL=6
    set DESC=매 6시간마다
)
if "%CHOICE%"=="6" (
    set SCHEDULE=HOURLY
    set INTERVAL=12
    set DESC=매 12시간마다
)
if "%CHOICE%"=="7" (
    set SCHEDULE=DAILY
    set INTERVAL=1
    set DESC=매일 오전 9시
)

if not defined SCHEDULE (
    echo Invalid choice!
    pause
    exit /b 1
)

echo.
echo Checking admin privileges...
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ====================================
    echo ERROR: 관리자 권한이 필요합니다!
    echo ====================================
    pause
    exit /b 1
)

echo Deleting existing task...
schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>&1

echo Creating new task: %DESC%
schtasks /Create ^
    /TN "%TASK_NAME%" ^
    /TR "%SCRIPT_PATH%" ^
    /SC %SCHEDULE% ^
    /MO %INTERVAL% ^
    /ST 09:00 ^
    /RL HIGHEST ^
    /F

if %errorlevel% neq 0 (
    echo Task creation failed!
    pause
    exit /b 1
)

echo.
echo ====================================
echo SUCCESS!
echo ====================================
echo.
echo Task: %TASK_NAME%
echo Schedule: %DESC%
echo Script: %SCRIPT_PATH%
echo.
echo The task is now active!
echo ====================================
pause
