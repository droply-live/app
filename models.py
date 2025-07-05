from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from sqlalchemy import func
import json
# import numpy as np

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    full_name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    industry = db.Column(db.String(100))
    profession = db.Column(db.String(100))
    expertise = db.Column(db.String(200))
    location = db.Column(db.String(100))
    background_image_url = db.Column(db.String(500))
    hourly_rate = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    is_available = db.Column(db.Boolean, default=True)
    is_top_expert = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    specialty_tags = db.Column(db.Text)  # JSON string of specialty tags
    profile_picture = db.Column(db.String(255))  # Path to profile picture
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
        """Store numpy array as binary - Temporarily disabled"""
        # self.embedding = embedding_array.tobytes()
        pass
    
    def get_embedding(self):
        """Retrieve numpy array from binary - Temporarily disabled"""
        # if self.embedding:
        #     return np.frombuffer(self.embedding, dtype=np.float32)
        return None
    
    def get_location_display(self):
        """Return location display string - placeholder for now"""
        return None

    def __repr__(self):
        return f'<User {self.username}>'

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

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # The person who booked
    expert_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # The expert
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    status = db.Column(db.String(32), default='confirmed')  # confirmed, cancelled, completed, etc.
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    # Payment and client info fields from payment-integration branch
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, refunded
    payment_amount = db.Column(db.Float)
    stripe_payment_intent_id = db.Column(db.String(100))
    stripe_session_id = db.Column(db.String(100))
    client_name = db.Column(db.String(100))
    client_email = db.Column(db.String(120))
    client_message = db.Column(db.Text)
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='bookings_as_user')
    expert = db.relationship('User', foreign_keys=[expert_id], backref='bookings_as_expert')

    def __repr__(self):
        return f'<Booking {self.id} - {self.status}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category_type = db.Column(db.String(20), nullable=False)  # industry, profession, expertise
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'
