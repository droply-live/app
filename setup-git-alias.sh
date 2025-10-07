#!/bin/bash

# Setup script to create git alias for automatic environment switching
# Run this once: source setup-git-alias.sh

echo "🎯 Setting up automatic git checkout environment switching..."

# Create the alias
alias git='./git-wrapper.sh'

echo "✅ Git alias created!"
echo ""
echo "Now you can use:"
echo "  git checkout develop  → Automatically sets development environment"
echo "  git checkout main     → Automatically sets production environment"
echo ""
echo "Just run: git checkout <branch> and environment is automatically set!"
echo "Then run: python app.py"
