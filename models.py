from app import db
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
    
    # Profile information
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
    
    # Social media links
    linkedin_url = db.Column(db.String(200))
    twitter_url = db.Column(db.String(200))
    youtube_url = db.Column(db.String(200))
    instagram_url = db.Column(db.String(200))
    website_url = db.Column(db.String(200))
    
    # Profile settings
    is_available = db.Column(db.Boolean, default=True)
    
    # New fields from redesigned website
    specialty_tags = db.Column(db.Text)  # JSON string of specialty tags
    profile_picture = db.Column(db.String(255))  # Path to profile picture
    background_color = db.Column(db.String(7), default='#f7faff')  # Hex color code
    embedding = db.Column(db.LargeBinary)  # Store numpy array as binary
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    time_slots = db.relationship('TimeSlot', backref='user', lazy=True, cascade='all, delete-orphan')
    bookings_as_provider = db.relationship('Booking', foreign_keys='Booking.provider_id', backref='provider', lazy=True)
    bookings_as_client = db.relationship('Booking', foreign_keys='Booking.client_id', backref='client', lazy=True)

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

class TimeSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Time information
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    
    # Session details
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    session_type = db.Column(db.String(50), default='consultation')  # consultation, coaching, mentoring
    meeting_details = db.Column(db.String(200))
    
    # Pricing
    price = db.Column(db.Float, default=0.0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    booking = db.relationship('Booking', backref='time_slot', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<TimeSlot {self.start_datetime} - {self.end_datetime}>'

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_slot_id = db.Column(db.Integer, db.ForeignKey('time_slot.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Booking details
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled, completed
    client_name = db.Column(db.String(100))
    client_email = db.Column(db.String(120))
    client_message = db.Column(db.Text)
    
    # Payment information
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, refunded
    payment_amount = db.Column(db.Float)
    stripe_payment_intent_id = db.Column(db.String(100))
    stripe_session_id = db.Column(db.String(100))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Booking {self.id} - {self.status}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category_type = db.Column(db.String(20), nullable=False)  # industry, profession, expertise
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'
