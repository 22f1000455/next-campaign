from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FloatField, SubmitField, PasswordField, DateField
from wtforms.validators import DataRequired, Length, EqualTo
from wtforms import HiddenField, IntegerField

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Length(min=6, max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    user_type = SelectField('User Type', choices=[('sponsor', 'Sponsor'), ('influencer', 'Influencer'),('admin', 'admin')])
    submit = SubmitField('Sign Up')




class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(min=6, max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CampaignForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    niche = StringField('Niche', validators=[DataRequired(), Length(min=2, max=50)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    budget = FloatField('Budget', validators=[DataRequired()])
    goals = TextAreaField('Goals', validators=[DataRequired()])
    visibility = SelectField('Visibility', choices=[('public', 'Public'), ('private', 'Private')])
    submit = SubmitField('Submit')



class SearchForm(FlaskForm):
    search_query = StringField('Search', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Search')


class AdRequestForm(FlaskForm):
    campaign_id = HiddenField('Campaign ID', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    requirements = TextAreaField('Requirements', validators=[DataRequired()])
    payment_amount = IntegerField('Payment Amount', validators=[DataRequired()])
    submit = SubmitField('Submit Request')




