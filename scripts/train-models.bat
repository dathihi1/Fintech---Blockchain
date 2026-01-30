@echo off
echo ========================================
echo   ML Training Pipeline
echo ========================================
echo.

cd /d "%~dp0\.."

echo Step 1: Preparing datasets...
python ml/training/prepare_dataset.py
if errorlevel 1 (
    echo Failed to prepare datasets
    pause
    exit /b 1
)

echo.
echo Step 2: Training NLP model (requires GPU for best results)...
echo This may take 10-30 minutes...
python ml/training/train_nlp.py
if errorlevel 1 (
    echo NLP training failed or skipped
)

echo.
echo Step 3: Training behavioral classifier...
python ml/behavioral/train_classifier.py
if errorlevel 1 (
    echo Behavioral training failed
)

echo.
echo ========================================
echo   Training Complete!
echo ========================================
echo.
echo Models saved to:
echo   - ml/models/finbert_trading_vi/
echo   - ml/models/behavioral_classifier.json
echo.

pause
