@echo off
chcp 65001 >nul
echo ================================
echo DB 마이그레이션 실행
echo ================================
echo.

cd /d "%~dp0"

if not exist venv (
    echo ❌ 가상환경이 없습니다. setup.bat를 먼저 실행하세요.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo 🔧 DB 스키마 마이그레이션 중...
python migrate_db.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ 마이그레이션 완료!
    echo.
    echo 이제 run_scraper.bat를 실행하여 데이터를 수집하세요.
) else (
    echo.
    echo ❌ 마이그레이션 실패
)

echo.
pause
