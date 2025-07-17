#!/usr/bin/env python3
"""
Test script to verify that profile URL generation works correctly
"""

from flask import Flask, render_template_string
from flask_login import LoginManager, current_user
from unittest.mock import Mock, patch

# Create a minimal Flask app for testing
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-key'

# Mock current_user
class MockUser:
    def __init__(self, username):
        self.username = username
        self.is_authenticated = True

# Test template that includes the profile link
test_template = """
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
    <nav>
        <ul>
            <li><a href="{{ url_for('profile', username=current_user.username) }}">Profile</a></li>
        </ul>
    </nav>
    <main>
        <h1>Dashboard</h1>
        <p>Welcome {{ current_user.username }}!</p>
    </main>
</body>
</html>
"""

def test_profile_url_generation():
    """Test that profile URL generation works correctly"""
    with app.app_context():
        # Mock current_user using patch
        with patch('flask_login.current_user') as mock_current_user:
            mock_user = MockUser('testuser')
            mock_current_user.username = mock_user.username
            mock_current_user.is_authenticated = mock_user.is_authenticated
            
            try:
                # This should not raise a BuildError
                rendered = render_template_string(test_template)
                print("✅ SUCCESS: Profile URL generation works correctly")
                print(f"Rendered template contains: {rendered[:200]}...")
                return True
            except Exception as e:
                print(f"❌ ERROR: {e}")
                return False

if __name__ == '__main__':
    test_profile_url_generation() 