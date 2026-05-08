@echo off
echo ============================================
echo PDF to Obsidian Converter
echo ============================================
echo.

REM Check if Ollama is running
echo [1/3] Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Ollama is not running!
    echo.
    echo Please start Ollama in a separate terminal:
    echo   ollama serve
    echo.
    echo Or check if glm-ocr model is installed:
    echo   ollama pull glm-ocr
    echo.
    pause
    exit /b 1
)
echo [OK] Ollama is running
echo.

REM Activate conda environment
echo [2/3] Activating conda environment...
call conda activate pdf2md
if %errorlevel% neq 0 (
    echo [ERROR] Conda environment 'pdf2md' not found!
    echo Please run setup_conda.bat first.
    pause
    exit /b 1
)
echo [OK] Environment activated: pdf2md
echo.

REM Start server
echo [3/3] Starting FastAPI server...
echo.
echo ============================================
echo Server starting at: http://localhost:8000
echo Press Ctrl+C to stop
echo ============================================
echo.

python -m uvicorn backend.app.main:app --reload
