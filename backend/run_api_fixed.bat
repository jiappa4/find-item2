@echo off
cd /d "%~dp0"

echo ================================
echo Flask API Server (Port Check)
echo ================================
echo.

if not exist venv (
    echo Virtual environment not found. Run setup.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Checking port 5000...
netstat -ano | findstr :5000
if %errorlevel% equ 0 (
    echo.
    echo WARNING: Port 5000 is already in use!
    echo Trying to kill the process...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000') do (
        taskkill /F /PID %%a 2>nul
    )
    timeout /t 2 >nul
)

echo.
echo Starting API server on 0.0.0.0:5000...
echo.
echo Access URLs:
echo - http://localhost:5000
echo - http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python api_server.py

pause
