@echo off
REM Quick start script for AI testing agent (Windows)

echo AI-Assisted UI Automation - Quick Start
echo =======================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is required but not found
    pause
    exit /b 1
)

echo ✓ Python found

REM Check if we're in the right directory
if not exist "src\main.py" (
    echo Error: Please run this script from the project root directory
    pause
    exit /b 1
)

REM Validate environment
echo Validating environment...
python validate_env.py
if errorlevel 1 (
    echo Environment validation failed. Please fix issues and try again.
    pause
    exit /b 1
)

REM Show available commands
echo.
echo Environment validation successful!
echo.
echo Available commands:
echo   python src\main.py --help                          # Show help
echo   python src\main.py --scenario swap_test --count 5  # Run 5 swaps
echo   python src\main.py --dry-run --scenario swap_test  # Dry run mode
echo.
echo Configuration:
echo   Edit config\production.yaml with your Azure credentials
echo.
echo Logs and reports will be saved in the 'logs\' directory
echo.

REM Ask if user wants to run a test
set /p choice="Would you like to run a dry-run test now? (y/n): "
if /i "%choice%"=="y" (
    echo Running dry-run test...
    python src\main.py --dry-run --scenario swap_test --count 1
)

pause
