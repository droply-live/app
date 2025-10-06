#!/bin/bash

# Add this to your ~/.bashrc or ~/.zshrc file
# Then you can just run: droply

droply() {
    # Source the environment file
    if [ -f .envrc ]; then
        source .envrc
    else
        echo "❌ No .envrc file found. Run 'git checkout <branch>' first."
        return 1
    fi
    
    # Run the app
    python app.py
}

# Make it available in current shell
alias droply='droply'
