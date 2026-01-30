@echo off
echo ========================================
echo   Smart Trading Journal - Frontend
echo ========================================
echo.

cd /d "%~dp0\..\frontend"

echo Installing dependencies...
call npm install

echo Installing recharts...
call npm install recharts

echo.
echo Starting frontend dev server...
echo App: http://localhost:5173
echo.

call npm run dev

pause
