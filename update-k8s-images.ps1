# 🐳 Update Kubernetes Manifests with Docker Hub Images
# Run this script after setting up Docker Hub to update all K8s files

param(
    [Parameter(Mandatory=$true)]
    [string]$DockerHubUsername,

    [Parameter(Mandatory=$false)]
    [string]$ImageTag = "latest"
)

Write-Host "🚀 Updating Kubernetes manifests with Docker Hub images..." -ForegroundColor Green
Write-Host "Docker Hub Username: $DockerHubUsername" -ForegroundColor Yellow
Write-Host "Image Tag: $ImageTag" -ForegroundColor Yellow

# Define the image replacements
$backendImage = "$DockerHubUsername/chatbot-backend:$ImageTag"
$frontendImage = "$DockerHubUsername/chatbot-frontend:$ImageTag"

Write-Host "`n📦 Images to use:" -ForegroundColor Cyan
Write-Host "Backend:  $backendImage" -ForegroundColor White
Write-Host "Frontend: $frontendImage" -ForegroundColor White

# Update backend.yaml
$backendFile = "k8s/backend.yaml"
if (Test-Path $backendFile) {
    Write-Host "`n🔧 Updating $backendFile..." -ForegroundColor Blue
    $content = Get-Content $backendFile -Raw
    $content = $content -replace 'image: .*chatbot-backend.*', "image: $backendImage"
    Set-Content $backendFile $content
    Write-Host "✅ Updated backend image" -ForegroundColor Green
} else {
    Write-Host "❌ $backendFile not found!" -ForegroundColor Red
}

# Update frontend.yaml
$frontendFile = "k8s/frontend.yaml"
if (Test-Path $frontendFile) {
    Write-Host "🔧 Updating $frontendFile..." -ForegroundColor Blue
    $content = Get-Content $frontendFile -Raw
    $content = $content -replace 'image: .*chatbot-frontend.*', "image: $frontendImage"
    Set-Content $frontendFile $content
    Write-Host "✅ Updated frontend image" -ForegroundColor Green
} else {
    Write-Host "❌ $frontendFile not found!" -ForegroundColor Red
}

# Update docker-compose.production.yml
$composeFile = "docker-compose.production.yml"
if (Test-Path $composeFile) {
    Write-Host "🔧 Updating $composeFile..." -ForegroundColor Blue
    $content = Get-Content $composeFile -Raw
    $content = $content -replace 'image: .*chatbot-backend.*', "image: $backendImage"
    $content = $content -replace 'image: .*chatbot-frontend.*', "image: $frontendImage"
    Set-Content $composeFile $content
    Write-Host "✅ Updated docker-compose production file" -ForegroundColor Green
} else {
    Write-Host "⚠️ $composeFile not found (optional)" -ForegroundColor Yellow
}

Write-Host "`n🎉 All Kubernetes manifests updated successfully!" -ForegroundColor Green
Write-Host "`n📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Commit and push your changes to GitHub" -ForegroundColor White
Write-Host "2. GitHub Actions will build and push your Docker images" -ForegroundColor White
Write-Host "3. Deploy to Kubernetes: kubectl apply -f k8s/" -ForegroundColor White

Write-Host "`n🔍 Verify the changes:" -ForegroundColor Cyan
Write-Host "git diff k8s/" -ForegroundColor White