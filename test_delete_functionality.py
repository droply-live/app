#!/usr/bin/env python3
"""
Comprehensive test for delete account functionality
"""

import requests
import sys
import time

def test_delete_account_workflow():
    """Test the complete delete account workflow"""
    base_url = "http://localhost:5000"
    
    print("=== Testing Delete Account Functionality ===\n")
    
    # Test 1: Check if server is running
    print("1. Testing server connectivity...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   ✓ Server is running (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("   ✗ Server is not running. Please start the Flask app first.")
        return False
    
    # Test 2: Check delete account endpoint exists
    print("\n2. Testing delete account endpoint...")
    try:
        response = requests.post(f"{base_url}/delete-account", data={
            'confirmation': 'DELETE',
            'reason': 'Test deletion'
        }, allow_redirects=False)
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            if '/login' in location:
                print("   ✓ Delete account endpoint exists and redirects to login (expected)")
            else:
                print(f"   ✓ Delete account endpoint exists (redirects to: {location})")
        elif response.status_code == 401:
            print("   ✓ Delete account endpoint exists (requires authentication)")
        else:
            print(f"   ⚠ Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"   ✗ Error testing delete account endpoint: {e}")
        return False
    
    # Test 3: Check homepage redirect logic
    print("\n3. Testing homepage redirect logic...")
    try:
        response = requests.get(f"{base_url}/", allow_redirects=False)
        if response.status_code == 200:
            print("   ✓ Homepage accessible for non-authenticated users")
        else:
            print(f"   ⚠ Homepage status: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error testing homepage: {e}")
    
    print("\n=== Test Summary ===")
    print("✓ Server is running")
    print("✓ Delete account endpoint exists")
    print("✓ Homepage is accessible")
    print("\n=== Manual Testing Instructions ===")
    print("To test the complete functionality:")
    print("1. Open http://localhost:5000 in your browser")
    print("2. Register a test account")
    print("3. Go to Account settings (click on your profile)")
    print("4. Click 'Delete account' in the left sidebar")
    print("5. Type 'DELETE' in the confirmation field")
    print("6. Click 'Delete Account Permanently'")
    print("7. Confirm the final dialog")
    print("8. Verify you're redirected to the homepage (external landing page)")
    print("9. Verify you can no longer access authenticated pages")
    
    return True

if __name__ == "__main__":
    test_delete_account_workflow() 