#!/usr/bin/env python3

import sqlite3
from werkzeug.security import generate_password_hash

# Connect to the database
db_path = 'instance/droply.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Test user credentials
test_users = [
    {
        'id': 3,
        'username': 'test_expert',
        'email': 'expert@test.com',
        'password': 'test123'
    },
    {
        'id': 4,
        'username': 'test_client',
        'email': 'client@test.com',
        'password': 'test123'
    }
]

print("Resetting test user passwords...")

for user in test_users:
    # Generate password hash
    password_hash = generate_password_hash(user['password'])
    
    # Update the user's password
    cursor.execute('''
        UPDATE user 
        SET password_hash = ? 
        WHERE id = ?
    ''', (password_hash, user['id']))
    
    print(f"✅ Updated {user['username']} ({user['email']})")
    print(f"   Password: {user['password']}")

# Commit the changes
conn.commit()
conn.close()

print("\n🎉 Test user passwords reset successfully!")
print("\n📋 Test User Credentials:")
print("=" * 40)
print("👨‍💼 Expert Account:")
print("   Email: expert@test.com")
print("   Password: test123")
print()
print("👤 Client Account:")
print("   Email: client@test.com")
print("   Password: test123")
print()
print("🔗 You can now log in with either account to test the meeting!") 