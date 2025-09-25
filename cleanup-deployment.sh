#!/bin/bash

# Cleanup script for deployment port conflicts
echo "🧹 Cleaning up existing containers on port 5001..."

# Stop and remove containers using port 5001
docker ps -q --filter "publish=5001" | xargs -r docker stop
docker ps -aq --filter "publish=5001" | xargs -r docker rm

# Stop and remove containers with "droply-web-new" in the name
docker ps -aq --filter "name=droply-web-new" | xargs -r docker stop
docker ps -aq --filter "name=droply-web-new" | xargs -r docker rm

echo "✅ Cleanup completed. You can now trigger a new deployment."
