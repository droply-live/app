import psycopg2
from psycopg2 import sql

# Database connection details from docker-compose.yml
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'droply',
    'user': 'droply',
    'password': 'droply'
}

# Columns to add
columns = [
    ("background_image_url", "VARCHAR(500)"),
    ("linkedin_url", "VARCHAR(200)"),
    ("twitter_url", "VARCHAR(200)"),
    ("youtube_url", "VARCHAR(200)"),
    ("instagram_url", "VARCHAR(200)"),
    ("website_url", "VARCHAR(200)")
]

def column_exists(cursor, table, column):
    """Check if a column exists in the table"""
    cursor.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = %s AND column_name = %s
    """, (table, column))
    return cursor.fetchone() is not None

def main():
    try:
        # Connect to PostgreSQL
        print("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Connected successfully!")
        
        # Add each column if it doesn't exist
        for col_name, col_type in columns:
            if not column_exists(cursor, "user", col_name):
                print(f"Adding column {col_name}...")
                alter_query = sql.SQL("ALTER TABLE {} ADD COLUMN {} {}").format(
                    sql.Identifier("user"),
                    sql.Identifier(col_name),
                    sql.SQL(col_type)
                )
                cursor.execute(alter_query)
                print(f"✓ Added column {col_name}")
            else:
                print(f"✓ Column {col_name} already exists")
        
        # Commit the changes
        conn.commit()
        print("\n✅ Database patched successfully!")
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main() 