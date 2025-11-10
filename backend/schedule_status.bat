@echo off
cd /d "%~dp0"

echo ================================
echo Schedule Status
echo ================================
echo.

schtasks /query /tn "PriceScraper_Hourly" /fo LIST /v

echo.
pause
