from flask import render_template, request, redirect, url_for, flash, jsonify, make_response, get_flashed_messages, session
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_, case, func
from app import app
from extensions import db
from models import User, AvailabilityRule, AvailabilityException, Booking, Payout, Favorite, Referral, ReferralReward
from forms import RegistrationForm, LoginForm, SearchForm, OnboardingForm, ProfileForm, TimeSlotForm, BookingForm
# Removed unused imports: utils and keyword_mappings
import json
# import faiss  # Temporarily disabled
# from sentence_transformers import SentenceTransformer  # Temporarily disabled
# import numpy as np  # Temporarily disabled
import os
import stripe
from datetime import datetime, timezone, timedelta, time

# Configure timezone to Eastern Time
EASTERN_TIMEZONE = timezone(timedelta(hours=-4))  # EDT (UTC-4)

# Template filter to convert naive datetime to Eastern Time
@app.template_filter('to_eastern')
def to_eastern(dt):
    """Convert naive datetime to Eastern Time"""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=EASTERN_TIMEZONE)
    return dt

# Template filter to format datetime for display
@app.template_filter('format_datetime')
def format_datetime(dt):
    """Format datetime for display, treating naive datetime as Eastern Time"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=EASTERN_TIMEZONE)
    return dt.strftime('%b %d, %Y %I:%M %p')

# Template filter to get current time in Eastern Time
@app.template_filter('now_eastern')
def now_eastern():
    """Get current time in Eastern Time"""
    return datetime.now(EASTERN_TIMEZONE)

import time
from app import oauth, google

def setup_default_availability(user):
    """Set up default 9-5 availability for weekdays only for new users"""
    try:
        # Check if user already has availability rules
        existing_rules = AvailabilityRule.query.filter_by(user_id=user.id).count()
        if existing_rules > 0:
            print(f"User {user.username} already has {existing_rules} availability rules, skipping setup")
            return
        
        # Detect user's current timezone
        import tzlocal
        try:
            # Get the system's local timezone
            local_timezone = tzlocal.get_localzone()
            default_timezone = str(local_timezone)
        except:
            # Fallback to Eastern Time if detection fails
            default_timezone = 'America/New_York'
        
        # Set user's default timezone
        user.timezone = default_timezone
        
        # Create availability rules for weekdays (Monday=1 to Friday=5)
        # Sunday=0, Monday=1, Tuesday=2, Wednesday=3, Thursday=4, Friday=5, Saturday=6
        weekdays = [1, 2, 3, 4, 5]  # Monday to Friday
        
        for weekday in weekdays:
            availability_rule = AvailabilityRule(
                user_id=user.id,
                weekday=weekday,
                start=time(9, 0),  # 9:00 AM
                end=time(17, 0),   # 5:00 PM
                is_active=True
            )
            db.session.add(availability_rule)
        
        db.session.commit()
        print(f"Set up default 9-5 availability for weekdays for user {user.username}")
        
    except Exception as e:
        print(f"Error setting up default availability for user {user.username}: {e}")
        db.session.rollback()

def fix_all_users_default_availability():
    """Fix all existing users who don't have default availability"""
    try:
        users = User.query.all()
        fixed_count = 0
        
        for user in users:
            existing_rules = AvailabilityRule.query.filter_by(user_id=user.id).count()
            if existing_rules == 0:
                setup_default_availability(user)
                fixed_count += 1
        
        print(f"Fixed default availability for {fixed_count} users")
        return fixed_count
        
    except Exception as e:
        print(f"Error fixing default availability for all users: {e}")
        return 0

@app.route('/fix-availability', methods=['POST'])
@login_required
def fix_user_availability():
    """Fix availability for current user if they don't have any rules"""
    try:
        existing_rules = AvailabilityRule.query.filter_by(user_id=current_user.id).count()
        if existing_rules == 0:
            setup_default_availability(current_user)
            return jsonify({'success': True, 'message': 'Default availability set to 9-5 weekdays'})
        else:
            return jsonify({'success': False, 'message': 'User already has availability rules'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/setup-availability/<username>', methods=['POST'])
@login_required
def setup_availability_for_user(username):
    """Set up default availability for a specific user"""
    try:
        user = User.query.filter_by(username=username).first_or_404()
        
        # Check if user already has availability rules
        existing_rules = AvailabilityRule.query.filter_by(user_id=user.id).count()
        if existing_rules > 0:
            return jsonify({'success': True, 'message': f'User {username} already has {existing_rules} availability rules'})
        
        # Set up default availability
        setup_default_availability(user)
        
        return jsonify({'success': True, 'message': f'Default availability set up successfully for {username}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/connected-calendar')
@login_required
def get_connected_calendar():
    """Get information about the user's connected Google Calendar"""
    try:
        if not current_user.google_calendar_connected or not current_user.google_calendar_id:
            return jsonify({'connected': False, 'message': 'No calendar connected'})
        
        # Get calendar name from Google Calendar API
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        
        # Create credentials object
        credentials = Credentials(
            token=current_user.google_calendar_token,
            refresh_token=current_user.google_calendar_refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=app.config['GOOGLE_CLIENT_ID'],
            client_secret=app.config['GOOGLE_CLIENT_SECRET']
        )
        
        service = build('calendar', 'v3', credentials=credentials)
        calendar = service.calendars().get(calendarId=current_user.google_calendar_id).execute()
        
        return jsonify({
            'connected': True,
            'calendar_id': current_user.google_calendar_id,
            'calendar_name': calendar.get('summary', 'Unknown Calendar'),
            'calendar_email': calendar.get('id', '')
        })
        
    except Exception as e:
        print(f"Error getting connected calendar info: {e}")
        return jsonify({'connected': False, 'error': str(e)}), 500

def convert_to_local_time(dt, user_timezone='America/New_York'):
    """Convert timezone-naive datetime to user's local timezone"""
    if dt is None:
        return None
    # Assume the datetime is in UTC if it's naive
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    # Convert to EDT (UTC-4) for simplicity
    edt_offset = timezone(timedelta(hours=-4))
    return dt.astimezone(edt_offset)

def convert_availability_to_user_timezone(availability_rules, expert_timezone, user_timezone):
    """Convert expert's availability from their timezone to user's timezone"""
    from zoneinfo import ZoneInfo
    from datetime import datetime, time
    
    if not availability_rules:
        return []
    
    expert_tz = ZoneInfo(expert_timezone)
    user_tz = ZoneInfo(user_timezone)
    
    converted_rules = []
    
    for rule in availability_rules:
        # Create datetime objects in expert's timezone for today
        today = datetime.now(expert_tz).date()
        start_dt = datetime.combine(today, rule.start).replace(tzinfo=expert_tz)
        end_dt = datetime.combine(today, rule.end).replace(tzinfo=expert_tz)
        
        # Convert to user's timezone
        start_user = start_dt.astimezone(user_tz)
        end_user = end_dt.astimezone(user_tz)
        
        # Create new rule with converted times
        converted_rule = {
            'weekday': rule.weekday,
            'start': start_user.time(),
            'end': end_user.time(),
            'is_active': rule.is_active,
            'original_start': rule.start,
            'original_end': rule.end
        }
        converted_rules.append(converted_rule)
    
    return converted_rules

def generate_available_slots_for_date(date, expert, user_timezone=None):
    """Generate available time slots for a specific date, converting to user's timezone"""
    try:
        from zoneinfo import ZoneInfo
        from datetime import datetime, time, timedelta
        
        # Get expert's timezone
        expert_timezone = expert.timezone or 'America/New_York'
        
        # Use user's timezone if provided, otherwise use expert's timezone
        display_timezone = user_timezone or expert_timezone
        
        # Get availability rules for this weekday
        weekday = date.weekday()
        rules = AvailabilityRule.query.filter_by(
            user_id=expert.id, 
            weekday=weekday,
            is_active=True
        ).all()
        
        if not rules:
            return []
        
        available_slots = []
        
        for rule in rules:
            try:
                # Create datetime objects in expert's timezone
                expert_tz = ZoneInfo(expert_timezone)
                display_tz = ZoneInfo(display_timezone)
                
                # Start and end times in expert's timezone
                start_dt = datetime.combine(date, rule.start).replace(tzinfo=expert_tz)
                end_dt = datetime.combine(date, rule.end).replace(tzinfo=expert_tz)
                
                # Convert to display timezone
                start_display = start_dt.astimezone(display_tz)
                end_display = end_dt.astimezone(display_tz)
                
                # Generate 30-minute slots
                current_time = start_display
                while current_time + timedelta(minutes=30) <= end_display:
                    # Check if this slot is already booked
                    # Convert back to expert's timezone for booking check
                    expert_time = current_time.astimezone(expert_tz)
                    
                    existing_booking = Booking.query.filter(
                        (Booking.expert_id == expert.id) &
                        (Booking.start_time == expert_time.replace(tzinfo=None)) &
                        (Booking.status.in_(['confirmed', 'pending']))
                    ).first()
                    
                    if not existing_booking:
                        slot = {
                            'start_time': current_time,
                            'end_time': current_time + timedelta(minutes=30),
                            'expert_time': expert_time,
                            'formatted_time': current_time.strftime('%I:%M %p'),
                            'date': date
                        }
                        available_slots.append(slot)
                    
                    current_time += timedelta(minutes=30)
            except Exception as e:
                print(f"Error processing rule for date {date}: {e}")
                continue
        
        return available_slots
    except Exception as e:
        print(f"Error in generate_available_slots_for_date: {e}")
        return []

# Video calling imports and configuration
import os
import requests
import json
import uuid
from datetime import datetime, timezone, timedelta

# Daily.co API configuration (similar to what Intro.co uses)
DAILY_API_KEY = os.environ.get('DAILY_API_KEY', 'your_daily_api_key_here')
DAILY_API_URL = 'https://api.daily.co/v1'

# Fallback video calling (simple WebRTC)
def create_simple_meeting_room(booking_id):
    """Create a simple meeting room using WebRTC when Daily.co is not available"""
    try:
        booking = Booking.query.get(booking_id)
        if not booking:
            return None, "Booking not found"
        
        # Generate a simple room ID
        room_id = f"droply-{booking_id}-{uuid.uuid4().hex[:8]}"
        
        # For simple WebRTC, we'll use a basic room URL
        meeting_url = f"/meeting-room/{room_id}"
        
        booking.meeting_room_id = room_id
        booking.meeting_url = meeting_url
        db.session.commit()
        
        return {'name': room_id, 'url': meeting_url}, None
        
    except Exception as e:
        return None, f"Error creating meeting room: {str(e)}"

def create_meeting_room(booking_id):
    """Create a Daily.co meeting room for a booking"""
    try:
        # Check if Daily.co API key is configured
        if not DAILY_API_KEY or DAILY_API_KEY == 'your_daily_api_key_here':
            print(f"[DEBUG] Daily.co API key not configured, using fallback")
            return create_simple_meeting_room(booking_id)
        
        # Generate a unique room name with timestamp to avoid conflicts
        from datetime import datetime
        timestamp = int(datetime.now().timestamp())
        room_name = f"droply-{booking_id}-{timestamp}"
        
        print(f"[DEBUG] Creating meeting room for booking {booking_id}")
        print(f"[DEBUG] Room name: {room_name}")
        print(f"[DEBUG] API Key: {DAILY_API_KEY[:10]}...")
        
        # Create the room on Daily.co with minimal settings for free tier
        headers = {
            'Authorization': f'Bearer {DAILY_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Use minimal room data that works with free tier
        room_data = {
            'name': room_name,
            'privacy': 'public'  # Use public for free tier
        }
        
        print(f"[DEBUG] Room data: {room_data}")
        
        response = requests.post(
            f'{DAILY_API_URL}/rooms',
            headers=headers,
            json=room_data
        )
        
        print(f"[DEBUG] Response status: {response.status_code}")
        print(f"[DEBUG] Response text: {response.text}")
        
        if response.status_code == 200:
            room_info = response.json()
            room_url = room_info.get('url')
            
            print(f"[DEBUG] Room created successfully: {room_url}")
            
            # Update the booking with room info
            booking = Booking.query.get(booking_id)
            if booking:
                booking.meeting_room_id = room_name
                booking.meeting_url = room_url
                db.session.commit()
                print(f"[DEBUG] Booking updated with room info")
            
            return room_info, None
        elif response.status_code == 400 and "already exists" in response.text:
            # Room already exists, try to get the existing room info
            print(f"[DEBUG] Room already exists, retrieving existing room info")
            get_response = requests.get(
                f'{DAILY_API_URL}/rooms/{room_name}',
                headers=headers
            )
            if get_response.status_code == 200:
                room_info = get_response.json()
                room_url = room_info.get('url')
                booking = Booking.query.get(booking_id)
                if booking:
                    booking.meeting_room_id = room_name
                    booking.meeting_url = room_url
                    db.session.commit()
                return room_info, None
            else:
                return None, f"Error retrieving existing room: {get_response.text}"
        else:
            error_msg = f"Failed to create room: {response.text}"
            print(f"[DEBUG] {error_msg}")
            return None, error_msg
            
    except Exception as e:
        error_msg = f"Error creating room: {str(e)}"
        print(f"[DEBUG] {error_msg}")
        return None, error_msg

def get_meeting_token(room_name, user_id, is_owner=False):
    """Generate a meeting token for a user"""
    # For now, just return a simple token since Daily.co token generation is complex
    # In production, you'd want to implement proper token generation
    return f"simple-token-{user_id}-{is_owner}", None

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')  # Use environment variable
# For local development, use localhost. For production, use the actual domain
YOUR_DOMAIN = os.environ.get('YOUR_DOMAIN', 'http://localhost:5001')

# Production safeguards
def is_production_environment():
    """Check if we're running in production environment"""
    return os.environ.get('FLASK_ENV') == 'production' or os.environ.get('ENVIRONMENT') == 'production'

def validate_stripe_environment():
    """Validate that Stripe environment matches deployment environment"""
    if is_production_environment():
        if stripe.api_key.startswith('sk_test_'):
            raise ValueError("❌ PRODUCTION ERROR: Test Stripe key detected in production environment!")
        if not stripe.api_key.startswith('sk_live_'):
            raise ValueError("❌ PRODUCTION ERROR: Invalid Stripe key format for production!")
    else:
        # In development, warn if using live keys
        if stripe.api_key.startswith('sk_live_'):
            print("⚠️  WARNING: Live Stripe key detected in development environment!")

# Validate Stripe environment on startup
# Temporarily disabled for testing
# try:
#     validate_stripe_environment()
# except ValueError as e:
#     print(f"🚨 {e}")
#     # In production, this should cause the app to fail to start
#     if is_production_environment():
#         raise

# Load the model once when the app starts
# try:
#     model = SentenceTransformer('all-MiniLM-L6-v2')
# except Exception as e:
#     print(f"Error loading SentenceTransformer model: {e}")
#     model = None
model = None  # Temporarily disabled

@app.route('/')
def homepage():
    # Handle referral code from URL parameter
    referral_code = request.args.get('ref')
    if referral_code:
        # Store referral code in session for use during registration
        session['referral_code'] = referral_code
        print(f"Referral code stored in session: {referral_code}")
    
    # Redirect authenticated users to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('homepage.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    print(f"Register route accessed. Method: {request.method}")
    form = RegistrationForm()
    
    if request.method == 'POST':
        print(f"Form data: {request.form}")
        print(f"Form validation: {form.validate()}")
        if form.errors:
            print(f"Form errors: {form.errors}")
    
    if form.validate_on_submit():
        # Check if email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        
        if existing_user:
            flash('Email already exists.', 'error')
            return render_template('register.html', form=form)
        
        # Generate username from email
        username = form.email.data.split('@')[0]
        # Ensure username is unique
        base_username = username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1
        
        # Create new user
        user = User(
            username=username,
            email=form.email.data,
            full_name=form.email.data.split('@')[0]  # Use email prefix as full name
        )
        user.set_password(form.password.data)
        
        # Generate referral code for the new user
        user.generate_referral_code()
        
        db.session.add(user)
        db.session.commit()
        
        # Set up default availability (9-5 weekdays only)
        setup_default_availability(user)
        
        # Handle referral tracking if referral code is provided
        referral_code = request.args.get('ref') or request.form.get('referral_code') or session.get('referral_code')
        if referral_code:
            try:
                # Find the referrer by referral code
                referrer = User.query.filter_by(referral_code=referral_code).first()
                if referrer and referrer.id != user.id:  # Can't refer yourself
                    # Create the referral record
                    referral = Referral(
                        referrer_id=referrer.id,
                        referred_user_id=user.id,
                        referral_code=referral_code,
                        status='pending'
                    )
                    
                    # Update the referred user's referred_by field
                    user.referred_by = referrer.id
                    
                    db.session.add(referral)
                    db.session.commit()
                    
                    print(f"Referral tracked: {referrer.username} referred {user.username}")
                    
                    # Clear referral code from session after successful tracking
                    session.pop('referral_code', None)
            except Exception as e:
                print(f"Error tracking referral: {e}")
                # Don't fail registration if referral tracking fails
        
        # Log in user but redirect to onboarding
        login_user(user)
        print(f"New user registered: {user.email}, redirecting to onboarding")
        flash('Registration successful! Please complete your profile.', 'success')
        return redirect(url_for('onboarding'))
    
    return render_template('register.html', form=form)

@app.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    """Multi-step onboarding process"""
    print(f"Onboarding accessed by user: {current_user.email}")
    print(f"Request method: {request.method}")
    print(f"User profession: {current_user.profession}")
    print(f"User bio: {current_user.bio}")
    print(f"User industry: {current_user.industry}")
    
    if request.method == 'POST':
        try:
            # Handle JSON data from the new onboarding flow
            if request.is_json:
                data = request.get_json()
                
                # Handle username step
                if data.get('step') == 'username':
                    username = data.get('username', '').strip().lower()
                    if not username:
                        return jsonify({'success': False, 'message': 'Username is required'})
                    
                    # Check if username is available
                    existing_user = User.query.filter_by(username=username).first()
                    if existing_user and existing_user.id != current_user.id:
                        return jsonify({'success': False, 'message': 'Username is already taken'})
                    
                    # Update username
                    current_user.username = username
                    db.session.commit()
                    
                    return jsonify({
                        'success': True,
                        'message': 'Username set successfully!'
                    })
                
                # Handle profile completion step
                elif data.get('step') == 'profile':
                    # Update user profile with onboarding data
                    current_user.profession = data.get('profession', '')
                    current_user.bio = data.get('bio', '')
                    current_user.hourly_rate = data.get('hourly_rate', 0)
                    current_user.industry = data.get('industry', '')
                    current_user.is_available = True  # Set as available by default
                    
                    # Handle expertise tags
                    expertise = data.get('expertise', [])
                    if expertise:
                        current_user.specialty_tags = json.dumps(expertise)
                    else:
                        current_user.specialty_tags = json.dumps([])
                    
                    db.session.commit()
                    
                    return jsonify({
                        'success': True,
                        'message': 'Profile setup complete!'
                    })
            
            # Handle traditional form submission (fallback)
            form = OnboardingForm()
            if form.validate_on_submit():
                current_user.profession = form.profession.data
                current_user.bio = form.bio.data
                current_user.hourly_rate = form.hourly_rate.data or 0
                current_user.industry = form.industry.data
                current_user.is_available = True
                
                # Handle specialties from form data
                specialties = request.form.get('specialties')
                if specialties:
                    try:
                        specialties_list = json.loads(specialties)
                        current_user.specialty_tags = json.dumps(specialties_list)
                    except (json.JSONDecodeError, TypeError) as e:
                        print(f"DEBUG: Error parsing specialties: {e}")
                        current_user.specialty_tags = json.dumps([])
                else:
                    current_user.specialty_tags = json.dumps([])
                
                db.session.commit()
                flash('Profile setup complete!', 'success')
                return redirect(url_for('dashboard'))
        
        except Exception as e:
            print(f"Error in onboarding: {e}")
            return jsonify({
                'success': False,
                'message': 'An error occurred while saving your profile.'
            })
    
    # GET request - show the onboarding form
    print("Rendering onboarding template")
    print(f"User profile data: profession={current_user.profession}, bio={current_user.bio}, industry={current_user.industry}")
    form = OnboardingForm()
    return render_template('onboarding.html', form=form, expertise_mapping=EXPERTISE_MAPPING)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    form = LoginForm()
    
    # Clear any existing flash messages on GET request (when just visiting the page)
    if request.method == 'GET':
        # Clear flash messages from session to prevent showing old messages
        if '_flashes' in session:
            del session['_flashes']
    
    if form.validate_on_submit():
        # Try to find user by email first, then by username
        user = User.query.filter_by(email=form.email_or_username.data).first()
        if not user:
            user = User.query.filter_by(username=form.email_or_username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid email/username or password.', 'error')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('homepage'))

# Removed /profile/<username> route - use /expert/<username> instead

@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        try:
            # Update basic information
            current_user.full_name = request.form.get('full_name', '')
            current_user.profession = request.form.get('profession', '')
            current_user.bio = request.form.get('bio', '')
            current_user.hourly_rate = float(request.form.get('hourly_rate', 0) or 0)
            current_user.industry = request.form.get('industry', '')
            current_user.location = request.form.get('location', '')
            current_user.expertise = request.form.get('expertise', '')  # Legacy field
            current_user.expertise_1 = request.form.get('expertise_1', '')
            current_user.expertise_2 = request.form.get('expertise_2', '')
            current_user.expertise_3 = request.form.get('expertise_3', '')
            
            # Update social media links
            current_user.linkedin_url = request.form.get('linkedin', '')
            current_user.twitter_url = request.form.get('twitter', '')
            current_user.github_url = request.form.get('github', '')
            current_user.website_url = request.form.get('website', '')
            current_user.instagram_url = request.form.get('instagram', '')
            current_user.facebook_url = request.form.get('facebook', '')
            current_user.youtube_url = request.form.get('youtube', '')
            current_user.snapchat_url = request.form.get('snapchat', '')
            
            # Update availability
            current_user.is_available = 'is_available' in request.form
            
            # Handle profile picture upload
            if 'profile_picture' in request.files:
                file = request.files['profile_picture']
                if file and file.filename:
                    # Save the file
                    filename = f"profile_{current_user.id}_{int(time.time())}.{file.filename.split('.')[-1]}"
                    filepath = os.path.join('static', 'uploads', filename)
                    file.save(filepath)
                    current_user.profile_picture = f"/static/uploads/{filename}"
            
            db.session.commit()
            
            # Check if this is an AJAX request (auto-save)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': 'Profile updated successfully'})
            
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': str(e)}), 400
            
            flash('Error updating profile. Please try again.', 'error')
            return redirect(url_for('profile_setup'))
    
    return redirect(url_for('profile_setup'))

@app.route('/profile/setup')
@login_required
def profile_setup():
    """Profile setup page for signed-in users"""
    return render_template('profile_setup.html')

@app.route('/profile/preview/<username>')
@login_required
def profile_preview(username):
    """Preview profile as a visitor would see it"""
    user = User.query.filter_by(username=username).first_or_404()
    
    # Only allow users to preview their own profile
    if current_user.username != username:
        flash('You can only preview your own profile.', 'error')
        return redirect(url_for('profile_setup'))
    
    # Show the expert profile view for preview
    availability_rules = AvailabilityRule.query.filter_by(user_id=user.id).all()
    return render_template('user_profile.html', expert=user, availability_rules=availability_rules)

@app.route('/user/<username>')
@login_required
def user_profile(username):
    """View user profile for booking"""
    user = User.query.filter_by(username=username).first_or_404()
    
    # Get user's availability for booking
    availability_rules = AvailabilityRule.query.filter_by(user_id=user.id).all()
    
    return render_template('user_profile.html', expert=user, availability_rules=availability_rules)

@app.route('/user/<username>/book')
@login_required
def user_booking_times(username):
    """Select available booking times for a user"""
    try:
        user = User.query.filter_by(username=username).first_or_404()
        
        # Get user's availability rules
        availability_rules = AvailabilityRule.query.filter_by(user_id=user.id).all()
        
        # If user has no availability rules, set up default 9-5 weekdays
        if not availability_rules:
            print(f"User {user.username} has no availability rules, setting up default 9-5 weekdays")
            setup_default_availability(user)
            db.session.commit()
            # Refresh availability rules
            availability_rules = AvailabilityRule.query.filter_by(user_id=user.id).all()
        
        # Get current user's timezone for display
        current_user_timezone = current_user.timezone or 'America/New_York'
        user_timezone = user.timezone or 'America/New_York'
        
        # Get available times for the next 60 days
        available_times = []
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if availability_rules:
            for i in range(60):  # Next 60 days
                check_date = today + timedelta(days=i)
                
                try:
                    # Use the new timezone-aware function
                    slots = generate_available_slots_for_date(check_date, user, current_user_timezone)
                    for slot in slots:
                        # Only include future slots
                        if slot['start_time'].replace(tzinfo=None) > datetime.now():
                            available_times.append({
                                'datetime': slot['start_time'].replace(tzinfo=None),
                                'formatted_date': slot['date'].strftime('%B %d, %Y'),
                                'formatted_time': slot['formatted_time'],
                                'iso_datetime': slot['start_time'].replace(tzinfo=None).isoformat(),
                                'user_time': slot['expert_time']
                            })
                except Exception as e:
                    print(f"Error generating slots for date {check_date}: {e}")
                    continue
        
        return render_template('user_booking_times.html', 
                             expert=user, 
                             available_times=available_times,
                             has_availability=bool(availability_rules),
                             current_user_timezone=current_user_timezone,
                             user_timezone=user_timezone)
    except Exception as e:
        print(f"Error in user_booking_times: {e}")
        flash('An error occurred while loading booking times. Please try again.', 'error')
        return redirect(url_for('user_profile', username=username))


@app.route('/expert/<username>/book-immediate')
@login_required
def book_immediate_meeting(username):
    """Book an immediate meeting with an expert - Development only"""
    # Only allow in development environment
    if is_production_environment():
        flash('Immediate booking is not available in production.', 'error')
        return redirect(url_for('user_profile', username=username))
    
    expert = User.query.filter_by(username=username).first_or_404()
    
    # Check if expert is available
    if not expert.is_available:
        flash('This expert is not currently available for immediate meetings.', 'error')
        return redirect(url_for('user_profile', username=username))
    
    # Create immediate meeting time (starts in 5 minutes)
    from datetime import datetime, timedelta
    # Use Eastern Time for immediate bookings
    now = datetime.now(EASTERN_TIMEZONE)
    meeting_start = now + timedelta(minutes=5)  # Start in 5 minutes
    meeting_end = meeting_start + timedelta(minutes=30)  # 30 minute session
    
    # Format for the booking confirmation URL (same format as regular time slots)
    datetime_str = meeting_start.isoformat()
    
    # Debug logging
    print(f"DEBUG: Book Now - Expert: {expert.username}")
    print(f"DEBUG: Book Now - Meeting start: {meeting_start}")
    print(f"DEBUG: Book Now - Datetime string: {datetime_str}")
    
    # Redirect to the normal booking confirmation flow
    return redirect(url_for('booking_confirmation', 
                          expert=expert.username, 
                          datetime=datetime_str, 
                          duration=30))

@app.route('/dev/test-video-call')
@login_required
def test_video_call():
    """Development-only route to test video call UI without booking"""
    # Only allow in development environment
    if is_production_environment():
        flash('This feature is only available in development.', 'error')
        return redirect(url_for('homepage'))
    
    # Create a fake booking for testing
    fake_booking = {
        'id': 'test-123',
        'expert_name': 'Test Expert',
        'start_time': datetime.now(EASTERN_TIMEZONE),
        'duration': 30,
        'meeting_url': 'https://test.daily.co/test-room'  # This will be replaced with actual room
    }
    
    return render_template('meeting_daily.html', 
                          booking=fake_booking, 
                          is_test_mode=True)

@app.route('/settings')
@login_required
def settings():
    """Settings page"""
    return render_template('settings.html')

@app.route('/account')
@login_required
def account():
    """Account management page"""
    return render_template('account.html')

@app.route('/profile/update', methods=['POST'])
@login_required
def profile_update():
    """Update user profile via form submission"""
    try:
        # Get form data
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        username = request.form.get('username', '').strip()
        bio = request.form.get('bio', '').strip()
        profession = request.form.get('profession', '').strip()
        industry = request.form.get('industry', '').strip()
        location = request.form.get('location', '').strip()
        hourly_rate = request.form.get('hourly_rate', '').strip()
        linkedin = request.form.get('linkedin', '').strip()
        twitter = request.form.get('twitter', '').strip()
        github = request.form.get('github', '').strip()
        website = request.form.get('website', '').strip()
        instagram = request.form.get('instagram', '').strip()
        youtube = request.form.get('youtube', '').strip()
        language = request.form.get('language', '').strip()
        timezone = request.form.get('timezone', '').strip()
        email_notifications = request.form.get('email_notifications') == 'on'
        is_available = request.form.get('is_available') == 'on'
        
        # Update user profile
        if full_name:
            current_user.full_name = full_name
        if phone:
            current_user.phone = phone
        if username and username != current_user.username:
            # Check if username is available
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username is already taken', 'error')
                return redirect(url_for('account'))
            current_user.username = username
        if bio:
            current_user.bio = bio
        if profession:
            current_user.profession = profession
        if industry:
            current_user.industry = industry
        if location:
            current_user.location = location
        if hourly_rate:
            try:
                current_user.hourly_rate = float(hourly_rate)
            except ValueError:
                flash('Invalid hourly rate', 'error')
                return redirect(url_for('account'))
        if linkedin:
            current_user.linkedin_url = linkedin
        if twitter:
            current_user.twitter_url = twitter
        if github:
            current_user.github_url = github
        if website:
            current_user.website_url = website
        if instagram:
            current_user.instagram_url = instagram
        if youtube:
            current_user.youtube_url = youtube
        if language:
            current_user.language = language
        if timezone:
            current_user.timezone = timezone
        
        current_user.email_notifications = email_notifications
        current_user.is_available = is_available
            
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Failed to update profile: ' + str(e), 'error')
    
    return redirect(url_for('account'))

@app.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    """Delete user account permanently"""
    try:
        user_id = current_user.id
        user_email = current_user.email
        
        print(f"DEBUG: Starting deletion for user {user_id}")
        
        # Simple approach: just delete the user and let database handle cascading
        # First clear any self-references
        User.query.filter_by(referred_by=user_id).update({'referred_by': None})
        db.session.commit()
        
        # Delete the user
        db.session.delete(current_user)
        db.session.commit()
        
        print(f"DEBUG: User {user_id} deleted successfully")
        logout_user()
        
        return jsonify({'success': True, 'message': 'Account deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        print(f"DEBUG: Error deleting account: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/test-account')
def test_account():
    """Test account page without authentication"""
    # Create a simple test template
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Account Page</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            .test-content { background: #f0f0f0; padding: 20px; border: 1px solid #ccc; }
        </style>
    </head>
    <body>
        <h1>Test Account Page</h1>
        <div class="test-content">
            <p>This is a test to see if the account page template renders correctly.</p>
            <p>If you can see this, the basic template structure is working.</p>
        </div>
    </body>
    </html>
    '''

@app.route('/referrals')
@login_required
def referrals():
    """Referrals page"""
    return render_template('referrals.html')

@app.route('/watch')
@login_required
def watch():
    """Display the Watch feed with user profiles"""
    # Generate fake user data for the feed
    fake_users = [
        {
            'id': 1,
            'name': 'Sarah Chen',
            'title': 'UX Designer',
            'company': 'Google',
            'bio': 'Creating beautiful digital experiences ✨',
            'image': 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=400&h=400&fit=crop&crop=face',
            'rating': 4.9,
            'reviews': 127,
            'price': 75
        },
        {
            'id': 2,
            'name': 'Marcus Johnson',
            'title': 'Marketing Strategist',
            'company': 'Meta',
            'bio': 'Helping brands grow through data-driven marketing 📈',
            'image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face',
            'rating': 4.8,
            'reviews': 89,
            'price': 95
        },
        {
            'id': 3,
            'name': 'Emily Rodriguez',
            'title': 'Product Manager',
            'company': 'Apple',
            'bio': 'Building products that matter 🚀',
            'image': 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop&crop=face',
            'rating': 4.9,
            'reviews': 156,
            'price': 120
        },
        {
            'id': 4,
            'name': 'David Kim',
            'title': 'Software Engineer',
            'company': 'Netflix',
            'bio': 'Full-stack developer passionate about clean code 💻',
            'image': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face',
            'rating': 4.7,
            'reviews': 203,
            'price': 85
        },
        {
            'id': 5,
            'name': 'Lisa Thompson',
            'title': 'Data Scientist',
            'company': 'Tesla',
            'bio': 'Turning data into insights that drive decisions 📊',
            'image': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=400&fit=crop&crop=face',
            'rating': 4.8,
            'reviews': 91,
            'price': 110
        },
        {
            'id': 6,
            'name': 'Alex Morgan',
            'title': 'Content Creator',
            'company': 'YouTube',
            'bio': 'Storytelling through video and social media 🎬',
            'image': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop&crop=face',
            'rating': 4.6,
            'reviews': 78,
            'price': 65
        },
        {
            'id': 7,
            'name': 'Zoe Williams',
            'title': 'Brand Strategist',
            'company': 'Nike',
            'bio': 'Building brands that inspire and connect 🌟',
            'image': 'https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=400&h=400&fit=crop&crop=face',
            'rating': 4.9,
            'reviews': 134,
            'price': 100
        },
        {
            'id': 8,
            'name': 'Ryan Patel',
            'title': 'Sales Director',
            'company': 'Salesforce',
            'bio': 'Helping teams close more deals and build relationships 🤝',
            'image': 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&h=400&fit=crop&crop=face',
            'rating': 4.7,
            'reviews': 167,
            'price': 90
        },
        {
            'id': 9,
            'name': 'Maya Singh',
            'title': 'Financial Advisor',
            'company': 'Goldman Sachs',
            'bio': 'Making finance accessible and understandable 💰',
            'image': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&h=400&fit=crop&crop=face',
            'rating': 4.8,
            'reviews': 112,
            'price': 125
        },
        {
            'id': 10,
            'name': 'James Wilson',
            'title': 'Startup Founder',
            'company': 'TechCrunch',
            'bio': 'Building the future, one startup at a time 🚀',
            'image': 'https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=400&h=400&fit=crop&crop=face',
            'rating': 4.9,
            'reviews': 89,
            'price': 150
        },
        {
            'id': 11,
            'name': 'Nina Chen',
            'title': 'Graphic Designer',
            'company': 'Adobe',
            'bio': 'Creating visual stories that captivate and inspire 🎨',
            'image': 'https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?w=400&h=400&fit=crop&crop=face',
            'rating': 4.7,
            'reviews': 145,
            'price': 70
        },
        {
            'id': 12,
            'name': 'Carlos Mendez',
            'title': 'Operations Manager',
            'company': 'Amazon',
            'bio': 'Optimizing processes for maximum efficiency ⚡',
            'image': 'https://images.unsplash.com/photo-1507591064344-4c6ce005b128?w=400&h=400&fit=crop&crop=face',
            'rating': 4.6,
            'reviews': 98,
            'price': 80
        },
        {
            'id': 13,
            'name': 'Aisha Okafor',
            'title': 'HR Specialist',
            'company': 'Microsoft',
            'bio': 'Building inclusive teams and company culture 🤗',
            'image': 'https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=400&h=400&fit=crop&crop=face',
            'rating': 4.8,
            'reviews': 76,
            'price': 85
        },
        {
            'id': 14,
            'name': 'Tom Anderson',
            'title': 'Business Analyst',
            'company': 'Deloitte',
            'bio': 'Transforming data into strategic insights 📈',
            'image': 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&h=400&fit=crop&crop=face',
            'rating': 4.7,
            'reviews': 123,
            'price': 95
        },
        {
            'id': 15,
            'name': 'Priya Sharma',
            'title': 'Research Scientist',
            'company': 'MIT',
            'bio': 'Pushing the boundaries of AI and machine learning 🤖',
            'image': 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&h=400&fit=crop&crop=face',
            'rating': 4.9,
            'reviews': 67,
            'price': 140
        }
    ]
    
    return render_template('watch.html', users=fake_users)

# Duplicate route removed - using the first definition

@app.route('/search')
@login_required
def search():
    """Search users page for signed-in users"""
    # Get search query and category
    search_query = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip().lower()
    
    # Base query for available users - exclude current user
    query = User.query.filter(
        User.is_available == True, 
        User.full_name.isnot(None),
        User.id != current_user.id  # Exclude current user from results
    )
    
    # Apply category filter if provided
    if category:
        # Map category names to search terms
        category_mapping = {
            'top': [],  # Special case for top experts - will be handled separately
            'favorites': [],  # Special case for favorites - will be handled separately
            'home': ['home', 'interior', 'design', 'decor', 'renovation', 'construction', 'architecture', 'furniture', 'decorating'],
            'business': ['business', 'consulting', 'strategy', 'management', 'entrepreneur', 'startup', 'finance', 'marketing', 'sales'],
            'design': ['design', 'ui', 'ux', 'graphic', 'visual', 'creative', 'art', 'branding', 'illustration', 'style', 'beauty', 'fashion'],
            'marketing': ['marketing', 'digital marketing', 'social media', 'seo', 'advertising', 'brand', 'growth', 'content'],
            'finance': ['finance', 'accounting', 'investment', 'financial', 'tax', 'budget', 'money', 'wealth'],
            'health': ['health', 'fitness', 'wellness', 'nutrition', 'medical', 'therapy', 'coaching', 'mental health'],
            'education': ['education', 'teaching', 'tutoring', 'training', 'learning', 'academic', 'course', 'mentor', 'astrology', 'spiritual']
        }
        
        if category in category_mapping:
            if category == 'top':
                # Special case for top experts - filter by is_top_expert flag
                query = query.filter(User.is_top_expert == True)
            elif category == 'favorites':
                # Special case for favorites - filter by user's favorites
                from models import Favorite
                favorites = Favorite.query.filter_by(user_id=current_user.id).all()
                expert_ids = [f.expert_id for f in favorites]
                
                if expert_ids:
                    query = query.filter(User.id.in_(expert_ids))
                else:
                    # Return empty list if no favorites
                    experts = []
                    from datetime import datetime, timedelta
                    return render_template('search.html', 
                                         users=experts, 
                                         now=datetime.now(), 
                                         timedelta=timedelta,
                                         current_user_favorites=[])
            else:
                search_terms = category_mapping[category]
                category_conditions = []
                for term in search_terms:
                    category_conditions.append(
                        or_(
                            User.expertise.ilike(f'%{term}%'),
                            User.profession.ilike(f'%{term}%'),
                            User.industry.ilike(f'%{term}%'),
                            User.bio.ilike(f'%{term}%'),
                            User.specialty_tags.ilike(f'%{term}%')
                        )
                    )
                if category_conditions:
                    query = query.filter(or_(*category_conditions))
    
    # Apply semantic search if provided
    if search_query:
        # Split search query into keywords for better matching
        search_keywords = search_query.lower().split()
        
        # Create search conditions for each keyword
        search_conditions = []
        for keyword in search_keywords:
            if len(keyword) > 2:  # Only search for keywords with 3+ characters
                keyword_term = f'%{keyword}%'
                search_conditions.append(
                    or_(
                        User.username.ilike(keyword_term),
                        User.full_name.ilike(keyword_term),
                        User.expertise.ilike(keyword_term),
                        User.profession.ilike(keyword_term),
                        User.industry.ilike(keyword_term),
                        User.bio.ilike(keyword_term),
                        User.specialty_tags.ilike(keyword_term),
                        User.location.ilike(keyword_term)
                    )
                )
        
        if search_conditions:
            query = query.filter(or_(*search_conditions))
    
    # Get all experts and sort by relevance
    experts = query.all()
    
    # Sort experts by relevance and priority
    def sort_score(expert):
        score = 0
        
        # Top experts get highest priority
        if expert.is_top_expert:
            score += 1000
        
        # If there's a search query, add relevance score
        if search_query:
            search_lower = search_query.lower()
            
            # Check exact matches first
            if search_lower in (expert.full_name or '').lower():
                score += 10
            if search_lower in (expert.expertise or '').lower():
                score += 8
            if search_lower in (expert.profession or '').lower():
                score += 6
            if search_lower in (expert.bio or '').lower():
                score += 4
            
            # Check keyword matches
            for keyword in search_query.lower().split():
                if len(keyword) > 2:
                    if keyword in (expert.full_name or '').lower():
                        score += 3
                    if keyword in (expert.expertise or '').lower():
                        score += 2
                    if keyword in (expert.profession or '').lower():
                        score += 2
                    if keyword in (expert.bio or '').lower():
                        score += 1
        
        return score
    
    experts = sorted(experts, key=sort_score, reverse=True)
    
    # Import datetime for template
    from datetime import datetime, timedelta
    
    # Get current user's favorites for template
    current_user_favorites = []
    if current_user.is_authenticated:
        from models import Favorite
        favorites = Favorite.query.filter_by(user_id=current_user.id).all()
        current_user_favorites = [f.expert_id for f in favorites]

    
    return render_template('search.html', 
                         users=experts, 
                         now=datetime.now(), 
                         timedelta=timedelta,
                         current_user_favorites=current_user_favorites)



@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    # Get upcoming bookings as provider
    provider_bookings = Booking.query.filter_by(expert_id=current_user.id).order_by(Booking.created_at.desc()).limit(10).all()
    
    # Get upcoming bookings as client
    client_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).limit(10).all()
    
    # Get recent time slots - TimeSlot model not available in current version
    time_slots = []
    
    return render_template('dashboard.html', 
                         provider_bookings=provider_bookings,
                         client_bookings=client_bookings)

@app.route('/debug-user')
@login_required
def debug_user():
    """Debug endpoint to check user status"""
    return jsonify({
        'user_id': current_user.id,
        'email': current_user.email,
        'has_google_token': bool(current_user.google_calendar_token),
        'google_calendar_connected': current_user.google_calendar_connected,
        'google_calendar_id': current_user.google_calendar_id
    })

@app.route('/availability')
@login_required
def availability():
    """Availability management page"""
    print(f"DEBUG: Availability page - User {current_user.id}")
    print(f"DEBUG: google_calendar_token: {bool(current_user.google_calendar_token)}")
    print(f"DEBUG: google_calendar_connected: {current_user.google_calendar_connected}")
    
    # Allow users to access availability page even without Google Calendar connected
    # The frontend will handle showing the connection status and options
    return render_template('availability.html')

# @app.route('/calendar/add', methods=['GET', 'POST'])
# @login_required
# def add_time_slot():
#     """Add new time slot - Temporarily disabled due to missing TimeSlot model"""
#     return redirect(url_for('dashboard'))

# @app.route('/booking/<int:slot_id>', methods=['GET', 'POST'])
# def book_session(slot_id):
#     """Book a session - Temporarily disabled due to missing TimeSlot model"""
#     flash('Booking functionality is temporarily unavailable.', 'error')
#     return redirect(url_for('homepage'))

@app.route('/test-checkout/<int:booking_id>')
def test_checkout(booking_id):
    """Test endpoint to debug checkout issues"""
    return f"Test endpoint reached with booking_id: {booking_id}"

@app.route('/create-checkout-session/<int:booking_id>', methods=['POST', 'GET'])
def create_checkout_session(booking_id):
    """Create Stripe checkout session"""
    try:
        print(f"DEBUG: create_checkout_session called with booking_id: {booking_id}")
        
        # Basic validation
        if not stripe.api_key:
            print("DEBUG: Stripe API key not configured")
            flash('Payment system not configured. Please contact support.', 'error')
            return redirect(url_for('homepage'))
        
        # Get booking
        booking = Booking.query.get(booking_id)
        if not booking:
            print(f"DEBUG: Booking {booking_id} not found")
            flash('Booking not found. Please try again.', 'error')
            return redirect(url_for('homepage'))
        
        # Get expert
        expert = User.query.get(booking.expert_id)
        if not expert:
            print("DEBUG: Expert not found for booking")
            flash('Expert not found', 'error')
            return redirect(url_for('homepage'))
        
        # Validate payment amount
        if not booking.payment_amount or booking.payment_amount <= 0:
            print(f"DEBUG: Invalid payment amount: {booking.payment_amount}")
            flash('Invalid payment amount', 'error')
            return redirect(url_for('user_profile', username=expert.username))
        
        print(f"DEBUG: Creating Stripe checkout session...")
        print(f"DEBUG: YOUR_DOMAIN: {YOUR_DOMAIN}")
        
        # Create checkout session with simplified error handling
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Session with {expert.full_name or expert.username}',
                        'description': f'{booking.duration}-minute video consultation',
                    },
                    'unit_amount': int(booking.payment_amount * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'{YOUR_DOMAIN}/booking/success/{booking.id}',
            cancel_url=f'{YOUR_DOMAIN}/user/{expert.username}',
            metadata={'booking_id': booking.id}
        )
        
        print(f"DEBUG: Stripe checkout session created successfully: {checkout_session.id}")
        
        booking.stripe_session_id = checkout_session.id
        db.session.commit()
        
        return redirect(checkout_session.url, code=303)
        
    except stripe.StripeError as e:
        print(f"DEBUG: Stripe error: {str(e)}")
        flash(f'Payment system error: {str(e)}', 'error')
        return redirect(url_for('homepage'))
    except Exception as e:
        print(f"DEBUG: General error: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('Payment processing error. Please try again or contact support.', 'error')
        return redirect(url_for('homepage'))

@app.route('/booking/success/<int:booking_id>')
def booking_success(booking_id):
    """Booking success page - redirects to bookings with success message"""
    booking = Booking.query.get_or_404(booking_id)
    booking.payment_status = 'paid'
    # Do NOT auto-confirm; leave as 'pending' for expert to accept/decline
    db.session.commit()
    
    # Process referral reward if applicable
    try:
        process_referral_reward_for_booking(booking_id)
    except Exception as e:
        print(f"Error processing referral reward: {e}")
        # Don't fail the booking success if referral processing fails
    
    flash('🎉 Payment successful! Your booking request has been sent to the expert for approval.', 'success')
    return redirect(url_for('bookings'))

@app.route('/booking/cancel/<int:booking_id>')
def booking_cancel(booking_id):
    """Handle booking cancellation from Stripe checkout"""
    booking = Booking.query.get_or_404(booking_id)
    
    # If payment was never completed, just delete the booking and redirect to expert profile
    if booking.payment_status in ['pending', 'cancelled']:
        expert = User.query.get(booking.expert_id)
        expert_username = expert.username if expert else 'unknown'
        
        # Delete the incomplete booking
        db.session.delete(booking)
        db.session.commit()
        
        # Redirect back to user profile
        return redirect(url_for('user_profile', username=expert_username))
    
    # If payment was completed, show the cancel page (this shouldn't happen from Stripe cancel)
    booking.status = 'cancelled'
    booking.payment_status = 'cancelled'
    db.session.commit()
    
    return render_template('cancel.html', booking=booking)

@app.route('/export/calendar/<username>')
def export_calendar(username):
    """Export user calendar as iCal"""
    user = User.query.filter_by(username=username).first_or_404()
    
    # For now, just redirect to the user's profile
    # In the future, this could generate an actual iCal file
    flash('Calendar export feature coming soon!', 'info')
    return redirect(url_for('user_profile', username=username))

@app.route('/bookings')
@login_required
def bookings():
    """View user's bookings and calendar"""
    from models import Booking, User
    from datetime import datetime, timezone
    from sqlalchemy import func
    
    now = datetime.now(EASTERN_TIMEZONE)
    
    # Bookings where the user is the booker (client) - only show paid bookings
    upcoming_as_client = Booking.query.filter(
        (Booking.user_id == current_user.id) &
        (func.datetime(Booking.start_time) >= now.replace(tzinfo=None)) &
        (Booking.payment_status == 'paid')
    ).order_by(Booking.start_time.asc()).all()
    
    past_as_client = Booking.query.filter(
        (Booking.user_id == current_user.id) &
        (func.datetime(Booking.start_time) < now.replace(tzinfo=None)) &
        (Booking.payment_status == 'paid')
    ).order_by(Booking.start_time.desc()).all()
    
    # Bookings where the user is the expert (provider) - only show paid bookings
    upcoming_as_expert = Booking.query.filter(
        (Booking.expert_id == current_user.id) &
        (func.datetime(Booking.start_time) >= now.replace(tzinfo=None)) &
        (Booking.payment_status == 'paid')
    ).order_by(Booking.start_time.asc()).all()
    
    past_as_expert = Booking.query.filter(
        (Booking.expert_id == current_user.id) &
        (func.datetime(Booking.start_time) < now.replace(tzinfo=None)) &
        (Booking.payment_status == 'paid')
    ).order_by(Booking.start_time.desc()).all()
    
    # Debug prints
    print(f"DEBUG: Current user ID: {current_user.id}")
    print(f"DEBUG: Current time: {now}")
    print(f"DEBUG: Upcoming as expert count: {len(upcoming_as_expert)}")
    print(f"DEBUG: Past as expert count: {len(past_as_expert)}")
    for booking in upcoming_as_expert:
        print(f"DEBUG: Upcoming booking ID {booking.id}, start_time: {booking.start_time}, status: {booking.status}")
    
    # Convert times to local timezone for display
    def convert_booking_times(booking_list):
        for booking in booking_list:
            booking.start_time_local = convert_to_local_time(booking.start_time)
            booking.end_time_local = convert_to_local_time(booking.end_time)
        return booking_list
    
    upcoming_as_client = convert_booking_times(upcoming_as_client)
    past_as_client = convert_booking_times(past_as_client)
    upcoming_as_expert = convert_booking_times(upcoming_as_expert)
    past_as_expert = convert_booking_times(past_as_expert)
    
    return render_template('bookings.html', 
                         user=current_user, 
                         upcoming_as_client=upcoming_as_client,
                         past_as_client=past_as_client,
                         upcoming_as_expert=upcoming_as_expert,
                         past_as_expert=past_as_expert,
                         now=now)

@app.route('/booking/accept/<int:booking_id>')
@login_required
def accept_booking(booking_id):
    """Accept a booking request"""
    booking = Booking.query.get_or_404(booking_id)
    if booking.expert_id != current_user.id:
        flash('You are not authorized to accept this booking.', 'error')
        return redirect(url_for('bookings'))
    if booking.status != 'pending':
        flash('This booking cannot be accepted.', 'error')
        return redirect(url_for('bookings'))
    booking.status = 'confirmed'
    db.session.commit()
    flash('✅ Booking accepted! The client has been notified.', 'success')
    return redirect(url_for('bookings'))

@app.route('/booking/decline/<int:booking_id>')
@login_required
def decline_booking(booking_id):
    """Decline a booking request"""
    booking = Booking.query.get_or_404(booking_id)
    if booking.expert_id != current_user.id:
        flash('You are not authorized to decline this booking.', 'error')
        return redirect(url_for('bookings'))
    if booking.status != 'pending':
        flash('This booking cannot be declined.', 'error')
        return redirect(url_for('bookings'))
    
    try:
        # Process full refund if payment was made
        if booking.payment_status == 'paid' and booking.stripe_session_id:
            # Get the payment intent from the session
            session = stripe.checkout.Session.retrieve(booking.stripe_session_id)
            if session.payment_intent:
                # Full refund for expert decline
                refund_amount = int(booking.payment_amount * 100)  # Convert to cents
                
                # Process the refund through Stripe
                refund = stripe.Refund.create(
                    payment_intent=session.payment_intent,
                    amount=refund_amount,
                    reason='requested_by_customer',
                    metadata={
                        'booking_id': booking.id,
                        'refund_reason': 'declined_by_expert',
                        'cancelled_by': 'expert'
                    }
                )
                
                booking.status = 'declined'
                booking.payment_status = 'refunded'
                flash(f'❌ Booking declined. Full refund of ${refund_amount/100:.2f} processed.', 'warning')
            else:
                booking.status = 'declined'
                booking.payment_status = 'refunded'
                flash('❌ Booking declined but refund could not be processed.', 'warning')
        else:
            # No payment to refund
            booking.status = 'declined'
            booking.payment_status = 'cancelled'
            flash('❌ Booking declined successfully.', 'warning')
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error processing decline: {str(e)}', 'error')
        return redirect(url_for('bookings'))
    
    return redirect(url_for('bookings'))

@app.route('/booking/cancel-by-client/<int:booking_id>')
@login_required
def cancel_booking_by_client(booking_id):
    """Cancel a booking by the client who made it"""
    print(f"[DEBUG] Cancel booking by client called for booking {booking_id}")
    booking = Booking.query.get_or_404(booking_id)
    
    print(f"[DEBUG] Booking found: {booking.id}, Status: {booking.status}")
    print(f"[DEBUG] Current user: {current_user.id}, Booking user: {booking.user_id}")
    
    if booking.user_id != current_user.id:
        print(f"[DEBUG] User not authorized to cancel booking")
        flash('You are not authorized to cancel this booking.', 'error')
        return redirect(url_for('bookings'))
    if booking.status not in ['pending', 'confirmed']:
        print(f"[DEBUG] Booking cannot be cancelled - status: {booking.status}")
        flash('This booking cannot be cancelled.', 'error')
        return redirect(url_for('bookings'))
    
    from datetime import datetime, timedelta
    now = datetime.now()
    time_until_booking = booking.start_time - now
    
    print(f"[DEBUG] Time until booking: {time_until_booking}")
    print(f"[DEBUG] 24 hour check: {time_until_booking < timedelta(hours=24)}")
    
    # Check 24-hour cancellation policy
    if time_until_booking < timedelta(hours=24):
        print(f"[DEBUG] Cancellation blocked - within 24 hours")
        flash('Bookings cannot be cancelled within 24 hours of the session.', 'error')
        return redirect(url_for('bookings'))
    
    try:
        # Process refund if payment was made
        if booking.payment_status == 'paid' and booking.stripe_session_id:
            # Get the payment intent from the session
            session = stripe.checkout.Session.retrieve(booking.stripe_session_id)
            if session.payment_intent:
                # Calculate refund amount based on cancellation policy
                if time_until_booking >= timedelta(hours=24):
                    # Full refund if cancelled 24+ hours before
                    refund_amount = int(booking.payment_amount * 100)  # Convert to cents
                    refund_reason = 'cancelled_by_client_full'
                else:
                    # Partial refund (platform fee is non-refundable)
                    platform_fee = max(5.0, booking.payment_amount * 0.10)
                    refund_amount = int((booking.payment_amount - platform_fee) * 100)
                    refund_reason = 'cancelled_by_client_partial'
                
                # Process the refund through Stripe
                refund = stripe.Refund.create(
                    payment_intent=session.payment_intent,
                    amount=refund_amount,
                    reason='requested_by_customer',
                    metadata={
                        'booking_id': booking.id,
                        'refund_reason': refund_reason,
                        'cancelled_by': 'client'
                    }
                )
                
                # Update booking status
                booking.status = 'cancelled'
                booking.payment_status = 'refunded'
                
                # Handle expert clawback if they were already paid
                if booking.status == 'confirmed':
                    expert = User.query.get(booking.expert_id)
                    if expert and expert.pending_balance > 0:
                        # Calculate expert's portion that needs to be clawed back
                        expert_portion = booking.payment_amount * 0.90  # After platform fee
                        expert.pending_balance = max(0, expert.pending_balance - expert_portion)
                        expert.total_earnings = max(0, expert.total_earnings - expert_portion)
                
                flash(f'✅ Booking cancelled successfully. Refund of ${refund_amount/100:.2f} processed.', 'success')
            else:
                flash('❌ Booking cancelled but refund could not be processed.', 'warning')
        else:
            # No payment to refund
            print(f"[DEBUG] No payment to refund, cancelling booking")
            booking.status = 'cancelled'
            booking.payment_status = 'cancelled'
            flash('❌ Booking cancelled successfully.', 'success')
        
        print(f"[DEBUG] Committing cancellation to database")
        db.session.commit()
        print(f"[DEBUG] Cancellation completed successfully")
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error processing cancellation: {str(e)}', 'error')
        return redirect(url_for('bookings'))
    
    return redirect(url_for('bookings'))

@app.route('/api/booking/cancel-by-client/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking_by_client_ajax(booking_id):
    """Cancel a booking by the client who made it - AJAX endpoint"""
    print(f"[DEBUG] AJAX Cancel booking by client called for booking {booking_id}")
    booking = Booking.query.get_or_404(booking_id)
    
    print(f"[DEBUG] Booking found: {booking.id}, Status: {booking.status}")
    print(f"[DEBUG] Current user: {current_user.id}, Booking user: {booking.user_id}")
    
    if booking.user_id != current_user.id:
        print(f"[DEBUG] User not authorized to cancel booking")
        return jsonify({
            'success': False,
            'message': 'You are not authorized to cancel this booking.',
            'type': 'error'
        }), 403
    
    if booking.status not in ['pending', 'confirmed']:
        print(f"[DEBUG] Booking cannot be cancelled - status: {booking.status}")
        return jsonify({
            'success': False,
            'message': 'This booking cannot be cancelled.',
            'type': 'error'
        }), 400
    
    from datetime import datetime, timedelta
    now = datetime.now()
    time_until_booking = booking.start_time - now
    
    print(f"[DEBUG] Time until booking: {time_until_booking}")
    print(f"[DEBUG] 24 hour check: {time_until_booking < timedelta(hours=24)}")
    
    # Check 24-hour cancellation policy
    if time_until_booking < timedelta(hours=24):
        print(f"[DEBUG] Cancellation blocked - within 24 hours")
        return jsonify({
            'success': False,
            'message': 'Bookings cannot be cancelled within 24 hours of the session.',
            'type': 'error'
        }), 400
    
    try:
        # Process refund if payment was made
        if booking.payment_status == 'paid' and booking.stripe_session_id:
            session = stripe.checkout.Session.retrieve(booking.stripe_session_id)
            if session.payment_intent:
                refund_amount = int(booking.payment_amount * 100)
                refund = stripe.Refund.create(
                    payment_intent=session.payment_intent,
                    amount=refund_amount,
                    reason='requested_by_customer',
                    metadata={
                        'booking_id': booking.id,
                        'refund_reason': 'cancelled_by_client_full',
                        'cancelled_by': 'client'
                    }
                )
                booking.status = 'cancelled'
                booking.payment_status = 'refunded'
                
                # Update expert earnings if booking was confirmed
                if booking.status == 'confirmed':
                    expert = User.query.get(booking.expert_id)
                    if expert and expert.pending_balance > 0:
                        expert_portion = booking.payment_amount * 0.90
                        expert.pending_balance = max(0, expert.pending_balance - expert_portion)
                        expert.total_earnings = max(0, expert.total_earnings - expert_portion)
                
                print(f"[DEBUG] Committing cancellation to database")
                db.session.commit()
                print(f"[DEBUG] Cancellation completed successfully")
                
                return jsonify({
                    'success': True,
                    'message': f'✅ Booking cancelled successfully. Refund of ${refund_amount/100:.2f} processed.',
                    'type': 'success'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '❌ Booking cancelled but refund could not be processed.',
                    'type': 'warning'
                })
        else:
            print(f"[DEBUG] No payment to refund, cancelling booking")
            booking.status = 'cancelled'
            booking.payment_status = 'cancelled'
            print(f"[DEBUG] Committing cancellation to database")
            db.session.commit()
            print(f"[DEBUG] Cancellation completed successfully")
            
            return jsonify({
                'success': True,
                'message': '❌ Booking cancelled successfully.',
                'type': 'success'
            })
            
    except Exception as e:
        db.session.rollback()
        print(f"[DEBUG] Error processing cancellation: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'❌ Error processing cancellation: {str(e)}',
            'type': 'error'
        }), 500

@app.route('/api/booking/cancel-by-expert/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking_by_expert_ajax(booking_id):
    """Cancel a booking by the expert - AJAX endpoint"""
    print(f"[DEBUG] AJAX Cancel booking by expert called for booking {booking_id}")
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.expert_id != current_user.id:
        return jsonify({
            'success': False,
            'message': 'You are not authorized to cancel this booking.',
            'type': 'error'
        }), 403
    
    if booking.status != 'confirmed':
        return jsonify({
            'success': False,
            'message': 'This booking cannot be cancelled.',
            'type': 'error'
        }), 400
    
    try:
        # Process full refund if payment was made
        if booking.payment_status == 'paid' and booking.stripe_session_id:
            session = stripe.checkout.Session.retrieve(booking.stripe_session_id)
            if session.payment_intent:
                refund_amount = int(booking.payment_amount * 100)
                refund = stripe.Refund.create(
                    payment_intent=session.payment_intent,
                    amount=refund_amount,
                    reason='requested_by_customer',
                    metadata={
                        'booking_id': booking.id,
                        'refund_reason': 'cancelled_by_expert_full',
                        'cancelled_by': 'expert'
                    }
                )
                booking.status = 'cancelled'
                booking.payment_status = 'refunded'
                
                # Update expert earnings
                expert = User.query.get(booking.expert_id)
                if expert and expert.pending_balance > 0:
                    expert_portion = booking.payment_amount * 0.90
                    expert.pending_balance = max(0, expert.pending_balance - expert_portion)
                    expert.total_earnings = max(0, expert.total_earnings - expert_portion)
                
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': f'✅ Booking cancelled successfully. Full refund of ${refund_amount/100:.2f} processed for client.',
                    'type': 'success'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '❌ Booking cancelled but refund could not be processed.',
                    'type': 'warning'
                })
        else:
            booking.status = 'cancelled'
            booking.payment_status = 'cancelled'
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '❌ Booking cancelled successfully.',
                'type': 'success'
            })
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'❌ Error processing cancellation: {str(e)}',
            'type': 'error'
        }), 500

@app.route('/booking/cancel-by-expert/<int:booking_id>')
@login_required
def cancel_booking_by_expert(booking_id):
    """Cancel a booking by the expert (gives full refund to client)"""
    booking = Booking.query.get_or_404(booking_id)
    if booking.expert_id != current_user.id:
        flash('You are not authorized to cancel this booking.', 'error')
        return redirect(url_for('bookings'))
    if booking.status != 'confirmed':
        flash('This booking cannot be cancelled.', 'error')
        return redirect(url_for('bookings'))
    
    try:
        # Process full refund if payment was made
        if booking.payment_status == 'paid' and booking.stripe_session_id:
            # Get the payment intent from the session
            session = stripe.checkout.Session.retrieve(booking.stripe_session_id)
            if session.payment_intent:
                # Full refund for expert cancellation
                refund_amount = int(booking.payment_amount * 100)  # Convert to cents
                
                # Process the refund through Stripe
                refund = stripe.Refund.create(
                    payment_intent=session.payment_intent,
                    amount=refund_amount,
                    reason='requested_by_customer',
                    metadata={
                        'booking_id': booking.id,
                        'refund_reason': 'cancelled_by_expert',
                        'cancelled_by': 'expert'
                    }
                )
                
                # Update booking status
                booking.status = 'cancelled'
                booking.payment_status = 'refunded'
                
                # Handle expert clawback since they were already paid
                expert = User.query.get(booking.expert_id)
                if expert and expert.pending_balance > 0:
                    # Calculate expert's portion that needs to be clawed back
                    expert_portion = booking.payment_amount * 0.90  # After platform fee
                    expert.pending_balance = max(0, expert.pending_balance - expert_portion)
                    expert.total_earnings = max(0, expert.total_earnings - expert_portion)
                
                flash(f'❌ Booking cancelled. Full refund of ${refund_amount/100:.2f} processed.', 'warning')
            else:
                booking.status = 'cancelled'
                booking.payment_status = 'refunded'
                flash('❌ Booking cancelled but refund could not be processed.', 'warning')
        else:
            # No payment to refund
            booking.status = 'cancelled'
            booking.payment_status = 'cancelled'
            flash('❌ Booking cancelled successfully.', 'warning')
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error processing cancellation: {str(e)}', 'error')
        return redirect(url_for('bookings'))
    
    return redirect(url_for('bookings'))

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Expertise tag mapping
EXPERTISE_MAPPING = {
    'python': 'Python',
    'javascript': 'JavaScript',
    'react': 'React',
    'ai': 'AI/ML',
    'webdev': 'Web Development',
    'mobile': 'Mobile Development',
    'data': 'Data Science',
    'cybersecurity': 'Cybersecurity',
    'strategy': 'Strategy',
    'startups': 'Startups',
    'fundraising': 'Fundraising',
    'operations': 'Operations',
    'leadership': 'Leadership',
    'finance': 'Finance',
    'trading': 'Trading',
    'money': 'Money Management',
    'digital': 'Digital Marketing',
    'social': 'Social Media',
    'seo': 'SEO',
    'content': 'Content Marketing',
    'branding': 'Branding',
    'coaching': 'Life Coaching',
    'fitness': 'Fitness',
    'nutrition': 'Nutrition',
    'wellness': 'Wellness',
    'therapy': 'Therapy',
    'counseling': 'Counseling',
    'education': 'Education',
    'teaching': 'Teaching',
    'tutoring': 'Tutoring',
    'mentoring': 'Mentoring',
    'training': 'Training',
    'consulting': 'Consulting',
    'design': 'Design',
    'ui': 'UI/UX Design',
    'graphic': 'Graphic Design',
    'creative': 'Creative',
    'writing': 'Writing',
    'editing': 'Editing',
    'translation': 'Translation'
}

def get_expertise_display_name(tag):
    """Get the display name for an expertise tag"""
    return EXPERTISE_MAPPING.get(tag, tag.title())

@app.route('/api/check-username', methods=['POST'])
def check_username():
    """Check if username is available"""
    data = request.get_json()
    username = data.get('username', '').strip().lower()
    
    if not username:
        return jsonify({'available': False, 'message': 'Username is required'})
    
    # Check if username exists
    existing_user = User.query.filter_by(username=username).first()
    
    if existing_user:
        return jsonify({'available': False, 'message': 'Username is already taken'})
    else:
        return jsonify({'available': True, 'message': 'Username is available'})

@app.route('/api/profile/test', methods=['GET', 'POST'])
@login_required
def api_profile_test():
    """Test endpoint to check authentication"""
    return jsonify({
        'success': True,
        'message': 'Authentication working',
        'user_id': current_user.id,
        'username': current_user.username
    })

@app.route('/api/profile/update', methods=['POST'])
@login_required
def api_profile_update():
    """Update user profile via API"""
    try:
        
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        # Update basic profile fields
        if 'username' in data:
            new_username = data['username'].strip()
            if new_username != current_user.username:
                # Check if username is already taken
                existing_user = User.query.filter_by(username=new_username).first()
                if existing_user:
                    return jsonify({
                        'success': False,
                        'message': 'Username is already taken'
                    }), 400
                current_user.username = new_username
        
        if 'bio' in data:
            current_user.bio = data['bio']
            
        # Update full name (handle multiple field names)
        if 'full_name' in data:
            current_user.full_name = data['full_name']
        elif 'name' in data:
            current_user.full_name = data['name']
            
        # Update profession/title
        if 'profession' in data:
            current_user.profession = data['profession']
        elif 'title' in data:
            current_user.profession = data['title']
            
        # Update industry/category
        if 'industry' in data:
            current_user.industry = data['industry']
        elif 'category' in data:
            current_user.industry = data['category']
            
        # Update hourly rate
        if 'hourly_rate' in data:
            current_user.hourly_rate = float(data['hourly_rate']) if data['hourly_rate'] else 0
        elif 'rate' in data:
            current_user.hourly_rate = float(data['rate']) if data['rate'] else 0
            
        # Update location
        if 'location' in data:
            current_user.location = data['location']
            
        # Update phone
        if 'phone' in data:
            current_user.phone = data['phone']
            
        # Update preference fields (for settings page auto-save)
        if 'language' in data:
            current_user.language = data['language']
        if 'timezone' in data:
            current_user.timezone = data['timezone']
        if 'email_notifications' in data:
            current_user.email_notifications = data['email_notifications']
            
        # Update social media URLs
        if 'linkedin' in data:
            current_user.linkedin_url = data['linkedin']
        if 'twitter' in data:
            current_user.twitter_url = data['twitter']
        if 'github' in data:
            current_user.github_url = data['github']
        if 'instagram' in data:
            current_user.instagram_url = data['instagram']
        if 'facebook' in data:
            current_user.facebook_url = data['facebook']
        if 'youtube' in data:
            current_user.youtube_url = data['youtube']
        if 'snapchat' in data:
            current_user.snapchat_url = data['snapchat']
        if 'website' in data:
            current_user.website_url = data['website']
            
        # Update availability
        if 'is_available' in data:
            current_user.is_available = data['is_available']
        
        db.session.commit()
        
        # Handle different response types
        if request.is_json:
            return jsonify({'success': True})
        else:
            # For form submissions, redirect back to account page with success message
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('account'))
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        else:
            flash('Failed to update profile: ' + str(e), 'error')
            return redirect(url_for('account'))

@app.route('/api/profile/specialties', methods=['POST'])
@login_required
def api_profile_specialties():
    """Update user specialties via API"""
    try:
        data = request.get_json()
        specialties = data.get('specialties', [])
        current_user.specialty_tags = json.dumps(specialties)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/profile/upload-picture', methods=['POST'])
@login_required
def upload_profile_picture():
    """Upload and update user profile picture"""
    try:
        print(f"Upload request from user {current_user.id} ({current_user.username})")
        print(f"Files in request: {list(request.files.keys())}")
        
        if 'profile_picture' not in request.files:
            print("No profile_picture in request files")
            return jsonify({
                'success': False,
                'message': 'No file provided'
            }), 400
        
        file = request.files['profile_picture']
        print(f"File received: {file.filename}, Content type: {file.content_type}, Size: {file.content_length}")
        
        if file.filename == '':
            print("Empty filename")
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            print(f"Invalid file type: {file.content_type}")
            return jsonify({
                'success': False,
                'message': 'File must be an image'
            }), 400
        
        # Generate unique filename
        import os
        import uuid
        from werkzeug.utils import secure_filename
        
        # Get file extension
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1]
        
        # Generate unique filename
        unique_filename = f"profile_{current_user.id}_{uuid.uuid4().hex}{file_ext}"
        print(f"Generated filename: {unique_filename}")
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(app.root_path, 'static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        print(f"Upload directory: {upload_dir}")
        
        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        print(f"File saved to: {file_path}")
        
        # Update user profile picture
        profile_picture_url = f"/static/uploads/{unique_filename}"
        current_user.profile_picture = profile_picture_url
        db.session.commit()
        print(f"Updated user profile picture to: {profile_picture_url}")
        
        return jsonify({
            'success': True,
            'message': 'Profile picture updated successfully',
            'profile_picture_url': current_user.profile_picture
        })
        
    except Exception as e:
        print(f"Error in upload_profile_picture: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error uploading profile picture: {str(e)}'
        }), 500

@app.route('/api/username/check', methods=['POST'])
@login_required
def check_username_availability():
    """Check if a username is available"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({
                'available': False,
                'message': 'Username is required'
            }), 400
        
        # Validate username format
        import re
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
            return jsonify({
                'available': False,
                'message': 'Username must be 3-20 characters, letters, numbers, and underscores only'
            }), 400
        
        # Check if username is already taken (excluding current user)
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != current_user.id:
            return jsonify({
                'available': False,
                'message': 'Username is already taken'
            })
        
        return jsonify({
            'available': True,
            'message': 'Username is available'
        })
        
    except Exception as e:
        return jsonify({
            'available': False,
            'message': f'Error checking username: {str(e)}'
        }), 500

@app.route('/api/profile/picture', methods=['POST', 'DELETE'])
@login_required
def api_profile_picture():
    """Upload or delete profile picture via API"""
    if request.method == 'POST':
        try:
            if 'profile_picture' not in request.files:
                return jsonify({'success': False, 'error': 'No file provided'})
            file = request.files['profile_picture']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No file selected'})
            # Save file
            ext = file.filename.rsplit('.', 1)[-1].lower()
            filename = f"profile_{current_user.id}_{int(time.time())}.{ext}"
            path = os.path.join('static', 'uploads', filename)
            file.save(path)
            # Remove old file if exists
            if current_user.profile_picture and os.path.exists(current_user.profile_picture[1:]):
                try:
                    os.remove(current_user.profile_picture[1:])
                except Exception:
                    pass
            current_user.profile_picture = f"/{path}"
            db.session.commit()
            return jsonify({'success': True, 'url': current_user.profile_picture})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    elif request.method == 'DELETE':
        try:
            # Remove file if exists
            if current_user.profile_picture and os.path.exists(current_user.profile_picture[1:]):
                try:
                    os.remove(current_user.profile_picture[1:])
                except Exception:
                    pass
            current_user.profile_picture = None
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

@app.route('/api/favorites/toggle', methods=['POST'])
@login_required
def api_favorites_toggle():
    """Toggle favorite status for an expert"""
    try:
        data = request.get_json()
        expert_id = data.get('expert_id')
        expert_username = data.get('expert_username')
        
        if not expert_id or not expert_username:
            return jsonify({'success': False, 'error': 'Missing expert information'})
        
        # Verify the expert exists
        expert = User.query.filter_by(id=expert_id, username=expert_username, is_available=True).first()
        if not expert:
            return jsonify({'success': False, 'error': 'Expert not found'})
        
        # Check if already favorited
        from models import Favorite
        existing_favorite = Favorite.query.filter_by(
            user_id=current_user.id, 
            expert_id=expert_id
        ).first()
        
        if existing_favorite:
            # Remove from favorites
            db.session.delete(existing_favorite)
            db.session.commit()
            return jsonify({'success': True, 'action': 'removed'})
        else:
            # Add to favorites
            new_favorite = Favorite(user_id=current_user.id, expert_id=expert_id)
            db.session.add(new_favorite)
            db.session.commit()
            return jsonify({'success': True, 'action': 'added'})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/profile/background', methods=['POST'])
@login_required
def api_profile_background():
    """Save background color preference via API"""
    try:
        data = request.get_json()
        background_color = data.get('background_color', '#f7faff')
        current_user.background_color = background_color
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/availability/rules', methods=['GET', 'POST'])
@login_required
def api_availability_rules():
    if request.method == 'GET':
        username = request.args.get('username')
        if username:
            user = User.query.filter_by(username=username).first()
            if not user:
                return jsonify([])
            user_id = user.id
        else:
            user_id = current_user.id
        
        print(f"Loading availability rules for user_id: {user_id}")
        rules = AvailabilityRule.query.filter_by(user_id=user_id).all()
        print(f"Found {len(rules)} availability rules")
        
        result = [
            {
                'id': r.id,
                'weekday': r.weekday,
                'start': r.start.strftime('%H:%M'),
                'end': r.end.strftime('%H:%M'),
                'is_active': r.is_active
            } for r in rules
        ]
        print(f"Returning availability rules: {result}")
        return jsonify(result)
    else:
        data = request.get_json()
        rules = data.get('rules', [])
        print(f"Saving availability rules for user {current_user.id}: {rules}")
        
        # Delete existing rules
        deleted_count = AvailabilityRule.query.filter_by(user_id=current_user.id).delete()
        print(f"Deleted {deleted_count} existing rules")
        
        # Add new rules
        for r in rules:
            if r.get('enabled'):
                new_rule = AvailabilityRule(
                    user_id=current_user.id,
                    weekday=r['weekday'],
                    start=datetime.strptime(r['start'], '%H:%M').time(),
                    end=datetime.strptime(r['end'], '%H:%M').time(),
                    is_active=True
                )
                db.session.add(new_rule)
                print(f"Added rule: weekday={r['weekday']}, start={r['start']}, end={r['end']}")
        
        db.session.commit()
        print(f"Successfully saved {len([r for r in rules if r.get('enabled')])} rules")
        return jsonify({'success': True})

@app.route('/api/availability/exceptions', methods=['GET', 'POST'])
@login_required
def api_availability_exceptions():
    if request.method == 'GET':
        username = request.args.get('username')
        if username:
            user = User.query.filter_by(username=username).first()
            if not user:
                return jsonify([])
            user_id = user.id
        else:
            user_id = current_user.id
        exceptions = AvailabilityException.query.filter_by(user_id=user_id).all()
        return jsonify([
            {
                'id': e.id,
                'start': e.start.isoformat(),
                'end': e.end.isoformat(),
                'reason': e.reason
            } for e in exceptions
        ])
    else:
        data = request.get_json()
        ex = AvailabilityException(
            user_id=current_user.id,
            start=datetime.fromisoformat(data['start']),
            end=datetime.fromisoformat(data['end']),
            reason=data.get('reason', '')
        )
        db.session.add(ex)
        db.session.commit()
        return jsonify({'success': True})

@app.route('/api/availability/exceptions/<int:exception_id>', methods=['DELETE'])
@login_required
def api_availability_exception_delete(exception_id):
    ex = AvailabilityException.query.filter_by(id=exception_id, user_id=current_user.id).first()
    if ex:
        db.session.delete(ex)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Not found'}), 404

@app.route('/api/availability/sync-calendar', methods=['POST'])
@login_required
def api_sync_google_calendar():
    """Sync Google Calendar events to create availability exceptions"""
    if not current_user.google_calendar_connected:
        return jsonify({'success': False, 'error': 'Google Calendar not connected'}), 400
    
    try:
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        from datetime import datetime, timedelta
        
        # Create credentials object
        credentials = Credentials(
            token=current_user.google_calendar_token,
            refresh_token=current_user.google_calendar_refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=app.config['GOOGLE_CLIENT_ID'],
            client_secret=app.config['GOOGLE_CLIENT_SECRET']
        )
        
        # Build calendar service
        service = build('calendar', 'v3', credentials=credentials)
        
        # Get events for the next 30 days
        now = datetime.now()
        time_min = now.isoformat() + 'Z'
        time_max = (now + timedelta(days=30)).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId=current_user.google_calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Clear existing calendar-based exceptions
        AvailabilityException.query.filter_by(
            user_id=current_user.id,
            reason='Google Calendar Event'
        ).delete()
        
        # Create new exceptions for calendar events
        synced_count = 0
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            if start and end:
                # Parse datetime
                if 'T' in start:  # datetime
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                else:  # date only
                    start_dt = datetime.fromisoformat(start + 'T00:00:00+00:00')
                    end_dt = datetime.fromisoformat(end + 'T23:59:59+00:00')
                
                # Create availability exception
                exception = AvailabilityException(
                    user_id=current_user.id,
                    start=start_dt,
                    end=end_dt,
                    reason='Google Calendar Event',
                    is_blocked=True
                )
                db.session.add(exception)
                synced_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'synced_events': synced_count,
            'message': f'Synced {synced_count} calendar events'
        })
        
    except Exception as e:
        print(f"Error syncing Google Calendar: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/availability/calendar-status', methods=['GET'])
@login_required
def api_calendar_status():
    """Get Google Calendar connection status"""
    print(f"DEBUG: Calendar status check for user {current_user.id}: connected={current_user.google_calendar_connected}")
    
    # Check if user has Google tokens but calendar is not connected
    # This happens when users logged in before calendar scope was added
    needs_reauth = False
    if current_user.google_calendar_token and not current_user.google_calendar_connected:
        needs_reauth = True
    
    return jsonify({
        'connected': current_user.google_calendar_connected,
        'calendar_id': current_user.google_calendar_id,
        'needs_reauth': needs_reauth
    })

@app.route('/api/user/timezone', methods=['GET'])
@login_required
def api_user_timezone():
    """Get user's timezone preference"""
    return jsonify({
        'timezone': current_user.timezone or 'America/New_York'
    })

@app.route('/api/availability/monthly-data', methods=['GET'])
@login_required
def api_monthly_availability_data():
    """Get monthly availability data for calendar display"""
    try:
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        
        if not year or not month:
            return jsonify({'success': False, 'error': 'Year and month required'}), 400
        
        # Get availability rules
        rules = AvailabilityRule.query.filter_by(user_id=current_user.id).all()
        availability_rules = {}
        for rule in rules:
            availability_rules[rule.weekday] = {
                'start': rule.start.strftime('%H:%M'),
                'end': rule.end.strftime('%H:%M'),
                'enabled': rule.is_active
            }
        
        # Get availability exceptions for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        exceptions = AvailabilityException.query.filter(
            AvailabilityException.user_id == current_user.id,
            AvailabilityException.start >= start_date,
            AvailabilityException.start < end_date
        ).all()
        
        exceptions_data = []
        for ex in exceptions:
            exceptions_data.append({
                'date': ex.start.strftime('%Y-%m-%d'),
                'start': ex.start.strftime('%H:%M'),
                'end': ex.end.strftime('%H:%M'),
                'is_blocked': ex.is_blocked,
                'reason': ex.reason
            })
        
        return jsonify({
            'success': True,
            'availability_rules': availability_rules,
            'exceptions': exceptions_data
        })
        
    except Exception as e:
        print(f"Error getting monthly availability data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/availability/time-slots', methods=['GET'])
@login_required
def api_availability_time_slots():
    """Get available time slots for a specific date"""
    try:
        date_str = request.args.get('date')
        if not date_str:
            return jsonify({'success': False, 'error': 'Date required'}), 400
        
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        weekday = target_date.weekday()
        
        # Get availability rule for this weekday
        rule = AvailabilityRule.query.filter_by(
            user_id=current_user.id, 
            weekday=weekday
        ).first()
        
        if not rule or not rule.is_active:
            return jsonify({
                'success': True,
                'time_slots': [],
                'message': 'No availability set for this day'
            })
        
        # Generate time slots
        time_slots = []
        start_time = rule.start
        end_time = rule.end
        duration_minutes = 60  # Default 1 hour sessions
        
        current_time = datetime.combine(target_date, start_time)
        end_datetime = datetime.combine(target_date, end_time)
        
        while current_time < end_datetime:
            slot_end = current_time + timedelta(minutes=duration_minutes)
            if slot_end <= end_datetime:
                time_slots.append({
                    'start': current_time.strftime('%H:%M'),
                    'end': slot_end.strftime('%H:%M'),
                    'start_datetime': current_time.isoformat(),
                    'end_datetime': slot_end.isoformat(),
                    'available': True
                })
            current_time += timedelta(minutes=duration_minutes)
        
        # Check for exceptions (blocked times)
        exceptions = AvailabilityException.query.filter(
            AvailabilityException.user_id == current_user.id,
            AvailabilityException.start >= datetime.combine(target_date, time(0, 0)),
            AvailabilityException.start < datetime.combine(target_date, time(23, 59))
        ).all()
        
        # Mark slots as unavailable if they conflict with exceptions
        for exception in exceptions:
            for slot in time_slots:
                slot_start = datetime.fromisoformat(slot['start_datetime'])
                slot_end = datetime.fromisoformat(slot['end_datetime'])
                
                if (slot_start < exception.end and slot_end > exception.start):
                    slot['available'] = False
                    slot['blocked_reason'] = exception.reason
        
        return jsonify({
            'success': True,
            'time_slots': time_slots,
            'date': date_str,
            'weekday': weekday
        })
        
    except Exception as e:
        print(f"Error getting time slots: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/availability/calendar-events', methods=['GET'])
@login_required
def api_calendar_events():
    """Get Google Calendar events for a date range"""
    if not current_user.google_calendar_connected:
        return jsonify({'success': False, 'error': 'Google Calendar not connected'}), 400
    
    try:
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        from datetime import datetime
        
        # Get date range from query parameters
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        
        if not start_date or not end_date:
            return jsonify({'success': False, 'error': 'Start and end dates required'}), 400
        
        # Create credentials object
        credentials = Credentials(
            token=current_user.google_calendar_token,
            refresh_token=current_user.google_calendar_refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=app.config['GOOGLE_CLIENT_ID'],
            client_secret=app.config['GOOGLE_CLIENT_SECRET']
        )
        
        # Build calendar service
        service = build('calendar', 'v3', credentials=credentials)
        
        # Get events for the date range
        events_result = service.events().list(
            calendarId=current_user.google_calendar_id,
            timeMin=start_date,
            timeMax=end_date,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Format events for frontend
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            formatted_events.append({
                'id': event['id'],
                'title': event.get('summary', 'No Title'),
                'start': start,
                'end': end,
                'description': event.get('description', ''),
                'location': event.get('location', '')
            })
        
        return jsonify({
            'success': True,
            'events': formatted_events
        })
        
    except Exception as e:
        print(f"ERROR: Failed to fetch calendar events: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/booking/confirm', methods=['GET', 'POST'])
@login_required
def booking_confirmation():
    print(f"DEBUG: booking_confirmation called - Method: {request.method}")
    print(f"DEBUG: booking_confirmation - Args: {dict(request.args)}")
    print(f"DEBUG: booking_confirmation - Form: {dict(request.form)}")
    print(f"DEBUG: Stripe API key configured: {bool(stripe.api_key)}")
    print(f"DEBUG: YOUR_DOMAIN: {YOUR_DOMAIN}")
    """Booking confirmation page with payment"""
    print(f"DEBUG: Current user: {current_user.is_authenticated if current_user else 'No user'}")
    print(f"DEBUG: Request URL: {request.url}")
    print(f"DEBUG: Request method: {request.method}")
    print(f"DEBUG: Request args: {dict(request.args)}")
    if request.method == 'GET':
        # Get booking details from query parameters
        expert_username = request.args.get('expert')
        datetime_str = request.args.get('datetime')
        duration = request.args.get('duration', 30)
        
        if not expert_username or not datetime_str:
            flash('Missing booking information', 'error')
            return redirect(url_for('homepage'))
        
        # Get expert details
        expert = User.query.filter_by(username=expert_username).first()
        if not expert:
            flash('Expert not found', 'error')
            return redirect(url_for('homepage'))
        
        # Parse datetime
        try:
            booking_datetime = datetime.fromisoformat(datetime_str)
        except ValueError:
            flash('Invalid date/time format', 'error')
            return redirect(url_for('homepage'))
        
        # Calculate pricing
        duration = int(duration)
        session_price = expert.hourly_rate or 0  # This field now stores session price directly
        # All sessions are 30 minutes, so session fee equals the session price
        session_fee = session_price
        platform_fee = max(5.0, session_fee * 0.10)  # 10% platform fee, minimum $5
        total_amount = session_fee + platform_fee
        
        return render_template('booking_confirmation.html',
                             expert=expert,
                             booking_date=booking_datetime.strftime('%B %d, %Y'),
                             booking_time=booking_datetime.strftime('%I:%M %p'),
                             duration=duration,
                             session_fee=f"{session_fee:.2f}",
                             platform_fee=f"{platform_fee:.2f}",
                             total_amount=f"{total_amount:.2f}")
    
    else:
        # Handle POST request - create booking and redirect to Stripe
        try:
            print("DEBUG: Starting booking confirmation POST handling")
            
            expert_username = request.args.get('expert')
            datetime_str = request.args.get('datetime')
            duration = int(request.args.get('duration', 30))
            
            # Debug logging
            print(f"DEBUG: Booking confirmation POST - Expert: {expert_username}")
            print(f"DEBUG: Booking confirmation POST - Datetime: {datetime_str}")
            print(f"DEBUG: Booking confirmation POST - Duration: {duration}")
            
            if not expert_username or not datetime_str:
                print("DEBUG: Missing booking information")
                flash('Missing booking information', 'error')
                return redirect(url_for('homepage'))
            
            expert = User.query.filter_by(username=expert_username).first()
            if not expert:
                print("DEBUG: Expert not found")
                flash('Expert not found', 'error')
                return redirect(url_for('homepage'))
            
            print(f"DEBUG: Expert found: {expert.username}")
            
            start_time = datetime.fromisoformat(datetime_str)
            end_time = start_time + timedelta(minutes=duration)
            
            print(f"DEBUG: Booking confirmation POST - Start time: {start_time}")
            print(f"DEBUG: Booking confirmation POST - End time: {end_time}")
            
        except Exception as e:
            print(f"DEBUG: Exception in booking confirmation POST: {e}")
            flash(f'Error processing booking: {str(e)}', 'error')
            return redirect(url_for('homepage'))
        
        # Prevent double booking: check for any overlapping bookings
        print("DEBUG: Checking for booking conflicts")
        conflict = Booking.query.filter(
            (Booking.expert_id == expert.id) &
            (Booking.status == 'confirmed') &
            (
                ((start_time >= Booking.start_time) & (start_time < Booking.end_time)) |
                ((end_time > Booking.start_time) & (end_time <= Booking.end_time)) |
                ((start_time <= Booking.start_time) & (end_time >= Booking.end_time))
            )
        ).first()
        
        if conflict:
            print("DEBUG: Booking conflict found")
            flash('This time slot has already been booked. Please choose another time.', 'error')
            return redirect(url_for('bookings'))
        
        print("DEBUG: No booking conflicts found")
        
        # Calculate pricing
        print("DEBUG: Calculating pricing")
        session_price = expert.hourly_rate or 0  # This field now stores session price directly
        # All sessions are 30 minutes, so session fee equals the session price
        session_fee = session_price
        platform_fee = max(5.0, session_fee * 0.10)
        total_amount = session_fee + platform_fee
        
        print(f"DEBUG: Pricing calculated - Session fee: {session_fee}, Platform fee: {platform_fee}, Total: {total_amount}")
        
        # Create booking with pending payment status
        print("DEBUG: Creating booking")
        booking = Booking(
            user_id=current_user.id,
            expert_id=expert.id,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            status='pending',
            payment_status='pending',
            payment_amount=total_amount
        )
        
        db.session.add(booking)
        db.session.commit()
        
        print(f"DEBUG: Booking created with ID: {booking.id}")
        
        # Redirect to Stripe checkout with error handling
        print(f"DEBUG: Redirecting to Stripe checkout for booking ID: {booking.id}")
        try:
            checkout_url = url_for('create_checkout_session', booking_id=booking.id)
            print(f"DEBUG: Redirect URL: {checkout_url}")
            return redirect(checkout_url)
        except Exception as e:
            print(f"DEBUG: Error creating checkout URL: {e}")
            # Fallback: redirect to booking success page with a message
            flash('Booking created successfully. Payment processing is temporarily unavailable. Please contact support.', 'warning')
            return redirect(url_for('booking_success', booking_id=booking.id))

@app.route('/debug/calendar/<username>')
@login_required
def debug_calendar(username):
    """Debug calendar booking issues for a specific user"""
    try:
        user = User.query.filter_by(username=username).first_or_404()
        
        # Check basic user info
        user_info = {
            'username': user.username,
            'full_name': user.full_name,
            'is_available': user.is_available,
            'timezone': user.timezone,
            'has_availability_rules': False,
            'availability_rules': [],
            'available_times_count': 0,
            'sample_available_times': []
        }
        
        # Check availability rules
        availability_rules = AvailabilityRule.query.filter_by(user_id=user.id).all()
        user_info['has_availability_rules'] = len(availability_rules) > 0
        user_info['availability_rules'] = [
            {
                'weekday': rule.weekday,
                'start': rule.start.strftime('%H:%M'),
                'end': rule.end.strftime('%H:%M'),
                'is_active': rule.is_active
            } for rule in availability_rules
        ]
        
        # Test slot generation for today and tomorrow
        from datetime import datetime, timedelta
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        # Get current user's timezone
        current_user_timezone = current_user.timezone or 'America/New_York'
        
        # Test slot generation
        test_dates = [today, tomorrow]
        all_available_times = []
        
        for test_date in test_dates:
            try:
                slots = generate_available_slots_for_date(test_date, user, current_user_timezone)
                for slot in slots:
                    if slot['start_time'].replace(tzinfo=None) > datetime.now():
                        all_available_times.append({
                            'date': test_date.strftime('%Y-%m-%d'),
                            'datetime': slot['start_time'].replace(tzinfo=None),
                            'formatted_time': slot['formatted_time'],
                            'iso_datetime': slot['start_time'].replace(tzinfo=None).isoformat()
                        })
            except Exception as e:
                print(f"Error generating slots for {test_date}: {e}")
        
        user_info['available_times_count'] = len(all_available_times)
        user_info['sample_available_times'] = all_available_times[:10]  # First 10 times
        
        return jsonify(user_info)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/availability/times', methods=['GET'])
def api_availability_times():
    """Get available times for a user, with default 9-5 availability if no rules set"""
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Username required'}), 400
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if user is available for bookings
    if not user.is_available:
        return jsonify({'available': False, 'message': 'User is currently unavailable'})
    
    # Get existing bookings for this user (as expert) to exclude booked times
    now = datetime.now()
    existing_bookings = Booking.query.filter(
        (Booking.expert_id == user.id) &
        (Booking.start_time >= now) &
        (Booking.status == 'confirmed')
    ).all()
    
    # Create a set of booked time slots for quick lookup
    booked_slots = set()
    for booking in existing_bookings:
        start_time = booking.start_time
        end_time = booking.end_time
        current = start_time
        while current < end_time:
            booked_slots.add(current.replace(second=0, microsecond=0))
            current += timedelta(minutes=30)
    
    # Get explicit availability rules
    rules = AvailabilityRule.query.filter_by(user_id=user.id).all()
    
    # If no explicit rules, provide default 9-5 availability for all weekdays
    if not rules:
        default_times = []
        for day_offset in range(7):
            date = now + timedelta(days=day_offset)
            if date.weekday() < 5:  # Monday to Friday
                for hour in range(9, 17):  # 9 AM to 5 PM
                    for minute in [0, 30]:
                        time_slot = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                        if time_slot > now and time_slot not in booked_slots:
                            default_times.append({
                                'date': time_slot.strftime('%Y-%m-%d'),
                                'time': time_slot.strftime('%H:%M'),
                                'datetime': time_slot.isoformat(),
                                'day_name': time_slot.strftime('%A'),
                                'formatted': time_slot.strftime('%I:%M %p'),
                                'duration': 30
                            })
        return jsonify({
            'available': True,
            'has_rules': False,
            'times': default_times[:20]
        })
    else:
        available_times = []
        for rule in rules:
            for day_offset in range(7):
                date = now + timedelta(days=day_offset)
                if date.weekday() == rule.weekday:
                    current_time = datetime.combine(date.date(), rule.start)
                    end_time = datetime.combine(date.date(), rule.end)
                    while current_time < end_time:
                        if current_time > now and current_time not in booked_slots:
                            available_times.append({
                                'date': current_time.strftime('%Y-%m-%d'),
                                'time': current_time.strftime('%H:%M'),
                                'datetime': current_time.isoformat(),
                                'day_name': current_time.strftime('%A'),
                                'formatted': current_time.strftime('%I:%M %p'),
                                'duration': 30
                            })
                        current_time += timedelta(minutes=30)
        return jsonify({
            'available': True,
            'has_rules': True,
            'times': available_times[:20]
        })

# ============================================================================
# STRIPE CONNECT ROUTES FOR EXPERT PAYOUTS
# ============================================================================

@app.route('/expert/onboard-stripe', methods=['GET', 'POST'])
@login_required
def expert_stripe_onboarding():
    """Onboard expert to Stripe Connect for payouts"""
    # Production safeguard
    if is_production_environment() and stripe.api_key.startswith('sk_test_'):
        flash('Payout setup temporarily unavailable. Please try again later.', 'error')
        return redirect(url_for('expert_dashboard'))
    
    # If user already has a Stripe account, redirect to Stripe dashboard
    if current_user.stripe_account_id:
        try:
            account = stripe.Account.retrieve(current_user.stripe_account_id)
            
            # Update account status
            if account.charges_enabled and account.payouts_enabled:
                current_user.stripe_account_status = 'active'
            elif account.details_submitted and not account.charges_enabled:
                current_user.stripe_account_status = 'pending_verification'
            elif account.details_submitted:
                current_user.stripe_account_status = 'pending'
            else:
                current_user.stripe_account_status = 'incomplete'
            
            db.session.commit()
            
            # Create login link for existing account
            login_link = stripe.Account.create_login_link(
                current_user.stripe_account_id,
                redirect_url=f'{YOUR_DOMAIN}/expert/dashboard'
            )
            return redirect(login_link.url)
            
        except stripe.StripeError as e:
            flash(f'Error accessing Stripe account: {str(e)}', 'error')
            return redirect(url_for('expert_dashboard'))
    
    if request.method == 'GET':
        return render_template('expert_stripe_onboarding.html')
    
    try:
        # Debug: Print the URL being constructed
        profile_url = f'{YOUR_DOMAIN}/profile/{current_user.username}'
        print(f"DEBUG: Constructing profile URL: {profile_url}")
        print(f"DEBUG: YOUR_DOMAIN = {YOUR_DOMAIN}")
        print(f"DEBUG: username = {current_user.username}")
        
        # Create Stripe Connect Express account
        account = stripe.Account.create(
            type='express',
            country='US',  # You can make this dynamic based on user location
            email=current_user.email,
            capabilities={
                'card_payments': {'requested': True},
                'transfers': {'requested': True},
            },
            business_type='individual',
            # Temporarily remove business_profile to avoid URL validation issues
            # business_profile={
            #     'url': profile_url,
            #     'mcc': '7399',  # Business Services - Not Elsewhere Classified
            # },
        )
        
        # Update user with Stripe account info
        current_user.stripe_account_id = account.id
        current_user.stripe_account_status = account.charges_enabled and 'active' or 'pending'
        db.session.commit()
        
        # Create account link for onboarding
        account_link = stripe.AccountLink.create(
            account=account.id,
            refresh_url=f'{YOUR_DOMAIN}/expert/onboard-stripe',
            return_url=f'{YOUR_DOMAIN}/expert/dashboard',
            type='account_onboarding',
        )
        
        return redirect(account_link.url)
        
    except Exception as e:
        flash(f'Error creating Stripe account: {str(e)}', 'error')
        return redirect(url_for('expert_stripe_onboarding'))

@app.route('/expert/dashboard')
@login_required
def expert_dashboard():
    """Expert dashboard with earnings and payout info"""
    if current_user.stripe_account_id:
        try:
            account = stripe.Account.retrieve(current_user.stripe_account_id)
            
            # More comprehensive status checking
            if account.charges_enabled and account.payouts_enabled:
                current_user.stripe_account_status = 'active'
            elif account.details_submitted and not account.charges_enabled:
                current_user.stripe_account_status = 'pending_verification'
            elif account.details_submitted:
                current_user.stripe_account_status = 'pending'
            else:
                current_user.stripe_account_status = 'incomplete'
            
            current_user.payout_enabled = account.payouts_enabled
            
            # Debug logging
            print(f"DEBUG: Stripe account status - charges_enabled: {account.charges_enabled}, payouts_enabled: {account.payouts_enabled}, details_submitted: {account.details_submitted}")
            print(f"DEBUG: Account status set to: {current_user.stripe_account_status}")

            # Total earnings: all completed and paid bookings (historical)
            completed_bookings = Booking.query.filter(
                (Booking.expert_id == current_user.id) &
                (Booking.status == 'completed') &
                (Booking.payment_status == 'paid')
            ).all()
            total_earnings = sum(booking.payment_amount for booking in completed_bookings)
            current_user.total_earnings = total_earnings

            # Pending balance: all confirmed or completed and paid bookings, not yet paid out
            pending_bookings = Booking.query.filter(
                (Booking.expert_id == current_user.id) &
                (Booking.status.in_(['confirmed', 'completed'])) &
                (Booking.payment_status == 'paid')
            ).all()
            pending_gross = sum(booking.payment_amount for booking in pending_bookings)
            platform_fees = sum(booking.payment_amount * 0.10 for booking in pending_bookings)
            # Subtract payouts already made
            total_payouts = current_user.total_payouts or 0.0
            current_user.pending_balance = pending_gross - platform_fees - total_payouts

            db.session.commit()
        except Exception as e:
            flash(f'Error fetching Stripe account info: {str(e)}', 'error')

    # Calculate potential earnings: sum of all confirmed, upcoming bookings (not yet completed)
    # Industry standard: only count confirmed bookings as potential earnings
    from datetime import datetime
    now = datetime.now()
    potential_earnings_bookings = Booking.query.filter(
        (Booking.expert_id == current_user.id) &
        (Booking.status == 'confirmed') &
        (Booking.start_time > now)
    ).all()
    potential_earnings = sum(booking.payment_amount for booking in potential_earnings_bookings)

    recent_bookings = Booking.query.filter(
        (Booking.expert_id == current_user.id) &
        (Booking.status.in_(['pending', 'confirmed']))
    ).order_by(Booking.start_time.desc()).limit(5).all()
    recent_payouts = Payout.query.filter_by(expert_id=current_user.id).order_by(Payout.created_at.desc()).limit(5).all()
    return render_template('expert_dashboard.html', 
                         recent_bookings=recent_bookings,
                         recent_payouts=recent_payouts,
                         potential_earnings=potential_earnings)

@app.route('/expert/request-payout', methods=['POST'])
@login_required
def request_payout():
    """Request a payout to expert's bank account"""
    # Production safeguard
    if is_production_environment() and stripe.api_key.startswith('sk_test_'):
        flash('Payout system temporarily unavailable. Please try again later.', 'error')
        return redirect(url_for('expert_dashboard'))
    
    if not current_user.stripe_account_id:
        flash('You need to complete Stripe onboarding first', 'error')
        return redirect(url_for('expert_dashboard'))
    
    if not current_user.payout_enabled:
        flash('Payouts are not enabled for your account', 'error')
        return redirect(url_for('expert_dashboard'))
    
    if current_user.pending_balance <= 0:
        flash('No pending balance to payout', 'error')
        return redirect(url_for('expert_dashboard'))
    
    try:
        # Create payout in Stripe
        payout = stripe.Payout.create(
            amount=int(current_user.pending_balance * 100),  # Convert to cents
            currency='usd',
            stripe_account=current_user.stripe_account_id,
        )
        
        # Create payout record in database
        payout_record = Payout(
            expert_id=current_user.id,
            amount=current_user.pending_balance * 100,  # Store in cents
            stripe_payout_id=payout.id,
            status='pending'
        )
        db.session.add(payout_record)
        
        # Update user's payout totals
        current_user.total_payouts += current_user.pending_balance
        current_user.pending_balance = 0.0
        
        db.session.commit()
        
        flash(f'Payout of ${current_user.total_payouts:.2f} requested successfully!', 'success')
        
    except Exception as e:
        flash(f'Error requesting payout: {str(e)}', 'error')
    
    return redirect(url_for('expert_dashboard'))

@app.route('/expert/complete-verification')
@login_required
def complete_verification():
    """Redirect to Stripe dashboard for the expert's account"""
    if not current_user.stripe_account_id:
        flash('No Stripe account found. Please complete payout setup first.', 'error')
        return redirect(url_for('expert_dashboard'))
    
    try:
        # Get the account to check its status
        account = stripe.Account.retrieve(current_user.stripe_account_id)
        
        # Create a login link for the account (works for both test and live)
        try:
            login_link = stripe.Account.create_login_link(
                current_user.stripe_account_id,
                redirect_url=f"{YOUR_DOMAIN}/expert/dashboard"
            )
            return redirect(login_link.url)
        except stripe.StripeError as e:
            # Fallback to direct URL if login link fails
            dashboard_url = f"https://connect.stripe.com/express/{current_user.stripe_account_id}/settings"
            return redirect(dashboard_url)
            
    except stripe.StripeError as e:
        flash(f'Error accessing Stripe account: {str(e)}', 'error')
    return redirect(url_for('expert_dashboard'))

@app.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks for payment confirmations and payouts"""
    # Production safeguard
    if is_production_environment() and stripe.api_key.startswith('sk_test_'):
        return 'Production environment detected with test keys', 500
    
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
        if not webhook_secret:
            return 'Webhook secret not configured', 500
            
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        return 'Invalid signature', 400
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        booking_id = session.get('metadata', {}).get('booking_id')
        
        if booking_id:
            booking = Booking.query.get(booking_id)
            if booking:
                booking.payment_status = 'paid'
                db.session.commit()
                
                # Update expert's earnings
                expert = User.query.get(booking.expert_id)
                if expert:
                    expert.total_earnings += booking.payment_amount
                    expert.pending_balance += booking.payment_amount * 0.90  # After platform fee
                    db.session.commit()
    
    elif event['type'] == 'payout.paid':
        payout = event['data']['object']
        payout_record = Payout.query.filter_by(stripe_payout_id=payout.id).first()
        
        if payout_record:
            payout_record.status = 'paid'
            payout_record.paid_at = datetime.now(EASTERN_TIMEZONE)
            db.session.commit()
    
    elif event['type'] == 'payout.failed':
        payout = event['data']['object']
        payout_record = Payout.query.filter_by(stripe_payout_id=payout.id).first()
        
        if payout_record:
            payout_record.status = 'failed'
            db.session.commit()
    
    elif event['type'] == 'charge.refunded':
        refund = event['data']['object']
        booking_id = refund.metadata.get('booking_id')
        
        if booking_id:
            booking = Booking.query.get(booking_id)
            if booking:
                booking.payment_status = 'refunded'
            db.session.commit()
    
    return 'OK', 200

@app.route('/earnings')
@login_required
def earnings():
    """Show expert's earnings history"""
    payouts = Payout.query.filter_by(expert_id=current_user.id).order_by(Payout.created_at.desc()).all()
    
    # Calculate totals
    total_earned = 0
    pending_total = 0
    failed_total = 0
    
    for payout in payouts:
        if payout.status == 'paid':
            total_earned += payout.amount
        elif payout.status == 'pending':
            pending_total += payout.amount
        elif payout.status == 'failed':
            failed_total += payout.amount
    
    return render_template('expert_payouts.html', 
                         payouts=payouts,
                         total_earned=total_earned,
                         pending_total=pending_total,
                         failed_total=failed_total)

@app.route('/expert/payout-details')
@login_required
def expert_payout_details():
    # On the way to your bank: payouts with status 'pending'
    pending_payouts = Payout.query.filter_by(expert_id=current_user.id, status='pending').all()
    on_the_way = sum(payout.amount for payout in pending_payouts) / 100  # convert cents to dollars
    # Upcoming payouts: (for now, same as on_the_way unless you have scheduled payouts)
    upcoming_payouts = on_the_way
    # Available in your balance: pending_balance
    available_balance = current_user.pending_balance
    # Total balance: total_earnings
    total_balance = current_user.total_earnings
    # Payout method: get from Stripe
    payout_method = None
    payout_schedule = current_user.payout_schedule
    if current_user.stripe_account_id:
        try:
            account = stripe.Account.retrieve(current_user.stripe_account_id)
            # Get external accounts (bank info)
            if account.external_accounts and account.external_accounts.data:
                ext = account.external_accounts.data[0]
                payout_method = f"{ext['bank_name']} ••••{ext['last4']}" if 'bank_name' in ext and 'last4' in ext else ext['id']
        except Exception as e:
            payout_method = None
    return jsonify({
        'on_the_way': f"${on_the_way:.2f}",
        'upcoming_payouts': f"${upcoming_payouts:.2f}",
        'available_balance': f"${available_balance:.2f}",
        'total_balance': f"${total_balance:.2f}",
        'payout_method': payout_method,
        'payout_schedule': payout_schedule
    })

@app.route('/debug/oauth')
def debug_oauth():
    """Debug endpoint to check OAuth configuration"""
    debug_info = {
        'google_client_id': app.config.get('GOOGLE_CLIENT_ID', 'NOT_SET'),
        'google_client_secret_set': app.config.get('GOOGLE_CLIENT_SECRET', 'NOT_SET') != 'YOUR_GOOGLE_CLIENT_SECRET',
        'redirect_uri': url_for('auth_google_callback', _external=True),
        'request_url': request.url,
        'request_host': request.host,
        'request_headers': dict(request.headers),
        'flask_env': os.environ.get('FLASK_ENV', 'NOT_SET'),
        'environment': os.environ.get('ENVIRONMENT', 'NOT_SET'),
    }
    return jsonify(debug_info)

@app.route('/test-deployment')
def test_deployment():
    return "Deployment test successful - code changes are active!"

@app.route('/admin/update-bookings-status')
def update_bookings_status():
    """Update all bookings whose end_time is in the past and status is 'confirmed' to 'completed'."""
    now = datetime.now(EASTERN_TIMEZONE)
    updated = 0
    bookings = Booking.query.filter(
        Booking.status == 'confirmed',
        Booking.end_time < now
    ).all()
    for booking in bookings:
        booking.status = 'completed'
        updated += 1
    db.session.commit()
    return jsonify({'updated': updated, 'message': f'{updated} bookings updated to completed.'})

@app.route('/auth/google')
def auth_google():
    # Manually construct redirect URI to ensure HTTPS for production
    if 'localhost' in request.host:
        # Local development - use HTTP
        redirect_uri = f"http://{request.host}/auth/google/callback"
    elif 'droply.live' in request.host:
        # Production - force HTTPS for droply.live
        redirect_uri = "https://droply.live/auth/google/callback"
    else:
        # Fallback - force HTTPS
        redirect_uri = f"https://{request.host}/auth/google/callback"
    
    print(f"DEBUG: Google OAuth redirect_uri = {redirect_uri}")
    return google.authorize_redirect(redirect_uri, scope='openid email profile https://www.googleapis.com/auth/calendar.readonly')

@app.route('/auth/google/callback')
def auth_google_callback():
    print(f"DEBUG: Google OAuth callback - Request URL = {request.url}")
    print(f"DEBUG: Google OAuth callback - Request args = {dict(request.args)}")
    print(f"DEBUG: Google OAuth callback - Request headers = {dict(request.headers)}")
    try:
        token = google.authorize_access_token()
        user_info = google.userinfo()
        print(f"DEBUG: Google OAuth callback - Token received successfully")
    except Exception as e:
        print(f"DEBUG: Google OAuth callback - Error: {str(e)}")
        flash(f'Google authentication failed: {str(e)}', 'error')
        return redirect(url_for('login'))
    email = user_info.get('email')
    username = user_info.get('name') or email.split('@')[0]
    if not email:
        flash('Google account did not return an email.', 'error')
        return redirect(url_for('login'))
    
    # Check if user exists
    user = User.query.filter_by(email=email).first()
    is_new_user = False
    
    if not user:
        # Register new user
        user = User(username=username, email=email, full_name=user_info.get('name'))
        db.session.add(user)
        db.session.commit()
        is_new_user = True
        print(f"New Google user registered: {user.email}")
        
        # Set up default availability (9-5 weekdays only)
        setup_default_availability(user)
    
    # Automatically connect Google Calendar if calendar scope is present
    print(f"DEBUG: Token scope: {token.get('scope', '')}")
    print(f"DEBUG: Token keys: {list(token.keys())}")
    print(f"DEBUG: Full token: {token}")
    if 'calendar' in token.get('scope', ''):
        print(f"DEBUG: Calendar integration detected. Scope: {token.get('scope', '')}")
        try:
            # Store the calendar tokens for the current user
            user.google_calendar_connected = True
            user.google_calendar_token = token.get('access_token')
            user.google_calendar_refresh_token = token.get('refresh_token')
            print(f"DEBUG: Stored calendar tokens for user {user.id}")
            print(f"DEBUG: google_calendar_connected set to: {user.google_calendar_connected}")
            
            # Get the primary calendar ID
            from googleapiclient.discovery import build
            from google.oauth2.credentials import Credentials
            
            # Create credentials object
            credentials = Credentials(
                token=token.get('access_token'),
                refresh_token=token.get('refresh_token'),
                token_uri='https://oauth2.googleapis.com/token',
                client_id=app.config['GOOGLE_CLIENT_ID'],
                client_secret=app.config['GOOGLE_CLIENT_SECRET']
            )
            
            print("DEBUG: Building calendar service...")
            service = build('calendar', 'v3', credentials=credentials)
            calendar_list = service.calendarList().list().execute()
            print(f"DEBUG: Retrieved {len(calendar_list.get('items', []))} calendars")
            
            # Find calendar that matches user's email address
            user_email_calendar = None
            user_email = user.email.lower()
            
            for calendar in calendar_list.get('items', []):
                calendar_id = calendar.get('id', '').lower()
                # Check if calendar ID matches user's email
                if user_email in calendar_id or calendar_id == user_email:
                    user_email_calendar = calendar
                    break
            
            # If no email-matching calendar found, fall back to primary calendar
            if not user_email_calendar:
                for calendar in calendar_list.get('items', []):
                    if calendar.get('primary'):
                        user_email_calendar = calendar
                        break
            
            if user_email_calendar:
                user.google_calendar_id = user_email_calendar['id']
                print(f"DEBUG: Set calendar ID: {user_email_calendar['id']} (email: {user_email_calendar.get('summary', 'Unknown')})")
            else:
                print("DEBUG: No matching calendar found, using first calendar")
                if calendar_list.get('items'):
                    user.google_calendar_id = calendar_list['items'][0]['id']
            
            db.session.commit()
            print("DEBUG: Calendar integration completed successfully")
            flash('Google Calendar connected automatically!', 'success')
            
        except Exception as e:
            print(f"ERROR: Failed to connect Google Calendar: {e}")
            import traceback
            traceback.print_exc()
            flash('Failed to connect Google Calendar automatically. You can connect it later in your availability settings.', 'warning')
    
    login_user(user)
    
    # Check if there's a redirect parameter
    redirect_to = request.args.get('redirect_to', 'dashboard')
    
    if is_new_user:
        flash('Welcome! Please complete your profile setup.', 'success')
        return redirect(url_for('onboarding'))
    else:
        # Only show generic login message if calendar wasn't connected
        if 'calendar' not in token.get('scope', ''):
            flash('Logged in with Google!', 'success')
        
        # Redirect to the specified page or dashboard
        if redirect_to == 'availability':
            return redirect(url_for('availability'))
        else:
            return redirect(url_for('dashboard'))

# Google Calendar Integration Routes
@app.route('/auth/google-calendar')
@login_required
def auth_google_calendar():
    """Connect Google Calendar for availability sync"""
    # Use the same redirect URI as regular OAuth to avoid redirect_uri_mismatch
    if 'localhost' in request.host:
        # Local development - use HTTP
        redirect_uri = f"http://{request.host}/auth/google/callback"
    elif 'droply.live' in request.host:
        # Production - force HTTPS for droply.live
        redirect_uri = "https://droply.live/auth/google/callback"
    else:
        # Fallback - force HTTPS
        redirect_uri = f"https://{request.host}/auth/google/callback"
    
    # Request calendar scope in addition to basic profile
    return google.authorize_redirect(redirect_uri, scope='openid email profile https://www.googleapis.com/auth/calendar.readonly')

@app.route('/disconnect-google-calendar', methods=['POST'])
@login_required
def disconnect_google_calendar():
    """Disconnect Google Calendar integration"""
    current_user.google_calendar_connected = False
    current_user.google_calendar_token = None
    current_user.google_calendar_refresh_token = None
    current_user.google_calendar_id = None
    
    db.session.commit()
    flash('Google Calendar disconnected successfully.', 'success')
    return redirect(url_for('account'))

@app.route('/meeting/<int:booking_id>')
@login_required
def join_meeting(booking_id):
    """Join a video meeting"""
    print(f"[DEBUG] Join meeting called for booking {booking_id}")
    booking = Booking.query.get_or_404(booking_id)
    
    print(f"[DEBUG] Booking found: {booking.id}, Status: {booking.status}")
    print(f"[DEBUG] Current user: {current_user.id}, Booking user: {booking.user_id}, Expert: {booking.expert_id}")
    
    # Check if user is authorized to join this meeting
    if booking.user_id != current_user.id and booking.expert_id != current_user.id:
        print(f"[DEBUG] User not authorized to join meeting")
        flash('You are not authorized to join this meeting.', 'error')
        return redirect(url_for('bookings'))
    
    # Check if meeting time is within 30 minutes before or after (more flexible for immediate bookings)
    from datetime import datetime, timedelta
    now = datetime.now(EASTERN_TIMEZONE)
    meeting_time = booking.start_time
    # Handle timezone-naive datetimes by assuming they're Eastern Time
    if meeting_time.tzinfo is None:
        meeting_time = meeting_time.replace(tzinfo=EASTERN_TIMEZONE)
    time_diff = abs((meeting_time - now).total_seconds() / 60)
    
    print(f"[DEBUG] Meeting time: {meeting_time}, Current time: {now}, Time diff: {time_diff} minutes")
    
    # Allow joining up to 30 minutes before or after the scheduled time
    if time_diff > 30:
        print(f"[DEBUG] Meeting not available - time difference too large")
        flash('Meeting is not available yet or has already ended.', 'warning')
        return redirect(url_for('bookings'))
    
    # Create meeting room if it doesn't exist
    if not booking.meeting_room_id or not booking.meeting_url:
        print(f"[DEBUG] No meeting room exists, creating one...")
        room_info, error = create_meeting_room(booking_id)
        if error:
            print(f"[DEBUG] Error creating meeting room: {error}")
            flash(f'Error setting up meeting: {error}', 'error')
            return redirect(url_for('bookings'))
        # Refresh booking to get updated room info
        db.session.refresh(booking)
        print(f"[DEBUG] Meeting room created successfully")
    else:
        print(f"[DEBUG] Meeting room already exists: {booking.meeting_room_id}")
    
    # Determine the other participant
    if current_user.id == booking.user_id:
        other_user = booking.expert
        is_owner = False
    else:
        other_user = booking.user
        is_owner = True
    
    print(f"[DEBUG] Other user: {other_user.username}, Is owner: {is_owner}")
    print(f"[DEBUG] Room URL: {booking.meeting_url}")
    
    # Check if Daily.co is working, fallback to simple WebRTC if not
    if not DAILY_API_KEY or DAILY_API_KEY == 'your_daily_api_key_here':
        print(f"[DEBUG] Daily.co not configured, using simple WebRTC")
        return render_template('meeting_simple.html', 
                             booking=booking, 
                             other_user=other_user)
    
    # Use the Daily.co template for video calling
    return render_template('meeting_daily.html', 
                         booking=booking, 
                         room_name=booking.meeting_room_id,
                         room_url=booking.meeting_url,
                         other_user=other_user,
                         is_owner=is_owner)

@app.route('/meeting/<int:booking_id>/start')
@login_required
def start_meeting(booking_id):
    """Mark meeting as started"""
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.expert_id != current_user.id:
        flash('Only the expert can start the meeting.', 'error')
        return redirect(url_for('bookings'))
    
    if not booking.can_join_meeting():
        flash('Meeting cannot be started at this time.', 'error')
        return redirect(url_for('bookings'))
    
    booking.meeting_started_at = datetime.now(EASTERN_TIMEZONE)
    db.session.commit()
    
    return redirect(url_for('join_meeting', booking_id=booking_id))

@app.route('/meeting/<int:booking_id>/end')
@login_required
def end_meeting(booking_id):
    """Mark meeting as ended"""
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.expert_id != current_user.id:
        flash('Only the expert can end the meeting.', 'error')
        return redirect(url_for('bookings'))
    
    booking.meeting_ended_at = datetime.now(EASTERN_TIMEZONE)
    if booking.meeting_started_at:
        duration = (booking.meeting_ended_at - booking.meeting_started_at).total_seconds() / 60
        booking.meeting_duration = int(duration)
    db.session.commit()
    
    flash('Meeting ended successfully.', 'success')
    return redirect(url_for('bookings'))

@app.route('/api/meeting/<int:booking_id>/status')
@login_required
def meeting_status(booking_id):
    """Get meeting status"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user is authorized to view this meeting
    if booking.user_id != current_user.id and booking.expert_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Determine if user can join the meeting
    can_join = booking.can_join_meeting()
    
    return jsonify({
        'booking_id': booking.id,
        'status': booking.status,
        'can_join': can_join,
        'meeting_room_id': booking.meeting_room_id,
        'meeting_url': booking.meeting_url,
        'start_time': booking.start_time.isoformat() if booking.start_time else None,
        'end_time': booking.end_time.isoformat() if booking.end_time else None
    })

@app.route('/dev-video-call')
def dev_video_call():
    """Development-only route for testing video call UI without booking"""
    # Only allow in development environment
    if os.environ.get('FLASK_ENV') != 'development':
        flash('This route is only available in development environment.', 'error')
        return redirect(url_for('index'))
    
    # Create a mock booking for testing
    mock_booking = type('MockBooking', (), {
        'id': 999,
        'meeting_room_id': 'dev-test-room',
        'meeting_url': 'https://droply-test.daily.co/dev-test-room',
        'start_time': datetime.now(EASTERN_TIMEZONE),
        'end_time': datetime.now(EASTERN_TIMEZONE) + timedelta(minutes=30),
        'status': 'confirmed',
        'user_id': 1,
        'expert_id': 2
    })()
    
    # Create mock users
    mock_user = type('MockUser', (), {
        'id': 1,
        'name': 'Test User',
        'email': 'test@example.com'
    })()
    
    mock_expert = type('MockExpert', (), {
        'id': 2,
        'name': 'Test Expert',
        'email': 'expert@example.com'
    })()
    
    # Generate meeting token
    token, error = get_meeting_token('dev-test-room', 1, True)
    if error:
        print(f"Error generating token: {error}")
        token = "dev-test-token"
    
    return render_template('meeting.html', 
                         booking=mock_booking, 
                         token=token, 
                         room_name='dev-test-room',
                         other_user=mock_expert,
                         current_user=mock_user)

@app.route('/dev-simple-video-call')
def dev_simple_video_call():
    """Development-only route for testing simple WebRTC video call UI"""
    # Only allow in development environment
    if os.environ.get('FLASK_ENV') != 'development':
        flash('This route is only available in development environment.', 'error')
        return redirect(url_for('index'))
    
    # Create a mock booking for testing
    mock_booking = type('MockBooking', (), {
        'id': 998,
        'meeting_room_id': 'dev-simple-room',
        'meeting_url': 'https://meet.daily.co/dev-simple-room',
        'start_time': datetime.now(EASTERN_TIMEZONE),
        'end_time': datetime.now(EASTERN_TIMEZONE) + timedelta(minutes=30),
        'status': 'confirmed',
        'user_id': 1,
        'expert_id': 2
    })()
    
    # Create mock users
    mock_user = type('MockUser', (), {
        'id': 1,
        'name': 'Test User',
        'email': 'test@example.com'
    })()
    
    mock_expert = type('MockExpert', (), {
        'id': 2,
        'name': 'Test Expert',
        'email': 'expert@example.com'
    })()
    
    return render_template('meeting_simple.html', 
                         booking=mock_booking, 
                         room_name='dev-simple-room',
                         other_user=mock_expert,
                         current_user=mock_user)

@app.route('/test-meeting/<int:booking_id>')
def test_meeting(booking_id):
    """Temporary test route for video calling - bypasses authentication"""
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Create meeting room if it doesn't exist
        if not booking.meeting_room_id:
            room_info, error = create_meeting_room(booking_id)
            if error:
                print(f"Error creating meeting room: {error}")
                # Fall back to simple meeting
                booking.meeting_room_id = f"test-room-{booking_id}"
                booking.meeting_url = f"https://droply-test.daily.co/test-room-{booking_id}"
                db.session.commit()
        
        # Generate meeting token
        token, error = get_meeting_token(booking.meeting_room_id, 1, True)
        if error:
            print(f"Error generating token: {error}")
            # Use a simple token
            token = "test-token"
        
        # Determine the other participant
        other_user = booking.expert
        
        # Use Daily.co template
        template_name = 'meeting.html'
        
        return render_template(template_name, 
                             booking=booking, 
                             token=token, 
                             room_name=booking.meeting_room_id,
                             other_user=other_user)
                             
    except Exception as e:
        print(f"Error in test_meeting: {e}")
        return f"Error: {str(e)}", 500

@app.route('/simple-test-meeting/<int:booking_id>')
def simple_test_meeting(booking_id):
    """Simple test route that bypasses Daily.co entirely"""
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Set up simple meeting data
        booking.meeting_room_id = f"simple-test-{booking_id}"
        booking.meeting_url = f"https://meet.daily.co/simple-test-{booking_id}"
        db.session.commit()
        
        # Determine the other participant
        other_user = booking.expert
        
        # Always use simple template
        return render_template('meeting_simple.html', 
                             booking=booking, 
                             token="simple-token",
                             other_user=other_user)
                             
    except Exception as e:
        print(f"Error in simple_test_meeting: {e}")
        return f"Error: {str(e)}", 500

@app.route('/force-simple-meeting/<int:booking_id>')
@login_required
def force_simple_meeting(booking_id):
    """Force use of simple WebRTC meeting with controls"""
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Check if user is authorized to join this meeting
        if booking.user_id != current_user.id and booking.expert_id != current_user.id:
            flash('You are not authorized to join this meeting.', 'error')
            return redirect(url_for('bookings'))
        
        # Determine the other participant
        if current_user.id == booking.user_id:
            other_user = booking.expert
        else:
            other_user = booking.user
        
        # Force use simple template with controls
        return render_template('meeting_simple.html', 
                             booking=booking, 
                             other_user=other_user)
                             
    except Exception as e:
        print(f"Error in force_simple_meeting: {e}")
        return f"Error: {str(e)}", 500

@app.route('/test-booking/<username>')
@login_required
def test_booking(username):
    """Create a test booking without payment for testing"""
    try:
        expert = User.query.filter_by(username=username).first_or_404()
        
        # Create a test booking for immediate use
        from datetime import datetime, timedelta
        now = datetime.now()
        start_time = now + timedelta(minutes=1)  # 1 minute from now
        end_time = start_time + timedelta(minutes=30)
        
        booking = Booking(
            user_id=current_user.id,
            expert_id=expert.id,
            start_time=start_time,
            end_time=end_time,
            duration=30,
            status='confirmed',  # Skip payment for testing
            payment_status='paid',
            payment_amount=5.00
        )
        
        db.session.add(booking)
        db.session.commit()
        
        flash('Test booking created successfully!', 'success')
        return redirect(url_for('join_meeting', booking_id=booking.id))
        
    except Exception as e:
        print(f"Error creating test booking: {e}")
        flash(f'Error creating test booking: {str(e)}', 'error')
        return redirect(url_for('user_profile', username=username))

@app.route('/daily-test/<int:booking_id>')
def daily_test(booking_id):
    """Simple Daily.co test route"""
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Create a simple Daily.co room
        room_name = f"droply-test-{booking_id}"
        room_url = f"https://droply-test.daily.co/{room_name}"
        
        # Update booking with room info
        booking.meeting_room_id = room_name
        booking.meeting_url = room_url
        db.session.commit()
        
        # Determine the other participant
        other_user = booking.expert
        
        return render_template('meeting.html', 
                             booking=booking, 
                             token="test-token", 
                             room_name=room_name,
                             other_user=other_user)
                             
    except Exception as e:
        print(f"Error in daily_test: {e}")
        return f"Error: {str(e)}", 500

@app.route('/simple-daily-test/<int:booking_id>')
def simple_daily_test(booking_id):
    """Very simple Daily.co test route"""
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Create meeting room if it doesn't exist
        if not booking.meeting_room_id or not booking.meeting_url:
            room_info, error = create_meeting_room(booking_id)
            if error:
                return f"Error creating room: {error}", 500
            # Refresh booking to get updated room info
            db.session.refresh(booking)
        
        # Return simple HTML with Daily.co iframe
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Daily.co Test</title>
            <script src="https://unpkg.com/@daily-co/daily-js"></script>
        </head>
        <body>
            <h1>Daily.co Video Call Test</h1>
            <p>Room: {booking.meeting_room_id}</p>
            <p>URL: {booking.meeting_url}</p>
            <div id="video-container" style="width: 100%; height: 500px;"></div>
            <script>
                const callObject = DailyIframe.createFrame(document.getElementById('video-container'), {{
                    iframeStyle: {{
                        width: '100%',
                        height: '100%',
                        border: '0'
                    }}
                }});
                callObject.join({{
                    url: '{booking.meeting_url}'
                }});
            </script>
        </body>
        </html>
        """
        
        return html
                             
    except Exception as e:
        print(f"Error in simple_daily_test: {e}")
        return f"Error: {str(e)}", 500

@app.route('/test-meeting-auth/<int:booking_id>')
def test_meeting_auth(booking_id):
    """Temporary test route that bypasses authentication for Daily.co testing"""
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Create meeting room if it doesn't exist
        if not booking.meeting_room_id or not booking.meeting_url:
            room_info, error = create_meeting_room(booking_id)
            if error:
                return f"Error creating room: {error}", 500
            # Refresh booking to get updated room info
            db.session.refresh(booking)
        
        # Get the other participant
        other_user = booking.expert
        
        # Use the working Daily.co template
        return render_template('meeting_daily.html', 
                             booking=booking, 
                             room_name=booking.meeting_room_id,
                             room_url=booking.meeting_url,
                             other_user=other_user,
                             is_owner=True)
                             
    except Exception as e:
        print(f"Error in test_meeting_auth: {e}")
        return f"Error: {str(e)}", 500

@app.route('/debug-bookings')
@login_required
def debug_bookings():
    """Debug route to check bookings query"""
    from models import Booking, User
    from datetime import datetime, timezone
    from sqlalchemy import func
    
    now = datetime.now(EASTERN_TIMEZONE)
    
    # Get all bookings for current user as expert
    all_bookings = Booking.query.filter(
        Booking.expert_id == current_user.id
    ).order_by(Booking.start_time.desc()).all()
    
    # Test the upcoming query
    upcoming_as_expert = Booking.query.filter(
        (Booking.expert_id == current_user.id) &
        (func.datetime(Booking.start_time) >= now.replace(tzinfo=None))
    ).order_by(Booking.start_time.asc()).all()
    
    debug_info = {
        'current_time_utc': str(now),
        'current_time_naive': str(now.replace(tzinfo=None)),
        'total_bookings': len(all_bookings),
        'upcoming_bookings': len(upcoming_as_expert),
        'all_bookings': [
            {
                'id': b.id,
                'start_time': str(b.start_time),
                'status': b.status,
                'is_future': b.start_time > now.replace(tzinfo=None)
            } for b in all_bookings[:5]
        ],
        'upcoming_bookings_detail': [
            {
                'id': b.id,
                'start_time': str(b.start_time),
                'status': b.status
            } for b in upcoming_as_expert
        ]
    }
    
    return jsonify(debug_info)

@app.route('/test-bookings')
@login_required
def test_bookings():
    """Simple test route to debug bookings query"""
    from models import Booking
    from datetime import datetime, timezone
    
    now = datetime.now(EASTERN_TIMEZONE)
    
    # Simple query without timezone complexity
    all_bookings = Booking.query.filter(
        Booking.expert_id == current_user.id
    ).all()
    
    # Manual filtering in Python
    upcoming = []
    past = []
    
    for booking in all_bookings:
        if booking.start_time > now.replace(tzinfo=None):
            upcoming.append(booking)
        else:
            past.append(booking)
    
    result = {
        'current_user_id': current_user.id,
        'current_time': str(now),
        'total_bookings': len(all_bookings),
        'upcoming_count': len(upcoming),
        'past_count': len(past),
        'upcoming_bookings': [
            {
                'id': b.id,
                'start_time': str(b.start_time),
                'status': b.status
            } for b in upcoming
        ]
    }
    
    return jsonify(result)

@app.route('/debug-auth')
def debug_auth():
    """Debug route to check authentication status"""
    from flask_login import current_user
    
    debug_info = {
        'is_authenticated': current_user.is_authenticated,
        'user_id': current_user.id if current_user.is_authenticated else None,
        'username': current_user.username if current_user.is_authenticated else None,
        'email': current_user.email if current_user.is_authenticated else None
    }
    
    return jsonify(debug_info)

# Referral Helper Functions

def process_referral_reward_for_booking(booking_id):
    """Process referral reward for a booking - helper function"""
    booking = Booking.query.get(booking_id)
    if not booking:
        return False
    
    # Check if the user was referred
    if not booking.user.referred_by:
        return False
    
    # Get the referrer
    referrer = User.query.get(booking.user.referred_by)
    if not referrer:
        return False
    
    # Check if this is the user's first paid booking
    previous_paid_bookings = Booking.query.filter_by(
        user_id=booking.user.id,
        payment_status='paid'
    ).filter(Booking.id != booking_id).count()
    
    if previous_paid_bookings > 0:
        return False  # Not the first booking
    
    # Check if reward already exists
    existing_reward = ReferralReward.query.filter_by(
        referrer_id=referrer.id,
        referred_user_id=booking.user.id,
        booking_id=booking_id
    ).first()
    
    if existing_reward:
        return False  # Reward already processed
    
    # Create the reward
    reward_amount = 10.0  # $10 per successful referral
    reward = ReferralReward(
        referrer_id=referrer.id,
        referred_user_id=booking.user.id,
        booking_id=booking_id,
        reward_amount=reward_amount,
        reward_type='booking',
        status='pending'
    )
    
    # Update referral status
    referral = Referral.query.filter_by(
        referrer_id=referrer.id,
        referred_user_id=booking.user.id
    ).first()
    
    if referral:
        referral.status = 'completed'
    
    # Update referrer's stats
    referrer.referral_count += 1
    referrer.total_referral_earnings += reward_amount
    
    db.session.add(reward)
    db.session.commit()
    
    print(f"Referral reward processed: ${reward_amount} for referrer {referrer.username}")
    return True

# Referral API Endpoints

@app.route('/api/referrals/generate-code', methods=['POST'])
@login_required
def generate_referral_code():
    """Generate a new referral code for the current user"""
    try:
        # Generate new referral code
        new_code = current_user.generate_referral_code()
        db.session.commit()
        
        # Get the full referral link
        referral_link = current_user.get_referral_link()
        
        return jsonify({
            'success': True,
            'referral_code': new_code,
            'referral_link': referral_link
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/referrals/history', methods=['GET'])
@login_required
def get_referral_history():
    """Get referral history for the current user"""
    try:
        # Get all referrals made by this user
        referrals = Referral.query.filter_by(referrer_id=current_user.id).order_by(Referral.created_at.desc()).all()
        
        referral_data = []
        for referral in referrals:
            # Get reward information if available
            reward = ReferralReward.query.filter_by(
                referrer_id=current_user.id,
                referred_user_id=referral.referred_user_id
            ).first()
            
            referral_data.append({
                'id': referral.id,
                'referred_user_name': referral.referred_user.full_name or referral.referred_user.username,
                'created_at': referral.created_at.isoformat(),
                'status': referral.status,
                'reward_amount': reward.reward_amount if reward else None
            })
        
        return jsonify({
            'success': True,
            'referrals': referral_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/referrals/stats', methods=['GET'])
@login_required
def get_referral_stats():
    """Get referral statistics for the current user"""
    try:
        # Get total referrals
        total_referrals = Referral.query.filter_by(referrer_id=current_user.id).count()
        
        # Get completed referrals (users who made bookings)
        completed_referrals = Referral.query.filter_by(
            referrer_id=current_user.id,
            status='completed'
        ).count()
        
        # Get total earnings
        total_earnings = current_user.total_referral_earnings or 0
        
        # Get pending earnings
        pending_rewards = ReferralReward.query.filter_by(
            referrer_id=current_user.id,
            status='pending'
        ).all()
        pending_earnings = sum(reward.reward_amount for reward in pending_rewards)
        
        return jsonify({
            'success': True,
            'stats': {
                'total_referrals': total_referrals,
                'completed_referrals': completed_referrals,
                'total_earnings': total_earnings,
                'pending_earnings': pending_earnings
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/referrals/track', methods=['POST'])
def track_referral():
    """Track a referral when someone signs up with a referral code"""
    try:
        data = request.get_json()
        referral_code = data.get('referral_code')
        user_id = data.get('user_id')
        
        if not referral_code or not user_id:
            return jsonify({
                'success': False,
                'error': 'Missing referral_code or user_id'
            }), 400
        
        # Find the referrer by referral code
        referrer = User.query.filter_by(referral_code=referral_code).first()
        if not referrer:
            return jsonify({
                'success': False,
                'error': 'Invalid referral code'
            }), 400
        
        # Get the referred user
        referred_user = User.query.get(user_id)
        if not referred_user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 400
        
        # Check if this user was already referred
        existing_referral = Referral.query.filter_by(
            referrer_id=referrer.id,
            referred_user_id=referred_user.id
        ).first()
        
        if existing_referral:
            return jsonify({
                'success': False,
                'error': 'User already referred'
            }), 400
        
        # Create the referral record
        referral = Referral(
            referrer_id=referrer.id,
            referred_user_id=referred_user.id,
            referral_code=referral_code,
            status='pending'
        )
        
        # Update the referred user's referred_by field
        referred_user.referred_by = referrer.id
        
        db.session.add(referral)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'referral_id': referral.id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/referrals/process-reward', methods=['POST'])
def process_referral_reward():
    """Process a referral reward when a referred user makes their first booking"""
    try:
        data = request.get_json()
        booking_id = data.get('booking_id')
        
        if not booking_id:
            return jsonify({
                'success': False,
                'error': 'Missing booking_id'
            }), 400
        
        # Get the booking
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({
                'success': False,
                'error': 'Booking not found'
            }), 400
        
        # Check if the user was referred
        if not booking.user.referred_by:
            return jsonify({
                'success': False,
                'error': 'User was not referred'
            }), 400
        
        # Get the referrer
        referrer = User.query.get(booking.user.referred_by)
        if not referrer:
            return jsonify({
                'success': False,
                'error': 'Referrer not found'
            }), 400
        
        # Check if this is the user's first booking
        previous_bookings = Booking.query.filter_by(
            user_id=booking.user.id,
            payment_status='paid'
        ).filter(Booking.id != booking_id).count()
        
        if previous_bookings > 0:
            return jsonify({
                'success': False,
                'error': 'Not the user\'s first booking'
            }), 400
        
        # Check if reward already exists
        existing_reward = ReferralReward.query.filter_by(
            referrer_id=referrer.id,
            referred_user_id=booking.user.id,
            booking_id=booking_id
        ).first()
        
        if existing_reward:
            return jsonify({
                'success': False,
                'error': 'Reward already processed'
            }), 400
        
        # Create the reward
        reward_amount = 10.0  # $10 per successful referral
        reward = ReferralReward(
            referrer_id=referrer.id,
            referred_user_id=booking.user.id,
            booking_id=booking_id,
            reward_amount=reward_amount,
            reward_type='booking',
            status='pending'
        )
        
        # Update referral status
        referral = Referral.query.filter_by(
            referrer_id=referrer.id,
            referred_user_id=booking.user.id
        ).first()
        
        if referral:
            referral.status = 'completed'
        
        # Update referrer's stats
        referrer.referral_count += 1
        referrer.total_referral_earnings += reward_amount
        
        db.session.add(reward)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'reward_id': reward.id,
            'reward_amount': reward_amount
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Privacy Policy and Terms of Service routes
@app.route('/privacy-policy')
def privacy_policy():
    """Display the privacy policy page"""
    return render_template('privacy_policy.html')

@app.route('/terms-of-service')
def terms_of_service():
    """Display the terms of service page"""
    return render_template('terms_of_service.html')
