@echo off
title Shivansh Astro-Vastu Professional (PC Edition)
color 0E

echo ==============================================================================
echo           SHIVANSH ASTRO-VASTU PROFESSIONAL CRM & KUNDLI SUITE
echo ==============================================================================
echo.
echo [1/3] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python is not found on your system PATH!
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check the box "Add Python to PATH" during installation.
    echo.
    pause
    exit /b
)

python --version
echo.
echo [2/3] Checking required packages...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo Note: Some packages may need administrative install, retrying...
    pip install fastapi uvicorn astronomy-engine pydantic pypdf pillow
)

echo.
echo [3/3] Starting Shivansh Astro-Vastu Server...
echo ------------------------------------------------------------------------------
echo App will open automatically in your default web browser in 2-3 seconds.
echo If it does not open, visit: http://127.0.0.1:8088
echo.
echo Login Username: Admin
echo Login Password: Harman
echo ------------------------------------------------------------------------------
echo Do NOT close this window while using the application.
echo To stop the application, press Ctrl+C or close this window.
echo ==============================================================================
echo.

python app.py
pause
