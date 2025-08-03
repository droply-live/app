#!/usr/bin/env python3
"""
Script to check users in the database
"""
import os
import sys
sys.path.append('.')

from app import app
from models import User

with app.app_context():
    users = User.query.all()
    print(f"Found {len(users)} users in database:")
    for user in users:
        print(f"- ID: {user.id}, Email: {user.email}, Username: {user.username}, Full Name: {user.full_name}")
        print(f"  Password hash: {user.password_hash[:20]}..." if user.password_hash else "  No password")
        print() 