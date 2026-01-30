@echo off
REM Run NLP Benchmarks
REM Benchmarks language detection, emotion detection, and performance

echo ========================================
echo Running NLP Benchmarks
echo ========================================
echo.

cd /d "%~dp0\..\backend"

REM Run benchmark
python scripts\benchmark_nlp.py

echo.
echo ========================================
echo Benchmark complete!
echo ========================================
pause
