#!/bin/bash

echo "🧹 Docker Cleanup Script for Droply"
echo "=================================="

# Check current disk usage
echo "📊 Current disk usage:"
df -h

echo ""
echo "🐳 Cleaning up Docker resources..."

# Stop and remove all droply containers
echo "Stopping and removing all droply containers..."
docker ps -aq --filter "name=droply" | xargs -r docker stop || true
docker ps -aq --filter "name=droply" | xargs -r docker rm || true

# Remove old droply images (keep only the latest 3)
echo "Removing old droply images (keeping latest 3)..."
docker images --filter "reference=droply-web" --format "table {{.Repository}}:{{.Tag}}\t{{.CreatedAt}}" | tail -n +2 | sort -k2 -r | tail -n +4 | awk '{print $1}' | xargs -r docker rmi || true

# Clean up dangling images
echo "Removing dangling images..."
docker image prune -f

# Clean up build cache
echo "Cleaning build cache..."
docker builder prune -f

# Clean up unused volumes
echo "Cleaning unused volumes..."
docker volume prune -f

# Clean up unused networks
echo "Cleaning unused networks..."
docker network prune -f

# Final disk usage check
echo ""
echo "📊 Disk usage after cleanup:"
df -h

echo ""
echo "✅ Docker cleanup completed!"
echo "💾 Space freed up for future deployments"
