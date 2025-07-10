# Stripe Connect Setup Guide

This guide explains how to set up Stripe Connect to enable experts to receive payouts from bookings.

## Overview

Stripe Connect allows your platform to collect payments and automatically distribute funds to experts (your service providers). This implementation uses **Stripe Connect Express** accounts, which provide a streamlined onboarding experience for experts.

## How It Works

1. **Client pays** → Money goes to your Stripe account
2. **Expert completes onboarding** → Creates Stripe Connect Express account
3. **Payment confirmed** → Expert's earnings are calculated (minus platform fees)
4. **Expert requests payout** → Money transferred to expert's bank account

## Setup Steps

### 1. Stripe Dashboard Configuration

#### Enable Stripe Connect
1. Log into your [Stripe Dashboard](https://dashboard.stripe.com)
2. Go to **Developers** → **Connect settings**
3. Enable **Connect** if not already enabled
4. Note your **Connect Client ID** (you'll need this later)

#### Configure Connect Settings
1. Go to **Connect** → **Settings**
2. Set your **Business name** and **Support email**
3. Configure **Branding** (logo, colors)
4. Set **Payout schedule** (recommended: weekly)
5. Configure **Payout methods** (bank accounts)

#### Set Up Webhooks
1. Go to **Developers** → **Webhooks**
2. Add endpoint: `https://yourdomain.com/stripe/webhook`
3. Select these events:
   - `checkout.session.completed`
   - `payout.paid`
   - `payout.failed`
4. Copy the **Webhook signing secret**

### 2. Environment Variables

Add these to your environment:

```bash
# Stripe Connect
STRIPE_SECRET_KEY=sk_live_...  # Your main Stripe secret key
STRIPE_WEBHOOK_SECRET=whsec_...  # Webhook signing secret
STRIPE_CONNECT_CLIENT_ID=ca_...  # Connect client ID (optional for Express)

# Your domain
YOUR_DOMAIN=https://yourdomain.com
```

### 3. Database Migration

Run the migration script to add Stripe Connect fields:

```bash
python migrate_stripe_connect.py
```

This will add:
- `stripe_account_id` - Expert's Stripe Connect account ID
- `stripe_account_status` - Account status (pending, active, etc.)
- `payout_enabled` - Whether payouts are enabled
- `total_earnings` - Total earnings before platform fees
- `total_payouts` - Total amount paid out
- `pending_balance` - Current pending balance

### 4. Test the Implementation

#### Test Expert Onboarding
1. Create a test expert account
2. Go to `/expert/onboard-stripe`
3. Complete the Stripe Connect onboarding
4. Verify account status updates

#### Test Payment Flow
1. Create a test booking with payment
2. Complete payment via Stripe Checkout
3. Verify earnings are calculated correctly
4. Test payout request functionality

## Expert Onboarding Flow

### 1. Expert Dashboard
- Experts see their earnings overview
- Pending balance and payout status
- Recent bookings and payout history

### 2. Stripe Connect Onboarding
- Expert clicks "Set Up Payouts"
- Redirected to Stripe's secure onboarding
- Provides business information and bank details
- Returns to platform with active account

### 3. Payout Process
- Expert can request payouts when balance > $0
- Payouts processed via Stripe to expert's bank account
- Status tracked in database and dashboard

## Platform Fee Structure

The current implementation uses:
- **10% platform fee** on all transactions
- **Minimum $5 platform fee** per transaction
- **90% goes to expert** (after platform fee)

Example:
- Session price: $100
- Platform fee: $10 (10%)
- Expert receives: $90

## Security Considerations

### Data Protection
- Never store bank account details in your database
- All sensitive data handled by Stripe
- Use HTTPS for all webhook endpoints

### Compliance
- Stripe handles PCI DSS compliance
- Experts must provide valid business information
- Follow local tax and business regulations

### Fraud Prevention
- Monitor for suspicious payment patterns
- Implement booking limits and verification
- Use Stripe's built-in fraud detection

## Troubleshooting

### Common Issues

#### Expert Can't Complete Onboarding
- Check Stripe Connect settings in dashboard
- Verify webhook endpoints are working
- Check for error messages in Stripe logs

#### Payouts Not Processing
- Verify expert's bank account is verified
- Check payout schedule settings
- Monitor for failed payout webhooks

#### Webhook Errors
- Verify webhook secret is correct
- Check endpoint URL is accessible
- Monitor webhook delivery in Stripe dashboard

### Debug Mode

Enable debug logging:

```python
import stripe
stripe.api_key = 'your_secret_key'
stripe.log = 'debug'  # Enable debug logging
```

## Production Checklist

Before going live:

- [ ] Stripe Connect enabled in dashboard
- [ ] Webhooks configured and tested
- [ ] Environment variables set
- [ ] Database migration completed
- [ ] Expert onboarding flow tested
- [ ] Payment flow tested end-to-end
- [ ] Payout process tested
- [ ] Error handling implemented
- [ ] Monitoring and logging set up
- [ ] Legal compliance verified

## Support Resources

- [Stripe Connect Documentation](https://stripe.com/docs/connect)
- [Stripe Connect API Reference](https://stripe.com/docs/api/connect)
- [Stripe Support](https://support.stripe.com)
- [Connect Onboarding Guide](https://stripe.com/docs/connect/onboarding)

## Cost Structure

### Stripe Fees
- **Standard processing fees**: 2.9% + 30¢ per transaction
- **Connect fees**: Additional 0.25% for Express accounts
- **Payout fees**: $0.25 per payout (US bank accounts)

### Your Platform Fees
- **10% platform fee** (configurable)
- **Minimum $5 per transaction**

### Example Calculation
- Client pays: $100
- Stripe fee: $3.20 (2.9% + 30¢)
- Platform fee: $10 (10%)
- Expert receives: $86.80
- Your profit: $6.80 (after Stripe fees)

## Next Steps

1. **Set up Stripe Connect** in your dashboard
2. **Run the migration script**
3. **Test the expert onboarding flow**
4. **Configure webhooks**
5. **Go live with a small group of experts**
6. **Monitor and optimize**

This implementation provides a complete payout solution for your booking platform while maintaining security and compliance standards. 