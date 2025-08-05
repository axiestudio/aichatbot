#!/bin/bash

echo "🧪 COMPREHENSIVE DEPLOYMENT TEST"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        exit 1
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo "1. Checking project structure..."

# Check essential files
files=(
    "frontend/package.json"
    "frontend/Dockerfile"
    "frontend/Dockerfile.prod"
    "backend/requirements.txt"
    "backend/Dockerfile"
    "backend/Dockerfile.prod"
    "docker-compose.yml"
    "docker-compose.prod.yml"
    "backend/app/main.py"
    "frontend/src/App.tsx"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        print_status 0 "Found $file"
    else
        print_status 1 "Missing $file"
    fi
done

echo ""
echo "2. Checking environment files..."

# Check .env files exist
if [ -f "backend/.env" ]; then
    print_status 0 "Backend .env exists"
else
    print_warning "Backend .env missing - copying from .env.example"
    cp backend/.env.example backend/.env
fi

if [ -f "frontend/.env" ]; then
    print_status 0 "Frontend .env exists"
else
    print_warning "Frontend .env missing - copying from .env.example"
    cp frontend/.env.example frontend/.env
fi

echo ""
echo "3. Testing Docker builds..."

# Test backend Docker build
echo "Building backend Docker image..."
cd backend
docker build -t chatbot-backend-test . > /dev/null 2>&1
print_status $? "Backend Docker build"
cd ..

# Test frontend Docker build
echo "Building frontend Docker image..."
cd frontend
docker build -t chatbot-frontend-test . > /dev/null 2>&1
print_status $? "Frontend Docker build"
cd ..

echo ""
echo "4. Testing production Docker builds..."

# Test backend production build
echo "Building backend production image..."
docker build -f backend/Dockerfile.prod -t chatbot-backend-prod-test backend/ > /dev/null 2>&1
print_status $? "Backend production Docker build"

# Test frontend production build
echo "Building frontend production image..."
docker build -f frontend/Dockerfile.prod -t chatbot-frontend-prod-test frontend/ > /dev/null 2>&1
print_status $? "Frontend production Docker build"

echo ""
echo "5. Testing Docker Compose..."

# Test docker-compose validation
docker-compose config > /dev/null 2>&1
print_status $? "Docker Compose development config validation"

docker-compose -f docker-compose.prod.yml config > /dev/null 2>&1
print_status $? "Docker Compose production config validation"

echo ""
echo "6. Checking backend health endpoint..."

# Start backend container temporarily
docker run -d --name test-backend -p 8001:8000 chatbot-backend-test > /dev/null 2>&1
sleep 10

# Test health endpoint
curl -f http://localhost:8001/health > /dev/null 2>&1
health_status=$?

# Cleanup
docker stop test-backend > /dev/null 2>&1
docker rm test-backend > /dev/null 2>&1

print_status $health_status "Backend health endpoint"

echo ""
echo "7. Cleaning up test images..."

docker rmi chatbot-backend-test chatbot-frontend-test chatbot-backend-prod-test chatbot-frontend-prod-test > /dev/null 2>&1

echo ""
echo "🎉 DEPLOYMENT TEST COMPLETE!"
echo "============================="
echo ""
echo "✅ All tests passed! Your application is ready for Docker Hub deployment."
echo ""
echo "Next steps:"
echo "1. Push to Docker Hub: docker-compose build && docker-compose push"
echo "2. Deploy: docker-compose up -d"
echo "3. Access: http://localhost:5173 (frontend) and http://localhost:8000 (backend)"
echo ""
echo "For production deployment:"
echo "1. Configure SSL certificates"
echo "2. Update environment variables"
echo "3. Use: docker-compose -f docker-compose.prod.yml up -d"
