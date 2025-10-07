# 🎯 Droply Environment Setup

## **One-Line Solution**

Add this function to your `~/.bashrc` or `~/.zshrc`:

```bash
git() {
    /usr/bin/git "$@"
    if [ "$1" = "checkout" ] && [ $? -eq 0 ]; then
        echo ""
        echo "🔄 Auto-switching environment..."
        current_branch=$(/usr/bin/git branch --show-current 2>/dev/null)
        if [ "$current_branch" = "main" ]; then
            export FLASK_ENV=production
            export ENVIRONMENT=production
            export FLASK_DEBUG=0
            export YOUR_DOMAIN=https://droply.live
            echo "🚀 Production environment active (main branch)"
        else
            export FLASK_ENV=development
            export ENVIRONMENT=development
            export FLASK_DEBUG=1
            export YOUR_DOMAIN=http://localhost:5000
            echo "🔧 Development environment active ($current_branch branch)"
        fi
        echo "✅ Environment automatically set!"
        echo "💡 Ready to run: python app.py"
    fi
}
```

## **Usage**

```bash
# Development
git checkout develop
python app.py

# Production testing
git checkout main
python app.py
```

**That's it! Just switch branches and run your app.**
