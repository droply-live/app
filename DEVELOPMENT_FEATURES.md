# Development-Only Features Guide

## Overview

This guide explains how to add features that should **only appear in development** while keeping the same code in all branches.

## The Golden Rule

> **Same code in all branches. Different behavior via environment variables.**

✅ Code goes to both main and develop  
✅ Features appear/disappear based on environment  
❌ Never create different code versions in different branches

## Environment Variables

### Available Variables

```python
# In templates
config.get('FLASK_ENV')        # 'development' or 'production'
config.get('ENVIRONMENT')       # 'development' or 'production'
config.get('FLASK_DEBUG')       # '1' or '0'

# In Python code
os.getenv('FLASK_ENV')
os.getenv('ENVIRONMENT')
os.getenv('FLASK_DEBUG')
```

### Values by Environment

| Environment | FLASK_ENV | ENVIRONMENT | FLASK_DEBUG |
|-------------|-----------|-------------|-------------|
| Local Dev   | development | development | 1 |
| Production  | production | production | 0 |

## Examples

### 1. Hide UI Element in Production

**Template (Jinja2):**
```jinja
{% if config.get('FLASK_ENV') == 'development' %}
<div class="dev-only-feature">
    <button>Debug Mode</button>
    <p>This only shows in development</p>
</div>
{% endif %}
```

**Real Example (Book Now button):**
```jinja
<!-- File: templates/user_booking_times.html, Line 75 -->
{% if expert.is_available and config.get('FLASK_ENV') == 'development' %}
<div class="book-now-section">
    <a href="{{ url_for('book_immediate_meeting', username=expert.username) }}" 
       class="book-now-btn">
        <div class="book-now-title">Book Now (Dev Only)</div>
    </a>
</div>
{% endif %}
```

### 2. Development-Only Route

**Python:**
```python
# File: routes.py

@app.route('/dev/test-payment')
def dev_test_payment():
    """Development-only route for testing payments"""
    if os.getenv('FLASK_ENV') != 'development':
        abort(404)  # Hide in production
    
    # Test payment logic here
    return render_template('dev/test_payment.html')
```

### 3. Extra Debug Logging

**Python:**
```python
@app.route('/booking/confirm/<int:booking_id>')
def confirm_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Extra logging only in development
    if os.getenv('FLASK_ENV') == 'development':
        print(f"DEBUG: Booking details: {booking.__dict__}")
        print(f"DEBUG: User: {current_user.email}")
    
    # Regular code continues...
    return render_template('confirm.html', booking=booking)
```

### 4. Development Tools Panel

**Template:**
```jinja
{% if config.get('FLASK_ENV') == 'development' %}
<div class="dev-tools-panel" style="position: fixed; bottom: 0; right: 0; background: #f0f0f0; padding: 10px;">
    <h4>Dev Tools</h4>
    <ul>
        <li>User: {{ current_user.email }}</li>
        <li>Environment: {{ config.get('ENVIRONMENT') }}</li>
        <li><a href="/dev/clear-cache">Clear Cache</a></li>
        <li><a href="/dev/test-data">Load Test Data</a></li>
    </ul>
</div>
{% endif %}
```

### 5. Skip Payment in Development

**Python:**
```python
@app.route('/checkout/<int:booking_id>')
def checkout(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # In development, allow skipping payment
    if os.getenv('FLASK_ENV') == 'development' and request.args.get('skip_payment'):
        booking.payment_status = 'paid'
        db.session.commit()
        return redirect(url_for('booking_success', booking_id=booking.id))
    
    # Normal Stripe checkout
    return redirect(stripe_checkout_url)
```

### 6. Mock External Services

**Python:**
```python
def send_email(to, subject, body):
    """Send email - mocked in development"""
    if os.getenv('FLASK_ENV') == 'development':
        print(f"📧 MOCK EMAIL TO {to}")
        print(f"   Subject: {subject}")
        print(f"   Body: {body}")
        return True
    
    # Real email sending in production
    return sendgrid.send(to, subject, body)
```

### 7. Conditional Styling

**Template:**
```jinja
<div class="user-profile 
    {% if config.get('FLASK_ENV') == 'development' %}dev-mode{% endif %}">
    <!-- Profile content -->
</div>
```

**CSS:**
```css
/* Development-specific styling */
.dev-mode {
    border: 3px solid orange;
}

.dev-mode::before {
    content: "DEV MODE";
    background: orange;
    color: white;
    padding: 5px;
}
```

## Best Practices

### ✅ DO

1. **Use environment variables** for all development-only features
2. **Keep the same code** in all branches
3. **Label clearly** with comments like `<!-- Dev Only -->` or `# Development only`
4. **Test in both environments** before deploying
5. **Document** your development-only features

### ❌ DON'T

1. **Create different code** in develop vs main branches
2. **Remove features** from main branch manually
3. **Hardcode** environment checks without variables
4. **Forget to test** in production mode locally
5. **Leave debug statements** that run in production

## Testing Development Features Locally

### Test Development Mode (Default)
```bash
# Uses .env file with FLASK_ENV=development
python app.py
# or
docker-compose up
```

### Test Production Mode Locally
```bash
# Temporarily set production environment
export FLASK_ENV=production
export ENVIRONMENT=production
export FLASK_DEBUG=0
python app.py

# Or in docker-compose
docker run -e FLASK_ENV=production -e ENVIRONMENT=production ...
```

## Common Patterns

### Pattern 1: Feature Toggle
```python
FEATURE_ENABLED = os.getenv('FLASK_ENV') == 'development'

if FEATURE_ENABLED:
    # Feature code
```

### Pattern 2: Conditional Import
```python
if os.getenv('FLASK_ENV') == 'development':
    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)
```

### Pattern 3: Configuration Override
```python
if os.getenv('FLASK_ENV') == 'development':
    app.config['SQLALCHEMY_ECHO'] = True  # Log all SQL queries
    app.config['TESTING'] = True
```

## Checklist for New Development Features

Before adding a development-only feature:

- [ ] Will this code exist in both branches? (Answer: Yes)
- [ ] Am I using environment variables to control behavior? (Answer: Yes)
- [ ] Have I tested in both development and production mode locally?
- [ ] Have I documented what the feature does?
- [ ] Have I labeled it clearly as "Dev Only"?
- [ ] Will this cause any security issues if accidentally visible in production?

## Example Workflow

```bash
# 1. Add feature to develop branch
git checkout develop
# ... add development-only feature with environment check ...
git commit -m "Add debug panel (dev only)"

# 2. Test locally in development mode
python app.py
# Feature should appear ✅

# 3. Test locally in production mode
export FLASK_ENV=production
python app.py
# Feature should be hidden ✅

# 4. Merge to main
git checkout main
git merge develop
git push origin main

# 5. Feature deploys to production but stays hidden!
# Same code, different behavior ✅
```

## Troubleshooting

### "My dev feature is showing in production!"

Check:
1. Is `FLASK_ENV=production` set in GitHub Actions?
2. Did you use the correct environment variable check?
3. Did you clear the cache/restart the server?

```bash
# Check production environment
ssh -i ~/.ssh/droply_key root@142.93.75.62 \
  "docker exec droply-web-1 printenv FLASK_ENV"
```

### "My feature isn't showing in development!"

Check:
1. Is `.env` file present with `FLASK_ENV=development`?
2. Did you restart the development server?
3. Check browser cache (hard refresh: Ctrl+Shift+R)

```bash
# Verify local environment
cat .env | grep FLASK_ENV
```

## Summary

✅ **Same code, different behavior**  
✅ **Environment variables control visibility**  
✅ **No branch divergence**  
✅ **Easy to test both modes locally**  
✅ **Clean, maintainable approach**

Your "Book Now" button is already following this pattern perfectly! 🎉

