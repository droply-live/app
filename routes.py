import os
import stripe
from datetime import datetime, timezone, timedelta
from flask import render_template, request, redirect, url_for, flash, session, make_response, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_, and_, case
from app import app, db
from models import User, TimeSlot, Booking
from forms import RegistrationForm, LoginForm, ProfileForm, TimeSlotForm, BookingForm, SearchForm, OnboardingForm
from utils import generate_ical_content
import json
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import time

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_default')
YOUR_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')
if not YOUR_DOMAIN.startswith('http'):
    YOUR_DOMAIN = f"https://{YOUR_DOMAIN}" if os.environ.get('REPLIT_DEPLOYMENT') else f"http://{YOUR_DOMAIN}"

# Load the model once when the app starts
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"Error loading SentenceTransformer model: {e}")
    model = None

@app.route('/')
def index():
    """Homepage with search and filtering for providers"""
    form = SearchForm(request.args)
    
    # Base query for available users
    query_obj = User.query.filter(User.is_available == True, User.full_name.isnot(None))

    search_query = request.args.get('query', '').strip()

    if search_query and model:
        # SEMANTIC SEARCH LOGIC
        users_with_embeddings = User.query.filter(User.embedding.isnot(None)).all()
        
        if users_with_embeddings:
            user_embeddings = np.array([user.get_embedding() for user in users_with_embeddings]).astype('float32')
            user_ids = [user.id for user in users_with_embeddings]
            
            if user_embeddings.shape[0] > 0:
                d = user_embeddings.shape[1]
                index = faiss.IndexFlatL2(d)
                index = faiss.IndexIDMap(index)
                index.add_with_ids(user_embeddings, np.array(user_ids))
                
                query_embedding = model.encode([search_query], convert_to_numpy=True).astype('float32')
                
                # Search for top 50 results
                k = min(50, len(users_with_embeddings))
                distances, found_ids = index.search(query_embedding, k)
                
                # Filter out -1s which indicate no result
                found_ids = [uid for uid in found_ids[0] if uid != -1]

                if found_ids:
                    # Order the results based on the search
                    whens = {found_ids[i]: i for i in range(len(found_ids))}
                    ordering = case(whens, value=User.id)
                    query_obj = query_obj.filter(User.id.in_(found_ids)).order_by(ordering)
                else:
                    # No semantic matches, return no users
                    query_obj = query_obj.filter(User.id == -1) 
    elif search_query:
        # FALLBACK TO KEYWORD SEARCH
        search_term = f"%{search_query}%"
        query_obj = query_obj.filter(
            or_(
                User.full_name.ilike(search_term),
                User.profession.ilike(search_term),
                User.industry.ilike(search_term),
                User.bio.ilike(search_term),
                User.specialty_tags.ilike(search_term)
            )
        )

    # Apply advanced filters
    if request.args.get('category') and request.args.get('category') != 'All Categories':
        category_term = f"%{request.args['category']}%"
        query_obj = query_obj.filter(User.industry.ilike(category_term))

    if request.args.get('price') and request.args.get('price') != 'Any Price':
        if request.args['price'] == 'free':
            query_obj = query_obj.filter(User.hourly_rate == 0)
        elif request.args['price'] == 'paid':
            query_obj = query_obj.filter(User.hourly_rate > 0)

    if request.args.get('rating') and request.args.get('rating') == 'Top Rated':
        query_obj = query_obj.filter(User.rating >= 4.5)

    users = query_obj.all()
    
    # Get unique industries for dropdown
    industries = sorted([res[0] for res in db.session.query(User.industry).filter(User.industry.isnot(None)).distinct().all()])

    return render_template('index.html', users=users, form=form, industries=industries)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter(
            or_(User.username == form.username.data, User.email == form.email.data)
        ).first()
        
        if existing_user:
            flash('Username or email already exists.', 'error')
            return render_template('register.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # Log in user but redirect to onboarding
        login_user(user)
        flash('Registration successful! Please complete your profile.', 'success')
        return redirect(url_for('onboarding'))
    
    return render_template('register.html', form=form)

@app.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    """Multi-step onboarding process"""
    form = OnboardingForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        # Update user profile with onboarding data
        current_user.profession = form.profession.data
        current_user.bio = form.bio.data
        current_user.hourly_rate = form.hourly_rate.data or 0
        current_user.industry = form.industry.data
        current_user.is_available = True  # Set as available by default
        
        # Handle specialties from form data
        specialties = request.form.get('specialties')
        print(f"DEBUG: Received specialties: {specialties}")
        if specialties:
            try:
                specialties_list = json.loads(specialties)
                print(f"DEBUG: Parsed specialties: {specialties_list}")
                current_user.specialty_tags = json.dumps(specialties_list)
            except (json.JSONDecodeError, TypeError) as e:
                print(f"DEBUG: Error parsing specialties: {e}")
                current_user.specialty_tags = json.dumps([])
        else:
            print("DEBUG: No specialties received")
            current_user.specialty_tags = json.dumps([])
        
        db.session.commit()
        flash('Profile setup complete!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('onboarding.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile/<username>')
@login_required
def profile(username):
    """View user profile"""
    user = User.query.filter_by(username=username).first_or_404()
    
    # If viewing own profile, show the profile edit page
    if current_user.username == username:
        return render_template('profile.html', user=user)
    
    # If viewing someone else's profile, show the public profile view
    return render_template('profile_view.html', user=user)

@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.bio = form.bio.data
        current_user.industry = form.industry.data
        current_user.profession = form.profession.data
        current_user.expertise = form.expertise.data
        current_user.location = form.location.data
        current_user.hourly_rate = form.hourly_rate.data or 0.0
        current_user.currency = form.currency.data
        current_user.linkedin_url = form.linkedin_url.data
        current_user.twitter_url = form.twitter_url.data
        current_user.youtube_url = form.youtube_url.data
        current_user.instagram_url = form.instagram_url.data
        current_user.website_url = form.website_url.data
        current_user.background_image_url = form.background_image_url.data
        current_user.is_available = form.is_available.data

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile', username=current_user.username))
    
    return render_template('edit_profile.html', form=form)

@app.route('/search')
def search():
    """Search for providers"""
    form = SearchForm(request.args)
    users = []
    
    # Build query
    query = User.query.filter(User.is_available == True, User.full_name.isnot(None))
    
    if form.query.data:
        search_term = f"%{form.query.data}%"
        query = query.filter(
            or_(
                User.full_name.ilike(search_term),
                User.bio.ilike(search_term),
                User.expertise.ilike(search_term)
            )
        )
    
    if form.industry.data:
        query = query.filter(User.industry == form.industry.data)
    
    if form.profession.data:
        query = query.filter(User.profession == form.profession.data)
    
    if form.location.data:
        query = query.filter(User.location == form.location.data)
    
    if form.min_rate.data is not None:
        query = query.filter(User.hourly_rate >= form.min_rate.data)
    
    if form.max_rate.data is not None:
        query = query.filter(User.hourly_rate <= form.max_rate.data)
    
    users = query.order_by(User.created_at.desc()).all()
    
    return render_template('search.html', form=form, users=users)

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    # Get upcoming bookings as provider
    provider_bookings = Booking.query.filter_by(provider_id=current_user.id).order_by(Booking.created_at.desc()).limit(10).all()
    
    # Get upcoming bookings as client
    client_bookings = Booking.query.filter_by(client_id=current_user.id).order_by(Booking.created_at.desc()).limit(10).all()
    
    # Get recent time slots
    time_slots = TimeSlot.query.filter_by(user_id=current_user.id).order_by(TimeSlot.start_datetime.desc()).limit(10).all()
    
    return render_template('dashboard.html', 
                         provider_bookings=provider_bookings,
                         client_bookings=client_bookings,
                         time_slots=time_slots)

@app.route('/calendar')
@login_required
def calendar():
    """Calendar view"""
    # Get time slots for the current month
    now = datetime.now(timezone.utc)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    time_slots = TimeSlot.query.filter(
        TimeSlot.user_id == current_user.id,
        TimeSlot.start_datetime >= start_of_month,
        TimeSlot.start_datetime <= end_of_month
    ).order_by(TimeSlot.start_datetime).all()
    
    return render_template('calendar.html', time_slots=time_slots)

@app.route('/calendar/add', methods=['GET', 'POST'])
@login_required
def add_time_slot():
    """Add new time slot"""
    form = TimeSlotForm()
    
    if form.validate_on_submit():
        # Validate that end time is after start time
        if form.end_datetime.data <= form.start_datetime.data:
            flash('End time must be after start time.', 'error')
            return render_template('calendar.html', form=form)
        
        time_slot = TimeSlot(
            user_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            start_datetime=form.start_datetime.data,
            end_datetime=form.end_datetime.data,
            session_type=form.session_type.data,
            meeting_details=form.location_details.data,
            price=form.price.data or current_user.hourly_rate
        )
        
        db.session.add(time_slot)
        db.session.commit()
        
        flash('Time slot added successfully!', 'success')
        return redirect(url_for('calendar'))
    
    return render_template('calendar.html', form=form)

@app.route('/booking/<int:slot_id>', methods=['GET', 'POST'])
def book_session(slot_id):
    """Book a session"""
    time_slot = TimeSlot.query.get_or_404(slot_id)
    
    if not time_slot.is_available:
        flash('This time slot is no longer available.', 'error')
        return redirect(url_for('profile', username=time_slot.user.username))
    
    form = BookingForm()
    form.time_slot_id.data = slot_id
    
    if form.validate_on_submit():
        # Create booking
        booking = Booking(
            time_slot_id=slot_id,
            provider_id=time_slot.user_id,
            client_id=current_user.id if current_user.is_authenticated else None,
            client_name=form.client_name.data,
            client_email=form.client_email.data,
            client_message=form.client_message.data,
            payment_amount=time_slot.price
        )
        
        db.session.add(booking)
        
        # Mark time slot as unavailable
        time_slot.is_available = False
        
        db.session.commit()
        
        # Redirect to payment if price > 0
        if time_slot.price > 0:
            return redirect(url_for('create_checkout_session', booking_id=booking.id))
        else:
            booking.payment_status = 'paid'
            booking.status = 'confirmed'
            db.session.commit()
            flash('Booking confirmed!', 'success')
            return redirect(url_for('booking_success', booking_id=booking.id))
    
    return render_template('booking.html', form=form, time_slot=time_slot)

@app.route('/create-checkout-session/<int:booking_id>', methods=['POST', 'GET'])
def create_checkout_session(booking_id):
    """Create Stripe checkout session"""
    booking = Booking.query.get_or_404(booking_id)
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': booking.provider.currency.lower(),
                    'product_data': {
                        'name': f'Session with {booking.provider.full_name}',
                        'description': booking.time_slot.title,
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
        return redirect(url_for('profile', username=booking.provider.username))

@app.route('/booking/success/<int:booking_id>')
def booking_success(booking_id):
    """Booking success page"""
    booking = Booking.query.get_or_404(booking_id)
    booking.payment_status = 'paid'
    booking.status = 'confirmed'
    db.session.commit()
    
    return render_template('success.html', booking=booking)

@app.route('/booking/cancel/<int:booking_id>')
def booking_cancel(booking_id):
    """Booking cancel page"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Restore time slot availability
    booking.time_slot.is_available = True
    booking.status = 'cancelled'
    
    db.session.commit()
    
    return render_template('cancel.html', booking=booking)

@app.route('/export/calendar/<username>')
def export_calendar(username):
    """Export user calendar as iCal"""
    user = User.query.filter_by(username=username).first_or_404()
    
    # Get all future time slots
    now = datetime.now(timezone.utc)
    time_slots = TimeSlot.query.filter(
        TimeSlot.user_id == user.id,
        TimeSlot.start_datetime > now
    ).order_by(TimeSlot.start_datetime).all()
    
    ical_content = generate_ical_content(time_slots, user)
    
    response = make_response(ical_content)
    response.headers['Content-Type'] = 'text/calendar'
    response.headers['Content-Disposition'] = f'attachment; filename={username}_calendar.ics'
    
    return response

@app.route('/bookings')
@login_required
def bookings():
    """View user's bookings and calendar"""
    return render_template('bookings.html', user=current_user)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/api/profile/update', methods=['POST'])
@login_required
def api_profile_update():
    """Update user profile via API"""
    try:
        data = request.get_json()
        
        # Update basic profile fields
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
    """Get or update availability rules"""
    if request.method == 'GET':
        # Return empty list for now since we don't have availability rules table yet
        return jsonify([])
    else:
        # POST - save rules (placeholder for now)
        return jsonify({'success': True})

@app.route('/api/availability/exceptions', methods=['GET', 'POST'])
@login_required
def api_availability_exceptions():
    """Get or update availability exceptions"""
    if request.method == 'GET':
        # Return empty list for now since we don't have exceptions table yet
        return jsonify([])
    else:
        # POST - save exception (placeholder for now)
        return jsonify({'success': True})

@app.route('/api/availability/exceptions/<int:exception_id>', methods=['DELETE'])
@login_required
def api_availability_exception_delete(exception_id):
    """Delete availability exception"""
    # Placeholder for now
    return jsonify({'success': True})
