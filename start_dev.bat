@echo off
chcp 65001 > nul
echo ================================
echo    Find-Item 개발 서버 시작
echo ================================
echo.

REM 가상환경 활성화
echo [1/3] 가상환경 활성화 중...
call backend\venv\Scripts\activate.bat

REM API 서버 시작 (새 창에서)
echo [2/3] API 서버 시작 중...
start "API Server" cmd /k "cd /d %~dp0backend && venv\Scripts\activate.bat && python api_server.py"

REM 잠시 대기 (API 서버가 시작될 시간)
timeout /t 3 /nobreak > nul

REM 웹 브라우저 열기
echo [3/3] 웹 브라우저 실행 중...
start http://localhost:5000

echo.
echo ================================
echo    서버가 시작되었습니다!
echo    브라우저: http://localhost:5000
echo    API: http://localhost:5000/api
echo ================================
echo.
echo 종료하려면 API Server 창을 닫으세요.
pause
