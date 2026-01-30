@echo off
echo ========================================
echo   Smart Trading Journal - Full Stack
echo ========================================
echo.
echo This will open TWO terminals:
echo   1. Backend (Python FastAPI)
echo   2. Frontend (React Vite)
echo.

REM Start backend in new window
start "Backend" cmd /k "%~dp0start-backend.bat"

REM Wait a moment for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend in new window
start "Frontend" cmd /k "%~dp0start-frontend.bat"

echo Both servers starting...
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.

pause
