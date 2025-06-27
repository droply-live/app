from app import app, db
from sqlalchemy import text

columns = [
    ("background_image_url", "VARCHAR(500)"),
    ("linkedin_url", "VARCHAR(200)"),
    ("twitter_url", "VARCHAR(200)"),
    ("youtube_url", "VARCHAR(200)"),
    ("instagram_url", "VARCHAR(200)"),
    ("website_url", "VARCHAR(200)"),
    ("rating_count", "INTEGER DEFAULT 0"),
    ("is_top_expert", "BOOLEAN DEFAULT 0"),
    ("donation_text", "TEXT"),
    ("github_url", "VARCHAR(200)"),
    ("facebook_url", "VARCHAR(200)"),
    ("snapchat_url", "VARCHAR(200)")
]

def column_exists(engine, table, column):
    # Detect SQLite or PostgreSQL
    if engine.dialect.name == 'sqlite':
        query = text(f"PRAGMA table_info({table})")
        with engine.connect() as conn:
            result = conn.execute(query)
            return any(row[1] == column for row in result.fetchall())
    else:
        query = text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name=:table AND column_name=:column
        """)
        with engine.connect() as conn:
            result = conn.execute(query, {"table": table, "column": column})
            return result.first() is not None

with app.app_context():
    engine = db.engine
    for col, coltype in columns:
        if not column_exists(engine, "user", col):
            print(f"Adding column {col} ...")
            try:
                with engine.connect() as conn:
                    conn.execute(text(f'ALTER TABLE "user" ADD COLUMN {col} {coltype};'))
                print(f"Added column {col}.")
            except Exception as e:
                print(f"Failed to add column {col}: {e}")
        else:
            print(f"Column {col} already exists.")
    print("Done.") 