@echo off
echo Starting Modern Chatbot System...
echo.

echo Starting Backend (FastAPI)...
start "Backend" cmd /k "cd backend && python start.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo Starting Frontend (React + Vite)...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Both services are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo Admin Panel: http://localhost:5173/admin
echo.
echo Press any key to exit...
pause > nul
