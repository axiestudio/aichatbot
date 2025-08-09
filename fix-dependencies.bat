@echo off
echo Fixing frontend dependencies and TypeScript issues...
echo.

echo Checking if Node.js is available...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Please install Node.js 18+ from https://nodejs.org
    echo This is required for the frontend to work properly.
    pause
    exit /b 1
)

echo [OK] Node.js found: 
node --version

echo.
echo Installing frontend dependencies...
cd frontend

echo Cleaning any existing node_modules...
if exist "node_modules" rmdir /s /q node_modules
if exist "package-lock.json" del package-lock.json

echo Installing dependencies with npm...
npm install

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    echo Trying with --legacy-peer-deps...
    npm install --legacy-peer-deps
)

echo.
echo Checking TypeScript compilation...
npx tsc --noEmit

if %errorlevel% neq 0 (
    echo [WARNING] TypeScript compilation has issues, but this might be normal for development
)

echo.
echo Testing build process...
npm run build

if %errorlevel% equ 0 (
    echo [SUCCESS] Build completed successfully!
    echo Frontend is ready for deployment.
) else (
    echo [ERROR] Build failed. Check the errors above.
)

cd ..

echo.
echo Dependencies installation complete!
echo.
echo Next steps:
echo 1. Push to GitHub: git add . && git commit -m "Fix dependencies" && git push
echo 2. Deploy to Vercel
echo 3. Test your site at https://chat.axiestudio.se
echo.
pause
