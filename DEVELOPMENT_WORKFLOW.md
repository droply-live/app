# Droply Development Workflow

## Branch Strategy

We use a **two-branch workflow**:

```
feature branches → develop → main → production
```

### Branches

- **`main`**: Production branch - automatically deploys to https://droply.live
- **`develop`**: Development branch - for testing and integration
- **`feature/*`**: Feature branches - for individual features/fixes

## Environment Configuration

### Key Principle
> **Same code in all branches. Different behavior via environment variables.**

### Local Development (Any Branch)

Environment controlled by `.env` file:
```bash
YOUR_DOMAIN=http://localhost:5000
FLASK_ENV=development
ENVIRONMENT=development
FLASK_DEBUG=1
STRIPE_SECRET_KEY=sk_test_...  # Test key
```

### Production (main branch on server)

Environment controlled by GitHub Actions secrets:
```bash
YOUR_DOMAIN=https://droply.live
FLASK_ENV=production
ENVIRONMENT=production
FLASK_DEBUG=0
STRIPE_SECRET_KEY=sk_live_...  # Live key
```

## Development Workflow

### 1. Starting a New Feature

```bash
# Make sure develop is up to date
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/my-feature-name

# Work on your feature
# ... make changes ...
git add .
git commit -m "Descriptive commit message"

# Push to GitHub
git push origin feature/my-feature-name
```

### 2. Merging Feature to Develop

**Option A: Via Pull Request (Recommended)**
```bash
# On GitHub:
# 1. Create Pull Request: feature/my-feature → develop
# 2. Request code review
# 3. Merge when approved
```

**Option B: Direct Merge (Faster)**
```bash
git checkout develop
git pull origin develop
git merge feature/my-feature-name
git push origin develop

# Clean up feature branch
git branch -d feature/my-feature-name
git push origin --delete feature/my-feature-name
```

### 3. Testing on Develop

```bash
git checkout develop
git pull origin develop

# Run locally with development environment
docker-compose up
# or
python app.py

# Test thoroughly
# - All new features work
# - No regressions in existing features
# - Database migrations (if any)
```

### 4. Deploying to Production

When develop is stable and ready:

```bash
# Make sure everything is up to date
git checkout main
git pull origin main

# Merge develop into main
git merge develop

# Push to trigger automatic deployment
git push origin main
```

**What happens:**
1. GitHub Actions workflow triggers
2. Deploys to production server
3. Uses production environment variables
4. Site updates at https://droply.live

### 5. Verify Production

After deployment completes (~2 minutes):
```bash
# Check deployment status
gh run list --limit 1

# Test production site
curl -I https://droply.live
```

## Important Rules

### ✅ DO
- Always work in feature branches
- Keep develop and main in sync
- Use `.env` file for local configuration
- Test on develop before merging to main
- Write descriptive commit messages
- Use Pull Requests for code review

### ❌ DON'T
- Commit `.env` file (it's in .gitignore)
- Push directly to main without testing on develop
- Merge half-finished features to develop
- Make production-specific code changes (use environment variables instead)
- Force push to main or develop
- Skip testing before deployment

## Handling Environment-Specific Code

Use environment variables, not different code in branches:

**❌ Bad: Different code in branches**
```python
# In develop branch
DOMAIN = "http://localhost:5000"

# In main branch  
DOMAIN = "https://droply.live"
```

**✅ Good: Same code, different environment**
```python
# Same code in all branches
DOMAIN = os.getenv('YOUR_DOMAIN')

# .env file (local):
YOUR_DOMAIN=http://localhost:5000

# GitHub Actions (production):
YOUR_DOMAIN=https://droply.live
```

## Troubleshooting

### "My changes aren't showing in production"

1. Check if deployment succeeded:
   ```bash
   gh run list --limit 1
   ```

2. Verify you merged develop to main:
   ```bash
   git log main --oneline -5
   ```

3. Check the production container:
   ```bash
   ssh -i ~/.ssh/droply_key root@142.93.75.62 "docker ps"
   ```

### "Merge conflict between develop and main"

```bash
git checkout develop
git merge main  # Resolve conflicts here first
git push origin develop

# Then merge to main
git checkout main
git merge develop  # Should be clean now
git push origin main
```

### "I need to rollback production"

```bash
# Find the last good commit
git log main --oneline -10

# Create a new branch from that commit
git checkout -b hotfix/rollback <commit-hash>

# Merge to main
git checkout main
git merge hotfix/rollback
git push origin main  # Deploys the rollback
```

## Quick Reference

```bash
# Feature work
git checkout develop
git checkout -b feature/name
# ... work ...
git push origin feature/name

# Merge to develop
git checkout develop
git merge feature/name
git push origin develop

# Deploy to production
git checkout main
git merge develop
git push origin main  # 🚀 Auto-deploys!
```

## Questions?

If you're unsure about any step:
1. Ask the team
2. Create a Pull Request (safer than direct merge)
3. Test on develop first
4. Check the deployment logs on GitHub Actions

