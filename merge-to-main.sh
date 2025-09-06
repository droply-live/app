#!/bin/bash

# Merge Develop to Main Script
# This script merges changes from develop branch to main branch

echo "🔄 Merging develop to main..."

# Check if we're on develop branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "develop" ]; then
    echo "❌ Error: You must be on the 'develop' branch to merge to main"
    echo "Current branch: $current_branch"
    exit 1
fi

# Make sure develop is up to date
echo "📤 Pushing develop branch..."
git push origin develop

# Switch to main branch
echo "🌿 Switching to main branch..."
git checkout main

# Pull latest main
echo "📥 Pulling latest main..."
git pull origin main

# Merge develop into main
echo "🔀 Merging develop into main..."
git merge develop

# Push main branch
echo "📤 Pushing main branch..."
git push origin main

echo "✅ Merge complete!"
echo "🌿 You're now on main branch"
echo "🚀 Run ./deploy.sh to deploy to production"
