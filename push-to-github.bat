@echo off
echo 🚀 PUSHING TO GITHUB: https://github.com/axiestudio/aichatbot
echo.

echo 📋 Step 1: Initializing Git repository...
git init

echo 📋 Step 2: Adding remote repository...
git remote add origin https://github.com/axiestudio/aichatbot.git

echo 📋 Step 3: Adding all files...
git add .

echo 📋 Step 4: Committing changes...
git commit -m "🚀 Production-ready Modern Chatbot System with Docker Hub CI/CD"

echo 📋 Step 5: Setting main branch...
git branch -M main

echo 📋 Step 6: Pushing to GitHub...
git push -u origin main

echo.
echo ✅ SUCCESS! Your code has been pushed to GitHub!
echo 🐳 Docker images will be built automatically!
echo.
echo 📊 Monitor the build at:
echo    https://github.com/axiestudio/aichatbot/actions
echo.
pause