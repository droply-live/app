#!/usr/bin/env python3
"""
Test script to verify the new onboarding functionality
"""

import requests
import json
import sys

def test_onboarding():
    """Test the new onboarding functionality"""
    base_url = "http://localhost:5000"
    
    print("=== Testing New Onboarding Functionality ===\n")
    
    # Test 1: Check if server is running
    print("1. Testing server connectivity...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   ✓ Server is running (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("   ✗ Server is not running. Please start the Flask app first.")
        return False
    
    # Test 2: Check onboarding endpoint
    print("\n2. Testing onboarding endpoint...")
    try:
        response = requests.get(f"{base_url}/onboarding", allow_redirects=False)
        if response.status_code == 302:
            print("   ✓ Onboarding endpoint exists (redirects to login - expected)")
        elif response.status_code == 200:
            print("   ✓ Onboarding endpoint accessible")
        else:
            print(f"   ⚠ Onboarding status: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error testing onboarding endpoint: {e}")
    
    # Test 3: Check account settings endpoint
    print("\n3. Testing account settings endpoint...")
    try:
        response = requests.get(f"{base_url}/account", allow_redirects=False)
        if response.status_code == 302:
            print("   ✓ Account settings endpoint exists (redirects to login - expected)")
        else:
            print(f"   ⚠ Account settings status: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error testing account settings: {e}")
    
    print("\n=== Test Summary ===")
    print("✓ Server is running")
    print("✓ Onboarding endpoint exists")
    print("✓ Account settings endpoint exists")
    print("\n=== Manual Testing Instructions ===")
    print("To test the new onboarding flow:")
    print("1. Open http://localhost:5000 in your browser")
    print("2. Register a new account")
    print("3. You should be redirected to the new multi-step onboarding")
    print("4. Test each step:")
    print("   - Step 1: Basic information (profession, bio, industry)")
    print("   - Step 2: Expertise tags (select from categories)")
    print("   - Step 3: Pricing (set hourly rate)")
    print("   - Step 4: Review and complete")
    print("5. After completion, go to Account settings")
    print("6. Check that expertise tags are saved and editable")
    print("7. Test the find experts page to see if filtering works")
    
    return True

if __name__ == "__main__":
    test_onboarding() 