@echo off
cd /d "%~dp0"

echo ================================
echo Port 5000 Diagnostic
echo ================================
echo.

echo [1] Checking if port 5000 is in use...
netstat -ano | findstr :5000
echo.

echo [2] Checking Python processes...
tasklist | findstr python.exe
echo.

echo [3] Testing localhost:5000...
curl http://localhost:5000/api/health 2>nul
if %errorlevel% neq 0 (
    echo Connection failed!
    echo.
    echo [4] Trying to access...
    powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:5000/api/health' -UseBasicParsing } catch { Write-Host 'Error:' $_.Exception.Message }"
) else (
    echo Connection successful!
)

echo.
echo [5] Firewall check...
echo Run as Administrator to check firewall rules
echo.

pause
