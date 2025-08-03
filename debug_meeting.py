#!/usr/bin/env python3

import sqlite3
from datetime import datetime, timezone, timedelta

# Configure timezone to Eastern Time
EASTERN_TIMEZONE = timezone(timedelta(hours=-4))

# Connect to the database
db_path = 'instance/droply.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get the latest booking
cursor.execute('SELECT id, start_time, end_time, status FROM booking ORDER BY id DESC LIMIT 1')
booking = cursor.fetchone()

if booking:
    booking_id, start_time, end_time, status = booking
    
    # Convert string to datetime (naive)
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)
    
    # Current time (timezone-aware)
    now = datetime.now(EASTERN_TIMEZONE)
    
    # Convert naive datetimes to timezone-aware for comparison
    start_dt_aware = start_dt.replace(tzinfo=EASTERN_TIMEZONE)
    end_dt_aware = end_dt.replace(tzinfo=EASTERN_TIMEZONE)
    
    print(f"Booking ID: {booking_id}")
    print(f"Status: {status}")
    print(f"Start time (naive): {start_dt}")
    print(f"End time (naive): {end_dt}")
    print(f"Current time: {now}")
    print(f"Start time (aware): {start_dt_aware}")
    print(f"End time (aware): {end_dt_aware}")
    
    # Test can_join_meeting logic
    time_diff = abs((start_dt_aware - now).total_seconds() / 60)
    print(f"Time difference from start: {time_diff:.1f} minutes")
    
    # Check if within 5 minutes before start or during meeting
    can_join = (start_dt_aware - timedelta(minutes=5)) <= now <= end_dt_aware
    print(f"Can join meeting: {can_join}")
    
    # Check if meeting is ongoing
    is_ongoing = start_dt_aware <= now <= end_dt_aware
    print(f"Is ongoing: {is_ongoing}")
    
    # Check if meeting is upcoming
    is_upcoming = start_dt_aware > now
    print(f"Is upcoming: {is_upcoming}")

conn.close() 