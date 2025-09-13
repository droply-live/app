#!/usr/bin/env python3
"""
Migration script to add referral system fields to existing users
Run this script after adding the referral models to your database schema
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from models import User

def migrate_referrals():
    """Add referral codes to existing users who don't have them"""
    with app.app_context():
        try:
            # Get all users without referral codes
            users_without_codes = User.query.filter(User.referral_code.is_(None)).all()
            
            print(f"Found {len(users_without_codes)} users without referral codes")
            
            for user in users_without_codes:
                # Generate referral code for each user
                user.generate_referral_code()
                print(f"Generated referral code for user: {user.username} -> {user.referral_code}")
            
            # Commit all changes
            db.session.commit()
            print(f"Successfully migrated {len(users_without_codes)} users")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()
            return False
    
    return True

if __name__ == "__main__":
    print("Starting referral system migration...")
    success = migrate_referrals()
    
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        sys.exit(1)

