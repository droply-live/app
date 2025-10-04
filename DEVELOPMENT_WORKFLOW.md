# Development Workflow for Droply

## 🌿 Git Branch Strategy

### **Current Branches:**
- `main` - Production code (auto-deploys to production)
- `develop` - Development code (behind main)
- `feature/*` - Feature branches

### **Recommended Workflow:**

#### **For Development:**
```bash
# 1. Switch to develop branch
git checkout develop

# 2. Pull latest changes from main
git pull origin main

# 3. Set development environment
export FLASK_ENV=development
export ENVIRONMENT=development
export FLASK_DEBUG=1

# 4. Run development server
python app.py
# Server runs on http://localhost:5000
```

#### **For Production:**
```bash
# 1. Switch to main branch
git checkout main

# 2. Set production environment
export FLASK_ENV=production
export ENVIRONMENT=production
export FLASK_DEBUG=0

# 3. Run production server
python app.py
# Server runs on http://localhost:5000
```

## 🔧 Environment Configuration

### **Development Environment Variables:**
```bash
# Development settings
FLASK_ENV=development
ENVIRONMENT=development
FLASK_DEBUG=1

# Use test Stripe keys
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_test_...

# Use localhost
YOUR_DOMAIN=http://localhost:5000
```

### **Production Environment Variables:**
```bash
# Production settings
FLASK_ENV=production
ENVIRONMENT=production
FLASK_DEBUG=0

# Use live Stripe keys
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Use production domain
YOUR_DOMAIN=https://droply.live
```

## 🚀 Deployment Strategy

### **Current Setup:**
- **`main` branch** → Auto-deploys to production server
- **`develop` branch** → Local development only

### **Recommended Changes:**

#### **Option 1: Keep Current Setup**
- Work on `main` branch
- Use environment variables to control behavior
- Deploy to production from `main`

#### **Option 2: Use Develop Branch**
- Work on `develop` branch
- Merge to `main` when ready for production
- Deploy to production from `main`

## 🧪 Development Testing

### **Local Development (localhost:5000):**
```bash
# Set development environment
export FLASK_ENV=development
export ENVIRONMENT=development

# Run server
python app.py

# Access development features:
# - Book Now button visible
# - Test Video link in navigation
# - /dev/test-video-call route available
```

### **Production Testing (localhost:5000 with production settings):**
```bash
# Set production environment
export FLASK_ENV=production
export ENVIRONMENT=production

# Run server
python app.py

# Production behavior:
# - Book Now button hidden
# - Test Video link hidden
# - /dev/test-video-call route disabled
```

## 📝 Recommended Workflow

### **Daily Development:**
1. **Start development**:
   ```bash
   git checkout develop
   export FLASK_ENV=development
   python app.py
   ```

2. **Make changes and test**:
   - Use `/dev/test-video-call` for video testing
   - Use Book Now button for full flow testing
   - Test on localhost:5000

3. **Commit changes**:
   ```bash
   git add .
   git commit -m "Feature: Add new functionality"
   git push origin develop
   ```

### **Deploy to Production:**
1. **Merge to main**:
   ```bash
   git checkout main
   git merge develop
   git push origin main
   ```

2. **Production auto-deploys** from main branch

## 🔄 Environment Switching

### **Quick Environment Switch:**
```bash
# Development
export FLASK_ENV=development && python app.py

# Production
export FLASK_ENV=production && python app.py
```

### **Environment Check:**
```bash
# Check current environment
echo $FLASK_ENV
echo $ENVIRONMENT

# Check if in development mode
python -c "import os; print('Development:', os.environ.get('FLASK_ENV') == 'development')"
```

## 🎯 Best Practices

### **For Development:**
- Always use `FLASK_ENV=development`
- Use test Stripe keys
- Use localhost URLs
- Enable debug logging
- Use development-only features

### **For Production:**
- Always use `FLASK_ENV=production`
- Use live Stripe keys
- Use production domain
- Disable debug logging
- Hide development features

### **Testing:**
- Test in development environment first
- Test production behavior locally
- Deploy to production when ready
- Monitor production logs

## 🚨 Important Notes

### **Environment Variables Override Branch:**
- **Environment variables** control runtime behavior
- **Git branches** control code versions
- You can run production code in development mode
- You can run development code in production mode

### **Current Setup:**
- **Production server**: Uses `main` branch + production environment
- **Local development**: Use any branch + development environment
- **Auto-deployment**: Only from `main` branch

### **Recommended:**
- Use `develop` branch for development
- Use `main` branch for production
- Use environment variables to control behavior
- Test both environments locally before deploying
