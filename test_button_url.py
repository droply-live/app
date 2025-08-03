#!/usr/bin/env python3

from flask import Flask, url_for
from datetime import datetime, timezone, timedelta

# Configure timezone to Eastern Time
EASTERN_TIMEZONE = timezone(timedelta(hours=-4))

# Create a minimal Flask app for testing URL generation
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test'

with app.app_context():
    # Test the URL generation
    booking_id = 32
    url = url_for('join_meeting', booking_id=booking_id)
    print(f"Join Meeting URL for booking {booking_id}: {url}")
    print(f"Full URL: https://c21fc370d58a.ngrok-free.app{url}")
    
    # Test the current time vs meeting time
    now = datetime.now(EASTERN_TIMEZONE)
    print(f"Current time: {now}")
    
    # Simulate the time check from the route
    from datetime import timedelta
    meeting_time = datetime(2025, 8, 2, 14, 23, 23)  # From the booking
    meeting_time = meeting_time.replace(tzinfo=EASTERN_TIMEZONE)
    time_diff = abs((meeting_time - now).total_seconds() / 60)
    print(f"Meeting time: {meeting_time}")
    print(f"Time difference: {time_diff:.1f} minutes")
    print(f"Within 15 minutes: {time_diff <= 15}") 