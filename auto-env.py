#!/usr/bin/env python3
"""
Automatic Environment Detection for Droply
Sets environment variables based on current Git branch
"""

import os
import subprocess
import sys

def get_current_branch():
    """Get the current Git branch"""
    try:
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def set_development_environment():
    """Set development environment variables"""
    os.environ['FLASK_ENV'] = 'development'
    os.environ['ENVIRONMENT'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    os.environ['YOUR_DOMAIN'] = 'http://localhost:5000'
    
    print("🔧 Development Environment Set")
    print("   Branch: develop/feature branch detected")
    print("   Features: Book Now button, Test Video link, Debug logging")

def set_production_environment():
    """Set production environment variables"""
    os.environ['FLASK_ENV'] = 'production'
    os.environ['ENVIRONMENT'] = 'production'
    os.environ['FLASK_DEBUG'] = '0'
    os.environ['YOUR_DOMAIN'] = 'https://droply.live'
    
    print("🚀 Production Environment Set")
    print("   Branch: main branch detected")
    print("   Features: Production mode, minimal logging")

def main():
    """Main function to detect branch and set environment"""
    current_branch = get_current_branch()
    
    if not current_branch:
        print("❌ Not in a Git repository or Git not available")
        sys.exit(1)
    
    print(f"📋 Current branch: {current_branch}")
    
    # Set environment based on branch
    if current_branch == 'main':
        set_production_environment()
    else:
        # All other branches (develop, feature/*, etc.) use development
        set_development_environment()
    
    print(f"✅ Environment configured for branch: {current_branch}")
    print("")

if __name__ == "__main__":
    main()
