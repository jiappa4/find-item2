@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ====================================
echo Updating GitHub Repository
echo ====================================
echo.

echo [1/3] Adding changes...
git add .
if %errorlevel% neq 0 (
    echo Error: Failed to add files
    pause
    exit /b 1
)
echo Done!
echo.

echo [2/3] Creating commit...
git commit -m "Update: Practical price comparison tool with manual input"
if %errorlevel% neq 0 (
    echo Error: Commit failed
    git status
    pause
    exit /b 1
)
echo Done!
echo.

echo [3/3] Pushing to GitHub...
git push origin main
if %errorlevel% neq 0 (
    echo Error: Failed to push
    pause
    exit /b 1
)
echo Done!
echo.

echo ====================================
echo SUCCESS! Changes pushed to GitHub
echo ====================================
echo.
echo Wait 1-2 minutes for deployment
echo Then visit: https://jiappa4.github.io/find-item2/
echo ====================================
echo.
pause
