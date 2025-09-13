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
from datetime import datetime, timezone, timedelta

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
        # Generate a unique room name
        room_name = f"droply-{booking_id}"
        
        # Create the room on Daily.co with minimal settings for free tier
        headers = {
            'Authorization': f'Bearer {DAILY_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Use minimal room data that works with free tier
        room_data = {
            'name': room_name,
            'privacy': 'public',  # Use public for free tier
            'max_participants': 2,
            'autojoin': True,
            'enable_chat': True,
            'enable_recording': 'cloud',
            'exp': int((datetime.now() + timedelta(minutes=35)).timestamp())  # Room expires in 35 minutes
        }
        
        response = requests.post(
            f'{DAILY_API_URL}/rooms',
            headers=headers,
            json=room_data
        )
        
        if response.status_code == 200:
            room_info = response.json()
            room_url = room_info.get('url')
            
            # Update the booking with room info
            booking = Booking.query.get(booking_id)
            if booking:
                booking.meeting_room_id = room_name
                booking.meeting_url = room_url
                db.session.commit()
            
            return room_info, None
        else:
            return None, f"Failed to create room: {response.text}"
            
    except Exception as e:
        return None, f"Error creating room: {str(e)}"

def get_meeting_token(room_name, user_id, is_owner=False):
    """Generate a meeting token for a user"""
    # For now, just return a simple token since Daily.co token generation is complex
    # In production, you'd want to implement proper token generation
    return f"simple-token-{user_id}-{is_owner}", None

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')  # Use environment variable
YOUR_DOMAIN = os.environ.get('YOUR_DOMAIN', 'https://f6b540a7cf43.ngrok-free.app')

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
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('homepage'))

@app.route('/profile/<username>')
def profile(username):
    """View user profile - public route"""
    user = User.query.filter_by(username=username).first_or_404()
    
    # If user is logged in and viewing own profile, redirect to profile setup
    if current_user.is_authenticated and current_user.username == username:
        return redirect(url_for('profile_setup'))
    
    # Otherwise show the public profile view (for both logged in and anonymous users)
    return render_template('profile_view.html', user=user)

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
    
    # Show the public profile view (same as profile_view.html)
    return render_template('profile_view.html', user=user)

@app.route('/expert/<username>')
@login_required
def expert_profile(username):
    """View expert profile for booking"""
    expert = User.query.filter_by(username=username).first_or_404()
    
    # Get expert's availability for booking
    availability_rules = AvailabilityRule.query.filter_by(user_id=expert.id).all()
    
    return render_template('expert_profile.html', expert=expert, availability_rules=availability_rules)

@app.route('/expert/<username>/book')
@login_required
def expert_booking_times(username):
    """Select available booking times for an expert"""
    expert = User.query.filter_by(username=username).first_or_404()
    
    # Get expert's availability rules
    availability_rules = AvailabilityRule.query.filter_by(user_id=expert.id).all()
    
    # Get available times for the next 7 days
    available_times = []
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    if availability_rules:
        for i in range(7):  # Next 7 days
            check_date = today + timedelta(days=i)
            
            # Get availability for this date
            for rule in availability_rules:
                if rule.weekday == check_date.weekday():
                    # Generate time slots for this day
                    start_time = datetime.combine(check_date, rule.start)
                    end_time = datetime.combine(check_date, rule.end)
                    
                    # Generate 30-minute slots
                    current_time = start_time
                    while current_time + timedelta(minutes=30) <= end_time:
                        # Check if this slot is not already booked
                        existing_booking = Booking.query.filter(
                            (Booking.expert_id == expert.id) &
                            (Booking.start_time == current_time) &
                            (Booking.status.in_(['confirmed', 'pending']))
                        ).first()
                        
                        if not existing_booking and current_time > datetime.now():
                            available_times.append({
                                'datetime': current_time,
                                'formatted_date': current_time.strftime('%B %d, %Y'),
                                'formatted_time': current_time.strftime('%I:%M %p'),
                                'iso_datetime': current_time.isoformat()
                            })
                        
                        current_time += timedelta(minutes=30)
    
    return render_template('expert_booking_times.html', 
                         expert=expert, 
                         available_times=available_times,
                         has_availability=bool(availability_rules))


@app.route('/expert/<username>/book-immediate')
@login_required
def book_immediate_meeting(username):
    """Book an immediate meeting with an expert"""
    expert = User.query.filter_by(username=username).first_or_404()
    
    # Check if expert is available
    if not expert.is_available:
        flash('This expert is not currently available for immediate meetings.', 'error')
        return redirect(url_for('expert_profile', username=username))
    
    # Create immediate meeting time (starts in 5 minutes)
    from datetime import datetime, timedelta
    now = datetime.now()
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

@app.route('/referrals')
@login_required
def referrals():
    """Referrals page"""
    return render_template('referrals.html')

@app.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    """Delete user account"""
    print("=" * 50)
    print("DELETE ACCOUNT ROUTE CALLED")
    print(f"Delete account request received from user: {current_user.email}")
    print(f"Form data: {request.form}")
    print(f"Request method: {request.method}")
    print(f"Request headers: {dict(request.headers)}")
    print("=" * 50)
    
    try:
        # Get the confirmation text and reason
        confirmation = request.form.get('confirmation', '').strip()
        reason = request.form.get('reason', '').strip()
        
        print(f"Confirmation text received: '{confirmation}'")
        print(f"Reason received: '{reason}'")
        
        if confirmation != current_user.username:
            print(f"Confirmation text mismatch. Expected '{current_user.username}', got '{confirmation}'")
            flash('Please type your username exactly to confirm account deletion.', 'error')
            return redirect(url_for('account'))
        
        # Get current user
        user = current_user
        
        # Log the deletion reason if provided
        if reason:
            print(f"Account deletion reason for {user.email}: {reason}")
        
        print(f"Starting account deletion for user: {user.email} (ID: {user.id})")
        
        # Delete associated data first (foreign key constraints)
        # Delete favorites (both as user and as expert)
        favorites_as_user_deleted = Favorite.query.filter_by(user_id=user.id).delete()
        favorites_as_expert_deleted = Favorite.query.filter_by(expert_id=user.id).delete()
        print(f"Deleted {favorites_as_user_deleted} favorites as user and {favorites_as_expert_deleted} favorites as expert")
        
        # Delete bookings (both as client and as expert)
        bookings_deleted = Booking.query.filter_by(user_id=user.id).delete()
        expert_bookings_deleted = Booking.query.filter_by(expert_id=user.id).delete()
        print(f"Deleted {bookings_deleted} bookings as client and {expert_bookings_deleted} bookings as expert")
        
        # Delete availability rules and exceptions
        rules_deleted = AvailabilityRule.query.filter_by(user_id=user.id).delete()
        exceptions_deleted = AvailabilityException.query.filter_by(user_id=user.id).delete()
        print(f"Deleted {rules_deleted} availability rules and {exceptions_deleted} availability exceptions")
        
        # Delete payouts
        payouts_deleted = Payout.query.filter_by(expert_id=user.id).delete()
        print(f"Deleted {payouts_deleted} payouts")
        
        # Clean up profile pictures and uploaded files
        if user.profile_picture:
            try:
                import os
                profile_pic_path = os.path.join('static', 'uploads', user.profile_picture.split('/')[-1])
                if os.path.exists(profile_pic_path):
                    os.remove(profile_pic_path)
            except Exception as e:
                print(f"Error deleting profile picture: {e}")
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        print(f"Successfully deleted user account: {user.email}")
        
        # Log out the user
        logout_user()
        
        flash('Your account has been permanently deleted.', 'info')
        return redirect(url_for('homepage'))
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting account: {str(e)}")
        print(f"Exception type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        flash(f'Error deleting account: {str(e)}. Please try again.', 'error')
        return redirect(url_for('account'))

@app.route('/find-experts')
@login_required
def find_experts():
    """Find experts page for signed-in users"""
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
                    return render_template('find_experts.html', 
                                         experts=experts, 
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

    
    return render_template('find_experts.html', 
                         experts=experts, 
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

# @app.route('/calendar')
# @login_required
# def calendar():
#     """Calendar view - Temporarily disabled due to missing TimeSlot model"""
#     return render_template('calendar.html', time_slots=[])

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

@app.route('/create-checkout-session/<int:booking_id>', methods=['POST', 'GET'])
def create_checkout_session(booking_id):
    """Create Stripe checkout session"""
    # Production safeguard
    if is_production_environment() and stripe.api_key.startswith('sk_test_'):
        flash('Payment system temporarily unavailable. Please try again later.', 'error')
        return redirect(url_for('homepage'))
    
    booking = Booking.query.get_or_404(booking_id)
    
    try:
        # Get expert details for the checkout session
        expert = User.query.get(booking.expert_id)
        if not expert:
            flash('Expert not found', 'error')
            return redirect(url_for('homepage'))
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',  # Default to USD for now
                    'product_data': {
                        'name': f'Session with {expert.full_name or expert.username}',
                        'description': f'{booking.duration}-minute video consultation on {booking.start_time.strftime("%B %d, %Y at %I:%M %p")}',
                    },
                    'unit_amount': int(booking.payment_amount * 100),  # Amount in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'{YOUR_DOMAIN}/booking/success/{booking.id}',
            cancel_url=f'{YOUR_DOMAIN}/booking/cancel/{booking.id}',
            metadata={
                'booking_id': booking.id
            }
        )
        
        booking.stripe_session_id = checkout_session.id
        db.session.commit()
        
        return redirect(checkout_session.url, code=303)
        
    except Exception as e:
        flash(f'Payment error: {str(e)}', 'error')
        return redirect(url_for('profile', username=expert.username))

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
    """Booking cancel page"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Mark booking as cancelled
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
    return redirect(url_for('profile', username=username))

@app.route('/bookings')
@login_required
def bookings():
    """View user's bookings and calendar"""
    from models import Booking, User
    from datetime import datetime, timezone
    from sqlalchemy import func
    
    now = datetime.now(EASTERN_TIMEZONE)
    
    # Bookings where the user is the booker (client)
    upcoming_as_client = Booking.query.filter(
        (Booking.user_id == current_user.id) &
        (func.datetime(Booking.start_time) >= now.replace(tzinfo=None))
    ).order_by(Booking.start_time.asc()).all()
    
    past_as_client = Booking.query.filter(
        (Booking.user_id == current_user.id) &
        (func.datetime(Booking.start_time) < now.replace(tzinfo=None))
    ).order_by(Booking.start_time.desc()).all()
    
    # Bookings where the user is the expert (provider)
    upcoming_as_expert = Booking.query.filter(
        (Booking.expert_id == current_user.id) &
        (func.datetime(Booking.start_time) >= now.replace(tzinfo=None))
    ).order_by(Booking.start_time.asc()).all()
    
    past_as_expert = Booking.query.filter(
        (Booking.expert_id == current_user.id) &
        (func.datetime(Booking.start_time) < now.replace(tzinfo=None))
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
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        flash('You are not authorized to cancel this booking.', 'error')
        return redirect(url_for('bookings'))
    if booking.status not in ['pending', 'confirmed']:
        flash('This booking cannot be cancelled.', 'error')
        return redirect(url_for('bookings'))
    
    from datetime import datetime, timedelta
    now = datetime.now()
    time_until_booking = booking.start_time - now
    
    # Check 24-hour cancellation policy
    if time_until_booking < timedelta(hours=24):
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
            booking.status = 'cancelled'
            booking.payment_status = 'cancelled'
            flash('❌ Booking cancelled successfully.', 'success')
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error processing cancellation: {str(e)}', 'error')
        return redirect(url_for('bookings'))
    
    return redirect(url_for('bookings'))

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

@app.route('/api/profile/update', methods=['POST'])
@login_required
def api_profile_update():
    """Update user profile via API"""
    try:
        data = request.get_json()
        
        # Update basic profile fields (for account page auto-save)
        if 'full_name' in data:
            current_user.full_name = data['full_name']
        if 'bio' in data:
            current_user.bio = data['bio']
            
        # Update preference fields (for settings page auto-save)
        if 'language' in data:
            current_user.language = data['language']
        if 'timezone' in data:
            current_user.timezone = data['timezone']
        if 'email_notifications' in data:
            current_user.email_notifications = data['email_notifications']
            
        # Legacy support for other profile fields
        if 'name' in data:
            current_user.full_name = data['name']
        if 'title' in data:
            current_user.profession = data['title']
        if 'description' in data:
            current_user.bio = data['description']
        if 'rate' in data:
            current_user.hourly_rate = float(data['rate']) if data['rate'] else 0
        if 'category' in data:
            current_user.industry = data['category']
            
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
        if 'snapchat' in data:
            current_user.snapchat_url = data['snapchat']
        if 'website' in data:
            current_user.website_url = data['website']
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

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
                'end': r.end.strftime('%H:%M')
            } for r in rules
        ]
        print(f"Returning availability rules: {result}")
        return jsonify(result)
    else:
        data = request.get_json()
        rules = data.get('rules', [])
        AvailabilityRule.query.filter_by(user_id=current_user.id).delete()
        for r in rules:
            if r.get('enabled'):
                db.session.add(AvailabilityRule(
                    user_id=current_user.id,
                    weekday=r['weekday'],
                    start=datetime.strptime(r['start'], '%H:%M').time(),
                    end=datetime.strptime(r['end'], '%H:%M').time()
                ))
        db.session.commit()
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
    return jsonify({
        'connected': current_user.google_calendar_connected,
        'calendar_id': current_user.google_calendar_id
    })

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
        hourly_rate = expert.hourly_rate or 0
        # For 30-minute sessions, session fee is always 50% of hourly rate
        if duration == 30:
            session_fee = hourly_rate * 0.5
        else:
            session_fee = (hourly_rate * duration) / 60  # fallback for other durations
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
        hourly_rate = expert.hourly_rate or 0
        if duration == 30:
            session_fee = hourly_rate * 0.5
        else:
            session_fee = (hourly_rate * duration) / 60
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
        
        # Redirect to Stripe checkout
        print("DEBUG: Redirecting to Stripe checkout")
        return redirect(url_for('create_checkout_session', booking_id=booking.id))

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
            
        except stripe.error.StripeError as e:
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
        except stripe.error.StripeError as e:
            # Fallback to direct URL if login link fails
            dashboard_url = f"https://connect.stripe.com/express/{current_user.stripe_account_id}/settings"
            return redirect(dashboard_url)
            
    except stripe.error.StripeError as e:
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

@app.route('/expert/payouts')
@login_required
def expert_payouts():
    """Show expert's payout history"""
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
    redirect_uri = url_for('auth_google_callback', _external=True)
    print(f"DEBUG: Google OAuth redirect_uri = {redirect_uri}")
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/google/callback')
def auth_google_callback():
    token = google.authorize_access_token()
    user_info = google.userinfo()
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
    
    # Check if this is a calendar integration request (has calendar scope)
    if 'calendar' in token.get('scope', ''):
        print(f"DEBUG: Calendar integration detected. Scope: {token.get('scope', '')}")
        try:
            # Store the calendar tokens for the current user
            user.google_calendar_connected = True
            user.google_calendar_token = token.get('access_token')
            user.google_calendar_refresh_token = token.get('refresh_token')
            print(f"DEBUG: Stored calendar tokens for user {user.id}")
            
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
            
            # Find primary calendar
            primary_calendar = None
            for calendar in calendar_list.get('items', []):
                if calendar.get('primary'):
                    primary_calendar = calendar
                    break
            
            if primary_calendar:
                user.google_calendar_id = primary_calendar['id']
                print(f"DEBUG: Set primary calendar ID: {primary_calendar['id']}")
            else:
                print("DEBUG: No primary calendar found, using first calendar")
                if calendar_list.get('items'):
                    user.google_calendar_id = calendar_list['items'][0]['id']
            
            db.session.commit()
            print("DEBUG: Calendar integration completed successfully")
            flash('Google Calendar connected successfully!', 'success')
            # Redirect back to account page for calendar connection
            login_user(user)
            return redirect(url_for('account'))
            
        except Exception as e:
            print(f"ERROR: Failed to connect Google Calendar: {e}")
            import traceback
            traceback.print_exc()
            flash('Failed to connect Google Calendar. Please try again.', 'error')
            # If this was a calendar connection attempt, redirect back to account page
            if 'calendar' in token.get('scope', ''):
                login_user(user)
                return redirect(url_for('account'))
    
    login_user(user)
    
    if is_new_user:
        flash('Welcome! Please complete your profile setup.', 'success')
        return redirect(url_for('onboarding'))
    else:
        if 'calendar' not in token.get('scope', ''):
            flash('Logged in with Google!', 'success')
        return redirect(url_for('dashboard'))

# Google Calendar Integration Routes
@app.route('/auth/google-calendar')
@login_required
def auth_google_calendar():
    """Connect Google Calendar for availability sync"""
    # Use the existing Google OAuth but with calendar scope
    redirect_uri = url_for('auth_google_callback', _external=True)
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
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user is authorized to join this meeting
    if booking.user_id != current_user.id and booking.expert_id != current_user.id:
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
    
    # Allow joining up to 30 minutes before or after the scheduled time
    if time_diff > 30:
        flash('Meeting is not available yet or has already ended.', 'warning')
        return redirect(url_for('bookings'))
    
    # Create meeting room if it doesn't exist
    if not booking.meeting_room_id or not booking.meeting_url:
        room_info, error = create_meeting_room(booking_id)
        if error:
            flash(f'Error setting up meeting: {error}', 'error')
            return redirect(url_for('bookings'))
        # Refresh booking to get updated room info
        db.session.refresh(booking)
    
    # Determine the other participant
    if current_user.id == booking.user_id:
        other_user = booking.expert
        is_owner = False
    else:
        other_user = booking.user
        is_owner = True
    
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
                             room_name=booking.meeting_room_id,
                             other_user=other_user)
                             
    except Exception as e:
        print(f"Error in simple_test_meeting: {e}")
        return f"Error: {str(e)}", 500

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
