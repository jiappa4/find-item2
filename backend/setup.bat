@echo off
chcp 65001 >nul
echo ================================
echo 백엔드 환경 설정
echo ================================
echo.

cd /d "%~dp0"

echo 1. 가상환경 생성 중...
python -m venv venv

echo 2. 가상환경 활성화...
call venv\Scripts\activate.bat

echo 3. 패키지 설치 중...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ✅ 설정 완료!
echo.
echo 다음 단계:
echo 1. run_migration.bat (최초 1회)
echo 2. run_scraper.bat (데이터 수집)
echo 3. run_api.bat (서버 실행)
echo.
pause
