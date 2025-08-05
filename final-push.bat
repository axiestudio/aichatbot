@echo off
echo 🔥 FINAL CLEAN PUSH
echo.

echo 📋 Removing old Git history...
rmdir /s /q .git

echo 📋 Initializing fresh repository...
git init

echo 📋 Adding remote (you'll need to authenticate)...
git remote add origin https://github.com/axiestudio/aichatbot.git

echo 📋 Adding all files...
git add .

echo 📋 Creating clean commit...
git commit -m "🚀 Production-ready Modern Chatbot System - Clean Version"

echo 📋 Setting main branch...
git branch -M main

echo 📋 Pushing (you'll be prompted for credentials)...
git push -f origin main

echo.
echo ✅ SUCCESS! Repository pushed!
echo.
pause