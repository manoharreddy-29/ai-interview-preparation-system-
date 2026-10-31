@echo off
title AI-Based Student Answer Evaluation System
echo ======================================================================
echo    Starting AI-Based Student Answer Evaluation System
echo ======================================================================
echo.

REM Detect Python executable (prefer local virtual environment if present)
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
    goto :start_server
)

REM Fallback to system Python
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_EXE=python"
    goto :check_deps
)

python3.14 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_EXE=python3.14"
    goto :check_deps
)

py --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_EXE=py"
    goto :check_deps
)

echo [WARNING] Python command not found in PATH or environment.
echo Opening the web application directly in your default browser...
echo (Client-side AI/NLP evaluation engine will run automatically!)
echo.
start static\index.html
pause
exit /b

:check_deps
echo [1/3] Checking dependencies...
%PYTHON_EXE% -m pip install -r requirements.txt --quiet --disable-pip-version-check

:start_server
echo [2/3] Launching Flask Server on http://127.0.0.1:5000 ...
start "" http://127.0.0.1:5000

echo [3/3] Server running. Press Ctrl+C in this console to terminate.
echo ======================================================================
%PYTHON_EXE% app.py
pause
