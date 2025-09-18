# Production Deployment Guide for Droply

## Prerequisites

1. **Domain Setup**: Ensure `droply.live` is pointing to your server
2. **SSL Certificate**: HTTPS must be configured (Let's Encrypt recommended)
3. **Server Access**: SSH access to your production server

## Step 1: Google OAuth Configuration

### Update Google Cloud Console:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services > Credentials**
3. Find your OAuth 2.0 Client ID: `192147572169-6hnr304rpl76u1l7lbsa6q0eu54aoihb.apps.googleusercontent.com`
4. Click **Edit**
5. Add these **Authorized redirect URIs**:
   - `https://droply.live/auth/google/callback`
   - `https://droply.live/auth/google/callback?redirect_to=availability`
6. **Save** the changes

## Step 2: Environment Variables

Set these environment variables on your production server:

```bash
# Production Environment
export FLASK_ENV=production
export ENVIRONMENT=production
export FLASK_DEBUG=0
export YOUR_DOMAIN=https://droply.live

# Security
export SECRET_KEY="your-super-secure-secret-key-here"

# Google OAuth
export GOOGLE_CLIENT_ID=192147572169-6hnr304rpl76u1l7lbsa6q0eu54aoihb.apps.googleusercontent.com
export GOOGLE_CLIENT_SECRET=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

# Stripe (replace with live keys for production)
export STRIPE_SECRET_KEY=sk_test_51Ra5LVPJHdGqB6baQmgVOqBxWJYwdgE3nqtjAibCmmNnZ8K2uzFFOmPBszfn5SIvKUyRWFu6rkxnCZbQcSIWfb2G00BoBogDUM

# Daily.co
export DAILY_API_KEY=6423a326f903299ed0f7ca08253be671e65f7527491adebb656d8a18fc24483f
```

## Step 3: Deploy to Production

### Option A: Using the deployment script
```bash
./deploy.sh
```

### Option B: Manual deployment
```bash
# Build production image
docker-compose -f docker-compose.prod.yml build

# Stop existing containers
docker-compose -f docker-compose.prod.yml down

# Start production container
docker-compose -f docker-compose.prod.yml up -d
```

## Step 4: Verify Deployment

1. **Check if the app is running**:
   ```bash
   curl -I https://droply.live
   ```

2. **Test Google OAuth**:
   - Go to `https://droply.live/login`
   - Click "Sign in with Google"
   - Verify the redirect URI matches what you configured in Google Cloud Console

3. **Check logs**:
   ```bash
   docker-compose -f docker-compose.prod.yml logs -f
   ```

## Step 5: Production Checklist

- [ ] Domain `droply.live` is configured with HTTPS
- [ ] Google OAuth redirect URIs are updated
- [ ] Environment variables are set
- [ ] Application is running and accessible
- [ ] Google OAuth flow works
- [ ] Database is properly configured
- [ ] SSL certificate is valid
- [ ] Stripe keys are updated to live keys (if needed)

## Troubleshooting

### Google OAuth Issues:
- Verify redirect URIs in Google Cloud Console match exactly
- Check that HTTPS is properly configured
- Ensure the domain is accessible

### Application Issues:
- Check Docker logs: `docker-compose -f docker-compose.prod.yml logs -f`
- Verify environment variables are set correctly
- Ensure the database is accessible

### SSL/HTTPS Issues:
- Verify SSL certificate is valid
- Check that the domain resolves correctly
- Ensure port 443 is open

## Security Notes

1. **Change the SECRET_KEY** to a secure random string
2. **Use live Stripe keys** for production payments
3. **Enable HTTPS only** (no HTTP redirects)
4. **Regular security updates** for dependencies
5. **Monitor logs** for suspicious activity

## Support

If you encounter issues:
1. Check the application logs
2. Verify all environment variables
3. Test the Google OAuth configuration
4. Ensure HTTPS is properly configured
