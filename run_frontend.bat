@echo off
echo Starting Contextra Frontend...
echo.

echo Navigating to frontend directory...
cd frontend

echo Installing dependencies...
call npm install

echo.
echo Starting development server...
call npm run dev

echo.
echo If the browser doesn't open automatically, navigate to http://localhost:3000
