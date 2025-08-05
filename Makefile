.PHONY: help install dev build test clean docker-build docker-up docker-down

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install all dependencies
	@echo "Installing dependencies..."
	npm install
	cd frontend && npm install
	cd backend && pip install -r requirements.txt

dev: ## Start development servers
	@echo "Starting development servers..."
	npm run dev

build: ## Build the application
	@echo "Building application..."
	cd frontend && npm run build

test: ## Run all tests
	@echo "Running tests..."
	cd frontend && npm run test
	cd backend && pytest

test-frontend: ## Run frontend tests
	cd frontend && npm run test

test-backend: ## Run backend tests
	cd backend && pytest

lint: ## Run linting
	@echo "Running linting..."
	cd frontend && npm run lint
	cd backend && flake8 app/

format: ## Format code
	@echo "Formatting code..."
	cd frontend && npm run format
	cd backend && black app/ && isort app/

clean: ## Clean build artifacts
	@echo "Cleaning..."
	rm -rf frontend/dist
	rm -rf frontend/node_modules
	rm -rf backend/__pycache__
	rm -rf backend/.pytest_cache

docker-build: ## Build Docker containers
	docker-compose build

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

setup-db: ## Initialize database
	cd backend && alembic upgrade head

migrate: ## Create new migration
	cd backend && alembic revision --autogenerate -m "$(msg)"

upgrade-db: ## Apply database migrations
	cd backend && alembic upgrade head
