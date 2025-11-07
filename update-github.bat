@echo off
echo ====================================
echo Updating GitHub Repository
echo ====================================
echo.

cd /d C:\Users\netwo\Documents\find-item2

echo Adding changes...
git add .
if errorlevel 1 (
    echo Error: Failed to add files
    pause
    exit /b 1
)

echo Creating commit...
git commit -m "Update: 실용적인 가격 비교 도구로 개선 - 수동 입력 방식"
if errorlevel 1 (
    echo No changes to commit or commit failed
    git status
    pause
    exit /b 1
)

echo Pushing to GitHub...
git push origin main
if errorlevel 1 (
    echo Error: Failed to push
    pause
    exit /b 1
)

echo.
echo ====================================
echo SUCCESS! Changes pushed to GitHub
echo ====================================
echo.
echo Wait 1-2 minutes for deployment
echo Then visit: https://jiappa4.github.io/find-item2/
echo ====================================
pause
