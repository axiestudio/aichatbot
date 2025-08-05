#!/bin/bash

# Production Deployment Script
# Enterprise-grade deployment with comprehensive checks and rollback capability

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="chatbot"
ENVIRONMENT="production"
BACKUP_DIR="/backups"
LOG_FILE="/var/log/chatbot-deploy.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root for security reasons"
    fi
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
    fi
    
    # Check environment file
    if [[ ! -f ".env.production" ]]; then
        error "Production environment file (.env.production) not found"
    fi
    
    # Check SSL certificates
    if [[ ! -f "nginx/ssl/chatbot.crt" ]] || [[ ! -f "nginx/ssl/chatbot.key" ]]; then
        warning "SSL certificates not found. HTTPS will not work."
    fi
    
    success "Prerequisites check passed"
}

# Backup current deployment
backup_current() {
    log "Creating backup of current deployment..."
    
    local backup_timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_path="${BACKUP_DIR}/${PROJECT_NAME}_${backup_timestamp}"
    
    mkdir -p "$backup_path"
    
    # Backup database
    if docker-compose -f docker-compose.production.yml ps postgres | grep -q "Up"; then
        log "Backing up database..."
        docker-compose -f docker-compose.production.yml exec -T postgres pg_dump -U chatbot_user chatbot > "${backup_path}/database.sql"
    fi
    
    # Backup volumes
    log "Backing up volumes..."
    docker run --rm -v chatbot_postgres_data:/data -v "${backup_path}:/backup" alpine tar czf /backup/postgres_data.tar.gz -C /data .
    docker run --rm -v chatbot_redis_data:/data -v "${backup_path}:/backup" alpine tar czf /backup/redis_data.tar.gz -C /data .
    docker run --rm -v chatbot_backend_uploads:/data -v "${backup_path}:/backup" alpine tar czf /backup/uploads.tar.gz -C /data .
    
    # Backup configuration
    cp -r . "${backup_path}/source"
    
    echo "$backup_path" > .last_backup
    success "Backup created at $backup_path"
}

# Run tests
run_tests() {
    log "Running tests..."
    
    # Frontend tests
    log "Running frontend tests..."
    cd frontend
    npm ci
    npm run test:ci || error "Frontend tests failed"
    cd ..
    
    # Backend tests
    log "Running backend tests..."
    cd backend
    python -m pytest tests/ -v --tb=short || error "Backend tests failed"
    cd ..
    
    success "All tests passed"
}

# Build images
build_images() {
    log "Building production images..."
    
    # Build with no cache for production
    docker-compose -f docker-compose.production.yml build --no-cache --parallel
    
    # Tag images with timestamp
    local timestamp=$(date +%Y%m%d_%H%M%S)
    docker tag chatbot_frontend:latest "chatbot_frontend:${timestamp}"
    docker tag chatbot_backend:latest "chatbot_backend:${timestamp}"
    
    success "Images built successfully"
}

# Health check function
health_check() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    log "Performing health check for $service..."
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s "$url" > /dev/null; then
            success "$service is healthy"
            return 0
        fi
        
        log "Health check attempt $attempt/$max_attempts failed, retrying in 10s..."
        sleep 10
        ((attempt++))
    done
    
    error "$service health check failed after $max_attempts attempts"
}

# Deploy services
deploy() {
    log "Starting production deployment..."
    
    # Stop existing services gracefully
    log "Stopping existing services..."
    docker-compose -f docker-compose.production.yml down --timeout 30
    
    # Start database and cache first
    log "Starting database and cache services..."
    docker-compose -f docker-compose.production.yml up -d postgres redis
    
    # Wait for database to be ready
    sleep 30
    health_check "Database" "http://localhost:5432"
    
    # Run database migrations
    log "Running database migrations..."
    docker-compose -f docker-compose.production.yml run --rm backend alembic upgrade head
    
    # Start backend services
    log "Starting backend services..."
    docker-compose -f docker-compose.production.yml up -d backend
    
    # Wait for backend to be ready
    sleep 20
    health_check "Backend" "http://localhost:8000/health"
    
    # Start frontend and nginx
    log "Starting frontend and nginx..."
    docker-compose -f docker-compose.production.yml up -d frontend nginx
    
    # Wait for frontend to be ready
    sleep 15
    health_check "Frontend" "http://localhost:80/health"
    
    # Start monitoring services
    log "Starting monitoring services..."
    docker-compose -f docker-compose.production.yml up -d prometheus grafana jaeger loki promtail
    
    success "Deployment completed successfully"
}

# Post-deployment verification
verify_deployment() {
    log "Verifying deployment..."
    
    # Check all services are running
    local services=("postgres" "redis" "backend" "frontend" "nginx" "prometheus" "grafana")
    
    for service in "${services[@]}"; do
        if ! docker-compose -f docker-compose.production.yml ps "$service" | grep -q "Up"; then
            error "Service $service is not running"
        fi
    done
    
    # Check API endpoints
    health_check "API Health" "http://localhost:8000/health"
    health_check "API Metrics" "http://localhost:8000/metrics"
    
    # Check frontend
    health_check "Frontend" "http://localhost:80"
    
    # Check monitoring
    health_check "Prometheus" "http://localhost:9090/-/healthy"
    health_check "Grafana" "http://localhost:3000/api/health"
    
    success "Deployment verification completed"
}

# Rollback function
rollback() {
    log "Rolling back to previous deployment..."
    
    if [[ ! -f ".last_backup" ]]; then
        error "No backup found for rollback"
    fi
    
    local backup_path=$(cat .last_backup)
    
    if [[ ! -d "$backup_path" ]]; then
        error "Backup directory not found: $backup_path"
    fi
    
    # Stop current services
    docker-compose -f docker-compose.production.yml down
    
    # Restore volumes
    log "Restoring volumes..."
    docker run --rm -v chatbot_postgres_data:/data -v "${backup_path}:/backup" alpine tar xzf /backup/postgres_data.tar.gz -C /data
    docker run --rm -v chatbot_redis_data:/data -v "${backup_path}:/backup" alpine tar xzf /backup/redis_data.tar.gz -C /data
    docker run --rm -v chatbot_backend_uploads:/data -v "${backup_path}:/backup" alpine tar xzf /backup/uploads.tar.gz -C /data
    
    # Restore database
    if [[ -f "${backup_path}/database.sql" ]]; then
        log "Restoring database..."
        docker-compose -f docker-compose.production.yml up -d postgres
        sleep 30
        docker-compose -f docker-compose.production.yml exec -T postgres psql -U chatbot_user -d chatbot < "${backup_path}/database.sql"
    fi
    
    # Start services
    docker-compose -f docker-compose.production.yml up -d
    
    success "Rollback completed"
}

# Cleanup old backups
cleanup_backups() {
    log "Cleaning up old backups..."
    find "$BACKUP_DIR" -name "${PROJECT_NAME}_*" -type d -mtime +7 -exec rm -rf {} \;
    success "Old backups cleaned up"
}

# Main deployment function
main() {
    log "Starting production deployment for $PROJECT_NAME"
    
    case "${1:-deploy}" in
        "deploy")
            check_root
            check_prerequisites
            backup_current
            run_tests
            build_images
            deploy
            verify_deployment
            cleanup_backups
            success "Production deployment completed successfully!"
            ;;
        "rollback")
            rollback
            ;;
        "health")
            verify_deployment
            ;;
        "backup")
            backup_current
            ;;
        *)
            echo "Usage: $0 {deploy|rollback|health|backup}"
            exit 1
            ;;
    esac
}

# Create necessary directories
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# Run main function
main "$@"
