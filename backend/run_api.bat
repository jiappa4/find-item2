@echo off
echo ====================================
echo Starting Flask API Server
echo ====================================
echo.

cd /d "%~dp0"

call venv\Scripts\activate.bat

echo Server will be available at:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python api_server.py

pause
