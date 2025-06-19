import os
import stripe
from datetime import datetime, timezone, timedelta, time
from flask import render_template, request, redirect, url_for, flash, session, make_response, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_, and_
from app import app, db
from models import User, TimeSlot, Booking, AvailabilityRule, AvailabilityException
from forms import RegistrationForm, LoginForm, ProfileForm, TimeSlotForm, BookingForm, SearchForm
from utils import generate_ical_content

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_default')
YOUR_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')
if not YOUR_DOMAIN.startswith('http'):
    YOUR_DOMAIN = f"https://{YOUR_DOMAIN}" if os.environ.get('REPLIT_DEPLOYMENT') else f"http://{YOUR_DOMAIN}"

@app.route('/')
def index():
    """Homepage with all available providers"""
    users = User.query.filter(
        User.is_available == True,
        User.full_name.isnot(None)
    ).order_by(User.created_at.desc()).all()
    return render_template('index.html', users=users)

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
            password_hash=generate_password_hash(form.password.data),
            full_name=form.full_name.data
        )
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Registration successful! Please complete your profile.', 'success')
        return redirect(url_for('edit_profile'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
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
def profile(username):
    """View user profile"""
    user = User.query.filter_by(username=username).first_or_404()
    
    # Get available time slots
    now = datetime.now(timezone.utc)
    available_slots = TimeSlot.query.filter(
        TimeSlot.user_id == user.id,
        TimeSlot.is_available == True,
        TimeSlot.start_datetime > now
    ).order_by(TimeSlot.start_datetime).limit(10).all()
    
    return render_template('profile.html', user=user, available_slots=available_slots)

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

@app.route('/api/timeslots', methods=['GET'])
@login_required
def api_get_timeslots():
    """Return all time slots for the current user as JSON (for FullCalendar)"""
    slots = TimeSlot.query.filter_by(user_id=current_user.id).all()
    events = []
    for slot in slots:
        events.append({
            'id': slot.id,
            'title': slot.title or 'Available',
            'start': slot.start_datetime.isoformat(),
            'end': slot.end_datetime.isoformat(),
            'color': '#4caf50' if slot.is_available else '#bdbdbd',
            'editable': slot.is_available,
        })
    return jsonify(events)

@app.route('/api/timeslots', methods=['POST'])
@login_required
def api_add_timeslot():
    """Add a new time slot for the current user (from FullCalendar)"""
    data = request.get_json()
    start = data.get('start')
    end = data.get('end')
    title = data.get('title', 'Available')
    if not start or not end:
        return jsonify({'error': 'Missing start or end'}), 400
    # Prevent overlap
    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.fromisoformat(end)
    overlap = TimeSlot.query.filter(
        TimeSlot.user_id == current_user.id,
        TimeSlot.end_datetime > start_dt,
        TimeSlot.start_datetime < end_dt
    ).first()
    if overlap:
        return jsonify({'error': 'Time slot overlaps with an existing slot'}), 400
    slot = TimeSlot(
        user_id=current_user.id,
        start_datetime=start_dt,
        end_datetime=end_dt,
        title=title,
        is_available=True
    )
    db.session.add(slot)
    db.session.commit()
    return jsonify({'success': True, 'id': slot.id})

@app.route('/api/timeslots/<int:slot_id>', methods=['DELETE'])
@login_required
def api_delete_timeslot(slot_id):
    """Delete a time slot for the current user (from FullCalendar)"""
    slot = TimeSlot.query.filter_by(id=slot_id, user_id=current_user.id).first()
    if not slot:
        return jsonify({'error': 'Not found'}), 404
    db.session.delete(slot)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/availability/rules', methods=['GET'])
@login_required
def get_availability_rules():
    rules = AvailabilityRule.query.filter_by(user_id=current_user.id).all()
    return jsonify([
        {
            'weekday': r.weekday,
            'start': r.start_time.strftime('%H:%M'),
            'end': r.end_time.strftime('%H:%M')
        } for r in rules
    ])

@app.route('/api/availability/rules', methods=['POST'])
@login_required
def set_availability_rules():
    data = request.get_json()
    # Remove all old rules
    AvailabilityRule.query.filter_by(user_id=current_user.id).delete()
    # Add new rules
    for rule in data.get('rules', []):
        if not rule.get('enabled'): continue
        new_rule = AvailabilityRule(
            user_id=current_user.id,
            weekday=rule['day'],
            start_time=time.fromisoformat(rule['start']),
            end_time=time.fromisoformat(rule['end'])
        )
        db.session.add(new_rule)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/availability/exceptions', methods=['GET'])
@login_required
def get_availability_exceptions():
    exceptions = AvailabilityException.query.filter_by(user_id=current_user.id).all()
    return jsonify([
        {
            'id': e.id,
            'start': e.start_datetime.isoformat(),
            'end': e.end_datetime.isoformat(),
            'reason': e.reason
        } for e in exceptions
    ])

@app.route('/api/availability/exceptions', methods=['POST'])
@login_required
def add_availability_exception():
    data = request.get_json()
    from datetime import datetime
    start = datetime.fromisoformat(data['start'])
    end = datetime.fromisoformat(data['end'])
    reason = data.get('reason')
    ex = AvailabilityException(user_id=current_user.id, start_datetime=start, end_datetime=end, reason=reason)
    db.session.add(ex)
    db.session.commit()
    return jsonify({'success': True, 'id': ex.id})

@app.route('/api/availability/exceptions/<int:ex_id>', methods=['DELETE'])
@login_required
def delete_availability_exception(ex_id):
    ex = AvailabilityException.query.filter_by(id=ex_id, user_id=current_user.id).first()
    if not ex:
        return jsonify({'error': 'Not found'}), 404
    db.session.delete(ex)
    db.session.commit()
    return jsonify({'success': True})

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
