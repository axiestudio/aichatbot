# 🚀 **RAILWAY DEPLOYMENT GUIDE**

## **QUICK DEPLOYMENT (5 MINUTES)**

### **Step 1: Install Railway CLI**
```bash
npm install -g @railway/cli
```

### **Step 2: Login to Railway**
```bash
railway login
```

### **Step 3: Deploy with One Command**
```bash
./deploy-railway.sh
```

---

## **MANUAL DEPLOYMENT STEPS**

### **1. Create Railway Project**
```bash
railway init
```

### **2. Add Services**
```bash
railway add postgresql
railway add redis
```

### **3. Set Environment Variables**
```bash
# Core Settings
railway variables set ENVIRONMENT=production
railway variables set SECRET_KEY=railway-super-secret-key-2024
railway variables set JWT_SECRET_KEY=railway-jwt-secret-key-2024

# Admin Credentials
railway variables set ADMIN_USERNAME=stefan@axiestudio.se
railway variables set ADMIN_PASSWORD=STEfanjohn!12
railway variables set ADMIN_EMAIL=stefan@axiestudio.se

# AI API Keys (Replace with your actual keys)
railway variables set OPENAI_API_KEY=your-openai-api-key
railway variables set ANTHROPIC_API_KEY=your-anthropic-api-key

# Performance Settings
railway variables set ENABLE_METRICS=true
railway variables set PERFORMANCE_MONITORING_ENABLED=true
railway variables set RATE_LIMIT_ENABLED=true
railway variables set SECURITY_HEADERS_ENABLED=true

# Advanced Features
railway variables set AI_SCALING_ENABLED=true
railway variables set SECURITY_INTELLIGENCE_ENABLED=true
railway variables set ADVANCED_ANALYTICS_ENABLED=true
railway variables set CONVERSATION_INTELLIGENCE_ENABLED=true
railway variables set CONTENT_MODERATION_ENABLED=true
railway variables set KNOWLEDGE_GRAPH_ENABLED=true
railway variables set REALTIME_COLLABORATION_ENABLED=true

# Production Settings
railway variables set WORKERS=4
railway variables set MAX_CONNECTIONS=1000
railway variables set PORT=8000
railway variables set HOST=0.0.0.0
```

### **4. Deploy**
```bash
railway up
```

---

## **ENVIRONMENT VARIABLES REFERENCE**

### **Required Variables**
| Variable | Value | Description |
|----------|-------|-------------|
| `ENVIRONMENT` | `production` | Deployment environment |
| `SECRET_KEY` | `railway-super-secret-key-2024` | Application secret |
| `JWT_SECRET_KEY` | `railway-jwt-secret-key-2024` | JWT signing key |
| `ADMIN_USERNAME` | `stefan@axiestudio.se` | Super admin username |
| `ADMIN_PASSWORD` | `STEfanjohn!12` | Super admin password |
| `ADMIN_EMAIL` | `stefan@axiestudio.se` | Super admin email |

### **AI API Keys (Required for AI Features)**
| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `ANTHROPIC_API_KEY` | Your Anthropic API key |

### **Optional Performance Variables**
| Variable | Default | Description |
|----------|---------|-------------|
| `WORKERS` | `4` | Number of worker processes |
| `MAX_CONNECTIONS` | `1000` | Maximum database connections |
| `ENABLE_METRICS` | `true` | Enable performance metrics |
| `RATE_LIMIT_ENABLED` | `true` | Enable rate limiting |

---

## **POST-DEPLOYMENT CHECKLIST**

### **1. Verify Deployment**
```bash
railway logs
railway status
```

### **2. Get Your URL**
```bash
railway domain
```

### **3. Test Admin Access**
- Navigate to: `https://your-app.railway.app/admin`
- Login with: `stefan@axiestudio.se` / `STEfanjohn!12`

### **4. Configure Custom Domain (Optional)**
```bash
railway domain add yourdomain.com
```

### **5. Monitor Application**
```bash
railway logs --follow
```

---

## **TROUBLESHOOTING**

### **Common Issues**

**1. Build Fails**
```bash
# Check logs
railway logs

# Redeploy
railway up --detach
```

**2. Database Connection Issues**
```bash
# Check database status
railway status

# Restart services
railway restart
```

**3. Environment Variables Not Set**
```bash
# List all variables
railway variables

# Set missing variables
railway variables set VARIABLE_NAME=value
```

### **Health Check Endpoints**
- Health: `https://your-app.railway.app/health`
- Metrics: `https://your-app.railway.app/metrics`
- Admin: `https://your-app.railway.app/admin`

---

## **PRODUCTION FEATURES ENABLED**

✅ **AI-Powered Chat Interface**
✅ **Advanced Analytics Dashboard**
✅ **Real-time Performance Monitoring**
✅ **Security Intelligence**
✅ **Content Moderation**
✅ **Knowledge Graph**
✅ **Auto-scaling**
✅ **Multi-tenant Architecture**
✅ **WebSocket Support**
✅ **Rate Limiting**
✅ **Health Checks**
✅ **Error Tracking**

---

## **SUPPORT**

### **Railway Documentation**
- [Railway Docs](https://docs.railway.app/)
- [Railway CLI](https://docs.railway.app/develop/cli)
- [Environment Variables](https://docs.railway.app/develop/variables)

### **Application Logs**
```bash
# View recent logs
railway logs

# Follow logs in real-time
railway logs --follow

# Filter logs by service
railway logs --service backend
```

---

**🎉 Your world-class AI platform is now live on Railway!**
