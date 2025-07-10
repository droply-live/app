#!/usr/bin/env python3
"""
Database migration script to add Stripe Connect fields to the User table
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Database configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///droply.db")

def migrate_database():
    """Add Stripe Connect fields to the User table"""
    
    print("🔄 Starting Stripe Connect migration...")
    
    try:
        # Create database engine
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if we're using SQLite or PostgreSQL
            if DATABASE_URL.startswith('sqlite'):
                print("📱 Using SQLite database")
                migrate_sqlite(conn)
            else:
                print("🐘 Using PostgreSQL database")
                migrate_postgresql(conn)
                
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

def migrate_sqlite(conn):
    """Migrate SQLite database"""
    
    # List of columns to add
    columns = [
        ("stripe_account_id", "TEXT"),
        ("stripe_account_status", "TEXT DEFAULT 'pending'"),
        ("payout_enabled", "BOOLEAN DEFAULT 0"),
        ("payout_schedule", "TEXT DEFAULT 'weekly'"),
        ("total_earnings", "REAL DEFAULT 0.0"),
        ("total_payouts", "REAL DEFAULT 0.0"),
        ("pending_balance", "REAL DEFAULT 0.0")
    ]
    
    for col_name, col_type in columns:
        try:
            # Check if column exists
            result = conn.execute(text(f"PRAGMA table_info(user)"))
            existing_columns = [row[1] for row in result.fetchall()]
            
            if col_name not in existing_columns:
                print(f"➕ Adding column: {col_name}")
                conn.execute(text(f"ALTER TABLE user ADD COLUMN {col_name} {col_type}"))
                conn.commit()
            else:
                print(f"✓ Column {col_name} already exists")
                
        except Exception as e:
            print(f"⚠️  Error adding column {col_name}: {e}")

def migrate_postgresql(conn):
    """Migrate PostgreSQL database"""
    
    # List of columns to add
    columns = [
        ("stripe_account_id", "VARCHAR(100)"),
        ("stripe_account_status", "VARCHAR(50) DEFAULT 'pending'"),
        ("payout_enabled", "BOOLEAN DEFAULT FALSE"),
        ("payout_schedule", "VARCHAR(20) DEFAULT 'weekly'"),
        ("total_earnings", "FLOAT DEFAULT 0.0"),
        ("total_payouts", "FLOAT DEFAULT 0.0"),
        ("pending_balance", "FLOAT DEFAULT 0.0")
    ]
    
    for col_name, col_type in columns:
        try:
            # Check if column exists
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'user' AND column_name = :col_name
            """), {"col_name": col_name})
            
            if not result.fetchone():
                print(f"➕ Adding column: {col_name}")
                conn.execute(text(f"ALTER TABLE \"user\" ADD COLUMN {col_name} {col_type}"))
                conn.commit()
            else:
                print(f"✓ Column {col_name} already exists")
                
        except Exception as e:
            print(f"⚠️  Error adding column {col_name}: {e}")

def create_payout_table(conn):
    """Create the Payout table"""
    
    print("📋 Creating Payout table...")
    
    try:
        if DATABASE_URL.startswith('sqlite'):
            # SQLite syntax
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS payout (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    expert_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    currency VARCHAR(3) DEFAULT 'usd',
                    stripe_transfer_id VARCHAR(100),
                    stripe_payout_id VARCHAR(100),
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    paid_at DATETIME,
                    FOREIGN KEY (expert_id) REFERENCES user (id)
                )
            """))
        else:
            # PostgreSQL syntax
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS payout (
                    id SERIAL PRIMARY KEY,
                    expert_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    currency VARCHAR(3) DEFAULT 'usd',
                    stripe_transfer_id VARCHAR(100),
                    stripe_payout_id VARCHAR(100),
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    paid_at TIMESTAMP,
                    FOREIGN KEY (expert_id) REFERENCES "user" (id)
                )
            """))
        
        conn.commit()
        print("✅ Payout table created successfully!")
        
    except Exception as e:
        print(f"⚠️  Error creating Payout table: {e}")

if __name__ == "__main__":
    migrate_database()
    print("\n🎉 Migration script completed!")
    print("\nNext steps:")
    print("1. Set up your Stripe Connect account in the Stripe Dashboard")
    print("2. Configure webhook endpoints for payment confirmations")
    print("3. Test the expert onboarding flow")
    print("4. Monitor payouts in the expert dashboard") 