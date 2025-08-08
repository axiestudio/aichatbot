#!/bin/bash

# Digital Ocean App Platform Deployment Script
# This script helps deploy the AI Chatbot Platform to Digital Ocean

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if doctl is installed
check_doctl() {
    if ! command -v doctl &> /dev/null; then
        log_error "doctl CLI is not installed. Please install it first:"
        echo "  curl -sL https://github.com/digitalocean/doctl/releases/download/v1.94.0/doctl-1.94.0-linux-amd64.tar.gz | tar -xzv"
        echo "  sudo mv doctl /usr/local/bin"
        exit 1
    fi
    log_success "doctl CLI found"
}

# Check authentication
check_auth() {
    if ! doctl auth list &> /dev/null; then
        log_error "Not authenticated with Digital Ocean. Please run:"
        echo "  doctl auth init"
        exit 1
    fi
    log_success "Digital Ocean authentication verified"
}

# Validate app.yaml
validate_config() {
    if [ ! -f ".do/app.yaml" ]; then
        log_error "app.yaml not found in .do/ directory"
        exit 1
    fi
    log_success "app.yaml configuration found"
}

# Create or update app
deploy_app() {
    log_info "Deploying to Digital Ocean App Platform..."
    
    # Check if app already exists
    APP_NAME="aichatbot-platform"
    
    if doctl apps list | grep -q "$APP_NAME"; then
        log_info "App '$APP_NAME' exists, updating..."
        APP_ID=$(doctl apps list --format ID,Name --no-header | grep "$APP_NAME" | awk '{print $1}')
        doctl apps update "$APP_ID" --spec .do/app.yaml
    else
        log_info "Creating new app '$APP_NAME'..."
        doctl apps create --spec .do/app.yaml
    fi
    
    log_success "Deployment initiated successfully!"
}

# Monitor deployment
monitor_deployment() {
    log_info "Monitoring deployment status..."
    APP_ID=$(doctl apps list --format ID,Name --no-header | grep "aichatbot-platform" | awk '{print $1}')
    
    if [ -z "$APP_ID" ]; then
        log_error "Could not find app ID"
        exit 1
    fi
    
    log_info "App ID: $APP_ID"
    log_info "You can monitor the deployment at:"
    echo "  https://cloud.digitalocean.com/apps/$APP_ID"
    
    # Wait for deployment to complete
    log_info "Waiting for deployment to complete..."
    while true; do
        STATUS=$(doctl apps get "$APP_ID" --format Phase --no-header)
        case $STATUS in
            "ACTIVE")
                log_success "Deployment completed successfully!"
                break
                ;;
            "ERROR"|"FAILED")
                log_error "Deployment failed!"
                exit 1
                ;;
            *)
                log_info "Deployment status: $STATUS"
                sleep 30
                ;;
        esac
    done
}

# Get app URLs
get_urls() {
    APP_ID=$(doctl apps list --format ID,Name --no-header | grep "aichatbot-platform" | awk '{print $1}')
    
    log_success "🎉 Deployment completed!"
    echo ""
    echo "📱 Your application is now live:"
    
    # Get app info
    doctl apps get "$APP_ID" --format Name,DefaultIngress,LiveURL --no-header | while read -r name ingress url; do
        echo "  🌐 App URL: $url"
    done
    
    echo ""
    echo "🔗 Quick Links:"
    echo "  📊 Dashboard: https://cloud.digitalocean.com/apps/$APP_ID"
    echo "  📋 API Docs: $url/docs"
    echo "  🔐 Admin Panel: $url/admin"
    echo ""
    echo "🔑 Admin Credentials:"
    echo "  Username: stefan@axiestudio.se"
    echo "  Password: STEfanjohn!12"
    echo ""
    echo "💡 Next Steps:"
    echo "  1. Test the application"
    echo "  2. Configure custom domain (optional)"
    echo "  3. Set up monitoring and alerts"
    echo "  4. Review and update environment variables"
}

# Main deployment function
main() {
    echo "🌊 Digital Ocean App Platform Deployment"
    echo "========================================"
    echo ""
    
    log_info "Starting deployment process..."
    
    # Run checks
    check_doctl
    check_auth
    validate_config
    
    # Deploy
    deploy_app
    monitor_deployment
    get_urls
    
    log_success "🚀 Deployment completed successfully!"
}

# Help function
show_help() {
    echo "Digital Ocean App Platform Deployment Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  deploy    Deploy the application (default)"
    echo "  status    Check deployment status"
    echo "  logs      Show application logs"
    echo "  destroy   Delete the application"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy    # Deploy the application"
    echo "  $0 status    # Check status"
    echo "  $0 logs      # View logs"
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "status")
        APP_ID=$(doctl apps list --format ID,Name --no-header | grep "aichatbot-platform" | awk '{print $1}')
        doctl apps get "$APP_ID"
        ;;
    "logs")
        APP_ID=$(doctl apps list --format ID,Name --no-header | grep "aichatbot-platform" | awk '{print $1}')
        doctl apps logs "$APP_ID" --follow
        ;;
    "destroy")
        log_warning "This will delete the entire application!"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            APP_ID=$(doctl apps list --format ID,Name --no-header | grep "aichatbot-platform" | awk '{print $1}')
            doctl apps delete "$APP_ID" --force
            log_success "Application deleted"
        fi
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
