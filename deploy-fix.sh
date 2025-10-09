#!/bin/bash
# Deployment fix script - removes conflicting containers

echo "🧹 Cleaning up conflicting containers..."

# Stop and remove any existing droply-web-1 container
docker stop droply-web-1 2>/dev/null || true
docker rm droply-web-1 2>/dev/null || true

# Stop and remove any containers on port 5000
docker ps -q --filter "publish=5000" | xargs -r docker stop || true
docker ps -aq --filter "publish=5000" | xargs -r docker rm || true

# Stop and remove any containers on port 5001  
docker ps -q --filter "publish=5001" | xargs -r docker stop || true
docker ps -aq --filter "publish=5001" | xargs -r docker rm || true

echo "✅ Cleanup complete. Ready for deployment."

