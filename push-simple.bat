@echo off
cd /d "%~dp0"

echo ================================
echo GitHub Push
echo ================================
echo.

git status
echo.

git add -A
echo.

git commit -m "Update: Search accuracy improvement v3.1"
echo.

git push origin main
echo.

if %errorlevel% equ 0 (
    echo.
    echo Push completed successfully!
    echo GitHub Pages: https://jiappa4.github.io/find-item2/
) else (
    echo.
    echo Push failed. Check:
    echo 1. Git credentials
    echo 2. Internet connection
    echo 3. Repository permissions
)

echo.
pause
