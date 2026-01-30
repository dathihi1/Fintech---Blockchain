@echo off
echo ========================================
echo   Download Large Datasets
echo ========================================
echo.

cd /d "%~dp0\..\backend"

echo Installing required libraries...
pip install datasets pandas kaggle

echo.
echo Downloading datasets from HuggingFace...
python ml/training/download_datasets.py

echo.
echo ========================================
echo   Download Complete!
echo ========================================
echo.
echo Datasets saved to: backend/ml/training/datasets/
echo.
echo To download Kaggle datasets manually:
echo   1. Go to kaggle.com/account and get API key
echo   2. Save to C:\Users\[You]\.kaggle\kaggle.json
echo   3. Run: kaggle datasets download -d [dataset-name]
echo.

pause
