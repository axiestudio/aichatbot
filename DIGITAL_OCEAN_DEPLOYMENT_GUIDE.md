# 🌊 Digital Ocean App Platform Deployment Guide

## 📋 Prerequisites

- ✅ Digital Ocean account
- ✅ GitHub repository: `https://github.com/axiestudio/aichatbot`
- ✅ Supabase project (or plan to use DO managed PostgreSQL)

## 🚀 Step-by-Step Deployment

### **Step 1: Create New App**

1. Go to [Digital Ocean App Platform](https://cloud.digitalocean.com/apps)
2. Click **"Create App"**
3. Choose **"GitHub"** as source
4. Connect your GitHub account
5. Select repository: `axiestudio/aichatbot`
6. Select branch: `main`
7. Enable **"Autodeploy"** for automatic updates

### **Step 2: Configure App Settings**

#### **App Info:**
- **App Name**: `aichatbot-platform` (or your preferred name)
- **Region**: Choose closest to your users
- **Plan**: **Basic ($5/month)** or **Professional ($12/month)**

#### **Service Configuration:**
- **Service Type**: Web Service
- **Source Directory**: `/backend`
- **Build Command**: `pip install -r requirements.txt`
- **Run Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **HTTP Port**: `8000`
- **Instance Size**: **Basic ($5/month)** or **Professional ($12/month)**

### **Step 3: Add Database Service (Optional)**

If you want to use Digital Ocean managed PostgreSQL instead of Supabase:

1. Click **"Add Resource"**
2. Select **"Database"**
3. Choose **"PostgreSQL"**
4. Select plan: **Basic ($15/month)** or higher
5. Name: `aichatbot-db`

### **Step 4: Configure Environment Variables**

Copy all variables from `DIGITAL_OCEAN_ENV.txt` and add them in the **Environment Variables** section:

#### **Required Variables (mark as SECRET):**
```bash
SECRET_KEY=your-super-secret-digital-ocean-key-2024-enterprise-minimum-32-chars
JWT_SECRET_KEY=your-jwt-secret-digital-ocean-key-2024-enterprise-minimum-32-chars
```

#### **Database Configuration:**
If using DO managed PostgreSQL:
```bash
DATABASE_URL=${aichatbot-db.DATABASE_URL}
```

If using Supabase (recommended):
```bash
DATABASE_URL=postgresql://postgres.ompjkiiabyuegytncbwq:STEfanjohn!12@aws-0-eu-north-1.pooler.supabase.com:6543/postgres
SUPABASE_URL=https://ompjkiiabyuegytncbwq.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9tcGpraWlhYnl1ZWd5dG5jYndxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI4NDg2MjYsImV4cCI6MjA2ODQyNDYyNn0.z9j2pwMfKjfR9Fs__fHkzwj9fjgiNOUQZ5Z9zv5FD6Q
```

#### **Update App-Specific Settings:**
```bash
CORS_ORIGINS=https://aichatbot-platform-xxxxx.ondigitalocean.app,https://yourdomain.com
ALLOWED_HOSTS=aichatbot-platform-xxxxx.ondigitalocean.app,localhost
```

### **Step 5: Deploy Application**

1. Click **"Create Resources"**
2. Wait for deployment (5-10 minutes)
3. Monitor build logs for any errors
4. Once deployed, note your app URL: `https://aichatbot-platform-xxxxx.ondigitalocean.app`

### **Step 6: Database Setup**

#### **If using Supabase:**
1. Go to [Supabase SQL Editor](https://supabase.com/dashboard/project/ompjkiiabyuegytncbwq/sql)
2. Run this SQL to create cache tables:

```sql
-- Platform cache entries table
CREATE TABLE IF NOT EXISTS cache_entries (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    cache_type VARCHAR(50) NOT NULL DEFAULT 'default',
    value JSONB NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cache_key ON cache_entries(cache_key);
CREATE INDEX IF NOT EXISTS idx_cache_type ON cache_entries(cache_type);
CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache_entries(expires_at);

-- Platform user sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255),
    session_data JSONB NOT NULL DEFAULT '{}',
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_session_id ON user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_session_expires ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_session_active ON user_sessions(is_active);
```

### **Step 7: Test Deployment**

1. **Health Check**: Visit `https://your-app.ondigitalocean.app/api/v1/health`
2. **Admin Panel**: Visit `https://your-app.ondigitalocean.app/api/v1/admin`
3. **API Docs**: Visit `https://your-app.ondigitalocean.app/docs`

#### **Expected Health Check Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-08-08T14:00:00Z",
  "version": "1.0.0",
  "environment": "production",
  "database": "connected",
  "cache": "available"
}
```

### **Step 8: Configure Admin Access**

1. Go to admin panel: `https://your-app.ondigitalocean.app/api/v1/admin`
2. Login with:
   - **Username**: `stefan@axiestudio.se`
   - **Password**: `STEfanjohn!12`
3. Configure your first client instance
4. Set up AI API keys for clients

## 🔧 Post-Deployment Configuration

### **Custom Domain (Optional):**
1. In DO App Platform, go to **Settings** → **Domains**
2. Add your custom domain
3. Update `CORS_ORIGINS` environment variable
4. Configure DNS records as instructed

### **Scaling:**
- **Horizontal**: Increase instance count in App settings
- **Vertical**: Upgrade to Professional plan for more resources

### **Monitoring:**
- Use DO App Platform built-in metrics
- Monitor `/api/v1/health` endpoint
- Set up alerts for downtime

## 🎯 Architecture Benefits

### **Digital Ocean Advantages:**
- ✅ **Managed Infrastructure** - No server management
- ✅ **Auto-scaling** - Handles traffic spikes
- ✅ **Built-in Monitoring** - Metrics and alerts
- ✅ **Easy Deployments** - Git-based deployments
- ✅ **Cost Effective** - Pay for what you use

### **Multi-Tenant Ready:**
- ✅ **Platform Database** - Your Supabase for infrastructure
- ✅ **Client Isolation** - Each client uses their own database
- ✅ **Scalable Architecture** - Add clients without infrastructure changes
- ✅ **Enterprise Grade** - Production-ready security and performance

## 💰 Estimated Costs

### **Basic Setup:**
- **App Platform Basic**: $5/month
- **Database (optional)**: $15/month (if not using Supabase)
- **Total**: $5-20/month

### **Professional Setup:**
- **App Platform Professional**: $12/month
- **Database Professional**: $25/month
- **Total**: $12-37/month

## 🆘 Troubleshooting

### **Common Issues:**

1. **Build Failures**: Check build logs for missing dependencies
2. **Database Connection**: Verify DATABASE_URL format
3. **CORS Errors**: Update CORS_ORIGINS with correct domain
4. **Environment Variables**: Ensure all required vars are set

### **Support:**
- Digital Ocean Documentation
- GitHub Issues: `https://github.com/axiestudio/aichatbot/issues`
- Community Support

This deployment guide ensures a production-ready multi-tenant AI chatbot platform on Digital Ocean! 🚀
