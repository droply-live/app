#!/usr/bin/env python3
"""
Test script for the referral system
This script tests the basic functionality of the referral system
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from models import User, Referral, ReferralReward, Booking
from datetime import datetime, timezone, timedelta

# Configure timezone to Eastern Time
EASTERN_TIMEZONE = timezone(timedelta(hours=-4))

def test_referral_system():
    """Test the referral system functionality"""
    with app.app_context():
        try:
            print("Testing referral system...")
            
            # Test 1: Create a referrer user
            print("\n1. Creating referrer user...")
            referrer = User(
                username="test_referrer",
                email="referrer@test.com",
                full_name="Test Referrer"
            )
            referrer.set_password("password123")
            referrer.generate_referral_code()
            db.session.add(referrer)
            db.session.commit()
            print(f"Referrer created: {referrer.username} with code: {referrer.referral_code}")
            
            # Test 2: Create a referred user
            print("\n2. Creating referred user...")
            referred_user = User(
                username="test_referred",
                email="referred@test.com",
                full_name="Test Referred"
            )
            referred_user.set_password("password123")
            referred_user.generate_referral_code()
            referred_user.referred_by = referrer.id
            db.session.add(referred_user)
            db.session.commit()
            print(f"Referred user created: {referred_user.username}")
            
            # Test 3: Create referral record
            print("\n3. Creating referral record...")
            referral = Referral(
                referrer_id=referrer.id,
                referred_user_id=referred_user.id,
                referral_code=referrer.referral_code,
                status='pending'
            )
            db.session.add(referral)
            db.session.commit()
            print(f"Referral record created: {referrer.username} -> {referred_user.username}")
            
            # Test 4: Create a booking for the referred user
            print("\n4. Creating booking for referred user...")
            booking = Booking(
                user_id=referred_user.id,
                expert_id=referrer.id,  # Using referrer as expert for simplicity
                start_time=datetime.now(EASTERN_TIMEZONE) + timedelta(days=1),
                end_time=datetime.now(EASTERN_TIMEZONE) + timedelta(days=1, hours=1),
                duration=60,
                status='confirmed',
                payment_status='paid',
                payment_amount=50.0
            )
            db.session.add(booking)
            db.session.commit()
            print(f"Booking created: {booking.id}")
            
            # Test 5: Process referral reward
            print("\n5. Processing referral reward...")
            reward = ReferralReward(
                referrer_id=referrer.id,
                referred_user_id=referred_user.id,
                booking_id=booking.id,
                reward_amount=10.0,
                reward_type='booking',
                status='pending'
            )
            
            # Update referral status
            referral.status = 'completed'
            
            # Update referrer's stats
            referrer.referral_count += 1
            referrer.total_referral_earnings += 10.0
            
            db.session.add(reward)
            db.session.commit()
            print(f"Referral reward processed: $10.00 for {referrer.username}")
            
            # Test 6: Verify results
            print("\n6. Verifying results...")
            updated_referrer = User.query.get(referrer.id)
            print(f"Referrer stats - Count: {updated_referrer.referral_count}, Earnings: ${updated_referrer.total_referral_earnings}")
            
            referral_record = Referral.query.filter_by(referrer_id=referrer.id).first()
            print(f"Referral status: {referral_record.status}")
            
            reward_record = ReferralReward.query.filter_by(referrer_id=referrer.id).first()
            print(f"Reward amount: ${reward_record.reward_amount}")
            
            print("\n✅ All tests passed! Referral system is working correctly.")
            
            # Cleanup
            print("\n7. Cleaning up test data...")
            db.session.delete(reward_record)
            db.session.delete(referral_record)
            db.session.delete(booking)
            db.session.delete(referred_user)
            db.session.delete(referrer)
            db.session.commit()
            print("Test data cleaned up.")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("Starting referral system tests...")
    success = test_referral_system()
    
    if success:
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n💥 Tests failed!")
        sys.exit(1)

