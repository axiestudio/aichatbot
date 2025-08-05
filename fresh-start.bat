@echo off
echo 🔥 FRESH START - CLEAN HISTORY
echo.

echo 📋 Step 1: Removing old Git history...
rmdir /s /q .git

echo 📋 Step 2: Initializing fresh Git repository...
git init

echo 📋 Step 3: Adding remote repository...
git remote add origin https://github.com/axiestudio/aichatbot.git

echo 📋 Step 4: Adding all clean files...
git add .

echo 📋 Step 5: Creating initial commit (no secrets)...
git commit -m "🚀 Initial commit - Production-ready Modern Chatbot System"

echo 📋 Step 6: Setting main branch...
git branch -M main

echo 📋 Step 7: Force pushing clean history...
git push -f origin main

echo.
echo ✅ SUCCESS! Fresh clean repository pushed!
echo 🔑 Now add your Docker Hub secret:
echo    Go to: https://github.com/axiestudio/aichatbot/settings/secrets/actions
echo    Name: DOCKERHUB_TOKEN
echo    Value: [Your Docker Hub Token]
echo.
echo 📊 Monitor builds: https://github.com/axiestudio/aichatbot/actions
echo.
pause