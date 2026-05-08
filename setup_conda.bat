@echo off
echo ============================================
echo PDF to Obsidian - Conda Setup
echo ============================================
echo.

echo Removing old environment if exists...
call conda deactivate 2>nul
call conda env remove -n pdf2md -y 2>nul

echo.
echo Creating new conda environment with Python 3.10...
call conda env create -f environment.yml

if %errorlevel% neq 0 (
    echo ERROR: Failed to create conda environment
    pause
    exit /b 1
)

echo.
echo ============================================
echo Setup complete!
echo ============================================
echo.
echo To start the application:
echo   1. Activate: conda activate pdf2md
echo   2. Start Ollama: ollama serve
echo   3. Run app: python -m uvicorn backend.app.main:app --reload
echo.
echo Or use: start_app.bat
echo.
pause
