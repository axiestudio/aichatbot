#!/bin/bash

# 🚀 Railway Deployment Script for AI Chatbot Platform
# This script helps deploy the application to Railway

set -e

echo "🚀 AI Chatbot Platform - Railway Deployment"
echo "==========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Railway CLI is installed
check_railway_cli() {
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI is not installed!"
        echo "Please install it from: https://docs.railway.app/develop/cli"
        echo "Or run: npm install -g @railway/cli"
        exit 1
    fi
    print_success "Railway CLI is installed"
}

# Check if user is logged in to Railway
check_railway_auth() {
    if ! railway whoami &> /dev/null; then
        print_error "Not logged in to Railway!"
        echo "Please run: railway login"
        exit 1
    fi
    print_success "Logged in to Railway"
}

# Create new Railway project
create_project() {
    print_status "Creating new Railway project..."
    railway login
    railway init
    print_success "Railway project created"
}

# Deploy services
deploy_services() {
    print_status "Deploying services to Railway..."
    
    # Deploy backend
    print_status "Deploying backend service..."
    cd backend
    railway up
    cd ..
    print_success "Backend deployed"
    
    # Deploy frontend
    print_status "Deploying frontend service..."
    cd frontend
    railway up
    cd ..
    print_success "Frontend deployed"
}

# Set environment variables
set_env_vars() {
    print_status "Setting up environment variables..."
    print_warning "Please set the following environment variables in Railway dashboard:"
    echo ""
    echo "Backend Service:"
    echo "- SECRET_KEY=your-super-secret-key-minimum-32-characters-long"
    echo "- DATABASE_URL=\${{Postgres.DATABASE_URL}}"
    echo "- REDIS_URL=\${{Redis.REDIS_URL}}"
    echo "- ADMIN_USERNAME=admin"
    echo "- ADMIN_PASSWORD=your-secure-password"
    echo ""
    echo "Frontend Service:"
    echo "- VITE_API_URL=https://your-backend-domain.railway.app"
    echo "- VITE_WS_URL=wss://your-backend-domain.railway.app"
    echo ""
    echo "See railway-env-template.txt for complete list"
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    print_warning "After deployment, run this command in Railway backend service terminal:"
    echo "alembic upgrade head"
}

# Main deployment flow
main() {
    echo "Starting Railway deployment process..."
    echo ""
    
    # Pre-deployment checks
    check_railway_cli
    check_railway_auth
    
    # Deployment steps
    echo "Choose deployment option:"
    echo "1) Create new project and deploy"
    echo "2) Deploy to existing project"
    echo "3) Just show environment variables"
    read -p "Enter choice (1-3): " choice
    
    case $choice in
        1)
            create_project
            deploy_services
            set_env_vars
            run_migrations
            ;;
        2)
            deploy_services
            set_env_vars
            run_migrations
            ;;
        3)
            set_env_vars
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
    
    echo ""
    print_success "Deployment process completed!"
    echo ""
    echo "Next steps:"
    echo "1. Set environment variables in Railway dashboard"
    echo "2. Add PostgreSQL and Redis services"
    echo "3. Run database migrations"
    echo "4. Test your application"
    echo ""
    echo "For detailed instructions, see RAILWAY_DEPLOYMENT.md"
}

# Run main function
main "$@"
