from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone, timedelta

# Configure timezone to Eastern Time
EASTERN_TIMEZONE = timezone(timedelta(hours=-4))  # EDT (UTC-4)
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
    expertise = db.Column(db.String(200))  # Legacy field - keeping for backward compatibility
    expertise_1 = db.Column(db.String(100))  # Primary expertise
    expertise_2 = db.Column(db.String(100))  # Secondary expertise  
    expertise_3 = db.Column(db.String(100))  # Tertiary expertise
    location = db.Column(db.String(100))
    background_image_url = db.Column(db.String(500))
    hourly_rate = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    is_available = db.Column(db.Boolean, default=True)
    is_top_expert = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now(EASTERN_TIMEZONE))
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

    # Stripe Connect fields for expert payouts
    stripe_account_id = db.Column(db.String(100))  # Stripe Connect account ID
    stripe_account_status = db.Column(db.String(50), default='pending')  # pending, active, restricted, disabled
    payout_enabled = db.Column(db.Boolean, default=False)  # Whether expert can receive payouts
    payout_schedule = db.Column(db.String(20), default='weekly')  # daily, weekly, monthly
    total_earnings = db.Column(db.Float, default=0.0)  # Total earnings before platform fees
    total_payouts = db.Column(db.Float, default=0.0)  # Total amount paid out
    pending_balance = db.Column(db.Float, default=0.0)  # Current pending balance

    # User preferences
    language = db.Column(db.String(10), default='en')  # Language preference
    timezone = db.Column(db.String(50), default='America/New_York')  # Timezone preference
    email_notifications = db.Column(db.Boolean, default=True)  # Email notifications preference
    
    # Google Calendar integration
    google_calendar_connected = db.Column(db.Boolean, default=False)  # Whether user has connected Google Calendar
    google_calendar_token = db.Column(db.Text)  # Encrypted Google Calendar access token
    google_calendar_refresh_token = db.Column(db.Text)  # Encrypted Google Calendar refresh token
    google_calendar_id = db.Column(db.String(100))  # Primary Google Calendar ID to sync with

    # Referral system fields
    referral_code = db.Column(db.String(20), unique=True)  # User's unique referral code
    referred_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # User who referred this user
    total_referral_earnings = db.Column(db.Float, default=0.0)  # Total earnings from referrals
    referral_count = db.Column(db.Integer, default=0)  # Number of successful referrals

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

    def generate_referral_code(self):
        """Generate a unique referral code for the user"""
        import secrets
        import string
        
        if not self.referral_code:
            # Generate a 8-character alphanumeric code
            alphabet = string.ascii_uppercase + string.digits
            code = ''.join(secrets.choice(alphabet) for _ in range(8))
            
            # Ensure uniqueness
            while User.query.filter_by(referral_code=code).first():
                code = ''.join(secrets.choice(alphabet) for _ in range(8))
            
            self.referral_code = code
            return code
        return self.referral_code

    def get_referral_link(self):
        """Get the full referral link for this user"""
        from flask import url_for
        if not self.referral_code:
            self.generate_referral_code()
        return f"{url_for('homepage', _external=True)}?ref={self.referral_code}"

    def __repr__(self):
        return f'<User {self.username}>'

class Favorite(db.Model):
    """Track user favorites - which experts users have favorited"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # The user who favorited
    expert_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # The expert being favorited
    created_at = db.Column(db.DateTime, default=datetime.now(EASTERN_TIMEZONE))
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='favorites_as_user')
    expert = db.relationship('User', foreign_keys=[expert_id], backref='favorites_as_expert')
    
    # Ensure unique combinations
    __table_args__ = (db.UniqueConstraint('user_id', 'expert_id', name='_user_expert_favorite_uc'),)
    
    def __repr__(self):
        return f'<Favorite {self.user_id} -> {self.expert_id}>'

class AvailabilityRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    weekday = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start = db.Column(db.Time, nullable=False)
    end = db.Column(db.Time, nullable=False)
    is_active = db.Column(db.Boolean, default=True)  # Whether this rule is active
    created_at = db.Column(db.DateTime, default=datetime.now(EASTERN_TIMEZONE))
    updated_at = db.Column(db.DateTime, default=datetime.now(EASTERN_TIMEZONE), onupdate=datetime.now(EASTERN_TIMEZONE))
    
    # Relationships
    user = db.relationship('User', backref='availability_rules')
    
    def __repr__(self):
        return f'<AvailabilityRule {self.weekday} {self.start}-{self.end}>'

class AvailabilityException(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(255))
    is_blocked = db.Column(db.Boolean, default=True)  # True = blocked time, False = available time
    created_at = db.Column(db.DateTime, default=datetime.now(EASTERN_TIMEZONE))
    
    # Relationships
    user = db.relationship('User', backref='availability_exceptions')
    
    def __repr__(self):
        return f'<AvailabilityException {self.start}-{self.end} ({self.reason})>'

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # The person who booked
    expert_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # The expert
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    status = db.Column(db.String(32), default='confirmed')  # confirmed, cancelled, completed, etc.
    created_at = db.Column(db.DateTime, default=datetime.now(EASTERN_TIMEZONE))
    # Payment and client info fields from payment-integration branch
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, refunded
    payment_amount = db.Column(db.Float)
    stripe_payment_intent_id = db.Column(db.String(100))
    stripe_session_id = db.Column(db.String(100))
    client_name = db.Column(db.String(100))
    client_email = db.Column(db.String(120))
    client_message = db.Column(db.Text)
    
    # Video call fields
    meeting_room_id = db.Column(db.String(100))  # Unique room ID for video call
    meeting_url = db.Column(db.String(500))  # Direct meeting URL
    meeting_started_at = db.Column(db.DateTime)  # When the meeting actually started
    meeting_ended_at = db.Column(db.DateTime)  # When the meeting ended
    meeting_duration = db.Column(db.Integer)  # Actual meeting duration in minutes
    recording_url = db.Column(db.String(500))  # URL to meeting recording if available
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='bookings_as_user')
    expert = db.relationship('User', foreign_keys=[expert_id], backref='bookings_as_expert')

    def __repr__(self):
        return f'<Booking {self.id} - {self.status}>'
    
    def is_upcoming(self):
        """Check if booking is in the future"""
        from datetime import datetime, timezone
        now = datetime.now(EASTERN_TIMEZONE)
        
        # Handle timezone-naive datetimes by assuming they're Eastern Time
        start_time = self.start_time
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=EASTERN_TIMEZONE)
            
        return start_time > now
    
    def is_ongoing(self):
        """Check if booking is currently happening"""
        from datetime import datetime, timezone
        now = datetime.now(EASTERN_TIMEZONE)
        
        # Handle timezone-naive datetimes by assuming they're Eastern Time
        start_time = self.start_time
        end_time = self.end_time
        
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=EASTERN_TIMEZONE)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=EASTERN_TIMEZONE)
            
        return start_time <= now <= end_time
    
    def can_join_meeting(self):
        """Check if user can join the meeting (within 5 minutes before start)"""
        from datetime import datetime, timezone, timedelta
        now = datetime.now(EASTERN_TIMEZONE)
        
        # Handle timezone-naive datetimes by assuming they're Eastern Time
        start_time = self.start_time
        end_time = self.end_time
        
        # If the datetime is timezone-naive, assume it's Eastern Time
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=EASTERN_TIMEZONE)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=EASTERN_TIMEZONE)
            
        return start_time - timedelta(minutes=5) <= now <= end_time

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category_type = db.Column(db.String(20), nullable=False)  # industry, profession, expertise
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Payout(db.Model):
    """Track payouts to experts"""
    id = db.Column(db.Integer, primary_key=True)
    expert_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)  # Amount in cents
    currency = db.Column(db.String(3), default='usd')
    stripe_transfer_id = db.Column(db.String(100))  # Stripe transfer ID
    stripe_payout_id = db.Column(db.String(100))  # Stripe payout ID
    status = db.Column(db.String(20), default='pending')  # pending, paid, failed
    created_at = db.Column(db.DateTime, default=datetime.now(EASTERN_TIMEZONE))
    paid_at = db.Column(db.DateTime)  # When payout was actually paid
    
    # Relationships
    expert = db.relationship('User', backref='payouts')
    
    def __repr__(self):
        return f'<Payout {self.id} - ${self.amount/100:.2f} - {self.status}>'

class Referral(db.Model):
    """Track referral relationships between users"""
    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User who made the referral
    referred_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User who was referred
    referral_code = db.Column(db.String(20), nullable=False)  # The referral code used
    created_at = db.Column(db.DateTime, default=datetime.now(EASTERN_TIMEZONE))
    status = db.Column(db.String(20), default='pending')  # pending, completed, expired
    
    # Relationships
    referrer = db.relationship('User', foreign_keys=[referrer_id], backref='referrals_made')
    referred_user = db.relationship('User', foreign_keys=[referred_user_id], backref='referrals_received')
    
    # Ensure unique combinations
    __table_args__ = (db.UniqueConstraint('referrer_id', 'referred_user_id', name='_referrer_referred_uc'),)
    
    def __repr__(self):
        return f'<Referral {self.referrer_id} -> {self.referred_user_id} ({self.status})>'

class ReferralReward(db.Model):
    """Track referral rewards earned by users"""
    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User who earned the reward
    referred_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User who triggered the reward
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)  # Booking that triggered the reward
    reward_amount = db.Column(db.Float, nullable=False)  # Reward amount in dollars
    reward_type = db.Column(db.String(20), default='booking')  # booking, signup, etc.
    status = db.Column(db.String(20), default='pending')  # pending, paid, cancelled
    created_at = db.Column(db.DateTime, default=datetime.now(EASTERN_TIMEZONE))
    paid_at = db.Column(db.DateTime)  # When reward was actually paid
    
    # Relationships
    referrer = db.relationship('User', foreign_keys=[referrer_id], backref='referral_rewards_earned')
    referred_user = db.relationship('User', foreign_keys=[referred_user_id], backref='referral_rewards_triggered')
    booking = db.relationship('Booking', backref='referral_rewards')
    
    def __repr__(self):
        return f'<ReferralReward {self.id} - ${self.reward_amount:.2f} - {self.status}>'
