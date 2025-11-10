@echo off
cd /d "%~dp0"

echo ================================
echo Stop Scheduled Task
echo ================================
echo.

schtasks /delete /tn "PriceScraper_Hourly" /f

if %errorlevel% equ 0 (
    echo.
    echo Task deleted successfully!
) else (
    echo.
    echo Task not found or delete failed
)

echo.
pause
