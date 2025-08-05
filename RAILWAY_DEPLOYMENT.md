# 🚀 Railway Deployment Guide

## Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template-id)

## Manual Deployment Steps

### 1. Prerequisites
- Railway account: https://railway.app
- GitHub repository pushed with latest code

### 2. Database Setup
1. Create a new Railway project
2. Add PostgreSQL service:
   - Click "Add Service" → "Database" → "PostgreSQL"
   - Note the connection details

3. Add Redis service:
   - Click "Add Service" → "Database" → "Redis"
   - Note the connection details

### 3. Backend Deployment
1. Add a new service:
   - Click "Add Service" → "GitHub Repo"
   - Select your repository
   - Set root directory to `backend`

2. Configure environment variables (copy from `railway-env-template.txt`):
   ```
   SECRET_KEY=your-super-secret-key-minimum-32-characters-long
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   REDIS_URL=${{Redis.REDIS_URL}}
   ENVIRONMENT=production
   DEBUG=false
   LOG_LEVEL=INFO
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=your-secure-admin-password
   ALLOWED_ORIGINS=["https://your-frontend-domain.railway.app"]
   ALLOWED_HOSTS=["your-backend-domain.railway.app"]
   ```

3. Set custom start command (if needed):
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

4. Deploy and wait for build to complete

5. Run database migrations:
   - Go to your backend service
   - Open "Deployments" tab
   - Click on latest deployment
   - Open terminal and run:
   ```bash
   alembic upgrade head
   ```

### 4. Frontend Deployment
1. Add another service:
   - Click "Add Service" → "GitHub Repo"
   - Select your repository
   - Set root directory to `frontend`

2. Configure environment variables:
   ```
   VITE_API_URL=https://your-backend-domain.railway.app
   VITE_WS_URL=wss://your-backend-domain.railway.app
   VITE_ENVIRONMENT=production
   ```

3. Deploy and wait for build to complete

### 5. Custom Domains (Optional)
1. Go to each service settings
2. Click "Networking" → "Custom Domain"
3. Add your custom domain
4. Update CORS settings in backend with new domain

### 6. Verification
1. Visit your frontend URL
2. Test chat functionality
3. Check file upload works
4. Verify WebSocket connection
5. Test admin panel access

## Environment Variables Reference

### Backend Required Variables
- `SECRET_KEY` - Minimum 32 characters
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `ADMIN_USERNAME` - Admin login username
- `ADMIN_PASSWORD` - Admin login password

### Frontend Required Variables
- `VITE_API_URL` - Backend service URL
- `VITE_WS_URL` - WebSocket URL (same as API but with wss://)

### Optional Variables
- AI API keys for enhanced functionality
- Custom CORS origins
- File upload limits
- Feature flags

## Troubleshooting

### Common Issues

1. **Build Fails**
   - Check logs in Railway dashboard
   - Ensure all dependencies are in requirements.txt
   - Verify Python version compatibility

2. **Database Connection Error**
   - Verify DATABASE_URL is correctly set
   - Check if migrations ran successfully
   - Ensure PostgreSQL service is running

3. **CORS Errors**
   - Update ALLOWED_ORIGINS with correct frontend URL
   - Ensure both HTTP and HTTPS are included if needed

4. **WebSocket Connection Fails**
   - Verify VITE_WS_URL uses wss:// for HTTPS sites
   - Check if WebSocket endpoint is accessible

5. **File Upload Issues**
   - Ensure upload directory permissions
   - Check file size limits
   - Verify CORS for file upload endpoints

### Logs and Monitoring
- View logs in Railway dashboard
- Monitor resource usage
- Set up alerts for errors

## Production Checklist
- [ ] Database migrations completed
- [ ] Environment variables configured
- [ ] CORS settings updated
- [ ] Admin credentials changed
- [ ] Custom domains configured (optional)
- [ ] SSL certificates active
- [ ] Monitoring and alerts set up
- [ ] Backup strategy implemented

## Support
For issues with this deployment:
1. Check Railway documentation
2. Review application logs
3. Verify environment variables
4. Test locally first

## Security Notes
- Change default admin credentials
- Use strong SECRET_KEY
- Enable HTTPS only in production
- Regularly update dependencies
- Monitor for security vulnerabilities
