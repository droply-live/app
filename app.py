import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Environment variables are set automatically by Git hook
# Just show what environment we're running in
current_env = os.environ.get('FLASK_ENV', 'development')
current_branch = os.environ.get('ENVIRONMENT', 'development')

if current_env == 'production':
    print("🚀 Running in: Production environment")
    print("   Book Now button: Hidden")
    print("   Debug logging: Minimal")
else:
    print("🔧 Running in: Development environment")
    print("   Book Now button: Visible")
    print("   Debug logging: Enabled")

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from extensions import db, login_manager
from authlib.integrations.flask_client import OAuth
from flask_login import LoginManager
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timezone, timedelta

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Configure timezone to Eastern Time
EASTERN_TIMEZONE = timezone(timedelta(hours=-4))  # EDT (UTC-4)
# For EST (UTC-5), use: timezone(timedelta(hours=-5))

# create the app
app = Flask(__name__)
app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID', 'YOUR_GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET', 'YOUR_GOOGLE_CLIENT_SECRET')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production-12345')

# Add environment variables to config for template access
app.config['FLASK_ENV'] = os.environ.get('FLASK_ENV', 'development')
app.config['ENVIRONMENT'] = os.environ.get('ENVIRONMENT', 'development')

# Configure URL scheme based on environment
# For local development, use HTTP; for production, use HTTPS
if os.environ.get('FLASK_ENV') == 'development' or os.environ.get('FLASK_DEBUG') == '1':
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    # Removed SERVER_NAME to avoid routing issues in development
    print("✅ Running in DEVELOPMENT mode - SERVER_NAME not set")
else:
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    # Set production domain if provided
    production_domain = os.environ.get('YOUR_DOMAIN', '').replace('https://', '').replace('http://', '')
    if production_domain:
        app.config['SERVER_NAME'] = production_domain
        print(f"⚠️  Running in PRODUCTION mode - SERVER_NAME set to: {production_domain}")

# Debug: Print loaded credentials (remove in production)
print(f"Loaded GOOGLE_CLIENT_ID: {app.config['GOOGLE_CLIENT_ID']}")
print(f"Loaded GOOGLE_CLIENT_SECRET: {app.config['GOOGLE_CLIENT_SECRET'][:10]}..." if app.config['GOOGLE_CLIENT_SECRET'] != 'YOUR_GOOGLE_CLIENT_SECRET' else "Using placeholder secret")

# OAuth setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1, x_for=1)  # needed for url_for to generate with https

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///droply.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# initialize the app with the extension
db.init_app(app)

# Setup Flask-Login
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    # Import here to avoid circular import
    from models import User
    return User.query.get(int(user_id))

def update_past_bookings():
    with app.app_context():
        from models import Booking
        from app import db
        now = datetime.now(EASTERN_TIMEZONE)  # Use Eastern Time instead of UTC
        bookings = Booking.query.filter(
            Booking.status == 'confirmed',
            Booking.end_time < now
        ).all()
        updated = 0
        for booking in bookings:
            booking.status = 'completed'
            updated += 1
        if updated > 0:
            db.session.commit()
            print(f"[APScheduler] Updated {updated} bookings to completed.")

scheduler = BackgroundScheduler()
scheduler.add_job(update_past_bookings, 'interval', minutes=5)
scheduler.start()

with app.app_context():
    # Make sure to import the models here or their tables won't be created
    from models import User, AvailabilityRule, AvailabilityException, Booking, Category
    db.create_all()

# Import routes after app initialization
from routes import *  # noqa: F401,F403

# Initialize agentic system
try:
    from agents.flask_integration import init_agents
    init_agents(app)
    print("✅ ProcuraAI agentic system initialized successfully")
except Exception as e:
    print(f"⚠️  Warning: Could not initialize agentic system: {e}")
    print("   The system will run without AI agents")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
