@echo off
REM ###############################################################################
REM Dell Boca Boys V2 - Installer Launcher (Windows)
REM Starts the web-based installation wizard
REM ###############################################################################

cls

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║              Dell Boca Boys V2 - Installer                    ║
echo ║          Enterprise AI Workflow Automation                    ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

echo Starting installation wizard...
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "INSTALLER_DIR=%SCRIPT_DIR%installer"

REM Check if Python 3 is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python 3 is required but not installed.
    echo.
    echo Please install Python 3 from: https://www.python.org/downloads/
    echo.
    echo IMPORTANT: During installation, check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip is required but not installed.
    echo.
    echo Installing pip...
    python -m ensurepip --upgrade
)

REM Create virtual environment if it doesn't exist
if not exist "%INSTALLER_DIR%\venv" (
    echo Creating Python virtual environment...
    python -m venv "%INSTALLER_DIR%\venv"
)

REM Activate virtual environment
call "%INSTALLER_DIR%\venv\Scripts\activate.bat"

REM Install required packages
echo Installing installer dependencies...
pip install --quiet --upgrade pip
pip install --quiet flask flask-socketio flask-cors psutil

REM Start the installer
echo.
echo Starting installer web interface...
echo.
echo Opening browser to: http://localhost:3000
echo.
echo IMPORTANT:
echo   - Do NOT close this window
echo   - The installer will open in your web browser
echo   - If browser doesn't open automatically, go to: http://localhost:3000
echo.
echo Press Ctrl+C to stop the installer
echo.

REM Wait a moment for the message to be read
timeout /t 2 /nobreak >nul

REM Start browser (in background)
start "" http://localhost:3000

REM Start the installer server
cd /d "%INSTALLER_DIR%"
python installer.py

REM Keep window open
pause
