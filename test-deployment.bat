@echo off
echo 🧪 COMPREHENSIVE DEPLOYMENT TEST
echo =================================

echo 1. Checking project structure...

if exist "frontend\package.json" (
    echo ✅ Found frontend\package.json
) else (
    echo ❌ Missing frontend\package.json
    exit /b 1
)

if exist "frontend\Dockerfile" (
    echo ✅ Found frontend\Dockerfile
) else (
    echo ❌ Missing frontend\Dockerfile
    exit /b 1
)

if exist "backend\requirements.txt" (
    echo ✅ Found backend\requirements.txt
) else (
    echo ❌ Missing backend\requirements.txt
    exit /b 1
)

if exist "backend\Dockerfile" (
    echo ✅ Found backend\Dockerfile
) else (
    echo ❌ Missing backend\Dockerfile
    exit /b 1
)

if exist "docker-compose.yml" (
    echo ✅ Found docker-compose.yml
) else (
    echo ❌ Missing docker-compose.yml
    exit /b 1
)

if exist "backend\app\main.py" (
    echo ✅ Found backend\app\main.py
) else (
    echo ❌ Missing backend\app\main.py
    exit /b 1
)

if exist "frontend\src\App.tsx" (
    echo ✅ Found frontend\src\App.tsx
) else (
    echo ❌ Missing frontend\src\App.tsx
    exit /b 1
)

echo.
echo 2. Checking environment files...

if exist "backend\.env" (
    echo ✅ Backend .env exists
) else (
    echo ⚠️  Backend .env missing - copying from .env.example
    copy "backend\.env.example" "backend\.env" >nul
)

if exist "frontend\.env" (
    echo ✅ Frontend .env exists
) else (
    echo ⚠️  Frontend .env missing - copying from .env.example
    copy "frontend\.env.example" "frontend\.env" >nul
)

echo.
echo 3. Testing Docker Compose validation...

docker-compose config >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker Compose development config validation
) else (
    echo ❌ Docker Compose development config validation failed
    exit /b 1
)

docker-compose -f docker-compose.prod.yml config >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker Compose production config validation
) else (
    echo ❌ Docker Compose production config validation failed
    exit /b 1
)

echo.
echo 🎉 DEPLOYMENT TEST COMPLETE!
echo =============================
echo.
echo ✅ All tests passed! Your application is ready for Docker deployment.
echo.
echo Next steps:
echo 1. Install dependencies: install.bat
echo 2. Start application: start.bat
echo 3. Access: http://localhost:5173 (frontend) and http://localhost:8000 (backend)
echo.
echo For Docker deployment:
echo 1. Development: docker-compose up --build
echo 2. Production: docker-compose -f docker-compose.prod.yml up --build
echo.
pause
