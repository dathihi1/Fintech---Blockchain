@echo off
echo ========================================
echo   Smart Trading Journal - System Test
echo ========================================
echo.

cd /d "%~dp0\.."

echo Running Python system tests...
echo.

python scripts\system_test.py

pause
