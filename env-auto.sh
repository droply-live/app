#!/bin/bash

echo "🎯 Auto Environment Setup"
echo "========================"

# Get current Git branch
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)

if [ -z "$CURRENT_BRANCH" ]; then
    echo "❌ Error: Not in a Git repository"
    exit 1
fi

echo "📋 Current branch: $CURRENT_BRANCH"

# Set environment based on branch
if [ "$CURRENT_BRANCH" = "main" ]; then
    echo "🚀 Setting PRODUCTION environment"
    export FLASK_ENV=production
    export ENVIRONMENT=production
    export FLASK_DEBUG=0
    export YOUR_DOMAIN=https://droply.live
    
    echo "   ✅ Production mode enabled"
    echo "   ✅ Book Now button hidden"
    echo "   ✅ Test Video link hidden"
    echo "   ✅ Minimal logging"
else
    echo "🔧 Setting DEVELOPMENT environment"
    export FLASK_ENV=development
    export ENVIRONMENT=development
    export FLASK_DEBUG=1
    export YOUR_DOMAIN=http://localhost:5000
    
    echo "   ✅ Development mode enabled"
    echo "   ✅ Book Now button visible"
    echo "   ✅ Test Video link visible"
    echo "   ✅ Debug logging enabled"
fi

echo ""
echo "🎉 Environment configured for branch: $CURRENT_BRANCH"
echo "   Run: python app.py"
echo "   Or:  python start.py (for smart starter)"
echo ""
