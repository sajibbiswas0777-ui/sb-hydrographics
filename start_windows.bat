@echo off
title SB HYDRO-GRAPHICS Studio Management Software
echo ============================================================
echo   🌊 SB HYDRO-GRAPHICS - Water Transfer Printing Software
echo ============================================================
echo Starting local server on http://localhost:5000 ...

python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python detected. Starting backend...
    start http://localhost:5000
    python server.py
    pause
    exit /b
)

node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Node.js detected. Starting Node server...
    start http://localhost:5000
    node server.py
    pause
    exit /b
)

echo [ERROR] Neither Python nor Node.js found. Please install Python 3 or Node.js.
pause
