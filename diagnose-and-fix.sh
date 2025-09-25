#!/bin/bash

echo "🔍 Diagnosing deployment issues..."
echo "=================================="

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ] && [ ! -f "Dockerfile" ]; then
    echo "❌ Error: Not in the app directory. Please run this from /opt/droply"
    exit 1
fi

echo "📍 Current directory: $(pwd)"
echo ""

# Check current container status
echo "📊 Current container status:"
docker ps -a --filter "name=droply"
echo ""

# Check application logs for errors
echo "📋 Recent application logs (last 50 lines):"
echo "----------------------------------------"
docker logs droply-web-1 --tail 50 2>&1 | grep -E "(ERROR|CRITICAL|Exception|Traceback|404|500)" || echo "No obvious errors found in recent logs"
echo ""

# Check if routes are loading
echo "🔍 Checking if routes are loading..."
echo "-----------------------------------"
docker logs droply-web-1 --tail 100 2>&1 | grep -E "(Route|@app.route|privacy-policy|terms-of-service|find-experts)" || echo "No route loading messages found"
echo ""

# Check Python syntax
echo "🐍 Checking Python syntax..."
echo "---------------------------"
docker exec droply-web-1 python3 -c "import routes; print('✅ Routes imported successfully')" 2>&1 || echo "❌ Python import error detected"
echo ""

# Check if templates exist
echo "📄 Checking if templates exist..."
echo "--------------------------------"
docker exec droply-web-1 ls -la /app/templates/ | grep -E "(privacy_policy|terms_of_service)" || echo "❌ Templates not found"
echo ""

# Restart container
echo "🔄 Restarting container..."
echo "-------------------------"
docker-compose down
sleep 5
docker-compose up -d
echo ""

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 10

# Check if container is running
echo "📊 Container status after restart:"
docker ps --filter "name=droply"
echo ""

# Test routes
echo "🧪 Testing routes..."
echo "-------------------"
echo "Testing Privacy Policy..."
curl -s -o /dev/null -w "Privacy Policy: %{http_code}\n" http://localhost:5000/privacy-policy

echo "Testing Terms of Service..."
curl -s -o /dev/null -w "Terms of Service: %{http_code}\n" http://localhost:5000/terms-of-service

echo "Testing Find Experts..."
curl -s -o /dev/null -w "Find Experts: %{http_code}\n" http://localhost:5000/find-experts

echo ""
echo "✅ Diagnosis and restart completed!"
echo "🌐 Check the live site now: https://droply.live"
