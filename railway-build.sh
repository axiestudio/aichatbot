#!/bin/bash

# Railway Build Script - Optimized for Railway deployment
# This script builds the frontend and prepares for Railway deployment

set -e

echo "🚀 Starting Railway-optimized build process..."

# Check if we're in Railway environment
if [ -n "$RAILWAY_ENVIRONMENT" ]; then
    echo "📡 Detected Railway environment: $RAILWAY_ENVIRONMENT"
else
    echo "🏠 Running in local environment"
fi

# Build frontend with minimal resources
echo "🎨 Building frontend..."
cd frontend

# Install only production dependencies
echo "📦 Installing frontend dependencies (production only)..."
npm ci --omit=dev --silent

# Build with memory optimization
echo "🔨 Building frontend assets..."
NODE_OPTIONS="--max-old-space-size=1024" npm run build

# Verify build output
if [ ! -d "dist" ]; then
    echo "❌ Frontend build failed - dist directory not found"
    exit 1
fi

echo "✅ Frontend build completed successfully"
echo "📊 Build size: $(du -sh dist | cut -f1)"

# Return to root
cd ..

echo "🎉 Railway build process completed!"
echo "📁 Frontend assets ready in frontend/dist/"
echo "🐳 Ready for Docker build"
