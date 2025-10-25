@echo off
echo ========================================
echo  Medi-Flow Systems - Backend Startup
echo  Smart Management. Better Health.
echo ========================================
echo.

echo [1/3] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)
echo.

echo [2/3] Starting Flask server...
echo Backend will run on http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
