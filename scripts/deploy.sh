#!/bin/bash

# Production Deployment Script for Chatbot System
# This script handles the complete deployment process with safety checks

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
NAMESPACE="chatbot-system"
ENVIRONMENT="${ENVIRONMENT:-production}"
DRY_RUN="${DRY_RUN:-false}"
SKIP_TESTS="${SKIP_TESTS:-false}"
BACKUP_BEFORE_DEPLOY="${BACKUP_BEFORE_DEPLOY:-true}"

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

# Error handling
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log_error "Deployment failed with exit code $exit_code"
        log_info "Rolling back changes..."
        rollback_deployment
    fi
    exit $exit_code
}

trap cleanup EXIT

# Utility functions
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check required tools
    local required_tools=("kubectl" "docker" "helm" "jq" "curl")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "$tool is required but not installed"
            exit 1
        fi
    done
    
    # Check kubectl context
    local current_context=$(kubectl config current-context)
    log_info "Current kubectl context: $current_context"
    
    if [[ "$ENVIRONMENT" == "production" && "$current_context" != *"prod"* ]]; then
        log_warning "You're deploying to production but kubectl context doesn't seem to be production"
        read -p "Are you sure you want to continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

validate_environment() {
    log_info "Validating environment configuration..."
    
    # Check required environment variables
    local required_vars=(
        "POSTGRES_PASSWORD"
        "REDIS_PASSWORD"
        "SECRET_KEY"
        "JWT_SECRET_KEY"
        "OPENAI_API_KEY"
    )
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            log_error "Required environment variable $var is not set"
            exit 1
        fi
    done
    
    # Validate secret lengths
    if [[ ${#SECRET_KEY} -lt 32 ]]; then
        log_error "SECRET_KEY must be at least 32 characters long"
        exit 1
    fi
    
    if [[ ${#JWT_SECRET_KEY} -lt 32 ]]; then
        log_error "JWT_SECRET_KEY must be at least 32 characters long"
        exit 1
    fi
    
    log_success "Environment validation passed"
}

run_tests() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        log_warning "Skipping tests as requested"
        return
    fi
    
    log_info "Running pre-deployment tests..."
    
    # Backend tests
    log_info "Running backend tests..."
    cd "$PROJECT_ROOT/backend"
    if ! python -m pytest tests/ -v --tb=short; then
        log_error "Backend tests failed"
        exit 1
    fi
    
    # Frontend tests
    log_info "Running frontend tests..."
    cd "$PROJECT_ROOT/frontend"
    if ! npm test -- --watchAll=false; then
        log_error "Frontend tests failed"
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
    log_success "All tests passed"
}

backup_database() {
    if [[ "$BACKUP_BEFORE_DEPLOY" != "true" ]]; then
        log_info "Skipping database backup"
        return
    fi
    
    log_info "Creating database backup..."
    
    local backup_name="chatbot-backup-$(date +%Y%m%d-%H%M%S)"
    local backup_file="/tmp/${backup_name}.sql"
    
    # Create backup using kubectl exec
    kubectl exec -n "$NAMESPACE" deployment/postgres -- pg_dump \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        --no-password \
        > "$backup_file"
    
    # Upload backup to cloud storage (implement based on your cloud provider)
    # aws s3 cp "$backup_file" "s3://your-backup-bucket/database-backups/"
    # gsutil cp "$backup_file" "gs://your-backup-bucket/database-backups/"
    
    log_success "Database backup created: $backup_file"
    export BACKUP_FILE="$backup_file"
}

build_and_push_images() {
    log_info "Building and pushing Docker images..."
    
    local git_sha=$(git rev-parse --short HEAD)
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local image_tag="${ENVIRONMENT}-${git_sha}-${timestamp}"
    
    # Build backend image
    log_info "Building backend image..."
    docker build -t "your-registry/chatbot-backend:${image_tag}" \
        -t "your-registry/chatbot-backend:latest" \
        --target production \
        "$PROJECT_ROOT/backend"
    
    # Build frontend image
    log_info "Building frontend image..."
    docker build -t "your-registry/chatbot-frontend:${image_tag}" \
        -t "your-registry/chatbot-frontend:latest" \
        --target production \
        "$PROJECT_ROOT/frontend"
    
    # Push images
    if [[ "$DRY_RUN" != "true" ]]; then
        log_info "Pushing images to registry..."
        docker push "your-registry/chatbot-backend:${image_tag}"
        docker push "your-registry/chatbot-backend:latest"
        docker push "your-registry/chatbot-frontend:${image_tag}"
        docker push "your-registry/chatbot-frontend:latest"
    fi
    
    export BACKEND_IMAGE="your-registry/chatbot-backend:${image_tag}"
    export FRONTEND_IMAGE="your-registry/chatbot-frontend:${image_tag}"
    
    log_success "Images built and pushed successfully"
}

create_namespace() {
    log_info "Creating namespace if it doesn't exist..."
    
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "DRY RUN: Would create namespace $NAMESPACE"
        else
            kubectl apply -f "$PROJECT_ROOT/k8s/namespace.yaml"
            log_success "Namespace $NAMESPACE created"
        fi
    else
        log_info "Namespace $NAMESPACE already exists"
    fi
}

deploy_secrets() {
    log_info "Deploying secrets..."
    
    # Create secrets from environment variables
    local secrets_file="/tmp/secrets.yaml"
    
    cat > "$secrets_file" << EOF
apiVersion: v1
kind: Secret
metadata:
  name: chatbot-secrets
  namespace: $NAMESPACE
type: Opaque
data:
  SECRET_KEY: $(echo -n "$SECRET_KEY" | base64 -w 0)
  JWT_SECRET_KEY: $(echo -n "$JWT_SECRET_KEY" | base64 -w 0)
  POSTGRES_PASSWORD: $(echo -n "$POSTGRES_PASSWORD" | base64 -w 0)
  REDIS_PASSWORD: $(echo -n "$REDIS_PASSWORD" | base64 -w 0)
  OPENAI_API_KEY: $(echo -n "$OPENAI_API_KEY" | base64 -w 0)
  ANTHROPIC_API_KEY: $(echo -n "${ANTHROPIC_API_KEY:-}" | base64 -w 0)
  SUPABASE_ANON_KEY: $(echo -n "${SUPABASE_ANON_KEY:-}" | base64 -w 0)
  GRAFANA_PASSWORD: $(echo -n "${GRAFANA_PASSWORD:-admin123}" | base64 -w 0)
  SENTRY_DSN: $(echo -n "${SENTRY_DSN:-}" | base64 -w 0)
EOF
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "DRY RUN: Would apply secrets"
    else
        kubectl apply -f "$secrets_file"
        rm -f "$secrets_file"
        log_success "Secrets deployed"
    fi
}

deploy_infrastructure() {
    log_info "Deploying infrastructure components..."
    
    local manifests=(
        "configmap.yaml"
        "postgres.yaml"
        "redis.yaml"
    )
    
    for manifest in "${manifests[@]}"; do
        log_info "Applying $manifest..."
        if [[ "$DRY_RUN" == "true" ]]; then
            kubectl apply -f "$PROJECT_ROOT/k8s/$manifest" --dry-run=client
        else
            kubectl apply -f "$PROJECT_ROOT/k8s/$manifest"
        fi
    done
    
    # Wait for infrastructure to be ready
    if [[ "$DRY_RUN" != "true" ]]; then
        log_info "Waiting for infrastructure to be ready..."
        kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=postgres -n "$NAMESPACE" --timeout=300s
        kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redis -n "$NAMESPACE" --timeout=300s
    fi
    
    log_success "Infrastructure deployed successfully"
}

deploy_applications() {
    log_info "Deploying application components..."
    
    # Update image tags in manifests
    local backend_manifest="/tmp/backend.yaml"
    local frontend_manifest="/tmp/frontend.yaml"
    
    sed "s|your-registry/chatbot-backend:latest|$BACKEND_IMAGE|g" \
        "$PROJECT_ROOT/k8s/backend.yaml" > "$backend_manifest"
    
    sed "s|your-registry/chatbot-frontend:latest|$FRONTEND_IMAGE|g" \
        "$PROJECT_ROOT/k8s/frontend.yaml" > "$frontend_manifest"
    
    local app_manifests=(
        "$backend_manifest"
        "$frontend_manifest"
        "nginx.yaml"
    )
    
    for manifest in "${app_manifests[@]}"; do
        log_info "Applying $(basename "$manifest")..."
        if [[ "$DRY_RUN" == "true" ]]; then
            kubectl apply -f "$manifest" --dry-run=client
        else
            kubectl apply -f "$manifest"
        fi
    done
    
    # Wait for applications to be ready
    if [[ "$DRY_RUN" != "true" ]]; then
        log_info "Waiting for applications to be ready..."
        kubectl rollout status deployment/chatbot-backend -n "$NAMESPACE" --timeout=600s
        kubectl rollout status deployment/chatbot-frontend -n "$NAMESPACE" --timeout=600s
        kubectl rollout status deployment/nginx -n "$NAMESPACE" --timeout=300s
    fi
    
    # Cleanup temporary files
    rm -f "$backend_manifest" "$frontend_manifest"
    
    log_success "Applications deployed successfully"
}

deploy_monitoring() {
    log_info "Deploying monitoring stack..."
    
    local monitoring_manifests=(
        "monitoring/prometheus.yaml"
        "monitoring/grafana.yaml"
        "monitoring/alertmanager.yaml"
    )
    
    for manifest in "${monitoring_manifests[@]}"; do
        if [[ -f "$PROJECT_ROOT/$manifest" ]]; then
            log_info "Applying $manifest..."
            if [[ "$DRY_RUN" == "true" ]]; then
                kubectl apply -f "$PROJECT_ROOT/$manifest" --dry-run=client
            else
                kubectl apply -f "$PROJECT_ROOT/$manifest"
            fi
        fi
    done
    
    log_success "Monitoring stack deployed"
}

run_health_checks() {
    log_info "Running health checks..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "DRY RUN: Skipping health checks"
        return
    fi
    
    # Wait for pods to be ready
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=chatbot-backend -n "$NAMESPACE" --timeout=300s
    
    # Test backend health endpoint
    local backend_pod=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=chatbot-backend -o jsonpath='{.items[0].metadata.name}')
    
    if kubectl exec -n "$NAMESPACE" "$backend_pod" -- curl -f http://localhost:8000/health; then
        log_success "Backend health check passed"
    else
        log_error "Backend health check failed"
        exit 1
    fi
    
    # Test database connectivity
    if kubectl exec -n "$NAMESPACE" "$backend_pod" -- python -c "
import asyncio
from app.core.database import db_manager
async def test():
    return await db_manager.check_connection()
result = asyncio.run(test())
exit(0 if result else 1)
"; then
        log_success "Database connectivity check passed"
    else
        log_error "Database connectivity check failed"
        exit 1
    fi
    
    log_success "All health checks passed"
}

rollback_deployment() {
    log_warning "Rolling back deployment..."
    
    # Get previous revision
    local backend_revision=$(kubectl rollout history deployment/chatbot-backend -n "$NAMESPACE" --revision=0 | tail -2 | head -1 | awk '{print $1}')
    local frontend_revision=$(kubectl rollout history deployment/chatbot-frontend -n "$NAMESPACE" --revision=0 | tail -2 | head -1 | awk '{print $1}')
    
    if [[ -n "$backend_revision" ]]; then
        kubectl rollout undo deployment/chatbot-backend -n "$NAMESPACE" --to-revision="$backend_revision"
    fi
    
    if [[ -n "$frontend_revision" ]]; then
        kubectl rollout undo deployment/chatbot-frontend -n "$NAMESPACE" --to-revision="$frontend_revision"
    fi
    
    log_warning "Rollback completed"
}

main() {
    log_info "Starting deployment to $ENVIRONMENT environment"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_warning "Running in DRY RUN mode - no changes will be applied"
    fi
    
    check_prerequisites
    validate_environment
    run_tests
    backup_database
    build_and_push_images
    create_namespace
    deploy_secrets
    deploy_infrastructure
    deploy_applications
    deploy_monitoring
    run_health_checks
    
    log_success "Deployment completed successfully!"
    log_info "Application should be available at: https://chatbot.yourdomain.com"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --no-backup)
            BACKUP_BEFORE_DEPLOY=false
            shift
            ;;
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --dry-run          Run without making changes"
            echo "  --skip-tests       Skip running tests"
            echo "  --no-backup        Skip database backup"
            echo "  --environment ENV  Set deployment environment (default: production)"
            echo "  --help             Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main function
main
