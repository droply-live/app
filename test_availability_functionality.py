#!/usr/bin/env python3
"""
Test script to verify availability functionality
"""

import requests
import json
import time

def test_availability_api():
    """Test the availability API endpoints"""
    base_url = "http://localhost:5000"
    
    print("Testing Availability API...")
    
    # Test GET availability rules (should return empty array for new user)
    try:
        response = requests.get(f"{base_url}/api/availability/rules")
        print(f"GET /api/availability/rules: {response.status_code}")
        if response.status_code == 200:
            rules = response.json()
            print(f"Rules returned: {rules}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing GET availability rules: {e}")
    
    # Test POST availability rules
    test_rules = {
        "rules": [
            {
                "weekday": 0,  # Monday
                "start": "09:00",
                "end": "17:00",
                "enabled": True
            },
            {
                "weekday": 1,  # Tuesday
                "start": "10:00",
                "end": "18:00",
                "enabled": True
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/availability/rules",
            json=test_rules,
            headers={"Content-Type": "application/json"}
        )
        print(f"POST /api/availability/rules: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Result: {result}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing POST availability rules: {e}")
    
    # Test GET availability times for a specific user
    try:
        response = requests.get(f"{base_url}/api/availability/times?username=testuser")
        print(f"GET /api/availability/times: {response.status_code}")
        if response.status_code == 200:
            times = response.json()
            print(f"Times returned: {times}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing GET availability times: {e}")

def test_javascript_functionality():
    """Test the JavaScript functionality by checking the HTML structure"""
    print("\nTesting JavaScript Functionality...")
    
    # Check if the availability page loads correctly
    try:
        response = requests.get("http://localhost:5000/account")
        print(f"Account page status: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            
            # Check for quick setup cards
            if 'quick-setup-card' in html:
                print("✓ Quick setup cards found in HTML")
            else:
                print("✗ Quick setup cards not found in HTML")
            
            # Check for flexible button
            if 'data-preset="flexible"' in html:
                print("✓ Flexible button found in HTML")
            else:
                print("✗ Flexible button not found in HTML")
            
            # Check for save button
            if 'saveAvailabilityBtn' in html:
                print("✓ Save availability button found in HTML")
            else:
                print("✗ Save availability button not found in HTML")
            
            # Check for JavaScript event listeners
            if 'addEventListener' in html and 'quick-setup-card' in html:
                print("✓ JavaScript event listeners found for quick setup cards")
            else:
                print("✗ JavaScript event listeners not found for quick setup cards")
            
            # Check for session slot generation
            if 'generateSessionTogglesForDay' in html:
                print("✓ Session generation function found")
            else:
                print("✗ Session generation function not found")
                
        else:
            print(f"Error loading account page: {response.status_code}")
            
    except Exception as e:
        print(f"Error testing JavaScript functionality: {e}")

if __name__ == "__main__":
    print("=== Availability Functionality Test ===")
    test_availability_api()
    test_javascript_functionality()
    print("\n=== Test Complete ===") 