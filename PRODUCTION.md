# Production Deployment Guide

## Prerequisites

- Docker & Docker Compose
- Domain name with SSL certificate
- Reverse proxy (nginx recommended)
- Environment variables configured

## Environment Configuration

### Backend Production Environment
```env
# backend/.env.production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Security
SECRET_KEY=your-super-secure-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-admin-password

# Database
DATABASE_URL=postgresql://user:password@db:5432/chatbot_prod

# AI APIs
OPENAI_API_KEY=your-production-openai-key
ANTHROPIC_API_KEY=your-production-anthropic-key

# Supabase
SUPABASE_URL=your-production-supabase-url
SUPABASE_ANON_KEY=your-production-anon-key
SUPABASE_SERVICE_KEY=your-production-service-key

# CORS
ALLOWED_ORIGINS=["https://yourdomain.com"]
ALLOWED_HOSTS=["yourdomain.com", "api.yourdomain.com"]

# Redis
REDIS_URL=redis://redis:6379

# Rate Limiting
RATE_LIMIT_PER_MINUTE=30
```

### Frontend Production Environment
```env
# frontend/.env.production
VITE_API_URL=https://api.yourdomain.com
VITE_DEBUG=false
VITE_ANALYTICS_ENABLED=true
```

## Docker Production Setup

### Production Docker Compose
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - ENVIRONMENT=production
    volumes:
      - ./backend/.env.production:/app/.env
    depends_on:
      - db
      - redis
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    volumes:
      - ./frontend/.env.production:/app/.env
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: chatbot_prod
      POSTGRES_USER: chatbot_user
      POSTGRES_PASSWORD: your-secure-db-password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

## Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:5173;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name yourdomain.com api.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # Frontend
    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    # Backend API
    server {
        listen 443 ssl http2;
        server_name api.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## Production Dockerfiles

### Backend Production Dockerfile
```dockerfile
# backend/Dockerfile.prod
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with gunicorn for production
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### Frontend Production Dockerfile
```dockerfile
# frontend/Dockerfile.prod
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Deployment Steps

1. **Prepare Environment**
   ```bash
   # Clone repository
   git clone <your-repo>
   cd modern-chatbot-system

   # Create production environment files
   cp backend/.env.example backend/.env.production
   cp frontend/.env.example frontend/.env.production

   # Edit environment files with production values
   ```

2. **SSL Certificates**
   ```bash
   # Create SSL directory
   mkdir ssl

   # Add your SSL certificates
   cp your-cert.pem ssl/cert.pem
   cp your-key.pem ssl/key.pem
   ```

3. **Deploy with Docker**
   ```bash
   # Build and start services
   docker-compose -f docker-compose.prod.yml up -d --build

   # Initialize database
   docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
   ```

4. **Verify Deployment**
   ```bash
   # Check service status
   docker-compose -f docker-compose.prod.yml ps

   # View logs
   docker-compose -f docker-compose.prod.yml logs -f

   # Test endpoints
   curl https://api.yourdomain.com/health
   curl https://yourdomain.com
   ```

## Monitoring & Maintenance

### Log Management
```bash
# View application logs
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend

# Rotate logs
docker system prune -f
```

### Database Backup
```bash
# Backup database
docker-compose -f docker-compose.prod.yml exec db pg_dump -U chatbot_user chatbot_prod > backup.sql

# Restore database
docker-compose -f docker-compose.prod.yml exec -T db psql -U chatbot_user chatbot_prod < backup.sql
```

### Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# Apply database migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

## Security Checklist

- [ ] Strong passwords for all services
- [ ] SSL certificates properly configured
- [ ] Firewall rules configured
- [ ] Database access restricted
- [ ] API rate limiting enabled
- [ ] Regular security updates
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting setup

## Performance Optimization

- [ ] Enable gzip compression in nginx
- [ ] Configure caching headers
- [ ] Use CDN for static assets
- [ ] Database query optimization
- [ ] Redis caching implementation
- [ ] Load balancing for high traffic
