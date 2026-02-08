@echo off
echo ========================================
echo  OpenCngsm MCP v2.0 - Startup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ first
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js first
    pause
    exit /b 1
)

echo [1/4] Installing Python dependencies...
pip install -r requirements.txt >nul 2>&1

echo [2/4] Installing Node.js dependencies...
cd frontend
call npm install >nul 2>&1
cd ..

echo [3/4] Starting Backend (Gateway)...
start "OpenCngsm Backend" cmd /k "python core/gateway/gateway.py"

echo [4/4] Starting Frontend (React)...
timeout /t 3 /nobreak >nul
cd frontend
start "OpenCngsm Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo  System Started Successfully!
echo ========================================
echo.
echo Backend:  http://127.0.0.1:18789
echo Frontend: http://localhost:5173
echo.
echo Login credentials:
echo   User ID: admin
echo   Secret:  opencngsm_secret_2024
echo.
echo Press any key to open frontend in browser...
pause >nul

start http://localhost:5173

echo.
echo To stop the system, close both terminal windows.
echo.
