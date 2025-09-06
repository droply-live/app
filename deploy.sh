#!/bin/bash

# Droply Deployment Script
# This script pushes changes to the live server

echo "🚀 Deploying Droply to production..."

# Check if we're on develop branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "develop" ]; then
    echo "❌ Error: You must be on the 'develop' branch to deploy"
    echo "Current branch: $current_branch"
    exit 1
fi

# Push to git
echo "📤 Pushing changes to git..."
git push origin develop

# Deploy to server
echo "🌐 Deploying to DigitalOcean server..."
ssh -i ~/.ssh/droply_key root@142.93.75.62 "cd /opt/droply && git pull origin develop && docker compose down && docker compose build --no-cache && docker compose up -d"

echo "✅ Deployment complete!"
echo "🌍 Your site is live at: https://droply.live"
