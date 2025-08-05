# Setup Guide - Modern Chatbot System

## Prerequisites

### System Requirements
- **Node.js** (v18 or higher) - for frontend
- **Python** (v3.9 or higher) - for backend
- **Git** - for version control

### Optional Services
- **Supabase** account - for database and RAG functionality
- **OpenAI API** key - for AI responses
- **Anthropic API** key - alternative AI provider
- **Redis** - for caching (optional)

## Quick Setup

### 1. Clone and Navigate
```bash
git clone <your-repo-url>
cd modern-chatbot-system
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# At minimum, set SECRET_KEY to a secure random string
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env if needed (defaults should work for local development)
```

### 4. Start the Application

#### Option A: Use Startup Scripts
**Windows:**
```bash
# From project root
start.bat
```

**Linux/Mac:**
```bash
# From project root
chmod +x start.sh
./start.sh
```

#### Option B: Manual Start
**Terminal 1 (Backend):**
```bash
cd backend
python start.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

## Access Points

- **Chat Interface**: http://localhost:5173/chat
- **Admin Panel**: http://localhost:5173/admin
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Configuration

### Environment Variables

#### Backend (.env)
```env
# Required
SECRET_KEY=your-secure-secret-key-here
DEBUG=true
ENVIRONMENT=development

# Optional - for AI functionality
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Optional - for database functionality
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key
```

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_DEBUG=true
```

### Admin Panel Setup

1. Navigate to http://localhost:5173/admin/login
2. Default credentials:
   - Username: `admin`
   - Password: `admin123`
3. Configure your settings:
   - **API Keys**: Add OpenAI/Anthropic keys
   - **Supabase**: Configure database connection
   - **Design**: Customize chat interface appearance
   - **RAG**: Set up retrieval instructions

## Features Overview

### Chat Interface
- Embeddable iframe widget
- Real-time messaging
- Responsive design
- Customizable appearance

### Admin Panel
- API key management
- Database configuration
- Design customization
- Analytics dashboard
- RAG system configuration

### Backend API
- RESTful endpoints
- Authentication system
- Rate limiting
- Comprehensive logging
- Health checks

## Troubleshooting

### Common Issues

1. **Port already in use**
   - Backend (8000): `lsof -ti:8000 | xargs kill -9`
   - Frontend (5173): `lsof -ti:5173 | xargs kill -9`

2. **Dependencies not installing**
   - Backend: Ensure Python 3.9+ and pip are updated
   - Frontend: Ensure Node.js 18+ and npm are updated

3. **Environment variables not loading**
   - Ensure `.env` files are in correct directories
   - Check file permissions
   - Restart the services after changes

4. **CORS errors**
   - Check `ALLOWED_ORIGINS` in backend `.env`
   - Ensure frontend URL is included

### Development Tips

- Use `npm run dev` for frontend hot reloading
- Use `python start.py` for backend auto-reload
- Check browser console for frontend errors
- Check terminal output for backend errors
- API documentation available at `/docs` endpoint

## Production Deployment

For production deployment, see the deployment guides:
- Frontend: Build with `npm run build`
- Backend: Use production WSGI server
- Environment: Set `ENVIRONMENT=production`
- Security: Update all default passwords and keys

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the API documentation at `/docs`
3. Check the browser console and terminal logs
4. Ensure all environment variables are properly set
