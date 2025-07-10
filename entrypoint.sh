#!/bin/bash
set -e

# Initialize the SQLite database if it doesn't exist
if [ ! -f /app/droply.db ]; then
  echo "Initializing SQLite database..."
  python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database initialized successfully')"
fi

# Start the Flask app
exec python -m flask run --host=0.0.0.0 