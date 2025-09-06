# Video Calling Setup Guide

This guide explains how to set up video calling functionality in Droply, similar to Intro.co's expert sessions.

## Overview

Droply now supports video calling for expert-client meetings with two options:

1. **Daily.co Integration** (Recommended) - Full-featured video calling with chat, recording, and screen sharing
2. **Simple WebRTC** (Fallback) - Basic video calling using browser WebRTC

## Option 1: Daily.co Integration (Recommended)

### Setup Steps

1. **Sign up for Daily.co**
   - Go to [daily.co](https://daily.co)
   - Create a free account
   - Get your API key from the dashboard

2. **Configure Environment Variables**
   ```bash
   # Add to your .env file
   DAILY_API_KEY=your_daily_api_key_here
   ```

3. **Features Available with Daily.co**
   - High-quality video/audio
   - Built-in chat
   - Screen sharing
   - Meeting recording
   - Participant management
   - Meeting analytics

### Daily.co Pricing
- **Free Tier**: 40 minutes per day, 4 participants max
- **Pro Plan**: $10/month - 1,000 minutes per day, 10 participants max
- **Business Plan**: $25/month - 5,000 minutes per day, 20 participants max

## Option 2: Simple WebRTC (Fallback)

If you don't configure Daily.co, the system automatically falls back to simple WebRTC video calling.

### Features
- Basic video/audio calling
- Mute/unmute controls
- Video on/off controls
- Connection status indicator

### Limitations
- No built-in chat
- No screen sharing
- No recording
- Limited to 2 participants
- Requires both users to be online simultaneously

## Database Migration

Run the migration script to add video call fields to your database:

```bash
python migrate_video_fields.py
```

## Testing the Video Calling

1. **Create a test booking** between two users
2. **Wait for the meeting time** (or use a booking in the past for testing)
3. **Click "Join Meeting"** from the bookings page
4. **Allow camera/microphone permissions** when prompted

## Meeting Flow

### For Experts
1. Receive booking confirmation
2. Click "Join Meeting" when it's time
3. Start the meeting (optional)
4. Conduct the session
5. End the meeting when finished

### For Clients
1. Book a session with an expert
2. Wait for confirmation
3. Click "Join Meeting" when it's time
4. Participate in the video call
5. Leave when the session ends

## Meeting Controls

### Available Controls
- **Mute/Unmute**: Toggle microphone
- **Video On/Off**: Toggle camera
- **Chat**: Send messages (Daily.co only)
- **Screen Share**: Share screen (Daily.co only)
- **End Meeting**: Leave the call

### Meeting Status
- **Pending**: Waiting for expert approval
- **Confirmed**: Booking confirmed, waiting for meeting time
- **Ongoing**: Meeting is currently happening
- **Completed**: Meeting has ended

## Security Features

- **Meeting Rooms**: Each booking gets a unique, private meeting room
- **Authentication**: Only booking participants can join
- **Time Restrictions**: Meetings can only be joined within 5 minutes of start time
- **Automatic Cleanup**: Meeting rooms expire after the session

## Troubleshooting

### Common Issues

1. **"Failed to access camera/microphone"**
   - Check browser permissions
   - Ensure camera/microphone are not in use by other applications

2. **"Meeting not available for joining"**
   - Check if it's within the allowed time window (5 minutes before start)
   - Verify the booking status is "confirmed"

3. **"Error creating meeting room"**
   - Check Daily.co API key configuration
   - Verify internet connection

4. **Poor video quality**
   - Check internet connection speed
   - Close other bandwidth-heavy applications
   - Try reducing video quality in browser settings

### Browser Compatibility

**Supported Browsers:**
- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+

**Mobile Support:**
- iOS Safari 11+
- Chrome Mobile 60+
- Firefox Mobile 55+

## Production Deployment

### Environment Variables
```bash
# Required for Daily.co
DAILY_API_KEY=your_production_api_key

# Optional: Custom domain for Daily.co
DAILY_DOMAIN=your-domain.daily.co
```

### SSL Requirements
Video calling requires HTTPS in production. Ensure your domain has a valid SSL certificate.

### Scaling Considerations
- Daily.co handles video infrastructure scaling
- Consider rate limiting for meeting creation
- Monitor API usage and costs

## Support

For issues with:
- **Daily.co**: Contact [Daily.co support](https://daily.co/support)
- **Droply Video Calling**: Check this documentation or create an issue

## Future Enhancements

Planned features:
- Meeting recordings storage
- Advanced analytics
- Custom branding
- Integration with calendar systems
- Mobile app support 