@echo off
echo 🚀 PUSHING CLEAN VERSION TO GITHUB
echo.

echo 📋 Adding cleaned files...
git add .

echo 📋 Committing clean version...
git commit -m "🔒 Remove secrets - Clean production-ready chatbot system"

echo 📋 Pushing clean version to GitHub...
git push origin main

echo.
echo ✅ SUCCESS! Clean version pushed to GitHub!
echo 🔑 Now add your Docker Hub token as a GitHub secret:
echo    Go to: https://github.com/axiestudio/aichatbot/settings/secrets/actions
echo    Name: DOCKERHUB_TOKEN
echo    Value: [Your Docker Hub token]
echo.
echo 📊 Monitor builds at: https://github.com/axiestudio/aichatbot/actions
echo.
pause