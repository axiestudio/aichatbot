# 🐳 AI CHATBOT PLATFORM - DOCKER DEPLOYMENT GUIDE

## 🚀 **AUTOMATED DOCKER HUB DEPLOYMENT**

### **Docker Hub Repository:** `axiestudio/aichatbot`
### **GitHub Actions:** Automated build and push on every commit to main

---

## 📋 **QUICK START**

### **1. Pull and Run (Simplest)**
```bash
docker run -p 8000:8000 axiestudio/aichatbot:latest
```

### **2. With Environment Variables**
```bash
docker run -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e DATABASE_URL=your_database_url \
  -e ADMIN_USERNAME=your_admin \
  -e ADMIN_PASSWORD=your_password \
  axiestudio/aichatbot:latest
```

### **3. Using Docker Compose (Recommended)**
```bash
docker-compose up -d
```

---

## 🔧 **DEPLOYMENT OPTIONS**

### **Option 1: Docker Hub Image (Recommended)**
```bash
# Pull latest image
docker pull axiestudio/aichatbot:latest

# Run with basic configuration
docker run -d \
  --name aichatbot \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  axiestudio/aichatbot:latest
```

### **Option 2: Docker Compose Stack**
```bash
# Clone repository
git clone https://github.com/axiestudio/aichatbot.git
cd aichatbot

# Start full stack
docker-compose up -d

# With nginx proxy
docker-compose --profile production up -d
```

### **Option 3: Build from Source**
```bash
# Clone and build
git clone https://github.com/axiestudio/aichatbot.git
cd aichatbot
docker build -t aichatbot-local .

# Run local build
docker run -p 8000:8000 aichatbot-local
```

---

## ⚙️ **ENVIRONMENT VARIABLES**

### **Required Variables:**
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
ADMIN_USERNAME=your_admin_email
ADMIN_PASSWORD=your_secure_password
```

### **Optional Variables:**
```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
API_V1_STR=/api/v1
ACCESS_TOKEN_EXPIRE_MINUTES=30
MAX_FILE_SIZE=10485760
RATE_LIMIT_REQUESTS=100
CORS_ORIGINS=*
```

---

## 🔄 **AUTOMATED DEPLOYMENT PIPELINE**

### **GitHub Actions Workflow:**
- **Trigger:** Push to main branch
- **Build:** Multi-platform (amd64, arm64)
- **Test:** Automated testing and linting
- **Push:** Automatic push to Docker Hub
- **Security:** Vulnerability scanning with Trivy

### **Image Tags:**
- `latest` - Latest stable release
- `main` - Latest main branch build
- `sha-<commit>` - Specific commit builds

---

## 🏥 **HEALTH CHECKS**

### **Built-in Health Check:**
```bash
# Check container health
docker ps

# Manual health check
curl http://localhost:8000/api/v1/health
```

### **Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-08-08T14:00:00Z",
  "version": "1.0.0",
  "environment": "production"
}
```

---

## 📊 **MONITORING & LOGS**

### **View Logs:**
```bash
# Container logs
docker logs aichatbot

# Follow logs
docker logs -f aichatbot

# Docker Compose logs
docker-compose logs -f chatbot-backend
```

### **Container Stats:**
```bash
# Resource usage
docker stats aichatbot

# Container info
docker inspect aichatbot
```

---

## 🔒 **SECURITY FEATURES**

### **Container Security:**
- ✅ Non-root user execution
- ✅ Minimal base image (Python slim)
- ✅ Multi-stage build
- ✅ Vulnerability scanning
- ✅ Read-only filesystem where possible

### **Application Security:**
- ✅ Environment variable configuration
- ✅ JWT authentication
- ✅ Rate limiting
- ✅ CORS protection
- ✅ Input validation

---

## 🚀 **PRODUCTION DEPLOYMENT**

### **Cloud Platforms:**

#### **Digital Ocean:**
```bash
# Deploy to Digital Ocean App Platform
# Use Docker Hub image: axiestudio/aichatbot:latest
```

#### **AWS ECS:**
```bash
# Task definition with image: axiestudio/aichatbot:latest
```

#### **Google Cloud Run:**
```bash
gcloud run deploy aichatbot \
  --image=axiestudio/aichatbot:latest \
  --platform=managed \
  --port=8000
```

#### **Azure Container Instances:**
```bash
az container create \
  --resource-group myResourceGroup \
  --name aichatbot \
  --image axiestudio/aichatbot:latest \
  --ports 8000
```

---

## 🛠️ **TROUBLESHOOTING**

### **Common Issues:**

#### **Container Won't Start:**
```bash
# Check logs
docker logs aichatbot

# Check environment variables
docker inspect aichatbot | grep -A 20 "Env"
```

#### **Database Connection Issues:**
```bash
# Test database connectivity
docker exec -it aichatbot python -c "
from app.core.database import get_db
print('Database connection test...')
"
```

#### **Port Already in Use:**
```bash
# Use different port
docker run -p 8001:8000 axiestudio/aichatbot:latest
```

---

## 📈 **SCALING**

### **Horizontal Scaling:**
```bash
# Multiple containers with load balancer
docker-compose up --scale chatbot-backend=3
```

### **Resource Limits:**
```bash
docker run \
  --memory=1g \
  --cpus=1.0 \
  -p 8000:8000 \
  axiestudio/aichatbot:latest
```

---

## 🔄 **UPDATES**

### **Update to Latest:**
```bash
# Pull latest image
docker pull axiestudio/aichatbot:latest

# Restart container
docker-compose down
docker-compose up -d
```

### **Rollback:**
```bash
# Use specific tag
docker run -p 8000:8000 axiestudio/aichatbot:sha-<previous-commit>
```

**This Docker deployment provides a production-ready, scalable solution for the AI Chatbot Platform!** 🚀
