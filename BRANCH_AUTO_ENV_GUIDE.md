# 🎯 Automatic Branch-Based Environment Guide

## **✨ Perfect! Environment Auto-Detection is Now Active!**

The environment automatically changes when you switch Git branches - no scripts needed!

## **🔄 How It Works**

### **Automatic Detection:**
- **Switch to `main` branch** → **Production environment** (Book Now hidden)
- **Switch to any other branch** → **Development environment** (Book Now visible)

### **What Happens Automatically:**
1. **Git hook** runs when you switch branches
2. **Environment file** (`.env.branch`) is created/updated
3. **Environment variables** are set automatically
4. **App detects** the environment when you run it

## **🚀 Your Super Simple Workflow**

### **Development Work:**
```bash
# 1. Switch to develop branch
git checkout develop
# → Automatically sets development environment
# → You'll see: "🔧 Auto-set: Development environment (develop branch)"

# 2. Run your app
python app.py
# → Uses development environment automatically
# → Book Now button visible, debug logging on
```

### **Production Testing:**
```bash
# 1. Switch to main branch  
git checkout main
# → Automatically sets production environment
# → You'll see: "🚀 Auto-set: Production environment (main branch)"

# 2. Run your app
python app.py
# → Uses production environment automatically
# → Book Now button hidden, minimal logging
```

### **Feature Development:**
```bash
# 1. Create feature branch
git checkout -b feature/new-feature
# → Automatically sets development environment

# 2. Run your app
python app.py
# → Uses development environment automatically
```

## **🎯 What You See When Switching Branches**

### **Switching to Main (Production):**
```
Switched to branch 'main'
🚀 Auto-set: Production environment (main branch)
✅ Environment variables set for branch: main
```

### **Switching to Develop (Development):**
```
Switched to branch 'develop'  
🔧 Auto-set: Development environment (develop branch)
✅ Environment variables set for branch: develop
```

## **📁 Files Created**

- **`.env.branch`** - Contains environment variables for current branch
- **`.git/hooks/post-checkout`** - Git hook that runs on branch switch
- **`setup-env.sh`** - Manual setup script (if needed)

## **🔧 Environment Variables Set**

### **Development Environment (non-main branches):**
```
FLASK_ENV=development
ENVIRONMENT=development
FLASK_DEBUG=1
YOUR_DOMAIN=http://localhost:5000
```

### **Production Environment (main branch):**
```
FLASK_ENV=production
ENVIRONMENT=production
FLASK_DEBUG=0
YOUR_DOMAIN=https://droply.live
```

## **🎉 Benefits**

1. **Zero Manual Setup** - Just switch branches and run your app
2. **Automatic Detection** - Environment changes with branch
3. **No Scripts Needed** - Just `git checkout` and `python app.py`
4. **Consistent Behavior** - Always matches your branch
5. **Safe Development** - Can't accidentally use dev features in production

## **🛠️ Troubleshooting**

### **If Environment Doesn't Update:**
```bash
# Manually run the setup script
source setup-env.sh

# Or check if hook is executable
chmod +x .git/hooks/post-checkout
```

### **Check Current Environment:**
```bash
# See what's in the environment file
cat .env.branch

# Check current branch
git branch --show-current
```

### **Manual Environment Override:**
```bash
# If you need to override for testing
export FLASK_ENV=development
python app.py
```

## **🚀 Quick Reference**

```bash
# Development
git checkout develop
python app.py

# Production testing
git checkout main
python app.py

# Feature development
git checkout -b feature/my-feature
python app.py
```

**That's it! Just switch branches and run your app - everything is automatic! 🎉**
