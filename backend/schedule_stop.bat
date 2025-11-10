@echo off
echo ====================================
echo Stop Hourly Price Scraper
echo ====================================
echo.

set TASK_NAME=PriceScraperHourly

echo Checking admin privileges...
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

echo Deleting scheduled task: %TASK_NAME%
schtasks /Delete /TN "%TASK_NAME%" /F

if %errorlevel% neq 0 (
    echo.
    echo Task not found or already deleted.
) else (
    echo.
    echo ====================================
    echo SUCCESS! Task deleted
    echo ====================================
    echo.
    echo The hourly scraper has been stopped.
    echo.
)

pause
