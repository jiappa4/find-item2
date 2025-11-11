@echo off
cd /d "%~dp0"

echo ================================
echo Database Check
echo ================================
echo.

if not exist venv (
    echo Virtual environment not found!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

python -c "import sqlite3; conn = sqlite3.connect('prices.db'); cursor = conn.cursor(); cursor.execute('SELECT name, brand, model_name, search_query FROM products LIMIT 20'); print('\n'.join([f'{i+1}. [{row[1]}] {row[2]} - {row[0][:50]}... (Query: {row[3]})' for i, row in enumerate(cursor.fetchall())])); conn.close()"

echo.
echo.
echo Check brand and model_name columns
echo.

pause
