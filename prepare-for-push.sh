#!/bin/bash

# 🚀 Prepare AI Chatbot Platform for Git Push
# This script prepares the codebase for pushing to GitHub

set -e

echo "🚀 AI Chatbot Platform - Git Preparation"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create .gitignore if it doesn't exist
create_gitignore() {
    if [ ! -f .gitignore ]; then
        print_status "Creating .gitignore file..."
        cat > .gitignore << 'EOF'
# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids/
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
.nyc_output/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Build outputs
dist/
build/
*.tgz
*.tar.gz

# Database
*.db
*.sqlite
*.sqlite3

# Uploads and temporary files
uploads/
quarantine/
temp/
tmp/

# Railway
.railway/

# Alembic
alembic/versions/*.py
!alembic/versions/001_initial_migration.py
!alembic/versions/002_enhanced_features.py

# Docker
.dockerignore

# Testing
.coverage
.pytest_cache/
test-results.xml

# Production secrets
*.pem
*.key
*.crt
EOF
        print_success ".gitignore created"
    else
        print_status ".gitignore already exists"
    fi
}

# Check for sensitive files
check_sensitive_files() {
    print_status "Checking for sensitive files..."
    
    sensitive_patterns=(
        "*.key"
        "*.pem"
        "*.crt"
        "*secret*"
        "*password*"
        "*.env"
    )
    
    found_sensitive=false
    for pattern in "${sensitive_patterns[@]}"; do
        if find . -name "$pattern" -not -path "./node_modules/*" -not -path "./.git/*" | grep -q .; then
            print_warning "Found potentially sensitive files matching: $pattern"
            find . -name "$pattern" -not -path "./node_modules/*" -not -path "./.git/*"
            found_sensitive=true
        fi
    done
    
    if [ "$found_sensitive" = true ]; then
        print_warning "Please review sensitive files before pushing!"
        echo "Make sure they are in .gitignore or remove sensitive data"
    else
        print_success "No obvious sensitive files found"
    fi
}

# Validate environment files
validate_env_files() {
    print_status "Validating environment files..."
    
    # Check backend .env
    if [ -f "backend/.env" ]; then
        if grep -q "your-.*-key" "backend/.env"; then
            print_warning "Backend .env contains placeholder values"
            print_warning "Make sure to update these in production!"
        fi
    fi
    
    # Check frontend .env files
    for env_file in frontend/.env*; do
        if [ -f "$env_file" ]; then
            if grep -q "your-.*-domain" "$env_file"; then
                print_warning "$env_file contains placeholder domains"
                print_warning "Update these with actual Railway URLs after deployment"
            fi
        fi
    done
}

# Check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check backend requirements
    if [ -f "backend/requirements-docker.txt" ]; then
        print_success "Backend requirements file found"
    else
        print_error "Backend requirements file missing!"
        exit 1
    fi
    
    # Check frontend package.json
    if [ -f "frontend/package.json" ]; then
        print_success "Frontend package.json found"
    else
        print_error "Frontend package.json missing!"
        exit 1
    fi
}

# Create README if missing
create_readme() {
    if [ ! -f README.md ]; then
        print_status "Creating README.md..."
        cat > README.md << 'EOF'
# 🤖 Enterprise AI Chatbot Platform

A production-ready, enterprise-grade AI chatbot platform with advanced features including real-time messaging, file uploads, search functionality, and comprehensive monitoring.

## ✨ Features

- 🚀 **Real-time Messaging** - WebSocket-powered instant communication
- 📁 **Secure File Upload** - Virus scanning and validation
- 🔍 **Advanced Search** - Full-text search with analytics
- 💬 **Rich Chat Features** - Reactions, replies, typing indicators
- 🛡️ **Enterprise Security** - Multi-layer protection
- 📊 **Comprehensive Monitoring** - Real-time metrics and error tracking
- 🎨 **Modern UI** - Responsive React interface
- 🐳 **Docker Ready** - Complete containerization
- ☁️ **Cloud Native** - Railway deployment ready

## 🚀 Quick Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template-id)

## 📖 Documentation

- [Railway Deployment Guide](RAILWAY_DEPLOYMENT.md)
- [API Documentation](http://localhost:8000/docs) (when running)
- [Environment Variables](railway-env-template.txt)

## 🛠️ Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL
- Redis

### Setup
```bash
# Clone repository
git clone https://github.com/axiestudio/aichatbot.git
cd aichatbot

# Backend setup
cd backend
pip install -r requirements-docker.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

## 🏗️ Architecture

- **Backend**: FastAPI + Python
- **Frontend**: React + TypeScript + Vite
- **Database**: PostgreSQL
- **Cache**: Redis
- **WebSocket**: Real-time messaging
- **Deployment**: Railway + Docker

## 🔧 Configuration

See `railway-env-template.txt` for all environment variables.

## 📊 Monitoring

- Health checks: `/health`
- Metrics: `/metrics`
- API docs: `/docs`
- Admin panel: `/admin`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For deployment issues, check the Railway deployment guide or create an issue.
EOF
        print_success "README.md created"
    else
        print_status "README.md already exists"
    fi
}

# Main preparation flow
main() {
    echo "Preparing codebase for Git push..."
    echo ""
    
    create_gitignore
    check_sensitive_files
    validate_env_files
    check_dependencies
    create_readme
    
    echo ""
    print_success "Preparation completed!"
    echo ""
    echo "Next steps:"
    echo "1. Review any warnings above"
    echo "2. Test the application locally"
    echo "3. Commit and push to GitHub:"
    echo "   git add ."
    echo "   git commit -m 'feat: production-ready AI chatbot platform'"
    echo "   git push origin main"
    echo "4. Deploy to Railway using the deployment guide"
    echo ""
    echo "For Railway deployment, see RAILWAY_DEPLOYMENT.md"
}

# Run main function
main "$@"
