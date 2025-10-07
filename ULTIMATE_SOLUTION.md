# 🎯 Ultimate Solution - Just ONE Line!

## **✨ Add This to Your Shell Profile**

Add this ONE function to your `~/.bashrc` or `~/.zshrc`:

```bash
# Droply automatic environment switching
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

## **🚀 Your Ultimate Workflow:**

```bash
# Development
git checkout develop
python app.py

# Production testing
git checkout main
python app.py
```

## **🎯 What Happens:**

1. **`git checkout develop`** → Automatically sets development environment
2. **`python app.py`** → Runs with correct environment

**That's it! Just 2 lines total!**

## **📝 Setup (One-time only):**

1. **Add the function** to your `~/.bashrc` or `~/.zshrc`
2. **Reload your shell**: `source ~/.bashrc` (or `source ~/.zshrc`)
3. **Done!** Now just use `git checkout` and everything is automatic

## **🎉 Result:**

- **Just `git checkout`** - environment automatically switches
- **Just `python app.py`** - runs with correct environment
- **No extra commands needed!**
