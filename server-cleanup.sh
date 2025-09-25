#!/bin/bash

echo "🧹 Starting server cleanup for deployment port conflicts..."
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ] && [ ! -f "Dockerfile" ]; then
    echo "❌ Error: Not in the app directory. Please run this from /opt/droply"
    exit 1
fi

echo "📍 Current directory: $(pwd)"
echo ""

# Stop and remove containers using port 5001
echo "🛑 Stopping containers on port 5001..."
docker ps -q --filter "publish=5001" | xargs -r docker stop
echo "🗑️  Removing containers on port 5001..."
docker ps -aq --filter "publish=5001" | xargs -r docker rm

# Stop and remove containers with "droply-web-new" in the name
echo "🛑 Stopping droply-web-new containers..."
docker ps -aq --filter "name=droply-web-new" | xargs -r docker stop
echo "🗑️  Removing droply-web-new containers..."
docker ps -aq --filter "name=droply-web-new" | xargs -r docker rm

# Clean up any dangling containers
echo "🧽 Cleaning up dangling containers..."
docker container prune -f

# Show current container status
echo ""
echo "📊 Current container status:"
docker ps -a --filter "name=droply"

echo ""
echo "✅ Cleanup completed successfully!"
echo "🚀 You can now trigger a new deployment."
echo ""
echo "To trigger deployment, run:"
echo "  git pull origin main"
echo ""
