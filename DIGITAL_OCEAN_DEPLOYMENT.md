# 🌊 Digital Ocean App Platform Deployment Guide

## 🚀 Quick Deploy

[![Deploy to DO](https://www.deploytodo.com/do-btn-blue.svg)](https://cloud.digitalocean.com/apps/new?repo=https://github.com/axiestudio/aichatbot/tree/main)

## 📋 Prerequisites

1. **Digital Ocean Account** with billing enabled
2. **GitHub Repository** connected to DO
3. **Domain** (optional, DO provides free subdomain)

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (React SPA)   │◄──►│   (FastAPI)     │◄──►│  (PostgreSQL)   │
│   Static Site   │    │   API Service   │    │   Managed DB    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Redis       │
                    │   (Caching)     │
                    └─────────────────┘
```

## 🔧 Step-by-Step Deployment

### 1. **Create New App**
1. Go to [Digital Ocean Apps](https://cloud.digitalocean.com/apps)
2. Click **"Create App"**
3. Choose **"GitHub"** as source
4. Select repository: `axiestudio/aichatbot`
5. Choose branch: `main`

### 2. **Configure Services**

#### **Backend Service:**
- **Name:** `backend`
- **Source Directory:** `/backend`
- **Build Command:** `pip install -r requirements.txt`
- **Run Command:** `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Instance Size:** Basic ($5/month)
- **Health Check:** `/api/v1/health`

#### **Frontend Service:**
- **Name:** `frontend`  
- **Source Directory:** `/frontend`
- **Build Command:** `npm ci && npm run build`
- **Output Directory:** `dist`
- **Type:** Static Site
- **Instance Size:** Basic ($3/month)

### 3. **Add Database**
1. Click **"Add Database"**
2. Choose **PostgreSQL 15**
3. Size: **Basic ($15/month)**
4. Name: `chatbot-db`

### 4. **Add Redis**
1. Click **"Add Service"**
2. Choose **"Docker Hub"**
3. Image: `redis:7-alpine`
4. Name: `redis`
5. Internal port: `6379`

### 5. **Environment Variables**

#### **Global Variables:**
```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

#### **Backend Variables:**
```bash
# Security
SECRET_KEY=your-super-secret-key-change-in-production-minimum-32-characters
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production-minimum-32-characters

# Admin Credentials
ADMIN_USERNAME=stefan@axiestudio.se
ADMIN_PASSWORD=STEfanjohn!12

# Database (Auto-configured by DO)
DATABASE_URL=${chatbot-db.DATABASE_URL}

# Redis (Auto-configured by DO)
REDIS_URL=redis://redis:6379/0

# CORS & Security
CORS_ORIGINS=https://your-app-name.ondigitalocean.app
ALLOWED_HOSTS=your-app-name.ondigitalocean.app
```

#### **Frontend Variables:**
```bash
NODE_ENV=production
VITE_API_URL=${backend.PUBLIC_URL}
VITE_WS_URL=${backend.PUBLIC_URL}
```

### 6. **Deploy**
1. Review configuration
2. Click **"Create Resources"**
3. Wait for deployment (5-10 minutes)

## 🔗 Access Your Application

After deployment:
- **Frontend:** `https://your-app-name.ondigitalocean.app`
- **Backend API:** `https://your-app-name.ondigitalocean.app/api/v1`
- **Admin Panel:** `https://your-app-name.ondigitalocean.app/admin`
- **API Docs:** `https://your-app-name.ondigitalocean.app/docs`

## 🔐 Admin Access

- **Username:** `stefan@axiestudio.se`
- **Password:** `STEfanjohn!12`

## 💰 Cost Breakdown

| Service | Size | Monthly Cost |
|---------|------|--------------|
| Backend | Basic | $5.00 |
| Frontend | Basic | $3.00 |
| PostgreSQL | Basic | $15.00 |
| Redis | Basic | $5.00 |
| **Total** | | **$28.00/month** |

## 🔧 Configuration Files

The deployment uses these key files:
- `.do/app.yaml` - Main app configuration
- `backend/Dockerfile.do` - Backend container
- `frontend/Dockerfile.do` - Frontend container
- Environment variables for configuration

## 🚨 Troubleshooting

### **Build Failures:**
1. Check build logs in DO dashboard
2. Verify `package.json` and `requirements.txt`
3. Check environment variables

### **Database Connection:**
1. Verify `DATABASE_URL` is set
2. Check database is running
3. Review connection logs

### **Frontend Not Loading:**
1. Check build output directory (`dist`)
2. Verify static site configuration
3. Check CORS settings

## 🔄 Auto-Deployment

Digital Ocean automatically deploys when you push to the `main` branch:
1. Push changes to GitHub
2. DO detects changes
3. Automatic build and deploy
4. Zero-downtime deployment

## 📊 Monitoring

Digital Ocean provides:
- **Real-time metrics** (CPU, Memory, Network)
- **Application logs** (Build, Runtime, Error)
- **Alerts** (Email/Slack notifications)
- **Health checks** (Automatic restart on failure)

## 🔒 Security Features

- **Automatic HTTPS** with Let's Encrypt
- **DDoS protection** included
- **Private networking** between services
- **Managed database** with automatic backups
- **Container isolation** for security

## 🎯 Next Steps

1. **Custom Domain:** Add your own domain
2. **CDN:** Enable for faster global access
3. **Scaling:** Increase instances for high traffic
4. **Monitoring:** Set up alerts and monitoring
5. **Backups:** Configure database backup schedule
