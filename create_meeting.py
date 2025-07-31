import sqlite3
from datetime import datetime, timedelta

# Connect to the database
conn = sqlite3.connect('instance/droply.db')
cursor = conn.cursor()

# Get current time and create meeting time 10 minutes from now
now = datetime.utcnow()
meeting_time = now + timedelta(minutes=10)
end_time = meeting_time + timedelta(minutes=30)

print(f"Current UTC time: {now}")
print(f"Meeting start time: {meeting_time}")
print(f"Meeting end time: {end_time}")

# Create a test booking
cursor.execute('''
    INSERT INTO booking (
        user_id, expert_id, start_time, end_time, duration,
        payment_amount, status, payment_status, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    2,  # test_client
    3,  # test_expert (expert_id = 3)
    meeting_time.strftime('%Y-%m-%d %H:%M:%S'),
    end_time.strftime('%Y-%m-%d %H:%M:%S'),
    30,  # 30 minutes
    50.00,  # $50
    'confirmed',
    'paid',
    now.strftime('%Y-%m-%d %H:%M:%S')
))

# Commit the changes
conn.commit()
booking_id = cursor.lastrowid
print(f"Created booking with ID: {booking_id}")

# Close the connection
conn.close()

print("✅ Test meeting created successfully!")
print(f"📅 Meeting starts in 10 minutes")
print(f"⏰ Duration: 30 minutes")
print(f"💰 Amount: $50.00")
print(f"👥 Between: test_client and test_expert") 