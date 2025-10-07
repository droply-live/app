# 🎯 Droply Environment Setup

## **Automatic Environment Detection**

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
            echo "   Book Now button: Hidden"
        else
            export FLASK_ENV=development
            export ENVIRONMENT=development
            export FLASK_DEBUG=1
            export YOUR_DOMAIN=http://localhost:5000
            echo "🔧 Development environment active ($current_branch branch)"
            echo "   Book Now button: Visible"
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

## **Features**

- **main branch**: Production environment (Book Now button hidden)
- **all other branches**: Development environment (Book Now button visible)
- **Automatic detection**: Environment changes when you switch branches
- **Zero configuration**: Just add the function to your shell profile
