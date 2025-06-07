from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FloatField, BooleanField, PasswordField, DateTimeLocalField, HiddenField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional
from models import Category

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class ProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=1000)])
    
    # Categories
    industry = SelectField('Industry', choices=[
        ('', 'Select Industry'),
        ('technology', 'Technology'),
        ('business', 'Business'),
        ('marketing', 'Marketing'),
        ('finance', 'Finance'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('consulting', 'Consulting'),
        ('creative', 'Creative'),
        ('fitness', 'Fitness & Wellness'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    
    profession = SelectField('Profession', choices=[
        ('', 'Select Profession'),
        ('coach', 'Coach'),
        ('mentor', 'Mentor'),
        ('consultant', 'Consultant'),
        ('advisor', 'Advisor'),
        ('trainer', 'Trainer'),
        ('therapist', 'Therapist'),
        ('instructor', 'Instructor'),
        ('specialist', 'Specialist'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    
    expertise = StringField('Area of Expertise', validators=[Optional(), Length(max=200)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    
    # Pricing
    hourly_rate = FloatField('Hourly Rate (USD)', validators=[Optional(), NumberRange(min=0, max=10000)])
    currency = SelectField('Currency', choices=[
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('GBP', 'GBP'),
        ('CAD', 'CAD'),
        ('AUD', 'AUD')
    ], default='USD')
    
    # Social media links
    linkedin_url = StringField('LinkedIn Profile', validators=[Optional(), Length(max=200)])
    twitter_url = StringField('Twitter/X Profile', validators=[Optional(), Length(max=200)])
    youtube_url = StringField('YouTube Channel', validators=[Optional(), Length(max=200)])
    instagram_url = StringField('Instagram Profile', validators=[Optional(), Length(max=200)])
    website_url = StringField('Website/Portfolio', validators=[Optional(), Length(max=200)])
    
    # Availability settings
    is_available = BooleanField('Currently Available for Sessions')
    offers_remote = BooleanField('Available for Remote Sessions', default=True)

class TimeSlotForm(FlaskForm):
    title = StringField('Session Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    start_datetime = DateTimeLocalField('Start Date & Time', validators=[DataRequired()])
    end_datetime = DateTimeLocalField('End Date & Time', validators=[DataRequired()])
    
    session_type = SelectField('Session Type', choices=[
        ('consultation', 'Consultation'),
        ('coaching', 'Coaching'),
        ('mentoring', 'Mentoring'),
        ('training', 'Training'),
        ('other', 'Other')
    ], default='consultation')
    
    location_type = HiddenField(default='remote')
    
    location_details = StringField('Location Details', validators=[Optional(), Length(max=200)])
    price = FloatField('Price', validators=[Optional(), NumberRange(min=0, max=10000)])

class BookingForm(FlaskForm):
    client_name = StringField('Your Name', validators=[DataRequired(), Length(max=100)])
    client_email = StringField('Your Email', validators=[DataRequired(), Email()])
    client_message = TextAreaField('Message (Optional)', validators=[Optional(), Length(max=500)])
    time_slot_id = HiddenField(validators=[DataRequired()])

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[Optional()])
    industry = SelectField('Industry', choices=[
        ('', 'All Industries'),
        ('technology', 'Technology'),
        ('business', 'Business'),
        ('marketing', 'Marketing'),
        ('finance', 'Finance'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('consulting', 'Consulting'),
        ('creative', 'Creative'),
        ('fitness', 'Fitness & Wellness'),
        ('other', 'Other')
    ], default='')
    
    profession = SelectField('Profession', choices=[
        ('', 'All Professions'),
        ('coach', 'Coach'),
        ('mentor', 'Mentor'),
        ('consultant', 'Consultant'),
        ('advisor', 'Advisor'),
        ('trainer', 'Trainer'),
        ('therapist', 'Therapist'),
        ('instructor', 'Instructor'),
        ('specialist', 'Specialist'),
        ('other', 'Other')
    ], default='')
    
    location = StringField('Location', validators=[Optional()])

    
    min_rate = FloatField('Min Rate', validators=[Optional(), NumberRange(min=0)])
    max_rate = FloatField('Max Rate', validators=[Optional(), NumberRange(min=0)])
