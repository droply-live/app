# Quick Daily.co Setup for Real Video Calls

## Step 1: Get Daily.co API Key (Free)
1. Go to [daily.co](https://daily.co)
2. Sign up for a free account
3. Go to your dashboard
4. Copy your API key

## Step 2: Add to Environment
Add this to your `.env` file:
```bash
DAILY_API_KEY=your_daily_api_key_here
```

## Step 3: Restart Docker
```bash
docker-compose down
docker-compose up -d
```

## That's It! 
- Your video calls will now use Daily.co's infrastructure
- Real peer-to-peer connections between participants
- Built-in chat, screen sharing, and recording
- No more simulation mode

## Free Tier Limits:
- 40 minutes per day
- 4 participants max
- Perfect for testing! 