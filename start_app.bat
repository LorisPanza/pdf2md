@echo off
title PDF to Obsidian
color 0A

echo.
echo ========================================
echo    PDF to Obsidian Converter
echo ========================================
echo.

REM Check Ollama
echo [1/2] Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Ollama not running!
    echo.
    echo Start Ollama first: ollama serve
    echo.
    pause
    exit /b 1
)
echo [OK] Ollama running
echo.

REM Activate environment
echo [2/2] Starting app...
call conda activate pdf2md 2>nul
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Environment 'pdf2md' not found!
    echo.
    echo Setup first: conda env create -f environment.yml
    echo See README.md for details
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Server: http://localhost:8000
echo   Press Ctrl+C to stop
echo ========================================
echo.

python -m uvicorn backend.app.main:app --reload
