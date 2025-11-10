@echo off
chcp 65001 >nul
echo ================================
echo Flask API 서버 실행
echo ================================
echo.

cd /d "%~dp0"

if not exist venv (
    echo ❌ 가상환경이 없습니다. setup.bat를 먼저 실행하세요.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo 🚀 API 서버 시작...
echo 📍 http://localhost:5000
echo.
python api_server.py
