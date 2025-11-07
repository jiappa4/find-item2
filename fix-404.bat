@echo off
echo ====================================
echo GitHub Pages 404 Fix - Force Rebuild
echo ====================================
echo.

cd /d C:\Users\netwo\Documents\find-item2

echo Creating empty commit to trigger rebuild...
git commit --allow-empty -m "Trigger GitHub Pages rebuild"
if errorlevel 1 (
    echo Error: Failed to create commit
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
echo SUCCESS! Rebuild triggered
echo ====================================
echo.
echo Wait 2-3 minutes, then check:
echo https://github.com/jiappa4/find-item2/actions
echo.
echo After deployment completes, visit:
echo https://jiappa4.github.io/find-item2/
echo ====================================
pause
