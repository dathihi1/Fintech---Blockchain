@echo off
echo ========================================
echo   Smart Trading Journal - Backend
echo ========================================
echo.

cd /d "%~dp0\..\backend"

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting backend server...
echo API: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo.

python main.py

pause
