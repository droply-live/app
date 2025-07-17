#!/usr/bin/env python3
"""
Manual database patch to add new expertise fields
Run this script to add expertise_1, expertise_2, expertise_3 columns to the User table
"""

import sqlite3
import os

def add_expertise_columns():
    """Add the new expertise columns to the User table"""
    
    # Get the database path
    db_path = os.path.join('instance', 'droply.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add new columns if they don't exist
        if 'expertise_1' not in columns:
            cursor.execute("ALTER TABLE user ADD COLUMN expertise_1 VARCHAR(100)")
            print("Added expertise_1 column")
        
        if 'expertise_2' not in columns:
            cursor.execute("ALTER TABLE user ADD COLUMN expertise_2 VARCHAR(100)")
            print("Added expertise_2 column")
        
        if 'expertise_3' not in columns:
            cursor.execute("ALTER TABLE user ADD COLUMN expertise_3 VARCHAR(100)")
            print("Added expertise_3 column")
        
        # Commit changes
        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_expertise_columns() 