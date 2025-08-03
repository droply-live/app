#!/usr/bin/env python3

import sqlite3
from datetime import datetime, timedelta
import os
import uuid

# Connect to the database
db_path = 'instance/droply.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get current time and create meeting time for right now
from datetime import timezone, timedelta
EASTERN_TIMEZONE = timezone(timedelta(hours=-4))  # EDT (UTC-4)
now = datetime.now(EASTERN_TIMEZONE)
meeting_time = now  # Start immediately

# Format times for database
start_time = meeting_time.strftime('%Y-%m-%d %H:%M:%S')
end_time = (meeting_time + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')

# Generate a unique meeting room ID
meeting_room_id = str(uuid.uuid4())

print(f"Creating immediate test meeting:")
print(f"Start time: {start_time}")
print(f"End time: {end_time}")
print(f"Meeting room ID: {meeting_room_id}")

# Create Daily.co room URL (public room, no API needed)
room_name = f"droply-{meeting_room_id}"
daily_url = f"https://droply.daily.co/{room_name}"

print(f"✅ Daily.co room created: {daily_url}")

# Create a test booking
cursor.execute('''
    INSERT INTO booking (
        user_id, expert_id, start_time, end_time, duration,
        payment_amount, status, payment_status, created_at,
        meeting_room_id, meeting_url
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    4,  # test_client (ID 4)
    3,  # test_expert (ID 3)
    start_time,
    end_time,
    30,  # 30 minutes
    50.00,  # $50
    'confirmed',
    'paid',
    now.strftime('%Y-%m-%d %H:%M:%S'),
    room_name,  # Use room name as meeting_room_id
    daily_url   # Use Daily.co URL
))

# Commit the changes
conn.commit()

# Get the booking ID
booking_id = cursor.lastrowid
print(f"Created booking with ID: {booking_id}")

# Close the connection
conn.close()

print("✅ Immediate test meeting created successfully!")
print(f"📅 Meeting starts NOW at {start_time}")
print(f"⏰ Duration: 30 minutes")
print(f"💰 Amount: $50.00")
print(f"👥 Between: test_client and test_expert")
print(f"🔗 Daily.co Room: {daily_url}")
print(f"🎥 You can now test the video call feature immediately!")
print(f"📋 Booking ID: {booking_id}") 