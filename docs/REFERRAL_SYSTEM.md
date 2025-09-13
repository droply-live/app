# Referral System Documentation

## Overview

The Droply referral system allows users to earn $10 for each person they refer who signs up and makes their first booking. This system is designed to encourage user growth through word-of-mouth marketing.

## How It Works

### 1. Referral Link Generation
- Each user gets a unique 8-character alphanumeric referral code
- Referral links are in the format: `https://yourdomain.com/?ref=ABC12345`
- Users can access their referral link in the Account > Referrals tab

### 2. Referral Tracking
- When someone visits a referral link, the referral code is stored in their session
- During registration, the system checks for referral codes and creates referral relationships
- Referral relationships are tracked in the `Referral` table

### 3. Reward Processing
- Rewards are triggered when a referred user makes their **first paid booking**
- The referrer earns $10 for each successful referral
- Rewards are tracked in the `ReferralReward` table

## Database Schema

### New Tables

#### Referral
- `id`: Primary key
- `referrer_id`: User who made the referral
- `referred_user_id`: User who was referred
- `referral_code`: The referral code used
- `created_at`: When the referral was created
- `status`: pending, completed, expired

#### ReferralReward
- `id`: Primary key
- `referrer_id`: User who earned the reward
- `referred_user_id`: User who triggered the reward
- `booking_id`: Booking that triggered the reward
- `reward_amount`: Reward amount in dollars ($10)
- `reward_type`: Type of reward (booking, signup, etc.)
- `status`: pending, paid, cancelled
- `created_at`: When the reward was created
- `paid_at`: When the reward was actually paid

### Updated User Model
- `referral_code`: User's unique referral code
- `referred_by`: ID of user who referred this user
- `total_referral_earnings`: Total earnings from referrals
- `referral_count`: Number of successful referrals

## API Endpoints

### GET /api/referrals/history
Returns referral history for the current user.

**Response:**
```json
{
  "success": true,
  "referrals": [
    {
      "id": 1,
      "referred_user_name": "John Doe",
      "created_at": "2024-01-15T10:30:00",
      "status": "completed",
      "reward_amount": 10.0
    }
  ]
}
```

### POST /api/referrals/generate-code
Generates a new referral code for the current user.

**Response:**
```json
{
  "success": true,
  "referral_code": "ABC12345",
  "referral_link": "https://yourdomain.com/?ref=ABC12345"
}
```

### GET /api/referrals/stats
Returns referral statistics for the current user.

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_referrals": 5,
    "completed_referrals": 3,
    "total_earnings": 30.0,
    "pending_earnings": 0.0
  }
}
```

## User Interface

### Referrals Tab
The referrals tab in the Account page includes:

1. **Referral Statistics**
   - Total referrals count
   - Total earnings
   - Reward amount per referral ($10)

2. **Referral Link Management**
   - Display current referral link
   - Copy to clipboard functionality
   - Share via email and social media
   - Generate new referral code

3. **Referral History**
   - List of all referrals made
   - Status of each referral
   - Reward amounts earned

4. **How It Works Section**
   - Step-by-step explanation of the referral process

## Implementation Details

### Referral Code Generation
- 8-character alphanumeric codes (uppercase letters and numbers)
- Codes are generated using Python's `secrets` module for security
- Uniqueness is enforced at the database level

### Referral Tracking Flow
1. User visits referral link: `/?ref=ABC12345`
2. Referral code stored in session
3. During registration, referral relationship is created
4. When referred user makes first booking, reward is processed

### Reward Processing
- Rewards are processed in the booking success flow
- Only the first paid booking triggers a reward
- Duplicate rewards are prevented by checking existing records

## Security Considerations

- Referral codes are generated using cryptographically secure random generation
- Users cannot refer themselves
- Duplicate referrals are prevented
- Referral relationships are immutable once created

## Testing

Run the test script to verify the referral system:

```bash
python test_referrals.py
```

## Migration

To add referral codes to existing users, run:

```bash
python migrate_referrals.py
```

## Configuration

### Reward Amount
The reward amount is currently set to $10.00 and can be modified in:
- `routes.py` - `process_referral_reward_for_booking()` function
- `routes.py` - `/api/referrals/process-reward` endpoint

### Referral Code Length
The referral code length is set to 8 characters in the `User.generate_referral_code()` method.

## Future Enhancements

1. **Tiered Rewards**: Different reward amounts based on referral count
2. **Bonus Rewards**: Additional rewards for reaching milestones
3. **Referral Analytics**: Detailed analytics and reporting
4. **Email Notifications**: Notify users when they earn rewards
5. **Payout Integration**: Integrate with existing payout system for referral rewards

