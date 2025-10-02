#!/bin/bash

echo "🧹 Starting server cleanup..."

# Check disk usage before cleanup
echo "📊 Disk usage before cleanup:"
df -h

echo "🐳 Cleaning up Docker..."

# Stop all running containers
echo "Stopping all containers..."
docker stop $(docker ps -aq) 2>/dev/null || true

# Remove all containers
echo "Removing all containers..."
docker rm $(docker ps -aq) 2>/dev/null || true

# Remove all images
echo "Removing all images..."
docker rmi $(docker images -q) 2>/dev/null || true

# Remove all volumes
echo "Removing all volumes..."
docker volume rm $(docker volume ls -q) 2>/dev/null || true

# Remove all networks
echo "Removing all networks..."
docker network prune -f

# Clean up build cache
echo "Cleaning build cache..."
docker builder prune -af

# Clean up system
echo "🧽 Cleaning system..."

# Clean package cache
apt-get clean
apt-get autoclean
apt-get autoremove -y

# Clean up logs
journalctl --vacuum-time=7d

# Clean up temp files
rm -rf /tmp/*
rm -rf /var/tmp/*

# Check disk usage after cleanup
echo "📊 Disk usage after cleanup:"
df -h

echo "✅ Server cleanup completed!"
