@echo off
echo ====================================
echo Windows Task Scheduler Setup
echo 1시간마다 가격 수집 배치 자동 실행
echo ====================================
echo.

cd /d "%~dp0"

set SCRIPT_PATH=%CD%\run_scraper.bat
set TASK_NAME=PriceScraperHourly

echo Task Name: %TASK_NAME%
echo Script Path: %SCRIPT_PATH%
echo.

echo [1/3] Checking admin privileges...
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ====================================
    echo ERROR: 관리자 권한이 필요합니다!
    echo ====================================
    echo.
    echo 이 스크립트를 마우스 우클릭 후
    echo "관리자 권한으로 실행"을 선택하세요.
    echo ====================================
    pause
    exit /b 1
)
echo Admin privileges confirmed!
echo.

echo [2/3] Deleting existing task (if any)...
schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>&1
echo.

echo [3/3] Creating new scheduled task...
schtasks /Create ^
    /TN "%TASK_NAME%" ^
    /TR "%SCRIPT_PATH%" ^
    /SC HOURLY ^
    /MO 1 ^
    /ST 09:00 ^
    /RL HIGHEST ^
    /F

if %errorlevel% neq 0 (
    echo.
    echo ====================================
    echo ERROR: Task creation failed
    echo ====================================
    pause
    exit /b 1
)

echo.
echo ====================================
echo SUCCESS! Task created successfully
echo ====================================
echo.
echo Task Details:
echo - Name: %TASK_NAME%
echo - Frequency: Every 1 hour
echo - Start time: 09:00 (first run today)
echo - Script: %SCRIPT_PATH%
echo.
echo The task will run:
echo - 09:00, 10:00, 11:00, ... 23:00 (every hour)
echo.
echo To view/modify the task:
echo 1. Press Win + R
echo 2. Type: taskschd.msc
echo 3. Find: %TASK_NAME%
echo.
echo To disable the task:
echo - run_scraper_stop.bat
echo ====================================
pause
