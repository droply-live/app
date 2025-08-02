#!/usr/bin/env python3
"""
Script to show all available test meetings
"""

import os
import sys
from datetime import datetime, timezone, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Booking, User

def show_all_test_meetings():
    """Show all available test meetings"""
    with app.app_context():
        try:
            # Get all bookings
            bookings = Booking.query.all()
            
            print("🎥 ALL AVAILABLE TEST MEETINGS")
            print("=" * 80)
            
            if not bookings:
                print("No bookings found in the database.")
                return
            
            # Filter for test bookings (IDs 19, 20, 21, 22)
            test_bookings = [b for b in bookings if b.id in [19, 20, 21, 22]]
            
            if not test_bookings:
                print("No test bookings found.")
                return
            
            for booking in test_bookings:
                print(f"\n📅 Booking ID: {booking.id}")
                print(f"   Client: {booking.user.full_name if booking.user else 'Unknown'}")
                print(f"   Expert: {booking.expert.full_name if booking.expert else 'Unknown'}")
                print(f"   Status: {booking.status}")
                print(f"   Duration: {booking.duration} minutes")
                print(f"   Room ID: {booking.meeting_room_id}")
                print(f"   Meeting URL: {booking.meeting_url}")
                
                # Time information
                now_utc = datetime.now(timezone.utc)
                start_time = booking.start_time
                end_time = booking.end_time
                
                # Ensure timezone awareness
                if start_time.tzinfo is None:
                    start_time = start_time.replace(tzinfo=timezone.utc)
                if end_time.tzinfo is None:
                    end_time = end_time.replace(tzinfo=timezone.utc)
                
                # Convert to local time (Eastern)
                eastern = timezone(timedelta(hours=-4))
                start_local = start_time.astimezone(eastern)
                end_local = end_time.astimezone(eastern)
                now_local = now_utc.astimezone(eastern)
                
                print(f"   🕐 Time Information:")
                print(f"      Current time (local): {now_local.strftime('%Y-%m-%d %I:%M:%S %p %Z')}")
                print(f"      Start time (local): {start_local.strftime('%Y-%m-%d %I:%M:%S %p %Z')}")
                print(f"      End time (local): {end_local.strftime('%Y-%m-%d %I:%M:%S %p %Z')}")
                print(f"      Start time (UTC): {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                print(f"      End time (UTC): {end_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                
                # Calculate time difference
                time_diff = abs((start_time - now_utc).total_seconds() / 60)
                print(f"      Time difference: {time_diff:.1f} minutes")
                
                # Check if can join
                can_join = booking.can_join_meeting()
                join_status = "✅ Can join" if can_join else "❌ Cannot join"
                print(f"      Join status: {join_status}")
                
                # Test URLs
                print(f"   🔗 Test URLs:")
                print(f"      Timezone-free: https://bfdc63768799.ngrok-free.app/timezone-free-meeting/{booking.id}")
                print(f"      Simple meeting: https://bfdc63768799.ngrok-free.app/simple-meeting/{booking.id}")
                print(f"      Force meeting: https://bfdc63768799.ngrok-free.app/force-meeting/{booking.id}")
                
                print("-" * 80)
            
            print(f"\n🎯 RECOMMENDED TEST MEETING:")
            # Find the most recent joinable booking
            joinable_bookings = [b for b in test_bookings if b.can_join_meeting()]
            if joinable_bookings:
                latest_booking = max(joinable_bookings, key=lambda b: b.start_time)
                print(f"   Use Booking ID {latest_booking.id} - {latest_booking.user.full_name} with {latest_booking.expert.full_name}")
                print(f"   URL: https://bfdc63768799.ngrok-free.app/timezone-free-meeting/{latest_booking.id}")
            else:
                print("   No joinable meetings found. Create a new one with the create_timezone_aware_meeting.py script.")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    show_all_test_meetings() 