@echo off
REM Run NLP Integration Tests
REM Tests all improvements to NLP and ML components

echo ========================================
echo Running NLP Integration Tests
echo ========================================
echo.

cd /d "%~dp0\.."

REM Run integration tests
python tests\test_integration_nlp.py

echo.
echo ========================================
echo Integration tests complete!
echo ========================================
pause
