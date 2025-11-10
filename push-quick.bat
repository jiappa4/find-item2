@echo off
cd /d "%~dp0"
git add -A
git commit -m "Update v3.1"
git push origin main
pause
