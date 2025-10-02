# Stripe Production Setup Guide

## Overview
This guide helps you move from Stripe sandbox/test mode to production mode.

## Step 1: Stripe Dashboard Configuration

### Switch to Live Mode
1. Go to your Stripe Dashboard
2. Click the purple "Switch to live account" button
3. Complete any required verification steps

### Get Live API Keys
1. Go to Developers → API Keys
2. Copy your **Live Secret Key** (starts with `sk_live_`)
3. Copy your **Live Publishable Key** (starts with `pk_live_`)

### Configure Live Webhooks
1. Go to Developers → Webhooks
2. Add endpoint: `https://droply.live/webhook/stripe`
3. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `checkout.session.completed`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
4. Copy the **Webhook Signing Secret**

## Step 2: Update GitHub Secrets

In your GitHub repository:
1. Go to Settings → Secrets and variables → Actions
2. Update these secrets:
   - `STRIPE_SECRET_KEY` → Your live secret key (`sk_live_...`)
   - `STRIPE_WEBHOOK_SECRET` → Your live webhook secret

## Step 3: Environment Configuration

### Production Environment Variables
```bash
FLASK_ENV=production
ENVIRONMENT=production
FLASK_DEBUG=0
STRIPE_SECRET_KEY=sk_live_your_live_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_live_webhook_secret_here
```

### Local Development (Keep Test Mode)
```bash
FLASK_ENV=development
ENVIRONMENT=development
FLASK_DEBUG=1
STRIPE_SECRET_KEY=sk_test_your_test_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_test_webhook_secret_here
```

## Step 4: Testing Strategy

### Development/Testing Environment
- ✅ Use **Sandbox/Test mode** with test keys
- ✅ Use test credit cards (4242 4242 4242 4242, etc.)
- ✅ No real money charged
- ✅ Test webhook endpoints locally

### Production Environment
- ⚠️ Use **Live mode** with live keys
- ⚠️ **Real credit cards will be charged real money**
- ⚠️ **No test cards work in live mode**
- ⚠️ Live webhook endpoints required

## Step 5: Recommended Setup

### Option A: Separate Environments
- **Development**: Keep using test mode
- **Production**: Use live mode
- **Staging**: Use test mode (optional)

### Option B: Environment-Specific Configuration
Your code already has environment validation that will:
- ✅ Prevent test keys in production
- ✅ Warn about live keys in development
- ✅ Validate key formats

## Step 6: Testing in Production

### Before Going Live
1. Test thoroughly in sandbox mode
2. Use Stripe's test cards to verify all flows
3. Test webhook handling
4. Verify error handling

### After Going Live
1. Start with small transactions
2. Monitor Stripe Dashboard for issues
3. Check webhook delivery logs
4. Monitor your application logs

## Important Notes

### ⚠️ Live Mode Warnings
- **Real money will be charged** for all transactions
- **Test credit cards do NOT work** in live mode
- **Webhook endpoints must be publicly accessible**
- **SSL/HTTPS required** for webhooks

### 🔒 Security Considerations
- Never commit live keys to code
- Use environment variables only
- Rotate keys regularly
- Monitor for unauthorized usage

## Troubleshooting

### Common Issues
1. **Webhook not receiving events**: Check endpoint URL and SSL
2. **Invalid API key**: Verify key format and environment
3. **Payment failures**: Check card details and Stripe logs
4. **Environment mismatch**: Verify FLASK_ENV and ENVIRONMENT variables

### Validation
Your code includes automatic validation:
```python
def validate_stripe_environment():
    if is_production_environment():
        if stripe.api_key.startswith('sk_test_'):
            raise ValueError("❌ PRODUCTION ERROR: Test Stripe key detected!")
```

This will prevent accidental use of test keys in production.
