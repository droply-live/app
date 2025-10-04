# 🎯 Automatic Environment Detection Guide

## **✨ Problem Solved!**

No more manual environment switching! The system now automatically detects your Git branch and sets the appropriate environment.

## **🔄 How It Works**

### **Branch-Based Environment Detection:**
- **`main` branch** → Automatically sets **PRODUCTION** environment
- **Any other branch** (`develop`, `feature/*`, etc.) → Automatically sets **DEVELOPMENT** environment

### **Environment Features:**

#### **Production Environment (main branch):**
- ✅ Book Now button **hidden**
- ✅ Test Video link **hidden**
- ✅ `/dev/test-video-call` route **disabled**
- ✅ Minimal debug logging
- ✅ Production domain: `https://droply.live`

#### **Development Environment (all other branches):**
- ✅ Book Now button **visible**
- ✅ Test Video link **visible**
- ✅ `/dev/test-video-call` route **available**
- ✅ Full debug logging enabled
- ✅ Development domain: `http://localhost:5000`

## **🚀 Usage Options**

### **Option 1: Smart Starter (Recommended)**
```bash
# Just run this - it handles everything automatically!
python start.py
```

**What it does:**
1. Detects current Git branch
2. Sets appropriate environment variables
3. Starts Flask app with correct settings
4. Shows you what environment is active

### **Option 2: Auto Environment Setup**
```bash
# Set environment based on current branch
source ./env-auto.sh

# Then start Flask normally
python app.py
```

### **Option 3: Manual (Old Way)**
```bash
# Still works if you prefer manual control
export FLASK_ENV=development  # or production
python app.py
```

## **🎯 Example Workflow**

### **Development Work:**
```bash
# 1. Switch to develop branch
git checkout develop

# 2. Start with auto environment
python start.py
# → Automatically sets DEVELOPMENT environment
# → Book Now button visible, debug logging on
```

### **Production Testing:**
```bash
# 1. Switch to main branch
git checkout main

# 2. Start with auto environment
python start.py
# → Automatically sets PRODUCTION environment
# → Book Now button hidden, minimal logging
```

### **Feature Development:**
```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Start with auto environment
python start.py
# → Automatically sets DEVELOPMENT environment
# → All development features available
```

## **🔧 Technical Details**

### **Files Created:**
- `start.py` - Smart Flask starter with auto environment detection
- `env-auto.sh` - Shell script for environment setup
- `auto-env.py` - Python utility for environment detection

### **Environment Variables Set:**

#### **Development Mode:**
```bash
FLASK_ENV=development
ENVIRONMENT=development
FLASK_DEBUG=1
YOUR_DOMAIN=http://localhost:5000
```

#### **Production Mode:**
```bash
FLASK_ENV=production
ENVIRONMENT=production
FLASK_DEBUG=0
YOUR_DOMAIN=https://droply.live
```

## **📋 Quick Reference**

### **Start Development:**
```bash
git checkout develop
python start.py
```

### **Start Production:**
```bash
git checkout main
python start.py
```

### **Check Current Environment:**
```bash
echo "Branch: $(git branch --show-current)"
echo "FLASK_ENV: $FLASK_ENV"
```

## **🎉 Benefits**

1. **No More Manual Switching** - Environment automatically matches branch
2. **No More Mistakes** - Can't accidentally run development features in production
3. **Consistent Workflow** - Same command works everywhere
4. **Clear Feedback** - Shows you exactly what environment is active
5. **Branch Safety** - Production features only available on main branch

## **🚨 Important Notes**

### **Branch Safety:**
- **Development features** (Book Now, Test Video) are **ONLY** available on non-main branches
- **Production features** are **ONLY** available on main branch
- This prevents accidental exposure of development features in production

### **Deployment:**
- **Production server** always runs from `main` branch
- **Environment variables** on server are set to production
- **No development features** are exposed in production

### **Local Testing:**
- **Main branch locally** = Production mode (for testing production behavior)
- **Develop branch locally** = Development mode (for feature development)
- **Feature branches locally** = Development mode (for feature development)

## **🎯 Perfect Workflow**

```bash
# Daily development
git checkout develop
python start.py  # → Development environment

# Feature work
git checkout -b feature/my-feature
python start.py  # → Development environment

# Production testing
git checkout main
python start.py  # → Production environment

# Deploy to production
git push origin main  # → Auto-deploys with production environment
```

**That's it! No more manual environment switching! 🎉**

