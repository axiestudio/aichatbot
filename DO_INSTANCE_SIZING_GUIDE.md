# 🌊 Digital Ocean App Platform - Instance Sizing Guide

## 📊 **Available Instance Sizes**

### **Basic Tier (Shared CPU)**
| Size | RAM | vCPU | Price/month | Best For |
|------|-----|------|-------------|----------|
| `basic-xxs` | 512MB | 0.5 | $5 | Static sites, simple APIs |
| `basic-xs` | 1GB | 1 | $10 | Small apps, development |
| `basic-s` | 2GB | 1 | $20 | Medium apps, production |

### **Professional Tier (Dedicated CPU)**
| Size | RAM | vCPU | Price/month | Best For |
|------|-----|------|-------------|----------|
| `professional-xs` | 1GB | 1 | $12 | Production APIs |
| `professional-s` | 2GB | 1 | $24 | High-traffic apps |
| `professional-m` | 4GB | 2 | $48 | Enterprise apps |
| `professional-l` | 8GB | 4 | $96 | Heavy workloads |

## 🎯 **Recommended Configuration for AI Chatbot**

### **Option 1: Budget Setup (~$17/month)**
```yaml
services:
  - name: backend
    instance_size_slug: basic-xs      # 1GB RAM, 1 vCPU - $10/month
    http_port: 8000
    
  - name: frontend  
    instance_size_slug: basic-xxs     # 512MB RAM - $5/month
    
databases:
  - name: chatbot-db
    size: basic-xs                     # $15/month
```
**Total: ~$30/month**

### **Option 2: Production Setup (~$41/month)**
```yaml
services:
  - name: backend
    instance_size_slug: professional-xs  # 1GB RAM, 1 vCPU - $12/month
    http_port: 8000
    
  - name: frontend
    instance_size_slug: basic-xxs        # 512MB RAM - $5/month
    
databases:
  - name: chatbot-db
    size: professional-xs                 # $25/month
```
**Total: ~$42/month**

### **Option 3: High-Performance Setup (~$69/month)**
```yaml
services:
  - name: backend
    instance_size_slug: professional-s   # 2GB RAM, 1 vCPU - $24/month
    http_port: 8000
    
  - name: frontend
    instance_size_slug: basic-xxs        # 512MB RAM - $5/month
    
databases:
  - name: chatbot-db
    size: professional-s                  # $40/month
```
**Total: ~$69/month**

## 🔌 **Port Configuration**

### **Backend Service:**
- **Default Port:** `8000` (FastAPI/Uvicorn)
- **Environment Variable:** `$PORT` (auto-set by DO)
- **Health Check:** `/api/v1/health`

### **Frontend Service:**
- **Static Site:** No port needed (served by DO CDN)
- **Build Output:** `dist/` directory

### **Database:**
- **PostgreSQL:** Port `5432` (internal)
- **Connection:** Via `$DATABASE_URL` environment variable

## 🚀 **Performance Recommendations**

### **For Development/Testing:**
- **Backend:** `basic-xs` (1GB RAM) - $10/month
- **Frontend:** `basic-xxs` (512MB) - $5/month
- **Database:** `basic-xs` - $15/month
- **Total:** $30/month

### **For Production (Recommended):**
- **Backend:** `professional-xs` (1GB RAM, dedicated CPU) - $12/month
- **Frontend:** `basic-xxs` (512MB) - $5/month  
- **Database:** `professional-xs` - $25/month
- **Total:** $42/month

### **For High Traffic:**
- **Backend:** `professional-s` (2GB RAM) - $24/month
- **Frontend:** `basic-xxs` (512MB) - $5/month
- **Database:** `professional-s` - $40/month
- **Total:** $69/month

## 📈 **Scaling Strategy**

### **Start Small:**
1. Begin with `basic-xs` for backend
2. Monitor performance and resource usage
3. Scale up when needed

### **Scale Indicators:**
- **CPU > 80%** consistently → Upgrade to professional tier
- **Memory > 80%** → Increase RAM size
- **Response time > 2s** → Scale up or add instances

### **Auto-Scaling:**
```yaml
services:
  - name: backend
    instance_count: 1
    autoscaling:
      min_instance_count: 1
      max_instance_count: 3
      metrics:
        cpu_threshold_percent: 80
```

## 🔧 **Configuration Examples**

### **Budget Configuration (.do/app.yaml):**
```yaml
services:
  - name: backend
    instance_size_slug: basic-xs
    instance_count: 1
    http_port: 8000
    
  - name: frontend
    instance_size_slug: basic-xxs
    
databases:
  - name: chatbot-db
    engine: PG
    size: basic-xs
```

### **Production Configuration (.do/app.yaml):**
```yaml
services:
  - name: backend
    instance_size_slug: professional-xs
    instance_count: 1
    http_port: 8000
    autoscaling:
      min_instance_count: 1
      max_instance_count: 2
    
  - name: frontend
    instance_size_slug: basic-xxs
    
databases:
  - name: chatbot-db
    engine: PG
    size: professional-xs
```

## 💡 **Pro Tips**

1. **Start with `professional-xs`** for backend (dedicated CPU)
2. **Frontend can stay `basic-xxs`** (static files don't need much)
3. **Database size should match backend** for optimal performance
4. **Monitor metrics** in DO dashboard
5. **Scale gradually** - don't over-provision initially
6. **Use autoscaling** for traffic spikes

## 🎯 **Final Recommendation**

For your AI Chatbot Platform, I recommend:

```yaml
services:
  - name: backend
    instance_size_slug: professional-xs  # 1GB RAM, 1 vCPU dedicated
    http_port: 8000
    
  - name: frontend
    instance_size_slug: basic-xxs        # 512MB RAM shared
    
databases:
  - name: chatbot-db
    size: professional-xs                 # 1GB RAM, dedicated
```

**Total Cost:** ~$42/month
**Performance:** Production-ready with room to grow
**Scaling:** Easy to upgrade when needed
