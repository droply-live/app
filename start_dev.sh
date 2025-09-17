#!/bin/bash

# Development startup script for Droply
# This script sets the required environment variables and starts the Flask app

echo "Starting Droply development server..."

# Set environment variables
export STRIPE_SECRET_KEY=sk_test_51Ra5LVPJHdGqB6baQmgVOqBxWJYwdgE3nqtjAibCmmNnZ8K2uzFFOmPBszfn5SIvKUyRWFu6rkxnCZbQcSIWfb2G00BoBogDUM
export YOUR_DOMAIN=http://localhost:5001
export FLASK_ENV=development
export ENVIRONMENT=development

# Kill any existing Flask processes
pkill -f "python app.py" 2>/dev/null
sleep 2

# Start the Flask app
echo "Environment variables set:"
echo "STRIPE_SECRET_KEY: $STRIPE_SECRET_KEY"
echo "YOUR_DOMAIN: $YOUR_DOMAIN"
echo "FLASK_ENV: $FLASK_ENV"
echo ""
echo "Starting Flask app on http://localhost:5001"
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
