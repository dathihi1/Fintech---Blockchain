@echo off
echo ========================================
echo   Smart Trading Journal - Run Tests
echo ========================================
echo.

cd /d "%~dp0\..\backend"

echo Running API tests...
python tests/test_api.py

echo.
echo Running NLP tests...
python tests/test_nlp.py

echo.
echo Running Analyzer tests...
python tests/test_analyzers.py

echo.
echo ========================================
echo   All tests complete!
echo ========================================

pause
