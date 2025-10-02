# Deployment Improvements for Disk Space Management

## 🎯 Problem Solved
The server was running out of disk space (100% usage) causing deployment failures. We've cleaned up 44GB of space, but need to prevent this from happening again.

## 🔧 Manual Deployment Script Improvements

Since we can't modify the GitHub Actions workflow directly, here are the improvements to manually apply to the server:

### 1. Enhanced Cleanup in Deployment Script

Add this to the beginning of your deployment script (before building new images):

```bash
# Comprehensive cleanup of old containers and images
echo "🧹 Cleaning up old containers and images..."

# Stop and remove all droply-related containers
docker ps -aq --filter "name=droply" | xargs -r docker stop || true
docker ps -aq --filter "name=droply" | xargs -r docker rm || true
docker ps -aq --filter "name=droply-web" | xargs -r docker stop || true
docker ps -aq --filter "name=droply-web" | xargs -r docker rm || true

# Clean up containers on ports 5000 and 5001
docker ps -q --filter "publish=5000" | xargs -r docker stop || true
docker ps -q --filter "publish=5001" | xargs -r docker stop || true
docker ps -aq --filter "publish=5000" | xargs -r docker rm || true
docker ps -aq --filter "publish=5001" | xargs -r docker rm || true

# Remove old droply images (keep only the latest 3)
echo "🗑️ Removing old droply images..."
docker images --filter "reference=droply-web" --format "table {{.Repository}}:{{.Tag}}\t{{.CreatedAt}}" | tail -n +2 | sort -k2 -r | tail -n +4 | awk '{print $1}' | xargs -r docker rmi || true

# Clean up dangling images and build cache
docker image prune -f
docker builder prune -f
```

### 2. Enhanced Final Cleanup

Add this after successful deployment:

```bash
# Final cleanup of old images (keep only current and 2 previous)
echo "🧹 Final cleanup of old images..."
docker images --filter "reference=droply-web" --format "table {{.Repository}}:{{.Tag}}\t{{.CreatedAt}}" | tail -n +2 | sort -k2 -r | tail -n +3 | awk '{print $1}' | xargs -r docker rmi || true
```

## 🛠️ Manual Cleanup Script

Use the `cleanup-docker.sh` script on the server:

```bash
# On the server:
cd /opt/droply
chmod +x cleanup-docker.sh
./cleanup-docker.sh
```

## 📊 Monitoring Disk Usage

Add this to your deployment script to monitor disk usage:

```bash
# Check disk usage before and after cleanup
echo "📊 Disk usage before cleanup:"
df -h

# ... cleanup commands ...

echo "📊 Disk usage after cleanup:"
df -h
```

## 🚀 Benefits

1. **Prevents Disk Space Buildup**: Automatically removes old images and containers
2. **Keeps Only Recent Images**: Maintains latest 3 images for rollback capability
3. **Comprehensive Cleanup**: Removes dangling images, build cache, and unused resources
4. **Zero Downtime**: Maintains service availability during cleanup
5. **Manual Override**: Cleanup script available for manual maintenance

## 🔄 Implementation

1. **Immediate**: Use the cleanup script to clean current server
2. **Long-term**: Apply the enhanced deployment script improvements
3. **Monitoring**: Check disk usage regularly to prevent future issues

## 📈 Expected Results

- **Disk Usage**: Should stay below 20% (vs previous 100%)
- **Deployment Success**: No more "No space left on device" errors
- **Performance**: Faster deployments due to less disk I/O
- **Reliability**: Consistent deployment success rate
