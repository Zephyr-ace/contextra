@echo off
echo ===================================================
echo            Contextra Frontend Launcher
echo ===================================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed or not in PATH.
    echo Please install Node.js from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo Node.js detected: 
node --version
echo.

REM Navigate to frontend directory
echo Navigating to frontend directory...
cd frontend
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Could not navigate to frontend directory.
    echo Please make sure you're running this script from the Contextra root folder.
    echo.
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: npm install encountered issues.
    echo The application might still work if dependencies were previously installed.
    echo.
)

echo.
echo ===================================================
echo Starting development server...
echo The application will be available at http://localhost:3000
echo Press Ctrl+C to stop the server when finished
echo ===================================================
echo.

REM Start the development server
call npm run dev

REM This will only execute if npm run dev exits normally
echo.
echo Development server has stopped.
pause
