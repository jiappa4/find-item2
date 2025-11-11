@echo off
cd /d "%~dp0"

echo ================================
echo Check Database Status
echo ================================
echo.

if not exist prices.db (
    echo ERROR: prices.db not found!
    echo Please run run_scraper.bat first
    pause
    exit /b 1
)

echo Database file exists
echo.

if not exist venv (
    echo Virtual environment not found!
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Checking tables...
python -c "import sqlite3; conn = sqlite3.connect('prices.db'); cursor = conn.cursor(); cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"'); print('Tables:', [row[0] for row in cursor.fetchall()]); conn.close()"

echo.
echo Checking columns...
python -c "import sqlite3; conn = sqlite3.connect('prices.db'); cursor = conn.cursor(); cursor.execute('PRAGMA table_info(products)'); print('\nColumns:'); [print(f'  - {row[1]} ({row[2]})') for row in cursor.fetchall()]; conn.close()"

echo.
echo Checking row count...
python -c "import sqlite3; conn = sqlite3.connect('prices.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM products'); print(f'\nTotal products: {cursor.fetchone()[0]}'); conn.close()"

echo.
echo Checking sample data...
python -c "import sqlite3; conn = sqlite3.connect('prices.db'); cursor = conn.cursor(); cursor.execute('SELECT search_query, name, brand, model_name FROM products LIMIT 5'); print('\nSample data:'); [print(f'{i+1}. Query: {row[0]}\n   Name: {row[1]}\n   Brand: {row[2]}, Model: {row[3]}\n') for i, row in enumerate(cursor.fetchall())]; conn.close()"

echo.
pause
