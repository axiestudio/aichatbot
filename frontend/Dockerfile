# Multi-stage production Dockerfile for React frontend
FROM node:18-alpine as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache curl && rm -rf /var/cache/apk/*

# Copy package files
COPY package*.json ./

# Development stage
FROM base as development

# Install all dependencies (including dev)
RUN npm install

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Development command
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Build stage
FROM base as builder

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine as production

# Install curl for health checks
RUN apk add --no-cache curl

# Copy custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create non-root user and set permissions
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001 && \
    chown -R nextjs:nodejs /usr/share/nginx/html && \
    chown -R nextjs:nodejs /var/cache/nginx && \
    chown -R nextjs:nodejs /var/log/nginx && \
    chown -R nextjs:nodejs /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R nextjs:nodejs /var/run/nginx.pid

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80 || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]