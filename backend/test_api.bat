@echo off
cd /d "%~dp0"

echo ================================
echo Test API Server
echo ================================
echo.

echo Testing API endpoints...
echo.

echo [1] Health Check:
curl http://localhost:5000/api/health
echo.
echo.

echo [2] Search Test:
curl "http://localhost:5000/api/search?q=test"
echo.
echo.

echo [3] Root:
curl http://localhost:5000/
echo.
echo.

pause
