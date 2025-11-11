@echo off
echo ================================
echo Kill all Python processes
echo ================================
echo.

taskkill /F /IM python.exe 2>nul
if %errorlevel% equ 0 (
    echo Python processes killed
) else (
    echo No Python processes found
)

timeout /t 2 >nul

echo.
echo ================================
echo Starting API Server
echo ================================
echo.

cd /d "%~dp0"

if not exist venv (
    echo Virtual environment not found!
    echo Run setup.bat first
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo.
echo Current directory: %CD%
echo Python path:
where python
echo.

python api_server.py

pause
