#!/usr/bin/env python3

import sqlite3
from datetime import datetime, timezone, timedelta

# Configure timezone to Eastern Time
EASTERN_TIMEZONE = timezone(timedelta(hours=-4))

# Connect to the database
db_path = 'instance/droply.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get the latest booking and user info
cursor.execute('''
    SELECT b.id, b.user_id, b.expert_id, b.start_time, b.end_time, b.status,
           u1.username as client_username, u2.username as expert_username
    FROM booking b
    JOIN user u1 ON b.user_id = u1.id
    JOIN user u2 ON b.expert_id = u2.id
    ORDER BY b.id DESC LIMIT 1
''')
booking = cursor.fetchone()

if booking:
    booking_id, user_id, expert_id, start_time, end_time, status, client_username, expert_username = booking
    
    print(f"Latest Booking Details:")
    print(f"Booking ID: {booking_id}")
    print(f"Client ID: {user_id} (username: {client_username})")
    print(f"Expert ID: {expert_id} (username: {expert_username})")
    print(f"Status: {status}")
    print(f"Start time: {start_time}")
    print(f"End time: {end_time}")
    
    # Check if meeting is joinable
    now = datetime.now(EASTERN_TIMEZONE)
    start_dt = datetime.fromisoformat(start_time)
    end_dt = datetime.fromisoformat(end_time)
    
    start_dt_aware = start_dt.replace(tzinfo=EASTERN_TIMEZONE)
    end_dt_aware = end_dt.replace(tzinfo=EASTERN_TIMEZONE)
    
    can_join = (start_dt_aware - timedelta(minutes=5)) <= now <= end_dt_aware
    is_ongoing = start_dt_aware <= now <= end_dt_aware
    
    print(f"\nMeeting Status:")
    print(f"Current time: {now}")
    print(f"Can join meeting: {can_join}")
    print(f"Is ongoing: {is_ongoing}")
    
    print(f"\nTo join this meeting, you need to be logged in as:")
    print(f"- Client: {client_username} (ID: {user_id})")
    print(f"- Expert: {expert_username} (ID: {expert_id})")

conn.close() 