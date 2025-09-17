#!/bin/bash

# Production Deployment Script for Droply
echo "🚀 Starting production deployment..."

# Set production environment variables
export FLASK_ENV=production
export ENVIRONMENT=production
export FLASK_DEBUG=0
export YOUR_DOMAIN=https://droply.live

# Build and run with production configuration
echo "📦 Building production Docker image..."
docker-compose -f docker-compose.prod.yml build

echo "🔄 Stopping any running containers..."
docker-compose -f docker-compose.prod.yml down

echo "🚀 Starting production container..."
docker-compose -f docker-compose.prod.yml up -d

echo "✅ Production deployment complete!"
echo "🌐 Your app should be available at: https://droply.live"
echo ""
echo "📋 Next steps:"
echo "1. Update Google OAuth redirect URIs to include: https://droply.live/auth/google/callback"
echo "2. Test the Google OAuth flow"
echo "3. Update Stripe keys to live keys if needed"
echo ""
echo "🔍 To check logs: docker-compose -f docker-compose.prod.yml logs -f"
