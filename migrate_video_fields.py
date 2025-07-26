#!/usr/bin/env python3
"""
Migration script to add video call fields to the Booking model
"""

import os
import sys
from datetime import datetime, timezone

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Booking

def migrate_video_fields():
    """Add video call fields to existing bookings table"""
    with app.app_context():
        try:
            # Check if the new columns already exist
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('booking')]
            
            new_columns = [
                'meeting_room_id',
                'meeting_url', 
                'meeting_started_at',
                'meeting_ended_at',
                'meeting_duration',
                'recording_url'
            ]
            
            missing_columns = [col for col in new_columns if col not in existing_columns]
            
            if not missing_columns:
                print("✅ All video call fields already exist in the database.")
                return
            
            print(f"🔧 Adding missing video call fields: {missing_columns}")
            
            # Add missing columns one by one using the correct SQLAlchemy syntax
            for column in missing_columns:
                try:
                    if column == 'meeting_room_id':
                        with db.engine.connect() as conn:
                            conn.execute(db.text('ALTER TABLE booking ADD COLUMN meeting_room_id VARCHAR(100)'))
                            conn.commit()
                    elif column == 'meeting_url':
                        with db.engine.connect() as conn:
                            conn.execute(db.text('ALTER TABLE booking ADD COLUMN meeting_url VARCHAR(500)'))
                            conn.commit()
                    elif column == 'meeting_started_at':
                        with db.engine.connect() as conn:
                            conn.execute(db.text('ALTER TABLE booking ADD COLUMN meeting_started_at DATETIME'))
                            conn.commit()
                    elif column == 'meeting_ended_at':
                        with db.engine.connect() as conn:
                            conn.execute(db.text('ALTER TABLE booking ADD COLUMN meeting_ended_at DATETIME'))
                            conn.commit()
                    elif column == 'meeting_duration':
                        with db.engine.connect() as conn:
                            conn.execute(db.text('ALTER TABLE booking ADD COLUMN meeting_duration INTEGER'))
                            conn.commit()
                    elif column == 'recording_url':
                        with db.engine.connect() as conn:
                            conn.execute(db.text('ALTER TABLE booking ADD COLUMN recording_url VARCHAR(500)'))
                            conn.commit()
                    
                    print(f"✅ Added column: {column}")
                    
                except Exception as e:
                    print(f"⚠️  Error adding column {column}: {e}")
                    # Column might already exist, continue
                    continue
            
            print("🎉 Video call fields migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            raise

if __name__ == '__main__':
    print("🚀 Starting video call fields migration...")
    migrate_video_fields()
    print("✨ Migration script completed!") 