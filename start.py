#!/usr/bin/env python3
"""
Smart Flask Starter for Droply
Automatically detects Git branch and sets appropriate environment
"""

import os
import sys
import subprocess

def get_current_branch():
    """Get the current Git branch"""
    try:
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def set_environment_for_branch(branch):
    """Set environment variables based on Git branch"""
    if branch == 'main':
        # Production environment
        os.environ['FLASK_ENV'] = 'production'
        os.environ['ENVIRONMENT'] = 'production'
        os.environ['FLASK_DEBUG'] = '0'
        os.environ['YOUR_DOMAIN'] = 'https://droply.live'
        
        print("🚀 Production Environment")
        print("   Branch: main")
        print("   Features: Production mode, minimal logging")
        print("   Domain: https://droply.live")
    else:
        # Development environment for all other branches
        os.environ['FLASK_ENV'] = 'development'
        os.environ['ENVIRONMENT'] = 'development'
        os.environ['FLASK_DEBUG'] = '1'
        os.environ['YOUR_DOMAIN'] = 'http://localhost:5000'
        
        print("🔧 Development Environment")
        print("   Branch:", branch)
        print("   Features: Book Now button, Test Video link, Debug logging")
        print("   Domain: http://localhost:5000")

def main():
    """Main function"""
    print("🎯 Droply Smart Starter")
    print("=" * 40)
    
    # Get current branch
    current_branch = get_current_branch()
    
    if not current_branch:
        print("❌ Error: Not in a Git repository or Git not available")
        print("   Please run this script from within your Droply repository")
        sys.exit(1)
    
    print(f"📋 Current branch: {current_branch}")
    print("")
    
    # Set environment based on branch
    set_environment_for_branch(current_branch)
    print("")
    
    # Start Flask app
    print("🚀 Starting Flask application...")
    print("   Press Ctrl+C to stop")
    print("=" * 40)
    
    try:
        # Import and run the Flask app
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=os.environ.get('FLASK_DEBUG') == '1')
    except ImportError:
        print("❌ Error: Could not import Flask app")
        print("   Make sure you're in the correct directory with app.py")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Flask application stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()
