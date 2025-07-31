#!/usr/bin/env python3

import sqlite3
from datetime import datetime, timedelta
import os

# Connect to the database
db_path = 'instance/droply.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get current time and create meeting time 5 minutes from now
now = datetime.utcnow()
meeting_time = now + timedelta(minutes=5)

# Format times for database
start_time = meeting_time.strftime('%Y-%m-%d %H:%M:%S')
end_time = (meeting_time + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')

print(f"Creating test meeting:")
print(f"Start time: {start_time}")
print(f"End time: {end_time}")

# Create a test booking
cursor.execute('''
    INSERT INTO booking (
        user_id, expert_id, start_time, end_time, duration,
        payment_amount, status, payment_status, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    2,  # test_client
    1,  # test_expert
    start_time,
    end_time,
    30,  # 30 minutes
    50.00,  # $50
    'confirmed',
    'paid',
    now.strftime('%Y-%m-%d %H:%M:%S')
))

# Commit the changes
conn.commit()

# Get the booking ID
booking_id = cursor.lastrowid
print(f"Created booking with ID: {booking_id}")

# Close the connection
conn.close()

print("✅ Test meeting created successfully!")
print(f"📅 Meeting starts in 5 minutes at {start_time}")
print(f"⏰ Duration: 30 minutes")
print(f"💰 Amount: $50.00")
print(f"👥 Between: test_client and test_expert")
print(f"🔗 You can now test the video call feature!") 