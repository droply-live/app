# Development Testing Guide for Droply

## 🎯 Video Call UI Testing

### Method 1: Development Test Route (Recommended)
**Best for**: Testing video call UI without creating actual bookings

1. **Access the test route**: `/dev/test-video-call`
   - Only available in development environment
   - Creates a fake booking for testing
   - No payment required
   - No database changes

2. **Features you can test**:
   - Video call interface layout
   - Button visibility and functionality
   - Responsive design
   - Audio/video controls
   - Meeting room creation

### Method 2: Book Now Button (Development Only)
**Best for**: Testing the complete booking flow

1. **Enable in development**:
   - Set `FLASK_ENV=development` or `ENVIRONMENT=development`
   - Book Now button will appear on expert profiles
   - Creates real bookings (but with test Stripe keys)

2. **Test the full flow**:
   - Immediate booking creation
   - Payment flow (with test cards)
   - Video call interface
   - Meeting room generation

### Method 3: Scheduled Bookings
**Best for**: Testing scheduled meeting functionality

1. **Create a scheduled booking**:
   - Go to expert profile
   - Select a future date/time
   - Complete booking process
   - Test video call at scheduled time

## 🛠️ Development Environment Setup

### Environment Variables for Development
```bash
# Development Environment
FLASK_ENV=development
ENVIRONMENT=development
FLASK_DEBUG=1

# Use test Stripe keys
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_test_...

# Use localhost or ngrok
YOUR_DOMAIN=http://localhost:5001
# OR
YOUR_DOMAIN=https://your-ngrok-domain.ngrok-free.app
```

### Quick Development Setup
1. **Set development environment**:
   ```bash
   export FLASK_ENV=development
   export ENVIRONMENT=development
   export FLASK_DEBUG=1
   ```

2. **Start development server**:
   ```bash
   python app.py
   ```

3. **Access test features**:
   - Navigate to `/dev/test-video-call`
   - Or use the "🧪 Test Video" link in navigation

## 🧪 Testing Scenarios

### Video Call UI Testing
1. **Layout Testing**:
   - Test on different screen sizes
   - Check button visibility
   - Verify responsive design

2. **Functionality Testing**:
   - Test audio/video controls
   - Check meeting room creation
   - Verify button interactions

3. **Edge Cases**:
   - Test with poor network connection
   - Test with different browsers
   - Test mobile responsiveness

### Payment Flow Testing
1. **Test Cards** (Stripe Test Mode):
   - `4242424242424242` - Success
   - `4000000000000002` - Declined
   - `4000000000009995` - Insufficient funds

2. **Webhook Testing**:
   - Use Stripe CLI for local webhook testing
   - Test payment confirmations
   - Test refund scenarios

## 🚀 Production vs Development

### Production Environment
- ❌ Book Now button hidden
- ❌ Test video call route disabled
- ✅ Only scheduled bookings allowed
- ✅ Live Stripe keys required
- ✅ Real payment processing

### Development Environment
- ✅ Book Now button visible (for testing)
- ✅ Test video call route available
- ✅ Test Stripe keys allowed
- ✅ Debug logging enabled
- ✅ Test payment processing

## 📝 Best Practices

### For Video Call Testing
1. **Use the test route** (`/dev/test-video-call`) for UI testing
2. **Use Book Now button** for full flow testing
3. **Test on multiple devices** and browsers
4. **Check console for errors** during testing

### For Payment Testing
1. **Always use test Stripe keys** in development
2. **Test with different card scenarios**
3. **Verify webhook handling**
4. **Check database state** after payments

### For Deployment Testing
1. **Test in staging environment** first
2. **Verify environment variables** are correct
3. **Test production features** are disabled
4. **Check error handling** and logging

## 🔧 Troubleshooting

### Common Issues
1. **Book Now button not showing**:
   - Check environment variables
   - Ensure `FLASK_ENV=development`

2. **Test video call not working**:
   - Check if in development mode
   - Verify user is logged in
   - Check console for errors

3. **Payment issues**:
   - Verify Stripe keys are correct
   - Check webhook configuration
   - Test with Stripe test cards

### Debug Commands
```bash
# Check environment
echo $FLASK_ENV
echo $ENVIRONMENT

# Check Stripe configuration
python -c "import stripe; print(stripe.api_key[:10])"

# Test video call route
curl http://localhost:5001/dev/test-video-call
```

## 📚 Additional Resources

- [Stripe Testing Guide](https://stripe.com/docs/testing)
- [Daily.co API Documentation](https://docs.daily.co/)
- [Flask Development Server](https://flask.palletsprojects.com/en/2.0.x/server/)
