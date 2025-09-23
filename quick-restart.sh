#!/bin/bash

echo "🔄 Quick container restart..."
cd /opt/droply
docker-compose down
sleep 5
docker-compose up -d
echo "✅ Container restarted!"
echo "⏳ Waiting 15 seconds for startup..."
sleep 15
echo "🧪 Testing routes..."
curl -s -o /dev/null -w "Privacy Policy: %{http_code}\n" http://localhost:5000/privacy-policy
curl -s -o /dev/null -w "Terms of Service: %{http_code}\n" http://localhost:5000/terms-of-service
curl -s -o /dev/null -w "Find Experts: %{http_code}\n" http://localhost:5000/find-experts
echo "🌐 Check live site: https://droply.live"
