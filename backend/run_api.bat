@echo off
cd /d "%~dp0"

echo ================================
echo Flask API Server
echo ================================
echo.

if not exist venv (
    echo Virtual environment not found. Run setup.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Starting API server...
echo Server will run at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python api_server.py

pause
