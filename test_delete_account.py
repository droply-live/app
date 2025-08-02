#!/usr/bin/env python3
"""
Test script to verify delete account functionality
"""

import requests
import sys

def test_delete_account():
    """Test the delete account functionality"""
    base_url = "http://localhost:5000"
    
    print("Testing delete account functionality...")
    
    # First, let's check if the server is running
    try:
        response = requests.get(f"{base_url}/")
        print(f"Server is running: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("Error: Server is not running. Please start the Flask app first.")
        return False
    
    # Test the delete account endpoint directly
    print("\nTesting delete account endpoint...")
    
    # This would normally require authentication, but we can test the route exists
    try:
        response = requests.post(f"{base_url}/delete-account", data={
            'confirmation': 'DELETE',
            'reason': 'Test deletion'
        }, allow_redirects=False)
        
        print(f"Delete account endpoint response: {response.status_code}")
        if response.status_code == 302:  # Redirect
            print(f"Redirect location: {response.headers.get('Location', 'None')}")
        elif response.status_code == 401:  # Unauthorized (expected for non-authenticated users)
            print("Expected: Unauthorized (user not logged in)")
        else:
            print(f"Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"Error testing delete account endpoint: {e}")
        return False
    
    print("\nTest completed. To fully test the functionality:")
    print("1. Start the Flask app: python app.py")
    print("2. Open http://localhost:5000 in your browser")
    print("3. Register a test account")
    print("4. Go to Account settings")
    print("5. Click 'Delete account'")
    print("6. Type 'DELETE' and submit")
    print("7. Verify you're redirected to the homepage (external landing page)")
    
    return True

if __name__ == "__main__":
    test_delete_account() 