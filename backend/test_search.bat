@echo off
cd /d "%~dp0"

echo ================================
echo Search Accuracy Test
echo ================================
echo.

if not exist venv (
    echo Virtual environment not found!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

python test_search.py

echo.
echo.
echo Check the scores above
echo Products with score less than 50 should be filtered out
echo.

pause
