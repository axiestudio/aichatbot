# Production Deployment Guide

This guide covers the complete production deployment of the Modern Chatbot System with RAG capabilities.

## 🏗️ Architecture Overview

The production system consists of:

- **Frontend**: React application with TypeScript
- **Backend**: FastAPI with Python 3.11
- **Database**: PostgreSQL 15 with connection pooling
- **Cache**: Redis 7 for sessions and caching
- **Vector Store**: Supabase for RAG embeddings
- **Load Balancer**: Nginx with SSL termination
- **Monitoring**: Prometheus + Grafana + AlertManager
- **Logging**: ELK Stack (Elasticsearch + Kibana + Filebeat)
- **Container Orchestration**: Kubernetes with Helm charts

## 📋 Prerequisites

### Infrastructure Requirements

- **Kubernetes Cluster**: v1.25+ with at least 3 nodes
- **Node Specifications**: 
  - CPU: 4 cores minimum per node
  - Memory: 8GB minimum per node
  - Storage: 100GB SSD per node
- **Load Balancer**: External load balancer with SSL termination
- **DNS**: Domain name with SSL certificate
- **Container Registry**: Docker registry for images

### Required Tools

```bash
# Install required tools
kubectl version --client  # v1.25+
helm version              # v3.10+
docker version           # v20.10+
jq --version             # v1.6+
curl --version           # v7.68+
```

### Cloud Provider Setup

#### AWS
```bash
# Install AWS CLI and configure
aws configure
eksctl create cluster --name chatbot-prod --region us-east-1 --nodes 3 --node-type m5.large
```

#### Google Cloud
```bash
# Install gcloud and configure
gcloud auth login
gcloud container clusters create chatbot-prod --num-nodes=3 --machine-type=e2-standard-4
```

#### Azure
```bash
# Install Azure CLI and configure
az login
az aks create --resource-group chatbot-rg --name chatbot-prod --node-count 3 --node-vm-size Standard_D4s_v3
```

## 🔧 Configuration

### 1. Environment Variables

Copy and configure the production environment:

```bash
cp .env.production.example .env.production
```

**Critical variables to set:**

```bash
# Security (MUST CHANGE)
SECRET_KEY="your-super-secret-key-min-32-chars"
JWT_SECRET_KEY="your-jwt-secret-key-min-32-chars"
POSTGRES_PASSWORD="your-secure-db-password"
REDIS_PASSWORD="your-secure-redis-password"

# AI Services
OPENAI_API_KEY="sk-your-openai-key"
ANTHROPIC_API_KEY="your-anthropic-key"

# Domain
CORS_ORIGINS="https://chatbot.yourdomain.com"
ALLOWED_HOSTS="chatbot.yourdomain.com"

# Monitoring
SENTRY_DSN="https://your-sentry-dsn@sentry.io/project"
GRAFANA_PASSWORD="your-grafana-password"
```

### 2. Kubernetes Secrets

Create secrets from environment variables:

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets
kubectl create secret generic chatbot-secrets \
  --from-literal=SECRET_KEY="$SECRET_KEY" \
  --from-literal=JWT_SECRET_KEY="$JWT_SECRET_KEY" \
  --from-literal=POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
  --from-literal=REDIS_PASSWORD="$REDIS_PASSWORD" \
  --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
  --from-literal=ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  --from-literal=SUPABASE_ANON_KEY="$SUPABASE_ANON_KEY" \
  --from-literal=GRAFANA_PASSWORD="$GRAFANA_PASSWORD" \
  --from-literal=SENTRY_DSN="$SENTRY_DSN" \
  -n chatbot-system
```

### 3. SSL Certificates

#### Option A: Let's Encrypt (Recommended)
```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@yourdomain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

#### Option B: Custom Certificates
```bash
# Create TLS secret with your certificates
kubectl create secret tls chatbot-tls \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key \
  -n chatbot-system
```

## 🚀 Deployment

### Automated Deployment (Recommended)

Use the provided deployment script:

```bash
# Set environment variables
export ENVIRONMENT=production
export POSTGRES_PASSWORD="your-secure-password"
export REDIS_PASSWORD="your-redis-password"
export SECRET_KEY="your-secret-key"
export JWT_SECRET_KEY="your-jwt-secret"
export OPENAI_API_KEY="your-openai-key"

# Run deployment
./scripts/deploy.sh

# For dry run first
./scripts/deploy.sh --dry-run
```

### Manual Deployment

1. **Deploy Infrastructure**:
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
```

2. **Wait for Infrastructure**:
```bash
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=postgres -n chatbot-system --timeout=300s
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redis -n chatbot-system --timeout=300s
```

3. **Deploy Applications**:
```bash
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/nginx.yaml
```

4. **Deploy Monitoring**:
```bash
kubectl apply -f k8s/monitoring/
```

5. **Verify Deployment**:
```bash
kubectl get pods -n chatbot-system
kubectl get services -n chatbot-system
kubectl get ingress -n chatbot-system
```

## 📊 Monitoring and Observability

### Access Monitoring Dashboards

- **Grafana**: https://grafana.yourdomain.com (admin/your-grafana-password)
- **Prometheus**: https://prometheus.yourdomain.com
- **Kibana**: https://kibana.yourdomain.com
- **Application**: https://chatbot.yourdomain.com

### Key Metrics to Monitor

1. **Application Metrics**:
   - Response time (95th percentile < 2s)
   - Error rate (< 1%)
   - Request rate
   - Active sessions

2. **Infrastructure Metrics**:
   - CPU usage (< 80%)
   - Memory usage (< 85%)
   - Disk usage (< 90%)
   - Network I/O

3. **Database Metrics**:
   - Connection count
   - Query performance
   - Replication lag
   - Lock waits

### Alerting Rules

Critical alerts are configured for:
- Service downtime
- High error rates
- Resource exhaustion
- Security events
- Certificate expiration

## 🔒 Security

### Security Checklist

- [ ] All secrets are stored in Kubernetes secrets
- [ ] Network policies are enabled
- [ ] RBAC is configured
- [ ] SSL/TLS is enforced
- [ ] Security headers are enabled
- [ ] Rate limiting is configured
- [ ] Input validation is implemented
- [ ] Audit logging is enabled

### Security Scanning

```bash
# Run security scans
docker run --rm -v $(pwd):/app aquasec/trivy fs /app
docker run --rm -v $(pwd):/app securecodewarrior/semgrep --config=auto /app
```

## 🔄 CI/CD Pipeline

The GitHub Actions workflow automatically:

1. **On Pull Request**:
   - Runs security scans
   - Executes tests
   - Builds images
   - Performs code quality checks

2. **On Merge to Main**:
   - Builds and pushes production images
   - Deploys to staging environment
   - Runs smoke tests

3. **On Release**:
   - Deploys to production
   - Runs comprehensive health checks
   - Sends notifications

### Manual Triggers

```bash
# Trigger deployment manually
gh workflow run "CI/CD Pipeline" --ref main

# Deploy specific version
gh workflow run "CI/CD Pipeline" --ref v1.2.3
```

## 🔧 Maintenance

### Database Maintenance

```bash
# Create backup
kubectl exec -n chatbot-system deployment/postgres -- pg_dump -U chatbot_user chatbot > backup.sql

# Restore backup
kubectl exec -i -n chatbot-system deployment/postgres -- psql -U chatbot_user chatbot < backup.sql

# Run maintenance
kubectl exec -n chatbot-system deployment/postgres -- psql -U chatbot_user -d chatbot -c "VACUUM ANALYZE;"
```

### Log Management

```bash
# View application logs
kubectl logs -f deployment/chatbot-backend -n chatbot-system

# View aggregated logs in Kibana
# Navigate to https://kibana.yourdomain.com
```

### Scaling

```bash
# Manual scaling
kubectl scale deployment chatbot-backend --replicas=5 -n chatbot-system

# Enable autoscaling
kubectl apply -f k8s/hpa.yaml
```

## 🚨 Troubleshooting

### Common Issues

1. **Pod Startup Issues**:
```bash
kubectl describe pod <pod-name> -n chatbot-system
kubectl logs <pod-name> -n chatbot-system --previous
```

2. **Database Connection Issues**:
```bash
kubectl exec -it deployment/postgres -n chatbot-system -- psql -U chatbot_user -d chatbot
```

3. **SSL Certificate Issues**:
```bash
kubectl describe certificate chatbot-tls -n chatbot-system
kubectl describe certificaterequest -n chatbot-system
```

4. **Performance Issues**:
```bash
# Check resource usage
kubectl top pods -n chatbot-system
kubectl top nodes

# Check HPA status
kubectl get hpa -n chatbot-system
```

### Emergency Procedures

1. **Rollback Deployment**:
```bash
kubectl rollout undo deployment/chatbot-backend -n chatbot-system
kubectl rollout undo deployment/chatbot-frontend -n chatbot-system
```

2. **Scale Down for Maintenance**:
```bash
kubectl scale deployment chatbot-backend --replicas=0 -n chatbot-system
```

3. **Emergency Database Backup**:
```bash
kubectl exec deployment/postgres -n chatbot-system -- pg_dump -U chatbot_user chatbot | gzip > emergency-backup-$(date +%Y%m%d-%H%M%S).sql.gz
```

## 📞 Support

For production support:
- **Monitoring**: Check Grafana dashboards first
- **Logs**: Use Kibana for log analysis
- **Alerts**: AlertManager sends notifications to configured channels
- **Documentation**: Refer to runbooks in the monitoring/runbooks/ directory

## 🔄 Updates and Upgrades

### Application Updates
1. Update version in CI/CD pipeline
2. Run automated tests
3. Deploy to staging
4. Validate functionality
5. Deploy to production
6. Monitor metrics

### Infrastructure Updates
1. Plan maintenance window
2. Create backups
3. Update components one by one
4. Validate each component
5. Update monitoring and alerting

Remember to always test changes in a staging environment before applying to production!
