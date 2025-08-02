from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FloatField, BooleanField, PasswordField, DateTimeLocalField, HiddenField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, EqualTo
from models import Category

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Sign Up')

class OnboardingForm(FlaskForm):
    profession = StringField('Professional Title', validators=[DataRequired(), Length(max=100)])
    bio = TextAreaField('Bio', validators=[DataRequired(), Length(max=500)])
    hourly_rate = IntegerField('Hourly Rate ($)', validators=[Optional()])
    industry = SelectField('Industry', choices=[
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

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

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
    location = SelectField('Location', choices=[
        ('', 'Select Location'),
        ('new-york-ny', 'New York, NY'),
        ('los-angeles-ca', 'Los Angeles, CA'),
        ('chicago-il', 'Chicago, IL'),
        ('houston-tx', 'Houston, TX'),
        ('phoenix-az', 'Phoenix, AZ'),
        ('philadelphia-pa', 'Philadelphia, PA'),
        ('san-antonio-tx', 'San Antonio, TX'),
        ('san-diego-ca', 'San Diego, CA'),
        ('dallas-tx', 'Dallas, TX'),
        ('san-jose-ca', 'San Jose, CA'),
        ('austin-tx', 'Austin, TX'),
        ('jacksonville-fl', 'Jacksonville, FL'),
        ('fort-worth-tx', 'Fort Worth, TX'),
        ('columbus-oh', 'Columbus, OH'),
        ('charlotte-nc', 'Charlotte, NC'),
        ('san-francisco-ca', 'San Francisco, CA'),
        ('indianapolis-in', 'Indianapolis, IN'),
        ('seattle-wa', 'Seattle, WA'),
        ('denver-co', 'Denver, CO'),
        ('washington-dc', 'Washington, DC'),
        ('boston-ma', 'Boston, MA'),
        ('el-paso-tx', 'El Paso, TX'),
        ('detroit-mi', 'Detroit, MI'),
        ('nashville-tn', 'Nashville, TN'),
        ('portland-or', 'Portland, OR'),
        ('memphis-tn', 'Memphis, TN'),
        ('oklahoma-city-ok', 'Oklahoma City, OK'),
        ('las-vegas-nv', 'Las Vegas, NV'),
        ('louisville-ky', 'Louisville, KY'),
        ('baltimore-md', 'Baltimore, MD'),
        ('milwaukee-wi', 'Milwaukee, WI'),
        ('albuquerque-nm', 'Albuquerque, NM'),
        ('tucson-az', 'Tucson, AZ'),
        ('fresno-ca', 'Fresno, CA'),
        ('mesa-az', 'Mesa, AZ'),
        ('sacramento-ca', 'Sacramento, CA'),
        ('atlanta-ga', 'Atlanta, GA'),
        ('kansas-city-mo', 'Kansas City, MO'),
        ('colorado-springs-co', 'Colorado Springs, CO'),
        ('miami-fl', 'Miami, FL'),
        ('raleigh-nc', 'Raleigh, NC'),
        ('omaha-ne', 'Omaha, NE'),
        ('long-beach-ca', 'Long Beach, CA'),
        ('virginia-beach-va', 'Virginia Beach, VA'),
        ('oakland-ca', 'Oakland, CA'),
        ('minneapolis-mn', 'Minneapolis, MN'),
        ('tulsa-ok', 'Tulsa, OK'),
        ('arlington-tx', 'Arlington, TX'),
        ('tampa-fl', 'Tampa, FL'),
        ('new-orleans-la', 'New Orleans, LA'),
        ('wichita-ks', 'Wichita, KS'),
        ('cleveland-oh', 'Cleveland, OH'),
        ('bakersfield-ca', 'Bakersfield, CA'),
        ('aurora-co', 'Aurora, CO'),
        ('anaheim-ca', 'Anaheim, CA'),
        ('honolulu-hi', 'Honolulu, HI'),
        ('santa-ana-ca', 'Santa Ana, CA'),
        ('corpus-christi-tx', 'Corpus Christi, TX'),
        ('riverside-ca', 'Riverside, CA'),
        ('lexington-ky', 'Lexington, KY'),
        ('stockton-ca', 'Stockton, CA'),
        ('st-paul-mn', 'St. Paul, MN'),
        ('cincinnati-oh', 'Cincinnati, OH'),
        ('anchorage-ak', 'Anchorage, AK'),
        ('henderson-nv', 'Henderson, NV'),
        ('greensboro-nc', 'Greensboro, NC'),
        ('plano-tx', 'Plano, TX'),
        ('newark-nj', 'Newark, NJ'),
        ('lincoln-ne', 'Lincoln, NE'),
        ('orlando-fl', 'Orlando, FL'),
        ('chula-vista-ca', 'Chula Vista, CA'),
        ('jersey-city-nj', 'Jersey City, NJ'),
        ('chandler-az', 'Chandler, AZ'),
        ('laredo-tx', 'Laredo, TX'),
        ('madison-wi', 'Madison, WI'),
        ('lubbock-tx', 'Lubbock, TX'),
        ('winston-salem-nc', 'Winston-Salem, NC'),
        ('garland-tx', 'Garland, TX'),
        ('glendale-az', 'Glendale, AZ'),
        ('hialeah-fl', 'Hialeah, FL'),
        ('reno-nv', 'Reno, NV'),
        ('baton-rouge-la', 'Baton Rouge, LA'),
        ('irvine-ca', 'Irvine, CA'),
        ('chesapeake-va', 'Chesapeake, VA'),
        ('irving-tx', 'Irving, TX'),
        ('scottsdale-az', 'Scottsdale, AZ'),
        ('north-las-vegas-nv', 'North Las Vegas, NV'),
        ('fremont-ca', 'Fremont, CA'),
        ('gilbert-az', 'Gilbert, AZ'),
        ('san-bernardino-ca', 'San Bernardino, CA'),
        ('boise-id', 'Boise, ID'),
        ('birmingham-al', 'Birmingham, AL'),
        ('london-uk', 'London, UK'),
        ('manchester-uk', 'Manchester, UK'),
        ('birmingham-uk', 'Birmingham, UK'),
        ('glasgow-uk', 'Glasgow, UK'),
        ('liverpool-uk', 'Liverpool, UK'),
        ('leeds-uk', 'Leeds, UK'),
        ('sheffield-uk', 'Sheffield, UK'),
        ('edinburgh-uk', 'Edinburgh, UK'),
        ('bristol-uk', 'Bristol, UK'),
        ('cardiff-uk', 'Cardiff, UK'),
        ('toronto-ca', 'Toronto, Canada'),
        ('montreal-ca', 'Montreal, Canada'),
        ('vancouver-ca', 'Vancouver, Canada'),
        ('calgary-ca', 'Calgary, Canada'),
        ('ottawa-ca', 'Ottawa, Canada'),
        ('edmonton-ca', 'Edmonton, Canada'),
        ('mississauga-ca', 'Mississauga, Canada'),
        ('winnipeg-ca', 'Winnipeg, Canada'),
        ('quebec-city-ca', 'Quebec City, Canada'),
        ('hamilton-ca', 'Hamilton, Canada'),
        ('sydney-au', 'Sydney, Australia'),
        ('melbourne-au', 'Melbourne, Australia'),
        ('brisbane-au', 'Brisbane, Australia'),
        ('perth-au', 'Perth, Australia'),
        ('adelaide-au', 'Adelaide, Australia'),
        ('gold-coast-au', 'Gold Coast, Australia'),
        ('canberra-au', 'Canberra, Australia'),
        ('newcastle-au', 'Newcastle, Australia'),
        ('wollongong-au', 'Wollongong, Australia'),
        ('hobart-au', 'Hobart, Australia'),
        ('berlin-de', 'Berlin, Germany'),
        ('hamburg-de', 'Hamburg, Germany'),
        ('cologne-de', 'Cologne, Germany'),
        ('frankfurt-de', 'Frankfurt, Germany'),
        ('stuttgart-de', 'Stuttgart, Germany'),
        ('dusseldorf-de', 'Düsseldorf, Germany'),
        ('dortmund-de', 'Dortmund, Germany'),
        ('essen-de', 'Essen, Germany'),
        ('leipzig-de', 'Leipzig, Germany'),
        ('paris-fr', 'Paris, France'),
        ('marseille-fr', 'Marseille, France'),
        ('lyon-fr', 'Lyon, France'),
        ('toulouse-fr', 'Toulouse, France'),
        ('nice-fr', 'Nice, France'),
        ('nantes-fr', 'Nantes, France'),
        ('strasbourg-fr', 'Strasbourg, France'),
        ('montpellier-fr', 'Montpellier, France'),
        ('bordeaux-fr', 'Bordeaux, France'),
        ('lille-fr', 'Lille, France'),
        ('remote-worldwide', 'Remote (Worldwide)'),
        ('remote-us', 'Remote (US Only)'),
        ('remote-europe', 'Remote (Europe Only)'),
        ('remote-asia', 'Remote (Asia Pacific)')
    ], validators=[Optional()])
    
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
    
    # Profile appearance
    background_image_url = StringField('Background Image URL', validators=[Optional(), Length(max=500)])
    
    # Availability settings
    is_available = BooleanField('Currently Available for Sessions')

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
    
    location_details = StringField('Meeting Details', validators=[Optional(), Length(max=200)])
    price = FloatField('Price', validators=[Optional(), NumberRange(min=0, max=10000)])

class BookingForm(FlaskForm):
    client_name = StringField('Your Name', validators=[DataRequired(), Length(max=100)])
    client_email = StringField('Your Email', validators=[DataRequired(), Email()])
    client_message = TextAreaField('Message (Optional)', validators=[Optional(), Length(max=500)])
    time_slot_id = HiddenField(validators=[DataRequired()])

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[Optional()])
    category = SelectField('Category', choices=[
        ('All Categories', 'All Categories'),
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
    ], default='All Categories')
    price = SelectField('Price', choices=[
        ('Any Price', 'Any Price'),
        ('free', 'Free'),
        ('paid', 'Paid')
    ], default='Any Price')
    rating = SelectField('Rating', choices=[
        ('Any Rating', 'Any Rating'),
        ('Top Rated', 'Top Rated')
    ], default='Any Rating')
