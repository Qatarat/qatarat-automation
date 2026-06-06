@echo off
REM Windows — one-command launcher + test runner
REM Usage:
REM   run.bat               -> start app only
REM   run.bat smoke         -> app + Maestro smoke tests
REM   run.bat regression    -> app + all 50 Maestro flows
REM   run.bat appium        -> app + all 191 Appium tests
REM   run.bat all           -> app + Maestro regression + Appium
cd /d "%~dp0"

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Install from https://python.org
    pause
    exit /b 1
)

python run.py %*
pause
