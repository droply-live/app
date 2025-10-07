#!/bin/bash

# Git wrapper that automatically sets environment after checkout
# This replaces the git command to add automatic environment switching

# Check if this is a checkout command
if [ "$1" = "checkout" ]; then
    # Run the actual git checkout command
    /usr/bin/git "$@"
    exit_code=$?
    
    # If checkout was successful, automatically source environment
    if [ $exit_code -eq 0 ]; then
        echo ""
        echo "🔄 Auto-switching environment..."
        
        # Get current branch
        current_branch=$(git branch --show-current 2>/dev/null)
        
        if [ "$current_branch" = "main" ]; then
            export FLASK_ENV=production
            export ENVIRONMENT=production
            export FLASK_DEBUG=0
            export YOUR_DOMAIN=https://droply.live
            echo "🚀 Production environment active (main branch)"
            echo "   Book Now button: Hidden"
            echo "   Debug logging: Minimal"
        else
            export FLASK_ENV=development
            export ENVIRONMENT=development
            export FLASK_DEBUG=1
            export YOUR_DOMAIN=http://localhost:5000
            echo "🔧 Development environment active ($current_branch branch)"
            echo "   Book Now button: Visible"
            echo "   Debug logging: Enabled"
        fi
        
        echo "✅ Environment automatically set!"
        echo "💡 Ready to run: python app.py"
    fi
    
    exit $exit_code
else
    # For all other git commands, just run them normally
    /usr/bin/git "$@"
fi
