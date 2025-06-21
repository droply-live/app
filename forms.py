from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])

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
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[])
    category = SelectField('Category', choices=[
        ('', 'All Categories'),
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
    price = SelectField('Price', choices=[
        ('', 'Any Price'),
        ('free', 'Free'),
        ('paid', 'Paid')
    ], default='')
    rating = SelectField('Rating', choices=[
        ('', 'Any Rating'),
        ('top', 'Top Rated')
    ], default='')
