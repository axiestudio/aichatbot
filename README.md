# 🚀 AI CHATBOT PLATFORM - PRODUCTION READY

**Enterprise-grade AI chatbot platform optimized for Digital Ocean App Platform deployment.**

## ⚡ **PRODUCTION DEPLOYMENT STATUS: READY**

**SINGLE DEPLOYMENT METHOD:** Digital Ocean App Platform
**ALL REDUNDANCIES ELIMINATED:** Clean, optimized architecture
**PRODUCTION OPTIMIZED:** Performance, security, scalability

[![Deploy on Digital Ocean](https://www.deploytodo.com/do-btn-blue.svg)](https://cloud.digitalocean.com/apps/new?repo=https://github.com/axiestudio/aichatbot)

## ✨ Features

- 🚀 **Real-time Messaging** - WebSocket-powered instant communication
- 📁 **Secure File Upload** - Virus scanning and validation
- 🔍 **Advanced Search** - Full-text search with analytics
- 💬 **Rich Chat Features** - Reactions, replies, typing indicators
- 🛡️ **Enterprise Security** - Multi-layer protection
- 📊 **Comprehensive Monitoring** - Real-time metrics and error tracking
- 🎨 **Modern UI** - Responsive React interface
- 🐳 **Docker Ready** - Complete containerization
- ☁️ **Cloud Native** - Railway deployment ready

## 🚀 Quick Deploy

### Railway (Recommended)
1. Click the "Deploy on Railway" button above
2. Connect your GitHub account
3. Add PostgreSQL and Redis services
4. Set environment variables from `railway-env-template.txt`
5. Deploy and enjoy!

### Local Development
```bash
# Clone repository
git clone https://github.com/axiestudio/aichatbot.git
cd aichatbot

# Backend setup
cd backend
pip install -r requirements-docker.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

## 🏗️ Architecture

### Frontend (React + TypeScript + Vite)
- **Chat Interface**: Embeddable chat widget that can be used as an iframe
- **Admin Panel**: Comprehensive configuration interface at `/admin`
  - Chat interface design customization
  - API key management
  - Supabase integration settings
  - RAG system instructions configuration

### Backend (Python + FastAPI)
- **RAG System**: Retrieval-Augmented Generation using Supabase data
- **API Endpoints**: RESTful API for chat interactions and admin operations
- **Supabase Integration**: Data storage and retrieval from configured tables

## Project Structure

```
├── frontend/          # React + TypeScript frontend
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Chat interface and admin panel
│   │   ├── hooks/         # Custom React hooks
│   │   ├── types/         # TypeScript type definitions
│   │   └── utils/         # Utility functions
│   └── public/
├── backend/           # Python FastAPI backend
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Core configuration
│   │   ├── models/        # Data models
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utility functions
│   └── requirements.txt
└── README.md
```

## Features

### Chat Interface
- Modern, responsive design
- Real-time messaging
- Iframe-embeddable
- Customizable appearance via admin panel

### Admin Panel
- **Design Configuration**: Colors, fonts, layout customization
- **API Management**: Configure OpenAI/other LLM API keys
- **Supabase Setup**: Database connection and table configuration
- **RAG Instructions**: Custom prompts and behavior settings
- **Analytics**: Chat usage and performance metrics

### RAG System
- Retrieves relevant information from Supabase tables
- Configurable search and ranking algorithms
- Custom instruction templates
- Context-aware response generation

## Quick Start

### Option 1: Automated Setup
```bash
# Windows
install.bat
start.bat

# Linux/Mac
chmod +x install.sh start.sh
./install.sh
./start.sh
```

### Option 2: Manual Setup
```bash
# Frontend
cd frontend
npm install
npm run dev

# Backend (new terminal)
cd backend
pip install -r requirements.txt
python start.py
```

### Option 3: Docker
```bash
docker-compose up --build
```

## Environment Variables

Create `.env` files in both frontend and backend directories:

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

### Backend (.env)
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_key
SECRET_KEY=your_secret_key
```

## Usage

1. **Setup**: Configure Supabase connection and API keys in admin panel
2. **Customize**: Design your chat interface appearance
3. **Configure RAG**: Set up data sources and instructions
4. **Embed**: Use the chat interface as an iframe in your website
5. **Monitor**: Track usage and performance through admin dashboard

## Development

- Frontend runs on `http://localhost:5173`
- Backend runs on `http://localhost:8000`
- Admin panel accessible at `http://localhost:5173/admin`
- Chat interface embeddable from `http://localhost:5173/chat`
