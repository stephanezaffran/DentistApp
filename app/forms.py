from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, TimeField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Optional, Regexp


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={'placeholder': 'username'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'placeholder': 'password'})


class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={'placeholder': 'Name'})
    username = StringField('Username', validators=[DataRequired()], render_kw={'placeholder': 'username'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'placeholder': 'password'})


class PatientForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Regexp(r'^[a-zA-Z0-9\s]+$', message='Invalid  format')])
    surname = StringField('Surname', validators=[DataRequired(), Regexp(r'^[a-zA-Z0-9\s]+$', message='Invalid  format')])
    phone_number = StringField('Phone_number', validators=[DataRequired(), Regexp(r'^(05)\d{8}$', message='Invalid  format')])
    email = StringField('email', validators=[DataRequired(), Regexp(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', message='Invalid  format')])
    identity_number = StringField('identity_number', validators=[DataRequired(), Regexp(r'^\d{9}$', message='Invalid  format')])


class AppointmentForm(FlaskForm):
    patient = SelectField('Patient', coerce=int, validators=[DataRequired()])
    message = StringField('Message', validators=[Optional()])
    date = DateField('Date', validators=[Optional()])
    start_time = TimeField('Start Time', validators=[Optional()])
    end_time = TimeField('End Time', validators=[Optional()])





