.PHONY: help install dev build test clean deploy-prod deploy-k8s backup restore logs health security-scan

# 🚀 Enterprise Chatbot Platform - Makefile
help: ## Show available commands
	@echo "🚀 Enterprise Chatbot Platform Commands:"
	@echo ""
	@echo "📦 Setup & Development:"
	@echo "  install      - Install all dependencies"
	@echo "  dev          - Start development environment"
	@echo "  test         - Run comprehensive test suite"
	@echo "  lint         - Run code linting"
	@echo "  format       - Format code"
	@echo ""
	@echo "🏗️  Build & Deploy:"
	@echo "  build        - Build production images"
	@echo "  deploy-prod  - Deploy to production (Docker Compose)"
	@echo "  deploy-k8s   - Deploy to Kubernetes"
	@echo ""
	@echo "🔧 Maintenance:"
	@echo "  backup       - Create database backup"
	@echo "  restore      - Restore database backup"
	@echo "  logs         - View application logs"
	@echo "  health       - Check system health"
	@echo "  clean        - Clean up resources"
	@echo "  security-scan - Run security vulnerability scan"

install: ## Install backend dependencies only
	@echo "📦 Installing production dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "✅ Backend dependencies installed!"

dev: ## Start backend development server
	@echo "🔧 Starting backend development server..."
	cd backend && python start.py
	@echo "✅ Backend server running on port 8000!"

test: ## Run comprehensive test suite
	@echo "🧪 Running comprehensive test suite..."
	cd backend && python -m pytest tests/ -v --cov=app
	cd frontend && npm run test
	@echo "✅ All tests completed!"

lint: ## Run code linting
	@echo "🔍 Running linting..."
	cd frontend && npm run lint
	cd backend && flake8 app/
	@echo "✅ Linting complete!"

format: ## Format code
	@echo "🎨 Formatting code..."
	cd frontend && npm run format
	cd backend && black app/ && isort app/
	@echo "✅ Code formatted!"

build: ## Build production images
	@echo "🏗️ Building production images..."
	docker-compose -f docker-compose.production.yml build
	@echo "✅ Production images built!"

deploy-prod: ## Deploy to production
	@echo "🚀 Deploying to production..."
	docker-compose -f docker-compose.production.yml up -d --build
	@echo "✅ Production deployment complete!"

deploy-k8s: ## Deploy to Kubernetes
	@echo "☸️ Deploying to Kubernetes..."
	kubectl apply -f k8s/
	@echo "✅ Kubernetes deployment complete!"

backup: ## Create database backup
	@echo "💾 Creating database backup..."
	docker-compose exec postgres pg_dump -U chatbot_user chatbot_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created successfully!"

restore: ## Restore database backup
	@echo "🔄 Restoring database..."
	@read -p "Enter backup file path: " backup_file; \
	docker-compose exec -T postgres psql -U chatbot_user chatbot_db < $$backup_file
	@echo "✅ Database restored!"

logs: ## View application logs
	@echo "📊 Viewing application logs..."
	docker-compose logs -f backend frontend

health: ## Check system health
	@echo "🏥 Checking system health..."
	curl -f http://localhost:8000/api/v1/health && echo "✅ Backend healthy" || echo "❌ Backend unhealthy"
	curl -f http://localhost:5173 && echo "✅ Frontend healthy" || echo "❌ Frontend unhealthy"

clean: ## Clean up resources
	@echo "🧹 Cleaning up resources..."
	docker system prune -f
	cd frontend && rm -rf dist node_modules/.cache
	cd backend && find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "✅ Cleanup complete!"

security-scan: ## Run security vulnerability scan
	@echo "🔒 Running security vulnerability scan..."
	cd backend && pip-audit
	cd frontend && npm audit
	@echo "✅ Security scan complete!"

setup-db: ## Initialize database
	cd backend && alembic upgrade head

migrate: ## Create new migration
	cd backend && alembic revision --autogenerate -m "$(msg)"

upgrade-db: ## Apply database migrations
	cd backend && alembic upgrade head
