from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import json
import numpy as np

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    full_name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    industry = db.Column(db.String(50))
    profession = db.Column(db.String(50))
    hourly_rate = db.Column(db.Float, default=0.0)
    rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    is_available = db.Column(db.Boolean, default=True)
    is_top_expert = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    specialty_tags = db.Column(db.Text)  # JSON string of specialty tags
    profile_picture = db.Column(db.String(255))  # Path to profile picture
    background_image_url = db.Column(db.String(500))  # URL to background image
    background_color = db.Column(db.String(7), default='#f7faff')  # Hex color code
    donation_text = db.Column(db.Text)  # Text for donation/booking info
    embedding = db.Column(db.LargeBinary)  # Store numpy array as binary
    
    # Social media URLs
    linkedin_url = db.Column(db.String(200))
    twitter_url = db.Column(db.String(200))
    github_url = db.Column(db.String(200))
    instagram_url = db.Column(db.String(200))
    facebook_url = db.Column(db.String(200))
    snapchat_url = db.Column(db.String(200))
    website_url = db.Column(db.String(200))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_specialty_tags(self):
        if self.specialty_tags:
            return json.loads(self.specialty_tags)
        return []
    
    def set_specialty_tags(self, tags):
        self.specialty_tags = json.dumps(tags)
    
    def set_embedding(self, embedding_array):
        """Store numpy array as binary"""
        self.embedding = embedding_array.tobytes()
    
    def get_embedding(self):
        """Retrieve numpy array from binary"""
        if self.embedding:
            return np.frombuffer(self.embedding, dtype=np.float32)
        return None
    
    def get_location_display(self):
        """Return location display string - placeholder for now"""
        return None

class AvailabilityRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    weekday = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start = db.Column(db.Time, nullable=False)
    end = db.Column(db.Time, nullable=False)

class AvailabilityException(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(255))
