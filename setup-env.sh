#!/bin/bash

# Setup environment variables based on current Git branch
# Run this once: source setup-env.sh

echo "🎯 Setting up environment for current branch..."

# Get current branch
current_branch=$(git branch --show-current 2>/dev/null)

if [ -z "$current_branch" ]; then
    echo "❌ Not in a Git repository"
    return 1
fi

echo "📋 Current branch: $current_branch"

# Set environment based on branch
if [ "$current_branch" = "main" ]; then
    export FLASK_ENV=production
    export ENVIRONMENT=production
    export FLASK_DEBUG=0
    export YOUR_DOMAIN=https://droply.live
    echo "🚀 Set: Production environment"
    echo "   Features: Book Now hidden, minimal logging"
else
    export FLASK_ENV=development
    export ENVIRONMENT=development
    export FLASK_DEBUG=1
    export YOUR_DOMAIN=http://localhost:5000
    echo "🔧 Set: Development environment"
    echo "   Features: Book Now visible, debug logging"
fi

echo "✅ Environment configured for branch: $current_branch"
echo ""
echo "Now you can run:"
echo "  python app.py"
echo "  docker-compose up"
echo ""
