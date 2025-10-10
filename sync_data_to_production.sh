#!/bin/bash

# Data Sync Script for Droply Production
# This script helps sync your local data to production

echo "🔄 Droply Data Sync to Production"
echo "================================="

# Check if we have the necessary files
if [ ! -f "instance/droply.db" ]; then
    echo "❌ Local database not found at instance/droply.db"
    echo "   Please run this script from your project root directory"
    exit 1
fi

# Check if static/uploads exists
if [ ! -d "static/uploads" ]; then
    echo "⚠️  No static/uploads directory found"
    mkdir -p static/uploads
fi

echo "📊 Local data found:"
echo "   - Database: $(ls -lh instance/droply.db 2>/dev/null || echo 'Not found')"
echo "   - Uploads: $(find static/uploads -type f | wc -l) files"

echo ""
echo "🚀 To sync your data to production:"
echo "1. Commit and push your changes to GitHub"
echo "2. The deployment workflow will now preserve your data"
echo ""
echo "📝 Your local data includes:"
echo "   - User accounts and profiles"
echo "   - Database schema with all columns"
echo "   - Uploaded profile pictures"
echo "   - Calendar settings"
echo "   - All user preferences and settings"
echo ""
echo "✅ The updated deployment workflow will:"
echo "   - Preserve your existing database"
echo "   - Keep all uploaded files"
echo "   - Run migrations to add missing columns"
echo "   - Maintain all your data across deployments"
echo ""
echo "🎯 Next steps:"
echo "1. git add ."
echo "2. git commit -m 'Fix deployment data persistence'"
echo "3. git push origin main"
echo "4. Your production site will have all your local data!"
