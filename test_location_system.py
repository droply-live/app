#!/usr/bin/env python3
"""
Test script to verify the new location system is working properly.
"""

from app import app, db
from models import Location, User

def test_location_system():
    """Test the location system functionality"""
    with app.app_context():
        print("=== Testing Location System ===\n")
        
        # Test 1: Check if locations are populated
        locations = Location.query.all()
        print(f"1. Total locations in database: {len(locations)}")
        
        # Test 2: Check a few specific locations
        print("\n2. Sample locations:")
        sample_locations = Location.query.limit(5).all()
        for loc in sample_locations:
            print(f"   - {loc.display_name()} (Timezone: {loc.timezone})")
        
        # Test 3: Test location search
        print("\n3. Testing location search:")
        search_results = Location.query.filter(
            Location.city.ilike('%new%')
        ).limit(3).all()
        
        for loc in search_results:
            print(f"   - {loc.city}, {loc.country} ({loc.timezone})")
        
        # Test 4: Test location relationship with users
        print("\n4. Testing user-location relationship:")
        users_with_location = User.query.filter(User.location_id.isnot(None)).all()
        print(f"   Users with location: {len(users_with_location)}")
        
        for user in users_with_location[:3]:  # Show first 3
            if user.location:
                print(f"   - {user.username}: {user.get_location_display()}")
        
        print("\n=== Location System Test Complete ===")

if __name__ == "__main__":
    test_location_system() 