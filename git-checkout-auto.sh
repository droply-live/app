#!/bin/bash

# Function that automatically sets environment after git checkout
# Add this to your ~/.bashrc or ~/.zshrc

git() {
    # Run the actual git command
    /usr/bin/git "$@"
    
    # If it was a successful checkout, set environment
    if [ "$1" = "checkout" ] && [ $? -eq 0 ]; then
        echo ""
        echo "🔄 Auto-switching environment..."
        
        # Get current branch
        current_branch=$(/usr/bin/git branch --show-current 2>/dev/null)
        
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
}
